#include <iostream>
#include "fixtures/synthetic/execution.hpp"
#include "gig/memory/tracked_resource.hpp"
using namespace gig;using namespace gig::fixtures;using namespace gig::execution;
namespace {
std::size_t checks=0;void check(bool x){++checks;if(!x)throw std::runtime_error("execution assertion #"+std::to_string(checks));}
void print(const Schedule& s){std::cout<<s.children().size();for(const auto& x:s.children())std::cout<<' '<<x.decision_time.value()<<':'<<x.order.quantity.value();std::cout<<'\n';}
void schedules(){
    auto c=plan_config(10,3);auto t=take(twap(c));check(t.children().size()==3 && t.children()[0].order.quantity.value()==4 && t.children()[1].order.quantity.value()==3 && t.children()[2].decision_time==sim_time(666));
    std::array<std::uint64_t,3> weights{1,2,1};auto v=take(vwap(c,weights,text("ex-ante-profile"),sim_time(0),VolumeProfile::ex_ante_forecast));check(v.children()[0].order.quantity.value()==3 && v.children()[1].order.quantity.value()==5 && v.children()[2].order.quantity.value()==2 && !v.oracle());
    check(!vwap(c,weights,text("future-profile"),sim_time(1),VolumeProfile::ex_ante_forecast));check(take(vwap(c,weights,text("oracle-profile"),sim_time(1000),VolumeProfile::oracle_hindsight)).oracle());
    c.max_child=number<QuantityLots>(2);auto split=take(twap(c));check(split.children().size()==6);std::uint64_t total=0;for(const auto& x:split.children()){check(x.order.quantity.value()<=2);total+=x.order.quantity.value();}check(total==10);
    std::array<VolumePoint,3> volume{{{sim_time(1),number<QuantityLots>(11),text("volume"),1},{sim_time(2),number<QuantityLots>(9),text("volume"),2},{sim_time(3),number<QuantityLots>(100),text("volume"),3}}};
    c=plan_config(20,1);auto p=take(pov(c,volume,1,10));check(p.children().size()==3 && p.children()[0].order.quantity.value()==1 && p.children()[1].order.quantity.value()==1 && p.children()[2].order.quantity.value()==10);
    auto prefix=take(pov(c,std::span(volume).first(2),1,10));check(std::equal(prefix.children().begin(),prefix.children().end(),p.children().begin()));
    volume[1].ordinal=1;check(!pov(c,volume,1,10));volume[1].ordinal=2;volume[2].available_at=sim_time(1001);check(!pov(c,volume,1,10));check(!pov(c,{},1,0));
    c=plan_config();c.target=number<QuantityLots>(101);check(!twap(c));c=plan_config();c.first_child_id=number<OrderId>(UINT64_MAX);check(!twap(c));c=plan_config(5000,1);c.max_child=number<QuantityLots>(1);check(!twap(c));
    c=plan_config(UINT64_MAX,2);weights={UINT64_MAX,UINT64_MAX,0};auto extreme=take(vwap(c,std::span(weights).first(2),text("wide-profile"),sim_time(0),VolumeProfile::ex_ante_forecast));check(extreme.children()[0].order.quantity.value()==(UINT64_MAX/2+1) && extreme.children()[1].order.quantity.value()==UINT64_MAX/2);
}
void costs(){
    std::array<CostFill,1> fills{cost_fill()};auto c=cost_config();auto r=take(transaction_costs(c,fills));const auto& s=r.summary();
    check(s.filled_lots==10 && s.unfilled_lots==10 && s.execution_vwap.value->str()=="103/1");check(s.delay_cost.str()=="20/1" && s.spread_cost.str()=="10/1" && s.fees.str()=="1/1" && s.opportunity_cost.str()=="40/1" && s.implementation_shortfall.str()=="71/1" && s.currency_shortfall.str()=="71/100");check(r.parents()[0].fill.run_id==c.simulation_run_id);
    auto future=fills;future[0].decision_benchmark.available_at=sim_time(6);check(!transaction_costs(c,future));future=fills;future[0].fill.reported_at=sim_time(21);check(!transaction_costs(c,future));
    std::array<CostFill,2> duplicate{fills[0],fills[0]};check(!transaction_costs(c,duplicate));c.target=number<QuantityLots>(9);check(!transaction_costs(c,fills));
    c=cost_config(20,Side::sell);fills[0]=cost_fill(10,99,Side::sell);fills[0].decision_benchmark=benchmark(100,5);fills[0].fee_ticks_per_lot=exact::Fraction::ratio(-1,10);auto sell=take(transaction_costs(c,fills));check(sell.summary().fees.str()=="-1/1" && sell.summary().slippage.str()=="10/1");
    auto empty=take(transaction_costs(cost_config(),{}));check(!empty.summary().execution_vwap.value && empty.summary().filled_lots==0 && empty.summary().implementation_shortfall.str()=="80/1");
}
void integration(){
    auto c=plan_config(10,2);auto p=take(twap(c));auto config=sim_config();config.run_id=c.run_id;std::array<simulation::SimOrder,1> liquidity{sim_order(1,Side::sell,100,100)};auto run=take(simulate(p,config,liquidity,sim_time(1000)));std::uint64_t filled=0;for(const auto& f:run.simulator.exchange_fills())filled+=f.quantity.value();check(filled==10 && !run.simulator.check_invariants());
    auto forged_children=std::pmr::vector<ChildSlice>(p.children());forged_children[0].order.quantity=number<QuantityLots>(100);
    Schedule forged(c,Algorithm::twap,false,p.profile(),std::move(forged_children),std::pmr::vector<std::uint64_t>(p.weights()),{},0,1,p.profile_available_at());
    check(!simulate(forged,config,liquidity,sim_time(1000)));
    config.run_id=text("wrong-run");check(!simulate(p,config,liquidity,sim_time(1000)));
    for(std::size_t n=0;n<30;++n){TrackedResource memory;memory.fail_after(n);auto result=twap(c,&memory);memory.disable_failure();if(result){result.data.reset();check(memory.stats().live_bytes==0);std::cout<<"schedule fault positions="<<n<<'\n';break;}check(result.error.code==ErrorCode::resource_exhausted && memory.stats().live_bytes==0);}
    bool complete=false;
    auto valid=sim_config();valid.run_id=p.config().run_id;
    for(std::size_t n=0;n<256 && !complete;++n){TrackedResource resource;resource.fail_after(n);auto run_result=simulate(p,valid,liquidity,sim_time(1000),&resource);resource.disable_failure();if(run_result){complete=true;run_result.data.reset();std::cout<<"integration fault positions="<<n<<'\n';}else check(run_result.error.code==ErrorCode::resource_exhausted);check(resource.stats().live_bytes==0);}
    check(complete);
    TrackedResource memory;memory.fail_after(0);std::array<CostFill,1> f{cost_fill()};check(!transaction_costs(cost_config(),f,&memory) && memory.stats().live_bytes==0);
}
}
int main(int argc,char** argv){try{
    if(argc==2 && std::string_view(argv[1])=="reference"){
        char mode{};while(std::cin>>mode){
            if(mode=='W'){std::uint64_t target{};std::uint32_t count{};std::cin>>target>>count;std::vector<std::uint64_t> weights(count);for(auto& w:weights)std::cin>>w;auto c=plan_config(target,count);print(take(vwap(c,weights,text("reference-profile"),sim_time(0),VolumeProfile::ex_ante_forecast)));}
            else if(mode=='P'){std::uint64_t target{},num{},den{};std::size_t count{};std::cin>>target>>num>>den>>count;std::vector<VolumePoint> volume;for(std::size_t i=0;i<count;++i){std::uint64_t q{};std::cin>>q;volume.push_back({sim_time(static_cast<std::int64_t>(i+1)),number<QuantityLots>(q),text("reference-volume"),i});}print(take(pov(plan_config(target,1),volume,num,den)));}
            else if(mode=='C'){int side{};std::uint64_t target{},quantity{};std::int64_t price{},arrival{},decision{},terminal{},fn{},fd{};std::cin>>side>>target>>quantity>>price>>arrival>>decision>>terminal>>fn>>fd;auto direction=side?Side::sell:Side::buy;auto c=cost_config(target,direction);c.arrival=benchmark(arrival,0);c.terminal=benchmark(terminal,20);auto f=cost_fill(quantity,price,direction);f.decision_benchmark=benchmark(decision,5);f.fee_ticks_per_lot=exact::Fraction::ratio(fn,fd);std::array<CostFill,1> fills{f};auto r=take(transaction_costs(c,fills));auto& s=r.summary();std::cout<<s.execution_vwap.value->str()<<' '<<s.gross_notional.str()<<' '<<s.delay_cost.str()<<' '<<s.spread_cost.str()<<' '<<s.fees.str()<<' '<<s.slippage.str()<<' '<<s.opportunity_cost.str()<<' '<<s.implementation_shortfall.str()<<' '<<s.currency_shortfall.str()<<'\n';}
            else return 1;
        }return 0;
    }
    std::string_view group=argc==2?argv[1]:"schedules";if(group=="schedules")schedules();else if(group=="costs")costs();else if(group=="integration")integration();else return 1;std::cout<<"PASS: "<<group<<", "<<checks<<" checks\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
