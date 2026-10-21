#pragma once
#include <array>
#include "gig/analytics/exact.hpp"
#include "gig/replay/replay.hpp"
namespace gig::analytics {
enum class Unavailable { none, empty_book, one_sided, insufficient_depth, zero_denominator, missing_observation, gap_or_reset, horizon_pending, unknown_direction, arithmetic_capacity, nonpositive_reference };
struct Metric {
    std::optional<exact::Fraction> value;
    Unavailable unavailable{Unavailable::missing_observation};
    static Metric known(exact::Fraction x) noexcept {return {x,Unavailable::none};}
    static Metric missing(Unavailable why) noexcept {return {std::nullopt,why};}
    bool operator==(const Metric&) const = default;
};
struct SnapshotReference {
    Identity run_id; std::size_t journal_prefix; std::uint64_t revision;
    InstrumentRules rules; BookSession session;
    bool operator==(const SnapshotReference&) const = default;
};
enum class BookMetric : std::size_t { best_bid, best_ask, spread, midpoint, microprice, top_imbalance, bid_depth, ask_depth, depth_imbalance, count };
class BookMetrics {
    SnapshotReference source_;std::size_t depth_;
    std::array<Metric,static_cast<std::size_t>(BookMetric::count)> metrics_;
public:
    BookMetrics(SnapshotReference source,std::size_t depth,decltype(metrics_) values) noexcept :source_(source),depth_(depth),metrics_(values) {}
    const SnapshotReference& source() const noexcept {return source_;}
    std::size_t depth() const noexcept {return depth_;}
    const Metric& get(BookMetric key) const {return metrics_.at(static_cast<std::size_t>(key));}
};
// Pure calculation over owned snapshot; malformed snapshot is a structured failure.
Result<BookMetrics> calculate(const ReplaySnapshot&,std::size_t depth) noexcept;
} // namespace gig::analytics
