#pragma once
#include "gig/replay/replay.hpp"
#include "fixtures/synthetic/book_events.hpp"
namespace gig::fixtures {
inline ReplayConfig replay_config(std::size_t streams=1,std::uint64_t first=0) {
    RestartPlan plan;
    for (std::size_t i=0;i<streams;++i) must(plan.append({rules().venue,{number<StreamId>(i+1),book_session().session,0,SequenceUnit::message},text("phase1-synthetic"),text("1"),number<SequenceNumber>(first),static_cast<std::uint32_t>(i)}));
    ReplayConfig config{text("phase2-synthetic-run"),book_session(),plan};config.initial_state=InitialBookState::declared_empty;return config;
}
inline MarketEvent replay_event(EventPayload payload,std::uint64_t sequence,std::uint64_t ordinal,std::uint64_t stream=1,BookSession session=book_session()) {
    auto e=book_event(std::move(payload),sequence,stream,session);
    e.metadata.capture_ordinal=Available<std::uint64_t>::known(ordinal);
    e.metadata.source_record=Available<Identity>::known(text("replay:"+std::to_string(stream)+":"+std::to_string(sequence)+":"+std::to_string(ordinal)));
    return e;
}
inline std::string state(const ReplayEngine& replay) { auto out=take(replay.canonical());return {out.begin(),out.end()}; }
inline RestartPlan restart_plan(std::size_t streams,BookSession session,std::uint64_t first=0) {
    auto plan=replay_config(streams,first).streams;
    for (std::size_t i=0;i<plan.count;++i) plan.items[i]->scope={number<StreamId>(i+1),session.session,session.epoch,SequenceUnit::message};
    return plan;
}
inline MarketEvent replay_recovery(std::size_t streams,std::uint64_t source_sequence,std::uint64_t ordinal,BookSession session=book_session()) {
    auto e=recovery_event(source_sequence,session);e.metadata.capture_ordinal=Available<std::uint64_t>::known(ordinal);
    e.metadata.source_record=Available<Identity>::known(text("recovery:"+std::to_string(ordinal)));
    auto& s=std::get<Snapshot>(e.payload);
    for (std::size_t i=1;i<streams;++i) must(s.boundaries.append({{number<StreamId>(i+1),session.session,session.epoch,SequenceUnit::message},number<SequenceNumber>(source_sequence),0,1}));
    return e;
}
inline void canonical_workflow(ReplayEngine& e) {
    must(e.apply(replay_event(add(1),0,0)));must(e.apply(replay_event(add(2,Side::sell,200),1,1)));
    must(e.apply(replay_event(ReplaceOrder{number<OrderId>(1),number<OrderId>(1),Side::buy,number<PriceTicks>(101),number<QuantityLots>(15),ReplacePriority::lose},2,2)));
    must(e.apply(replay_event(CancelOrder{number<OrderId>(1),number<QuantityLots>(5)},3,3)));
    auto print=replay_event(Trade{TradePrint{number<PriceTicks>(101),number<QuantityLots>(2),{}}},4,4);
    must(print.metadata.provenance.lineage.append({TransformationKind::normalized,text("normalize"),text("1")}));
    must(print.metadata.provenance.parents.append({text("parent;artifact:1"),Available<Digest>::missing(MissingReason::unavailable)}));
    print.metadata.source_record=Available<Identity>::known(text("quoted;:token\\\""));must(e.apply(print));
    must(e.apply(replay_event(Quote{QuoteLevel{number<PriceTicks>(99),number<QuantityLots>(1)},QuoteLevel{number<PriceTicks>(201),number<QuantityLots>(2)}},5,5)));
    auto session=replay_event(SessionEvent{SessionAction::halt,Available<Identity>::missing(MissingReason::unavailable)},6,6);
    session.metadata.receive_time=Available<Timestamp<ReceiveTimestamp>>::missing(MissingReason::unavailable);must(e.apply(session));
    must(e.apply(replay_event(Trade{BookExecution{number<OrderId>(1),Side::buy,number<PriceTicks>(101),number<QuantityLots>(2)}},7,7)));
    must(e.apply(replay_event(CancelOrder{number<OrderId>(2),CancelAll{}},8,8)));
    const BookSession next{text("next-session"),1};must(e.reset(replay_event(BookReset{ResetReason::session_start,1},9,9),restart_plan(1,next)));
    must(e.recover(replay_recovery(1,0,10,next)));
}
} // namespace gig::fixtures
