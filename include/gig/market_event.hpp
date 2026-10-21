#pragma once

#include <cstdint>

namespace gig {

using PriceTicks = std::int64_t;
using Quantity = std::uint64_t;
using OrderId = std::uint64_t;

enum class Side : std::uint8_t { buy, sell };

struct AddOrder {
    OrderId order_id;
    Side side;
    PriceTicks price_ticks;
    Quantity quantity;
    std::uint64_t sequence;
};

[[nodiscard]] constexpr bool valid(const AddOrder& event) noexcept {
    return event.order_id != 0 && event.price_ticks > 0 &&
           event.quantity > 0 && event.sequence > 0;
}

} // namespace gig
