#pragma once
#include "gig/itch/decoder.hpp"
#include <memory_resource>
#include <vector>

namespace gig::itch {
// Synthetic semantic-policy module, not a native replay adapter or L3 validator.
enum class ContextStatus : std::uint8_t { accepted, source_invalid, context_invalid, unsupported, integration_ineligible, resource_limit };
enum class ContextCode : std::uint8_t { none, invalid_config, allocation_failure, provenance_conflict, discontinuity, timestamp_policy, lifecycle, unknown_locate, directory_conflict, stock_conflict, invalid_reference, duplicate_reference, missing_order, inactive_order, invalid_quantity, quantity_underflow, equal_cancel, duplicate_match, missing_match, broken_match, capacity, unit_conversion, unsupported_source, already_finished, invalid_prepared, stale_prepared };
struct ContextError {
    ContextCode code{ContextCode::none}; Location location{}; std::string_view field{}; std::uint64_t expected{},actual{}; Error source_error{};
    bool operator==(const ContextError&)const=default;
};
enum class Initialization : std::uint8_t { unknown, synthetic_history_declared };
struct SourceManifest {
    // Required explicit identity tokens; missing observations within provenance stay missing.
    SourceIdentity source; SourceIdentity session; Provenance provenance{};
    Initialization initialization{Initialization::unknown};
    bool operator==(const SourceManifest&)const=default;
};
struct ContextPolicy {
    std::size_t max_directories{64}, max_lifetime_orders{4096}, max_matches{4096};
    // Logical vector-storage budget, not process RSS or allocator overhead. Requested
    // slots are checked before reserve; actual capacities are checked afterward.
    // Use a caller-owned bounded PMR resource for a hard allocation governor.
    std::size_t memory_budget_bytes{4U*1024U*1024U};
    // Source-order policy is exact BinaryFile adjacency, not exchange sequencing.
    Location first_location{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}};
    bool require_monotonic_timestamps{false}, require_intraday_timestamps{false};
    bool require_lifecycle_order{true}, allow_equal_cancel{false};
    // Explicit hypothetical native conversion only. No inferred instrument units.
    std::uint32_t price_quantum{1}, lot_size{1};
    DecodeProfile decode_profile{DecodeProfile::baseline_v1};
    bool operator==(const ContextPolicy&)const=default;
};
struct DirectoryState { StockLocate locate{}; StockDirectory directory; bool operator==(const DirectoryState&)const=default; };
struct OrderState {
    OrderReference reference{}; StockLocate locate{}; Text<8> stock; Side side{};
    Shares remaining{}; Price4 resting_price{}; std::optional<Text<4>> attribution;
    RecordOrdinal arrival{}; bool active{};
    bool operator==(const OrderState&)const=default;
};
enum class MatchKind : std::uint8_t { displayed_execution, non_displayed_trade, cross };
struct MatchState { MatchNumber number{}; StockLocate locate{}; MatchKind kind{}; bool broken{}; bool operator==(const MatchState&)const=default; };
enum class SemanticKind : std::uint8_t { system, directory, add, execution, cancel, erase, replace, trade_print, cross_print, broken_trade, trading_action, reg_sho_restriction };
enum class IntegrationClass : std::uint8_t { external_observation, exact_candidate, book_only_projection, unsupported };
struct NormalizedRecord {
    DecodedRecord source; SourceManifest manifest; SemanticKind kind{};
    // Reproduction envelope: all selected semantic policies and algorithm version.
    std::uint32_t normalization_version{1}; ContextPolicy policy{};
    NormalizedRecord(DecodedRecord r,SourceManifest m) noexcept:source(std::move(r)),manifest(std::move(m)) {}
    IntegrationClass integration{IntegrationClass::external_observation};
    std::optional<OrderState> before,after;
    std::optional<Price4> observed_execution_price;
    std::optional<char> printable;
    // Hypothetical native candidate units only; E/C use context resting price,
    // while C retains its distinct observed execution price above. No native replay
    // happens here. P candidates mean prints only; Q auction semantics and B tape
    // corrections remain integration-unsupported even when units are representable.
    std::optional<std::uint64_t> price_ticks,quantity_lots;
    // Always true in P1F: initial-state evidence and actual native replay are future work.
    bool initialization_incomplete{true};
};
struct ContextResult {
    ContextStatus status{ContextStatus::context_invalid}; std::optional<NormalizedRecord> record; ContextError error{};
    // integration_ineligible can still commit valid source-context observations.
    bool committed()const noexcept{return record.has_value();}
};
enum class ContextEnd : std::uint8_t { bounded_prefix, declared_source_complete, unexpected_eof };
struct ContextSummary {
    std::uint64_t accepted_records{}; std::size_t directories{},lifetime_orders{},matches{},active_orders{},reserved_bytes{};
    std::optional<Location> last_location; std::optional<TimestampNanoseconds> last_timestamp;
    // source_complete is the caller's framing/container declaration only. An ordered
    // O/S/Q/M/E/C lifecycle plus declared completion closes this local session policy;
    // neither flag establishes initial L3 state or upstream exchange completeness.
    bool initialization_incomplete{true},session_incomplete{true},finished{},source_complete{},bounded_prefix{};
    ContextCode finish_error{ContextCode::none};
    bool operator==(const ContextSummary&)const=default;
};
class SourceContext;
class SyntheticReconstructor;
// Owned single-use semantic delta. Preparation never changes accepted context.
// Moving a token consumes the donor; destroying an uncommitted token is rollback.
class PreparedContext {
    friend class SourceContext;
    const SourceContext* owner_{};
    std::uint64_t instance_{},generation_{};
    ContextResult result_;
    std::optional<DirectoryState> add_directory_;
    std::optional<OrderState> add_order_,update_order_;
    std::optional<MatchState> add_match_,update_match_;
    std::size_t order_slot_{},match_slot_{};
    std::uint8_t next_stage_{};
    Location next_location_{};
    bool cursor_exhausted_{},valid_{};
    PreparedContext(const SourceContext*,std::uint64_t,std::uint64_t,ContextResult) noexcept;
public:
    PreparedContext(PreparedContext&&) noexcept;
    PreparedContext& operator=(PreparedContext&&)=delete;
    PreparedContext(const PreparedContext&)=delete;
    PreparedContext& operator=(const PreparedContext&)=delete;
    const NormalizedRecord& record()const noexcept{return *result_.record;}
    ContextStatus status()const noexcept{return result_.status;}
    const ContextError& error()const noexcept{return result_.error;}
};
struct ContextPreparation {
    ContextStatus status{ContextStatus::context_invalid}; ContextError error{};
    std::optional<PreparedContext> prepared;
    ContextPreparation() noexcept=default;
    ContextPreparation(ContextStatus s,ContextError e,PreparedContext token) noexcept
        :status(s),error(e),prepared(std::move(token)) {}
    ContextPreparation(ContextResult rejection) noexcept:status(rejection.status),error(rejection.error) {}
    explicit operator bool()const noexcept{return prepared.has_value();}
};
class SourceContext {
    friend class SyntheticReconstructor;
    SourceManifest manifest_; ContextPolicy policy_;
    std::pmr::vector<DirectoryState> directories_;
    std::pmr::vector<OrderState> orders_;
    std::pmr::vector<MatchState> matches_;
    ContextSummary summary_{}; std::uint8_t lifecycle_stage_{}; Location next_location_{};
    bool cursor_exhausted_{},moved_from_{};
    std::uint64_t instance_{};
    ContextResult commit_validated(PreparedContext&&) noexcept;
    SourceContext(SourceManifest,ContextPolicy,std::pmr::memory_resource*) noexcept;
public:
    SourceContext(SourceContext&&) noexcept;
    SourceContext& operator=(SourceContext&&)=delete;
    SourceContext(const SourceContext&)=delete;
    SourceContext& operator=(const SourceContext&)=delete;
    static Result<SourceContext> create(SourceManifest,ContextPolicy={},std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
    // All runtime input crosses the validated wire boundary; forged DecodedRecord is not accepted.
    // Rejects never advance cursors or ledgers. Unsupported/unknown records return an
    // explicit stop disposition; callers must not skip source records after rejection.
    // There is no silent skip API or automatic recovery/reset.
    ContextPreparation prepare(std::span<const std::byte>,Location,Provenance={}) const noexcept;
    // Validate immediately before any native mutation. The private nofail commit is
    // available only to the stable, single-threaded owning reconstruction adapter.
    ContextError validate_prepared(const PreparedContext&)const noexcept;
    ContextResult commit(PreparedContext&&) noexcept;
    ContextResult apply(std::span<const std::byte>,Location,Provenance={}) noexcept;
    ContextResult disposition(const Error& source_error,Location)const noexcept;
    ContextSummary finish(ContextEnd) noexcept;
    const ContextSummary& summary()const noexcept{return summary_;}
    const SourceManifest& manifest()const noexcept{return manifest_;}
    std::span<const DirectoryState> directories()const noexcept{return directories_;}
    std::span<const OrderState> orders()const noexcept{return orders_;}
    std::span<const MatchState> matches()const noexcept{return matches_;}
    static std::optional<std::size_t> required_bytes(const ContextPolicy&) noexcept;
};
} // namespace gig::itch
