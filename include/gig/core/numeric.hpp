#pragma once
#include <compare>
#include <concepts>
#include <cstdint>
#include <limits>
#include <numeric>
#include <string_view>
#include <type_traits>
#include <utility>
#include "gig/core/result.hpp"

namespace gig::types {
// No raw constructor, default value, implicit conversion or unchecked arithmetic.
template<class Tag, std::integral Rep, Rep Minimum, bool Arithmetic = false>
class Scalar {
    Rep value_;
    explicit constexpr Scalar(Rep value) noexcept : value_(value) {}
public:
    using rep = Rep;
    static constexpr bool arithmetic = Arithmetic;
    template<std::integral I> requires (!std::same_as<I, bool>)
    static constexpr Result<Scalar> make(I value) noexcept {
        if (!std::in_range<Rep>(value)) return Result<Scalar>::failure(ErrorCode::invalid_range);
        const auto raw = static_cast<Rep>(value);
        if (raw < Minimum) return Result<Scalar>::failure(ErrorCode::invalid_range);
        return Result<Scalar>::success(Scalar(raw));
    }
    constexpr Rep value() const noexcept { return value_; }
    constexpr auto operator<=>(const Scalar&) const = default;
};
struct PriceTag; struct QuantityTag; struct OrderTag; struct InstrumentTag;
struct VenueTag; struct StreamTag; struct SequenceTag; struct EventTimeTag;
struct ReceiveTimeTag; struct SimulationTimeTag; struct DurationTag;
using PriceTicks = Scalar<PriceTag, std::int64_t, INT64_MIN, true>;
using QuantityLots = Scalar<QuantityTag, std::uint64_t, 0, true>;
using OrderId = Scalar<OrderTag, std::uint64_t, 1>;
using InstrumentId = Scalar<InstrumentTag, std::uint64_t, 1>;
using VenueId = Scalar<VenueTag, std::uint64_t, 1>;
using StreamId = Scalar<StreamTag, std::uint64_t, 1>;
using SequenceNumber = Scalar<SequenceTag, std::uint64_t, 0>;
using EventTimestamp = Scalar<EventTimeTag, std::int64_t, INT64_MIN>;
using ReceiveTimestamp = Scalar<ReceiveTimeTag, std::int64_t, INT64_MIN>;
using SimulationTime = Scalar<SimulationTimeTag, std::int64_t, 0>;
using Duration = Scalar<DurationTag, std::int64_t, 0, true>;

namespace detail {
template<std::integral R> constexpr Result<R> add(R a, R b) noexcept {
    constexpr auto hi = std::numeric_limits<R>::max();
    if constexpr (std::is_unsigned_v<R>) {
        if (a > hi - b) return Result<R>::failure(ErrorCode::overflow);
    } else {
        constexpr auto lo = std::numeric_limits<R>::min();
        if ((b > 0 && a > hi - b) || (b < 0 && a < lo - b))
            return Result<R>::failure(ErrorCode::overflow);
    }
    return Result<R>::success(static_cast<R>(a + b));
}
template<std::integral R> constexpr Result<R> subtract(R a, R b) noexcept {
    if constexpr (std::is_unsigned_v<R>) {
        if (a < b) return Result<R>::failure(ErrorCode::underflow);
    } else {
        constexpr auto hi = std::numeric_limits<R>::max();
        constexpr auto lo = std::numeric_limits<R>::min();
        if ((b < 0 && a > hi + b) || (b > 0 && a < lo + b))
            return Result<R>::failure(ErrorCode::overflow);
    }
    return Result<R>::success(static_cast<R>(a - b));
}
template<std::integral R> constexpr Result<R> multiply(R a, R b) noexcept {
    constexpr auto hi = std::numeric_limits<R>::max();
    if constexpr (std::is_unsigned_v<R>) {
        if (b != 0 && a > hi / b) return Result<R>::failure(ErrorCode::overflow);
    } else {
        constexpr auto lo = std::numeric_limits<R>::min();
        if (a > 0 ? (b > 0 ? a > hi / b : b < lo / a) :
            (a < 0 && (b > 0 ? a < lo / b : b < 0 && a < hi / b)))
            return Result<R>::failure(ErrorCode::overflow);
    }
    return Result<R>::success(static_cast<R>(a * b));
}
template<class T, class R> constexpr Result<T> wrap(Result<R> raw) noexcept {
    if (!raw) return Result<T>::failure(raw.error.code);
    return T::make(*raw.data);
}
} // namespace detail

template<class T> requires T::arithmetic
constexpr Result<T> checked_add(T a, T b) noexcept { return detail::wrap<T>(detail::add(a.value(), b.value())); }
template<class T> requires T::arithmetic
constexpr Result<T> checked_subtract(T a, T b) noexcept { return detail::wrap<T>(detail::subtract(a.value(), b.value())); }
template<class T, std::integral I> requires (T::arithmetic && !std::same_as<I, bool>)
constexpr Result<T> checked_multiply(T value, I factor) noexcept {
    if (!std::in_range<typename T::rep>(factor)) return Result<T>::failure(ErrorCode::invalid_range);
    return detail::wrap<T>(detail::multiply(value.value(), static_cast<typename T::rep>(factor)));
}
template<class T, std::integral I> requires (T::arithmetic && !std::same_as<I, bool>)
constexpr Result<T> checked_divide_exact(T value, I divisor) noexcept {
    using R=typename T::rep;
    if (!std::in_range<R>(divisor)) return Result<T>::failure(ErrorCode::invalid_range);
    const auto b=static_cast<R>(divisor),a=value.value();
    if (b==0) return Result<T>::failure(ErrorCode::invalid_range);
    if constexpr (std::is_signed_v<R>) {
        if (a==std::numeric_limits<R>::min() && b==-1) return Result<T>::failure(ErrorCode::overflow);
    }
    if (a%b!=0) return Result<T>::failure(ErrorCode::off_unit);
    return T::make(static_cast<R>(a/b));
}
template<std::integral R, class T> requires (!std::same_as<R, bool>)
constexpr Result<R> checked_cast(T value) noexcept {
    if (!std::in_range<R>(value.value())) return Result<R>::failure(ErrorCode::invalid_range);
    return Result<R>::success(static_cast<R>(value.value()));
}
template<class T> requires (std::same_as<T, EventTimestamp> || std::same_as<T, ReceiveTimestamp> || std::same_as<T, SimulationTime>)
constexpr Result<T> advance(T timestamp, Duration delta) noexcept {
    return detail::wrap<T>(detail::add(timestamp.value(), delta.value()));
}
template<class T> requires (std::same_as<T, EventTimestamp> || std::same_as<T, ReceiveTimestamp> || std::same_as<T, SimulationTime>)
constexpr Result<Duration> elapsed(T later, T earlier) noexcept {
    return detail::wrap<Duration>(detail::subtract(later.value(), earlier.value()));
}
constexpr Result<SequenceNumber> next_sequence(SequenceNumber sequence) noexcept {
    return detail::wrap<SequenceNumber>(detail::add(sequence.value(), std::uint64_t{1}));
}

enum class TimestampUnit : std::uint8_t { nanoseconds, microseconds, milliseconds, seconds };
template<class T, std::integral I> requires (std::same_as<T, EventTimestamp> || std::same_as<T, ReceiveTimestamp> || std::same_as<T, SimulationTime> || std::same_as<T, Duration>) && (!std::same_as<I, bool>)
constexpr Result<T> timestamp_from_count(I count, TimestampUnit unit) noexcept {
    if (!std::in_range<std::int64_t>(count)) return Result<T>::failure(ErrorCode::invalid_range);
    std::int64_t factor{};
    switch (unit) {
    case TimestampUnit::nanoseconds: factor=1; break;
    case TimestampUnit::microseconds: factor=1000; break;
    case TimestampUnit::milliseconds: factor=1000000; break;
    case TimestampUnit::seconds: factor=1000000000; break;
    default: return Result<T>::failure(ErrorCode::invalid_enum);
    }
    return detail::wrap<T>(detail::multiply(static_cast<std::int64_t>(count),factor));
}

// One tick/lot equals numerator/denominator physical units. Positive, reduced on use.
struct UnitScale {
    std::uint64_t numerator;
    std::uint64_t denominator;
    constexpr bool valid() const noexcept { return numerator != 0 && denominator != 0; }
    bool operator==(const UnitScale&) const = default;
};
struct Decimal { bool negative; std::uint64_t magnitude; std::uint64_t denominator; };
constexpr Result<Decimal> parse_decimal(std::string_view input) noexcept {
    if (input.empty() || input.size() > 64) return Result<Decimal>::failure(ErrorCode::malformed);
    bool negative = input.front() == '-';
    std::size_t pos = negative ? 1U : 0U;
    if (pos == input.size()) return Result<Decimal>::failure(ErrorCode::malformed);
    std::uint64_t magnitude = 0, denominator = 1;
    bool dot = false; unsigned fraction = 0; unsigned whole = 0;
    for (; pos < input.size(); ++pos) {
        const auto c = input[pos];
        if (c == '.' && !dot && whole != 0) { dot = true; continue; }
        if (c < '0' || c > '9') return Result<Decimal>::failure(ErrorCode::malformed);
        if (dot) {
            if (++fraction > 18) return Result<Decimal>::failure(ErrorCode::invalid_range);
            denominator *= 10;
        } else ++whole;
        const auto digit = static_cast<std::uint64_t>(c - '0');
        if (magnitude > (UINT64_MAX - digit) / 10) return Result<Decimal>::failure(ErrorCode::overflow);
        magnitude = magnitude * 10 + digit;
    }
    if (whole == 0 || (dot && fraction == 0)) return Result<Decimal>::failure(ErrorCode::malformed);
    return Result<Decimal>::success({negative, magnitude, denominator});
}
constexpr Result<Decimal> exact_units(std::string_view decimal, UnitScale scale) noexcept {
    if (!scale.valid()) return Result<Decimal>::failure(ErrorCode::invalid_range);
    auto parsed = parse_decimal(decimal);
    if (!parsed) return parsed;
    auto amount = *parsed.data;
    auto a = amount.magnitude, b = scale.denominator;
    auto c = amount.denominator, d = scale.numerator;
    const auto cancel = [](std::uint64_t& x, std::uint64_t& y) constexpr {
        const auto divisor = std::gcd(x, y); x /= divisor; y /= divisor;
    };
    cancel(a, c); cancel(a, d); cancel(b, c); cancel(b, d);
    if (c != 1 || d != 1) return Result<Decimal>::failure(ErrorCode::off_unit);
    const auto product = detail::multiply(a, b);
    if (!product) return Result<Decimal>::failure(product.error.code);
    return Result<Decimal>::success({amount.negative, *product.data, 1});
}
constexpr Result<PriceTicks> to_ticks(std::string_view decimal, UnitScale tick) noexcept {
    const auto units = exact_units(decimal, tick);
    if (!units) return Result<PriceTicks>::failure(units.error.code);
    const auto [negative, magnitude, denominator] = *units.data;
    (void)denominator;
    const auto limit = static_cast<std::uint64_t>(INT64_MAX) + (negative ? 1U : 0U);
    if (magnitude > limit) return Result<PriceTicks>::failure(ErrorCode::overflow);
    if (negative && magnitude == (std::uint64_t{1} << 63U)) return PriceTicks::make(INT64_MIN);
    const auto signed_value = static_cast<std::int64_t>(magnitude);
    return PriceTicks::make(negative ? -signed_value : signed_value);
}
constexpr Result<QuantityLots> to_lots(std::string_view decimal, UnitScale lot) noexcept {
    const auto units = exact_units(decimal, lot);
    if (!units) return Result<QuantityLots>::failure(units.error.code);
    if (units.data->negative) return Result<QuantityLots>::failure(ErrorCode::invalid_range);
    return QuantityLots::make(units.data->magnitude);
}
// Exact physical units as signed-magnitude rational, never a rounded double.
template<class T> requires (std::same_as<T, PriceTicks> || std::same_as<T, QuantityLots>)
constexpr Result<Decimal> to_physical(T units, UnitScale scale) noexcept {
    if (!scale.valid()) return Result<Decimal>::failure(ErrorCode::invalid_range);
    bool negative = false;
    std::uint64_t magnitude{};
    if constexpr (std::same_as<T, PriceTicks>) {
        const auto raw = units.value(); negative = raw < 0;
        magnitude = negative ? static_cast<std::uint64_t>(-(raw + 1)) + 1U : static_cast<std::uint64_t>(raw);
    } else magnitude = units.value();
    auto denominator = scale.denominator;
    auto numerator = scale.numerator;
    const auto g1 = std::gcd(magnitude, denominator); magnitude /= g1; denominator /= g1;
    const auto g2 = std::gcd(numerator, denominator); numerator /= g2; denominator /= g2;
    const auto product = detail::multiply(magnitude, numerator);
    if (!product) return Result<Decimal>::failure(product.error.code);
    return Result<Decimal>::success({negative, *product.data, denominator});
}
} // namespace gig::types
