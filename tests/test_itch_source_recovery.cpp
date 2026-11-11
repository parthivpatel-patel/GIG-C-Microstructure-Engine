#include "gig/itch/source_recovery.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_gzip_fixture.hpp"
#include "support/itch_seed_checks.hpp"
#include <iostream>
using namespace gig::itch;using namespace gig::itch::test;
namespace {
std::size_t checks=0;void expect(bool v,const char*s){++checks;check(v,s);}
gig::Digest code(){return *gig::Digest::make(std::string(64,'b')).data;}
SourceIdentity capture(){return source_id("source-recovery-authored");}
std::pmr::vector<std::byte> save(const SyntheticReconstructor&r){auto image=r.hot_checkpoint();expect(bool(image),"checkpoint at accepted boundary");auto b=encode_hot_checkpoint(*image.data,capture(),7,code());expect(bool(b),"durable encode");return std::move(*b.data);}
DurableAdmission trust(const auto&b,const SyntheticReconstructor&r){return {sha256(b),hot_contract_sha256(r.config()),code(),capture(),7};}
SourceRecoveryAdmission source(const auto&b,RecoveryContainer c,Location first={ByteOffset{0},ByteOffset{2},RecordOrdinal{0}}){return {c,sha256(b),capture(),7,first};}
void plain_and_gzip(){
 std::vector<std::vector<std::byte>>prefix{system(),directory(),directory(2,"TWO     "),add(),add(201,9,200,2)};
 Harness h;for(const auto&b:prefix)h.accept(b);auto checkpoint=save(h.reconstruction);auto a=trust(checkpoint,h.reconstruction);
 const auto before=state(h.reconstruction);auto continuation=prefix;continuation.push_back(reduce('E',101,2,71));continuation.push_back(replace(101,103,8));continuation.push_back(reduce('D',201,0,0,2));
 auto raw=framed_records(continuation,false);for(std::size_t n=prefix.size();n<continuation.size();++n)h.accept(continuation[n]);
 for(bool compressed:{false,true}){auto b=compressed?stored_gzip(raw):raw;auto s=source(b,compressed?RecoveryContainer::single_gzip:RecoveryContainer::binary_file);s.gzip.output_buffer_bytes=7;
  auto restored=resume_hot_source(checkpoint,a,b,s);if(!restored)std::cerr<<restored.error.field<<'\n';expect(bool(restored),"source coordinated restore");expect(state(*restored.data)==state(h.reconstruction),"only suffix applied;no duplicate source/native events");expect(restored.data->summary()==h.reconstruction.summary(),"source receipts and cursors match uninterrupted run");
  auto old=resume_hot_source(checkpoint,a,b,{s.container,s.source_sha256,s.capture,8,s.first_location});expect(!old,"stale generation cannot restore source");
  auto wrong=s;wrong.source_sha256[0]^=std::byte{1};gig::TrackedResource memory;memory.fail_after(0);expect(!resume_hot_source(checkpoint,a,b,wrong,&memory)&&memory.stats().attempts==0,"source identity fails before allocation");
 }
 // Rehashing altered files does not make a different committed prefix admissible.
 auto altered=continuation;altered[3]=add(101,11);auto bad=framed_records(altered,false);expect(!resume_hot_source(checkpoint,a,bad,source(bad,RecoveryContainer::binary_file)),"committed prefix semantic mismatch");
 auto truncated=raw;truncated.pop_back();expect(!resume_hot_source(checkpoint,a,truncated,source(truncated,RecoveryContainer::binary_file)),"incomplete tail cannot publish candidate");
 auto missing=framed_records({prefix[0]},false);expect(!resume_hot_source(checkpoint,a,missing,source(missing,RecoveryContainer::binary_file)),"missing committed prefix cannot restore");
 auto terminal=framed_records(continuation,true);expect(!resume_hot_source(checkpoint,a,terminal,source(terminal,RecoveryContainer::binary_file)),"terminal cursor is explicitly unsupported");
 auto gz=stored_gzip(raw);gz[gz.size()-8]^=std::byte{1};expect(!resume_hot_source(checkpoint,a,gz,source(gz,RecoveryContainer::single_gzip)),"CRC mismatch rejects fully mutated isolated candidate");
 gz=stored_gzip(raw);gz.pop_back();expect(!resume_hot_source(checkpoint,a,gz,source(gz,RecoveryContainer::single_gzip)),"truncated gzip rejected");
 gz=stored_gzip(raw);const auto header=std::vector<std::byte>(gz.begin(),gz.begin()+10);gz.insert(gz.end(),header.begin(),header.end());expect(!resume_hot_source(checkpoint,a,gz,source(gz,RecoveryContainer::single_gzip)),"additional gzip data rejected");
 auto limit=source(raw,RecoveryContainer::binary_file);limit.framing.max_records=2;expect(!resume_hot_source(checkpoint,a,raw,limit),"framer bound");
 auto plain_prefix=framed_records(prefix,false);auto exact=resume_hot_source(checkpoint,a,plain_prefix,source(plain_prefix,RecoveryContainer::binary_file));expect(bool(exact)&&state(*exact.data)==before,"zero suffix performs no native updates");
 auto suffix_only=framed_records({continuation.back()},false);auto wrong_start=source(suffix_only,RecoveryContainer::binary_file,{ByteOffset{h.offset},ByteOffset{h.offset+2},RecordOrdinal{h.ordinal}});expect(!resume_hot_source(checkpoint,a,suffix_only,wrong_start),"arbitrary source seek/gap rejected");
 // Sweep actual PMR failures across gzip,framer,typed decoding and native import.
 auto source_gzip=stored_gzip(raw);auto spec=source(source_gzip,RecoveryContainer::single_gzip);gig::TrackedResource baseline;{auto r=resume_hot_source(checkpoint,a,source_gzip,spec,&baseline);expect(bool(r),"allocation baseline");}auto count=baseline.stats().attempts;
 for(std::size_t n=0;n<count;++n){gig::TrackedResource memory;memory.fail_after(n);{auto r=resume_hot_source(checkpoint,a,source_gzip,spec,&memory);expect(!r,"allocation fault cannot publish candidate");}expect(memory.stats().live_bytes==0,"all source/gzip/native allocations released");}
 std::cout<<"source_restore_failpoints="<<count<<'\n';
}
void seeded(){SeedFixture f;auto original=f.create();expect(bool(original),"seed create");auto checkpoint=save(*original.data);auto a=trust(checkpoint,*original.data);auto raw=framed_records({reduce('E',11,2,71),replace(12,13,9,101)},false);auto gz=stored_gzip(raw);auto s=source(gz,RecoveryContainer::single_gzip,f.boundary);s.gzip.output_buffer_bytes=1;auto restored=resume_hot_source(checkpoint,a,gz,s);if(!restored)std::cerr<<restored.error.field<<'\n';expect(bool(restored),"seeded gzip source boundary");expect(restored.data->summary().context_committed==2&&restored.data->engine(0)->journal_size()==3,"seed plus two source events exactly once");expect(restored.data->engine(0)->book().remaining()==17,"seeded result exact");}
}
int main(){try{plain_and_gzip();seeded();std::cout<<"checks="<<checks<<" failures=0\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
