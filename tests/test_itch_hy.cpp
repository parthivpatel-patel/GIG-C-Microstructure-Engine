#include "gig/itch/restart.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "tests/support/itch_reconstruction_fixture.hpp"
#include "gig/itch/binary_file.hpp"
#include <iostream>
#include <sstream>
using namespace gig::itch;
using namespace gig::itch::test;
namespace {
using Bytes=std::vector<std::byte>;
constexpr auto profile=DecodeProfile::status_observations_v2;
constexpr Location wire_location{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}};
Bytes status(char type,char action='T',std::uint16_t locate=1,std::string_view symbol="TEST    "){
 auto b=payload(type,locate);text(b,11,symbol);b[19]=static_cast<std::byte>(action);if(type=='H'){b[20]=std::byte{' '};text(b,21,"T1  ");}return b;
}
SourceManifest manifest(){auto c=config();return c.source;}
ContextPolicy policy(){auto p=config().context_policy;p.decode_profile=profile;return p;}
SourceContext context(std::pmr::memory_resource* memory=std::pmr::get_default_resource()){auto c=SourceContext::create(manifest(),policy(),memory);check(bool(c),"HY context factory");return std::move(*c.data);}
struct ContextHarness {
 SourceContext c;std::uint64_t offset{},ordinal{};
 explicit ContextHarness(std::pmr::memory_resource* r=std::pmr::get_default_resource()):c(context(r)){}
 ContextResult apply(const Bytes& b){auto x=c.apply(b,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},manifest().provenance);if(x.committed()){offset+=b.size()+2;++ordinal;}return x;}
 void setup(){check(apply(system()).committed(),"HY O");check(apply(directory()).committed(),"HY R");}
};
std::string hex(std::span<const std::byte> bytes){constexpr char digits[]="0123456789abcdef";std::string out;for(auto b:bytes){auto x=std::to_integer<unsigned>(b);out+=digits[x>>4];out+=digits[x&15];}return out;}
std::string hex(std::string_view s){return hex(std::as_bytes(std::span(s.data(),s.size())));}
void wire(){
 for(char t:std::string_view{"HY"})for(char a:t=='H'?std::string_view{"HPQT"}:std::string_view{"012"}){
  auto b=status(t,a);put(b,1,65535,2);put(b,3,65535,2);put(b,5,(1ULL<<48)-1,6);auto p=manifest().provenance;
  auto r=decode(b,{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}},p,profile);check(bool(r)&&r.data->header.timestamp.value()==(1ULL<<48)-1&&r.data->header.stock_locate.value()==65535&&r.data->provenance==p,"exact header provenance");
  check(!decode(b)&&decode(b).error.code==Code::unsupported_type,"legacy classification preserved");
  for(std::size_t size=0;size<=b.size()+1;++size)if(size!=b.size()){auto bad=b;bad.resize(size);check(!decode(bad,wire_location,p,profile),"HY length rejection");}
 }
 auto h=status('H');h[20]=std::byte{'?'};text(h,21,"Z9?!");auto d=decode(h,wire_location, {},profile);check(d&&std::get<StockTradingAction>(d.data->message).reserved=='?'&&std::get<StockTradingAction>(d.data->message).reason.view()=="Z9?!","opaque Alpha preserved without invented enums");
 for(char t:std::string_view{"HY"})for(unsigned n=0;n<256;++n){auto b=status(t,t=='H'?'T':'0');b[19]=static_cast<std::byte>(n);auto r=decode(b,wire_location, {},profile);const auto allowed=t=='H'?std::string_view{"HPQT"}:std::string_view{"012"};check(bool(r)==(allowed.find(static_cast<char>(n))!=std::string_view::npos),"exhaustive status enum");}
 for(std::size_t field:std::array<std::size_t,3>{11,20,21}){auto b=h;b[field]=std::byte{0};check(!decode(b,wire_location, {},profile),"Alpha control rejected");}
 check(!decode(h,wire_location, {},static_cast<DecodeProfile>(255)),"invalid decode profile");auto p=policy();p.decode_profile=static_cast<DecodeProfile>(255);check(!SourceContext::create(manifest(),p),"invalid context profile");
}
void contextual(){
 ContextHarness h;check(!h.apply(status('H')).committed(),"no implicit lifecycle start");h.setup();const auto before=h.c.summary();
 for(auto b:{status('H','T',2),status('Y','0',1,"WRONG   "),status('H','T',0)})check(!h.apply(b).committed()&&h.c.summary()==before,"identity validation atomic");
 for(char t:std::string_view{"HY"}){auto r=h.apply(status(t,t=='H'?'H':'2'));check(r.committed()&&r.record->integration==IntegrationClass::external_observation&&!r.record->before&&!r.record->after&&!r.record->price_ticks&&!r.record->quantity_lots,"observations only");check(r.record->normalization_version==2&&r.record->policy.decode_profile==profile&&r.record->source.provenance==manifest().provenance,"versioned exact provenance");}
 check(h.c.orders().empty()&&h.c.matches().empty()&&h.c.summary().initialization_incomplete,"no identities or initial state invented");
 auto bad=status('H');bad[19]=std::byte{'?'};const auto accepted=h.c.summary();check(h.apply(bad).status==ContextStatus::source_invalid&&h.c.summary()==accepted,"invalid status no cursor advance");
 check(h.apply(directory(2,"TWO     ")).committed()&&h.apply(status('Y','1',2,"TWO     ")).committed(),"two symbol associations");
 for(char c:std::string_view{"SQMEC"}){check(h.apply(system(c)).committed(),"unchanged system scope");}
 check(!h.apply(status('H')).committed(),"no status after session end");
 auto closed=h.c.finish(ContextEnd::declared_source_complete);check(closed.source_complete&&closed.initialization_incomplete,"complete local session not L3 proof");
}
Bytes framed(const std::vector<Bytes>& rows,bool terminal=false){Bytes out;for(const auto& r:rows){out.push_back(static_cast<std::byte>(r.size()>>8));out.push_back(static_cast<std::byte>(r.size()&255));out.insert(out.end(),r.begin(),r.end());}if(terminal){out.push_back(std::byte{0});out.push_back(std::byte{0});}return out;}
void fragments(){
 const std::vector<Bytes> rows{system(),directory(),status('H'),status('Y','0')};auto bytes=framed(rows);bytes.push_back(std::byte{0});bytes.push_back(std::byte{25});bytes.push_back(std::byte{'H'});
 for(std::size_t chunk=1;chunk<=bytes.size();++chunk){auto f=BinaryFileFramer::create();auto c=context();check(bool(f),"framer create");std::size_t at=0;
  while(at<bytes.size()){const auto end=std::min(bytes.size(),at+chunk);while(at<end){auto r=f.data->feed(std::span(bytes).subspan(at,end-at));at+=r.consumed;check(!r.error,"fragment parse");if(r.frame)check(c.apply(r.frame->payload,r.frame->location).committed(),"fragment context");check(r.consumed>0,"progress");}}
  auto end=f.data->finish(EndKind::bounded_prefix);check(!end.error&&end.residual_bytes==3&&f.data->position().value()==bytes.size()&&c.summary().accepted_records==4,"partial-frame consumption counter regression");}
}
void integration(){
 auto c=config();c.context_policy.decode_profile=profile;Harness h(c);h.setup();h.accept(add());const auto before=state(h.reconstruction);auto counts=h.reconstruction.summary().native_counts;
 for(auto b:{status('H','H'),status('Y','1'),status('H','T',2,"TWO     ")}){auto s=h.process(b);check(s.committed&&s.disposition==SourceDisposition::external_observation,"external receipt");check(state(h.reconstruction)==before&&h.reconstruction.summary().native_counts==counts,"no native mutation sequence journal or FIFO effects");}
 check(h.reconstruction.summary().external_observations==6&&h.reconstruction.summary().context_committed==7&&h.reconstruction.receipts().size()==7,"every source counted");
 const auto& receipt=h.reconstruction.receipts().back();check(receipt.source.type=='H'&&receipt.source.header.stock_locate.value()==2&&!receipt.native_sequence&&receipt.book_index==1,"exact routed receipt");
 auto unknown=config();unknown.context_policy.decode_profile=profile;unknown.initialization.kind=InitialStateKind::unknown;check(!SyntheticReconstructor::create(unknown),"no relaxed initialization");
}
void allocation(){
 gig::TrackedResource baseline;{auto c=context(&baseline);(void)c;}auto sites=baseline.stats().attempts;check(sites==3&&baseline.stats().live_bytes==0,"context reserve baseline");
 for(std::size_t i=0;i<sites;++i){gig::TrackedResource r;r.fail_after(i);auto c=SourceContext::create(manifest(),policy(),&r);check(!c&&c.error.code==Code::resource_exhausted&&r.stats().live_bytes==0,"real allocation failure cleanup");}
 gig::TrackedResource r;{ContextHarness h(&r);h.setup();const auto before=h.c.summary();r.fail_after(0);const auto attempts=r.stats().attempts;auto p=h.c.prepare(status('H'),{ByteOffset{h.offset},ByteOffset{h.offset+2},RecordOrdinal{h.ordinal}},manifest().provenance);check(p&&h.c.summary()==before,"prepare nonmutating");check(h.c.commit(std::move(*p.prepared)).committed()&&r.stats().attempts==attempts,"allocation free commit");check(!h.c.commit(std::move(*p.prepared)).committed(),"token one shot");}check(r.stats().live_bytes==0,"context cleanup");
 gig::TrackedResource native;{auto c=config();c.context_policy.decode_profile=profile;Harness h(c,&native);h.setup();auto before=state(h.reconstruction);native.fail_after(0);auto attempts=native.stats().attempts;check(h.process(status('Y','2')).committed&&native.stats().attempts==attempts,"native observation allocates nothing");native.disable_failure();check(state(h.reconstruction)==before,"armed allocation isolation");}check(native.stats().live_bytes==0,"native cleanup");
 std::cout<<"hy_creation_allocation_fault_sites="<<sites<<" observation_allocations=0\n";
}
void restart(){
 auto c=config();c.context_policy.decode_profile=profile;Harness h(c);std::vector<Bytes> rows{system(),directory(),directory(2,"TWO     "),add(),status('H','P'),status('Y','2')};for(const auto& b:rows)h.accept(b);
 const auto bytes=framed(rows);const auto code=number<gig::Digest>(std::string(64,'7'));auto cp=capture_checkpoint(h.reconstruction,bytes,code);check(bool(cp),"HY capture");auto replay=restart_from_checkpoint(*cp.data,c,bytes,code);check(replay&&state(*replay.data)==state(h.reconstruction)&&replay.data->receipts().size()==6,"deterministic HY restart");
 auto legacy=c;legacy.context_policy.decode_profile=DecodeProfile::baseline_v1;check(!restart_from_checkpoint(*cp.data,legacy,bytes,code),"profile bound to restart identity");
}
void decode_json(const Bytes& b,unsigned selected){const auto p=manifest().provenance;auto r=decode(b,wire_location,p,static_cast<DecodeProfile>(selected));
 if(!r){std::cout<<"{\"ok\":false,\"code\":"<<static_cast<unsigned>(r.error.code)<<",\"offset\":"<<r.error.offset.value()<<",\"field\":\""<<r.error.field<<"\"}";return;}
 const auto& d=*r.data;std::cout<<"{\"ok\":true,\"type\":"<<static_cast<unsigned>(d.type)<<",\"locate\":"<<d.header.stock_locate.value()<<",\"tracking\":"<<d.header.tracking_number.value()<<",\"timestamp\":"<<d.header.timestamp.value()<<",\"stock\":\"";
 if(d.type=='H'){const auto& h=std::get<StockTradingAction>(d.message);std::cout<<hex(h.stock.view())<<"\",\"action\":"<<static_cast<unsigned char>(h.trading_state)+0U<<",\"reserved\":"<<static_cast<unsigned char>(h.reserved)+0U<<",\"reason\":\""<<hex(h.reason.view())<<'"';}
 else if(d.type=='Y'){const auto& y=std::get<RegShoRestriction>(d.message);std::cout<<hex(y.stock.view())<<"\",\"action\":"<<static_cast<unsigned char>(y.action)+0U<<",\"reserved\":null,\"reason\":null";}
 std::cout<<",\"origin\":"<<static_cast<unsigned>(d.provenance.origin)<<",\"seed\":"<<*d.provenance.generator_seed<<"}";
}
void oracle(){std::string line;while(std::getline(std::cin,line)){std::istringstream in(line);char mode;unsigned option;in>>mode>>option;std::string token;std::uint64_t offset=0,ordinal=0;ContextPolicy pol=policy();pol.require_monotonic_timestamps=(option&1U)!=0;pol.require_intraday_timestamps=(option&2U)!=0;auto ctx=SourceContext::create(manifest(),pol);bool first=true;std::cout<<'[';
 while(in>>token){Bytes b;for(std::size_t i=0;i<token.size();i+=2)b.push_back(static_cast<std::byte>(std::stoul(token.substr(i,2),nullptr,16)));if(!first)std::cout<<',';first=false;
  if(mode=='D'){decode_json(b,option);continue;}
  auto r=ctx.data->apply(b,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},manifest().provenance);if(r.committed()){offset+=b.size()+2;++ordinal;}
  std::cout<<"{\"status\":"<<static_cast<unsigned>(r.status)<<",\"code\":"<<static_cast<unsigned>(r.error.code)<<",\"source_code\":"<<static_cast<unsigned>(r.error.source_error.code)<<",\"accepted\":"<<ctx.data->summary().accepted_records<<",\"offset\":"<<offset<<",\"directories\":"<<ctx.data->directories().size()<<",\"orders\":"<<ctx.data->orders().size()<<",\"matches\":"<<ctx.data->matches().size()<<",\"kind\":"<<(r.record?static_cast<int>(r.record->kind):-1)<<",\"normalization\":"<<(r.record?r.record->normalization_version:0)<<",\"integration\":"<<(r.record?static_cast<int>(r.record->integration):-1)<<",\"incomplete\":"<<(ctx.data->summary().initialization_incomplete?"true":"false")<<'}';
 }
 std::cout<<"]\n";}}
}
int main(int argc,char**argv){try{if(argc==2){const std::string_view mode=argv[1];if(mode=="oracle")oracle();else if(mode=="wire")wire();else if(mode=="context")contextual();else if(mode=="fragments")fragments();else if(mode=="integration")integration();else if(mode=="allocation")allocation();else if(mode=="restart")restart();else return 2;}else return 2;return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
