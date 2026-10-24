#pragma once
#include "gig/itch/binary_file.hpp"
#include "gig/itch/reconstruction.hpp"
#include "gig/itch/sha256.hpp"

namespace gig::itch {
// Evidence categories are caller declarations, never an exchange authentication.
enum class InitialClaim : std::uint8_t { unknown, session_start_evidence, snapshot_evidence, incomplete, authored_synthetic };
struct DatasetContract {
    SourceIdentity provider,dataset,acquisition,permission_reference,redistribution_reference,initial_state_reference;
    std::optional<Text<10>> session_date;
    ByteOffset capture_start{};
    std::optional<ByteOffset> capture_end;
    bool known_gaps{true};
};
struct InputAdapterConfig {
    DatasetContract dataset;
    SourceManifest source;
    ContextPolicy context_policy;
    FramerLimits framing;
    InitialClaim initial{InitialClaim::unknown};
    // Only authored synthetic configurations may enter the existing native factory.
    std::optional<ReconstructionConfig> synthetic;
};
enum class AdapterCode : std::uint8_t { none, invalid_config, framing, context, native, digest, finished, moved_from, reentrant };
struct AdapterError {
    AdapterCode code{AdapterCode::none};
    std::string_view field{};
    Error framing{};
    ContextError context{};
    ReconstructionStep native{};
    explicit operator bool()const noexcept{return code!=AdapterCode::none;}
};
struct AdapterFeed {
    std::size_t consumed{};
    bool frame{},committed{};
    std::optional<Location> location;
    std::optional<std::uint8_t> type;
    std::optional<NormalizedRecord> normalized;
    ReconstructionStep native{};
    AdapterError error{};
};
struct AdapterSummary {
    std::uint64_t bytes{},records{},accepted{},native_records{},rejected{};
    bool input_complete{},session_complete{},full_l3_complete{},publication_eligible{},context_only{true};
    InitialClaim declared_initial{InitialClaim::unknown};
    Sha256Digest input_sha256{};
    AdapterError error{};
};
// Pull one owned normalized record/native receipt per call; caller must consume all
// reported bytes and declare EOF versus interruption honestly. No I/O, gzip or
// legal/publisher attestation. Resource must outlive this single-owner adapter.
class BinarySourceAdapter {
    InputAdapterConfig config_;
    BinaryFileFramer framer_;
    std::optional<SourceContext> context_;
    std::optional<SyntheticReconstructor> native_;
    Sha256 hash_;
    AdapterSummary summary_;
    bool finished_{},moved_from_{},busy_{};
    BinarySourceAdapter(InputAdapterConfig,BinaryFileFramer,std::optional<SourceContext>,std::optional<SyntheticReconstructor>) noexcept;
public:
    BinarySourceAdapter(BinarySourceAdapter&&) noexcept;
    BinarySourceAdapter(const BinarySourceAdapter&)=delete;
    BinarySourceAdapter& operator=(const BinarySourceAdapter&)=delete;
    BinarySourceAdapter& operator=(BinarySourceAdapter&&)=delete;
    static gig::Result<BinarySourceAdapter> create(InputAdapterConfig,std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
    AdapterFeed feed(std::span<const std::byte>) noexcept;
    AdapterSummary finish(EndKind=EndKind::source_eof) noexcept;
    const InputAdapterConfig& config()const noexcept{return config_;}
    const AdapterSummary& summary()const noexcept{return summary_;}
    const SourceContext& context()const noexcept{return native_?native_->context():*context_;}
    const SyntheticReconstructor* reconstruction()const noexcept{return !moved_from_&&native_?&*native_:nullptr;}
};
} // namespace gig::itch
