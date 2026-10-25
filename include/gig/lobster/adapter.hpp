#pragma once
#include "gig/core/result.hpp"
#include <array>
#include <chrono>
#include <cstdint>
#include <optional>
#include <string_view>
namespace gig::lobster {
struct TimeNs { std::uint64_t value; bool operator==(const TimeNs&)const=default; };
struct Price4 { std::int64_t value; bool operator==(const Price4&)const=default; };
struct Shares { std::uint64_t value; bool operator==(const Shares&)const=default; };
enum class Kind : std::uint8_t { add, cancel, erase, visible_execution, hidden_execution, halt, unsupported };
struct Message { TimeNs time; std::uint32_t code; std::uint64_t order; Shares quantity; Price4 price; std::int64_t direction; Kind kind; bool operator==(const Message&)const=default; };
struct Level { Price4 price; Shares quantity; bool missing; bool operator==(const Level&)const=default; };
struct Reference { std::array<Level,5> asks,bids; bool locked{},crossed{},zero_volume{}; std::size_t missing_levels{}; bool operator==(const Reference&)const=default; };
gig::Result<Message> parse_message(std::string_view) noexcept;
gig::Result<Reference> parse_reference(std::string_view) noexcept;
struct Limits { std::uint64_t max_bytes{128U*1024U*1024U},max_records{1000000}; std::size_t max_line_bytes{4096}; std::uint64_t max_milliseconds{120000}; std::size_t max_errors{1}; };
struct Summary {std::uint64_t accepted{},bytes{},rejected{},locked{},crossed{},zero_volume{},missing_levels{},unsupported{};std::array<std::uint64_t,8> codes{};std::optional<TimeNs> first,last;bool stopped{},input_complete{},full_l3_complete{};};
struct Pair {Message message;Reference reference;};
// Single explicit externally supplied instrument. No inferred exchange IDs/timezone.
// No allocation or book mutation. Both rows validate before accepted state changes.
class PairedValidator {
    Limits limits_;Summary summary_{};std::chrono::steady_clock::time_point start_;
    explicit PairedValidator(Limits) noexcept;
public:
    static gig::Result<PairedValidator> create(Limits={}) noexcept;
    gig::Result<Pair> accept(std::string_view message,std::string_view reference) noexcept;
    gig::Error finish(bool message_eof,bool reference_eof) noexcept;
    const Summary& summary()const noexcept{return summary_;}
};
} // namespace gig::lobster
