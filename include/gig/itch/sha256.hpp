#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace gig::itch {
using Sha256Digest=std::array<std::byte,32>;
// FIPS180-4 SHA-256; fixed storage, no allocation, no secret/key processing.
class Sha256 {
    std::array<std::uint32_t,8> state_{0x6a09e667U,0xbb67ae85U,0x3c6ef372U,0xa54ff53aU,0x510e527fU,0x9b05688cU,0x1f83d9abU,0x5be0cd19U};
    std::array<std::byte,64> pending_{};
    std::uint64_t bytes_{};
    std::size_t used_{};
    void block(const std::byte*) noexcept;
public:
    // False means bit-length overflow; the complete call is rejected without mutation.
    bool update(std::span<const std::byte>) noexcept;
    // Non-destructive finalization: repeated calls and subsequent update are supported.
    Sha256Digest finish() const noexcept;
};
// Convenience for ordinary bounded buffers. Span length must fit SHA-256's bit length.
Sha256Digest sha256(std::span<const std::byte>) noexcept;
std::array<char,64> hex_digest(Sha256Digest) noexcept;
} // namespace gig::itch
