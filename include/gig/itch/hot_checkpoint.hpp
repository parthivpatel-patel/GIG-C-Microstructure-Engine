#pragma once
#include "gig/itch/reconstruction.hpp"
#include <string>
namespace gig::itch {
// Only a complete accepted BinaryFile record boundary. No compressor,partial
// frame,borrowed preparation token,worker/socket handle or fabricated sequence.
struct HotReconstructionState {
    std::uint32_t version{1};ReconstructionConfig config;ContextStateImage context;
    ReconstructionSummary summary;std::array<std::uint64_t,2> sequence_base{};
    std::pmr::vector<SourceReceipt> receipts;
    std::array<std::optional<gig::ReplayStateImage>,2> engines;
    std::array<std::pmr::string,2> canonical;
    HotReconstructionState(ReconstructionConfig c,ContextStateImage image,std::pmr::memory_resource* r)
        :config(std::move(c)),context(std::move(image)),receipts(r),canonical{std::pmr::string(r),std::pmr::string(r)}{}
};
struct HotReconstructionIdentity {
    std::uint32_t version{1};ReconstructionConfig config;gig::Digest implementation_sha256;
    ReconstructionSummary summary;Sha256Digest context_sha256{},receipts_sha256{};
    std::array<std::uint64_t,2> sequence_base{};
    std::array<Sha256Digest,2> native_sha256{};
};
// The owner retains this independently trusted identity. A checksum supplied in
// the same untrusted document is not authentication. Explicit field encoding;
// no padding,pointers,locale,host-endianness or process token identities.
gig::Result<HotReconstructionIdentity> hot_identity(const HotReconstructionState&,gig::Digest implementation_sha256) noexcept;
}
