#pragma once
#include "gig/itch/durable_checkpoint.hpp"
#include "gig/itch/gzip.hpp"
namespace gig::itch {
enum class RecoveryContainer : std::uint8_t { binary_file, single_gzip };
struct SourceRecoveryAdmission {
    RecoveryContainer container;
    Sha256Digest source_sha256;
    SourceIdentity capture;
    std::uint64_t generation;
    Location first_location;
    GzipLimits gzip{};
    FramerLimits framing{65535,65535,4096,32U*1024U*1024U};
};
// Isolated candidate only. Authenticate the supplied immutable source first,then
// start the container at byte0,check the already-committed frames against receipts
// WITHOUT applying them,and apply only the continuation. No gzip/internal inflate
// pointer snapshot or arbitrary compressed seek. Single complete CRC-verified gzip
// member;BinaryFile must end at a complete nonterminal bounded-prefix boundary.
// Configured starting Location supports authored seeded tails. Missing prefix,
// partial frames,terminal positions,source mismatch,gaps and stale generations fail.
gig::Result<SyntheticReconstructor> resume_hot_source(std::span<const std::byte> checkpoint,
    const DurableAdmission&,std::span<const std::byte> source,const SourceRecoveryAdmission&,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
struct PartialBinaryTail {
    Location next_location;
    std::size_t source_offset;  // Relative to the supplied container, not the source's absolute cursor.
    std::size_t residual_bytes;
    Sha256Digest residual_sha256;
};
struct PartialBinaryRecovery {
    SyntheticReconstructor owner;
    PartialBinaryTail tail;
};
// Explicit partial BinaryFile admission. Commit only verified whole frames. The
// unfinished frame remains with the caller at tail.source_offset and must be
// completed before process() can advance the returned active owner.
gig::Result<PartialBinaryRecovery> resume_partial_binary_source(std::span<const std::byte> checkpoint,
    const DurableAdmission&,std::span<const std::byte> source,const SourceRecoveryAdmission&,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
// Explicit complete-source profile. The durable input remains an accepted active
// Version1 boundary; replay validates its committed prefix without applying it.
// Require the BinaryFile zero-length terminator at exact EOF and,for gzip,the
// verified complete single-member trailer before sealing the isolated candidate.
// Completion is a supplied-container fact,not observed exchange completeness.
// The returned owner is finished;further process/hot_checkpoint calls fail. This
// does not introduce terminal-image serialization or migrate Version1 images.
gig::Result<SyntheticReconstructor> resume_complete_source(std::span<const std::byte> checkpoint,
    const DurableAdmission&,std::span<const std::byte> source,const SourceRecoveryAdmission&,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
}
