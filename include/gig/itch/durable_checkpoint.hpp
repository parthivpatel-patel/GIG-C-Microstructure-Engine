#pragma once
#include "gig/itch/hot_checkpoint.hpp"
namespace gig::itch {
// Version1 only. No automatic schema or implementation migration. Little-endian
// field encoding,never ABI/object bytes. External digest/contract/code/capture and
// generation must come from independently retained trusted evidence.
inline constexpr std::size_t durable_max_bytes=32U*1024U*1024U;
struct DurableAdmission {
    Sha256Digest artifact_sha256,contract_sha256;
    gig::Digest implementation_sha256;
    SourceIdentity capture;
    std::uint64_t generation;
};
Sha256Digest hot_contract_sha256(const ReconstructionConfig&) noexcept;
gig::Result<std::pmr::vector<std::byte>> encode_hot_checkpoint(const HotReconstructionState&,
    SourceIdentity capture,std::uint64_t generation,gig::Digest implementation_sha256,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
gig::Result<SyntheticReconstructor> restore_durable_checkpoint(std::span<const std::byte>,const DurableAdmission&,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
}
