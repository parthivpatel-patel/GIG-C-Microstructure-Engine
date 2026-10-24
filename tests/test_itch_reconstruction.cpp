#include "support/itch_reconstruction_fixture.hpp"
#include "support/itch_input_adapter_checks.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <iostream>
#include <string_view>
using namespace gig::itch;
using namespace gig::itch::test;
namespace {
void initialization(){
    input_adapter_checks();
    // Every encoded invalid kind must fail before the first allocation, including
    // a caller that shifts both declared boundaries to an arbitrary file prefix.
    for(unsigned raw=0;raw<=255;++raw){
        if(raw==static_cast<unsigned>(InitialStateKind::authored_empty))continue;
        auto candidate=config();candidate.initialization.kind=static_cast<InitialStateKind>(raw);
        gig::TrackedResource memory;memory.fail_after(0);
        const auto refused=SyntheticReconstructor::create(candidate,&memory);
        check(!refused&&refused.error.code==gig::ErrorCode::inconsistent_metadata&&memory.stats().attempts==0,"all non-authored states rejected before allocation");
    }
    for(const auto ordinal:{std::uint64_t{1},UINT64_MAX}){
        auto candidate=config();candidate.context_policy.first_location={ByteOffset{14},ByteOffset{16},RecordOrdinal{ordinal}};
        candidate.initialization.boundary=candidate.context_policy.first_location;
        check(!SyntheticReconstructor::create(candidate),"matching arbitrary boundaries do not authenticate initial state");
    }

    for(auto kind:{InitialStateKind::unknown,InitialStateKind::complete_seed,InitialStateKind::incomplete_history,InitialStateKind::invalid,static_cast<InitialStateKind>(255)}){auto c=config();c.initialization.kind=kind;check(!SyntheticReconstructor::create(c),"incomplete/seed/invalid initialization blocked");}
    auto c=config();c.initialization.complete_history=false;check(!SyntheticReconstructor::create(c),"history declaration required");
    c=config();c.initialization.boundary={ByteOffset{14},ByteOffset{16},RecordOrdinal{1}};check(!SyntheticReconstructor::create(c),"arbitrary boundary blocked");
    c=config();c.source.initialization=Initialization::unknown;check(!SyntheticReconstructor::create(c),"S/O alone cannot establish empty state");
    c=config();c.initialization.session=source_id("wrong-session");check(!SyntheticReconstructor::create(c),"scope proof exact");
    c=config();c.source.provenance.origin=Origin::observed;check(!SyntheticReconstructor::create(c),"observed source excluded");
    c=config();c.source.provenance.generator_seed=9;check(!SyntheticReconstructor::create(c),"seed contradictory");
    c=config();c.source.provenance.generator_seed.reset();check(!SyntheticReconstructor::create(c),"missing generator seed blocked");
    c=config();c.context_policy.price_quantum=0;const auto zero_units=SyntheticReconstructor::create(c);check(!zero_units&&zero_units.error.code==gig::ErrorCode::inconsistent_metadata,"zero context units are configuration error, not allocation failure");
    c=config();c.context_policy.memory_budget_bytes=0;const auto bad_context=SyntheticReconstructor::create(c);check(!bad_context&&bad_context.error.code==gig::ErrorCode::inconsistent_metadata,"invalid context budget classified as configuration error");
    c=config();c.bindings[0]->stock.bytes[0]='\1';const auto bad_symbol=SyntheticReconstructor::create(c);check(!bad_symbol&&bad_symbol.error.code==gig::ErrorCode::inconsistent_metadata,"nonprintable binding symbol rejected");

    c=config();(*c.source.provenance.sha256)[0]=std::byte{1};check(!SyntheticReconstructor::create(c),"digest contradictory");
    c=config();c.context_policy.price_quantum=2;check(!SyntheticReconstructor::create(c),"context/full-rule units consistent");
    c=config();c.bindings[1]->derived_stream=c.bindings[0]->derived_stream;check(!SyntheticReconstructor::create(c),"duplicate derived stream rejected");
    c=config();c.book_count=1;c.bindings[1].reset();auto single=reconstructor(c);check(single.engine(0)&&!single.engine(1),"one-book bounded profile");
    c=config();c.initialization.version=identity("2");Harness versioned(c);versioned.setup();versioned.accept(add(700));check(versioned.book().last_metadata()->provenance.lineage.items[0]->version==identity("2"),"declared fixture/generator contract version preserved");
    Harness h;h.setup();check(h.reconstruction.summary().initialization_verified,"authored empty proof accepted");check(h.reconstruction.context().summary().initialization_incomplete,"P1F evidence scope remains unchanged");
    h.accept(add(999));
    gig::Snapshot snapshot{gig::SnapshotKind::order_level,gig::SnapshotCoverage::complete,0,{},{},{}};
    for(std::uint64_t i=0;i<64;++i)check(!snapshot.orders.append({{number<gig::OrderId>(1000+i),gig::Side::buy,number<gig::PriceTicks>(100),number<gig::QuantityLots>(1)},i}),"64-order native snapshot append");
    const auto metadata=*h.book().last_metadata();check(!snapshot.boundaries.append({*metadata.scope.data,*metadata.sequence.data,0,1}),"native snapshot scope");
    auto native=gig::OrderBook::create(h.book().rules(),h.book().session(),{128,128,16});check(bool(native),"native snapshot target");
    check(!native.data->recover({metadata,snapshot},h.book().session())&&native.data->order_count()==64&&native.data->remaining()==64,"complete 64-order native recovery supported independently of adapter seed");
    for(std::uint64_t i=0;i<64;++i)check(native.data->find(number<gig::OrderId>(1000+i))->priority==i,"native snapshot exact authored priority");
    check(snapshot.orders.append({{number<gig::OrderId>(1064),gig::Side::buy,number<gig::PriceTicks>(100),number<gig::QuantityLots>(1)},64}).code==gig::ErrorCode::capacity,"65th order cannot append");
    snapshot.orders.count=65;check(bool(native.data->recover({metadata,snapshot},h.book().session()))&&native.data->order_count()==64&&native.data->remaining()==64,"forged 65-count snapshot rejected atomically");

}
void golden(){
    Harness h;h.setup();h.accept(add(101,10));h.accept(add(102,20));
    const auto first=h.book().find(number<gig::OrderId>(101));const auto second=h.book().find(number<gig::OrderId>(102));check(first&&second&&first->priority<second->priority,"FIFO add order");
    h.accept(reduce('E',102,4,1));check(h.book().find(number<gig::OrderId>(101))->order.quantity.value()==10,"nonhead execution leaves head");
    check(h.book().find(number<gig::OrderId>(102))->priority==second->priority,"partial execute keeps priority");
    h.accept(reduce('X',101,3));check(h.book().find(number<gig::OrderId>(101))->priority==first->priority,"partial cancel keeps priority");
    h.accept(reduce('D',101));h.accept(replace(102,103,15));
    check(!h.book().find(number<gig::OrderId>(101))&&!h.book().find(number<gig::OrderId>(102)),"retired absent");
    const auto remaining=h.book().find(number<gig::OrderId>(103));check(remaining&&remaining->order.quantity.value()==15&&remaining->order.price_ticks.value()==101&&remaining->priority>second->priority,"literal final identity/quantity/price/newpriority");
    const gig::QuantityLedger expected{30,10,4,0,0,15,16,45,30};check(h.book().ledger()==expected,"independent six-step ledger arithmetic");
    check(h.book().remaining()==15&&h.book().revision()==6&&h.reconstruction.engine(0)->journal_size()==6,"golden revisions and conservation");
    check(h.reconstruction.context().orders()[2].reference.value()==103&&h.reconstruction.context().orders()[2].remaining.value()==15,"context/native final agreement");
    check(!h.book().check_invariants(),"native invariants");
    const auto before=state(h.reconstruction);const auto context_before=h.reconstruction.context().summary();
    check(!h.process(add(101)).committed,"retired lifetime ID reuse rejected");check(state(h.reconstruction)==before&&h.reconstruction.context().summary()==context_before,"reuse rejection joint atomicity");
    Harness attributed;attributed.setup();attributed.accept(add(1,9,100,1,'B',true));attributed.accept(replace(1,2,7,100));check(attributed.reconstruction.context().orders()[1].attribution->view()=="MPID","U retains source attribution");
    attributed.accept(reduce('E',2,7,7));check(attributed.book().order_count()==0&&attributed.reconstruction.context().summary().active_orders==0,"full execute retires both states");
}
void observations(){
    Harness disabled;disabled.setup();disabled.accept(add(1));const auto before=state(disabled.reconstruction);const auto context_before=disabled.reconstruction.context().summary();
    auto blocked=disabled.process(reduce('C',1,2,1));check(!blocked.committed&&blocked.native_error.code==gig::ErrorCode::unsupported,"C opt-in required");check(state(disabled.reconstruction)==before&&disabled.reconstruction.context().summary()==context_before,"disabled C does not consume match or order");
    auto c=config();c.allow_c_book_only=true;Harness h(c);h.setup();h.accept(add(1));h.accept(reduce('C',1,2,1,1,123,'N'));
    check(h.book().remaining()==8,"C book-only decrement at resting price");const auto& raw=std::get<OrderExecutedWithPrice>(h.reconstruction.receipts().back().source.message);check(raw.execution_price.value()==123&&raw.printable=='N',"actual execution price/printable retained");
    check(h.book().find(number<gig::OrderId>(1))->order.price_ticks.value()==100,"resting price distinct");
    const auto native=state(h.reconstruction);const auto journal=h.reconstruction.engine(0)->journal_size();
    h.accept(trade(2));h.accept(cross(3));h.accept(broken(2));check(state(h.reconstruction)==native&&h.reconstruction.engine(0)->journal_size()==journal,"P Q B no displayed liquidity or journals");
    check(h.reconstruction.context().matches()[1].broken,"B correction ledger only");
    const auto accepted=h.reconstruction.context().summary();check(!h.process(broken(3)).committed&&h.reconstruction.context().summary()==accepted,"Q-origin B explicitly unsupported");
    Harness closing;closing.setup();closing.accept(add(8));for(char marker:std::string_view{"SQMEC"})closing.accept(system(marker));check(closing.book().remaining()==10,"S observations never reset native book");const auto complete=closing.reconstruction.finish(ContextEnd::declared_source_complete);check(complete.input_complete&&!closing.reconstruction.context().summary().session_incomplete,"container and local lifecycle complete");
}
void multisymbol(){
    Harness h;h.setup();h.accept(add(1,10,100));h.accept(add(2,20,200,2,'S'));h.accept(reduce('X',1,3));h.accept(reduce('E',2,4,77,2));
    check(h.book().remaining()==7&&h.book(1).remaining()==16,"separate symbol quantities");check(h.reconstruction.summary().native_counts==std::array<std::uint64_t,2>{2,2},"independent contiguous derived counts");
    check(h.reconstruction.engine(0)->book().last_metadata()->sequence.data->value()==1&&h.reconstruction.engine(1)->book().last_metadata()->sequence.data->value()==1,"native sequence ordinal gaps ignored");
    check(h.book().last_metadata()->capture_ordinal.data==5&&h.book(1).last_metadata()->capture_ordinal.data==6,"global source capture ordinal exact");
    check(!h.book().last_metadata()->event_time.data&&!h.book().last_metadata()->receive_time.data,"raw time of day not invented UTC");
    const auto before=state(h.reconstruction);auto collision=h.process(add(1,1,200,2,'S'));check(!collision.committed&&collision.context_error.code==ContextCode::duplicate_reference,"global source identity namespace across symbols");check(state(h.reconstruction)==before,"cross-symbol duplicate no contamination");
    Harness unknown;unknown.setup();auto third=directory(3,"OTHER   ");const auto accepted=unknown.reconstruction.context().summary();check(!unknown.process(third).committed&&unknown.reconstruction.context().summary()==accepted,"unknown routing blocks before directory commit");
}
void numeric(){
    check(price4_to_ticks(Price4{12345},{1,10000}).data->value()==12345,"price exact canonical scale");check(price4_to_ticks(Price4{100},{1,100}).data->value()==1,"price decimal scale independent arithmetic");
    check(!price4_to_ticks(Price4{101},{1,100})&&price4_to_ticks(Price4{101},{1,100}).error.code==gig::ErrorCode::off_unit,"off tick rejected");
    check(shares_to_lots(30,{3,2}).data->value()==20,"rational lot exact");check(!shares_to_lots(1,{3,2}),"off lot rejected");
    check(price4_to_ticks(Price4{0},{1,10000}).data->value()==0&&shares_to_lots(0,{1,1}).data->value()==0,"conversion zero preserved for domain validation");
    check(!price4_to_ticks(Price4{1},{0,1})&&!shares_to_lots(1,{1,0}),"invalid rational denominator/numerator");
    check(shares_to_lots(UINT64_MAX,{UINT64_MAX,UINT64_MAX}).data->value()==UINT64_MAX,"cancel before multiplication at max");
    check(shares_to_lots(UINT64_MAX,{1,2}).error.code==gig::ErrorCode::overflow,"quantity multiply overflow");check(!price4_to_ticks(Price4{2000000000},{1,UINT64_MAX}),"price intermediate overflow rejected");
    Harness h;h.setup();h.accept(add(UINT64_MAX,UINT32_MAX,2000000000));check(h.book().find(number<gig::OrderId>(UINT64_MAX))->order.quantity.value()==UINT32_MAX,"unsigned maximum ID and source quantity");h.accept(reduce('E',UINT64_MAX,UINT32_MAX,UINT64_MAX));check(h.book().remaining()==0,"maximum exact full execution");
    auto c=config();c.context_policy.price_quantum=10;c.context_policy.lot_size=5;for(auto& b:c.bindings){b->rules.tick_size={1,1000};b->rules.lot_size={5,1};}Harness off(c);off.setup();const auto before=state(off.reconstruction);check(!off.process(add(1,11,101)).committed&&state(off.reconstruction)==before&&off.reconstruction.context().summary().active_orders==0,"off units joint rejection");
    Harness zero;zero.setup();check(!zero.process(add(1,10,0)).committed&&zero.book().order_count()==0,"zero price rule rejected before joint commit");
    c=config();c.initialization.fixture=identity(std::string(128,'f'));Harness long_token(c);long_token.setup();const auto long_context=long_token.reconstruction.context().summary();check(!long_token.process(add(1)).committed&&long_token.book().order_count()==0&&long_token.reconstruction.context().summary()==long_context,"overlong derived source identity rejected without truncation");

}
class ReentrantResource final : public std::pmr::memory_resource {
public:
    SyntheticReconstructor* owner{};bool armed{},called{},rejected{},finish_unchanged{};
private:
    void* do_allocate(std::size_t bytes,std::size_t alignment) override {
        if(armed&&owner){armed=false;called=true;const auto before=owner->summary();const auto raw=system();const auto attempt=owner->process(raw,{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}});rejected=!attempt.committed&&attempt.native_error.field=="reentrant.process";finish_unchanged=owner->finish(ContextEnd::declared_source_complete)==before;}
        return std::pmr::get_default_resource()->allocate(bytes,alignment);
    }
    void do_deallocate(void* pointer,std::size_t bytes,std::size_t alignment)override{std::pmr::get_default_resource()->deallocate(pointer,bytes,alignment);}
    bool do_is_equal(const std::pmr::memory_resource& other)const noexcept override{return this==&other;}
};
void accounting(const SyntheticReconstructor& r){const auto s=r.summary();check(s.considered==s.native_committed+s.external_observations+s.rejected+(s.pending?1U:0U),"disjoint considered-record accounting");check(s.context_committed==s.native_committed+s.external_observations&&s.context_committed==r.context().summary().accepted_records,"context accepted prefix accounting");}
void atomicity(){
    ReentrantResource resource;{Harness guarded(config(),&resource);guarded.setup();resource.owner=&guarded.reconstruction;resource.armed=true;guarded.accept(add(900));check(resource.called&&resource.rejected&&resource.finish_unchanged,"allocator reentry cannot mutate or finish owned context");accounting(guarded.reconstruction);}resource.owner=nullptr;

    Harness h;h.setup();h.accept(add(1,10,100));h.accept(add(2,10,100,1,'S'));check(h.book().best_bid()->price_ticks==h.book().best_ask()->price_ticks,"locked book allowed");
    const auto before=state(h.reconstruction);const auto context_before=h.reconstruction.context().summary();auto crossed=h.process(add(3,1,99,1,'S'));check(!crossed.committed,"crossed native add rejected");accounting(h.reconstruction);check(h.reconstruction.summary().rejected==1&&!h.reconstruction.summary().pending,"semantic failure classified rejected, not pending");check(state(h.reconstruction)==before&&h.reconstruction.context().summary()==context_before&&h.reconstruction.receipts().size()==5,"native rejection preserves context/journal/receipts");
    auto changed=add(4,1,101,1,'S');check(h.process(changed).disposition==SourceDisposition::pending_identity_mismatch,"pending rejected record cannot be skipped");
    Harness replace_cross;replace_cross.setup();replace_cross.accept(add(1,10,100));replace_cross.accept(add(2,10,110,1,'S'));const auto prior=state(replace_cross.reconstruction);const auto ctx=replace_cross.reconstruction.context().summary();check(!replace_cross.process(replace(1,3,10,111)).committed&&state(replace_cross.reconstruction)==prior&&replace_cross.reconstruction.context().summary()==ctx,"crossing U preserves original identity/priority in both states");
}
void allocation(){
    // Direct native regression isolates the empty unordered-map sentinel defect:
    // the final node insertion previously allocated buckets after FIFO/level transfer.
    std::size_t direct_sites=0;
    Harness donor;donor.setup();donor.accept(add(42));
    const gig::MarketEvent event{*donor.book().last_metadata(),gig::AddOrder{number<gig::OrderId>(42),gig::Side::buy,number<gig::PriceTicks>(100),number<gig::QuantityLots>(10)}};
    {gig::TrackedResource tracked;auto native=gig::OrderBook::create(donor.book().rules(),donor.book().session(),{},&tracked);check(bool(native),"direct native baseline create");const auto attempts=tracked.stats().attempts;check(!native.data->apply(event),"direct native baseline add");direct_sites=tracked.stats().attempts-attempts;}
    for(std::size_t site=0;site<direct_sites;++site){gig::TrackedResource tracked;{auto native=gig::OrderBook::create(donor.book().rules(),donor.book().session(),{},&tracked);check(bool(native),"direct native sweep create");tracked.fail_after(site);const auto failure=native.data->apply(event);tracked.disable_failure();check(failure.code==gig::ErrorCode::resource_exhausted,"direct native first-add failure injected");check(native.data->order_count()==0&&native.data->remaining()==0&&native.data->revision()==0&&native.data->ledger()==gig::QuantityLedger{}&&!native.data->check_invariants(),"direct first-add failure leaves no transferred FIFO/level/index/ledger state");check(!native.data->apply(event)&&native.data->order_count()==1&&native.data->remaining()==10,"direct first-add retry exactly once");}check(tracked.stats().live_bytes==0,"direct native first-add sweep no leak");}
    std::size_t create_sites=0;{gig::TrackedResource resource;{auto made=SyntheticReconstructor::create(config(),&resource);check(bool(made),"create baseline");create_sites=resource.stats().attempts;}check(resource.stats().live_bytes==0,"create baseline release");}
    for(std::size_t site=0;site<create_sites;++site){gig::TrackedResource resource;resource.fail_after(site);auto made=SyntheticReconstructor::create(config(),&resource);check(!made&&resource.stats().live_bytes==0,"create actual failure rollback");}
    std::size_t add_sites=0,replace_sites=0;
    const auto sweep=[&](bool replacement){
        std::size_t sites=0;
        {gig::TrackedResource resource;Harness h(config(),&resource);h.setup();if(replacement)h.accept(add(1));const auto attempts=resource.stats().attempts;h.accept(replacement?replace(1,2,7,110):add(1));sites=resource.stats().attempts-attempts;}
        check(sites>0,"native mutation has real allocation sites");
        for(std::size_t site=0;site<sites;++site){gig::TrackedResource resource;{Harness h(config(),&resource);h.setup();if(replacement)h.accept(add(1));const auto before=state(h.reconstruction);const auto context_before=h.reconstruction.context().summary();const auto receipts=h.reconstruction.receipts().size();const auto native_count=h.reconstruction.summary().native_counts;const auto cursor_before=h.reconstruction.engine(0)->cursor(h.reconstruction.config().bindings[0]->derived_stream);const auto bytes=replacement?replace(1,2,7,110):add(1);resource.fail_after(site);const auto failed=h.process(bytes);resource.disable_failure();check(!failed.committed,"injected native failure observed");check(h.reconstruction.engine(0)->cursor(h.reconstruction.config().bindings[0]->derived_stream)==cursor_before,"native rejection preserves exact replay cursor");accounting(h.reconstruction);check(h.reconstruction.summary().pending&&h.reconstruction.summary().rejected==0,"resource failure pending disjoint from semantic reject");if(!(state(h.reconstruction)==before&&h.reconstruction.context().summary()==context_before&&h.reconstruction.receipts().size()==receipts&&h.reconstruction.summary().native_counts==native_count)){std::cerr<<"fault stage="<<(replacement?"replace":"add")<<" site="<<site<<" state_same="<<(state(h.reconstruction)==before)<<" context_same="<<(h.reconstruction.context().summary()==context_before)<<" receipts="<<h.reconstruction.receipts().size()<<" expected="<<receipts<<" counts_same="<<(h.reconstruction.summary().native_counts==native_count)<<" native_error="<<static_cast<unsigned>(failed.native_error.code)<<':'<<failed.native_error.field<<'\n';throw std::runtime_error("every native allocation rejection is joint atomic");}check(h.process(bytes).committed,"same exact record resource retry once");check(h.reconstruction.receipts().size()==receipts+1&&h.reconstruction.summary().context_committed==context_before.accepted_records+1,"retry no duplicate commit");accounting(h.reconstruction);}check(resource.stats().live_bytes==0,"failure sweep no leak");}
        return sites;
    };
    add_sites=sweep(false);replace_sites=sweep(true);
    gig::TrackedResource resource;{Harness h(config(),&resource);h.setup();h.accept(add(1,20));h.accept(add(2));h.accept(add(3));h.accept(reduce('X',1,1));h.accept(reduce('X',1,1));const auto attempts=resource.stats().attempts;resource.fail_after(0);h.accept(reduce('E',1,1,1));h.accept(reduce('X',1,1));h.accept(trade(2));check(resource.stats().attempts==attempts,"armed final native/context/receipt commits make no allocation");resource.disable_failure();const auto committed=h.reconstruction.summary();const auto before=state(h.reconstruction);resource.fail_after(0);check(!h.reconstruction.engine(0)->canonical(),"query allocation failure visible");resource.disable_failure();check(h.reconstruction.summary()==committed&&state(h.reconstruction)==before,"query failure does not uncommit accepted event");}check(resource.stats().live_bytes==0,"armed test release");
    std::cout<<"allocation_sites direct_native_first_add="<<direct_sites<<" create="<<create_sites<<" native_add="<<add_sites<<" native_replace="<<replace_sites<<"; armed_noalloc_native_E_X_external=3\n";
}
void budgets(){
    auto c=config();c.receipt_budget_bytes=sizeof(SourceReceipt)*c.max_source_records-1;check(!SyntheticReconstructor::create(c),"receipt preflight byte budget");
    c=config();c.max_source_records=4;Harness source(c);source.setup();source.accept(add(1));const auto before=state(source.reconstruction);check(!source.process(add(2)).committed&&state(source.reconstruction)==before&&source.reconstruction.receipts().size()==4,"source cap explicit no silent eviction");accounting(source.reconstruction);check(source.reconstruction.summary().unconsidered_record,"cap+1 source is explicitly unconsidered");check(!source.reconstruction.finish(ContextEnd::declared_source_complete).input_complete,"cap+1 cannot masquerade as full source completion");
    c=config();c.context_policy.max_lifetime_orders=1;Harness lifetime(c);lifetime.setup();lifetime.accept(add(1));lifetime.accept(reduce('D',1));check(!lifetime.process(add(2)).committed&&lifetime.book().order_count()==0,"retired reference cap retained");
    c=config();c.bindings[0]->max_journal_records=1;Harness journal(c);journal.setup();journal.accept(add(1));const auto ctx=journal.reconstruction.context().summary();check(!journal.process(reduce('X',1,1)).committed&&journal.book().remaining()==10&&journal.reconstruction.context().summary()==ctx,"journal cap preserves joint prefix");
    c=config();c.bindings[0]->limits={1,1,1};Harness active(c);active.setup();active.accept(add(1));check(!active.process(add(2)).committed&&active.book().order_count()==1,"active cap no drop");
    c=config();c.context_policy.max_matches=1;Harness matches(c);matches.setup();matches.accept(add(1));matches.accept(reduce('E',1,1,1));
    const auto match_context=matches.reconstruction.context().summary();const auto match_book=state(matches.reconstruction);
    check(matches.reconstruction.context().matches().size()==1,"exact match cap accepted");
    const auto match_failure=matches.process(reduce('E',1,1,2));
    check(!match_failure.committed&&match_failure.disposition==SourceDisposition::resource_rejected&&matches.reconstruction.context().summary()==match_context&&state(matches.reconstruction)==match_book&&matches.book().remaining()==9,"match cap+1 preserves native and context prefix");accounting(matches.reconstruction);
    c=config();c.bindings[0]->limits.max_levels=1;c.bindings[0]->limits.max_snapshot_depth=1;Harness levels(c);levels.setup();levels.accept(add(1,10,100));
    const auto level_context=levels.reconstruction.context().summary();const auto level_book=state(levels.reconstruction);
    check(levels.book().best_bid()->price_ticks.value()==100,"exact level cap accepted");
    const auto level_failure=levels.process(add(2,10,101));
    check(!level_failure.committed&&level_failure.native_error.code==gig::ErrorCode::capacity&&levels.reconstruction.context().summary()==level_context&&state(levels.reconstruction)==level_book&&levels.book().order_count()==1,"level cap+1 preserves native and context prefix");accounting(levels.reconstruction);
    gig::TrackedResource tiny(std::pmr::get_default_resource(),64);check(!SyntheticReconstructor::create(config(),&tiny)&&tiny.stats().live_bytes==0,"hard shared PMR budget enforced");
}
void restart(){
    const std::vector<std::vector<std::byte>> bytes{system(),directory(),directory(2,"TWO     "),add(101),add(201,20,200,2,'S'),reduce('E',101,3,9),replace(201,202,7,201,2),trade(10),broken(10)};
    for(std::size_t boundary=0;boundary<=bytes.size();++boundary){Harness first_run;Harness replay;for(std::size_t i=0;i<boundary;++i){first_run.accept(bytes[i]);replay.accept(bytes[i]);}check(state(first_run.reconstruction)==state(replay.reconstruction)&&first_run.reconstruction.summary()==replay.reconstruction.summary()&&first_run.reconstruction.context().summary()==replay.reconstruction.context().summary(),"fresh replay exact authenticated fixture prefix");const auto stop=first_run.reconstruction.finish(ContextEnd::bounded_prefix);check(stop.finished&&!stop.input_complete&&stop.eligibility==ReconstructionEligibility::stopped_at_valid_prefix,"bounded finish explicit incomplete");check(!first_run.process(system()).committed,"finished cannot resume in place");}
    Harness pending;pending.setup();check(!pending.process(reduce('D',999)).committed,"unknown order pending");const auto stopped=pending.reconstruction.finish(ContextEnd::declared_source_complete);check(!stopped.input_complete,"pending failure cannot declare complete source");
}
}
int main(int argc,char** argv){try{const std::string_view name=argc>1?argv[1]:"all";
#define RUN(group) if(name=="all"||name==#group)group()
RUN(initialization);RUN(golden);RUN(observations);RUN(multisymbol);RUN(numeric);RUN(atomicity);RUN(allocation);RUN(budgets);RUN(restart);
#undef RUN
std::cout<<"reconstruction "<<name<<" passed\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
