#include "gig/itch/streaming.hpp"
#include <algorithm>
#include <cassert>

namespace gig::itch {
namespace {
struct Guard {bool& busy;explicit Guard(bool& b)noexcept:busy(b){busy=true;}~Guard(){busy=false;}};
bool valid_digest(gig::Digest digest) noexcept {
    const auto value=digest.view();return value.size()==64&&std::all_of(value.begin(),value.end(),[](char c){return (c>='0'&&c<='9')||(c>='a'&&c<='f');});
}
}
StreamingReconstructor::StreamingReconstructor(StreamingConfig config,GzipReader gzip,BinaryFileFramer framer,SyntheticReconstructor reconstruction) noexcept
:config_(std::move(config)),gzip_(std::move(gzip)),framer_(std::move(framer)),reconstruction_(std::move(reconstruction)) {}
StreamingReconstructor::StreamingReconstructor(StreamingReconstructor&& other) noexcept
:config_(std::move(other.config_)),gzip_(std::move(other.gzip_)),framer_(std::move(other.framer_)),reconstruction_(std::move(other.reconstruction_)),
 compressed_hash_(other.compressed_hash_),decompressed_hash_(other.decompressed_hash_),accepted_hash_(other.accepted_hash_),accepted_bytes_(other.accepted_bytes_),
 pending_output_(other.pending_output_),pause_after_(other.pause_after_),paused_(other.paused_),finished_(other.finished_),moved_from_(other.moved_from_),error_(other.error_),deferred_gzip_error_(other.deferred_gzip_error_),final_(other.final_) {other.moved_from_=true;other.pending_output_={};}
gig::Result<StreamingReconstructor> StreamingReconstructor::create(StreamingConfig config,std::pmr::memory_resource* resource) noexcept {
    if(!resource||config.gzip.max_compressed_bytes>UINT64_MAX/8||config.gzip.max_decompressed_bytes>UINT64_MAX/8)
        return gig::Result<StreamingReconstructor>::failure(gig::ErrorCode::invalid_range,"streaming.hash_limits");
    auto gzip=GzipReader::create(config.gzip,resource);if(!gzip)return gig::Result<StreamingReconstructor>::failure(gzip.error.code,gzip.error.field);
    auto framer=BinaryFileFramer::create(config.framing,ByteOffset{0},RecordOrdinal{0},resource);
    if(!framer)return gig::Result<StreamingReconstructor>::failure(framer.error.code==Code::resource_exhausted?gig::ErrorCode::resource_exhausted:gig::ErrorCode::invalid_range,"streaming.framer");
    auto reconstruction=SyntheticReconstructor::create(config.reconstruction,resource);
    if(!reconstruction)return gig::Result<StreamingReconstructor>::failure(reconstruction.error.code,reconstruction.error.field);
    return gig::Result<StreamingReconstructor>::success(StreamingReconstructor(std::move(config),std::move(*gzip.data),std::move(*framer.data),std::move(*reconstruction.data)));
}
void StreamingReconstructor::consume_output() noexcept {
    while(!pending_output_.empty()&&!paused_&&!error_){
        const auto framed=framer_.feed(pending_output_);pending_output_=pending_output_.subspan(framed.consumed);
        if(framed.error){error_.code=StreamingCode::framing;error_.framing=framed.error;break;}
        if(framed.frame){
            const auto step=reconstruction_.process(framed.frame->payload,framed.frame->location,config_.reconstruction.source.provenance);
            if(!step.committed){error_.code=StreamingCode::reconstruction;error_.reconstruction=step;break;}
            // At most100000 admitted frames, each<=65535 bytes. These fixed-size
            // nonallocating hash updates cannot reach SHA256's length boundary.
            const auto size=framed.frame->payload.size();const std::array<std::byte,2> length{static_cast<std::byte>(size>>8U),static_cast<std::byte>(size&255U)};
            const bool a=accepted_hash_.update(length),b=accepted_hash_.update(framed.frame->payload);assert(a&&b);(void)a;(void)b;
            accepted_bytes_+=size+2;
            if(pause_after_&&reconstruction_.summary().context_committed==*pause_after_)paused_=true;
        }
        if(framed.consumed==0&&!framed.frame){error_.code=StreamingCode::framing;error_.framing={Code::invalid_value,framer_.position(),"streaming.no_progress",0,0};break;}
    }
}
StreamingFeed StreamingReconstructor::feed_impl(std::span<const std::byte> input) noexcept {
    std::size_t consumed=0;
    consume_output();
    if(!paused_&&deferred_gzip_error_){
        if(!error_)error_.code=StreamingCode::gzip;
        error_.gzip=deferred_gzip_error_;
    }
    while(!paused_&&!error_){
        const auto next=gzip_.feed(input.subspan(consumed));
        const bool hash_ok=compressed_hash_.update(input.subspan(consumed,next.consumed));assert(hash_ok);(void)hash_ok;consumed+=next.consumed;
        if(!next.output.empty()){
            const bool output_hash_ok=decompressed_hash_.update(next.output);assert(output_hash_ok);(void)output_hash_ok;
            pending_output_=next.output;consume_output();
        }
        // Output before an error is a provisional decoded prefix. Never certify
        // source integrity, even if every frame happened to be reconstructed.
        if(next.error){
            if(paused_&&!error_)deferred_gzip_error_=next.error;
            else {if(!error_)error_.code=StreamingCode::gzip;error_.gzip=next.error;}
        }
        if(paused_||error_||(next.consumed==0&&next.output.empty()))break;
        // Continue with empty input to drain cached inflater output/trailer state.
    }
    return {consumed,paused_,error_};
}
StreamingFeed StreamingReconstructor::feed(std::span<const std::byte> input) noexcept {
    if(busy_)return {0,paused_,{StreamingCode::reentrant,{},{},{}}};
    if(moved_from_)return {0,false,{StreamingCode::moved_from,{},{},{}}};
    if(finished_)return {0,paused_,{StreamingCode::already_finished,{},{},{}}};
    if(error_)return {0,paused_,error_};
    Guard guard(busy_);return feed_impl(input);
}
StreamingSummary StreamingReconstructor::summary()const noexcept {
    if(final_)return *final_;
    StreamingSummary out;
    out.compressed_bytes=gzip_.compressed_bytes();out.decompressed_bytes=gzip_.decompressed_bytes();out.framing_bytes=framer_.position().value();out.accepted_prefix_bytes=accepted_bytes_;
    out.source_records=framer_.records();out.accepted_records=reconstruction_.summary().context_committed;out.native_records=reconstruction_.summary().native_committed;out.external_observations=reconstruction_.summary().external_observations;
    out.compressed_sha256=compressed_hash_.finish();out.decompressed_sha256=decompressed_hash_.finish();out.accepted_prefix_sha256=accepted_hash_.finish();
    out.gzip_member_verified=gzip_.member_verified();out.framer_terminated=framer_.terminated();
    out.compressed_identity_verified=out.gzip_member_verified&&out.compressed_sha256==config_.compressed_sha256;
    out.decompressed_identity_verified=out.gzip_member_verified&&config_.reconstruction.source.provenance.sha256&&out.decompressed_sha256==*config_.reconstruction.source.provenance.sha256;
    out.residual_frame_bytes=framer_.residual_bytes();
    out.paused=paused_;out.finished=finished_;out.buffered_output_bytes=pending_output_.size();out.error=error_;out.observed_gzip_error=gzip_.error();
    // Before finish EOF is unavailable. Matched hashes/CRC are individual facts,
    // never a claim that an unseen extra member or trailing bytes do not exist.
    return out;
}
StreamingSummary StreamingReconstructor::finish(EndKind kind) noexcept {
    if(busy_)return summary();
    if(moved_from_){auto result=summary();result.error.code=StreamingCode::moved_from;return result;}
    if(final_)return *final_;
    if(kind!=EndKind::source_eof&&kind!=EndKind::bounded_prefix){auto result=summary();result.error.code=StreamingCode::framing;result.error.framing.code=Code::invalid_config;return result;}
    Guard guard(busy_);
    if(!paused_&&!error_)(void)feed_impl({});
    const auto gzip_end=gzip_.finish((paused_||error_)?EndKind::bounded_prefix:kind);
    if(gzip_end.error&&!(paused_&&deferred_gzip_error_)){if(!error_)error_.code=StreamingCode::gzip;error_.gzip=gzip_end.error;}
    const auto frame_end=framer_.finish(paused_||error_?EndKind::bounded_prefix:kind);
    if(frame_end.error&&!error_){error_.code=StreamingCode::framing;error_.framing=frame_end.error;}
    auto result=summary();
    result.source_complete=!paused_&&!error_&&kind==EndKind::source_eof&&gzip_end.complete&&frame_end.session_complete;
    if(result.source_complete&&(!result.compressed_identity_verified||!result.decompressed_identity_verified)){
        error_.code=StreamingCode::identity_mismatch;result.source_complete=false;
    }
    result.publication_eligible=result.source_complete&&!error_;
    result.bounded_prefix=kind==EndKind::bounded_prefix||paused_;result.residual_frame_bytes=frame_end.residual_bytes;
    (void)reconstruction_.finish(result.source_complete?ContextEnd::declared_source_complete:(kind==EndKind::bounded_prefix||paused_)?ContextEnd::bounded_prefix:ContextEnd::unexpected_eof);
    finished_=true;result.finished=true;result.error=error_;final_=result;return result;
}
gig::Error StreamingReconstructor::pause_after(std::uint64_t records) noexcept {
    if(busy_||moved_from_||finished_||error_)return {gig::ErrorCode::inconsistent_state,"streaming.pause_state"};
    if(records<reconstruction_.summary().context_committed||records>config_.reconstruction.max_source_records)return {gig::ErrorCode::invalid_range,"streaming.pause_boundary"};
    pause_after_=records;paused_=records==reconstruction_.summary().context_committed;return {};
}
gig::Error StreamingReconstructor::resume() noexcept {
    if(busy_||moved_from_||finished_||error_)return {gig::ErrorCode::inconsistent_state,"streaming.resume_state"};
    pause_after_.reset();paused_=false;return {};
}
gig::Result<StreamingCheckpoint> StreamingReconstructor::checkpoint(gig::Digest code)const noexcept {
    if(busy_||moved_from_||finished_||error_||reconstruction_.summary().pending||reconstruction_.summary().rejected||reconstruction_.summary().unconsidered_record)
        return gig::Result<StreamingCheckpoint>::failure(gig::ErrorCode::inconsistent_state,"streaming.checkpoint_state");
    if(!valid_digest(code))return gig::Result<StreamingCheckpoint>::failure(gig::ErrorCode::malformed,"streaming.code_identity");
    Guard guard(busy_);
    StreamingCheckpoint out{1,config_,code,reconstruction_.summary(),reconstruction_.context().summary(),accepted_bytes_,accepted_hash_.finish(),{}};
    for(std::size_t i=0;i<config_.reconstruction.book_count;++i){
        const auto* engine=reconstruction_.engine(i);const auto canonical=engine->canonical();
        if(!canonical)return gig::Result<StreamingCheckpoint>::failure(canonical.error.code,canonical.error.field);
        const auto text=std::string_view(*canonical.data);const auto& book=engine->book();
        out.books[i]=BookCheckpoint{book.revision(),book.remaining(),engine->journal_size(),book.order_count(),book.ledger(),sha256(std::as_bytes(std::span{text.data(),text.size()})),engine->needs_recovery()};
    }
    return gig::Result<StreamingCheckpoint>::success(std::move(out));
}
gig::Error StreamingReconstructor::verify_checkpoint(const StreamingCheckpoint& expected,gig::Digest code)const noexcept {
    if(expected.version!=1||expected.config!=config_||expected.implementation_sha256!=code)return {gig::ErrorCode::identity_mismatch,"streaming.checkpoint_contract"};
    auto actual=checkpoint(code);if(!actual)return actual.error;
    if(*actual.data!=expected)return {gig::ErrorCode::identity_mismatch,"streaming.checkpoint_prefix"};
    return {};
}
} // namespace gig::itch
