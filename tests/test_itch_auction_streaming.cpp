#include "gig/itch/streaming.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_gzip_fixture.hpp"
#include <iostream>
using namespace gig::itch;
using namespace gig::itch::test;
namespace {
using Bytes=std::vector<std::byte>;
Bytes observation(char t,std::uint16_t locate=1){
 auto b=payload(t,t=='K'?0:locate);text(b,t=='I'?28:11,locate==1?"TEST    ":"TWO     ");
 if(t=='K'){put(b,19,123,4);b[23]=std::byte{'A'};put(b,24,100,4);}
 if(t=='J'){put(b,19,100,4);put(b,23,101,4);put(b,27,99,4);put(b,31,UINT32_MAX,4);}
 if(t=='I'){put(b,11,UINT64_MAX,8);put(b,19,0,8);b[27]=std::byte{'P'};put(b,36,100,4);put(b,40,100,4);put(b,44,100,4);b[48]=std::byte{'A'};b[49]=std::byte{' '};}
 if(t=='O'){b[19]=std::byte{'Y'};put(b,20,90,4);put(b,24,110,4);put(b,28,100,4);put(b,32,UINT64_MAX,8);put(b,40,99,4);put(b,44,101,4);}
 return b;
}
struct Fixture {
 Bytes raw,compressed;StreamingConfig configuration;
 Fixture():configuration{config(),{},{},{}}{
  auto rows=streaming_records();std::size_t position=3;for(char type:std::string_view{"KJIO"})rows.insert(rows.begin()+static_cast<std::ptrdiff_t>(position++),observation(type,type=='I'?2:1));
  raw=framed_records(rows);compressed=stored_gzip(raw);configuration.compressed_sha256=sha256(compressed);configuration.reconstruction.context_policy.decode_profile=DecodeProfile::retained_2023_auctions_v4;
  configuration.reconstruction.source.provenance.sha256=sha256(raw);auto h=hex_digest(sha256(raw));configuration.reconstruction.initialization.fixture_sha256=*gig::Digest::make({h.data(),h.size()}).data;configuration.gzip.output_buffer_bytes=31;
 }
};
StreamingReconstructor make(const Fixture& f,std::pmr::memory_resource* r=std::pmr::get_default_resource()){auto out=StreamingReconstructor::create(f.configuration,r);check(bool(out),"auction streaming create");return std::move(*out.data);}
StreamingFeed feed(StreamingReconstructor& s,const Fixture& f,std::size_t& at,std::size_t chunk){StreamingFeed out;for(std::size_t n=0;n<100000&&at<f.compressed.size();++n){out=s.feed(std::span(f.compressed).subspan(at,std::min(chunk,f.compressed.size()-at)));at+=out.consumed;if(out.error||out.paused)return out;}return out;}
void truth(const StreamingReconstructor& s){const auto f=s.summary();check(f.accepted_records==22&&f.source_records==22&&f.native_records==7&&f.external_observations==15,"source accounting includes all auction observations");check(s.reconstruction().engine(0)->journal_size()==6&&s.reconstruction().engine(1)->journal_size()==1,"observations excluded from both journals");check(s.reconstruction().receipts().size()==22,"receipts exact");}
void rehash(Fixture& f){f.compressed=stored_gzip(f.raw);f.configuration.compressed_sha256=sha256(f.compressed);f.configuration.reconstruction.source.provenance.sha256=sha256(f.raw);auto h=hex_digest(sha256(f.raw));f.configuration.reconstruction.initialization.fixture_sha256=*gig::Digest::make({h.data(),h.size()}).data;}
std::size_t find_frame(const Bytes& bytes,char type){std::size_t at=0;while(at+2<bytes.size()){const auto n=(std::to_integer<std::size_t>(bytes[at])<<8)|std::to_integer<std::size_t>(bytes[at+1]);if(!n)break;if(bytes[at+2]==static_cast<std::byte>(type))return at;at+=n+2;}throw std::runtime_error("fixture frame absent");}
void interrupted_prefixes(){
 Fixture f;check(f.raw.size()<65536,"one authored stored block oracle");
 std::size_t schedules=0;
 for(std::size_t cut=0;cut<f.compressed.size();++cut){
  // RFC1951 stored block:10-byte gzip header +5-byte block header.
  const auto available=cut<=15?0:std::min(cut-15,f.raw.size());
  std::size_t offset=0,expected=0;
  while(offset+2<=available){
   const auto length=std::to_integer<std::size_t>(f.raw[offset])*256+std::to_integer<std::size_t>(f.raw[offset+1]);
   if(!length||length>available-offset-2)break;
   offset+=length+2;++expected;
  }
  const auto native=expected<=7?0:std::min(expected-7,std::size_t{7});
  std::optional<StreamingSummary> golden;
  for(std::size_t chunk:{std::size_t{1},std::size_t{17},std::size_t{65536}}){
   gig::TrackedResource memory(std::pmr::get_default_resource(),8U*1024U*1024U);
   {auto pipeline=make(f,&memory);std::size_t at=0;
    while(at<cut){const auto step=pipeline.feed(std::span(f.compressed).subspan(at,std::min(chunk,cut-at)));check(!step.error&&step.consumed>0,"prefix bounded progress");at+=step.consumed;}
    const auto end=pipeline.finish();
    check(bool(end.error)&&!end.source_complete&&!end.publication_eligible,"every incomplete gzip prefix refused");
    check(end.accepted_records==expected&&end.native_records==native&&end.external_observations==expected-native,"independent stored-block/frame prefix oracle");
    check(pipeline.reconstruction().receipts().size()==expected,"no missing/duplicate prefix receipts");
    const auto journal=pipeline.reconstruction().engine(0)->journal_size()+pipeline.reconstruction().engine(1)->journal_size();
    check(journal==native,"prefix native journal accounting");
    if(golden)check(end.accepted_prefix_sha256==golden->accepted_prefix_sha256&&end.error.code==golden->error.code,"all-prefix fragmentation invariance");else golden=end;
   }check(memory.stats().live_bytes==0&&memory.stats().live_blocks==0,"all-prefix cleanup");++schedules;
  }
 }
 std::cout<<"exhaustive_gzip_prefixes="<<f.compressed.size()<<" fragment_schedules="<<schedules<<" independent_native_external_receipt_oracle=true\n";
}
void faults(){
 for(unsigned variant=0;variant<10;++variant){std::optional<StreamingSummary> expected;for(std::size_t chunk:{std::size_t{1},std::size_t{65536}}){Fixture f;std::uint64_t accepted=22,native=7;
  switch(variant){
  case 0:f.compressed[f.compressed.size()-8]^=std::byte{1};f.configuration.compressed_sha256=sha256(f.compressed);break;
  case 1:f.compressed.pop_back();f.configuration.compressed_sha256=sha256(f.compressed);break;
  case 2:f.raw.pop_back();rehash(f);break;
  case 3:f.configuration.framing.max_payload_bytes=49;accepted=5;native=0;break;
  case 4:f.raw[find_frame(f.raw,'I')+2+27]=std::byte{'?'};rehash(f);accepted=5;native=0;break;
  case 5:f.raw[find_frame(f.raw,'K')+2+23]=std::byte{'C'};rehash(f);accepted=3;native=0;break;
  case 6:{const auto at=find_frame(f.raw,'A');const auto n=(std::to_integer<std::size_t>(f.raw[at])<<8)|std::to_integer<std::size_t>(f.raw[at+1]);Bytes record(f.raw.begin()+static_cast<std::ptrdiff_t>(at),f.raw.begin()+static_cast<std::ptrdiff_t>(at+n+2));f.raw.insert(f.raw.begin()+static_cast<std::ptrdiff_t>(at+n+2),record.begin(),record.end());rehash(f);accepted=8;native=1;break;}
  case 7:for(auto& b:f.configuration.reconstruction.bindings)b->max_journal_records=1;accepted=9;native=2;break;
  case 8:f.configuration.reconstruction.max_source_records=3;accepted=3;native=0;break;
  case 9:f.raw[find_frame(f.raw,'K')+2]=std::byte{'?'};rehash(f);accepted=3;native=0;break;
  default:break;}
  auto pipeline=make(f);std::size_t at=0;const auto fed=feed(pipeline,f,at,chunk);const auto end=pipeline.finish();check(fed.error||end.error,"fault explicit");check(!end.publication_eligible&&!end.source_complete,"fault cannot publish");check(end.accepted_records==accepted&&end.native_records==native&&end.accepted_records==end.native_records+end.external_observations,"independent fault prefix accounting");
  if(expected)check(end.accepted_prefix_sha256==expected->accepted_prefix_sha256&&end.error.code==expected->error.code&&end.accepted_records==expected->accepted_records,"fragment invariant deterministic failure");else expected=end;
 }}std::cout<<"auction_fault_variants=10 fragmentation_schedules=20 independently_checked_prefix_counts=true\n";
}
}
int main(int argc,char** argv){try{if(argc==2&&std::string_view(argv[1])=="faults"){faults();interrupted_prefixes();return 0;}check(argc==1,"arguments");Fixture f;std::optional<StreamingSummary> golden;
 for(std::size_t chunk:std::array<std::size_t,4>{1,3,17,65536}){auto s=make(f);std::size_t at=0;check(!feed(s,f,at,chunk).error,"auction streaming feed");auto end=s.finish();check(end.publication_eligible&&end.source_complete,"synthetic publication gates remain");truth(s);if(golden)check(end.accepted_prefix_sha256==golden->accepted_prefix_sha256,"fragment deterministic hash");else golden=end;}
 auto a=make(f);check(!a.pause_after(5),"pause at auction boundary");std::size_t ai=0;check(feed(a,f,ai,1).paused,"source pause");auto code=*gig::Digest::make(std::string(64,'8')).data;auto cp=a.checkpoint(code);check(bool(cp),"auction stream checkpoint");auto b=make(f);check(!b.pause_after(5),"replay pause");std::size_t bi=0;check(feed(b,f,bi,17).paused&&!b.verify_checkpoint(*cp.data,code),"restart fragmentation equality");auto wrong=*cp.data;wrong.config.reconstruction.context_policy.decode_profile=DecodeProfile::baseline_v1;check(bool(b.verify_checkpoint(wrong,code)),"profile checkpoint mismatch");check(!a.resume()&&!b.resume(),"resume");check(!feed(a,f,ai,1).error&&!feed(b,f,bi,65536).error,"complete restart");check(a.finish().accepted_prefix_sha256==b.finish().accepted_prefix_sha256,"restart accepted hash");truth(a);truth(b);
 auto bounded=make(f);std::size_t at=0;const auto half=std::span(f.compressed).first(f.compressed.size()/2);while(at<half.size()){auto r=bounded.feed(half.subspan(at));at+=r.consumed;check(!r.error&&r.consumed>0,"bounded progress");}check(!bounded.finish(EndKind::bounded_prefix).publication_eligible,"partial prefix not published");
 gig::TrackedResource baseline;{auto s=make(f,&baseline);std::size_t p=0;check(!feed(s,f,p,3).error&&s.finish().publication_eligible,"allocation baseline");}const auto sites=baseline.stats().attempts;check(sites>3&&baseline.stats().live_bytes==0,"tracked baseline cleanup");
 for(std::size_t fail=0;fail<sites;++fail){gig::TrackedResource r;r.fail_after(fail);{auto s=StreamingReconstructor::create(f.configuration,&r);if(s){std::size_t p=0;auto error=feed(*s.data,f,p,3);check(bool(error.error)||!s.data->finish().publication_eligible,"reached failure stops publication");}else check(s.error.code==gig::ErrorCode::resource_exhausted,"creation failure structured");}check(r.stats().live_bytes==0&&r.stats().live_blocks==0,"all reached failures clean");}
 std::cout<<"auction_streaming_allocation_fault_sites="<<sites<<" authored_records=22 native_records=7 external_observations=15\n";return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
