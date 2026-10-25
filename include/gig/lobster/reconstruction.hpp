#pragma once
#include "gig/lobster/adapter.hpp"
#include "gig/book/order_book.hpp"
namespace gig::lobster {
struct Effect {bool quantity_eligible{},quantity_match{},best_eligible{},best_match{},depth_eligible{},depth_match{};std::string_view exclusion{};};
// Conditional local observed-level transition, not full L3 reconstruction.
Effect reference_effect(const Reference&,const Message&,const Reference&) noexcept;
enum class Disposition : std::uint8_t { native, external, unknown_order, inconsistent_history, unsupported, prefix_blocked, native_rejected, resource_rejected };
struct SourceBinding {gig::Identity dataset,session,permission;gig::Digest dataset_sha,message_sha,reference_sha;gig::Origin origin;std::uint64_t generator_seed{};};
struct Step {Message message;Disposition disposition;Effect effect;gig::Error native_error{};bool coverage_lost{};std::uint64_t lower_bound_checks{},lower_bound_violations{},equal_level_quantities{};};
struct ReconstructionSummary {std::uint64_t rows{},native{},external{},unknown{},inconsistent{},unsupported{},blocked{},native_rejected{},resource_rejected{},quantity_eligible{},quantity_matches{},best_eligible{},best_matches{},depth_eligible{},depth_matches{},lower_bound_checks{},lower_bound_violations{},equal_level_quantities{};bool prefix_blocked{},initial_state_unknown{true},full_l3_complete{};std::optional<std::uint64_t> first_mismatch,first_unknown_order;std::string_view first_mismatch_category{};std::uint32_t first_mismatch_code{};};
// Book represents known post-boundary submissions ONLY, never an empty historical
// market. Missing references are observations; reference depth is never imported.
class KnownSubset {
    SourceBinding source_;gig::OrderBook book_;PairedValidator validator_;
    struct Seen {gig::OrderId id;bool known_submission;};
    std::pmr::vector<Seen> seen_;std::size_t lifetime_limit_;std::optional<Reference> previous_;
    ReconstructionSummary summary_{};
    KnownSubset(SourceBinding,gig::OrderBook,PairedValidator,std::pmr::memory_resource*,std::size_t) noexcept;
public:
    KnownSubset(KnownSubset&&) noexcept=default;KnownSubset(const KnownSubset&)=delete;
    KnownSubset& operator=(KnownSubset&&)=delete;
    static gig::Result<KnownSubset> create(SourceBinding,Limits,std::size_t lifetime_limit=4096,
        std::pmr::memory_resource* =std::pmr::get_default_resource(),bool claim_complete=false) noexcept;
    gig::Result<Step> process(std::string_view message,std::string_view reference) noexcept;
    gig::Error finish(bool a,bool b) noexcept{return validator_.finish(a,b);}
    const ReconstructionSummary& summary()const noexcept{return summary_;}
    const Summary& parsing()const noexcept{return validator_.summary();}
    const gig::OrderBook& book()const noexcept{return book_;}
};
} // namespace gig::lobster
