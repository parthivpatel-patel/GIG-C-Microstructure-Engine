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
}
