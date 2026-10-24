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
struct Price8Tag;
struct LocateTag; struct TrackingTag; struct TimeTag; struct ReferenceTag;
struct SharesTag; struct PriceTag; struct MatchTag; struct WideSharesTag;
using StockLocate=WireNumber<LocateTag,std::uint16_t>;
using TrackingNumber=WireNumber<TrackingTag,std::uint16_t>;
using TimestampNanoseconds=WireNumber<TimeTag,std::uint64_t>;
using OrderReference=WireNumber<ReferenceTag,std::uint64_t>;
using Shares=WireNumber<SharesTag,std::uint32_t>;
using Price8=WireNumber<Price8Tag,std::uint64_t>;
using Price4=WireNumber<PriceTag,std::uint32_t>;
using MatchNumber=WireNumber<MatchTag,std::uint64_t>;
using CrossShares=WireNumber<WideSharesTag,std::uint64_t>;
template<std::size_t N> struct Text {
    std::array<char,N> bytes{};
    std::string_view view() const noexcept { return {bytes.data(),N}; }
    bool operator==(const Text&) const = default;
};
enum class Side : char { buy='B', sell='S' };
// Explicit extension: baseline results remain stable for previously unsupported H/Y.
enum class DecodeProfile : std::uint8_t { baseline_v1, status_observations_v2, administrative_observations_v3, retained_2023_auctions_v4 };
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
struct StockTradingAction {
    Text<8> stock; char trading_state{}; char reserved{}; Text<4> reason;
    bool operator==(const StockTradingAction&)const=default;
};
struct RegShoRestriction {
    Text<8> stock; char action{};
    bool operator==(const RegShoRestriction&)const=default;
};
struct MarketParticipantPosition {
    Text<4> mpid; Text<8> stock; char primary_market_maker{},mode{},state{};
    bool operator==(const MarketParticipantPosition&)const=default;
};
struct MwcbDeclineLevels {
    Price8 level1{},level2{},level3{};
    bool operator==(const MwcbDeclineLevels&)const=default;
};
struct MwcbStatus { char breached_level{}; bool operator==(const MwcbStatus&)const=default; };
struct OperationalHalt {
    Text<8> stock; char market{},action{};
    bool operator==(const OperationalHalt&)const=default;
};
struct RetailPriceImprovement {
    Text<8> stock; char interest{};
    bool operator==(const RetailPriceImprovement&)const=default;
};
// Retained-2023 layout observations; not a certified2019 auction profile.
struct IpoQuotingUpdate {
    Text<8> stock; std::uint32_t release_seconds{}; char qualifier{}; Price4 price{};
    bool operator==(const IpoQuotingUpdate&)const=default;
};
struct LuldAuctionCollar {
    Text<8> stock; Price4 reference{},upper{},lower{}; std::uint32_t extension{};
    bool operator==(const LuldAuctionCollar&)const=default;
};
struct NetOrderImbalance {
    std::uint64_t paired{},imbalance{}; Text<8> stock;
    Price4 far{},near{},reference{}; char direction{},cross_type{},variation{};
    bool operator==(const NetOrderImbalance&)const=default;
};
struct DirectListingDiscovery {
    Text<8> stock; char eligible{}; Price4 minimum{},maximum{},near{};
    // The table states time of price setting, without a separate unit contract.
    // Preserve the full raw64-bit field; do not fabricate ns/date semantics.
    std::uint64_t near_time_raw{}; Price4 lower{},upper{};
    bool operator==(const DirectListingDiscovery&)const=default;
};
static_assert(sizeof(NetOrderImbalance)<=sizeof(CrossTrade));
using Message=std::variant<SystemEvent,StockDirectory,AddOrder,AddAttributedOrder,OrderExecuted,OrderExecutedWithPrice,OrderCancel,OrderDelete,OrderReplace,Trade,CrossTrade,BrokenTrade,StockTradingAction,RegShoRestriction,MarketParticipantPosition,MwcbDeclineLevels,MwcbStatus,OperationalHalt,RetailPriceImprovement,IpoQuotingUpdate,LuldAuctionCollar,NetOrderImbalance,DirectListingDiscovery>;
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
Result<DecodedRecord> decode(std::span<const std::byte> payload,
    Location location, Provenance provenance, DecodeProfile profile) noexcept;
} // namespace gig::itch
