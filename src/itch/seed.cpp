#include "gig/itch/seed.hpp"
#include "gig/itch/binary_file.hpp"
#include <algorithm>
#include <numeric>
namespace gig::itch {
gig::Result<Sha256Digest> seed_sha256(const SeedState& s,SourceIdentity source,SourceIdentity session) noexcept {
    if(s.directories.size()>2||s.orders.size()>128||s.retired.size()>4096||s.matches.size()>4096)
        return gig::Result<Sha256Digest>::failure(gig::ErrorCode::capacity,"seed.hash_limits");
    Sha256 hash;
    const auto number=[&](std::uint64_t x){std::array<std::byte,8> b{};for(std::size_t i=0;i<8;++i){b[7-i]=static_cast<std::byte>(x&255);x>>=8;}(void)hash.update(b);};
    const auto text=[&](std::string_view v){number(v.size());(void)hash.update(std::as_bytes(std::span(v.data(),v.size())));};
    text("gig.typed_seed.v1");text(source.view());text(session.view());
    number(s.boundary.frame_offset.value());number(s.boundary.payload_offset.value());number(s.boundary.ordinal.value());number(s.lifecycle_stage);number(s.last_timestamp.has_value());if(s.last_timestamp)number(s.last_timestamp->value());
    std::array<std::size_t,4096> indices{};
    const auto sorted=[&](std::size_t n,const auto& less){std::iota(indices.begin(),indices.begin()+static_cast<std::ptrdiff_t>(n),std::size_t{});std::sort(indices.begin(),indices.begin()+static_cast<std::ptrdiff_t>(n),less);};
    number(s.directories.size());sorted(s.directories.size(),[&](auto a,auto b){return s.directories[a].payload<s.directories[b].payload;});
    for(std::size_t i=0;i<s.directories.size();++i)(void)hash.update(s.directories[indices[i]].payload);
    number(s.orders.size());sorted(s.orders.size(),[&](auto a,auto b){return s.orders[a].state.reference<s.orders[b].state.reference;});
    for(std::size_t i=0;i<s.orders.size();++i){const auto& x=s.orders[indices[i]];const auto& o=x.state;number(o.reference.value());number(o.locate.value());text(o.stock.view());number(static_cast<unsigned char>(o.side));number(o.remaining.value());number(o.resting_price.value());number(o.attribution.has_value());if(o.attribution)text(o.attribution->view());number(o.arrival.value());number(o.active);number(x.priority);}
    number(s.retired.size());sorted(s.retired.size(),[&](auto a,auto b){return s.retired[a]<s.retired[b];});for(std::size_t i=0;i<s.retired.size();++i)number(s.retired[indices[i]].value());
    number(s.matches.size());sorted(s.matches.size(),[&](auto a,auto b){return s.matches[a].number<s.matches[b].number;});
    for(std::size_t i=0;i<s.matches.size();++i){const auto& m=s.matches[indices[i]];number(m.number.value());number(m.locate.value());number(static_cast<unsigned>(m.kind));number(m.broken);}
    return gig::Result<Sha256Digest>::success(hash.finish());
}
gig::Result<SyntheticReconstructor> restart_seeded_prefix(ReconstructionConfig config,const SeedState& seed,Sha256Digest trusted_seed,std::span<const std::byte> bytes,Sha256Digest trusted_prefix,std::pmr::memory_resource* resource) noexcept {
    if(bytes.size()>128U*1024U*1024U||config.max_source_records==0||config.max_source_records>100000)
        return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::capacity,"seed_restart.budget");
    if(sha256(bytes)!=trusted_prefix)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::identity_mismatch,"seed_restart.prefix_digest");
    auto reconstruction=SyntheticReconstructor::create_seeded(config,seed,trusted_seed,resource);if(!reconstruction)return reconstruction;
    FramerLimits limits;limits.max_records=config.max_source_records;limits.max_stream_bytes=128U*1024U*1024U;
    auto reader=BinaryFileFramer::create(limits,seed.boundary.frame_offset,seed.boundary.ordinal,resource);
    if(!reader)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::resource_exhausted,"seed_restart.framer");
    while(!bytes.empty()){
        const auto frame=reader.data->feed(bytes);
        if(frame.error||!frame.consumed)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::malformed,"seed_restart.framing");
        bytes=bytes.subspan(frame.consumed);
        if(frame.frame){const auto step=reconstruction.data->process(frame.frame->payload,frame.frame->location,config.source.provenance);
            if(!step.committed)return gig::Result<SyntheticReconstructor>::failure(step.native_error?step.native_error.code:gig::ErrorCode::malformed,"seed_restart.transition");}
    }
    const auto end=reader.data->finish(EndKind::bounded_prefix);
    if(end.error||end.residual_bytes)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::malformed,"seed_restart.incomplete_frame");
    return reconstruction;
}
} // namespace gig::itch
