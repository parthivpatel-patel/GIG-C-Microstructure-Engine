#include "gig/analytics/book_metrics.hpp"
namespace gig::analytics {
Result<BookMetrics> calculate(const ReplaySnapshot& snapshot,std::size_t depth) noexcept {
    using exact::Fraction;using exact::Wide;
    const auto& b=snapshot.book;
    if (depth==0 || depth>b.requested_depth) return Result<BookMetrics>::failure(ErrorCode::invalid_range,"analytics.depth");
    if (const auto e=validate(b.rules)) return Result<BookMetrics>::failure(e.code,e.field);
    Wide total=0;
    for (bool bid:{true,false}) {
        const auto& levels=bid?b.bids:b.asks;
        if (levels.size()>b.requested_depth || ((bid?b.bid_truncated:b.ask_truncated) && levels.size()!=b.requested_depth)) return Result<BookMetrics>::failure(ErrorCode::inconsistent_state,"snapshot.depth");
        for (std::size_t i=0;i<levels.size();++i) {
            const auto& l=levels[i];
            if (l.quantity.value()==0 || l.order_count==0 || l.order_count>l.quantity.value() || l.price_ticks<b.rules.minimum_price || l.price_ticks>b.rules.maximum_price)
                return Result<BookMetrics>::failure(ErrorCode::invalid_range,"snapshot.level");
            if (i && (bid?levels[i-1].price_ticks<=l.price_ticks:levels[i-1].price_ticks>=l.price_ticks)) return Result<BookMetrics>::failure(ErrorCode::inconsistent_state,"snapshot.level_order");
            total+=static_cast<Wide>(l.quantity.value());
            if (total>static_cast<Wide>(UINT64_MAX)) return Result<BookMetrics>::failure(ErrorCode::overflow,"snapshot.total");
        }
    }
    if (!b.bids.empty() && !b.asks.empty() && b.bids.front().price_ticks>b.asks.front().price_ticks) return Result<BookMetrics>::failure(ErrorCode::crossed_quote,"snapshot");
    std::array<Metric,static_cast<std::size_t>(BookMetric::count)> m;
    const auto set=[&](BookMetric k,Metric v){m[static_cast<std::size_t>(k)]=v;};
    auto missing=b.bids.empty() && b.asks.empty()?Unavailable::empty_book:Unavailable::one_sided;
    for (auto& v:m) v=Metric::missing(missing);
    try {
        if (!b.bids.empty()) set(BookMetric::best_bid,Metric::known(Fraction(b.bids.front().price_ticks.value())));
        if (!b.asks.empty()) set(BookMetric::best_ask,Metric::known(Fraction(b.asks.front().price_ticks.value())));
        if (!b.bids.empty() && !b.asks.empty()) {
            const auto bid=Fraction(b.bids.front().price_ticks.value()),ask=Fraction(b.asks.front().price_ticks.value());
            const auto bq=Fraction::whole(b.bids.front().quantity.value()),aq=Fraction::whole(b.asks.front().quantity.value());
            set(BookMetric::spread,Metric::known(ask-bid));set(BookMetric::midpoint,Metric::known((ask+bid)/Fraction(2)));
            set(BookMetric::microprice,Metric::known((ask*bq+bid*aq)/(bq+aq)));
            set(BookMetric::top_imbalance,Metric::known((bq-aq)/(bq+aq)));
        }
        Wide bid_sum=0,ask_sum=0;
        for (std::size_t i=0;i<std::min(depth,b.bids.size());++i) bid_sum+=static_cast<Wide>(b.bids[i].quantity.value());
        for (std::size_t i=0;i<std::min(depth,b.asks.size());++i) ask_sum+=static_cast<Wide>(b.asks[i].quantity.value());
        // Aggregate existing displayed levels; strict D-level imbalance requires D on both sides.
        set(BookMetric::bid_depth,Metric::known(Fraction::whole(bid_sum)));set(BookMetric::ask_depth,Metric::known(Fraction::whole(ask_sum)));
        if (b.bids.size()<depth || b.asks.size()<depth) set(BookMetric::depth_imbalance,Metric::missing(missing==Unavailable::empty_book?missing:Unavailable::insufficient_depth));
        else if (bid_sum+ask_sum==0) set(BookMetric::depth_imbalance,Metric::missing(Unavailable::zero_denominator));
        else set(BookMetric::depth_imbalance,Metric::known(Fraction::ratio(bid_sum-ask_sum,bid_sum+ask_sum)));
        return Result<BookMetrics>::success(BookMetrics({snapshot.run_id,snapshot.journal_prefix,b.revision,b.rules,b.session},depth,m));
    } catch (const exact::ArithmeticFailure& e) {return Result<BookMetrics>::failure(e.code,"analytics.exact_capacity");}
}
} // namespace gig::analytics
