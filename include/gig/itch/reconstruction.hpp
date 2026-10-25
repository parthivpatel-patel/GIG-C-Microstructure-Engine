#pragma once
#include "gig/itch/context.hpp"
#include "gig/replay/replay.hpp"

namespace gig::itch {
enum class InitialStateKind : std::uint8_t { unknown, authored_empty, complete_seed, incomplete_history, invalid };
enum class ReconstructionEligibility : std::uint8_t { blocked, eligible_synthetic_empty, stopped_at_valid_prefix, eligible_synthetic_seed };
// This evidence is an explicit caller assertion, authenticated by the fixture runner.
// It is not a market-data empty-state inference or a cryptographic verifier.
struct InitializationEvidence {
    InitialStateKind kind;
    SourceIdentity source, session, generator;
    // Version identifies the declared authored fixture/generator contract.
    gig::Identity fixture, version, policy_reference;
    gig::Digest fixture_sha256;
    std::uint64_t seed;
    Location boundary;
    bool complete_history;
    bool operator==(const InitializationEvidence&) const = default;
};
struct BookBinding {
    Text<8> stock;
    StockLocate locate;
    gig::InstrumentRules rules;
    gig::StreamId derived_stream;
    gig::BookLimits limits{128,128,16};
    std::size_t max_journal_records{1024};
    bool operator==(const BookBinding&) const = default;
};
struct ReconstructionConfig {
    SourceManifest source;
    ContextPolicy context_policy;
    InitializationEvidence initialization;
    gig::Identity run_id;
    std::array<std::optional<BookBinding>,2> bindings;
    std::size_t book_count{2};
    std::size_t max_source_records{4096};
    std::size_t receipt_budget_bytes{2*1024*1024};
    bool allow_c_book_only{false};
    std::optional<gig::Digest> seed_sha256{};
    bool operator==(const ReconstructionConfig&) const = default;
};
enum class SourceDisposition : std::uint8_t { native_committed, external_observation, source_rejected, context_rejected, integration_rejected, resource_rejected, pending_identity_mismatch, finished };
struct ReconstructionStep {
    SourceDisposition disposition{SourceDisposition::integration_rejected};
    ContextError context_error{};
    gig::Error native_error{};
    std::optional<std::size_t> book_index;
    std::optional<std::uint64_t> native_sequence;
    bool committed{false};
};
struct SourceReceipt {
    DecodedRecord source;
    SourceDisposition disposition;
    std::optional<std::size_t> book_index;
    std::optional<std::uint64_t> native_sequence;
};
struct ReconstructionSummary {
    ReconstructionEligibility eligibility{ReconstructionEligibility::eligible_synthetic_empty};
    std::uint64_t considered{}, context_committed{}, native_committed{}, external_observations{}, rejected{};
    std::array<std::uint64_t,2> native_counts{};
    std::optional<Location> physical_position, committed_position;
    bool pending{}, input_complete{}, finished{}, unconsidered_record{};
    bool initialization_verified{true};
    bool operator==(const ReconstructionSummary&) const = default;
};
struct SeedState;
class SyntheticReconstructor {
    ReconstructionConfig config_;
    SourceContext context_;
    std::array<std::optional<gig::ReplayEngine>,2> engines_;
    std::pmr::vector<SourceReceipt> receipts_;
    ReconstructionSummary summary_;
    std::array<std::uint64_t,2> sequence_base_{};
    std::array<std::byte,65535> pending_{};
    std::size_t pending_size_{};
    Location pending_location_{};
    Provenance pending_provenance_{};
    bool moved_from_{};
    bool busy_{};
    bool held_{};
    SyntheticReconstructor(ReconstructionConfig,SourceContext,std::pmr::memory_resource*) noexcept;
    gig::Result<gig::MarketEvent> project(const NormalizedRecord&,std::size_t) const noexcept;
public:
    SyntheticReconstructor(SyntheticReconstructor&&) noexcept;
    SyntheticReconstructor(const SyntheticReconstructor&)=delete;
    SyntheticReconstructor& operator=(const SyntheticReconstructor&)=delete;
    SyntheticReconstructor& operator=(SyntheticReconstructor&&)=delete;
    static gig::Result<SyntheticReconstructor> create(ReconstructionConfig,
        std::pmr::memory_resource* = std::pmr::get_default_resource()) noexcept;
    // Atomic factory: typed complete synthetic snapshot only, not observed evidence.
    static gig::Result<SyntheticReconstructor> create_seeded(ReconstructionConfig,const SeedState&,
        std::array<std::byte,32> trusted_snapshot_sha256,
        std::pmr::memory_resource* = std::pmr::get_default_resource()) noexcept;
    std::uint64_t seed_journal_records(std::size_t i)const noexcept{return i<config_.book_count?sequence_base_[i]:0;}
    ReconstructionStep process(std::span<const std::byte>,Location,Provenance={}) noexcept;
    ReconstructionSummary finish(ContextEnd) noexcept;
    const SourceContext& context() const noexcept {return context_;}
    const ReconstructionConfig& config() const noexcept {return config_;}
    const ReconstructionSummary& summary() const noexcept {return summary_;}
    const gig::ReplayEngine* engine(std::size_t i) const noexcept {return i<config_.book_count&&engines_[i]?&*engines_[i]:nullptr;}
    std::span<const SourceReceipt> receipts() const noexcept {return receipts_;}
};
// Exact checked conversions; these do not apply instrument min/max rules.
gig::Result<gig::PriceTicks> price4_to_ticks(Price4,gig::types::UnitScale) noexcept;
gig::Result<gig::QuantityLots> shares_to_lots(std::uint64_t,gig::types::UnitScale) noexcept;
} // namespace gig::itch
