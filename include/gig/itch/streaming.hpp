#pragma once
#include "gig/itch/gzip.hpp"
#include "gig/itch/restart.hpp"

namespace gig::itch {
struct StreamingConfig {
    ReconstructionConfig reconstruction;
    GzipLimits gzip{};
    FramerLimits framing{};
    Sha256Digest compressed_sha256; // independently measured authored artifact
    bool operator==(const StreamingConfig& other) const noexcept {
        return reconstruction==other.reconstruction&&gzip==other.gzip&&compressed_sha256==other.compressed_sha256
            &&framing.max_payload_bytes==other.framing.max_payload_bytes&&framing.buffer_bytes==other.framing.buffer_bytes
            &&framing.max_records==other.framing.max_records&&framing.max_stream_bytes==other.framing.max_stream_bytes;
    }
};
enum class StreamingCode : std::uint8_t { none, gzip, framing, reconstruction, identity_mismatch, already_finished, moved_from, reentrant };
struct StreamingError {
    StreamingCode code{StreamingCode::none};
    GzipError gzip{};
    Error framing{};
    ReconstructionStep reconstruction{};
    explicit operator bool()const noexcept{return code!=StreamingCode::none;}
};
struct StreamingFeed {
    std::size_t consumed{};
    bool paused{};
    StreamingError error{};
};
struct StreamingSummary {
    std::uint64_t compressed_bytes{},decompressed_bytes{},framing_bytes{},accepted_prefix_bytes{};
    std::uint64_t source_records{},accepted_records{},native_records{},external_observations{};
    Sha256Digest compressed_sha256{},decompressed_sha256{},accepted_prefix_sha256{};
    bool gzip_member_verified{},framer_terminated{},compressed_identity_verified{},decompressed_identity_verified{};
    bool source_complete{},publication_eligible{},paused{},finished{},bounded_prefix{};
    std::uint64_t residual_frame_bytes{},buffered_output_bytes{};
    StreamingError error{};
    GzipError observed_gzip_error{}; // physical corruption may already be known while the logical prefix is paused
};
// Trusted in-memory logical checkpoint. Compressed read-ahead/partial framing are
// intentionally excluded: restart replays from byte0 and pauses at this exact
// accepted frame boundary; it never seeks to a compressed offset.
struct StreamingCheckpoint {
    std::uint32_t version{1};
    StreamingConfig config;
    gig::Digest implementation_sha256;
    ReconstructionSummary reconstruction;
    ContextSummary context;
    std::uint64_t accepted_prefix_bytes{};
    Sha256Digest accepted_prefix_sha256{};
    std::array<std::optional<BookCheckpoint>,2> books;
    bool operator==(const StreamingCheckpoint&) const = default;
};
class StreamingReconstructor {
    StreamingConfig config_;
    GzipReader gzip_;
    BinaryFileFramer framer_;
    SyntheticReconstructor reconstruction_;
    Sha256 compressed_hash_,decompressed_hash_,accepted_hash_;
    std::uint64_t accepted_bytes_{};
    std::span<const std::byte> pending_output_{};
    std::optional<std::uint64_t> pause_after_;
    bool paused_{},finished_{},moved_from_{};
    mutable bool busy_{};
    StreamingError error_{};
    GzipError deferred_gzip_error_{};
    std::optional<StreamingSummary> final_;
    StreamingReconstructor(StreamingConfig,GzipReader,BinaryFileFramer,SyntheticReconstructor) noexcept;
    void consume_output() noexcept;
    StreamingFeed feed_impl(std::span<const std::byte>) noexcept;
public:
    static gig::Result<StreamingReconstructor> create(StreamingConfig,
        std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
    StreamingReconstructor(StreamingReconstructor&&) noexcept;
    StreamingReconstructor(const StreamingReconstructor&)=delete;
    StreamingReconstructor& operator=(const StreamingReconstructor&)=delete;
    StreamingReconstructor& operator=(StreamingReconstructor&&)=delete;
    StreamingFeed feed(std::span<const std::byte>) noexcept;
    StreamingSummary finish(EndKind=EndKind::source_eof) noexcept;
    StreamingSummary summary() const noexcept;
    // Pause occurs only after a complete committed frame; owned decompressed
    // read-ahead remains bounded and is drained on resume before new inflate calls.
    gig::Error pause_after(std::uint64_t accepted_records) noexcept;
    gig::Error resume() noexcept;
    gig::Result<StreamingCheckpoint> checkpoint(gig::Digest implementation_sha256)const noexcept;
    gig::Error verify_checkpoint(const StreamingCheckpoint&,gig::Digest expected_implementation_sha256)const noexcept;
    const SyntheticReconstructor& reconstruction()const noexcept{return reconstruction_;}
    const StreamingConfig& config()const noexcept{return config_;}
};
} // namespace gig::itch
