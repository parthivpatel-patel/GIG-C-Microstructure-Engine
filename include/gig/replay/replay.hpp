#pragma once
#include <span>
#include "gig/book/order_book.hpp"

namespace gig {
enum class InitialBookState : std::uint8_t { requires_snapshot, declared_empty };
enum class OrderingPolicy : std::uint8_t { capture_ordinal, timestamp_rank };
struct StreamStart {
    VenueId venue; StreamScope scope; Identity dataset; Identity dataset_version;
    SequenceNumber first_sequence; std::uint32_t rank;
    bool operator==(const StreamStart&) const = default;
};
using RestartPlan=BoundedList<StreamStart,8>;
struct ReplayConfig {
    Identity run_id; BookSession session; RestartPlan streams;
    OrderingPolicy ordering{OrderingPolicy::capture_ordinal};
    Available<Identity> timestamp_clock{};
    BoundedList<InstrumentRules,8> additional_instruments{};
    std::size_t max_journal_records{4096};
    InitialBookState initial_state{InitialBookState::requires_snapshot};
    bool operator==(const ReplayConfig&) const = default;
};
struct StreamCursor {
    StreamStart start; SequenceNumber expected;
    std::uint32_t next_subevent{},message_count{};
    std::optional<SequenceNumber> last_sequence;
    std::uint32_t last_subevent{},last_message_count{};
    bool exhausted{};
    bool operator==(const StreamCursor&) const = default;
};
enum class JournalDisposition : std::uint8_t { book_event, filtered_instrument, reset, recovery };
struct JournalEntry {
    MarketEvent event; JournalDisposition disposition; std::optional<RestartPlan> restart;
    bool operator==(const JournalEntry&) const = default;
};
struct ReplaySnapshot {
    Identity run_id; std::size_t journal_prefix; DepthSnapshot book;
    // Resolve lineage against this run's canonical journal archive, not latest input alone.
};
struct ReplayBatchResult {
    std::size_t accepted{}; Error error{}; std::optional<std::size_t> failed_input_index{};
    explicit operator bool() const noexcept { return !error; }
};
class ReplayEngine {
    struct OrderKey {
        std::int64_t timestamp; std::uint32_t rank; std::uint64_t sequence; std::uint32_t subevent;
        auto operator<=>(const OrderKey&) const = default;
    };
    OrderBook book_;
    ReplayConfig config_;
    BoundedList<StreamCursor,8> cursors_;
    std::pmr::memory_resource* resource_;
    std::pmr::vector<JournalEntry> journal_;
    std::optional<std::uint64_t> last_ordinal_;
    std::optional<OrderKey> last_key_;
    std::optional<Error> continuity_error_;
    ReplayEngine(OrderBook,ReplayConfig,std::pmr::memory_resource*) noexcept;
    std::optional<std::size_t> stream_index(StreamId) const noexcept;
    Result<StreamCursor> advance(const StreamCursor&,const Metadata&) const noexcept;
    Error order_check(const Metadata&,std::uint32_t) const noexcept;
    void order_commit(const Metadata&,std::uint32_t) noexcept;
    Error reserve_record() noexcept;
    Error source_check(const StreamStart&,const Metadata&,bool allow_new_scope=false) const noexcept;
    const InstrumentRules* instrument_rules(const Metadata&) const noexcept;
    Error stop(Error) noexcept;
public:
    static Result<ReplayEngine> create(InstrumentRules,ReplayConfig,BookLimits={},
        std::pmr::memory_resource* resource=std::pmr::get_default_resource()) noexcept;
    ReplayEngine(ReplayEngine&&) noexcept=default;
    ReplayEngine& operator=(ReplayEngine&&)=delete;
    ReplayEngine(const ReplayEngine&)=delete;
    ReplayEngine& operator=(const ReplayEngine&)=delete;
    Error apply(const MarketEvent&) noexcept;
    ReplayBatchResult run(std::span<const MarketEvent>) noexcept;
    Error reset(const MarketEvent&,const RestartPlan&) noexcept;
    Error recover(const MarketEvent&) noexcept;
    const OrderBook& book() const noexcept { return book_; }
    std::size_t journal_size() const noexcept { return journal_.size(); }
    bool needs_recovery() const noexcept { return continuity_error_.has_value(); }
    std::optional<StreamCursor> cursor(StreamId) const noexcept;
    Result<ReplaySnapshot> depth(std::size_t) const noexcept;
    Result<std::pmr::string> canonical() const noexcept;
};
} // namespace gig
