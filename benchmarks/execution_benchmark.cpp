#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include "fixtures/synthetic/execution.hpp"
#include "gig/memory/tracked_resource.hpp"
using namespace gig;using namespace gig::fixtures;using namespace gig::execution;
int main(int argc,char** argv){try{
    auto config=plan_config(20,2);auto plan=take(twap(config));auto model=sim_config();model.run_id=config.run_id;
    std::array<simulation::SimOrder,1> liquidity{sim_order(1,Side::sell,103,10)};auto run=take(simulate(plan,model,liquidity,sim_time(1000)));
    auto row=cost_fill();row.fill=run.simulator.exchange_fills().front();row.decision_time=sim_time(0);row.decision_benchmark=benchmark(102,0);
    std::array<CostFill,1> fills{row};auto costs=cost_config();costs.terminal=benchmark(104,1000);costs.as_of=sim_time(1000);
    auto expected=take(transaction_costs(costs,fills));if(expected.summary().implementation_shortfall.str()!="71/1" || expected.summary().currency_shortfall.str()!="71/100")return 1;
    if(argc==2){if(std::filesystem::exists(argv[1]))throw std::runtime_error("refusing overwrite");auto canonical=take(run.simulator.canonical());std::ofstream out(argv[1],std::ios::binary);out.exceptions(std::ios::badbit|std::ios::failbit);out.write(canonical.data(),static_cast<std::streamsize>(canonical.size()));}else if(argc!=1)throw std::runtime_error("usage: [new-canonical-path]");
    using BenchClock=std::chrono::steady_clock;TrackedResource resource;std::vector<std::int64_t> bulk,latency;latency.reserve(35000);std::uint64_t checksum=0;
    auto operation=[&](){auto p=take(twap(config,&resource));auto r=take(transaction_costs(costs,fills,&resource));checksum+=static_cast<std::uint64_t>(r.summary().implementation_shortfall.numerator())+p.children()[0].order.quantity.value();};
    for(int pass=-2;pass<7;++pass){auto a=BenchClock::now();for(int i=0;i<5000;++i)operation();auto z=BenchClock::now();if(pass>=0)bulk.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(z-a).count());}
    for(int i=0;i<35000;++i){auto a=BenchClock::now();operation();auto z=BenchClock::now();latency.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(z-a).count());}
    auto stats=resource.stats();if(stats.live_bytes)return 1;
    std::cout<<"{\"case\":\"schedule_and_tca_v1\",\"seed\":1729,\"warmup\":2,\"repetitions\":7,\"operations_per_repetition\":5000,\"checksum\":"<<checksum<<",\"pmr_allocations_including_warmup_and_service\":"<<stats.allocations<<",\"pmr_peak_bytes\":"<<stats.peak_bytes<<",\"bulk_ns\":[";
    for(std::size_t i=0;i<bulk.size();++i){if(i)std::cout<<',';std::cout<<bulk[i];}std::cout<<"],\"service_ns\":[";for(std::size_t i=0;i<latency.size();++i){if(i)std::cout<<',';std::cout<<latency[i];}std::cout<<"]}\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
