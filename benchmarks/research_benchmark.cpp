#include "memory_stats.hpp"
#include <chrono>
#include <iostream>
#include <fstream>
#include <filesystem>
#include <vector>
#include "gig/analytics/book_metrics.hpp"
#include "fixtures/synthetic/replay_events.hpp"
using namespace gig;using namespace gig::fixtures;
int main(int argc,char** argv) {
    try {
        auto config=replay_config();config.run_id=text("research-benchmark-run");
        auto replay=take(ReplayEngine::create(rules(),config));
        must(replay.apply(replay_event(add(1),0,0)));
        must(replay.apply(replay_event(add(2),1,1)));
        must(replay.apply(replay_event(add(3,Side::sell,200),2,2)));
        auto snapshot=take(replay.depth(1));
        if (argc==2) {
            if (std::filesystem::exists(argv[1])) throw std::runtime_error("refusing to overwrite canonical input");
            auto canonical=take(replay.canonical());std::ofstream f(argv[1],std::ios::binary);f.exceptions(std::ios::badbit|std::ios::failbit);f.write(canonical.data(),static_cast<std::streamsize>(canonical.size()));
        } else if (argc!=1) throw std::runtime_error("usage: [new-input-canonical-path]");
        auto expected=take(analytics::calculate(snapshot,1));
        if (expected.get(analytics::BookMetric::midpoint).value->str()!="150/1" || expected.get(analytics::BookMetric::microprice).value->str()!="500/3") return 1;
        using Clock=std::chrono::steady_clock;
        std::vector<std::int64_t> bulk,latencies;latencies.reserve(35000);std::uint64_t checksum=0;
        for (int pass=-2;pass<7;++pass) {
            auto a=Clock::now();
            for (int i=0;i<5000;++i) {auto m=take(analytics::calculate(snapshot,1));checksum+=static_cast<std::uint64_t>(m.get(analytics::BookMetric::microprice).value->numerator());}
            auto z=Clock::now();if(pass>=0)bulk.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(z-a).count());
        }
        for (int i=0;i<35000;++i) {auto a=Clock::now();auto m=take(analytics::calculate(snapshot,1));checksum+=static_cast<std::uint64_t>(m.get(analytics::BookMetric::microprice).value->numerator());auto z=Clock::now();latencies.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(z-a).count());}
        std::cout << "{\"case\":\"book_metrics_depth1\",\"seed\":0,\"warmup\":2,\"repetitions\":7,\"operations_per_repetition\":5000,\"checksum\":" << checksum << ",\"bulk_ns\":[";
        for(std::size_t i=0;i<bulk.size();++i){if(i)std::cout<<',';std::cout<<bulk[i];}std::cout<<"],\"service_ns\":[";
        for(std::size_t i=0;i<latencies.size();++i){if(i)std::cout<<',';std::cout<<latencies[i];}std::cout<<"]";gig::benchmark_memory::emit_native_peak_rss();std::cout<<"}\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
