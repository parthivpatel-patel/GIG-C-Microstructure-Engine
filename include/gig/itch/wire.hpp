#pragma once
#include <array>
#include <compare>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <string_view>
#include <utility>
#include <type_traits>

namespace gig::itch {
template<class Tag> class Position {
    std::uint64_t value_;
public:
    explicit constexpr Position(std::uint64_t value=0) noexcept:value_(value) {}
    constexpr std::uint64_t value() const noexcept { return value_; }
    auto operator<=>(const Position&) const = default;
};
struct ByteOffsetTag; struct RecordOrdinalTag;
using ByteOffset=Position<ByteOffsetTag>;
using RecordOrdinal=Position<RecordOrdinalTag>;
enum class Code : std::uint8_t {
    none, invalid_config, resource_exhausted, record_too_large, stream_limit,
    record_limit, offset_overflow, ordinal_overflow, truncated_length,
    truncated_payload, missing_terminator, trailing_after_terminator,
    already_finished, unknown_type, unsupported_type, length_mismatch,
    invalid_enum, invalid_value, invalid_location
};
struct Error {
    Code code{Code::none}; ByteOffset offset{}; std::string_view field{};
    std::uint64_t expected{},actual{};
    explicit constexpr operator bool() const noexcept { return code!=Code::none; }
    bool operator==(const Error&) const = default;
};
template<class T> struct Result {
    std::optional<T> data; Error error{};
    explicit constexpr operator bool() const noexcept { return data.has_value(); }
    static Result success(T value) noexcept { static_assert(std::is_nothrow_move_constructible_v<T>); return {std::move(value),{}}; }
    static Result failure(Error e) noexcept { return {std::nullopt,e}; }
};
struct Location {
    ByteOffset frame_offset{},payload_offset{}; RecordOrdinal ordinal{};
    bool operator==(const Location&) const = default;
};
class SourceIdentity {
    std::array<char,128> bytes_{}; std::size_t size_{};
    SourceIdentity() noexcept=default;
public:
    static Result<SourceIdentity> make(std::string_view value) noexcept {
        if(value.empty() || value.size()>128) return Result<SourceIdentity>::failure({Code::invalid_value,ByteOffset{},"source.identity",128,value.size()});
        SourceIdentity out;
        for(std::size_t i=0;i<value.size();++i){
            const auto c=static_cast<unsigned char>(value[i]);
            if(c<33 || c>126) return Result<SourceIdentity>::failure({Code::invalid_value,ByteOffset{i},"source.identity",0,c});
            out.bytes_[i]=value[i];
        }
        out.size_=value.size();return Result<SourceIdentity>::success(out);
    }
    std::string_view view() const noexcept { return {bytes_.data(),size_}; }
    bool operator==(const SourceIdentity&) const = default;
};
enum class Origin : std::uint8_t { unspecified, synthetic, observed };
struct Provenance {
    Origin origin{Origin::unspecified}; std::optional<SourceIdentity> source;
    std::optional<std::array<std::byte,32>> sha256;
    std::optional<std::uint64_t> generator_seed;
    bool operator==(const Provenance&) const = default;
};
} // namespace gig::itch
