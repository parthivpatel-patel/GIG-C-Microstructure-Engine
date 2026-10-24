#include "gig/itch/restart.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "tests/support/itch_reconstruction_fixture.hpp"
#include <algorithm>
#include <iostream>
#include <sstream>
#include <type_traits>
using namespace gig::itch;
using namespace gig::itch::test;
namespace {
using Bytes=std::vector<std::byte>;
constexpr auto profile=DecodeProfile::administrative_observations_v3;
constexpr Location loc{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}};
static_assert(!std::is_convertible_v<Price8,Price4>);
Bytes observation(char t,std::uint16_t locate=1){
 auto b=payload(t,(t=='V'||t=='W')?0:locate);
 if(t=='L'){text(b,11,"MPID");text(b,15,locate==1?"TEST    ":"TWO     ");text(b,23,"YNA");}
 if(t=='V'){put(b,11,0,8);put(b,19,UINT64_MAX,8);put(b,27,UINT64_C(1)<<32,8);}
 if(t=='W')b[11]=std::byte{'2'};
 if(t=='h'){text(b,11,locate==1?"TEST    ":"TWO     ");text(b,19,"QH");}
 if(t=='N'){text(b,11,locate==1?"TEST    ":"TWO     ");b[19]=std::byte{'A'};}
 return b;
}
ReconstructionConfig configuration(){auto c=config();c.context_policy.decode_profile=profile;return c;}
SourceContext context(std::pmr::memory_resource* memory=std::pmr::get_default_resource()){auto c=configuration();auto x=SourceContext::create(c.source,c.context_policy,memory);check(bool(x),"admin create");return std::move(*x.data);}
void wire(){
 for(char t:std::string_view{"LVWhN"}){auto b=observation(t);auto d=decode(b,loc,{},profile);check(bool(d),"new family decoded");for(auto p:{DecodeProfile::baseline_v1,DecodeProfile::status_observations_v2})check(decode(b,loc,{},p).error.code==Code::unsupported_type,"old profiles unchanged");
  for(std::size_t n=0;n<=b.size()+1;++n){
   if(n==b.size())continue;
   // Construct the requested extent directly: preserve the available prefix and
   // zero-fill only the one-byte extension, without copy-then-resize growth.
   Bytes bad(n,std::byte{});
   std::copy_n(b.begin(),std::min(n,b.size()),bad.begin());
   check(!decode(bad,loc,{},profile),"all malformed lengths");
  }
 }
 auto v=decode(observation('V'),loc,{},profile);const auto& levels=std::get<MwcbDeclineLevels>(v.data->message);check(levels.level1.value()==0&&levels.level2.value()==UINT64_MAX&&levels.level3.value()==(UINT64_C(1)<<32),"exact full Price8 source values");
 auto bad=observation('L');bad[11]=std::byte{0};check(decode(bad,loc,{},profile).error.code==Code::invalid_value,"MPID encoding");
 for(auto pair:{std::pair{'L',23U},std::pair{'L',24U},std::pair{'L',25U},std::pair{'W',11U},std::pair{'h',19U},std::pair{'h',20U},std::pair{'N',19U}}){auto b=observation(pair.first);b[pair.second]=std::byte{0};check(decode(b,loc,{},profile).error.code==Code::invalid_enum,"invalid enum");}
 check(!decode(observation('V'),loc,{},static_cast<DecodeProfile>(255)),"invalid profile");
}
void contextual(){
 auto c=context();std::uint64_t offset=0,ordinal=0;
 const auto apply=[&](const Bytes& b){auto r=c.apply(b,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},configuration().source.provenance);if(r.committed()){offset+=b.size()+2;++ordinal;}return r;};
 check(apply(system()).committed(),"session start");check(apply(observation('V')).committed()&&apply(observation('W')).committed(),"global observations need no invented directory");
 auto before=c.summary();check(!apply(observation('N')).committed()&&c.summary()==before,"unknown security failure atomic");check(apply(directory()).committed()&&apply(directory(2,"TWO     ")).committed(),"directories");
 for(char t:std::string_view{"LVWhN"}){auto x=apply(observation(t));check(x.committed()&&x.record->normalization_version==3&&x.record->policy.decode_profile==profile,"v3 contract");check(x.record->integration==IntegrationClass::external_observation&&!x.record->before&&!x.record->after&&!x.record->price_ticks&&!x.record->quantity_lots,"not liquidity");check(x.record->source.provenance==configuration().source.provenance,"exact provenance");}
 for(char t:std::string_view{"VW"}){auto b=observation(t);put(b,1,1,2);before=c.summary();check(!apply(b).committed()&&c.summary()==before,"global locate nonzero rejection");}
 for(char t:std::string_view{"LhN"}){auto b=observation(t);text(b,t=='L'?15:11,"WRONG   ");before=c.summary();check(!apply(b).committed()&&c.summary()==before,"stock mismatch atomic");}
 check(c.orders().empty()&&c.matches().empty()&&c.summary().initialization_incomplete,"no order history invented");
}
void integration(){
 Harness h(configuration());h.setup();h.accept(add());const auto initial=state(h.reconstruction);auto counts=h.reconstruction.summary().native_counts;
 for(char t:std::string_view{"LVWhN"}){auto s=h.process(observation(t,t=='h'?2:1));check(s.committed&&s.disposition==SourceDisposition::external_observation,"external receipt");check(!s.native_sequence&&state(h.reconstruction)==initial&&h.reconstruction.summary().native_counts==counts,"no native mutation");if(t=='V'||t=='W')check(!s.book_index,"global no fabricated book binding");}
 check(h.reconstruction.receipts().size()==9&&h.reconstruction.summary().context_committed==9,"source accounting");
 auto unknown=configuration();unknown.initialization.kind=InitialStateKind::unknown;check(!SyntheticReconstructor::create(unknown),"unknown init remains blocked");
}
void allocation(){
 gig::TrackedResource base;{auto c=context(&base);(void)c;}const auto sites=base.stats().attempts;check(sites==3&&base.stats().live_bytes==0,"reserve bounds");
 for(std::size_t i=0;i<sites;++i){gig::TrackedResource memory;memory.fail_after(i);auto c=configuration();check(!SourceContext::create(c.source,c.context_policy,&memory)&&memory.stats().live_bytes==0,"reached failure clean");}
 gig::TrackedResource memory;{Harness h(configuration(),&memory);h.setup();const auto initial=state(h.reconstruction);memory.fail_after(0);const auto attempts=memory.stats().attempts;for(char t:std::string_view{"LVWhN"})check(h.process(observation(t)).committed,"allocation-free observation");check(memory.stats().attempts==attempts,"observations allocated zero times");memory.disable_failure();check(state(h.reconstruction)==initial,"no book changes");}check(memory.stats().live_bytes==0,"all storage clean");
 std::cout<<"admin_context_allocation_sites="<<sites<<" observation_allocations=0 sizeof_message="<<sizeof(Message)<<" sizeof_record="<<sizeof(DecodedRecord)<<'\n';
}
void restart(){
 Harness h(configuration());h.setup();h.accept(observation('V'));h.accept(observation('h'));h.accept(observation('N'));auto code=number<gig::Digest>(std::string(64,'9'));
 Bytes bytes;
 const std::vector<Bytes> rows{system(),directory(),directory(2,"TWO     "),observation('V'),observation('h'),observation('N')};
 for(const auto& b:rows){bytes.push_back(static_cast<std::byte>(b.size()>>8));bytes.push_back(static_cast<std::byte>(b.size()&255));bytes.insert(bytes.end(),b.begin(),b.end());}
 auto cp=capture_checkpoint(h.reconstruction,bytes,code);check(bool(cp),"checkpoint capture");auto replay=restart_from_checkpoint(*cp.data,configuration(),bytes,code);check(replay&&state(*replay.data)==state(h.reconstruction)&&replay.data->receipts().size()==6,"deterministic replay");auto wrong=configuration();wrong.context_policy.decode_profile=DecodeProfile::status_observations_v2;check(!restart_from_checkpoint(*cp.data,wrong,bytes,code),"profile mismatch");
}
void context_oracle(){
 std::string line;while(std::getline(std::cin,line)){std::istringstream in(line);unsigned flags;in>>flags;auto cfg=configuration();cfg.context_policy.require_monotonic_timestamps=(flags&1U)!=0;cfg.context_policy.require_intraday_timestamps=(flags&2U)!=0;auto c=SourceContext::create(cfg.source,cfg.context_policy);check(bool(c),"reference context create");std::uint64_t offset=0,ordinal=0;std::string token;bool first=true;std::cout<<'[';
 while(in>>token){Bytes b;for(std::size_t i=0;i<token.size();i+=2)b.push_back(static_cast<std::byte>(std::stoul(token.substr(i,2),nullptr,16)));auto x=c.data->apply(b,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},cfg.source.provenance);if(x.committed()){offset+=b.size()+2;++ordinal;}if(!first)std::cout<<',';first=false;std::cout<<"{\"committed\":"<<(x.committed()?"true":"false")<<",\"accepted\":"<<c.data->summary().accepted_records<<",\"directories\":"<<c.data->directories().size()<<",\"orders\":"<<c.data->orders().size()<<",\"matches\":"<<c.data->matches().size()<<",\"offset\":"<<offset<<",\"version\":"<<(x.record?x.record->normalization_version:0)<<'}';}
 std::cout<<"]\n";}
}
void oracle(){
 std::string line;while(std::getline(std::cin,line)){std::istringstream in(line);unsigned p;std::string token;in>>p>>token;Bytes b;for(std::size_t i=0;i<token.size();i+=2)b.push_back(static_cast<std::byte>(std::stoul(token.substr(i,2),nullptr,16)));Provenance provenance;provenance.origin=Origin::observed;auto d=decode(b,loc,provenance,static_cast<DecodeProfile>(p));
 if(!d){std::cout<<"{\"ok\":false,\"code\":"<<static_cast<unsigned>(d.error.code)<<"}\n";continue;}
 Bytes encoded;encoded.push_back(static_cast<std::byte>(d.data->type));for(auto pair:{std::pair{std::uint64_t(d.data->header.stock_locate.value()),2U},std::pair{std::uint64_t(d.data->header.tracking_number.value()),2U},std::pair{d.data->header.timestamp.value(),6U}}){auto start=encoded.size();encoded.resize(start+pair.second);put(encoded,start,pair.first,pair.second);}
 const auto append=[&](std::string_view s){for(char c:s)encoded.push_back(static_cast<std::byte>(static_cast<unsigned char>(c)));};
 switch(d.data->type){
 case 'L':{const auto& l=std::get<MarketParticipantPosition>(d.data->message);append(l.mpid.view());append(l.stock.view());for(char c:{l.primary_market_maker,l.mode,l.state})encoded.push_back(static_cast<std::byte>(c));break;}
 case 'V':{const auto& v=std::get<MwcbDeclineLevels>(d.data->message);for(auto n:{v.level1.value(),v.level2.value(),v.level3.value()}){auto start=encoded.size();encoded.resize(start+8);put(encoded,start,n,8);}break;}
 case 'W':encoded.push_back(static_cast<std::byte>(std::get<MwcbStatus>(d.data->message).breached_level));break;
 case 'h':{const auto& h=std::get<OperationalHalt>(d.data->message);append(h.stock.view());encoded.push_back(static_cast<std::byte>(h.market));encoded.push_back(static_cast<std::byte>(h.action));break;}
 case 'N':{const auto& n=std::get<RetailPriceImprovement>(d.data->message);append(n.stock.view());encoded.push_back(static_cast<std::byte>(n.interest));break;}
 default:throw std::runtime_error("unexpected oracle input");}
 std::cout<<"{\"ok\":true,\"wire\":\"";constexpr char hex[]="0123456789abcdef";for(auto v:encoded){auto n=std::to_integer<unsigned>(v);std::cout<<hex[n>>4]<<hex[n&15];}std::cout<<"\",\"origin\":"<<static_cast<unsigned>(d.data->provenance.origin)<<"}\n";
 }
}
}
int main(int argc,char** argv){try{check(argc==2,"mode required");const std::string_view mode=argv[1];if(mode=="wire")wire();else if(mode=="context")contextual();else if(mode=="integration")integration();else if(mode=="allocation")allocation();else if(mode=="restart")restart();else if(mode=="oracle")oracle();else if(mode=="context_oracle")context_oracle();else return 2;return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
