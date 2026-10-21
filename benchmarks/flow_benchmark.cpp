#include "memory_stats.hpp"
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include "gig/analytics/flow_metrics.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "fixtures/synthetic/replay_events.hpp"
using namespace gig;using namespace gig::fixtures;
int main(int argc,char** argv){try{
    auto c=replay_config();c.run_id=text("flow-benchmark-run");c.streams.items[0]->dataset=text("phase4-benchmark");auto e=take(ReplayEngine::create(rules(),c));
    auto send=[&](EventPayload payload,std::uint64_t seq,std::int64_t time){auto event=replay_event(std::move(payload),seq,seq);event.metadata.provenance.dataset.data->identity=text("phase4-benchmark");event.metadata.provenance.lineage.items[0]->operation=text("phase4-benchmark-v1");event.metadata.event_time.data->nanoseconds=number<EventTimestamp>(time);event.metadata.event_time.data->clock.data->identity=text("flow-utc");event.metadata.receive_time.data->nanoseconds=number<ReceiveTimestamp>(time+1);must(e.apply(event));};
    send(add(1,Side::buy,100,30),0,0);send(add(2,Side::sell,102,10),1,0);
    std::vector<analytics::FlowQuote> quotes;quotes.push_back(take(analytics::quote_observation(take(e.depth(1)),number<EventTimestamp>(0),text("flow-utc"))));
    send(Trade{TradePrint{number<PriceTicks>(102),number<QuantityLots>(1),{}}},2,5);
    auto snap=take(e.depth(1));auto source=take(analytics::calculate(snap,1)).source();std::array<analytics::FlowTrade,1> trades{{{source,number<EventTimestamp>(5),text("flow-utc"),number<PriceTicks>(102),number<QuantityLots>(1)}}};
    send(ReplaceOrder{number<OrderId>(1),number<OrderId>(1),Side::buy,number<PriceTicks>(101),number<QuantityLots>(20),ReplacePriority::lose},3,7);
    quotes.push_back(take(analytics::quote_observation(take(e.depth(1)),number<EventTimestamp>(7),text("flow-utc"))));
    send(ReplaceOrder{number<OrderId>(2),number<OrderId>(2),Side::sell,number<PriceTicks>(103),number<QuantityLots>(20),ReplacePriority::lose},4,10);
    quotes.push_back(take(analytics::quote_observation(take(e.depth(1)),number<EventTimestamp>(10),text("flow-utc"))));
    if(argc==2){if(std::filesystem::exists(argv[1]))throw std::runtime_error("refusing overwrite");auto data=take(e.canonical());std::ofstream out(argv[1],std::ios::binary);out.exceptions(std::ios::failbit|std::ios::badbit);out.write(data.data(),static_cast<std::streamsize>(data.size()));}else if(argc!=1)throw std::runtime_error("usage: [new-input-canonical-path]");
    analytics::FlowConfig config{text("flow-utc"),number<Duration>(10),number<Duration>(0),number<Duration>(5),number<Duration>(100),number<Duration>(10),true,true};
    auto expected=take(analytics::calculate_flow(quotes,trades,config,number<EventTimestamp>(10)));
    if(expected.summary().ofi.value->str()!="30/1" || expected.trades()[0].effective_spread.value->str()!="2/1" || expected.trades()[0].realized_spread.value->str()!="0/1")return 1;
    using BenchClock=std::chrono::steady_clock;std::vector<std::int64_t> bulk,latency;latency.reserve(35000);std::uint64_t checksum=0;TrackedResource resource;
    auto operation=[&](){auto result=take(analytics::calculate_flow(quotes,trades,config,number<EventTimestamp>(10),&resource));checksum+=static_cast<std::uint64_t>(result.summary().ofi.value->numerator());};
    for(int pass=-2;pass<7;++pass){auto a=BenchClock::now();for(int i=0;i<5000;++i)operation();auto z=BenchClock::now();if(pass>=0)bulk.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(z-a).count());}
    for(int i=0;i<35000;++i){auto a=BenchClock::now();operation();auto z=BenchClock::now();latency.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(z-a).count());}
    auto stats=resource.stats();if(stats.live_bytes!=0)return 1;
    std::cout<<"{\"case\":\"causal_flow_window_v1\",\"seed\":0,\"warmup\":2,\"repetitions\":7,\"operations_per_repetition\":5000,\"checksum\":"<<checksum<<",\"pmr_allocations_including_warmup_and_service\":"<<stats.allocations<<",\"pmr_peak_bytes\":"<<stats.peak_bytes<<",\"bulk_ns\":[";
    for(std::size_t i=0;i<bulk.size();++i){if(i)std::cout<<',';std::cout<<bulk[i];}std::cout<<"],\"service_ns\":[";for(std::size_t i=0;i<latency.size();++i){if(i)std::cout<<',';std::cout<<latency[i];}std::cout<<"]";gig::benchmark_memory::emit_native_peak_rss();std::cout<<"}\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
