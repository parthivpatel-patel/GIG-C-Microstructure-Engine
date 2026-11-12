#include "wire.hpp"
#include "gig/itch/durable_checkpoint.hpp"
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
class ItchRecovery {
 TrackedResource memory_;
 itch::DurableAdmission admission_;
 itch::SyntheticReconstructor engine_;
public:
 ItchRecovery(std::span<const std::byte>b,itch::DurableAdmission a,std::size_t budget):memory_(std::pmr::get_default_resource(),budget),admission_(a),engine_(take(itch::restore_durable_checkpoint(b,a,&memory_))){}
 py::dict status(){return api([&](){auto context=engine_.context().checkpoint(&memory_);if(!context)bad(ErrorCode::inconsistent_state,"itch.context_capture");py::dict out;const auto&s=engine_.summary();out["source_records"]=write(s.context_committed);out["native_records"]=write(s.native_committed);out["external_records"]=write(s.external_observations);out["next_frame"]=write(context.data->next_location.frame_offset.value());out["next_ordinal"]=write(context.data->next_location.ordinal.value());out["generation"]=write(admission_.generation);out["capture"]=py::str(admission_.capture.view());out["pmr_live_bytes"]=write(memory_.stats().live_bytes);out["pmr_peak_bytes"]=write(memory_.stats().peak_bytes);return out;});}
 py::dict canonical(){return api([&](){py::list out;for(std::size_t n=0;n<engine_.config().book_count;++n){auto c=take(engine_.engine(n)->canonical());out.append(py::str(c.data(),c.size()));}return out;});}
 py::dict checkpoint(){return api([&]()->py::object{auto state=take(engine_.hot_checkpoint(&memory_));auto b=take(itch::encode_hot_checkpoint(state,admission_.capture,admission_.generation,admission_.implementation_sha256,&memory_));return py::bytes(reinterpret_cast<const char*>(b.data()),b.size());});}
 py::dict describe(){return api([&](){const auto&c=engine_.config();py::dict out;out["source"]=py::str(c.source.source.view());out["session"]=py::str(c.source.session.view());out["run_id"]=py::str(c.run_id.view());out["seeded"]=c.seed_sha256.has_value();out["fixture_sha256"]=py::str(c.initialization.fixture_sha256.view());out["generator_seed"]=write(c.initialization.seed);out["source_price_quantum"]=write(c.context_policy.price_quantum);out["source_lot_size"]=write(c.context_policy.lot_size);out["initial_frame"]=write(c.context_policy.first_location.frame_offset.value());out["initial_ordinal"]=write(c.context_policy.first_location.ordinal.value());py::list books;for(std::size_t n=0;n<c.book_count;++n){const auto&b=*c.bindings[n];py::dict row;row["index"]=write(n);row["stock"]=py::str(b.stock.view());row["locate"]=write(b.locate.value());row["rules"]=write(b.rules);row["limits"]=write(b.limits);books.append(row);}out["books"]=books;return out;});}
 py::dict book(py::handle index,py::handle depth){return api([&](){auto n=read<std::size_t>(index);if(n>=engine_.config().book_count)bad(ErrorCode::invalid_range,"itch.book_index");auto d=read<std::size_t>(depth);auto native=engine_.engine(n);py::dict out;out["snapshot"]=snapshot_wire(take(native->depth(d)));out["metrics"]=book_metrics_wire(take(analytics::calculate(take(native->depth(d)),d)));out["journal_size"]=write(native->journal_size());return out;});}
 py::dict rebind(py::handle target){return api([&]()->py::object{const auto code=read<Digest>(target);auto state=take(engine_.hot_checkpoint(&memory_));auto b=take(itch::encode_hot_checkpoint(state,admission_.capture,admission_.generation,code,&memory_));return py::bytes(reinterpret_cast<const char*>(b.data()),b.size());});}
 py::dict process(py::handle payload,py::handle offset,py::handle ordinal){return api([&](){auto b=blob(payload,65535);auto frame=read<std::uint64_t>(offset);if(frame>UINT64_MAX-2)bad(ErrorCode::overflow,"itch.source_position");auto step=engine_.process(b,{itch::ByteOffset{frame},itch::ByteOffset{frame+2},itch::RecordOrdinal{read<std::uint64_t>(ordinal)}});py::dict out;out["committed"]=step.committed;out["disposition"]=write(static_cast<unsigned>(step.disposition));out["context_code"]=write(static_cast<unsigned>(step.context_error.code));out["native_code"]=write(static_cast<unsigned>(step.native_error.code));return out;});}
};
}
void bind_itch_recovery(py::module_&m){
 py::class_<ItchRecovery>(m,"_ItchRecovery").def("describe",&ItchRecovery::describe).def("book",&ItchRecovery::book).def("rebind",&ItchRecovery::rebind).def("status",&ItchRecovery::status).def("canonical",&ItchRecovery::canonical).def("checkpoint",&ItchRecovery::checkpoint).def("process",&ItchRecovery::process);
 m.def("restore_itch_checkpoint",[](py::handle bytes,py::handle artifact,py::handle contract,py::handle code,py::handle capture,py::handle generation,py::handle budget){return api([&](){auto n=read<std::size_t>(budget);if(n==0||n>256U*1024U*1024U)bad(ErrorCode::capacity,"itch.resource_budget");itch::DurableAdmission a{digest(artifact),digest(contract),read<Digest>(code),capture_id(capture),read<std::uint64_t>(generation)};return py::cast(std::make_unique<ItchRecovery>(blob(bytes,itch::durable_max_bytes),a,n));});});
}
}
