#include "wire.hpp"
#include "gig/itch/durable_checkpoint.hpp"
#include "gig/itch/source_recovery.hpp"
#include "gig/itch/completion_capsule.hpp"
#include "gig/memory/tracked_resource.hpp"
namespace gig::python {
namespace {
std::span<const std::byte> blob(py::handle h,std::size_t limit){
 if(!PyBytes_CheckExact(h.ptr()))bad(ErrorCode::malformed,"itch.bytes_required");
 const auto n=PyBytes_GET_SIZE(h.ptr());if(n<0||static_cast<std::size_t>(n)>limit)bad(ErrorCode::capacity,"itch.byte_budget");
 return {reinterpret_cast<const std::byte*>(PyBytes_AS_STRING(h.ptr())),static_cast<std::size_t>(n)};
}
itch::Sha256Digest digest(py::handle h){auto s=text(h,64);if(s.size()!=64)bad(ErrorCode::malformed,"itch.digest");itch::Sha256Digest out{};
 const auto nibble=[](char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;};
 for(std::size_t n=0;n<32;++n){auto a=nibble(s[n*2]),b=nibble(s[n*2+1]);if(a<0||b<0)bad(ErrorCode::malformed,"itch.digest");out[n]=static_cast<std::byte>(a*16+b);}return out;
}
itch::SourceIdentity capture_id(py::handle h){auto v=itch::SourceIdentity::make(text(h,128));if(!v)bad(ErrorCode::malformed,"itch.capture_identity");return *v.data;}
#ifdef GIG_PYTHON_ITCH_SOURCE_RECOVERY
itch::SyntheticReconstructor partial_source_owner(std::span<const std::byte> checkpoint,
    const itch::DurableAdmission& admission,std::span<const std::byte> source,
    const itch::SourceRecoveryAdmission& spec,itch::PartialBinaryTail& tail,TrackedResource& memory){
 auto result=take(itch::resume_partial_binary_source(checkpoint,admission,source,spec,&memory));
 tail=result.tail;
 return std::move(result.owner);
}
itch::SyntheticReconstructor partial_source_owner(std::span<const std::byte> checkpoint,
    const itch::DurableAdmission& admission,std::span<const std::byte> source,
    const itch::SourceRecoveryAdmission& spec,itch::PartialGzipTail& tail,TrackedResource& memory){
 auto result=take(itch::resume_partial_gzip_source(checkpoint,admission,source,spec,&memory));
 tail=result.tail;
 return std::move(result.owner);
}
#endif
class ItchRecovery {
 TrackedResource memory_;
 itch::DurableAdmission admission_;
 itch::SyntheticReconstructor engine_;
#ifdef GIG_PYTHON_ITCH_SOURCE_RECOVERY
 struct PendingTail {itch::Location next;std::size_t bytes;itch::Sha256Digest digest;};
 std::optional<PendingTail> pending_tail_;
#endif
public:
 ItchRecovery(std::span<const std::byte>b,itch::DurableAdmission a,std::size_t budget):memory_(std::pmr::get_default_resource(),budget),admission_(a),engine_(take(itch::restore_durable_checkpoint(b,a,&memory_))){}
#ifdef GIG_PYTHON_ITCH_SOURCE_RECOVERY
 ItchRecovery(std::span<const std::byte>b,itch::DurableAdmission a,std::size_t budget,std::span<const std::byte>s,const itch::SourceRecoveryAdmission&source,bool complete=false):memory_(std::pmr::get_default_resource(),budget),admission_(a),engine_(take(complete?itch::resume_complete_source(b,a,s,source,&memory_):itch::resume_hot_source(b,a,s,source,&memory_))){}
 template<class Tail>
 ItchRecovery(std::span<const std::byte>b,itch::DurableAdmission admission,std::size_t budget,
              std::span<const std::byte> source,const itch::SourceRecoveryAdmission& spec,
              Tail& tail)
 :memory_(std::pmr::get_default_resource(),budget),admission_(admission),
  engine_(partial_source_owner(b,admission,source,spec,tail,memory_)),
  pending_tail_(PendingTail{tail.next_location,tail.residual_bytes,tail.residual_sha256}) {}
#endif
#ifdef GIG_PYTHON_ITCH_SOURCE_RECOVERY
 ItchRecovery(std::span<const std::byte>b,const itch::CompletionCapsuleAdmission&a,std::size_t budget):memory_(std::pmr::get_default_resource(),budget),admission_(a.checkpoint),engine_(take(itch::restore_completion_capsule(b,a,&memory_))){}
#endif
 py::dict status(){return api([&](){
  const auto cursor=engine_.context().next_location();
  const auto& summary=engine_.summary();
  const auto memory=memory_.stats();
  py::dict out;
  out["source_records"]=write(summary.context_committed);
  out["native_records"]=write(summary.native_committed);
  out["external_records"]=write(summary.external_observations);
  out["next_frame"]=write(cursor.frame_offset.value());
  out["next_ordinal"]=write(cursor.ordinal.value());
  out["generation"]=write(admission_.generation);
  out["capture"]=py::str(admission_.capture.view());
  out["pmr_live_bytes"]=write(memory.live_bytes);
  out["pmr_peak_bytes"]=write(memory.peak_bytes);
  return out;
 });}
 py::dict completion(){return api([&](){const auto&s=engine_.summary();const auto&c=engine_.context().summary();py::dict out;out["source_records"]=write(s.context_committed);out["native_records"]=write(s.native_committed);out["external_records"]=write(s.external_observations);out["finished"]=s.finished;out["input_complete"]=s.input_complete;out["session_incomplete"]=c.session_incomplete;return out;});}
 py::dict canonical(){return api([&](){py::list out;for(std::size_t n=0;n<engine_.config().book_count;++n){auto c=take(engine_.engine(n)->canonical());out.append(py::str(c.data(),c.size()));}return out;});}
 py::dict checkpoint(){return api([&]()->py::object{auto state=take(engine_.hot_checkpoint(&memory_));auto b=take(itch::encode_hot_checkpoint(state,admission_.capture,admission_.generation,admission_.implementation_sha256,&memory_));return py::bytes(reinterpret_cast<const char*>(b.data()),b.size());});}
 py::dict describe(){return api([&](){const auto&c=engine_.config();py::dict out;out["source"]=py::str(c.source.source.view());out["session"]=py::str(c.source.session.view());out["run_id"]=py::str(c.run_id.view());out["seeded"]=c.seed_sha256.has_value();out["fixture_sha256"]=py::str(c.initialization.fixture_sha256.view());out["generator_seed"]=write(c.initialization.seed);out["source_price_quantum"]=write(c.context_policy.price_quantum);out["source_lot_size"]=write(c.context_policy.lot_size);out["initial_frame"]=write(c.context_policy.first_location.frame_offset.value());out["initial_ordinal"]=write(c.context_policy.first_location.ordinal.value());py::list books;for(std::size_t n=0;n<c.book_count;++n){const auto&b=*c.bindings[n];py::dict row;row["index"]=write(n);row["stock"]=py::str(b.stock.view());row["locate"]=write(b.locate.value());row["rules"]=write(b.rules);row["limits"]=write(b.limits);books.append(row);}out["books"]=books;return out;});}
 py::dict book(py::handle index,py::handle depth){return api([&](){
  const auto book_index=read<std::size_t>(index);
  if(book_index>=engine_.config().book_count)bad(ErrorCode::invalid_range,"itch.book_index");
  const auto count=read<std::size_t>(depth);
  const auto* native=engine_.engine(book_index);
  const auto snapshot=take(native->depth(count));
  py::dict out;
  out["snapshot"]=snapshot_wire(snapshot);
  out["metrics"]=book_metrics_wire(take(analytics::calculate(snapshot,count)));
  out["journal_size"]=write(native->journal_size());
  return out;
 });}
 py::dict rebind(py::handle target){return api([&]()->py::object{const auto code=read<Digest>(target);auto state=take(engine_.hot_checkpoint(&memory_));auto b=take(itch::encode_hot_checkpoint(state,admission_.capture,admission_.generation,code,&memory_));return py::bytes(reinterpret_cast<const char*>(b.data()),b.size());});}
 py::dict process(py::handle payload,py::handle offset,py::handle ordinal){return api([&](){
  const auto bytes=blob(payload,65535);
  const auto frame=read<std::uint64_t>(offset);
  if(frame>UINT64_MAX-2)bad(ErrorCode::overflow,"itch.source_position");
  const itch::Location location{itch::ByteOffset{frame},itch::ByteOffset{frame+2},itch::RecordOrdinal{read<std::uint64_t>(ordinal)}};
#ifdef GIG_PYTHON_ITCH_SOURCE_RECOVERY
  if(pending_tail_&&(location!=pending_tail_->next||
     !itch::matches_partial_frame_prefix(bytes,pending_tail_->bytes,pending_tail_->digest)))
   bad(ErrorCode::identity_mismatch,"itch.partial_tail_identity");
#endif
  const auto step=engine_.process(bytes,location);
#ifdef GIG_PYTHON_ITCH_SOURCE_RECOVERY
  if(step.committed)pending_tail_.reset();
#endif
  py::dict out;
  out["committed"]=step.committed;
  out["disposition"]=write(static_cast<unsigned>(step.disposition));
  out["context_code"]=write(static_cast<unsigned>(step.context_error.code));
  out["native_code"]=write(static_cast<unsigned>(step.native_error.code));
  return out;
 });}
};
}
void bind_itch_recovery(py::module_&m){
 py::class_<ItchRecovery>(m,"_ItchRecovery").def("describe",&ItchRecovery::describe).def("book",&ItchRecovery::book).def("rebind",&ItchRecovery::rebind).def("status",&ItchRecovery::status).def("completion",&ItchRecovery::completion).def("canonical",&ItchRecovery::canonical).def("checkpoint",&ItchRecovery::checkpoint).def("process",&ItchRecovery::process);
 m.def("restore_itch_checkpoint",[](py::handle bytes,py::handle artifact,py::handle contract,py::handle code,py::handle capture,py::handle generation,py::handle budget){return api([&](){auto n=read<std::size_t>(budget);if(n==0||n>256U*1024U*1024U)bad(ErrorCode::capacity,"itch.resource_budget");itch::DurableAdmission a{digest(artifact),digest(contract),read<Digest>(code),capture_id(capture),read<std::uint64_t>(generation)};return py::cast(std::make_unique<ItchRecovery>(blob(bytes,itch::durable_max_bytes),a,n));});});
#ifdef GIG_PYTHON_ITCH_SOURCE_RECOVERY
 m.def("resume_itch_source",[](py::handle bytes,py::handle artifact,py::handle contract,py::handle code,py::handle capture,py::handle generation,py::handle budget,py::handle source,py::handle source_hash,py::handle container,py::handle frame,py::handle ordinal){return api([&](){
  auto n=read<std::size_t>(budget);if(n==0||n>256U*1024U*1024U)bad(ErrorCode::capacity,"itch.resource_budget");
  itch::DurableAdmission a{digest(artifact),digest(contract),read<Digest>(code),capture_id(capture),read<std::uint64_t>(generation)};
  const auto kind=read<unsigned>(container);if(kind>static_cast<unsigned>(itch::RecoveryContainer::gzip_members))bad(ErrorCode::unsupported,"itch.source_container");
  const auto offset=read<std::uint64_t>(frame);if(offset>UINT64_MAX-2)bad(ErrorCode::overflow,"itch.source_position");
  itch::SourceRecoveryAdmission s{static_cast<itch::RecoveryContainer>(kind),digest(source_hash),a.capture,a.generation,{itch::ByteOffset{offset},itch::ByteOffset{offset+2},itch::RecordOrdinal{read<std::uint64_t>(ordinal)}}};
  return py::cast(std::make_unique<ItchRecovery>(blob(bytes,itch::durable_max_bytes),a,n,blob(source,32U*1024U*1024U),s));
 });});
 const auto bind_partial=[&m]<class Tail>(const char* name,itch::RecoveryContainer container){
  m.def(name,[container](py::handle bytes,py::handle artifact,py::handle contract,
       py::handle code,py::handle capture,py::handle generation,py::handle budget,py::handle source,
       py::handle source_hash,py::handle frame,py::handle ordinal){return api([&](){
   const auto limit=read<std::size_t>(budget);
   if(limit==0||limit>256U*1024U*1024U)bad(ErrorCode::capacity,"itch.resource_budget");
   const itch::DurableAdmission admission{digest(artifact),digest(contract),read<Digest>(code),
       capture_id(capture),read<std::uint64_t>(generation)};
   const auto offset=read<std::uint64_t>(frame);
   if(offset>UINT64_MAX-2)bad(ErrorCode::overflow,"itch.source_position");
   const itch::SourceRecoveryAdmission spec{container,digest(source_hash),admission.capture,
       admission.generation,{itch::ByteOffset{offset},itch::ByteOffset{offset+2},
                              itch::RecordOrdinal{read<std::uint64_t>(ordinal)}}};
   Tail tail{};
   auto owner=std::make_unique<ItchRecovery>(blob(bytes,itch::durable_max_bytes),admission,limit,
       blob(source,32U*1024U*1024U),spec,tail);
   const auto hash=itch::hex_digest(tail.residual_sha256);
   py::dict receipt;
   if constexpr(std::is_same_v<Tail,itch::PartialBinaryTail>){
    receipt["source_offset"]=write(tail.source_offset);
   }else{
    receipt["decompressed_offset"]=write(tail.decompressed_offset);
    const auto decompressed=itch::hex_digest(tail.decompressed_sha256);
    receipt["decompressed_sha256"]=py::str(decompressed.data(),decompressed.size());
   }
   receipt["residual_bytes"]=write(tail.residual_bytes);
   receipt["next_frame"]=write(tail.next_location.frame_offset.value());
   receipt["next_ordinal"]=write(tail.next_location.ordinal.value());
   receipt["residual_sha256"]=py::str(hash.data(),hash.size());
   return py::make_tuple(py::cast(std::move(owner)),receipt);
  });});
 };
 bind_partial.operator()<itch::PartialBinaryTail>("resume_itch_partial_binary_source",itch::RecoveryContainer::binary_file);
 bind_partial.operator()<itch::PartialGzipTail>("resume_itch_partial_gzip_source",itch::RecoveryContainer::single_gzip);
 bind_partial.operator()<itch::PartialGzipTail>("resume_itch_partial_gzip_members",itch::RecoveryContainer::gzip_members);
 m.def("complete_itch_source",[](py::handle bytes,py::handle artifact,py::handle contract,py::handle code,py::handle capture,py::handle generation,py::handle budget,py::handle source,py::handle source_hash,py::handle container,py::handle frame,py::handle ordinal){return api([&](){
  auto n=read<std::size_t>(budget);if(n==0||n>256U*1024U*1024U)bad(ErrorCode::capacity,"itch.resource_budget");
  itch::DurableAdmission a{digest(artifact),digest(contract),read<Digest>(code),capture_id(capture),read<std::uint64_t>(generation)};
  const auto kind=read<unsigned>(container);if(kind>static_cast<unsigned>(itch::RecoveryContainer::gzip_members))bad(ErrorCode::unsupported,"itch.source_container");
  const auto offset=read<std::uint64_t>(frame);if(offset>UINT64_MAX-2)bad(ErrorCode::overflow,"itch.source_position");
  itch::SourceRecoveryAdmission s{static_cast<itch::RecoveryContainer>(kind),digest(source_hash),a.capture,a.generation,{itch::ByteOffset{offset},itch::ByteOffset{offset+2},itch::RecordOrdinal{read<std::uint64_t>(ordinal)}}};
  return py::cast(std::make_unique<ItchRecovery>(blob(bytes,itch::durable_max_bytes),a,n,blob(source,32U*1024U*1024U),s,true));
 });});
 m.def("encode_itch_completion_capsule",[](py::handle bytes,py::handle artifact,py::handle contract,py::handle code,py::handle capture,py::handle generation,py::handle budget,py::handle source,py::handle source_hash,py::handle container,py::handle frame,py::handle ordinal){return api([&](){
  const auto n=read<std::size_t>(budget);if(n==0||n>256U*1024U*1024U)bad(ErrorCode::capacity,"itch.resource_budget");
  itch::DurableAdmission a{digest(artifact),digest(contract),read<Digest>(code),capture_id(capture),read<std::uint64_t>(generation)};
  const auto kind=read<unsigned>(container);if(kind>static_cast<unsigned>(itch::RecoveryContainer::gzip_members))bad(ErrorCode::unsupported,"itch.source_container");const auto offset=read<std::uint64_t>(frame);if(offset>UINT64_MAX-2)bad(ErrorCode::overflow,"itch.source_position");
  itch::SourceRecoveryAdmission spec{static_cast<itch::RecoveryContainer>(kind),digest(source_hash),a.capture,a.generation,{itch::ByteOffset{offset},itch::ByteOffset{offset+2},itch::RecordOrdinal{read<std::uint64_t>(ordinal)}}};
  TrackedResource memory(std::pmr::get_default_resource(),n);const auto result=take(itch::encode_completion_capsule(blob(bytes,itch::durable_max_bytes),a,blob(source,32U*1024U*1024U),spec,&memory));
  return py::bytes(reinterpret_cast<const char*>(result.data()),result.size());
 });});
 m.def("restore_itch_completion_capsule",[](py::handle bytes,py::handle capsule_hash,py::handle artifact,py::handle contract,py::handle code,py::handle capture,py::handle generation,py::handle budget,py::handle source_hash,py::handle container,py::handle frame,py::handle ordinal){return api([&](){
  const auto n=read<std::size_t>(budget);if(n==0||n>256U*1024U*1024U)bad(ErrorCode::capacity,"itch.resource_budget");
  itch::DurableAdmission a{digest(artifact),digest(contract),read<Digest>(code),capture_id(capture),read<std::uint64_t>(generation)};
  const auto kind=read<unsigned>(container);if(kind>static_cast<unsigned>(itch::RecoveryContainer::gzip_members))bad(ErrorCode::unsupported,"itch.source_container");const auto offset=read<std::uint64_t>(frame);if(offset>UINT64_MAX-2)bad(ErrorCode::overflow,"itch.source_position");
  itch::SourceRecoveryAdmission spec{static_cast<itch::RecoveryContainer>(kind),digest(source_hash),a.capture,a.generation,{itch::ByteOffset{offset},itch::ByteOffset{offset+2},itch::RecordOrdinal{read<std::uint64_t>(ordinal)}}};
  return py::cast(std::make_unique<ItchRecovery>(blob(bytes,itch::completion_capsule_max_bytes),itch::CompletionCapsuleAdmission{digest(capsule_hash),a,spec},n));
 });});
#endif
}
}
