#include "gig/itch/streaming.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_gzip_fixture.hpp"
#include <iostream>
using namespace gig::itch;
using namespace gig::itch::test;
namespace {
using Bytes=std::vector<std::byte>;
Bytes observation(char type,std::uint16_t locate=1){auto b=payload(type,(type=='V'||type=='W')?0:locate);
 if(type=='L'){text(b,11,"MPID");text(b,15,"TEST    ");text(b,23,"YNA");}
 if(type=='V'){put(b,11,UINT64_MAX,8);put(b,19,0,8);put(b,27,100000000,8);}
 if(type=='W')b[11]=std::byte{'1'};
 if(type=='h'){text(b,11,"TWO     ");text(b,19,"XT");}
 if(type=='N'){text(b,11,"TEST    ");b[19]=std::byte{'B'};}
 return b;}
struct Fixture {
 Bytes raw,compressed;StreamingConfig configuration;
 Fixture():configuration{config(),{},{},{}}{
  auto rows=streaming_records();std::size_t position=3;for(char type:std::string_view{"LVWhN"})rows.insert(rows.begin()+static_cast<std::ptrdiff_t>(position++),observation(type,type=='h'?2:1));
  raw=framed_records(rows);compressed=stored_gzip(raw);configuration.compressed_sha256=sha256(compressed);configuration.reconstruction.context_policy.decode_profile=DecodeProfile::administrative_observations_v3;
  configuration.reconstruction.source.provenance.sha256=sha256(raw);auto h=hex_digest(sha256(raw));configuration.reconstruction.initialization.fixture_sha256=*gig::Digest::make({h.data(),h.size()}).data;configuration.gzip.output_buffer_bytes=31;
 }
};
StreamingReconstructor make(const Fixture& f,std::pmr::memory_resource* r=std::pmr::get_default_resource()){auto out=StreamingReconstructor::create(f.configuration,r);check(bool(out),"administrative streaming create");return std::move(*out.data);}
StreamingFeed feed(StreamingReconstructor& s,const Fixture& f,std::size_t& at,std::size_t chunk){StreamingFeed out;for(std::size_t n=0;n<100000&&at<f.compressed.size();++n){out=s.feed(std::span(f.compressed).subspan(at,std::min(chunk,f.compressed.size()-at)));at+=out.consumed;if(out.error||out.paused)return out;}return out;}
void truth(const StreamingReconstructor& s){const auto f=s.summary();check(f.accepted_records==23&&f.source_records==23&&f.native_records==7&&f.external_observations==16,"source accounting includes all H/Y");check(s.reconstruction().engine(0)->journal_size()==6&&s.reconstruction().engine(1)->journal_size()==1,"observations excluded from both journals");check(s.reconstruction().receipts().size()==23,"receipts exact");}
}
int main(){try{Fixture f;std::optional<StreamingSummary> golden;
 for(std::size_t chunk:std::array<std::size_t,4>{1,3,17,65536}){auto s=make(f);std::size_t at=0;check(!feed(s,f,at,chunk).error,"administrative streaming feed");auto end=s.finish();check(end.publication_eligible&&end.source_complete,"synthetic publication gates remain");truth(s);if(golden)check(end.accepted_prefix_sha256==golden->accepted_prefix_sha256,"fragment deterministic hash");else golden=end;}
 auto a=make(f);check(!a.pause_after(5),"pause at administrative boundary");std::size_t ai=0;check(feed(a,f,ai,1).paused,"source pause");auto code=*gig::Digest::make(std::string(64,'8')).data;auto cp=a.checkpoint(code);check(bool(cp),"administrative stream checkpoint");auto b=make(f);check(!b.pause_after(5),"replay pause");std::size_t bi=0;check(feed(b,f,bi,17).paused&&!b.verify_checkpoint(*cp.data,code),"restart fragmentation equality");auto wrong=*cp.data;wrong.config.reconstruction.context_policy.decode_profile=DecodeProfile::baseline_v1;check(bool(b.verify_checkpoint(wrong,code)),"profile checkpoint mismatch");check(!a.resume()&&!b.resume(),"resume");check(!feed(a,f,ai,1).error&&!feed(b,f,bi,65536).error,"complete restart");check(a.finish().accepted_prefix_sha256==b.finish().accepted_prefix_sha256,"restart accepted hash");truth(a);truth(b);
 auto bounded=make(f);std::size_t at=0;const auto half=std::span(f.compressed).first(f.compressed.size()/2);while(at<half.size()){auto r=bounded.feed(half.subspan(at));at+=r.consumed;check(!r.error&&r.consumed>0,"bounded progress");}check(!bounded.finish(EndKind::bounded_prefix).publication_eligible,"partial prefix not published");
 gig::TrackedResource baseline;{auto s=make(f,&baseline);std::size_t p=0;check(!feed(s,f,p,3).error&&s.finish().publication_eligible,"allocation baseline");}const auto sites=baseline.stats().attempts;check(sites>3&&baseline.stats().live_bytes==0,"tracked baseline cleanup");
 for(std::size_t fail=0;fail<sites;++fail){gig::TrackedResource r;r.fail_after(fail);{auto s=StreamingReconstructor::create(f.configuration,&r);if(s){std::size_t p=0;auto error=feed(*s.data,f,p,3);check(bool(error.error)||!s.data->finish().publication_eligible,"reached failure stops publication");}else check(s.error.code==gig::ErrorCode::resource_exhausted,"creation failure structured");}check(r.stats().live_bytes==0&&r.stats().live_blocks==0,"all reached failures clean");}
 std::cout<<"admin_streaming_allocation_fault_sites="<<sites<<" authored_records=23 native_records=7 external_observations=16\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
