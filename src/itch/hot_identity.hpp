#pragma once
#include "gig/itch/hot_checkpoint.hpp"
#include <tuple>
#include <type_traits>
namespace gig::itch::hot_detail {
#define F(T,...) inline auto fields(const T&v){return std::tie(__VA_ARGS__);}
F(Location,v.frame_offset,v.payload_offset,v.ordinal)
F(Provenance,v.origin,v.source,v.sha256,v.generator_seed)
F(SourceManifest,v.source,v.session,v.provenance,v.initialization)
F(ContextPolicy,v.max_directories,v.max_lifetime_orders,v.max_matches,v.memory_budget_bytes,v.first_location,v.require_monotonic_timestamps,v.require_intraday_timestamps,v.require_lifecycle_order,v.allow_equal_cancel,v.price_quantum,v.lot_size,v.decode_profile)
F(ContextSummary,v.accepted_records,v.directories,v.lifetime_orders,v.matches,v.active_orders,v.reserved_bytes,v.last_location,v.last_timestamp,v.initialization_incomplete,v.session_incomplete,v.finished,v.source_complete,v.bounded_prefix,v.finish_error)
F(StockDirectory,v.stock,v.market_category,v.financial_status,v.round_lot_size,v.round_lots_only,v.issue_classification,v.issue_subtype,v.authenticity,v.short_sale_threshold,v.ipo_flag,v.luld_tier,v.etp_flag,v.etp_leverage,v.inverse)
F(DirectoryState,v.locate,v.directory)
F(OrderState,v.reference,v.locate,v.stock,v.side,v.remaining,v.resting_price,v.attribution,v.arrival,v.active)
F(MatchState,v.number,v.locate,v.kind,v.broken)
F(ContextStateImage,v.version,v.manifest,v.policy,v.summary,v.lifecycle_stage,v.next_location,v.cursor_exhausted,v.directories,v.orders,v.matches,v.seed_retired)
F(Header,v.stock_locate,v.tracking_number,v.timestamp)
F(SystemEvent,v.event_code)
F(AddOrder,v.order_reference,v.side,v.shares,v.stock,v.price)
F(AddAttributedOrder,v.order,v.attribution)
F(OrderExecuted,v.order_reference,v.executed_shares,v.match_number)
F(OrderExecutedWithPrice,v.execution,v.printable,v.execution_price)
F(OrderCancel,v.order_reference,v.cancelled_shares)
F(OrderDelete,v.order_reference)
F(OrderReplace,v.original_reference,v.new_reference,v.shares,v.price)
F(Trade,v.order_reference,v.side,v.shares,v.stock,v.price,v.match_number)
F(CrossTrade,v.shares,v.stock,v.cross_price,v.match_number,v.cross_type)
F(BrokenTrade,v.match_number)
F(StockTradingAction,v.stock,v.trading_state,v.reserved,v.reason)
F(RegShoRestriction,v.stock,v.action)
F(MarketParticipantPosition,v.mpid,v.stock,v.primary_market_maker,v.mode,v.state)
F(MwcbDeclineLevels,v.level1,v.level2,v.level3)
F(MwcbStatus,v.breached_level)
F(OperationalHalt,v.stock,v.market,v.action)
F(RetailPriceImprovement,v.stock,v.interest)
F(IpoQuotingUpdate,v.stock,v.release_seconds,v.qualifier,v.price)
F(LuldAuctionCollar,v.stock,v.reference,v.upper,v.lower,v.extension)
F(NetOrderImbalance,v.paired,v.imbalance,v.stock,v.far,v.near,v.reference,v.direction,v.cross_type,v.variation)
F(DirectListingDiscovery,v.stock,v.eligible,v.minimum,v.maximum,v.near,v.near_time_raw,v.lower,v.upper)
F(DecodedRecord,v.type,v.header,v.message,v.location,v.provenance)
F(SourceReceipt,v.source,v.disposition,v.book_index,v.native_sequence)
#undef F
class Writer {
    Sha256 hash_;bool valid_{true};
public:
    void integer(std::uint64_t v) noexcept {std::array<std::byte,8>b{};for(auto&x:b){x=static_cast<std::byte>(v&255);v>>=8;}valid_=hash_.update(b)&&valid_;}
    template<class T>void put(const T&v)noexcept {
        if constexpr(std::is_enum_v<T>)integer(static_cast<std::uint64_t>(v));
        else if constexpr(std::is_integral_v<T>)integer(static_cast<std::uint64_t>(v));
        else if constexpr(requires{v.has_value();}){integer(v.has_value());if(v)put(*v);}
        else if constexpr(requires{v.value();})put(v.value());
        else if constexpr(requires{v.view();}){auto s=v.view();integer(s.size());valid_=hash_.update(std::as_bytes(std::span{s.data(),s.size()}))&&valid_;}
        else if constexpr(requires{v.index();}){integer(v.index());std::visit([&](const auto&x){put(x);},v);}
        else if constexpr(requires{v.bytes;}){put(v.bytes);}
        else if constexpr(requires{v.size();v.begin();}){integer(v.size());for(const auto&x:v)put(x);}
        else std::apply([&](const auto&...x){(put(x),...);},fields(v));
    }
    Sha256Digest finish()const noexcept{return hash_.finish();}
    bool valid()const noexcept{return valid_;}
};
}
