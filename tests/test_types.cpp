#include <cassert>
#include "gig/market_event.hpp"

int main() {
    using namespace gig;
    static_assert(valid(AddOrder{1, Side::buy, 100, 10, 1}));
    static_assert(!valid(AddOrder{0, Side::buy, 100, 10, 1}));
    static_assert(!valid(AddOrder{1, Side::sell, 0, 10, 1}));
    static_assert(!valid(AddOrder{1, Side::sell, 100, 0, 1}));
    static_assert(!valid(AddOrder{1, Side::sell, 100, 10, 0}));
    assert(valid(AddOrder{42, Side::sell, 999, 1, 4}));
}
