#include "gig/itch/source_recovery.hpp"
namespace gig::itch {
gig::Result<SyntheticReconstructor> resume_hot_source(std::span<const std::byte> bytes,const DurableAdmission&trusted,std::span<const std::byte> source,const SourceRecoveryAdmission&a,std::pmr::memory_resource*r)noexcept {
 using R=gig::Result<SyntheticReconstructor>;
 const auto bad=[](gig::ErrorCode c,std::string_view f){return R::failure(c,f);};
 if(!r||source.size()>32U*1024U*1024U||a.gzip.max_decompressed_bytes>32U*1024U*1024U||a.gzip.max_compressed_bytes>32U*1024U*1024U||a.framing.max_records>4096||a.framing.max_stream_bytes>32U*1024U*1024U)return bad(gig::ErrorCode::capacity,"source_recovery.budget");
 if(a.capture!=trusted.capture||a.generation!=trusted.generation||sha256(source)!=a.source_sha256)return bad(gig::ErrorCode::identity_mismatch,"source_recovery.capture_generation_digest");
 if(a.container!=RecoveryContainer::binary_file&&a.container!=RecoveryContainer::single_gzip)return bad(gig::ErrorCode::unsupported,"source_recovery.container");
 auto candidate=restore_durable_checkpoint(bytes,trusted,r);if(!candidate)return candidate;auto&engine=*candidate.data;
 if(a.first_location!=engine.config().context_policy.first_location||a.first_location.frame_offset.value()>UINT64_MAX-2||a.first_location.payload_offset.value()!=a.first_location.frame_offset.value()+2)return bad(gig::ErrorCode::identity_mismatch,"source_recovery.boundary");
 auto framer=BinaryFileFramer::create(a.framing,a.first_location.frame_offset,a.first_location.ordinal,r);if(!framer)return bad(gig::ErrorCode::resource_exhausted,"source_recovery.framer");
 const auto prefix_count=engine.receipts().size();std::size_t seen=0;gig::Error error{};
 const auto consume=[&](std::span<const std::byte>b){
  while(!b.empty()&&!error){auto frame=framer.data->feed(b);if(frame.error||!frame.consumed){error={gig::ErrorCode::malformed,"source_recovery.framing"};break;}b=b.subspan(frame.consumed);
   if(frame.status==FrameStatus::terminal){error={gig::ErrorCode::unsupported,"source_recovery.terminal_position"};break;}
   if(frame.frame){if(seen<prefix_count){const auto&receipt=engine.receipts()[seen];auto decoded=decode(frame.frame->payload,frame.frame->location,receipt.source.provenance,engine.config().context_policy.decode_profile);
     if(!decoded||*decoded.data!=receipt.source){error={gig::ErrorCode::identity_mismatch,"source_recovery.committed_prefix"};break;}}
    else {auto step=engine.process(frame.frame->payload,frame.frame->location,engine.config().source.provenance);if(!step.committed){error=step.native_error?step.native_error:gig::Error{gig::ErrorCode::recovery_required,"source_recovery.continuation"};break;}}
    ++seen;
   }
  }
 };
 if(a.container==RecoveryContainer::binary_file)consume(source);
 else {
  auto gzip=GzipReader::create(a.gzip,r);if(!gzip)return bad(gzip.error.code,gzip.error.field);
  while(!source.empty()&&!error){auto feed=gzip.data->feed(source);source=source.subspan(feed.consumed);if(feed.error)return bad(gig::ErrorCode::malformed,"source_recovery.gzip_integrity");consume(feed.output);if(!feed.consumed&&feed.output.empty())return bad(gig::ErrorCode::malformed,"source_recovery.gzip_progress");}
  if(!error){for(;;){auto feed=gzip.data->feed({});if(feed.error)return bad(gig::ErrorCode::malformed,"source_recovery.gzip_integrity");consume(feed.output);if(error||feed.output.empty())break;}
   if(!error){auto finish=gzip.data->finish(EndKind::source_eof);if(finish.error||!finish.member_verified||!finish.complete)return bad(gig::ErrorCode::malformed,"source_recovery.gzip_truncated");}}
 }
 if(error)return bad(error.code,error.field);
 const auto finish=framer.data->finish(EndKind::bounded_prefix);
 if(finish.error||finish.residual_bytes||seen<prefix_count)return bad(gig::ErrorCode::malformed,"source_recovery.incomplete_prefix");
 return candidate;
}
}
