#include "gig/itch/completion_capsule.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_gzip_fixture.hpp"
#include "support/itch_seed_checks.hpp"
#include <iostream>
using namespace gig::itch;using namespace gig::itch::test;
namespace {
std::size_t checks=0;void expect(bool v,const char*s){++checks;check(v,s);}
void run(){
 const auto code=*gig::Digest::make(std::string(64,'b')).data;const auto capture=source_id("completed-capsule-authored");
 Harness h;const std::vector<std::vector<std::byte>> prefix{system(),directory(),directory(2,"TWO     "),add(),add(201,9,200,2)};for(const auto&b:prefix)h.accept(b);
 auto hot=h.reconstruction.hot_checkpoint();expect(bool(hot),"active original checkpoint");auto image=encode_hot_checkpoint(*hot.data,capture,7,code);expect(bool(image),"durable original encode");
 const DurableAdmission trusted{sha256(*image.data),hot_contract_sha256(h.reconstruction.config()),code,capture,7};auto records=prefix;records.push_back(reduce('E',101,2,71));const auto plain=framed_records(records,true);
 const auto before=state(h.reconstruction);for(bool gzip:{false,true}){
  auto source=gzip?stored_gzip(plain):plain;SourceRecoveryAdmission spec{gzip?RecoveryContainer::single_gzip:RecoveryContainer::binary_file,sha256(source),capture,7,{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}}};spec.gzip.output_buffer_bytes=1;
  auto capsule=encode_completion_capsule(*image.data,trusted,source,spec);expect(bool(capsule),"encode verified terminal capsule");CompletionCapsuleAdmission admission{sha256(*capsule.data),trusted,spec};
  auto restored=restore_completion_capsule(*capsule.data,admission);auto direct=resume_complete_source(*image.data,trusted,source,spec);expect(bool(restored)&&bool(direct),"capsule restore and direct completion");expect(state(*restored.data)==state(*direct.data)&&restored.data->summary()==direct.data->summary(),"deterministic finished replay");expect(restored.data->summary().finished&&restored.data->summary().input_complete,"finished capsule owner");expect(!restored.data->hot_checkpoint(),"finished state never relabeled active v1");
  auto limited=admission;
  if(gzip)limited.source.gzip.max_decompressed_bytes=1;
  else limited.source.framing.max_records=1;
  expect(restore_completion_capsule(*capsule.data,limited).error.code==gig::ErrorCode::capacity,
         "valid capsule restore preserves the configured source capacity failure");
  expect(encode_completion_capsule(*image.data,trusted,source,limited.source).error.code==gig::ErrorCode::capacity,
         "capsule encoding preserves the configured source capacity failure");
  auto repeated=encode_completion_capsule(*image.data,trusted,source,spec);expect(bool(repeated)&&*repeated.data==*capsule.data,"canonical capsule bytes");
  auto stale=admission;stale.checkpoint.generation=8;expect(!restore_completion_capsule(*capsule.data,stale),"stale checkpoint admission rejected");stale=admission;stale.source.generation=8;expect(!restore_completion_capsule(*capsule.data,stale),"stale source admission rejected");
  for(std::size_t offset:{std::size_t{0},std::size_t{7},std::size_t{8},std::size_t{16},std::size_t{24},capsule.data->size()-1}){auto bad=*capsule.data;bad[offset]^=std::byte{1};gig::TrackedResource mem;mem.fail_after(0);expect(!restore_completion_capsule(bad,admission,&mem)&&mem.stats().attempts==0,"capsule hash fails before allocation");auto forged=admission;forged.capsule_sha256=sha256(bad);expect(!restore_completion_capsule(bad,forged),"rehashing malformed capsule cannot change trusted originals");}
  auto trailing=*capsule.data;trailing.push_back(std::byte{});auto edited=admission;edited.capsule_sha256=sha256(trailing);expect(!restore_completion_capsule(trailing,edited),"trailing capsule data rejected");
  for(std::size_t offset:{std::size_t{8},std::size_t{16}}){auto overflowing=*capsule.data;std::fill(overflowing.begin()+static_cast<std::ptrdiff_t>(offset),overflowing.begin()+static_cast<std::ptrdiff_t>(offset+8),std::byte{255});auto edited_length=admission;edited_length.capsule_sha256=sha256(overflowing);gig::TrackedResource memory;memory.fail_after(0);expect(!restore_completion_capsule(overflowing,edited_length,&memory)&&memory.stats().attempts==0,"overflowing lengths reject before allocation");}
  expect(!restore_completion_capsule(*capsule.data,admission,nullptr),"null restore resource rejected");expect(!encode_completion_capsule(*image.data,trusted,source,spec,nullptr),"null encode resource rejected");
  auto short_source=source;short_source.pop_back();auto bad_spec=spec;bad_spec.source_sha256=sha256(short_source);expect(!encode_completion_capsule(*image.data,trusted,short_source,bad_spec),"only verified completion can be encoded");
  gig::TrackedResource baseline;{auto value=restore_completion_capsule(*capsule.data,admission,&baseline);expect(bool(value),"restore allocation baseline");}const auto count=baseline.stats().attempts;
  for(std::size_t n=0;n<count;++n){gig::TrackedResource mem;mem.fail_after(n);{auto value=restore_completion_capsule(*capsule.data,admission,&mem);expect(!value,"capsule restore allocation failure is isolated");}expect(mem.stats().live_bytes==0,"capsule restore allocation cleanup");}
  gig::TrackedResource encoder;{auto value=encode_completion_capsule(*image.data,trusted,source,spec,&encoder);expect(bool(value),"encode allocation baseline");}const auto enc=encoder.stats().attempts;
  for(std::size_t n=0;n<enc;++n){gig::TrackedResource mem;mem.fail_after(n);{auto value=encode_completion_capsule(*image.data,trusted,source,spec,&mem);expect(!value,"capsule output failure cannot publish bytes");}expect(mem.stats().live_bytes==0,"capsule output allocation cleanup");}
  std::cout<<"capsule_container="<<(gzip?"single_gzip":"binary_file")<<" restore_failpoints="<<count<<" encode_failpoints="<<enc<<'\n';
 }
 expect(state(h.reconstruction)==before&&sha256(*image.data)==trusted.artifact_sha256,"prior state and original image immutable");
}
}
int main(){try{run();std::cout<<"checks="<<checks<<" failures=0\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
