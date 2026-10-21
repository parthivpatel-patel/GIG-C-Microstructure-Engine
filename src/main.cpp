#include <iostream>
#include "gig/market_event.hpp"

int main() {
    constexpr gig::AddOrder example{1, gig::Side::buy, 10050, 100, 1};
    static_assert(gig::valid(example));
    std::cout << "GIG C++ Microstructure Engine: scaffold ready\n";
}
