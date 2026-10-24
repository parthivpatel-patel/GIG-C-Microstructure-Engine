#pragma once
#include "gig/execution/execution.hpp"
#include "fixtures/synthetic/simulation.hpp"
namespace gig::fixtures {
inline execution::PlanConfig plan_config(std::uint64_t target=100,std::uint32_t bins=4){return {text("synthetic-execution-run"),text("explicit-limit-and-inventory-v1"),rules(),Side::buy,number<PriceTicks>(105),number<QuantityLots>(target),number<QuantityLots>(target),number<QuantityLots>(UINT64_MAX),sim_time(0),sim_time(1000),bins,number<OrderId>(1000)};}
inline execution::PriceBenchmark benchmark(std::int64_t value,std::int64_t available){return {exact::Fraction(value),sim_time(available),text("synthetic-midpoint-artifact")};}
inline execution::CostFill cost_fill(std::uint64_t quantity=10,std::int64_t price=103,Side side=Side::buy){return {{text("synthetic-execution-run"),1729,number<OrderId>(1),number<OrderId>(1000),side,number<PriceTicks>(price),number<QuantityLots>(quantity),sim_time(10),sim_time(12),0,1},number<OrderId>(1000),sim_time(5),benchmark(102,5),exact::Fraction::ratio(1,10)};}
inline execution::CostConfig cost_config(std::uint64_t target=20,Side side=Side::buy){return {text("cost-research-run"),text("synthetic-execution-run"),rules(),side,number<QuantityLots>(target),benchmark(100,0),benchmark(104,20),sim_time(20)};}
}
