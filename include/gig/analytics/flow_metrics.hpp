#pragma once
#include <span>
#include <vector>
#include "gig/analytics/book_metrics.hpp"
namespace gig::analytics {
struct FlowQuote {
    SnapshotReference source; EventTimestamp timestamp; Identity utc_clock;
    std::optional<DepthLevel> bid,ask;
};
struct FlowTrade {
    SnapshotReference source; EventTimestamp timestamp; Identity utc_clock;
    PriceTicks price; QuantityLots quantity;
};
struct FlowConfig {
    Identity utc_clock;
    Duration window,quote_lag,horizon,max_quote_age,sampling_interval;
    bool continuity_complete{true},complete_top_updates{true};
};
enum class TradeSign { unknown, buy, sell };
struct SignedTrade {
    SnapshotReference source; TradeSign sign; Metric effective_spread,realized_spread,price_impact;
};
struct FlowSummary {
    Metric ofi,trade_intensity,quote_intensity,window_return,realized_variance;
    std::optional<long double> realized_volatility; // explicitly approximate sqrt(variance)
};
class FlowMetrics {
    FlowConfig config_;EventTimestamp as_of_;FlowSummary summary_;
    std::pmr::vector<SignedTrade> trades_;std::pmr::vector<SnapshotReference> parents_;
public:
    FlowMetrics(FlowConfig c,EventTimestamp t,FlowSummary s,std::pmr::vector<SignedTrade> trades,std::pmr::vector<SnapshotReference> parents)
        :config_(c),as_of_(t),summary_(s),trades_(std::move(trades)),parents_(std::move(parents)) {}
    const FlowConfig& config() const noexcept {return config_;}
    EventTimestamp as_of() const noexcept {return as_of_;}
    const FlowSummary& summary() const noexcept {return summary_;}
    const std::pmr::vector<SignedTrade>& trades() const noexcept {return trades_;}
    const std::pmr::vector<SnapshotReference>& parents() const noexcept {return parents_;}
};
Result<FlowQuote> quote_observation(const ReplaySnapshot&,EventTimestamp,Identity utc_clock) noexcept;
// Pure, bounded window calculation; full context inputs are retained by parent references.
Result<FlowMetrics> calculate_flow(std::span<const FlowQuote>,std::span<const FlowTrade>,FlowConfig,EventTimestamp as_of,std::pmr::memory_resource* resource=std::pmr::get_default_resource()) noexcept;
} // namespace gig::analytics
