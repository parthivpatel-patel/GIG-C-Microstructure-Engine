#include "gig/itch/restart.hpp"
#include "gig/itch/binary_file.hpp"
#include <algorithm>

namespace gig::itch {
namespace {
bool digest_valid(gig::Digest value) noexcept {
    const auto text=value.view();return text.size()==64&&std::all_of(text.begin(),text.end(),[](char c){return (c>='0'&&c<='9')||(c>='a'&&c<='f');});
}
bool active_prefix(const SyntheticReconstructor& r) noexcept {
    const auto& s=r.summary();
    return s.initialization_verified&&!s.pending&&!s.rejected&&!s.unconsidered_record&&!s.finished&&!s.input_complete
        &&s.eligibility==ReconstructionEligibility::eligible_synthetic_empty&&!r.context().summary().finished;
}
gig::Error framing_error(const Error& error) noexcept {
    return {error.code==Code::resource_exhausted?gig::ErrorCode::resource_exhausted:
        error.code==Code::record_limit||error.code==Code::stream_limit?gig::ErrorCode::capacity:gig::ErrorCode::malformed,"restart.framing"};
}
gig::Result<SyntheticReconstructor> replay_prefix(const ReconstructionConfig& config,std::span<const std::byte> bytes,
    Provenance provenance,bool& terminal,std::pmr::memory_resource* resource) noexcept {
    // Validate limits before multiplying. These are the reconstruction factory's
    // declared hard bounds, not a promise that a maximum-sized profile fits memory.
    if(config.max_source_records==0||config.max_source_records>100000)
        return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::capacity,"restart.source_limit");
    const auto maximum=static_cast<std::uint64_t>(config.max_source_records)*65537U+2U;
    if(bytes.size()>maximum)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::capacity,"restart.prefix_bytes");
    auto reconstruction=SyntheticReconstructor::create(config,resource);if(!reconstruction)return reconstruction;
    FramerLimits limits;limits.max_records=config.max_source_records;limits.max_stream_bytes=maximum;
    auto reader=BinaryFileFramer::create(limits,ByteOffset{0},RecordOrdinal{0},resource);
    if(!reader)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::resource_exhausted,"restart.framer_storage");
    auto remaining=bytes;
    while(!remaining.empty()){
        const auto framed=reader.data->feed(remaining);
        if(framed.error){const auto error=framing_error(framed.error);return gig::Result<SyntheticReconstructor>::failure(error.code,error.field);}
        remaining=remaining.subspan(framed.consumed);
        if(framed.frame){
            const auto result=reconstruction.data->process(framed.frame->payload,framed.frame->location,provenance);
            if(!result.committed){
                if(result.native_error)return gig::Result<SyntheticReconstructor>::failure(result.native_error.code,result.native_error.field);
                return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::malformed,"restart.source_context");
            }
        }
        if(framed.consumed==0)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::inconsistent_state,"restart.no_progress");
    }
    const auto end=reader.data->finish(EndKind::bounded_prefix);
    if(end.error){const auto error=framing_error(end.error);return gig::Result<SyntheticReconstructor>::failure(error.code,error.field);}
    if(end.residual_bytes!=0)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::malformed,"restart.partial_frame");
    terminal=reader.data->terminated();return reconstruction;
}
gig::Result<ReconstructionCheckpoint> describe(const SyntheticReconstructor& r,std::span<const std::byte> bytes,
    gig::Digest implementation,Provenance provenance,bool terminal) noexcept {
    ReconstructionCheckpoint out{1,r.config(),implementation,r.summary(),r.context().summary(),static_cast<std::uint64_t>(bytes.size()),sha256(bytes),provenance,{},terminal};
    for(std::size_t i=0;i<r.config().book_count;++i){
        const auto* engine=r.engine(i);
        if(!engine)return gig::Result<ReconstructionCheckpoint>::failure(gig::ErrorCode::inconsistent_state,"restart.engine");
        const auto canonical=engine->canonical();if(!canonical)return gig::Result<ReconstructionCheckpoint>::failure(canonical.error.code,canonical.error.field);
        const auto text=std::string_view(*canonical.data);
        const auto digest=sha256(std::as_bytes(std::span{text.data(),text.size()}));
        const auto& book=engine->book();
        out.books[i]=BookCheckpoint{book.revision(),book.remaining(),engine->journal_size(),book.order_count(),book.ledger(),digest,engine->needs_recovery()};
    }
    return gig::Result<ReconstructionCheckpoint>::success(std::move(out));
}
template<class T> bool same_span(std::span<const T> a,std::span<const T> b) noexcept {
    return a.size()==b.size()&&std::equal(a.begin(),a.end(),b.begin());
}
bool same_context_and_receipts(const SyntheticReconstructor& a,const SyntheticReconstructor& b) noexcept {
    if(a.context().summary()!=b.context().summary()||!same_span(a.context().directories(),b.context().directories())
        ||!same_span(a.context().orders(),b.context().orders())||!same_span(a.context().matches(),b.context().matches()))return false;
    const auto x=a.receipts(),y=b.receipts();if(x.size()!=y.size())return false;
    for(std::size_t i=0;i<x.size();++i)if(x[i].source!=y[i].source||x[i].disposition!=y[i].disposition
        ||x[i].book_index!=y[i].book_index||x[i].native_sequence!=y[i].native_sequence)return false;
    return true;
}
}
gig::Result<ReconstructionCheckpoint> capture_checkpoint(const SyntheticReconstructor& original,std::span<const std::byte> bytes,
    gig::Digest implementation,std::pmr::memory_resource* resource) noexcept {
    if(!digest_valid(implementation))return gig::Result<ReconstructionCheckpoint>::failure(gig::ErrorCode::malformed,"restart.implementation_sha256");
    if(!active_prefix(original))return gig::Result<ReconstructionCheckpoint>::failure(gig::ErrorCode::inconsistent_state,"restart.not_active_prefix");
    const auto records=original.receipts();const auto provenance=records.empty()?Provenance{}:records.front().source.provenance;
    for(const auto& record:records)if(record.source.provenance!=provenance)
        return gig::Result<ReconstructionCheckpoint>::failure(gig::ErrorCode::unsupported,"restart.nonuniform_provenance");
    bool terminal=false;auto rebuilt=replay_prefix(original.config(),bytes,provenance,terminal,resource);
    if(!rebuilt)return gig::Result<ReconstructionCheckpoint>::failure(rebuilt.error.code,rebuilt.error.field);
    if(!same_context_and_receipts(original,*rebuilt.data))return gig::Result<ReconstructionCheckpoint>::failure(gig::ErrorCode::identity_mismatch,"restart.context_or_receipts");
    auto expected=describe(original,bytes,implementation,provenance,terminal);if(!expected)return expected;
    auto actual=describe(*rebuilt.data,bytes,implementation,provenance,terminal);if(!actual)return actual;
    if(*expected.data!=*actual.data)return gig::Result<ReconstructionCheckpoint>::failure(gig::ErrorCode::identity_mismatch,"restart.state");
    return expected;
}
gig::Result<SyntheticReconstructor> restart_from_checkpoint(const ReconstructionCheckpoint& checkpoint,const ReconstructionConfig& expected,
    std::span<const std::byte> bytes,gig::Digest implementation,std::pmr::memory_resource* resource) noexcept {
    if(checkpoint.format_version!=1||checkpoint.config!=expected||checkpoint.implementation_sha256!=implementation||!digest_valid(implementation))
        return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::identity_mismatch,"restart.contract");
    if(expected.max_source_records==0||expected.max_source_records>100000
        ||bytes.size()>static_cast<std::uint64_t>(expected.max_source_records)*65537U+2U)
        return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::capacity,"restart.prefix_bytes");
    if(checkpoint.prefix_bytes!=bytes.size()||checkpoint.prefix_sha256!=sha256(bytes))
        return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::identity_mismatch,"restart.prefix_identity");
    bool terminal=false;auto rebuilt=replay_prefix(expected,bytes,checkpoint.record_provenance,terminal,resource);if(!rebuilt)return rebuilt;
    auto actual=describe(*rebuilt.data,bytes,implementation,checkpoint.record_provenance,terminal);
    if(!actual)return gig::Result<SyntheticReconstructor>::failure(actual.error.code,actual.error.field);
    if(*actual.data!=checkpoint)return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::identity_mismatch,"restart.descriptor");
    return rebuilt;
}
} // namespace gig::itch
