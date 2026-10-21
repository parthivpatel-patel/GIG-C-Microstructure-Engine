#pragma once
#include <cstddef>
#include <optional>
#include <string_view>
#include <type_traits>

namespace gig {
enum class ErrorCode {
    none, invalid_range, overflow, underflow, malformed, off_unit,
    invalid_enum, missing_metadata, inconsistent_metadata, duplicate,
    capacity, unsupported, crossed_quote, identity_mismatch
};
struct Error {
    ErrorCode code{ErrorCode::none};
    std::string_view field{}; // Static-lifetime diagnostic paths only; no allocation.
    std::size_t index{0};
    constexpr explicit operator bool() const noexcept { return code != ErrorCode::none; }
    bool operator==(const Error&) const = default;
};
template<class T> struct [[nodiscard]] Result {
    std::optional<T> data;
    Error error;
    constexpr explicit operator bool() const noexcept { return data.has_value(); }
    static constexpr Result success(T value) noexcept(std::is_nothrow_copy_constructible_v<T>) { return {value, {}}; }
    static constexpr Result failure(ErrorCode code, std::string_view field = "numeric", std::size_t index = 0) noexcept {
        return {std::nullopt, {code, field, index}};
    }
};
} // namespace gig
