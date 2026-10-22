#include "gig/itch/binary_file.hpp"
#include <algorithm>
#include <cstring>
#include <limits>
namespace gig::itch {
BinaryFileFramer::BinaryFileFramer(FramerLimits l,Buffer b,ByteOffset o,RecordOrdinal n) noexcept
:limits_(l),buffer_(std::move(b)),offset_(o),frame_start_(o),next_ordinal_(n) {}
Result<BinaryFileFramer> BinaryFileFramer::create(FramerLimits l,ByteOffset o,RecordOrdinal n,std::pmr::memory_resource* r) noexcept {
    if(!r || l.max_payload_bytes==0 || l.max_payload_bytes>l.buffer_bytes || l.buffer_bytes>65535)
        return Result<BinaryFileFramer>::failure({Code::invalid_config,o,"limits",65535,l.buffer_bytes});
    try {
        Buffer b(static_cast<std::byte*>(r->allocate(l.buffer_bytes,alignof(std::byte))),Deleter{r,l.buffer_bytes});
        return Result<BinaryFileFramer>::success(BinaryFileFramer(l,std::move(b),o,n));
    } catch(...) { return Result<BinaryFileFramer>::failure({Code::resource_exhausted,o,"buffer",l.buffer_bytes,0}); }
}
FrameResult BinaryFileFramer::fail(Error e,std::size_t n) noexcept { stopped_=e;return {FrameStatus::error,n,std::nullopt,e}; }
FrameResult BinaryFileFramer::feed(std::span<const std::byte> in) noexcept {
    if(stopped_) return {FrameStatus::error,0,std::nullopt,stopped_};
    if(!buffer_) return fail({Code::invalid_config,offset_,"moved_from",0,0},0);
    if(finished_) return {FrameStatus::error,0,std::nullopt,{Code::already_finished,offset_,"finish",0,0}};
    if(terminal_) {
        if(!in.empty()) return fail({Code::trailing_after_terminator,offset_,"trailing",0,in.size()},0);
        return {FrameStatus::terminal,0,std::nullopt,{}};
    }
    std::size_t used=0;
    while(used<in.size()) {
        if(consumed_==limits_.max_stream_bytes) return fail({Code::stream_limit,offset_,"stream",limits_.max_stream_bytes,consumed_},used);
        if(offset_.value()==UINT64_MAX) return fail({Code::offset_overflow,offset_,"offset",UINT64_MAX,UINT64_MAX},used);
        if(prefix_size_<2) {
            if(prefix_size_==0) frame_start_=offset_;
            prefix_[prefix_size_++]=in[used++];++consumed_;offset_=ByteOffset{offset_.value()+1};
            if(prefix_size_<2) continue;
            length_=(std::to_integer<std::size_t>(prefix_[0])<<8)|std::to_integer<std::size_t>(prefix_[1]);
            if(length_==0) {terminal_=true;prefix_size_=0;return {FrameStatus::terminal,used,std::nullopt,{}};}
            if(length_>limits_.max_payload_bytes) return fail({Code::record_too_large,frame_start_,"length",limits_.max_payload_bytes,length_},used);
            if(records_==limits_.max_records) return fail({Code::record_limit,frame_start_,"records",limits_.max_records,records_},used);
            if(ordinal_exhausted_) return fail({Code::ordinal_overflow,frame_start_,"ordinal",UINT64_MAX,UINT64_MAX},used);
        }
        const auto count=static_cast<std::size_t>(std::min<std::uint64_t>({in.size()-used,length_-payload_size_,limits_.max_stream_bytes-consumed_,UINT64_MAX-offset_.value()}));
        if(count==0) continue; // Next iteration emits the exact exhausted-bound error.
        std::memcpy(buffer_.get()+payload_size_,in.data()+used,count);
        payload_size_+=count;used+=count;consumed_+=count;offset_=ByteOffset{offset_.value()+count};
        if(payload_size_==length_) {
            const FrameView frame{{frame_start_,ByteOffset{frame_start_.value()+2},next_ordinal_},{buffer_.get(),length_}};
            ++records_;
            if(next_ordinal_.value()==UINT64_MAX) ordinal_exhausted_=true;
            else next_ordinal_=RecordOrdinal{next_ordinal_.value()+1};
            prefix_size_=payload_size_=0;
            return {FrameStatus::record,used,frame,{}};
        }
    }
    return {FrameStatus::need_more,used,std::nullopt,{}};
}
FinishResult BinaryFileFramer::finish(EndKind kind) noexcept {
    if(final_) return *final_;
    FinishResult out{terminal_,kind==EndKind::bounded_prefix,prefix_size_+payload_size_,stopped_};
    if(!out.error && kind!=EndKind::source_eof && kind!=EndKind::bounded_prefix) out.error={Code::invalid_enum,offset_,"end_kind",0,static_cast<std::uint64_t>(kind)};
    if(!out.error && kind==EndKind::source_eof && !terminal_) {
        if(prefix_size_==1) out.error={Code::truncated_length,frame_start_,"length",2,1};
        else if(prefix_size_==2) out.error={Code::truncated_payload,ByteOffset{frame_start_.value()+2},"payload",length_,payload_size_};
        else out.error={Code::missing_terminator,offset_,"terminator",2,0};
    }
    out.session_complete=terminal_ && !out.error && kind==EndKind::source_eof;
    finished_=true; final_=out; return out;
}
} // namespace gig::itch
