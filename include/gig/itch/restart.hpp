#pragma once
#include "gig/itch/reconstruction.hpp"
#include "gig/itch/sha256.hpp"

namespace gig::itch {
struct BookCheckpoint {
    std::uint64_t revision{},remaining{};
    std::size_t journal_records{},active_orders{};
    gig::QuantityLedger ledger{};
    Sha256Digest canonical_sha256{};
    bool needs_recovery{};
    bool operator==(const BookCheckpoint&) const = default;
};
// An in-memory, versioned replay descriptor, not a serialized state loader or MAC.
// The caller retains this descriptor as trusted evidence and supplies independently
// measured implementation identity. Hash equality is integrity, not proof of origin.
struct ReconstructionCheckpoint {
    std::uint32_t format_version{1};
    ReconstructionConfig config;
    gig::Digest implementation_sha256;
    ReconstructionSummary summary;
    ContextSummary context;
    std::uint64_t prefix_bytes{};
    Sha256Digest prefix_sha256{};
    Provenance record_provenance{};
    std::array<std::optional<BookCheckpoint>,2> books;
    bool terminal_observed{};
    bool operator==(const ReconstructionCheckpoint&) const = default;
};
// Captures only an active accepted prefix with no held/rejected/unconsidered record.
// Independently rebuilds from byte0 and checks context, receipts and native state
// against the supplied instance before producing a descriptor. Optional BinaryFile
// terminal is allowed; a partial frame and bytes after terminal are rejected.
// Per-record provenance must be uniform; nonuniform envelopes return unsupported
// rather than dropping their distinctions. Manifest provenance remains independent.
gig::Result<ReconstructionCheckpoint> capture_checkpoint(const SyntheticReconstructor&,
    std::span<const std::byte> binary_file_prefix,gig::Digest implementation_sha256,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
// Replays the authenticated complete-frame prefix from the authored empty start in
// an isolated fresh instance and compares the entire descriptor before publication.
// Exact config/code identity must be supplied separately; never seeks into a gzip
// stream or restores from native snapshots. The returned instance remains active.
gig::Result<SyntheticReconstructor> restart_from_checkpoint(const ReconstructionCheckpoint&,
    const ReconstructionConfig& expected_config,std::span<const std::byte> binary_file_prefix,
    gig::Digest expected_implementation_sha256,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
} // namespace gig::itch
