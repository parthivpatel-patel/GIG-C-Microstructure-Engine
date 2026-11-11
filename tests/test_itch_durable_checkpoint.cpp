#include "gig/itch/durable_checkpoint.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_reconstruction_fixture.hpp"
#include "support/itch_seed_checks.hpp"
#include <fstream>
#include <iostream>
using namespace gig::itch;using namespace gig::itch::test;
namespace {
std::size_t checks=0;void expect(bool v,const char*m){++checks;check(v,m);}
gig::Digest code(){return *gig::Digest::make(std::string(64,'b')).data;}
SourceIdentity capture(){return source_id("durable-authored-capture");}
void le(std::pmr::vector<std::byte>&b,std::size_t p,std::uint64_t v){for(std::size_t n=0;n<8;++n){b[p+n]=static_cast<std::byte>(v&255);v>>=8;}}
void repair(std::pmr::vector<std::byte>&b){le(b,16,b.size()-56);auto hash=sha256(std::span{b}.subspan(56));std::copy(hash.begin(),hash.end(),b.begin()+24);}
void setup(Harness&h){h.setup();h.accept(add());h.accept(add(201,9,200,2));h.accept(reduce('E',101,2,77));h.accept(replace(101,103,8));h.accept(trade(88));h.accept(broken(88));}
std::pmr::vector<std::byte> image(Harness&h){auto i=h.reconstruction.hot_checkpoint();expect(bool(i),"capture image");auto bytes=encode_hot_checkpoint(*i.data,capture(),17,code());expect(bool(bytes),"encode image");return std::move(*bytes.data);}
DurableAdmission admission(const std::pmr::vector<std::byte>&b,const Harness&h){return {sha256(b),hot_contract_sha256(h.reconstruction.config()),code(),capture(),17};}
void equivalence(){Harness h;setup(h);auto bytes=image(h);auto twice=image(h);expect(bytes==twice,"deterministic portable encoding");auto trust=admission(bytes,h);auto restored=restore_durable_checkpoint(bytes,trust);expect(bool(restored),"durable import");expect(state(h.reconstruction)==state(*restored.data),"both native states preserved");expect(h.reconstruction.summary()==restored.data->summary(),"source accounting preserved");auto recaptured=restored.data->hot_checkpoint();auto encoded=encode_hot_checkpoint(*recaptured.data,capture(),17,code());expect(bool(encoded)&&*encoded.data==bytes,"byte-identical recapture after isolated restore");
 for(const auto&b:std::vector<std::vector<std::byte>>{reduce('X',103,1),reduce('D',201,0,0,2),add(301,7,190,2,'S')}){auto loc=h.location();expect(h.process(b).committed,"original suffix");expect(restored.data->process(b,loc).committed,"restored suffix without duplicate prefix");expect(state(h.reconstruction)==state(*restored.data),"deterministic suffix");}
 auto before=state(*restored.data);auto duplicate=restored.data->process(add(),{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}});expect(!duplicate.committed&&state(*restored.data)==before,"old source position cannot mutate book");
}
void invalid(){Harness h;setup(h);auto bytes=image(h);auto trusted=admission(bytes,h);
 auto reject=[&](const auto&b,DurableAdmission a){expect(!restore_durable_checkpoint(b,a),"malformed image rejected");};
 for(auto n:std::array<std::size_t,8>{0,1,8,16,24,55,56,bytes.size()-1}){auto b=std::span{bytes}.first(n);auto t=trusted;t.artifact_sha256=sha256(b);reject(b,t);}
 auto mutate=[&](auto change,bool rehash){auto b=bytes;change(b);if(rehash)repair(b);auto t=trusted;t.artifact_sha256=sha256(b);reject(b,t);};
 mutate([](auto&b){b[0]=std::byte{'X'};},false);
 mutate([](auto&b){le(b,8,2);},false);
 mutate([](auto&b){le(b,16,UINT64_MAX);},false);
 mutate([](auto&b){b.back()^=std::byte{1};},false);
 mutate([](auto&b){le(b,56,UINT64_MAX);},true); // token length:before allocation
 const auto generation_at=56+8+capture().view().size();mutate([&](auto&b){le(b,generation_at,18);},true);
 const auto version_at=generation_at+8+8+64;mutate([&](auto&b){le(b,version_at,2);},true);
 mutate([](auto&b){b.push_back(std::byte{});},true);
 auto wrong=trusted;wrong.capture=source_id("other-capture");reject(bytes,wrong);wrong=trusted;++wrong.generation;reject(bytes,wrong);wrong=trusted;wrong.contract_sha256[0]^=std::byte{1};reject(bytes,wrong);wrong=trusted;wrong.artifact_sha256[0]^=std::byte{1};reject(bytes,wrong);
 gig::TrackedResource zero;zero.fail_after(0);auto corrupt=bytes;corrupt[0]^=std::byte{1};auto t=trusted;t.artifact_sha256=sha256(corrupt);expect(!restore_durable_checkpoint(corrupt,t,&zero)&&zero.stats().attempts==0,"invalid header rejected before PMR allocation");
 gig::TrackedResource baseline;{auto r=restore_durable_checkpoint(bytes,trusted,&baseline);expect(bool(r),"restoration allocation baseline");}const auto count=baseline.stats().attempts;expect(baseline.stats().live_bytes==0,"baseline released");
 std::size_t rejected=0;for(std::size_t n=0;n<count;++n){gig::TrackedResource memory;memory.fail_after(n);{auto r=restore_durable_checkpoint(bytes,trusted,&memory);expect(!r,"every measured restore allocation fails when injected");expect(r.error.code==gig::ErrorCode::resource_exhausted,"real allocation exhaustion classified");++rejected;}expect(memory.stats().live_bytes==0,"failed admission leaks no PMR allocations");}
 expect(rejected>40&&rejected<1000,"all restoration allocation points swept");std::cout<<"durable_restore_failpoints="<<rejected<<'\n';
 auto again=restore_durable_checkpoint(bytes,trusted);expect(bool(again)&&state(*again.data)==state(h.reconstruction),"donor unchanged and image remains admissible after failures");
}
void encoding_faults_and_empty_cursor(){Harness empty;auto i=empty.reconstruction.hot_checkpoint();expect(bool(i),"empty initial checkpoint");i.data->context.next_location.frame_offset=ByteOffset{4};auto identity=hot_identity(*i.data,code());expect(bool(identity)&&!SyntheticReconstructor::restore_hot(*i.data,*identity.data,empty.reconstruction.config(),code()),"even a matching digest cannot admit an impossible empty cursor");
 Harness h;setup(h);auto state=h.reconstruction.hot_checkpoint();gig::TrackedResource baseline;{auto b=encode_hot_checkpoint(*state.data,capture(),17,code(),&baseline);expect(bool(b),"encode allocation baseline");}auto count=baseline.stats().attempts;expect(count>50&&baseline.stats().live_bytes==0,"encode allocation envelope measured");
 for(std::size_t n=0;n<count;++n){gig::TrackedResource memory;memory.fail_after(n);{auto b=encode_hot_checkpoint(*state.data,capture(),17,code(),&memory);expect(!b&&b.error.code==gig::ErrorCode::resource_exhausted,"each encode allocation failure explicit");}expect(memory.stats().live_bytes==0,"failed encode releases all memory");}
 std::cout<<"durable_encode_failpoints="<<count<<'\n';
}
void seeded(){SeedFixture f;auto original=f.create();expect(bool(original),"seed factory");auto&engine=*original.data;
 auto verify=[&](){auto img=engine.hot_checkpoint();expect(bool(img),"seed typed checkpoint");auto b=encode_hot_checkpoint(*img.data,capture(),17,code());expect(bool(b),"seed durable encoding");DurableAdmission a{sha256(*b.data),hot_contract_sha256(engine.config()),code(),capture(),17};auto restored=restore_durable_checkpoint(*b.data,a);if(!restored)std::cerr<<restored.error.field<<'\n';expect(bool(restored),"seed durable admission");expect(state(*restored.data)==state(engine),"seed native/retired/matches preserved");auto other=restored.data->hot_checkpoint();expect(context_image_identity(other.data->context).data==context_image_identity(img.data->context).data,"seed full context identity");return std::move(*restored.data);};
 auto initial=verify();auto loc=f.boundary;auto bytes=reduce('E',11,2,71);expect(engine.process(bytes,loc,engine.config().source.provenance).committed,"seed first continuation");expect(initial.process(bytes,loc,initial.config().source.provenance).committed,"restored seed continuation");expect(state(engine)==state(initial),"seed continuation exact");auto resumed=verify();
 auto after=Location{ByteOffset{loc.frame_offset.value()+bytes.size()+2},ByteOffset{loc.payload_offset.value()+bytes.size()+2},RecordOrdinal{loc.ordinal.value()+1}};bytes=replace(12,13,9,101);expect(engine.process(bytes,after,engine.config().source.provenance).committed&&resumed.process(bytes,after,resumed.config().source.provenance).committed,"post-checkpoint seeded replacement");expect(state(engine)==state(resumed),"seed FIFO/sequence continuation exact");
}
void fixture(const char*path,bool depth_one=false){auto c=config();if(depth_one)for(auto&b:c.bindings)if(b)b->limits.max_snapshot_depth=1;Harness h(c);setup(h);auto b=image(h);std::ofstream out(path,std::ios::binary);out.write(reinterpret_cast<const char*>(b.data()),static_cast<std::streamsize>(b.size()));out.close();expect(bool(out),"fixture write");const auto a=admission(b,h);auto ah=hex_digest(a.artifact_sha256),ch=hex_digest(a.contract_sha256);std::cout<<"{\"artifact_sha256\":\""<<std::string_view(ah.data(),ah.size())<<"\",\"contract_sha256\":\""<<std::string_view(ch.data(),ch.size())<<"\",\"implementation_sha256\":\""<<code().view()<<"\",\"capture\":\""<<capture().view()<<"\",\"generation\":17,\"bytes\":"<<b.size()<<",\"records\":"<<h.ordinal<<",\"next_frame\":"<<h.offset<<"}\n";}
}
int main(int argc,char**argv){try{if(argc==3&&(std::string_view(argv[1])=="--fixture"||std::string_view(argv[1])=="--fixture-depth1")){fixture(argv[2],std::string_view(argv[1])=="--fixture-depth1");return 0;}equivalence();invalid();encoding_faults_and_empty_cursor();seeded();std::cout<<"checks="<<checks<<" failures=0\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
