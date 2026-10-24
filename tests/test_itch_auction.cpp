#include "gig/itch/restart.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "tests/support/itch_reconstruction_fixture.hpp"
#include <iostream>
#include <sstream>
#include <type_traits>
using namespace gig::itch;
using namespace gig::itch::test;
namespace {
using Bytes=std::vector<std::byte>;
constexpr auto profile=DecodeProfile::retained_2023_auctions_v4;
constexpr Location loc{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}};
static_assert(!std::is_convertible_v<Price8,Price4>);
Bytes observation(char t,std::uint16_t locate=1){
 auto b=payload(t,t=='K'?0:locate);text(b,t=='I'?28:11,locate==1?"TEST    ":"TWO     ");
 if(t=='K'){put(b,19,123,4);b[23]=std::byte{'A'};put(b,24,100,4);}
 if(t=='J'){put(b,19,100,4);put(b,23,101,4);put(b,27,99,4);put(b,31,UINT32_MAX,4);}
 if(t=='I'){put(b,11,UINT64_MAX,8);put(b,19,0,8);b[27]=std::byte{'P'};put(b,36,100,4);put(b,40,100,4);put(b,44,100,4);b[48]=std::byte{'A'};b[49]=std::byte{' '};}
 if(t=='O'){b[19]=std::byte{'Y'};put(b,20,90,4);put(b,24,110,4);put(b,28,100,4);put(b,32,UINT64_MAX,8);put(b,40,99,4);put(b,44,101,4);}
 return b;
}
ReconstructionConfig configuration(){auto c=config();c.context_policy.decode_profile=profile;return c;}
SourceContext context(std::pmr::memory_resource* memory=std::pmr::get_default_resource()){auto c=configuration();auto x=SourceContext::create(c.source,c.context_policy,memory);check(bool(x),"auction create");return std::move(*x.data);}
void wire(){
 for(char t:std::string_view{"KJIO"}){auto b=observation(t);auto d=decode(b,loc,{},profile);check(bool(d),"new family decoded");for(auto p:{DecodeProfile::baseline_v1,DecodeProfile::status_observations_v2,DecodeProfile::administrative_observations_v3})check(decode(b,loc,{},p).error.code==Code::unsupported_type,"old profiles unchanged");
  for(std::size_t n=0;n<=b.size()+1;++n){if(n==b.size())continue;auto bad=b;bad.resize(n);check(!decode(bad,loc,{},profile),"malformed length");}
 }
 auto i=decode(observation('I'),loc,{},profile);check(std::get<NetOrderImbalance>(i.data->message).paired==UINT64_MAX,"full shares64");
 auto o=decode(observation('O'),loc,{},profile);check(std::get<DirectListingDiscovery>(o.data->message).near_time_raw==UINT64_MAX,"raw time64 no invented units");
 for(auto pair:{std::pair{'K',24U},std::pair{'J',19U},std::pair{'I',36U},std::pair{'O',20U}}){auto b=observation(pair.first);put(b,pair.second,2000000000,4);check(bool(decode(b,loc,{},profile)),"maximum Price4");put(b,pair.second,2000000001,4);check(decode(b,loc,{},profile).error.code==Code::invalid_value,"off-range Price4");}
}
void contextual(){
 auto c=context();std::uint64_t offset=0,ordinal=0;
 const auto apply=[&](const Bytes& b){auto r=c.apply(b,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},configuration().source.provenance);if(r.committed()){offset+=b.size()+2;++ordinal;}return r;};
 check(apply(system()).committed(),"session start");
 auto before=c.summary();check(!apply(observation('K')).committed()&&c.summary()==before,"unknown security failure atomic");check(apply(directory()).committed()&&apply(directory(2,"TWO     ")).committed(),"directories");
 for(char t:std::string_view{"KJIO"}){auto x=apply(observation(t));check(x.committed()&&x.record->normalization_version==4&&x.record->policy.decode_profile==profile,"v4 contract");check(x.record->integration==IntegrationClass::external_observation&&!x.record->before&&!x.record->after&&!x.record->price_ticks&&!x.record->quantity_lots,"not liquidity");check(x.record->source.provenance==configuration().source.provenance,"exact provenance");const auto kind=t=='K'?SemanticKind::ipo_quoting:t=='J'?SemanticKind::luld_collar:t=='I'?SemanticKind::imbalance:SemanticKind::direct_listing;check(x.record->kind==kind,"exact semantic classification");}
 auto bad=observation('K');put(bad,1,1,2);before=c.summary();check(!apply(bad).committed()&&c.summary()==before,"K requires global locate0");
 bad=observation('K');bad[23]=std::byte{'C'};before=c.summary();check(!apply(bad).committed()&&c.summary()==before,"K cancellation contradictory fields atomic");put(bad,19,0,4);put(bad,24,0,4);check(apply(bad).committed(),"cancel observation zero fields");
 for(char t:std::string_view{"KJIO"}){auto b=observation(t);text(b,t=='I'?28:11,"WRONG   ");before=c.summary();check(!apply(b).committed()&&c.summary()==before,"stock mismatch atomic");}
 check(c.orders().empty()&&c.matches().empty()&&c.summary().initialization_incomplete,"no order history invented");
}
void integration(){
 Harness h(configuration());h.setup();h.accept(add());const auto initial=state(h.reconstruction);auto counts=h.reconstruction.summary().native_counts;
 for(char t:std::string_view{"KJIO"}){auto s=h.process(observation(t,t=='I'?2:1));check(s.committed&&s.disposition==SourceDisposition::external_observation,"external receipt");check(!s.native_sequence&&state(h.reconstruction)==initial&&h.reconstruction.summary().native_counts==counts,"no native mutation");if(t=='K')check(s.book_index==0&&h.reconstruction.receipts().back().source.header.stock_locate.value()==0,"K symbol routing preserves source locate0");}
 auto second=h.process(observation('K',2));check(second.committed&&second.book_index==1&&state(h.reconstruction)==initial,"global K routes second stock without mutation");
 check(h.reconstruction.receipts().size()==9&&h.reconstruction.summary().context_committed==9,"source accounting");
 auto unknown=configuration();unknown.initialization.kind=InitialStateKind::unknown;check(!SyntheticReconstructor::create(unknown),"unknown init remains blocked");
}
void allocation(){
 gig::TrackedResource base;{auto c=context(&base);(void)c;}const auto sites=base.stats().attempts;check(sites==3&&base.stats().live_bytes==0,"reserve bounds");
 for(std::size_t i=0;i<sites;++i){gig::TrackedResource memory;memory.fail_after(i);auto c=configuration();check(!SourceContext::create(c.source,c.context_policy,&memory)&&memory.stats().live_bytes==0,"reached failure clean");}
 gig::TrackedResource memory;{Harness h(configuration(),&memory);h.setup();const auto initial=state(h.reconstruction);memory.fail_after(0);const auto attempts=memory.stats().attempts;for(char t:std::string_view{"KJIO"})check(h.process(observation(t)).committed,"allocation-free observation");check(memory.stats().attempts==attempts,"observations allocated zero times");memory.disable_failure();check(state(h.reconstruction)==initial,"no book changes");}check(memory.stats().live_bytes==0,"all storage clean");
 std::cout<<"auction_context_allocation_sites="<<sites<<" observation_allocations=0 sizeof_message="<<sizeof(Message)<<" sizeof_record="<<sizeof(DecodedRecord)<<'\n';
}
void restart(){
 Harness h(configuration());h.setup();for(char t:std::string_view{"KJIO"})h.accept(observation(t));auto code=number<gig::Digest>(std::string(64,'9'));Bytes bytes;
 const std::vector<Bytes> rows{system(),directory(),directory(2,"TWO     "),observation('K'),observation('J'),observation('I'),observation('O')};
 for(const auto& b:rows){bytes.push_back(static_cast<std::byte>(b.size()>>8));bytes.push_back(static_cast<std::byte>(b.size()&255));bytes.insert(bytes.end(),b.begin(),b.end());}
 auto cp=capture_checkpoint(h.reconstruction,bytes,code);check(bool(cp),"checkpoint capture");auto replay=restart_from_checkpoint(*cp.data,configuration(),bytes,code);check(replay&&state(*replay.data)==state(h.reconstruction)&&replay.data->receipts().size()==7,"deterministic replay");auto wrong=configuration();wrong.context_policy.decode_profile=DecodeProfile::administrative_observations_v3;check(!restart_from_checkpoint(*cp.data,wrong,bytes,code),"profile mismatch");
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
 case 'K':{const auto& k=std::get<IpoQuotingUpdate>(d.data->message);append(k.stock.view());auto at=encoded.size();encoded.resize(at+9);put(encoded,at,k.release_seconds,4);encoded[at+4]=static_cast<std::byte>(k.qualifier);put(encoded,at+5,k.price.value(),4);break;}
 case 'J':{const auto& j=std::get<LuldAuctionCollar>(d.data->message);append(j.stock.view());for(auto n:{j.reference.value(),j.upper.value(),j.lower.value(),j.extension}){auto at=encoded.size();encoded.resize(at+4);put(encoded,at,n,4);}break;}
 case 'I':{const auto& i=std::get<NetOrderImbalance>(d.data->message);for(auto n:{i.paired,i.imbalance}){auto at=encoded.size();encoded.resize(at+8);put(encoded,at,n,8);}encoded.push_back(static_cast<std::byte>(i.direction));append(i.stock.view());for(auto n:{i.far.value(),i.near.value(),i.reference.value()}){auto at=encoded.size();encoded.resize(at+4);put(encoded,at,n,4);}encoded.push_back(static_cast<std::byte>(i.cross_type));encoded.push_back(static_cast<std::byte>(i.variation));break;}
 case 'O':{const auto& o=std::get<DirectListingDiscovery>(d.data->message);append(o.stock.view());encoded.push_back(static_cast<std::byte>(o.eligible));for(auto n:{o.minimum.value(),o.maximum.value(),o.near.value()}){auto at=encoded.size();encoded.resize(at+4);put(encoded,at,n,4);}auto at=encoded.size();encoded.resize(at+8);put(encoded,at,o.near_time_raw,8);for(auto n:{o.lower.value(),o.upper.value()}){at=encoded.size();encoded.resize(at+4);put(encoded,at,n,4);}break;}
 default:throw std::runtime_error("unexpected oracle input");}
 std::cout<<"{\"ok\":true,\"wire\":\"";constexpr char hex[]="0123456789abcdef";for(auto v:encoded){auto n=std::to_integer<unsigned>(v);std::cout<<hex[n>>4]<<hex[n&15];}std::cout<<"\",\"origin\":"<<static_cast<unsigned>(d.data->provenance.origin)<<"}\n";
 }
}
}
int main(int argc,char** argv){try{check(argc==2,"mode required");const std::string_view mode=argv[1];if(mode=="wire")wire();else if(mode=="context")contextual();else if(mode=="integration")integration();else if(mode=="allocation")allocation();else if(mode=="restart")restart();else if(mode=="oracle")oracle();else if(mode=="context_oracle")context_oracle();else return 2;return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
