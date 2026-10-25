#pragma once
#include <cstdint>
#include <memory_resource>
#include <optional>
#include <span>
#include <vector>
#include "gig/analytics/exact.hpp"
namespace gig::market_data {
// Aggregate displayed price levels only: no order IDs, executions or FIFO inference.
struct Level {std::int64_t price_ticks{};std::uint64_t quantity{};bool operator==(const Level&)const=default;};
struct Metrics {
    std::optional<exact::Fraction> spread,midpoint,microprice,depth_imbalance;
    exact::Fraction bid_depth,ask_depth;
    bool locked{},crossed{};
};
class AggregateDepth {
    std::size_t limit_;std::pmr::memory_resource* resource_;
    std::pmr::vector<Level> bids_,asks_;
    std::optional<std::uint64_t> sequence_;
    std::uint64_t revision_{};bool initialized_{};
    Error apply(std::span<const Level>,std::span<const Level>,std::optional<std::uint64_t>,bool);
public:
    explicit AggregateDepth(std::size_t max_levels=1024,std::pmr::memory_resource* resource=std::pmr::get_default_resource());
    Error snapshot(std::span<const Level> bids,std::span<const Level> asks,std::optional<std::uint64_t> sequence={}) {return apply(bids,asks,sequence,true);}
    Error update(std::span<const Level> bids,std::span<const Level> asks,std::optional<std::uint64_t> sequence={}) {return apply(bids,asks,sequence,false);}
    std::span<const Level> bids()const noexcept{return bids_;}
    std::span<const Level> asks()const noexcept{return asks_;}
    std::uint64_t revision()const noexcept{return revision_;}
    std::optional<std::uint64_t> sequence()const noexcept{return sequence_;}
    bool initialized()const noexcept{return initialized_;}
    Result<Metrics> metrics()const;
};
}
