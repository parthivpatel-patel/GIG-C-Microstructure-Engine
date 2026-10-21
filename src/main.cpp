#include <iostream>
#include "fixtures/synthetic/phase1.hpp"
int main() {
    const auto example=gig::fixtures::event();
    const auto checked=gig::make_validated(example,gig::fixtures::rules());
    if (!checked) { std::cerr << "event validation failed\n"; return 1; }
    std::cout << "GIG C++ Microstructure Engine: Phase 1 event contracts ready\n";
}
