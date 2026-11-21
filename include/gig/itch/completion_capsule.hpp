#pragma once
#include "gig/itch/source_recovery.hpp"
namespace gig::itch {
// Separate replay capsule;not a changed durable v1 image or opaque terminal state.
// Layout:GIGSCAP1 (8bytes),u64le image length,u64le source length,original image,source.
// Independent admission authenticates both embedded originals and this entire capsule.
inline constexpr std::size_t completion_capsule_max_bytes=32U*1024U*1024U;
struct CompletionCapsuleAdmission {
    Sha256Digest capsule_sha256;
    DurableAdmission checkpoint;
    SourceRecoveryAdmission source;
};
gig::Result<std::pmr::vector<std::byte>> encode_completion_capsule(
    std::span<const std::byte> checkpoint,const DurableAdmission&,
    std::span<const std::byte> source,const SourceRecoveryAdmission&,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
gig::Result<SyntheticReconstructor> restore_completion_capsule(
    std::span<const std::byte>,const CompletionCapsuleAdmission&,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
}
