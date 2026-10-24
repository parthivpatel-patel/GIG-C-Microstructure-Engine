#include "memory_stats.hpp"
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include "fixtures/synthetic/simulation.hpp"
#include "gig/memory/tracked_resource.hpp"
using namespace gig;using namespace gig::fixtures;using namespace gig::simulation;
int main(int argc,char** argv){try{
    using BenchClock=std::chrono::steady_clock;
    std::vector<std::int64_t> bulk,latency;std::vector<std::size_t> allocations,peaks;latency.reserve(896);std::uint64_t checksum=0;std::string reference;
    for(int pass=-2;pass<14;++pass){TrackedResource resource;{
        auto c=sim_config();c.run_id=text("simulation-benchmark-run");auto e=take(Simulator::create(c,&resource));
        for(std::uint64_t i=1;i<=32;++i){must(e.submit_at(sim_time(0),sim_order(i,Side::sell,static_cast<std::int64_t>(100+i%4),8)));must(e.advance_to(sim_time(0)));}
        const auto before=resource.stats();const auto start=BenchClock::now();
        for(std::uint64_t i=0;i<128;++i){const auto a=pass>=7?BenchClock::now():start;must(e.submit_at(sim_time(0),sim_order(100+i,Side::buy,103,1,TimeInForce::ioc)));must(e.advance_to(sim_time(0)));checksum+=e.exchange_fills().size();if(pass>=7){auto z=BenchClock::now();latency.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(z-a).count());}}
        const auto end=BenchClock::now();auto after=resource.stats();
        if(pass>=0 && pass<7){bulk.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(end-start).count());allocations.push_back(after.allocations-before.allocations);peaks.push_back(after.peak_bytes);}
        if(e.exchange_fills().size()!=128 || e.conservation()!=Conservation{384,256,0,0,0} || e.check_invariants())return 1;
        auto canonical=sim_state(e);if(reference.empty())reference=canonical;else if(canonical!=reference)return 1;
    }if(resource.stats().live_bytes!=0)return 1;}
    if(argc==2){if(std::filesystem::exists(argv[1]))throw std::runtime_error("refusing overwrite");std::ofstream f(argv[1],std::ios::binary);f.exceptions(std::ios::badbit|std::ios::failbit);f.write(reference.data(),static_cast<std::streamsize>(reference.size()));}else if(argc!=1)throw std::runtime_error("usage: [new-canonical-path]");
    std::cout<<"{\"case\":\"synthetic_ioc_matching_v1\",\"seed\":1729,\"warmup\":2,\"repetitions\":7,\"operations_per_repetition\":128,\"checksum\":"<<checksum<<",\"bulk_ns\":[";
    for(std::size_t i=0;i<bulk.size();++i){if(i)std::cout<<',';std::cout<<bulk[i];}std::cout<<"],\"service_ns\":[";for(std::size_t i=0;i<latency.size();++i){if(i)std::cout<<',';std::cout<<latency[i];}
    std::cout<<"],\"pmr_bulk_allocations\":[";for(std::size_t i=0;i<allocations.size();++i){if(i)std::cout<<',';std::cout<<allocations[i];}std::cout<<"],\"pmr_peak_bytes_including_setup\":[";for(std::size_t i=0;i<peaks.size();++i){if(i)std::cout<<',';std::cout<<peaks[i];}std::cout<<"]";gig::benchmark_memory::emit_native_peak_rss();std::cout<<"}\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
