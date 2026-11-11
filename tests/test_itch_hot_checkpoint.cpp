#include "gig/itch/hot_checkpoint.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_reconstruction_fixture.hpp"
#include <iostream>
using namespace gig::itch;using namespace gig::itch::test;
namespace {
std::size_t checks=0;void expect(bool v,const char*s){++checks;check(v,s);}
gig::Digest code(){return *gig::Digest::make(std::string(64,'b')).data;}
void compare(const SyntheticReconstructor&a,const SyntheticReconstructor&b){
 expect(state(a)==state(b),"native books/journals equal");expect(a.summary()==b.summary(),"source summary equal");
 auto x=a.context().checkpoint(),y=b.context().checkpoint();expect(bool(x)&&bool(y),"context images");expect(context_image_identity(*x.data).data==context_image_identity(*y.data).data,"full contexts equal");
}
void context_tokens(){
 auto cfg=config();auto made=SourceContext::create(cfg.source,cfg.context_policy);expect(bool(made),"context create");auto&c=*made.data;
 auto s=system();expect(c.apply(s,{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}}).committed(),"context system");
 auto dir=directory();const Location location{ByteOffset{s.size()+2},ByteOffset{s.size()+4},RecordOrdinal{1}};
 auto token=c.prepare(dir,location);expect(bool(token),"prepared donor token");auto image=c.checkpoint();auto digest=context_image_identity(*image.data);auto restored=SourceContext::restore(*image.data,cfg.source,cfg.context_policy,*digest.data);expect(bool(restored),"context hot import");
 auto wrong=restored.data->commit(std::move(*token.prepared));expect(!wrong.committed()&&wrong.error.code==ContextCode::invalid_prepared,"old owner token cannot cross hot restore");
 expect(c.commit(std::move(*token.prepared)).committed(),"original owner token remains valid");auto fresh=restored.data->prepare(dir,location);expect(bool(fresh)&&restored.data->commit(std::move(*fresh.prepared)).committed(),"new owner prepares fresh token");
 auto after=c.checkpoint(),other=restored.data->checkpoint();expect(context_image_identity(*after.data).data==context_image_identity(*other.data).data,"token identity not in deterministic state");
}
void reconstruction(){
 Harness h;h.setup();h.accept(add());h.accept(add(201,9,200,2));h.accept(reduce('E',101,2,77));h.accept(replace(101,103,8));h.accept(trade(88));h.accept(broken(88));
 auto image=h.reconstruction.hot_checkpoint();expect(bool(image),"joint hot checkpoint");auto trust=hot_identity(*image.data,code());expect(bool(trust),"owned independent hot identity");
 auto resumed=SyntheticReconstructor::restore_hot(*image.data,*trust.data,h.reconstruction.config(),code());expect(bool(resumed),"joint import without source replay");compare(h.reconstruction,*resumed.data);
 const std::vector<std::vector<std::byte>>suffix{reduce('X',103,2),reduce('D',201,0,0,2),add(301,4,150,2,'S'),trade(89),broken(89)};
 for(const auto&bytes:suffix){const auto loc=h.location();expect(h.process(bytes).committed,"original suffix");expect(resumed.data->process(bytes,loc).committed,"restored suffix");compare(h.reconstruction,*resumed.data);}
 auto corrupted=[&](auto modify){auto candidate=h.reconstruction.hot_checkpoint();auto expected=hot_identity(*candidate.data,code());modify(*candidate.data);expect(!SyntheticReconstructor::restore_hot(*candidate.data,*expected.data,h.reconstruction.config(),code()),"tampered joint image rejected");};
 corrupted([](auto&i){i.context.matches[0].broken=!i.context.matches[0].broken;});
 corrupted([](auto&i){i.context.orders[0].attribution=Text<4>{};});
 corrupted([](auto&i){++i.summary.external_observations;});
 corrupted([](auto&i){i.receipts[0].source.provenance.generator_seed=42;});
 corrupted([](auto&i){i.canonical[0]+='x';});
 corrupted([](auto&i){++i.engines[0]->book.ledger.added;});
 auto current=h.reconstruction.hot_checkpoint();auto expected=hot_identity(*current.data,code());auto wrong=h.reconstruction.config();wrong.run_id=identity("other-run");expect(!SyntheticReconstructor::restore_hot(*current.data,*expected.data,wrong,code()),"expected source configuration bound");
 auto forged=h.reconstruction.hot_checkpoint();for(auto&o:forged.data->context.orders)if(o.active){o.remaining=Shares{o.remaining.value()+1};break;}
 auto forged_trust=hot_identity(*forged.data,code());expect(!SyntheticReconstructor::restore_hot(*forged.data,*forged_trust.data,h.reconstruction.config(),code()),"context/native inconsistency independently rejected");
 const auto before=state(h.reconstruction);expect(!h.process(add(103)).committed,"retired reference cannot reappear");expect(state(h.reconstruction)==before,"source rejection leaves book unchanged");expect(!h.reconstruction.hot_checkpoint(),"held rejected source cannot masquerade as eligible image");
}
void allocation(){
 Harness h;h.setup();h.accept(add());h.accept(add(201,8,200,2));auto image=h.reconstruction.hot_checkpoint();auto trusted=hot_identity(*image.data,code());const auto before=state(h.reconstruction);
 gig::TrackedResource baseline;{auto restored=SyntheticReconstructor::restore_hot(*image.data,*trusted.data,h.reconstruction.config(),code(),&baseline);expect(bool(restored),"allocation baseline");}
 const auto count=baseline.stats().attempts;expect(count>10&&baseline.stats().live_bytes==0,"restore allocations measured");
 for(std::size_t n=0;n<count;++n){gig::TrackedResource memory;memory.fail_after(n);{auto failed=SyntheticReconstructor::restore_hot(*image.data,*trusted.data,h.reconstruction.config(),code(),&memory);expect(!failed&&failed.error.code==gig::ErrorCode::resource_exhausted,"every actual restore allocation failure is explicit");}expect(memory.stats().live_bytes==0,"failed restore releases memory");expect(state(h.reconstruction)==before,"failed isolated restore cannot mutate owner");}
 for(std::size_t n=0;n<12;++n){gig::TrackedResource memory;memory.fail_after(n);{auto copied=h.reconstruction.hot_checkpoint(&memory);if(!copied)expect(copied.error.code==gig::ErrorCode::resource_exhausted,"capture allocation failure classification");}expect(memory.stats().live_bytes==0&&state(h.reconstruction)==before,"capture failure clean and atomic");}
 std::cout<<"hot_itch_restore_allocation_failpoints="<<count<<'\n';
}
void capture_preflight(){
 auto cfg=config();cfg.context_policy.max_lifetime_orders=5000;auto made=SourceContext::create(cfg.source,cfg.context_policy);expect(bool(made),"large-context factory remains supported");auto&context=*made.data;std::uint64_t offset=0,ordinal=0;
 const auto apply=[&](const auto&bytes){const auto result=context.apply(bytes,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}});check(result.committed(),"large-context authored input");offset+=bytes.size()+2;++ordinal;};
 apply(system());apply(directory());for(std::uint64_t i=1;i<=4097;++i)apply(add(i));
 gig::TrackedResource memory;memory.fail_after(0);const auto image=context.checkpoint(&memory);expect(!image&&image.error.code==Code::record_limit,"hot vector limit enforced before any copy");expect(memory.stats().attempts==0,"oversized capture performs no allocation");expect(context.summary().active_orders==4097,"preflight cannot mutate accepted context");
}
}
int main(){try{context_tokens();reconstruction();allocation();capture_preflight();std::cout<<"checks="<<checks<<" failures=0\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
