#include <iostream>
#include <string_view>
#include "fixtures/synthetic/phase1.hpp"
int main(int argc,char** argv) {
    using namespace gig; using namespace gig::fixtures;
    if (argc!=2) return 2;
    const std::string_view name{argv[1]};
    auto e=order(); const auto config=rules(); bool ok=false;
    if (name=="valid_buy") ok=!validate(e,config);
    else if (name=="valid_sell") { e.side=Side::sell; ok=!validate(e,config); }
    else if (name=="zero_id") ok=!OrderId::make(0);
    else if (name=="zero_price") { e.price_ticks=number<PriceTicks>(0); ok=bool(validate(e,config)); }
    else if (name=="negative_price") { e.price_ticks=number<PriceTicks>(-1); ok=bool(validate(e,config)); }
    else if (name=="zero_quantity") { e.quantity=number<QuantityLots>(0); ok=bool(validate(e,config)); }
    else if (name=="zero_based_sequence") ok=!validate(event(),config);
    else if (name=="max_price") { e.price_ticks=number<PriceTicks>(INT64_MAX); ok=!validate(e,config); }
    else if (name=="max_quantity") { e.quantity=number<QuantityLots>(UINT64_MAX); ok=!validate(e,config); }
    else if (name=="max_id") { e.order_id=number<OrderId>(UINT64_MAX); ok=!validate(e,config); }
    else if (name=="max_sequence") { auto m=metadata();m.sequence=Available<SequenceNumber>::known(number<SequenceNumber>(UINT64_MAX));ok=!validate(m); }
    else if (name=="deliberate_failure") ok=false;
    else return 2;
    if (!ok) { std::cerr << "FAIL: " << name << '\n'; return 1; }
    std::cout << "PASS: " << name << '\n'; return 0;
}
