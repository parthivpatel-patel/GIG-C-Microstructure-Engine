#pragma once
#include "gig/itch/wire.hpp"
#include <span>
#include <variant>

namespace gig::itch {
// Source wire units only: no tick normalization, rounding, or clock conversion.
template<class Tag, class Rep> class WireNumber {
    Rep value_{};
public:
    explicit constexpr WireNumber(Rep value=0) noexcept:value_(value) {}
    constexpr Rep value() const noexcept { return value_; }
    auto operator<=>(const WireNumber&) const = default;
};
struct LocateTag; struct TrackingTag; struct TimeTag; struct ReferenceTag;
struct SharesTag; struct PriceTag; struct MatchTag; struct WideSharesTag;
using StockLocate=WireNumber<LocateTag,std::uint16_t>;
using TrackingNumber=WireNumber<TrackingTag,std::uint16_t>;
using TimestampNanoseconds=WireNumber<TimeTag,std::uint64_t>;
using OrderReference=WireNumber<ReferenceTag,std::uint64_t>;
using Shares=WireNumber<SharesTag,std::uint32_t>;
using Price4=WireNumber<PriceTag,std::uint32_t>;
using MatchNumber=WireNumber<MatchTag,std::uint64_t>;
using CrossShares=WireNumber<WideSharesTag,std::uint64_t>;
template<std::size_t N> struct Text {
    std::array<char,N> bytes{};
    std::string_view view() const noexcept { return {bytes.data(),N}; }
    bool operator==(const Text&) const = default;
};
enum class Side : char { buy='B', sell='S' };
struct Header { StockLocate stock_locate{}; TrackingNumber tracking_number{}; TimestampNanoseconds timestamp{}; bool operator==(const Header&) const=default; };
struct SystemEvent { char event_code{}; bool operator==(const SystemEvent&)const=default; };
// Classification/subtype are retained as printable ASCII, not appendix-enum certified.
struct StockDirectory {
    Text<8> stock; char market_category{},financial_status{}; std::uint32_t round_lot_size{};
    char round_lots_only{},issue_classification{}; Text<2> issue_subtype;
    char authenticity{},short_sale_threshold{},ipo_flag{},luld_tier{},etp_flag{};
    std::uint32_t etp_leverage{}; char inverse{};
    bool operator==(const StockDirectory&)const=default;
};
struct AddOrder { OrderReference order_reference{}; Side side{}; Shares shares{}; Text<8> stock; Price4 price{}; bool operator==(const AddOrder&)const=default; };
struct AddAttributedOrder { AddOrder order; Text<4> attribution; bool operator==(const AddAttributedOrder&)const=default; };
struct OrderExecuted { OrderReference order_reference{}; Shares executed_shares{}; MatchNumber match_number{}; bool operator==(const OrderExecuted&)const=default; };
struct OrderExecutedWithPrice { OrderExecuted execution; char printable{}; Price4 execution_price{}; bool operator==(const OrderExecutedWithPrice&)const=default; };
struct OrderCancel { OrderReference order_reference{}; Shares cancelled_shares{}; bool operator==(const OrderCancel&)const=default; };
struct OrderDelete { OrderReference order_reference{}; bool operator==(const OrderDelete&)const=default; };
struct OrderReplace { OrderReference original_reference{},new_reference{}; Shares shares{}; Price4 price{}; bool operator==(const OrderReplace&)const=default; };
// P reference and side are raw source fields, never queue identity or aggressor inference.
struct Trade { OrderReference order_reference{}; Side side{}; Shares shares{}; Text<8> stock; Price4 price{}; MatchNumber match_number{}; bool operator==(const Trade&)const=default; };
struct CrossTrade { CrossShares shares{}; Text<8> stock; Price4 cross_price{}; MatchNumber match_number{}; char cross_type{}; bool operator==(const CrossTrade&)const=default; };
struct BrokenTrade { MatchNumber match_number{}; bool operator==(const BrokenTrade&)const=default; };
using Message=std::variant<SystemEvent,StockDirectory,AddOrder,AddAttributedOrder,OrderExecuted,OrderExecutedWithPrice,OrderCancel,OrderDelete,OrderReplace,Trade,CrossTrade,BrokenTrade>;
struct DecodedRecord {
    std::uint8_t type{}; Header header; Message message; Location location; Provenance provenance;
    bool operator==(const DecodedRecord&)const=default;
};
// All 23 message lengths in the retrieved S1 layout; nullopt means unknown type.
std::optional<std::size_t> expected_length(std::uint8_t type) noexcept;
// S1 retrieved-2023 layout only; this does not certify historical archive compatibility.
// Exact wire validation is stateless: referential/session/locate relationships belong
// to a subsequent semantic validator. All unsigned references/share counts, including
// zero, remain observable: native book positivity rules are not wire validity rules.
// Default describes a single BinaryFile frame at byte zero. Output owns every byte.
Result<DecodedRecord> decode(std::span<const std::byte> payload,
    Location location={ByteOffset{0},ByteOffset{2},RecordOrdinal{0}}, Provenance provenance={}) noexcept;
} // namespace gig::itch
