#include "validator_batch.hpp"
std::uint64_t count_valid(std::span<const gig::AddOrder> events) noexcept {
    std::uint64_t result = 0;
    for (const auto& event : events) result += gig::valid(event) ? 1U : 0U;
    return result;
}
