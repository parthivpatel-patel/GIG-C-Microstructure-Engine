#include <iostream>
#include <string_view>
#include <string>
#include <type_traits>
#include "gig/core/numeric.hpp"
using namespace gig;
using namespace gig::types;

template<class A, class B> constexpr bool separated = std::same_as<A,B> ||
    (!std::is_convertible_v<A,B> && !std::is_constructible_v<A,B>);
template<class... T> struct Separation;
template<class A, class... Rest> struct Separation<A,Rest...> {
    static constexpr bool value = (separated<A,Rest> && ...) && Separation<Rest...>::value;
};
template<> struct Separation<> { static constexpr bool value = true; };
static_assert(Separation<PriceTicks,QuantityLots,OrderId,InstrumentId,VenueId,StreamId,
    SequenceNumber,EventTimestamp,ReceiveTimestamp,SimulationTime,Duration>::value);
static_assert(!std::is_constructible_v<PriceTicks,double>);
static_assert(!std::is_convertible_v<PriceTicks,std::int64_t>);
static_assert(!std::is_default_constructible_v<OrderId>);
static_assert(!OrderId::make(0) && !QuantityLots::make(-1) && !Duration::make(-1));
static_assert(PriceTicks::make(INT64_MIN) && EventTimestamp::make(INT64_MIN));
static_assert(!checked_add(*PriceTicks::make(INT64_MAX).data,*PriceTicks::make(1).data));
static_assert(!checked_multiply(*PriceTicks::make(INT64_MIN).data,-1));
static_assert(to_ticks("0.3",{1,10}).data->value()==3);
static_assert(!to_ticks("0.31",{1,10}));

template<class T> void emit(const Result<T>& result) {
    if (result) std::cout << result.data->value() << '\n';
    else std::cout << "error\n";
}
int main(int argc, char** argv) {
    if (argc == 2 && std::string_view(argv[1]) == "contracts") {
        int failures = 0;
        const auto check = [&failures](bool ok, const char* message) {
            if (!ok) { ++failures; std::cerr << message << '\n'; }
        };
        check(!OrderId::make(0) && !InstrumentId::make(0) && !VenueId::make(0) && !StreamId::make(0), "zero identifiers");
        check(OrderId::make(UINT64_MAX).data->value()==UINT64_MAX, "max identifier");
        check(!OrderId::make(-1) && !QuantityLots::make(-1) && !Duration::make(-1) && !SimulationTime::make(-1), "signed range");
        check(!checked_cast<std::int32_t>(*PriceTicks::make(INT64_MAX).data), "narrow cast");
        check(!checked_cast<std::uint64_t>(*PriceTicks::make(-1).data), "unsigned cast");
        check(checked_cast<std::int32_t>(*PriceTicks::make(42).data).data==42, "exact cast");
        check(!next_sequence(*SequenceNumber::make(UINT64_MAX).data), "sequence wrap");
        check(next_sequence(*SequenceNumber::make(0).data).data->value()==1, "zero-based sequence");
        check(EventTimestamp::make(INT64_MIN) && ReceiveTimestamp::make(INT64_MAX), "timestamp endpoints");
        check(!advance(*EventTimestamp::make(INT64_MAX).data,*Duration::make(1).data), "time overflow");
        check(advance(*SimulationTime::make(0).data,*Duration::make(1).data).data->value()==1, "time advance");
        check(!elapsed(*ReceiveTimestamp::make(0).data,*ReceiveTimestamp::make(1).data), "negative elapsed");
        check(!elapsed(*EventTimestamp::make(INT64_MAX).data,*EventTimestamp::make(INT64_MIN).data), "elapsed overflow");
        check(elapsed(*EventTimestamp::make(0).data,*EventTimestamp::make(-1).data).data->value()==1, "elapsed exact");
        check(timestamp_from_count<EventTimestamp>(-1,TimestampUnit::seconds).data->value()==-1000000000, "timestamp units");
        check(!timestamp_from_count<ReceiveTimestamp>(INT64_MAX,TimestampUnit::microseconds), "timestamp conversion overflow");
        check(!timestamp_from_count<Duration>(1,static_cast<TimestampUnit>(255)), "timestamp unit enum");
        check(checked_subtract(*QuantityLots::make(0).data,*QuantityLots::make(1).data).error.code==ErrorCode::underflow, "structured underflow");
        check(to_ticks("0.31",{1,10}).error.code==ErrorCode::off_unit, "structured off tick");
        const auto physical=to_physical(*PriceTicks::make(INT64_MIN).data,{1,2});
        check(physical && physical.data->negative && physical.data->magnitude==(std::uint64_t{1}<<62U) && physical.data->denominator==1, "physical min");
        check(!to_physical(*QuantityLots::make(UINT64_MAX).data,{2,1}), "physical overflow");
        check(!to_physical(*PriceTicks::make(1).data,{1,0}), "bad scale");
        check(to_physical(*QuantityLots::make(3).data,{1,2}).data->denominator==2, "fraction preserved");
        check(to_ticks("-9223372036854775808",{1,1}).data->value()==INT64_MIN, "parse signed min");
        check(to_lots("18446744073709551615",{1,1}).data->value()==UINT64_MAX, "parse unsigned max");
        check(!to_lots("-0",{1,1}) && !to_ticks(" 1",{1,1}) && !to_ticks("",{1,1}), "malformed/signed zero");
        check(!checked_multiply(*QuantityLots::make(1).data,-1), "negative multiplier");
        std::cout << "numeric contracts: " << failures << " failures\n";
        return failures==0 ? 0 : 1;
    }
    if (argc != 1) return 2;
    std::string op;
    while (std::cin >> op) {
        if (op == "ticks" || op == "lots") {
            std::string decimal; std::uint64_t n{},d{};
            if (!(std::cin >> decimal >> n >> d)) return 2;
            if (op == "ticks") emit(to_ticks(decimal,{n,d})); else emit(to_lots(decimal,{n,d}));
        } else if (op == "sadd" || op == "ssub" || op == "smul") {
            std::int64_t a{},b{}; if (!(std::cin >> a >> b)) return 2;
            auto x=*PriceTicks::make(a).data, y=*PriceTicks::make(b).data;
            if (op == "sadd") emit(checked_add(x,y));
            else if (op == "ssub") emit(checked_subtract(x,y)); else emit(checked_multiply(x,b));
        } else if (op == "uadd" || op == "usub" || op == "umul") {
            std::uint64_t a{},b{}; if (!(std::cin >> a >> b)) return 2;
            auto x=*QuantityLots::make(a).data,y=*QuantityLots::make(b).data;
            if (op == "uadd") emit(checked_add(x,y));
            else if (op == "usub") emit(checked_subtract(x,y)); else emit(checked_multiply(x,b));
        } else return 2;
    }
    return std::cin.eof() ? 0 : 2;
}
