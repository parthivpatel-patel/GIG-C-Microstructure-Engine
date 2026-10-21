#include <iostream>
#include <limits>
#include <string_view>
#include "gig/market_event.hpp"

// Explicit checks remain active under NDEBUG. No domain contract is expanded here.
int main(int argc, char** argv) {
    using namespace gig;
    if (argc != 2) { std::cerr << "expected one named case\n"; return 2; }
    const std::string_view name{argv[1]};
    AddOrder event{1, Side::buy, 100, 10, 1};
    bool expected = true;
    if (name == "valid_buy") {}
    else if (name == "valid_sell") event.side = Side::sell;
    else if (name == "zero_id") { event.order_id = 0; expected = false; }
    else if (name == "zero_price") { event.price_ticks = 0; expected = false; }
    else if (name == "negative_price") { event.price_ticks = -1; expected = false; }
    else if (name == "zero_quantity") { event.quantity = 0; expected = false; }
    else if (name == "zero_sequence") { event.sequence = 0; expected = false; }
    else if (name == "max_price") event.price_ticks = std::numeric_limits<PriceTicks>::max();
    else if (name == "max_quantity") event.quantity = std::numeric_limits<Quantity>::max();
    else if (name == "max_id") event.order_id = std::numeric_limits<OrderId>::max();
    else if (name == "max_sequence") event.sequence = std::numeric_limits<std::uint64_t>::max();
    else if (name == "deliberate_failure") expected = false;
    else { std::cerr << "unknown case: " << name << '\n'; return 2; }
    if (valid(event) != expected) {
        std::cerr << "FAIL: " << name << '\n';
        return 1;
    }
    std::cout << "PASS: " << name << '\n';
    return 0;
}
