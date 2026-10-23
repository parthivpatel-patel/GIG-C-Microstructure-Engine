#pragma once
#include <memory>
#include <memory_resource>
#include <span>
#include "gig/core/result.hpp"
#include "gig/itch/binary_file.hpp"

namespace gig::itch {
// Independent limits: the tighter compressed/header bound applies first.
struct GzipLimits {
    std::size_t output_buffer_bytes{65536};
    std::uint64_t max_compressed_bytes{1024*1024},max_decompressed_bytes{32*1024*1024};
    std::uint64_t max_expansion_ratio{1024},expansion_slack_bytes{65536},max_header_bytes{65536};
    bool operator==(const GzipLimits&) const=default;
};
enum class GzipCode : std::uint8_t {
    none,invalid_config,allocation_failure,compressed_limit,decompressed_limit,
    expansion_limit,header_limit,corrupt,truncated,trailing_data,already_finished,moved_from
};
struct GzipError {
    GzipCode code{GzipCode::none};
    std::uint64_t compressed_offset{},decompressed_offset{};
    int library_code{};
    explicit operator bool()const noexcept{return code!=GzipCode::none;}
    bool operator==(const GzipError&)const=default;
};
struct GzipFeed {
    std::size_t consumed{};
    std::span<const std::byte> output;
    GzipError error{};
    bool member_ended{};
};
struct GzipFinish {
    bool complete{},bounded_prefix{},member_verified{};
    std::uint64_t compressed_bytes{},decompressed_bytes{};
    GzipError error{};
    bool operator==(const GzipFinish&)const=default;
};
// Single-member gzip only. Extra members/trailing bytes are explicit errors.
// No passthrough of plain/zlib/raw-deflate input. EOF is supplied only by finish.
// Output is borrowed until next feed or destruction of the owning state. Moves
// transfer that stable state and preserve its buffer address. Each call publishes at
// most output_buffer_bytes. Call again with unconsumed bytes; empty input can drain
// cached output. Output accompanying an error is still an unverified prefix; the
// caller must mark the whole source integrity-ineligible. Fixed one-input-byte /
// one-output-byte inflate steps make prefix/limit outcomes independent of caller
// fragmentation; this is a conservative correctness baseline, not an optimization.
// Exact output-cap verification uses at most one internal overflow-probe byte;
// it is never published/counted as accepted decompressed output. The caller-owned
// PMR must outlive reader. All zlib allocation exceptions are contained at C ABI.
class GzipReader {
    struct State;
    struct Deleter {std::pmr::memory_resource* resource{};void operator()(State*)const noexcept;};
    std::unique_ptr<State,Deleter> state_;
    explicit GzipReader(std::unique_ptr<State,Deleter>) noexcept;
public:
    static gig::Result<GzipReader> create(GzipLimits={},std::pmr::memory_resource* =std::pmr::get_default_resource()) noexcept;
    ~GzipReader();
    GzipReader(GzipReader&&) noexcept;
    GzipReader& operator=(GzipReader&&) noexcept;
    GzipReader(const GzipReader&)=delete;
    GzipReader& operator=(const GzipReader&)=delete;
    GzipFeed feed(std::span<const std::byte>) noexcept;
    GzipFinish finish(EndKind=EndKind::source_eof) noexcept;
    std::uint64_t compressed_bytes()const noexcept;
    std::uint64_t decompressed_bytes()const noexcept;
    bool member_verified()const noexcept;
    GzipError error()const noexcept;
    std::size_t output_buffer_bytes()const noexcept;
};
} // namespace gig::itch
