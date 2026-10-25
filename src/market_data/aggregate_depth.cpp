#include "gig/market_data/aggregate_depth.hpp"
#include <algorithm>
#include <limits>
#include <stdexcept>
namespace gig::market_data {
namespace {
Result<Metrics> calculate(std::span<const Level>bids,std::span<const Level>asks) {
    try {
        using exact::Fraction;using exact::Wide;Metrics m;Wide bq=0,aq=0;
        for(const auto& l:bids)bq=exact::checked_add(bq,static_cast<Wide>(l.quantity));
        for(const auto& l:asks)aq=exact::checked_add(aq,static_cast<Wide>(l.quantity));
        m.bid_depth=Fraction::whole(bq);m.ask_depth=Fraction::whole(aq);
        if(bq!=0||aq!=0)m.depth_imbalance=Fraction::ratio(bq-aq,exact::checked_add(bq,aq));
        if(!bids.empty()&&!asks.empty()) {
            const auto b=static_cast<Wide>(bids.front().price_ticks),a=static_cast<Wide>(asks.front().price_ticks);
            const auto btop=static_cast<Wide>(bids.front().quantity),atop=static_cast<Wide>(asks.front().quantity);
            m.spread=Fraction::whole(a-b);m.midpoint=Fraction::ratio(a+b,2);
            // Reduce the quantity weight before multiplication; equal very large
            // sizes must not overflow an avoidable unreduced weighted sum.
            m.microprice=Fraction::whole(b)+Fraction::whole(a-b)*Fraction::ratio(btop,exact::checked_add(btop,atop));
            m.locked=a==b;m.crossed=a<b;
        }
        return Result<Metrics>::success(std::move(m));
    }catch(const exact::ArithmeticFailure&e){return Result<Metrics>::failure(e.code,"aggregate.metrics");}
}
}
AggregateDepth::AggregateDepth(std::size_t limit,std::pmr::memory_resource*r):limit_(limit),resource_(r?r:std::pmr::get_default_resource()),bids_(resource_),asks_(resource_) {
    if(!r||limit==0||limit>4096)throw std::invalid_argument("aggregate.max_levels");
}
Error AggregateDepth::apply(std::span<const Level> bids,std::span<const Level>asks,std::optional<std::uint64_t> sequence,bool snapshot) {
    if(!snapshot&&!initialized_)return {ErrorCode::recovery_required,"aggregate.snapshot_required"};
    if(revision_==std::numeric_limits<std::uint64_t>::max())return {ErrorCode::overflow,"aggregate.revision"};
    if(!snapshot) {
        if(sequence.has_value()!=sequence_.has_value())return {ErrorCode::inconsistent_metadata,"aggregate.sequence_presence"};
        if(sequence_) {
            if(*sequence_==std::numeric_limits<std::uint64_t>::max())return {ErrorCode::sequence_exhausted,"aggregate.sequence"};
            if(*sequence<*sequence_)return {ErrorCode::sequence_regression,"aggregate.sequence"};
            if(*sequence==*sequence_)return {ErrorCode::sequence_duplicate,"aggregate.sequence"};
            if(*sequence!=*sequence_+1)return {ErrorCode::sequence_gap,"aggregate.sequence"};
        }
    }
    if(bids.size()>limit_||asks.size()>limit_)return {ErrorCode::capacity,"aggregate.update_count"};
    try {
        std::pmr::vector<Level> next_bids(resource_),next_asks(resource_);
        next_bids.reserve(limit_);next_asks.reserve(limit_);
        if(!snapshot){next_bids.assign(bids_.begin(),bids_.end());next_asks.assign(asks_.begin(),asks_.end());}
        auto modify=[&](auto& out,std::span<const Level> updates,bool descending)->Error {
            for(std::size_t i=0;i<updates.size();++i){
                const auto x=updates[i];if(x.price_ticks<=0)return {ErrorCode::invalid_range,"aggregate.price",i};
                if(snapshot&&x.quantity==0)return {ErrorCode::invalid_range,"aggregate.snapshot_quantity",i};
                for(std::size_t j=0;j<i;++j)if(updates[j].price_ticks==x.price_ticks)return {ErrorCode::duplicate,"aggregate.price",i};
            }
            // Absolute updates are a single transaction; delete first so a full
            // book can replace a level regardless of update-list ordering.
            for(const auto x:updates)if(x.quantity==0){const auto it=std::find_if(out.begin(),out.end(),[&](const auto&v){return v.price_ticks==x.price_ticks;});if(it!=out.end())out.erase(it);}
            for(const auto x:updates)if(x.quantity!=0){
                auto it=std::find_if(out.begin(),out.end(),[&](const auto&v){return v.price_ticks==x.price_ticks;});
                if(it!=out.end())it->quantity=x.quantity;
                else {if(out.size()==limit_)return {ErrorCode::capacity,"aggregate.depth"};out.push_back(x);}
            }
            std::sort(out.begin(),out.end(),[&](const auto&a,const auto&b){return descending?a.price_ticks>b.price_ticks:a.price_ticks<b.price_ticks;});return {};
        };
        if(auto e=modify(next_bids,bids,true))return e;
        if(auto e=modify(next_asks,asks,false))return e;
        if(auto m=calculate(next_bids,next_asks);!m)return m.error;
        bids_.swap(next_bids);asks_.swap(next_asks);sequence_=sequence;++revision_;initialized_=true;return {};
    }catch(const std::bad_alloc&){return {ErrorCode::resource_exhausted,"aggregate.memory"};}
}
Result<Metrics> AggregateDepth::metrics()const{return calculate(bids_,asks_);}
}
