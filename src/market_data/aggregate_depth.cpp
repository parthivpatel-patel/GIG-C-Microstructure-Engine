#include "gig/market_data/aggregate_depth.hpp"
#include <algorithm>
#include <array>
#include <numeric>
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
        std::array<std::size_t,4096> order;
        auto merge=[&](auto& out,std::span<const Level> before,std::span<const Level> updates,bool descending)->Error {
            const auto precedes=[&](std::int64_t left,std::int64_t right){return descending?left>right:left<right;};
            Error invalid{};
            std::size_t first_invalid=updates.size();
            for(std::size_t i=0;i<updates.size();++i){
                if(updates[i].price_ticks<=0){invalid={ErrorCode::invalid_range,"aggregate.price",i};first_invalid=i;break;}
                if(snapshot&&updates[i].quantity==0){invalid={ErrorCode::invalid_range,"aggregate.snapshot_quantity",i};first_invalid=i;break;}
            }
            auto end=order.begin()+static_cast<std::ptrdiff_t>(first_invalid);
            std::iota(order.begin(),end,std::size_t{0});
            std::sort(order.begin(),end,[&](auto i,auto j){
                const auto left=updates[i].price_ticks,right=updates[j].price_ticks;
                return left==right?i<j:precedes(left,right);
            });
            auto duplicate=first_invalid;
            for(std::size_t i=1;i<first_invalid;++i)
                if(updates[order[i]].price_ticks==updates[order[i-1]].price_ticks)
                    duplicate=std::min(duplicate,order[i]);
            if(duplicate<first_invalid)return {ErrorCode::duplicate,"aggregate.price",duplicate};
            if(invalid)return invalid;
            if(snapshot)before={};

            // Merge one sorted patch with the existing sorted side. The patch
            // already includes deletions, so the bound applies to the final side.
            std::size_t previous=0,change=0;
            while(previous<before.size()||change<updates.size()){
                Level next;
                if(change==updates.size()||(previous<before.size()&&
                    precedes(before[previous].price_ticks,updates[order[change]].price_ticks))){
                    next=before[previous++];
                }else{
                    next=updates[order[change++]];
                    if(previous<before.size()&&before[previous].price_ticks==next.price_ticks)++previous;
                }
                if(!next.quantity)continue;
                if(out.size()==limit_)return {ErrorCode::capacity,"aggregate.depth"};
                out.push_back(next);
            }
            return {};
        };
        if(auto e=merge(next_bids,bids_,bids,true))return e;
        if(auto e=merge(next_asks,asks_,asks,false))return e;
        if(auto m=calculate(next_bids,next_asks);!m)return m.error;
        bids_.swap(next_bids);asks_.swap(next_asks);sequence_=sequence;++revision_;initialized_=true;return {};
    }catch(const std::bad_alloc&){return {ErrorCode::resource_exhausted,"aggregate.memory"};}
}
Result<Metrics> AggregateDepth::metrics()const{return calculate(bids_,asks_);}
Result<AggregateStateImage> AggregateDepth::checkpoint(std::pmr::memory_resource* resource)const noexcept {
    if(!resource)return Result<AggregateStateImage>::failure(ErrorCode::invalid_range,"aggregate.checkpoint_resource");
    try {
        AggregateStateImage image(resource);image.max_levels=limit_;image.sequence=sequence_;
        image.revision=revision_;image.initialized=initialized_;
        image.bids.assign(bids_.begin(),bids_.end());image.asks.assign(asks_.begin(),asks_.end());
        return Result<AggregateStateImage>::success(std::move(image));
    }catch(const std::bad_alloc&){return Result<AggregateStateImage>::failure(ErrorCode::resource_exhausted,"aggregate.checkpoint_memory");}
}
Result<AggregateDepth> AggregateDepth::restore(const AggregateStateImage& image,std::size_t expected,std::pmr::memory_resource* resource)noexcept {
    if(!resource||expected==0||expected>4096||image.version!=1||image.max_levels!=expected)
        return Result<AggregateDepth>::failure(ErrorCode::inconsistent_metadata,"aggregate.checkpoint_contract");
    if(image.bids.size()>expected||image.asks.size()>expected)
        return Result<AggregateDepth>::failure(ErrorCode::capacity,"aggregate.checkpoint_depth");
    if((!image.initialized&&(image.revision||image.sequence||!image.bids.empty()||!image.asks.empty()))||
       (image.initialized&&image.revision==0))
        return Result<AggregateDepth>::failure(ErrorCode::inconsistent_state,"aggregate.checkpoint_boundary");
    auto ordered=[](const auto& side,bool bid){
        for(std::size_t i=0;i<side.size();++i){
            if(side[i].price_ticks<=0||side[i].quantity==0)return false;
            if(i&&(bid?side[i-1].price_ticks<=side[i].price_ticks:side[i-1].price_ticks>=side[i].price_ticks))return false;
        }return true;
    };
    if(!ordered(image.bids,true)||!ordered(image.asks,false))
        return Result<AggregateDepth>::failure(ErrorCode::inconsistent_state,"aggregate.checkpoint_levels");
    try {
        AggregateDepth owner(expected,resource);
        if(image.initialized){
            if(const auto e=owner.snapshot(image.bids,image.asks,image.sequence))
                return Result<AggregateDepth>::failure(e.code,e.field);
            owner.revision_=image.revision;
        }
        return Result<AggregateDepth>::success(std::move(owner));
    }catch(const std::bad_alloc&){return Result<AggregateDepth>::failure(ErrorCode::resource_exhausted,"aggregate.restore_memory");}
}
}
