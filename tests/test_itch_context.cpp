#include "gig/itch/context.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace gig::itch;
namespace {
void check(bool value,const char* message){if(!value)throw std::runtime_error(message);}
std::vector<std::byte> payload(char type,std::uint16_t locate=1,std::uint64_t time=1){
    std::vector<std::byte> out(*expected_length(static_cast<std::uint8_t>(type)),std::byte{});out[0]=static_cast<std::byte>(type);
    out[1]=static_cast<std::byte>(locate>>8);out[2]=static_cast<std::byte>(locate&255);
    for(std::size_t i=0;i<6;++i){out[10-i]=static_cast<std::byte>(time&255);time>>=8;}return out;
}
void put(std::vector<std::byte>& p,std::size_t at,std::uint64_t value,std::size_t width){for(std::size_t i=0;i<width;++i){p[at+width-i-1]=static_cast<std::byte>(value&255);value>>=8;}}
void text(std::vector<std::byte>& p,std::size_t at,std::string_view value){for(char c:value)p[at++]=static_cast<std::byte>(c);}
SourceManifest manifest(){return {*SourceIdentity::make("synthetic-p1f").data,*SourceIdentity::make("session-A").data,{},Initialization::unknown};}
std::vector<std::byte> system(char code){auto p=payload('S',0);p[11]=static_cast<std::byte>(code);return p;}
std::vector<std::byte> directory(std::uint16_t locate=1,std::string_view symbol="ABC     "){
    auto p=payload('R',locate);text(p,11,symbol);p[19]=std::byte{'Q'};p[20]=std::byte{'N'};put(p,21,100,4);text(p,25,"NC  P N1N");p[38]=std::byte{'N'};return p;
}
std::vector<std::byte> add(std::uint64_t ref=101,std::uint32_t qty=10,std::uint32_t price=100,std::uint16_t locate=1,std::string_view symbol="ABC     ",bool attributed=false){
    auto p=payload(attributed?'F':'A',locate);put(p,11,ref,8);p[19]=std::byte{'B'};put(p,20,qty,4);text(p,24,symbol);put(p,32,price,4);if(attributed)text(p,36,"MPID");return p;
}
std::vector<std::byte> reduce(char type,std::uint64_t ref,std::uint32_t qty=1,std::uint64_t match=1,std::uint16_t locate=1){
    auto p=payload(type,locate);put(p,11,ref,8);if(type!='D')put(p,19,qty,4);
    if(type=='E'||type=='C')put(p,23,match,8);
    if(type=='C'){p[31]=std::byte{'Y'};put(p,32,101,4);}return p;
}
std::vector<std::byte> replace(std::uint64_t old,std::uint64_t next,std::uint32_t qty,std::uint32_t price=101){auto p=payload('U');put(p,11,old,8);put(p,19,next,8);put(p,27,qty,4);put(p,31,price,4);return p;}
struct Harness {
    SourceContext context;std::uint64_t offset{},ordinal{};
    explicit Harness(ContextPolicy policy={},std::pmr::memory_resource* resource=std::pmr::get_default_resource(),SourceManifest source=manifest()):context(make(policy,resource,std::move(source))){}
    static SourceContext make(ContextPolicy policy,std::pmr::memory_resource* r,SourceManifest source){auto x=SourceContext::create(std::move(source),policy,r);check(bool(x),"context create");return std::move(*x.data);}
    ContextResult apply(const std::vector<std::byte>& p,Provenance provenance={}){
        auto result=context.apply(p,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},provenance);
        if(result.committed()){offset+=p.size()+2;++ordinal;}return result;
    }
    void setup(){check(apply(system('O')).committed(),"O setup");check(apply(directory()).committed(),"R setup");}
};
void lifecycle(){
    Harness h;h.setup();check(h.apply(add()).committed(),"add101");check(h.apply(add(102,20)).committed(),"add102");
    auto r=h.apply(reduce('E',102,4,11));check(r.committed()&&r.record->before->remaining.value()==20&&r.record->after->remaining.value()==16,"identified nonhead execution");
    check(!r.record->observed_execution_price,"E price not falsely observed");
    check(h.apply(reduce('X',101,3)).committed(),"partial cancel");check(h.apply(reduce('D',101)).committed(),"delete");
    r=h.apply(replace(102,103,15));check(r.committed()&&r.record->before->reference.value()==102&&r.record->after->reference.value()==103,"replace identity");
    const auto s=h.context.summary();check(s.active_orders==1&&s.lifetime_orders==3,"retired retained");
    check(h.context.orders()[2].remaining.value()==15&&h.context.orders()[2].resting_price.value()==101,"golden final state");
    check(h.context.orders()[2].arrival.value()==h.ordinal-1,"new arrival annotation");
    auto prior=h.context.summary();r=h.apply(add(101));check(!r.committed()&&r.error.code==ContextCode::duplicate_reference&&h.context.summary()==prior,"no retired reuse");
    r=h.apply(reduce('E',103,15,12));check(r.committed()&&!r.record->after->active&&h.context.summary().active_orders==0,"full execution retires");
}
void identity(){
    Harness h;h.setup();auto a=add(1,10,100,1,"ABC     ",true);auto accepted=h.apply(a);check(accepted.committed(),"attributed add");
    check(h.apply(replace(1,2,5)).record->after->attribution->view()=="MPID","replace attribution inherited");
    const auto before=h.context.summary();
    for(auto bad:std::vector<std::vector<std::byte>>{add(2),reduce('E',999),reduce('E',2,6),reduce('X',2,6),reduce('X',2,5),replace(2,1,2),reduce('D',1),add(0),add(3,0)}){
        auto r=h.apply(bad);check(!r.committed()&&h.context.summary()==before,"invalid lifecycle atomic");
        check(h.context.orders()[1].remaining.value()==5,"quantity unchanged");
    }
    check(h.apply(directory(2,"XYZ     ")).committed(),"second symbol");
    check(h.apply(add(3,7,110,2,"XYZ     ")).committed(),"interleaved symbol");
    auto wrong=reduce('E',2,1,9,2);check(h.apply(wrong).error.code==ContextCode::stock_conflict,"wrong locate ownership");
    check(h.apply(add(4,1,100,1,"XYZ     ")).error.code==ContextCode::stock_conflict,"symbol conflict");
    check(h.apply(directory()).committed(),"identical directory idempotent");
    check(h.apply(directory(1,"DIFF    ")).error.code==ContextCode::directory_conflict,"conflicting directory");
    check(h.apply(directory(3,"        ")).error.field=="empty_stock","blank stock identity rejected");
    auto new_session=manifest();new_session.session=*SourceIdentity::make("session-B").data;
    Harness next({},std::pmr::get_default_resource(),new_session);next.setup();check(next.apply(add(1)).committed(),"new explicit session context ref namespace");
}
void observations(){
    Harness h;h.setup();h.apply(add(1,10));auto r=h.apply(reduce('C',1,2,17));
    check(r.committed()&&r.record->observed_execution_price->value()==101&&r.record->before->resting_price.value()==100,"C distinct prices");
    check(r.record->integration!=IntegrationClass::exact_candidate&&r.record->printable=='Y'&&r.record->price_ticks==100,"C no lossy full integration");
    auto p=payload('P');p[19]=std::byte{'B'};put(p,20,3,4);text(p,24,"ABC     ");put(p,32,100,4);put(p,36,18,8);
    auto q=payload('Q');text(q,19,"ABC     ");put(q,27,100,4);put(q,31,19,8);q[39]=std::byte{'O'};
    const auto live=h.context.summary().active_orders;
    r=h.apply(p);check(r.committed()&&r.record->kind==SemanticKind::trade_print,"hidden print distinct");
    r=h.apply(q);check(r.committed()&&r.record->kind==SemanticKind::cross_print,"zero cross observable");
    auto b=payload('B');put(b,11,18,8);r=h.apply(b);check(r.committed()&&r.record->kind==SemanticKind::broken_trade,"break explicit");
    check(h.context.summary().active_orders==live&&h.context.orders()[0].remaining.value()==8,"prints/correction no liquidity restoration");
    const auto before=h.context.summary();check(!h.apply(b).committed()&&h.context.summary()==before,"duplicate break atomic");
    put(b,11,999,8);check(h.apply(b).error.code==ContextCode::missing_match,"unknown match");
    put(b,11,19,8);check(!h.apply(b).committed(),"cross break unsupported referenced kind");
    check(h.apply(reduce('E',1,1,17)).error.code==ContextCode::duplicate_match,"duplicate match generation");
    auto u=payload('H');const auto x=h.apply(u);check(x.status==ContextStatus::unsupported&&!x.committed(),"unsupported outcome");
    auto unknown=std::vector<std::byte>{std::byte{255}};check(h.apply(unknown).status==ContextStatus::unsupported,"unknown outcome");
    check(h.context.summary()==before,"unsupported doesn't advance");
}
void policies(){
    Harness h;h.setup();h.apply(add(1));
    for(char code:std::string_view{"SQME"})check(h.apply(system(code)).committed(),"system lifecycle observation");
    check(h.context.summary().active_orders==1,"close markers never reset orders");check(h.apply(reduce('D',1)).committed(),"delete after end system hours");
    check(h.apply(system('C')).committed(),"end messages");check(!h.apply(system('O')).committed(),"no implicit new session");
    Harness complete;complete.setup();for(char c:std::string_view{"SQMEC"})complete.apply(system(c));
    const auto finished=complete.context.finish(ContextEnd::declared_source_complete);
    check(!finished.session_incomplete&&finished.source_complete&&finished.initialization_incomplete,"complete declared session distinct L3");
    auto s=h.context.finish(ContextEnd::bounded_prefix);check(s.initialization_incomplete&&!s.source_complete&&s.bounded_prefix,"bounded incomplete");
    check(!h.apply(system('O')).committed(),"finished no reopen");
    ContextPolicy p;p.require_monotonic_timestamps=true;p.require_intraday_timestamps=true;Harness clocks(p);clocks.setup();
    auto a=add();put(a,5,2,6);check(clocks.apply(a).committed(),"clock forward");
    auto before=clocks.context.summary();check(clocks.apply(add(2)).error.code==ContextCode::timestamp_policy&&clocks.context.summary()==before,"clock policy reject regression");
    put(a,5,86400000000000ULL,6);check(!clocks.apply(a).committed(),"intraday explicit cap");
    ContextPolicy permissive;permissive.require_lifecycle_order=false;Harness prefix(permissive);
    check(prefix.apply(directory()).committed()&&prefix.context.summary().initialization_incomplete,"unknown history inventory");
    auto max_time=add();put(max_time,5,(1ULL<<48)-1,6);check(prefix.apply(max_time).committed(),"raw48 time preserved default");
    auto malformed=add(2);malformed[19]=std::byte{'?'};check(prefix.apply(malformed).status==ContextStatus::source_invalid,"wire invalid distinct");
}
void limits(){
    ContextPolicy p;p.max_directories=1;p.max_lifetime_orders=1;p.max_matches=1;Harness h(p);h.setup();h.apply(add(1));h.apply(reduce('D',1));
    auto before=h.context.summary();auto r=h.apply(add(2));check(!r.committed()&&r.status==ContextStatus::resource_limit&&h.context.summary()==before,"retired limit no eviction");
    check(h.apply(directory(2,"XYZ     ")).status==ContextStatus::resource_limit,"directory cap");
    p.memory_budget_bytes=0;check(!SourceContext::create(manifest(),p),"byte budget preflight");
    p.max_directories=SIZE_MAX;check(!SourceContext::required_bytes(p),"checked capacity multiplication");
}
void allocation(){
    ContextPolicy p;p.max_directories=2;p.max_lifetime_orders=4;p.max_matches=4;
    gig::TrackedResource resource;
    for(std::size_t site=0;site<3;++site){resource.fail_after(site);auto r=SourceContext::create(manifest(),p,&resource);check(!r,"real allocation failure");check(resource.stats().live_bytes==0,"create rollback releases prior allocations");}
    resource.disable_failure();
    {
        Harness h(p,&resource);const auto stats=resource.stats();resource.fail_after(0);h.setup();h.apply(add(1));h.apply(reduce('E',1,1,1));h.apply(reduce('X',1,99));
        check(resource.stats()==stats,"all admission and failure paths allocation free");
        check(h.context.summary().reserved_bytes==stats.live_bytes,"reserved actual bytes");
    }
    check(resource.stats().live_bytes==0,"destruction releases all state");
    resource.disable_failure();
    auto original=SourceContext::create(manifest(),p,&resource);auto moved=std::move(*original.data);
    const auto before_move_test=resource.stats();resource.fail_after(0);
    check(!original.data->apply(system('O'),{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}}).committed(),"moved-from safe reject");
    check(resource.stats()==before_move_test,"moved-from no allocation");
    check(moved.apply(system('O'),{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}}).committed(),"move preserves context");
}
void provenance(){
    auto pinned=manifest();pinned.provenance.origin=Origin::synthetic;pinned.provenance.generator_seed=42;
    pinned.provenance.sha256=std::array<std::byte,32>{std::byte{7}};
    Harness h({},std::pmr::get_default_resource(),pinned);h.setup();
    auto good=pinned.provenance;good.source=pinned.source;
    auto r=h.apply(add(1),good);check(r.committed()&&r.record->source.provenance==good&&r.record->manifest==pinned,"provenance exact preservation");
    const auto before=h.context.summary();auto conflict=good;conflict.generator_seed=43;
    check(h.apply(add(2),conflict).error.code==ContextCode::provenance_conflict&&h.context.summary()==before,"seed contradiction atomic");
    conflict=good;conflict.source=*SourceIdentity::make("other-source").data;
    check(h.apply(add(2),conflict).error.code==ContextCode::provenance_conflict,"source contradiction");
    conflict=good;(*conflict.sha256)[0]=std::byte{8};check(!h.apply(add(2),conflict).committed(),"digest contradiction");
    r=h.apply(add(2));check(r.committed()&&!r.record->source.provenance.source&&!r.record->source.provenance.generator_seed,"missing raw provenance never invented");
    const auto pos=h.context.summary();const auto location=Location{ByteOffset{h.offset+1},ByteOffset{h.offset+3},RecordOrdinal{h.ordinal}};
    check(!h.context.apply(add(3),location).committed()&&h.context.summary()==pos,"physical gap no skip");
    ContextPolicy p;p.allow_equal_cancel=true;Harness equal(p);equal.setup();equal.apply(add(1));
    check(equal.apply(reduce('X',1,10)).record->after->active==false,"explicit equal cancel policy retires");
    p.max_matches=1;Harness matches(p);matches.setup();matches.apply(add(1));matches.apply(reduce('E',1,2,1));
    const auto previous=matches.context.summary();check(matches.apply(reduce('E',1,2,2)).status==ContextStatus::resource_limit&&matches.context.summary()==previous&&matches.context.orders()[0].remaining.value()==8,"match capacity atomic before reduce");
}
void numeric(){
    Harness h;h.setup();auto r=h.apply(add(UINT64_MAX,UINT32_MAX,2000000000));check(r.committed(),"unsigned maxima");
    check(h.apply(reduce('E',UINT64_MAX,UINT32_MAX,UINT64_MAX)).committed(),"exact max reduction");
    ContextPolicy p;p.price_quantum=3;p.lot_size=7;Harness units(p);units.setup();r=units.apply(add(1,10,100));
    check(r.committed()&&r.status==ContextStatus::integration_ineligible&&!r.record->price_ticks&&!r.record->quantity_lots,"off unit not rounded");
    check(r.record->source.header.timestamp.value()==1&&r.record->manifest.source==manifest().source,"source preservation");
    check(r.record->normalization_version==1&&r.record->policy==p,"complete normalization policy provenance");
    auto invalid=units.context.finish(static_cast<ContextEnd>(255));check(invalid.finish_error==ContextCode::invalid_config&&!units.context.summary().finished,"invalid finish atomic");
    ContextPolicy edge;edge.first_location={ByteOffset{UINT64_MAX-14},ByteOffset{UINT64_MAX-12},RecordOrdinal{UINT64_MAX}};
    auto limit=SourceContext::create(manifest(),edge);check(bool(limit),"near max create");
    auto end_record=limit.data->apply(system('O'),edge.first_location);check(end_record.committed(),"last ordinal and source extent valid");
    const auto edge_state=limit.data->summary();check(!limit.data->apply(system('S'),edge.first_location).committed()&&limit.data->summary()==edge_state,"exhausted cursor no wrap");
    edge.first_location.ordinal=RecordOrdinal{0};auto byte_edge=SourceContext::create(manifest(),edge);
    check(byte_edge.data->apply(system('O'),edge.first_location).committed(),"byte-only edge valid");
    check(byte_edge.data->apply(system('S'),edge.first_location).error.field=="cursor_exhausted","byte exhaustion independent of ordinal");
    edge.first_location={ByteOffset{0},ByteOffset{2},RecordOrdinal{UINT64_MAX}};auto ordinal_edge=SourceContext::create(manifest(),edge);
    check(ordinal_edge.data->apply(system('O'),edge.first_location).committed(),"ordinal-only edge valid");
    check(ordinal_edge.data->apply(system('S'),edge.first_location).error.field=="cursor_exhausted","ordinal exhaustion independent of byte end");
    auto s=units.context.finish(ContextEnd::declared_source_complete);check(s.initialization_incomplete&&s.session_incomplete,"complete framing never grants L3 eligibility");
}
}
int main(int argc,char** argv){try{const std::string_view name=argc>1?argv[1]:"all";
    if(name=="all"||name=="lifecycle")lifecycle();
    if(name=="all"||name=="identity")identity();
    if(name=="all"||name=="observations")observations();
    if(name=="all"||name=="policies")policies();
    if(name=="all"||name=="limits")limits();
    if(name=="all"||name=="allocation")allocation();
    if(name=="all"||name=="numeric")numeric();
    if(name=="all"||name=="provenance")provenance();
    std::cout<<"context "<<name<<" passed; OrderState="<<sizeof(OrderState)<<" MatchState="<<sizeof(MatchState)<<" NormalizedRecord="<<sizeof(NormalizedRecord)<<'\n';return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
