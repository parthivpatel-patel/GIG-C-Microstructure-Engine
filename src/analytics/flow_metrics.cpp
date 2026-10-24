#include "gig/analytics/flow_metrics.hpp"
#include <cmath>
namespace gig::analytics {
namespace {
using exact::Fraction;using exact::Wide;
Metric unavailable(Unavailable reason) {return Metric::missing(reason);}
Metric safe_metric(auto calculation) {
    try {return Metric::known(calculation());}catch(const exact::ArithmeticFailure&){return unavailable(Unavailable::arithmetic_capacity);}
}
std::optional<Fraction> midpoint(const FlowQuote* q) {
    if (!q || !q->bid || !q->ask) return {};
    return (Fraction(q->bid->price_ticks.value())+Fraction(q->ask->price_ticks.value()))/Fraction(2);
}
const FlowQuote* quote_at(std::span<const FlowQuote> quotes,Wide time,Wide max_age,std::optional<std::size_t> prefix={}) {
    const FlowQuote* found=nullptr;
    for (const auto& q:quotes) {
        if (static_cast<Wide>(q.timestamp.value())<=time && (!prefix || q.source.journal_prefix<*prefix)) found=&q;
        if (static_cast<Wide>(q.timestamp.value())>time) break;
    }
    return found && time-static_cast<Wide>(found->timestamp.value())<=max_age?found:nullptr;
}
bool same_scope(const SnapshotReference& a,const SnapshotReference& b) {
    return a.run_id==b.run_id && a.rules==b.rules && a.session==b.session;
}
Error validate_inputs(std::span<const FlowQuote> quotes,std::span<const FlowTrade> trades,const FlowConfig& c,EventTimestamp asof) {
    if (quotes.size()>4096 || trades.size()>4096) return {ErrorCode::capacity,"flow.observations"};
    if (c.window.value()==0 || c.sampling_interval.value()==0 || c.window.value()%c.sampling_interval.value()!=0 || c.window.value()/c.sampling_interval.value()>4096) return {ErrorCode::invalid_range,"flow.window_or_sampling"};
    const SnapshotReference* scope=quotes.empty()?(trades.empty()?nullptr:&trades.front().source):&quotes.front().source;
    auto validate_order=[&](const auto& list)->Error {
        for (std::size_t i=0;i<list.size();++i) {
            const auto& x=list[i];
            if (!same_scope(*scope,x.source)) return {ErrorCode::session_boundary,"flow.scope",i};
            if (x.utc_clock!=c.utc_clock) return {ErrorCode::identity_mismatch,"flow.utc_clock",i};
            if (x.timestamp>asof) return {ErrorCode::ordering_error,"flow.future_observation",i};
            if (const auto e=validate(x.source.rules)) return e;
            if (i && (x.timestamp<list[i-1].timestamp || x.source.journal_prefix<=list[i-1].source.journal_prefix || x.source.revision<list[i-1].source.revision)) return {ErrorCode::ordering_error,"flow.order",i};
        }return {};
    };
    if (auto e=validate_order(quotes)) return e;
    if (auto e=validate_order(trades)) return e;
    // Check combined source/time monotonicity without sorting or quadratic scans.
    std::size_t q=0,t=0;std::optional<std::int64_t> last_time;std::optional<std::size_t> last_prefix;std::optional<std::uint64_t> last_revision;
    while(q<quotes.size() || t<trades.size()) {
        const bool use_quote=t==trades.size() || (q<quotes.size() && quotes[q].source.journal_prefix<=trades[t].source.journal_prefix);
        const auto time=use_quote?quotes[q].timestamp.value():trades[t].timestamp.value();
        const auto revision=use_quote?quotes[q].source.revision:trades[t].source.revision;
        const auto prefix=use_quote?quotes[q++].source.journal_prefix:trades[t++].source.journal_prefix;
        if(last_time && (time<*last_time || revision<*last_revision || (last_prefix==prefix && (time!=*last_time || revision!=*last_revision)))) return {ErrorCode::ordering_error,"flow.combined_order"};
        last_time=time;last_prefix=prefix;last_revision=revision;
    }
    for(const auto& x:quotes) {
        for(const auto& side:{x.bid,x.ask}) if(side && (side->quantity.value()==0 || side->order_count==0 || side->order_count>side->quantity.value() || side->price_ticks<x.source.rules.minimum_price || side->price_ticks>x.source.rules.maximum_price)) return {ErrorCode::invalid_range,"flow.quote"};
        if(x.bid && x.ask && x.bid->price_ticks>x.ask->price_ticks) return {ErrorCode::crossed_quote,"flow.quote"};
        if(x.bid && x.ask && static_cast<Wide>(x.bid->quantity.value())+static_cast<Wide>(x.ask->quantity.value())>static_cast<Wide>(UINT64_MAX)) return {ErrorCode::overflow,"flow.quote_quantity"};
    }
    for(const auto& x:trades) if(x.quantity.value()==0 || x.quantity>x.source.rules.maximum_quantity || x.price<x.source.rules.minimum_price || x.price>x.source.rules.maximum_price) return {ErrorCode::invalid_range,"flow.trade"};
    return {};
}
}
Result<FlowQuote> quote_observation(const ReplaySnapshot& s,EventTimestamp time,Identity clock) noexcept {
    auto m=calculate(s,1);if(!m)return Result<FlowQuote>::failure(m.error.code,m.error.field);
    return Result<FlowQuote>::success({m.data->source(),time,clock,s.book.bids.empty()?std::nullopt:std::optional<DepthLevel>(s.book.bids.front()),s.book.asks.empty()?std::nullopt:std::optional<DepthLevel>(s.book.asks.front())});
}
Result<FlowMetrics> calculate_flow(std::span<const FlowQuote> quotes,std::span<const FlowTrade> trades,FlowConfig config,EventTimestamp asof,std::pmr::memory_resource* resource) noexcept {
    if(!resource)return Result<FlowMetrics>::failure(ErrorCode::invalid_range,"flow.resource");
    if(auto e=validate_inputs(quotes,trades,config,asof))return Result<FlowMetrics>::failure(e.code,e.field,e.index);
    try {
        const Wide end=asof.value(),start=end-config.window.value(),age=config.max_quote_age.value();
        const auto absent=config.continuity_complete?Unavailable::missing_observation:Unavailable::gap_or_reset;
        FlowSummary summary{unavailable(absent),unavailable(absent),unavailable(absent),unavailable(absent),unavailable(absent),std::nullopt};
        std::pmr::vector<SignedTrade> signed_trades(resource);std::pmr::vector<SnapshotReference> parents(resource);parents.reserve(quotes.size()+trades.size());
        for(const auto& q:quotes)parents.push_back(q.source);
        for(const auto& t:trades)parents.push_back(t.source);
        std::size_t quote_count=0,trade_count=0;
        for(const auto& q:quotes)if(q.timestamp.value()>start)++quote_count;
        for(const auto& t:trades)if(t.timestamp.value()>start)++trade_count;
        if(config.continuity_complete) {
            summary.trade_intensity=Metric::known(Fraction::ratio(exact::checked_mul(static_cast<Wide>(trade_count),1000000000),config.window.value()));
            summary.quote_intensity=Metric::known(Fraction::ratio(exact::checked_mul(static_cast<Wide>(quote_count),1000000000),config.window.value()));
            Wide ofi=0;bool valid=config.complete_top_updates;const FlowQuote* previous=nullptr;
            for(const auto& q:quotes) {
                if(q.timestamp.value()>start) {
                    if(!previous || !midpoint(previous) || !midpoint(&q) || static_cast<Wide>(q.timestamp.value())-previous->timestamp.value()>age)valid=false;
                    else {
                        if(q.bid->price_ticks>=previous->bid->price_ticks)ofi+=static_cast<Wide>(q.bid->quantity.value());
                        if(q.bid->price_ticks<=previous->bid->price_ticks)ofi-=static_cast<Wide>(previous->bid->quantity.value());
                        if(q.ask->price_ticks<=previous->ask->price_ticks)ofi-=static_cast<Wide>(q.ask->quantity.value());
                        if(q.ask->price_ticks>=previous->ask->price_ticks)ofi+=static_cast<Wide>(previous->ask->quantity.value());
                    }
                }previous=&q;
            }
            if(previous && end-static_cast<Wide>(previous->timestamp.value())>age)valid=false;
            if(valid && previous && static_cast<Wide>(previous->timestamp.value())<=start) summary.ofi=Metric::known(Fraction(0));
            else if(valid && previous)summary.ofi=Metric::known(Fraction::whole(ofi));
            const auto first=midpoint(quote_at(quotes,start,age)),last=midpoint(quote_at(quotes,end,age));
            if(first && last && first->numerator()>0 && last->numerator()>0) summary.window_return=safe_metric([&]{return *last/ *first-Fraction(1);});
            else if(first && last)summary.window_return=unavailable(first->numerator()==0?Unavailable::zero_denominator:Unavailable::nonpositive_reference);
            bool valid_sampling=true;Fraction variance;auto previous_mid=first;
            for(Wide time=start+config.sampling_interval.value();time<=end;time+=config.sampling_interval.value()) {
                auto current=midpoint(quote_at(quotes,time,age));
                if(!previous_mid || !current || previous_mid->numerator()<=0 || current->numerator()<=0) {
                    valid_sampling=false;
                    if(previous_mid && current)summary.realized_variance=unavailable(previous_mid->numerator()==0?Unavailable::zero_denominator:Unavailable::nonpositive_reference);
                }
                else if(valid_sampling) {try{auto r=*current/ *previous_mid-Fraction(1);variance=variance+r*r;}catch(const exact::ArithmeticFailure&){valid_sampling=false;summary.realized_variance=unavailable(Unavailable::arithmetic_capacity);}}
                previous_mid=current;
            }
            if(config.window.value()<config.sampling_interval.value())valid_sampling=false;
            if(valid_sampling) {
                summary.realized_variance=Metric::known(variance);
                const auto value=std::sqrt(static_cast<long double>(variance.numerator())/static_cast<long double>(variance.denominator()));
                if(std::isfinite(value))summary.realized_volatility=value;
            }
        }
        int tick_sign=0;std::optional<std::int64_t> previous_trade;
        signed_trades.reserve(trade_count);
        for(const auto& t:trades) {
            if(previous_trade && t.price.value()!=*previous_trade)tick_sign=t.price.value()>*previous_trade?1:-1;
            previous_trade=t.price.value();
            if(t.timestamp.value()<=start)continue;
            SignedTrade result{t.source,TradeSign::unknown,unavailable(absent),unavailable(absent),unavailable(absent)};
            if(config.continuity_complete) {
                const auto lagged=midpoint(quote_at(quotes,static_cast<Wide>(t.timestamp.value())-config.quote_lag.value(),age,t.source.journal_prefix));
                int sign=0;
                if(lagged) {
                    const auto price_twice=exact::checked_mul(static_cast<Wide>(t.price.value()),lagged->denominator());
                    sign=price_twice>lagged->numerator()?1:(price_twice<lagged->numerator()?-1:tick_sign);
                }
                if(sign) {
                    result.sign=sign>0?TradeSign::buy:TradeSign::sell;
                    auto now=midpoint(quote_at(quotes,t.timestamp.value(),age,t.source.journal_prefix));
                    if(now)result.effective_spread=safe_metric([&]{return Fraction(2*sign)*(Fraction(t.price.value())-*now);});
                    const Wide horizon=static_cast<Wide>(t.timestamp.value())+config.horizon.value();
                    if(horizon>end) {result.realized_spread=unavailable(Unavailable::horizon_pending);result.price_impact=unavailable(Unavailable::horizon_pending);}
                    else {
                        const auto future=midpoint(quote_at(quotes,horizon,age,config.horizon.value()==0?std::optional<std::size_t>(t.source.journal_prefix):std::nullopt));
                        if(future)result.realized_spread=safe_metric([&]{return Fraction(2*sign)*(Fraction(t.price.value())-*future);});
                        if(now && future)result.price_impact=safe_metric([&]{return Fraction(2*sign)*(*future-*now);});
                    }
                }else {result.effective_spread=unavailable(Unavailable::unknown_direction);result.realized_spread=unavailable(Unavailable::unknown_direction);result.price_impact=unavailable(Unavailable::unknown_direction);}
            }
            signed_trades.push_back(result);
        }
        return Result<FlowMetrics>::success(FlowMetrics(config,asof,summary,std::move(signed_trades),std::move(parents)));
    }catch(const std::bad_alloc&){return Result<FlowMetrics>::failure(ErrorCode::resource_exhausted,"flow.output");}
     catch(const exact::ArithmeticFailure& e){return Result<FlowMetrics>::failure(e.code,"flow.exact_capacity");}
}
} // namespace gig::analytics
