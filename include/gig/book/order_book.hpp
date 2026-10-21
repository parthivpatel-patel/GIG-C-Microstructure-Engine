#pragma once
#include <memory>
#include <memory_resource>
#include <optional>
#include <string>
#include <vector>
#include "gig/market_event.hpp"

namespace gig {
struct BookSession { Identity session; std::uint64_t epoch; bool operator==(const BookSession&) const = default; };
struct BookLimits {
    std::size_t max_orders{100000},max_levels{10000},max_snapshot_depth{10000};
    bool operator==(const BookLimits&) const = default;
};
struct QuantityLedger {
    std::uint64_t added{},cancelled{},executed{},discarded{},recovered{},replacement_in{},replacement_out{},total_in{},total_out{};
    bool operator==(const QuantityLedger&) const = default;
};
struct DepthLevel {
    PriceTicks price_ticks; QuantityLots quantity; std::uint64_t order_count;
    bool operator==(const DepthLevel&) const = default;
};
struct DepthSnapshot {
    InstrumentRules rules; BookSession session; std::uint64_t revision; std::size_t requested_depth;
    bool bid_truncated{},ask_truncated{};
    std::pmr::vector<DepthLevel> bids,asks;
    // Replay journal (run ID, prefix count, book revision) supplies complete lineage.
    DepthSnapshot(InstrumentRules r,BookSession s,std::uint64_t rev,std::size_t depth,std::pmr::memory_resource* resource)
        : rules(r),session(s),revision(rev),requested_depth(depth),bids(resource),asks(resource) {}
};
struct RestingOrder { AddOrder order; std::uint64_t priority; bool operator==(const RestingOrder&) const = default; };
class OrderBook {
    struct State;
    struct Deleter { std::pmr::memory_resource* resource; void operator()(State*) const noexcept; };
    using StatePtr=std::unique_ptr<State,Deleter>;
    InstrumentRules rules_;
    BookLimits limits_;
    std::pmr::memory_resource* resource_;
    StatePtr state_;
    std::optional<Metadata> last_metadata_;
    OrderBook(InstrumentRules,BookLimits,std::pmr::memory_resource*,StatePtr) noexcept;
    static StatePtr allocate_state(BookSession,std::pmr::memory_resource*);
public:
    static Result<OrderBook> create(InstrumentRules,BookSession,BookLimits={},
        std::pmr::memory_resource* resource=std::pmr::get_default_resource()) noexcept;
    ~OrderBook();
    OrderBook(OrderBook&&) noexcept;
    OrderBook& operator=(OrderBook&&) noexcept;
    OrderBook(const OrderBook&)=delete;
    OrderBook& operator=(const OrderBook&)=delete;
    // No implicit recovery and no matching. Reset may explicitly change session.
    Error apply(const MarketEvent&,std::optional<BookSession> reset_session=std::nullopt) noexcept;
    Error recover(const MarketEvent&,BookSession) noexcept;
    Error check_invariants() const noexcept;
    const InstrumentRules& rules() const noexcept { return rules_; }
    const BookLimits& limits() const noexcept { return limits_; }
    const BookSession& session() const noexcept;
    std::uint64_t revision() const noexcept;
    std::uint64_t remaining() const noexcept;
    std::size_t order_count() const noexcept;
    QuantityLedger ledger() const noexcept;
    const std::optional<Metadata>& last_metadata() const noexcept { return last_metadata_; }
    std::optional<RestingOrder> find(OrderId) const noexcept;
    std::optional<DepthLevel> best_bid() const noexcept;
    std::optional<DepthLevel> best_ask() const noexcept;
    Result<DepthSnapshot> depth(std::size_t requested) const noexcept;
    Result<std::pmr::string> canonical() const noexcept;
};
} // namespace gig
