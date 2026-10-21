#pragma once
#include <vector>
#include "fixtures/synthetic/replay_events.hpp"
namespace gig::fixtures {
struct Phase2Workload {
    std::uint64_t seed;
    std::vector<MarketEvent> adds,cancels,executions,replay;
    MarketEvent copy_snapshot;
    ReplayConfig config;
};
inline MarketEvent benchmark_frame(EventPayload payload,std::uint64_t ordinal,std::uint64_t seed,std::string_view scenario) {
    if (ordinal>static_cast<std::uint64_t>((INT64_MAX-10)/1000)) throw std::invalid_argument("fixture timestamp range");
    auto event=replay_event(std::move(payload),ordinal/2,ordinal,ordinal%2+1);
    event.metadata.provenance.generator_seed=Available<std::uint64_t>::known(seed);
    event.metadata.provenance.dataset.data->identity=text("phase2-benchmark-"+std::string(scenario));
    event.metadata.provenance.lineage.items[0]->operation=text("phase2-benchmark-generator-v1");
    event.metadata.source_record=Available<Identity>::known(text(std::string(scenario)+":"+std::to_string(ordinal)));
    event.metadata.event_time.data->nanoseconds=number<EventTimestamp>(static_cast<std::int64_t>(ordinal)*1000);
    event.metadata.receive_time.data->nanoseconds=number<ReceiveTimestamp>(static_cast<std::int64_t>(ordinal)*1000+10);
    return event;
}
inline Phase2Workload phase2_workload(std::size_t count,std::uint64_t seed) {
    if (count==0 || count>2048 || seed==0) throw std::invalid_argument("argument out of range");
    auto config=replay_config(2);config.run_id=text("phase2-benchmark-run");config.max_journal_records=count*2+4;
    for (std::size_t i=0;i<config.streams.count;++i) config.streams.items[i]->dataset=text("phase2-benchmark-replay");
    auto snapshot=benchmark_frame(recovery_event().payload,0,seed,"copy-snapshot");
    Phase2Workload w{seed,{},{},{},{},snapshot,config};
    w.adds.reserve(count);w.cancels.reserve(count);w.executions.reserve(count);w.replay.reserve(count*2);
    auto state=seed;
    const auto random=[&]() {state^=state<<13U;state^=state>>7U;state^=state<<17U;return state;};
    for (std::size_t i=0;i<count;++i) {
        const auto side=i%2==0?Side::buy:Side::sell;
        auto order=add(i+1,side,static_cast<std::int64_t>((side==Side::buy?100:200)+random()%16),10+random()%91);
        w.adds.push_back(benchmark_frame(order,i,seed,"add"));
        w.cancels.push_back(benchmark_frame(CancelOrder{order.order_id,CancelAll{}},count+i,seed,"cancel"));
        w.executions.push_back(benchmark_frame(Trade{BookExecution{order.order_id,order.side,order.price_ticks,number<QuantityLots>(1)}},count+i,seed,"execution"));
        w.replay.push_back(benchmark_frame(order,i,seed,"replay"));
    }
    for (std::size_t i=0;i<count;++i) w.replay.push_back(benchmark_frame(i%2==0?w.cancels[i].payload:w.executions[i].payload,count+i,seed,"replay"));
    return w;
}
} // namespace gig::fixtures
