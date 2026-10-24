#include "gig/itch/gzip.hpp"
#include <algorithm>
#include <cstddef>
#include <limits>
#include <new>
#include <vector>
#include <zlib.h>

namespace gig::itch {
struct GzipReader::State {
    struct alignas(std::max_align_t) Allocation {std::size_t size;};
    GzipLimits limits;
    std::pmr::memory_resource* resource;
    std::pmr::vector<std::byte> output;
    z_stream stream{};
    gz_header header{};
    std::uint64_t compressed{},decompressed{};
    GzipError error{};
    std::optional<GzipFinish> final;
    bool initialized{},verified{},allocation_failed{};
    State(GzipLimits l,std::pmr::memory_resource* r):limits(l),resource(r),output(r){}
    ~State(){if(initialized)(void)inflateEnd(&stream);}
    static voidpf allocate(voidpf opaque,uInt items,uInt size) noexcept {
        auto* self=static_cast<State*>(opaque);
        const auto a=static_cast<std::size_t>(items),b=static_cast<std::size_t>(size);
        if((b!=0&&a>(SIZE_MAX-sizeof(Allocation))/b)){self->allocation_failed=true;return Z_NULL;}
        const auto bytes=a*b+sizeof(Allocation);
        try{auto* allocation=static_cast<Allocation*>(self->resource->allocate(bytes,alignof(Allocation)));allocation->size=bytes;return allocation+1;}
        catch(...){self->allocation_failed=true;return Z_NULL;}
    }
    static void release(voidpf opaque,voidpf address) noexcept {
        if(!address)return;
        auto* self=static_cast<State*>(opaque);auto* allocation=static_cast<Allocation*>(address)-1;
        self->resource->deallocate(allocation,allocation->size,alignof(Allocation));
    }
    GzipError stop(GzipCode code,int library=0) noexcept {
        if(!error)error={code,compressed,decompressed,library};
        return error;
    }
    bool ratio_allows_next()const noexcept {
        const auto allowed=decompressed+1;
        if(allowed<=limits.expansion_slack_bytes)return true;
        const auto excess=allowed-limits.expansion_slack_bytes;
        // ceil(excess/ratio)<=compressed, avoiding overflowing product/sum.
        const auto quotient=excess/limits.max_expansion_ratio;
        const auto remainder=excess%limits.max_expansion_ratio;
        return quotient<compressed||(quotient==compressed&&remainder==0);
    }
};
GzipReader::GzipReader(std::unique_ptr<State,Deleter> state) noexcept:state_(std::move(state)){}
GzipReader::~GzipReader()=default;
GzipReader::GzipReader(GzipReader&&) noexcept=default;
GzipReader& GzipReader::operator=(GzipReader&&) noexcept=default;
void GzipReader::Deleter::operator()(State* state)const noexcept {
    if(state){std::pmr::polymorphic_allocator<State> allocator(resource);allocator.delete_object(state);}
}
gig::Result<GzipReader> GzipReader::create(GzipLimits limits,std::pmr::memory_resource* resource) noexcept {
    if(!resource||limits.output_buffer_bytes==0||limits.output_buffer_bytes>65536
        ||limits.max_compressed_bytes==0||limits.max_decompressed_bytes==UINT64_MAX
        ||limits.max_expansion_ratio==0||limits.max_header_bytes==0)
        return gig::Result<GzipReader>::failure(gig::ErrorCode::invalid_range,"gzip.limits");
    try {
        std::pmr::polymorphic_allocator<State> allocator(resource);
        std::unique_ptr<State,Deleter> state(allocator.new_object<State>(limits,resource),Deleter{resource});
        state->output.resize(limits.output_buffer_bytes);
        state->stream.zalloc=&State::allocate;state->stream.zfree=&State::release;state->stream.opaque=state.get();
        const auto initialized=inflateInit2(&state->stream,15+16);
        if(initialized!=Z_OK)return gig::Result<GzipReader>::failure(initialized==Z_MEM_ERROR?gig::ErrorCode::resource_exhausted:gig::ErrorCode::unsupported,"gzip.initialize");
        state->initialized=true;
        if(inflateGetHeader(&state->stream,&state->header)!=Z_OK)return gig::Result<GzipReader>::failure(gig::ErrorCode::unsupported,"gzip.header_observer");
        return gig::Result<GzipReader>::success(GzipReader(std::move(state)));
    }catch(...){return gig::Result<GzipReader>::failure(gig::ErrorCode::resource_exhausted,"gzip.storage");}
}
GzipFeed GzipReader::feed(std::span<const std::byte> input) noexcept {
    if(!state_)return {0,{},{GzipCode::moved_from,0,0,0},false};
    auto& s=*state_;
    if(s.error)return {0,{},s.error,s.verified};
    if(s.final)return {0,{},{GzipCode::already_finished,s.compressed,s.decompressed,0},s.verified};
    if(s.verified){if(!input.empty())s.stop(GzipCode::trailing_data);return {0,{},s.error,true};}
    std::size_t consumed=0,produced=0;
    while(produced<s.output.size()){
        // One-byte input/output steps are a versioned deterministic policy. Neither
        // caller input fragmentation nor output chunk capacity alters admission order.
        const bool has_input=consumed<input.size();
        const bool compressed_room=s.compressed<s.limits.max_compressed_bytes;
        const bool header_room=s.header.done!=0||s.compressed<s.limits.max_header_bytes;
        const bool offer=has_input&&compressed_room&&header_room;
        s.stream.next_in=offer?reinterpret_cast<Bytef*>(const_cast<std::byte*>(input.data()+consumed)):Z_NULL;
        s.stream.avail_in=offer?1U:0U;
        std::byte byte{};s.stream.next_out=reinterpret_cast<Bytef*>(&byte);s.stream.avail_out=1;
        const auto result=inflate(&s.stream,s.header.done==0?Z_BLOCK:Z_NO_FLUSH);
        const auto read=offer?static_cast<std::size_t>(1-s.stream.avail_in):0U;
        const auto wrote=static_cast<std::size_t>(1-s.stream.avail_out);
        consumed+=read;s.compressed+=read;
        if(wrote){
            if(s.decompressed==s.limits.max_decompressed_bytes){s.stop(GzipCode::decompressed_limit,result);break;}
            if(!s.ratio_allows_next()){s.stop(GzipCode::expansion_limit,result);break;}
            s.output[produced++]=byte;++s.decompressed;
        }
        if(result==Z_STREAM_END){s.verified=true;break;}
        if(result!=Z_OK&&result!=Z_BUF_ERROR){s.stop(result==Z_MEM_ERROR||s.allocation_failed?GzipCode::allocation_failure:GzipCode::corrupt,result);break;}
        if(read==0&&wrote==0){
            if(has_input&&!compressed_room)s.stop(GzipCode::compressed_limit,result);
            else if(has_input&&!header_room)s.stop(GzipCode::header_limit,result);
            // Z_BLOCK may report a header boundary with no consumption. With an
            // observed completed header, continue once in ordinary inflate mode.
            else if(result==Z_OK&&s.header.done!=0&&offer)continue;
            break;
        }
    }
    // Do not retain pointers into caller buffers across calls/moves.
    s.stream.next_in=Z_NULL;s.stream.avail_in=0;s.stream.next_out=Z_NULL;s.stream.avail_out=0;
    return {consumed,std::span<const std::byte>(s.output.data(),produced),s.error,s.verified};
}
GzipFinish GzipReader::finish(EndKind kind) noexcept {
    if(!state_)return {false,false,false,0,0,{GzipCode::moved_from,0,0,0}};
    auto& s=*state_;if(s.final)return *s.final;
    if(kind!=EndKind::source_eof&&kind!=EndKind::bounded_prefix)
        return {false,false,s.verified,s.compressed,s.decompressed,{GzipCode::invalid_config,s.compressed,s.decompressed,0}};
    if(!s.error&&!s.verified&&kind==EndKind::source_eof)s.stop(GzipCode::truncated);
    s.final=GzipFinish{!s.error&&s.verified&&kind==EndKind::source_eof,kind==EndKind::bounded_prefix,s.verified,s.compressed,s.decompressed,s.error};
    return *s.final;
}
std::uint64_t GzipReader::compressed_bytes()const noexcept{return state_?state_->compressed:0;}
std::uint64_t GzipReader::decompressed_bytes()const noexcept{return state_?state_->decompressed:0;}
bool GzipReader::member_verified()const noexcept{return state_&&state_->verified;}
GzipError GzipReader::error()const noexcept{return state_?state_->error:GzipError{GzipCode::moved_from,0,0,0};}
std::size_t GzipReader::output_buffer_bytes()const noexcept{return state_?state_->output.size():0;}
} // namespace gig::itch
