#pragma once
#include <array>
#include <optional>
#include <string_view>
#include <variant>
#include "gig/core/numeric.hpp"

namespace gig {
using types::PriceTicks; using types::QuantityLots; using types::OrderId;
using types::InstrumentId; using types::VenueId; using types::StreamId;
using types::SequenceNumber; using types::EventTimestamp; using types::ReceiveTimestamp;
using types::SimulationTime; using types::Duration;

// Owned bounded tokens: printable non-whitespace ASCII, no embedded NUL.
template<std::size_t N> class Token {
    std::array<char,N> bytes_{};
    std::size_t size_{};
    constexpr Token() noexcept = default;
public:
    static constexpr Result<Token> make(std::string_view input) noexcept {
        if (input.empty()) return Result<Token>::failure(ErrorCode::malformed,"token");
        if (input.size()>N) return Result<Token>::failure(ErrorCode::capacity,"token");
        Token token;
        for (std::size_t i=0;i<input.size();++i) {
            const auto c=static_cast<unsigned char>(input[i]);
            if (c<33 || c>126) return Result<Token>::failure(ErrorCode::malformed,"token",i);
            token.bytes_[i]=input[i];
        }
        token.size_=input.size(); return Result<Token>::success(token);
    }
    constexpr std::string_view view() const noexcept { return {bytes_.data(),size_}; }
    bool operator==(const Token&) const = default;
};
using Identity = Token<128>;
using Digest = Token<64>;

enum class MissingReason : std::uint8_t { none, not_reported, unavailable, not_applicable };
template<class T> struct Available {
    std::optional<T> data{};
    MissingReason reason{MissingReason::not_reported};
    static constexpr Available known(T value) noexcept(std::is_nothrow_copy_constructible_v<T>) { return {value,MissingReason::none}; }
    static constexpr Available missing(MissingReason reason) noexcept { return {std::nullopt,reason}; }
    bool operator==(const Available&) const = default;
};
template<class T,std::size_t N> struct BoundedList {
    std::array<std::optional<T>,N> items{};
    std::size_t count{};
    Error append(const T& value) noexcept(std::is_nothrow_copy_assignable_v<std::optional<T>>) {
        if (count>=N) return {ErrorCode::capacity,"list",count};
        if (items[count]) return {ErrorCode::inconsistent_metadata,"list",count};
        items[count]=value; ++count; return {};
    }
    bool operator==(const BoundedList&) const = default;
};

enum class Side : std::uint8_t { buy, sell };
enum class ClockDomain : std::uint8_t { utc, venue_utc_unsynchronized, monotonic, simulation };
struct Clock { ClockDomain domain; Identity identity; bool operator==(const Clock&) const = default; };
template<class T> struct Timestamp {
    T nanoseconds;
    Available<Clock> clock;
    Available<types::TimestampUnit> precision;
    bool operator==(const Timestamp&) const = default;
};
enum class SequenceUnit : std::uint8_t { message, event };
struct StreamScope {
    StreamId stream; Identity session; std::uint64_t epoch; SequenceUnit unit;
    bool operator==(const StreamScope&) const = default;
};
struct DatasetIdentity {
    Identity identity; Available<Identity> version; Available<Identity> license_reference;
    Available<Digest> sha256;
    bool operator==(const DatasetIdentity&) const = default;
};
enum class Origin : std::uint8_t { synthetic, observed };
enum class Source : std::uint8_t { generator, exchange, broker, sip_consolidated, public_dataset };
enum class TransformationKind : std::uint8_t { generated, observed, normalized, reconstructed, simulated };
struct Transformation {
    TransformationKind kind; Identity operation; Identity version;
    bool operator==(const Transformation&) const = default;
};
struct ParentArtifact {
    Identity identity; Available<Digest> sha256;
    bool operator==(const ParentArtifact&) const = default;
};
struct Provenance {
    Available<DatasetIdentity> dataset;
    Available<Origin> origin;
    Available<Source> source;
    Available<std::uint64_t> generator_seed;
    BoundedList<Transformation,8> lineage;
    BoundedList<ParentArtifact,8> parents;
    bool operator==(const Provenance&) const = default;
};
struct Metadata {
    std::uint32_t schema_version{1};
    Available<InstrumentId> instrument;
    Available<VenueId> venue;
    Available<StreamScope> scope;
    Available<SequenceNumber> sequence;
    std::uint32_t subevent_index{};
    std::uint32_t subevent_count{1};
    Available<Timestamp<EventTimestamp>> event_time;
    Available<Timestamp<ReceiveTimestamp>> receive_time;
    Available<Identity> source_record;
    Available<std::uint64_t> capture_ordinal;
    Provenance provenance;
    bool operator==(const Metadata&) const = default;
};
struct InstrumentRules {
    InstrumentId instrument; VenueId venue;
    PriceTicks minimum_price; PriceTicks maximum_price;
    QuantityLots maximum_quantity;
    types::UnitScale tick_size; types::UnitScale lot_size;
    bool operator==(const InstrumentRules&) const = default;
};

struct AddOrder { OrderId order_id; Side side; PriceTicks price_ticks; QuantityLots quantity; bool operator==(const AddOrder&) const = default; };
struct CancelAll { bool operator==(const CancelAll&) const = default; };
struct CancelOrder { OrderId order_id; std::variant<CancelAll,QuantityLots> amount; bool operator==(const CancelOrder&) const = default; };
enum class ReplacePriority : std::uint8_t { lose, retain_only_same_price_reduction };
struct ReplaceOrder {
    OrderId old_order_id; OrderId new_order_id; Side side; PriceTicks price_ticks;
    QuantityLots quantity; ReplacePriority priority;
    bool operator==(const ReplaceOrder&) const = default;
};
struct TradePrint {
    PriceTicks price_ticks; QuantityLots quantity; Available<Side> aggressor;
    bool operator==(const TradePrint&) const = default;
};
struct BookExecution {
    OrderId resting_order_id; Side resting_side; PriceTicks price_ticks; QuantityLots quantity;
    bool operator==(const BookExecution&) const = default;
};
struct Trade { std::variant<TradePrint,BookExecution> details; bool operator==(const Trade&) const = default; };
struct QuoteLevel { PriceTicks price_ticks; QuantityLots quantity; bool operator==(const QuoteLevel&) const = default; };
struct Quote { std::optional<QuoteLevel> bid; std::optional<QuoteLevel> ask; bool operator==(const Quote&) const = default; };
enum class ResetReason : std::uint8_t { session_start, sequence_gap, recovery, manual };
struct BookReset { ResetReason reason; std::uint64_t next_epoch; bool operator==(const BookReset&) const = default; };
enum class SnapshotKind : std::uint8_t { order_level, aggregated };
enum class SnapshotCoverage : std::uint8_t { complete, bounded_depth };
struct SnapshotOrder {
    AddOrder order;
    std::uint64_t priority_index;
    bool operator==(const SnapshotOrder&) const = default;
};
struct SnapshotLevel {
    Side side; PriceTicks price_ticks; QuantityLots quantity;
    bool operator==(const SnapshotLevel&) const = default;
};
struct SequenceBoundary {
    StreamScope scope; SequenceNumber sequence;
    std::uint32_t last_subevent; std::uint32_t subevent_count;
    bool operator==(const SequenceBoundary&) const = default;
};
struct Snapshot {
    SnapshotKind kind; SnapshotCoverage coverage; std::uint32_t depth;
    BoundedList<SnapshotOrder,64> orders;
    BoundedList<SnapshotLevel,64> levels;
    BoundedList<SequenceBoundary,8> boundaries;
    bool operator==(const Snapshot&) const = default;
};
enum class SessionAction : std::uint8_t { open, halt, resume, close };
struct SessionEvent { SessionAction action; Available<Identity> reason; bool operator==(const SessionEvent&) const = default; };
struct UnsupportedEvent { std::uint32_t wire_type; bool operator==(const UnsupportedEvent&) const = default; };
using EventPayload = std::variant<AddOrder,CancelOrder,ReplaceOrder,Trade,Quote,BookReset,Snapshot,SessionEvent,UnsupportedEvent>;
struct MarketEvent { Metadata metadata; EventPayload payload; bool operator==(const MarketEvent&) const = default; };
enum class ValidationMode : std::uint8_t { complete, inspect_incomplete };

// Stateless validators return the first deterministic error; input is never changed.
Error validate(const InstrumentRules& rules) noexcept;
Error validate(const AddOrder& order,const InstrumentRules& rules) noexcept;
Error validate(const Metadata& metadata,ValidationMode mode=ValidationMode::complete) noexcept;
Error validate(const MarketEvent& event,const InstrumentRules& rules,ValidationMode mode=ValidationMode::complete) noexcept;
class ValidatedEvent {
    MarketEvent event_;
    InstrumentRules rules_;
    explicit ValidatedEvent(const MarketEvent& event,const InstrumentRules& rules) noexcept : event_(event),rules_(rules) {}
    friend Result<ValidatedEvent> make_validated(const MarketEvent&,const InstrumentRules&) noexcept;
public:
    const MarketEvent& event() const noexcept { return event_; }
    const InstrumentRules& rules() const noexcept { return rules_; }
    bool operator==(const ValidatedEvent&) const = default;
};
Result<ValidatedEvent> make_validated(const MarketEvent& event,const InstrumentRules& rules) noexcept;
} // namespace gig
