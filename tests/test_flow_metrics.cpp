#include <iostream>
#include <cmath>
#include "gig/memory/tracked_resource.hpp"
#include "gig/analytics/flow_metrics.hpp"
#include "fixtures/synthetic/book_events.hpp"
using namespace gig;using namespace gig::analytics;using namespace gig::fixtures;
namespace {
void check(bool x){if(!x)throw std::runtime_error("flow assertion");}
SnapshotReference ref(std::size_t n){return {text("flow-fixture-run"),n,static_cast<std::uint64_t>(n),rules(),book_session()};}
FlowQuote quote(std::int64_t t,std::size_t n,std::int64_t b,std::int64_t a,std::uint64_t bq=10,std::uint64_t aq=10){return {ref(n),number<EventTimestamp>(t),text("flow-utc"),DepthLevel{number<PriceTicks>(b),number<QuantityLots>(bq),1},DepthLevel{number<PriceTicks>(a),number<QuantityLots>(aq),1}};}
FlowTrade trade(std::int64_t t,std::size_t n,std::int64_t p){return {ref(n),number<EventTimestamp>(t),text("flow-utc"),number<PriceTicks>(p),number<QuantityLots>(1)};}
FlowConfig config(){return {text("flow-utc"),number<Duration>(10),number<Duration>(0),number<Duration>(5),number<Duration>(100),number<Duration>(10),true,true};}
std::string value(const Metric& x){return x.value?x.value->str():"NA";}
void emit(const FlowMetrics& f){const auto& s=f.summary();const auto& t=f.trades().front();std::cout<<value(s.ofi)<<' '<<value(s.trade_intensity)<<' '<<value(s.quote_intensity)<<' '<<value(s.window_return)<<' '<<value(s.realized_variance)<<' '<<static_cast<int>(t.sign)<<' '<<value(t.effective_spread)<<' '<<value(t.realized_spread)<<' '<<value(t.price_impact)<<'\n';}
}
int main(int argc,char** argv){try{
    if(argc==2 && std::string_view(argv[1])=="reference"){
        std::int64_t b{},a{},c{},d{},p{};std::uint64_t x{},y{},z{},w{};
        while(std::cin>>b>>a>>x>>y>>c>>d>>z>>w>>p){std::array<FlowQuote,2> q{quote(0,1,b,a,x,y),quote(10,3,c,d,z,w)};std::array<FlowTrade,1> t{trade(5,2,p)};auto f=take(calculate_flow(q,t,config(),number<EventTimestamp>(10)));emit(f);}return 0;
    }
    std::array<FlowQuote,2> q{quote(0,1,100,102,30,10),quote(10,3,101,103,20,20)};std::array<FlowTrade,1> t{trade(5,2,102)};
    auto f=take(calculate_flow(q,t,config(),number<EventTimestamp>(10)));check(value(f.summary().ofi)=="30/1");check(value(f.trades()[0].effective_spread)=="2/1" && value(f.trades()[0].realized_spread)=="0/1" && value(f.trades()[0].price_impact)=="2/1");check(value(f.summary().window_return)=="1/101" && value(f.summary().realized_variance)=="1/10201");check(std::fabs(*f.summary().realized_volatility-1.0L/101)<1e-18L);check(f.parents().size()==3);
    auto c=config();c.continuity_complete=false;check(!take(calculate_flow(q,t,c,number<EventTimestamp>(10))).summary().ofi.value);
    c=config();c.complete_top_updates=false;check(!take(calculate_flow(q,t,c,number<EventTimestamp>(10))).summary().ofi.value);
    c=config();c.quote_lag=number<Duration>(6);check(take(calculate_flow(q,t,c,number<EventTimestamp>(10))).trades()[0].sign==TradeSign::unknown);
    c=config();c.horizon=number<Duration>(6);check(take(calculate_flow(q,t,c,number<EventTimestamp>(10))).trades()[0].realized_spread.unavailable==Unavailable::horizon_pending);
    c=config();c.max_quote_age=number<Duration>(1);check(!take(calculate_flow(q,t,c,number<EventTimestamp>(10))).summary().ofi.value);
    c=config();c.sampling_interval=number<Duration>(3);check(!calculate_flow(q,t,c,number<EventTimestamp>(10)));
    auto altered=q;altered[1].source.session.epoch=1;check(!calculate_flow(altered,t,config(),number<EventTimestamp>(10)));
    altered=q;altered[1].utc_clock=text("other-clock");check(!calculate_flow(altered,t,config(),number<EventTimestamp>(10)));
    altered=q;altered[1].source.revision=1;check(!calculate_flow(altered,t,config(),number<EventTimestamp>(10)));
    altered=q;altered[1].timestamp=number<EventTimestamp>(11);check(!calculate_flow(altered,t,config(),number<EventTimestamp>(10)));
    altered=q;altered[1].source.journal_prefix=1;check(!calculate_flow(altered,t,config(),number<EventTimestamp>(10)));
    altered=q;altered[0].ask.reset();check(take(calculate_flow(altered,t,config(),number<EventTimestamp>(10))).trades()[0].sign==TradeSign::unknown);
    // Equal-time quote with later journal prefix is unavailable at the trade decision.
    altered=q;altered[1].timestamp=number<EventTimestamp>(5);t[0].price=number<PriceTicks>(101);
    check(take(calculate_flow(altered,t,config(),number<EventTimestamp>(10))).trades()[0].sign==TradeSign::unknown);
    std::array<FlowTrade,3> ticks{trade(3,2,100),trade(5,3,101),trade(6,4,101)};std::array<FlowQuote,1> fixed{q[0]};auto signed_ticks=take(calculate_flow(fixed,ticks,config(),number<EventTimestamp>(10)));check(signed_ticks.trades()[1].sign==TradeSign::buy && signed_ticks.trades()[2].sign==TradeSign::buy);
    for(std::size_t position=0;position<2;++position){TrackedResource memory;memory.fail_after(position);auto failed=calculate_flow(q,t,config(),number<EventTimestamp>(10),&memory);check(!failed && failed.error.code==ErrorCode::resource_exhausted && memory.stats().live_bytes==0);}
    check(!calculate_flow(q,t,config(),number<EventTimestamp>(10),nullptr));
    auto zero_quote=q;auto zero_trade=t;
    for(auto& x:zero_quote){x.source.rules.minimum_price=number<PriceTicks>(0);x.bid->price_ticks=number<PriceTicks>(0);x.ask->price_ticks=number<PriceTicks>(0);}
    zero_trade[0].source.rules.minimum_price=number<PriceTicks>(0);zero_trade[0].price=number<PriceTicks>(0);
    auto zero_result=take(calculate_flow(zero_quote,zero_trade,config(),number<EventTimestamp>(10)));
    check(zero_result.summary().window_return.unavailable==Unavailable::zero_denominator && zero_result.summary().realized_variance.unavailable==Unavailable::zero_denominator);
    auto empty=take(calculate_flow({}, {},config(),number<EventTimestamp>(10)));check(value(empty.summary().trade_intensity)=="0/1" && !empty.summary().realized_variance.value);
    std::cout<<"PASS: OFI, quote lag/tick signing, horizons, clock/order/gap/reset/age/sampling boundaries and exact hand references\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
