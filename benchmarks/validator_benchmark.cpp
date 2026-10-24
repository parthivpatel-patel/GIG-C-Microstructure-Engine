#include <charconv>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string_view>
#include <vector>
#include "validator_batch.hpp"
#include "fixtures/synthetic/phase1.hpp"
using gig::fixtures::number;

namespace {
std::uint64_t number(const char* text, std::uint64_t limit) {
    const std::string_view input{text};
    std::uint64_t value{};
    const auto result = std::from_chars(input.data(), input.data() + input.size(), value);
    if (result.ec != std::errc{} || result.ptr != input.data() + input.size() ||
        value == 0 || value > limit) throw std::invalid_argument("argument out of range");
    return value;
}
std::uint64_t next(std::uint64_t& state) noexcept {
    // Fixed xorshift64; unsigned shifts/arithmetic are intentional and defined.
    state ^= state << 13U; state ^= state >> 7U; state ^= state << 17U;
    return state;
}
}
int main(int argc, char** argv) {
    try {
        if (argc != 6) throw std::invalid_argument("usage: events repetitions warmup batches seed");
        const auto size = number(argv[1], 1000000);
        const auto repetitions = number(argv[2], 100);
        const auto warmup = number(argv[3], 100);
        const auto batches = number(argv[4], 1000);
        const auto seed = number(argv[5], std::numeric_limits<std::uint64_t>::max());
        auto state = seed;
        auto rules=gig::fixtures::rules();
        rules.maximum_price=number<gig::PriceTicks>(1000000);
        std::vector<gig::AddOrder> events;
        events.reserve(static_cast<std::size_t>(size));
        std::uint64_t oracle = 0;
        std::uint64_t fingerprint = 14695981039346656037ULL;
        const auto hash = [&fingerprint](std::uint64_t value) {
            // FNV-1a over explicit little-endian 64-bit fields, not object padding.
            for (unsigned i = 0; i < 8; ++i) {
                fingerprint ^= (value >> (8U * i)) & 255U;
                fingerprint *= 1099511628211ULL;
            }
        };
        for (std::uint64_t i = 0; i < size; ++i) {
            gig::AddOrder event{number<gig::OrderId>(i+1), gig::Side::buy,
                number<gig::PriceTicks>(next(state) % 1000000U + 1U),
                number<gig::QuantityLots>(next(state) % 10000U + 1U)};
            // Independent truth comes from construction categories, not valid().
            switch (i % 8U) {
            case 0: ++oracle; break;
            case 1: event.side = gig::Side::sell; ++oracle; break;
            case 2: event.side = static_cast<gig::Side>(255); break;
            case 3: event.price_ticks = number<gig::PriceTicks>(0); break;
            case 4: event.price_ticks = number<gig::PriceTicks>(-1); break;
            case 5: event.quantity = number<gig::QuantityLots>(0); break;
            case 6: event.price_ticks = number<gig::PriceTicks>(1000001); break;
            case 7:
                event.price_ticks = number<gig::PriceTicks>(1000000);
                event.quantity = number<gig::QuantityLots>(UINT64_MAX);
                ++oracle; break;
            }
            // Check each item, so aggregate cancellation cannot hide disagreement.
            const bool expected = i % 8U == 0 || i % 8U == 1 || i % 8U == 7;
            if ((!gig::validate(event,rules)) != expected) throw std::runtime_error("oracle mismatch");
            hash(event.order_id.value()); hash(static_cast<std::uint64_t>(event.side));
            hash(static_cast<std::uint64_t>(event.price_ticks.value()));
            hash(event.quantity.value());
            events.push_back(event);
        }
        if (count_valid(events,rules) != oracle) throw std::runtime_error("batch oracle mismatch");
        const auto run = [&events, &rules, batches]() {
            std::uint64_t count = 0;
            for (std::uint64_t b = 0; b < batches; ++b) count += count_valid(events,rules);
            return count;
        };
        const auto expected = oracle * batches; // bounded <= 1e9
        for (std::uint64_t i = 0; i < warmup; ++i)
            if (run() != expected) throw std::runtime_error("warmup mismatch");
        std::cout << "{\"standard_library\":\""
#if defined(__GLIBCXX__)
                  << "libstdc++-" << __GLIBCXX__
#elif defined(_LIBCPP_VERSION)
                  << "libc++-" << _LIBCPP_VERSION
#else
                  << "unknown"
#endif
                  << "\",\"scope\":\"validated_add_order_payload_only\",\"workload_version\":2,"
                  << "\"events\":" << size << ",\"seed\":" << seed
                  << ",\"batches\":" << batches << ",\"warmup\":" << warmup
                  << ",\"repetitions\":" << repetitions << ",\"threads\":1,"
                  << "\"instrument_max_price_ticks\":1000000,\"oracle_valid_per_batch\":" << oracle
                  << ",\"workload_fnv1a64\":\"" << fingerprint << "\",\"samples\":[";
        for (std::uint64_t r = 0; r < repetitions; ++r) {
            const auto start = std::chrono::steady_clock::now();
            const auto actual = run();
            const auto end = std::chrono::steady_clock::now();
            if (actual != expected) throw std::runtime_error("timed result mismatch");
            const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count();
            if (ns <= 0) throw std::runtime_error("timer resolution insufficient");
            if (r != 0) std::cout << ',';
            std::cout << "{\"elapsed_ns\":" << ns << ",\"checked_count\":" << actual << '}';
        }
        std::cout << "]}\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
