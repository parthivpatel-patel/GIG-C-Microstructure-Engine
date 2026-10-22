#pragma once
#include <memory>
#include <memory_resource>
#include <span>
#include "gig/itch/wire.hpp"

namespace gig::itch {
struct FramerLimits {
    std::size_t max_payload_bytes{65535},buffer_bytes{65535};
    std::uint64_t max_records{100000},max_stream_bytes{UINT64_MAX};
};
struct FrameView {
    Location location; std::span<const std::byte> payload;
};
enum class FrameStatus : std::uint8_t { need_more, record, terminal, error };
struct FrameResult {
    FrameStatus status{FrameStatus::need_more}; std::size_t consumed{};
    std::optional<FrameView> frame; Error error{};
};
enum class EndKind : std::uint8_t { source_eof, bounded_prefix };
struct FinishResult {
    bool session_complete{}; bool bounded_prefix{}; std::uint64_t residual_bytes{};
    Error error{};
};
// The supplied PMR resource must outlive this object. One allocation at create;
// feed/finish allocate nothing. Limits include terminal bytes but not an external
// transport/container; record ordinals are local capture identities, not exchange sequence.
// Pull interface emits at most one record/terminal per call. FrameView is borrowed
// until the next nonempty feed or destruction. Finish seals the reader, not input.
class BinaryFileFramer {
    struct Deleter { std::pmr::memory_resource* resource{}; std::size_t size{}; void operator()(std::byte* p) const noexcept { if(p) resource->deallocate(p,size,alignof(std::byte)); } };
    using Buffer=std::unique_ptr<std::byte[],Deleter>;
    FramerLimits limits_; Buffer buffer_;
    std::array<std::byte,2> prefix_{}; std::size_t prefix_size_{},payload_size_{},length_{};
    ByteOffset offset_{},frame_start_{}; RecordOrdinal next_ordinal_{};
    std::uint64_t consumed_{},records_{}; bool ordinal_exhausted_{},terminal_{},finished_{};
    Error stopped_{}; std::optional<FinishResult> final_;
    BinaryFileFramer(FramerLimits,Buffer,ByteOffset,RecordOrdinal) noexcept;
    FrameResult fail(Error,std::size_t) noexcept;
public:
    static Result<BinaryFileFramer> create(FramerLimits={},ByteOffset=ByteOffset{},RecordOrdinal=RecordOrdinal{},std::pmr::memory_resource* = std::pmr::get_default_resource()) noexcept;
    BinaryFileFramer(BinaryFileFramer&&) noexcept=default;
    BinaryFileFramer& operator=(BinaryFileFramer&&) noexcept=default;
    BinaryFileFramer(const BinaryFileFramer&)=delete;
    BinaryFileFramer& operator=(const BinaryFileFramer&)=delete;
    FrameResult feed(std::span<const std::byte>) noexcept;
    FinishResult finish(EndKind=EndKind::source_eof) noexcept;
    ByteOffset position() const noexcept { return offset_; }
    std::uint64_t records() const noexcept { return records_; }
    std::size_t allocated_payload_bytes() const noexcept { return buffer_?limits_.buffer_bytes:0; }
    bool terminated() const noexcept { return terminal_; }
};
} // namespace gig::itch
