#pragma once
#include "gig/itch/reconstruction.hpp"
#include "gig/itch/sha256.hpp"
namespace gig::itch {
struct SeedDirectory { std::array<std::byte,39> payload; };
struct SeedOrder { OrderState state; std::uint64_t priority; };
// Borrowed only for create_seeded(); no seed span is retained. Retired IDs carry
// no fabricated stock/side/price history. Caller separately owns fixture evidence.
struct SeedState {
    Location boundary;
    std::uint8_t lifecycle_stage;
    std::optional<TimestampNanoseconds> last_timestamp;
    std::span<const SeedDirectory> directories;
    std::span<const SeedOrder> orders;
    std::span<const OrderReference> retired;
    std::span<const MatchState> matches;
};
// Canonical versioned binary SHA256, sorted by identities; no object-layout hash.
// Limits2 directories/128 orders/4096 retired/4096 matches. No allocation.
gig::Result<Sha256Digest> seed_sha256(const SeedState&,SourceIdentity,SourceIdentity) noexcept;
// Re-create from trusted seed + exact authenticated complete-frame continuation.
// Returns an active accepted prefix, not a deserialized hot state or full session.
gig::Result<SyntheticReconstructor> restart_seeded_prefix(ReconstructionConfig,const SeedState&,
    Sha256Digest trusted_seed,std::span<const std::byte> prefix,Sha256Digest trusted_prefix,
    std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
} // namespace gig::itch
