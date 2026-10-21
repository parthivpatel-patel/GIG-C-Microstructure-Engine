#include <iostream>
#include <string_view>
#include "gig/memory/tracked_resource.hpp"
#include "fixtures/synthetic/replay_events.hpp"
using namespace gig;using namespace gig::fixtures;
namespace {
std::size_t checks=0,failures=0;
void check(bool ok,const char* name) {++checks;if (!ok) {++failures;std::cerr << "FAIL " << name << '\n';}}
ReplayEngine engine(ReplayConfig config=replay_config(),std::pmr::memory_resource* r=std::pmr::get_default_resource()) {return take(ReplayEngine::create(rules(),config,{},r));}
void accepted(ReplayEngine& e,const MarketEvent& event) {must(e.apply(event));check(!e.book().check_invariants(),"accepted replay invariants");}
void stopped(ReplayEngine& e,const MarketEvent& event,ErrorCode code) {
    const auto before=state(e.book());const auto cursor=e.cursor(event.metadata.scope.data->stream);const auto records=e.journal_size();
    const auto result=e.apply(event);check(result.code==code && e.needs_recovery(),"strict continuity/order stop");
    check(state(e.book())==before && e.cursor(event.metadata.scope.data->stream)==cursor && e.journal_size()==records,"stop preserves book/cursor/journal");
    check(!e.depth(1),"blocked replay cannot publish healthy snapshot");
}
}
int main(int argc,char** argv) {
    if (argc!=2) return 2;
    try {
        const std::string_view group{argv[1]};
        if (group=="emit") {auto e=engine();canonical_workflow(e);std::cout << state(e) << '\n';return 0;}
        if (group=="config") {
            auto config=replay_config(2);config.streams.items[1]->rank=0;
            check(!ReplayEngine::create(rules(),config),"duplicate ranks rejected");
            config=replay_config();config.initial_state=InitialBookState::requires_snapshot;auto e=engine(config);
            check(e.needs_recovery() && e.apply(replay_event(add(1),0,0)).code==ErrorCode::recovery_required,"explicit initial-state requirement");
            must(e.recover(replay_recovery(1,0,0)));check(!e.needs_recovery() && e.book().order_count()==2,"initial snapshot establishes state");
            config=replay_config();config.streams.count=9;check(!ReplayEngine::create(rules(),config),"stream capacity");
            config=replay_config();config.max_journal_records=0;check(!ReplayEngine::create(rules(),config),"journal limit");
            config=replay_config();config.ordering=static_cast<OrderingPolicy>(255);check(!ReplayEngine::create(rules(),config),"order-policy enum");
            config=replay_config();config.ordering=OrderingPolicy::timestamp_rank;check(!ReplayEngine::create(rules(),config),"common clock required");
            config=replay_config();config.streams.items[0]->scope.unit=static_cast<SequenceUnit>(255);check(!ReplayEngine::create(rules(),config),"sequence unit enum");
        } else if (group=="continuity") {
            auto e=engine();accepted(e,replay_event(add(1),0,0));check(e.cursor(number<StreamId>(1))->expected.value()==1,"next expected");
            stopped(e,replay_event(add(2),0,1),ErrorCode::sequence_duplicate);

        } else if (group=="gaps") {
            auto e=engine(replay_config(1,10));stopped(e,replay_event(add(1),11,0),ErrorCode::sequence_gap);
            auto r=engine(replay_config(1,10));stopped(r,replay_event(add(1),9,0),ErrorCode::sequence_regression);
            auto x=engine(replay_config(1,UINT64_MAX));accepted(x,replay_event(add(1),UINT64_MAX,0));
            check(x.cursor(number<StreamId>(1))->exhausted,"max sequence accepted once without wrapping");stopped(x,replay_event(add(2),0,1),ErrorCode::sequence_exhausted);
            auto bad=engine();auto malformed=replay_event(add(1,Side::buy,100,0),0,0);const auto before=state(bad);
            check(bad.apply(malformed).code==ErrorCode::invalid_range && state(bad)==before && !bad.needs_recovery(),"invalid payload is not consumed");accepted(bad,replay_event(add(1),0,0));
        } else if (group=="subevents") {
            auto e=engine();auto a=replay_event(add(1),0,0);a.metadata.subevent_count=3;accepted(e,a);
            auto b=replay_event(CancelOrder{number<OrderId>(1),number<QuantityLots>(1)},0,1);b.metadata.subevent_index=1;b.metadata.subevent_count=3;accepted(e,b);
            auto c=replay_event(Trade{TradePrint{number<PriceTicks>(100),number<QuantityLots>(1),{}}},0,2);c.metadata.subevent_index=2;c.metadata.subevent_count=3;accepted(e,c);
            check(e.cursor(number<StreamId>(1))->expected.value()==1 && e.book().remaining()==9,"message advances only at final subevent");
            auto gap=engine();accepted(gap,a);stopped(gap,c,ErrorCode::sequence_gap);
            auto mismatch=engine();accepted(mismatch,a);b.metadata.subevent_count=2;stopped(mismatch,b,ErrorCode::inconsistent_metadata);
            auto config=replay_config();config.streams.items[0]->scope.unit=SequenceUnit::event;auto per_event=engine(config);
            a=replay_event(add(1),0,0);a.metadata.scope.data->unit=SequenceUnit::event;accepted(per_event,a);
            b=a;b.metadata.subevent_count=2;check(per_event.apply(b).code==ErrorCode::inconsistent_metadata,"event sequences cannot carry message bundle");
        } else if (group=="multistream") {
            auto e=engine(replay_config(2));accepted(e,replay_event(add(1),0,0,1));accepted(e,replay_event(add(2),0,1,2));
            auto duplicate=replay_event(add(1),1,2,2);auto before=state(e);check(e.apply(duplicate).code==ErrorCode::duplicate && state(e)==before,"shared order namespace across sequence streams");
            accepted(e,replay_event(CancelOrder{number<OrderId>(1),CancelAll{}},1,2,2));check(!e.book().find(number<OrderId>(1)),"cross-channel identified reference");
            auto backwards=replay_event(add(3),1,3,1);backwards.metadata.event_time.data->nanoseconds=number<EventTimestamp>(-100);accepted(e,backwards);
            stopped(e,replay_event(add(4),2,2,1),ErrorCode::ordering_error);
            auto config=replay_config(2);config.ordering=OrderingPolicy::timestamp_rank;config.timestamp_clock=Available<Identity>::known(text("fixture-clock"));
            auto timed=engine(config);accepted(timed,replay_event(add(1),0,0,1));accepted(timed,replay_event(add(2),0,1,2));
            auto later=replay_event(add(3),1,2,1);later.metadata.event_time.data->nanoseconds=number<EventTimestamp>(1);accepted(timed,later);
            auto tie=engine(config);accepted(tie,replay_event(add(1),0,0,2));stopped(tie,replay_event(add(2),0,1,1),ErrorCode::ordering_error);
            auto wrong_clock=engine(config);auto wrong=replay_event(add(1),0,0);wrong.metadata.event_time.data->clock.data->domain=ClockDomain::venue_utc_unsynchronized;
            stopped(wrong_clock,wrong,ErrorCode::unsupported);
        } else if (group=="filtering") {
            auto config=replay_config();auto other=rules();other.instrument=number<InstrumentId>(2);must(config.additional_instruments.append(other));
            auto e=engine(config);auto filtered=replay_event(add(1),0,0);filtered.metadata.instrument=Available<InstrumentId>::known(other.instrument);accepted(e,filtered);
            check(e.book().order_count()==0 && e.journal_size()==1 && e.cursor(number<StreamId>(1))->expected.value()==1,"filtered event advances continuity and is journaled");
            stopped(e,replay_event(add(2),2,1),ErrorCode::sequence_gap);
            auto valid=engine(config);accepted(valid,filtered);accepted(valid,replay_event(add(1),1,1));check(valid.book().order_count()==1,"filter before book dispatch, after sequence checks");
            auto invalid=engine(config);filtered.payload=add(1,static_cast<Side>(255));check(invalid.apply(filtered).code==ErrorCode::invalid_enum && invalid.journal_size()==0,"filtered payload still validated under its own rules");
        } else if (group=="reset") {
            auto e=engine(replay_config(2));accepted(e,replay_event(add(1),0,0));
            const BookSession next{text("next-session"),1};auto plan=restart_plan(2,next,5);plan.items[1]->first_sequence=number<SequenceNumber>(9);
            auto reset=replay_event(BookReset{ResetReason::session_start,1},1,1);const auto before=state(e);
            check(e.apply(reset).code==ErrorCode::unsupported && state(e)==before,"reset requires explicit starts");
            auto incomplete=plan;incomplete.items[1].reset();incomplete.count=1;check(e.reset(reset,incomplete).code==ErrorCode::missing_metadata && state(e)==before,"all stream starts required atomically");
            must(e.reset(reset,plan));check(e.book().order_count()==0 && e.book().session()==next && e.book().ledger().discarded==10,"reset removes old state with ledger");
            accepted(e,replay_event(add(1),5,2,1,next));accepted(e,replay_event(add(2),9,3,2,next));
            stopped(e,replay_event(add(3),6,4,1),ErrorCode::session_boundary);
            auto pending=engine();auto a=replay_event(add(1),0,0);a.metadata.subevent_count=3;accepted(pending,a);
            auto mid=replay_event(BookReset{ResetReason::manual,1},0,1);mid.metadata.subevent_count=3;mid.metadata.subevent_index=1;
            const auto p_before=state(pending);check(pending.reset(mid,restart_plan(1,next)).code==ErrorCode::session_boundary && state(pending)==p_before,"reset cannot discard pending subevents");
        } else if (group=="recovery") {
            auto e=engine(replay_config(2));accepted(e,replay_event(add(1),0,0));stopped(e,replay_event(add(2),2,1,2),ErrorCode::sequence_gap);
            auto recovery=replay_recovery(2,10,10);auto incomplete=recovery;
            auto& partial=std::get<Snapshot>(incomplete.payload);partial.boundaries.items[1].reset();partial.boundaries.count=1;
            const auto before=state(e);check(e.recover(incomplete).code==ErrorCode::missing_metadata && state(e)==before,"recovery requires all streams");
            must(e.recover(recovery));check(!e.needs_recovery() && e.book().order_count()==2 && e.cursor(number<StreamId>(2))->expected.value()==11,"recovery commits book and all cursors");
            check(e.book().find(number<OrderId>(8))->priority<e.book().find(number<OrderId>(7))->priority,"snapshot supplies FIFO, not aggregate inference");
            accepted(e,replay_event(CancelOrder{number<OrderId>(7),CancelAll{}},11,11,2));
            auto rewind=replay_recovery(2,9,12);const auto recovered=state(e);check(e.recover(rewind).code==ErrorCode::sequence_regression && state(e)==recovered,"recovery cannot rewind committed boundary");
            auto aggregate=replay_recovery(2,12,12);auto& snap=std::get<Snapshot>(aggregate.payload);snap.kind=SnapshotKind::aggregated;snap.orders={};
            check(e.recover(aggregate).code==ErrorCode::unsupported && state(e)==recovered,"aggregate recovery forbidden");
            auto bad_count=replay_recovery(2,12,12);auto& bound=*std::get<Snapshot>(bad_count.payload).boundaries.items[1];bound.sequence=number<SequenceNumber>(11);bound.last_subevent=1;bound.subevent_count=2;
            check(e.recover(bad_count).code==ErrorCode::inconsistent_metadata && state(e)==recovered,"recovery cannot alter observed message extent");
            const BookSession next{text("new-session"),1};must(e.recover(replay_recovery(2,0,12,next)));check(e.book().session()==next && e.cursor(number<StreamId>(1))->expected.value()==1,"explicit new-session snapshot boundary");
            auto initial=replay_config(1,10);initial.initial_state=InitialBookState::requires_snapshot;auto start=engine(initial);
            must(start.recover(replay_recovery(1,9,0)));check(start.cursor(number<StreamId>(1))->expected.value()==10,"initial snapshot immediately precedes declared capture boundary");
        } else if (group=="atomicity") {
            std::size_t failure_sites=0;
            for (int scenario=0;scenario<5;++scenario) {
                bool success=false;
                for (std::size_t site=0;site<128;++site) {
                    TrackedResource r;
                    {
                        auto e=engine(replay_config(),&r);must(e.apply(replay_event(add(1),0,0)));must(e.apply(replay_event(add(2,Side::sell,200),1,1)));
                        if (scenario==1) {auto error=e.apply(replay_event(add(99),5,2));check(error.code==ErrorCode::sequence_gap,"prepare recovery fault fixture");}
                        const auto before=state(e);r.fail_after(site);Error error;
                        if (scenario==0) error=e.apply(replay_event(add(3,Side::buy,101),2,2));
                        else if (scenario==1) error=e.recover(replay_recovery(1,10,10));
                        else if (scenario==2) error=e.reset(replay_event(BookReset{ResetReason::manual,1},2,2),restart_plan(1,{text("new-session"),1}));
                        else if (scenario==3) {auto out=e.canonical();error=out.error;}
                        else {auto out=e.depth(10);error=out.error;}
                        r.disable_failure();check(!e.book().check_invariants(),"replay allocator-failure invariants");
                        if (error) {check(error.code==ErrorCode::resource_exhausted && state(e)==before,"book/cursors/journal/order key/diagnostic atomicity");++failure_sites;}
                        else success=true;
                    }
                    check(r.stats().live_blocks==0 && r.stats().live_bytes==0,"replay allocations released on destruction");
                    if (success) break;
                }
                check(success,"eventually exhaust replay allocation sites");
            }
            auto limited=replay_config();limited.max_journal_records=1;auto e=engine(limited);accepted(e,replay_event(add(1),0,0));const auto before=state(e);
            check(e.apply(replay_event(add(2),1,1)).code==ErrorCode::capacity && state(e)==before,"journal resource limit is atomic");
            std::cout << "replay allocation failure sites=" << failure_sites << '\n';
        } else if (group=="canonical") {
            TrackedResource a_resource,b_resource;
            auto a=engine(replay_config(),&a_resource),b=engine(replay_config(),&b_resource);canonical_workflow(a);canonical_workflow(b);
            check(state(a)==state(b),"canonical equivalence across allocations and repeated replay");
            check(a.book().order_count()==2 && a.book().remaining()==30 && a.journal_size()==11,"independently expected canonical-workflow final state");
            const auto text_out=state(a);check(text_out.find("quoted;:token\\\"")!=std::string::npos && text_out.find("parent;artifact:1")!=std::string::npos,"owned provenance and delimiter-bearing tokens preserved");
            auto c=engine();auto event=replay_event(add(1),0,0);event.metadata.provenance.generator_seed=Available<std::uint64_t>::known(1730);accepted(c,event);
            auto d=engine();accepted(d,replay_event(add(1),0,0));check(state(c)!=state(d) && state(c.book())==state(d.book()),"canonical journal distinguishes provenance with same book");
            auto snapshot=take(a.depth(1));check(snapshot.run_id==replay_config().run_id && snapshot.journal_prefix==a.journal_size() && snapshot.book.revision==a.book().revision(),"snapshot has resolvable run/journal/revision lineage");
        } else if (group=="batch") {
            auto e=engine();const std::array<MarketEvent,3> input{replay_event(add(1),0,0),replay_event(add(2),2,1),replay_event(add(3),3,2)};
            auto result=e.run(input);check(!result && result.accepted==1 && result.failed_input_index==1 && e.journal_size()==1,"batch stops at first error");
            auto good=engine();const std::array<MarketEvent,2> valid{replay_event(add(1),0,0),replay_event(add(2),1,1)};
            result=good.run(valid);check(bool(result) && result.accepted==2 && !result.failed_input_index && good.book().remaining()==20,"batch deterministic dispatch");
        } else return 2;
    } catch (const std::exception& e) {std::cerr << "unexpected test exception: " << e.what() << '\n';return 1;}
    std::cout << argv[1] << ": " << checks << " checks, " << failures << " failures\n";
    return failures==0?0:1;
}
