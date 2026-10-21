#pragma once
#include "gig/simulation/simulator.hpp"
#include "fixtures/synthetic/book_events.hpp"
namespace gig::fixtures {
inline simulation::SimConfig sim_config(std::uint64_t seed=1729){
    simulation::Latency zero{number<Duration>(0),number<Duration>(0)};
    return {text("synthetic-simulation-run"),rules(),seed,zero,zero,zero,zero};
}
inline simulation::SimOrder sim_order(std::uint64_t id,Side side,std::int64_t price,std::uint64_t quantity,simulation::TimeInForce tif=simulation::TimeInForce::gtc,bool post_only=false){return {number<OrderId>(id),side,number<PriceTicks>(price),number<QuantityLots>(quantity),tif,post_only};}
inline SimulationTime sim_time(std::int64_t value){return number<SimulationTime>(value);}
inline std::string sim_state(const simulation::Simulator& s){auto c=take(s.canonical());return {c.begin(),c.end()};}
}
