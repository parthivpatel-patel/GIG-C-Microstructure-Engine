#include "gig/itch/streaming.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_gzip_fixture.hpp"
#include <iostream>
using namespace gig::itch;
using namespace gig::itch::test;
namespace {
using Bytes=std::vector<std::byte>;
Bytes observation(char type,char value,std::uint16_t locate=1){auto b=payload(type,locate);text(b,11,locate==1?"TEST    ":"TWO     ");b[19]=static_cast<std::byte>(value);if(type=='H'){b[20]=std::byte{' '};text(b,21,"T1  ");}return b;}
struct Fixture {
 Bytes raw,compressed;StreamingConfig configuration;
 Fixture():configuration{config(),{},{},{}}{
  auto rows=streaming_records();rows.insert(rows.begin()+3,observation('H','H'));rows.insert(rows.begin()+4,observation('Y','1',2));rows.insert(rows.begin()+5,observation('H','T'));
  raw=framed_records(rows);compressed=stored_gzip(raw);configuration.compressed_sha256=sha256(compressed);configuration.reconstruction.context_policy.decode_profile=DecodeProfile::status_observations_v2;
  configuration.reconstruction.source.provenance.sha256=sha256(raw);auto h=hex_digest(sha256(raw));configuration.reconstruction.initialization.fixture_sha256=*gig::Digest::make({h.data(),h.size()}).data;configuration.gzip.output_buffer_bytes=31;
 }
};
StreamingReconstructor make(const Fixture& f,std::pmr::memory_resource* r=std::pmr::get_default_resource()){auto out=StreamingReconstructor::create(f.configuration,r);check(bool(out),"HY streaming create");return std::move(*out.data);}
StreamingFeed feed(StreamingReconstructor& s,const Fixture& f,std::size_t& at,std::size_t chunk){StreamingFeed out;for(std::size_t n=0;n<100000&&at<f.compressed.size();++n){out=s.feed(std::span(f.compressed).subspan(at,std::min(chunk,f.compressed.size()-at)));at+=out.consumed;if(out.error||out.paused)return out;}return out;}
void truth(const StreamingReconstructor& s){const auto f=s.summary();check(f.accepted_records==21&&f.source_records==21&&f.native_records==7&&f.external_observations==14,"source accounting includes all H/Y");check(s.reconstruction().engine(0)->journal_size()==6&&s.reconstruction().engine(1)->journal_size()==1,"observations excluded from both journals");check(s.reconstruction().receipts().size()==21,"receipts exact");}
}
int main(){try{Fixture f;std::optional<StreamingSummary> golden;
 for(std::size_t chunk:std::array<std::size_t,4>{1,3,17,65536}){auto s=make(f);std::size_t at=0;check(!feed(s,f,at,chunk).error,"HY streaming feed");auto end=s.finish();check(end.publication_eligible&&end.source_complete,"synthetic publication gates remain");truth(s);if(golden)check(end.accepted_prefix_sha256==golden->accepted_prefix_sha256,"fragment deterministic hash");else golden=end;}
 auto a=make(f);check(!a.pause_after(5),"pause at HY boundary");std::size_t ai=0;check(feed(a,f,ai,1).paused,"source pause");auto code=*gig::Digest::make(std::string(64,'8')).data;auto cp=a.checkpoint(code);check(bool(cp),"HY stream checkpoint");auto b=make(f);check(!b.pause_after(5),"replay pause");std::size_t bi=0;check(feed(b,f,bi,17).paused&&!b.verify_checkpoint(*cp.data,code),"restart fragmentation equality");auto wrong=*cp.data;wrong.config.reconstruction.context_policy.decode_profile=DecodeProfile::baseline_v1;check(bool(b.verify_checkpoint(wrong,code)),"profile checkpoint mismatch");check(!a.resume()&&!b.resume(),"resume");check(!feed(a,f,ai,1).error&&!feed(b,f,bi,65536).error,"complete restart");check(a.finish().accepted_prefix_sha256==b.finish().accepted_prefix_sha256,"restart accepted hash");truth(a);truth(b);
 auto bounded=make(f);std::size_t at=0;const auto half=std::span(f.compressed).first(f.compressed.size()/2);while(at<half.size()){auto r=bounded.feed(half.subspan(at));at+=r.consumed;check(!r.error&&r.consumed>0,"bounded progress");}check(!bounded.finish(EndKind::bounded_prefix).publication_eligible,"partial prefix not published");
 gig::TrackedResource baseline;{auto s=make(f,&baseline);std::size_t p=0;check(!feed(s,f,p,3).error&&s.finish().publication_eligible,"allocation baseline");}const auto sites=baseline.stats().attempts;check(sites>3&&baseline.stats().live_bytes==0,"tracked baseline cleanup");
 for(std::size_t fail=0;fail<sites;++fail){gig::TrackedResource r;r.fail_after(fail);{auto s=StreamingReconstructor::create(f.configuration,&r);if(s){std::size_t p=0;auto error=feed(*s.data,f,p,3);check(bool(error.error)||!s.data->finish().publication_eligible,"reached failure stops publication");}else check(s.error.code==gig::ErrorCode::resource_exhausted,"creation failure structured");}check(r.stats().live_bytes==0&&r.stats().live_blocks==0,"all reached failures clean");}
 std::cout<<"hy_streaming_allocation_fault_sites="<<sites<<" authored_records=21 native_records=7 external_observations=14\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
