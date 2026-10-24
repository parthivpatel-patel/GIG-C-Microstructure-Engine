#pragma once
#include "wire.hpp"
namespace gig::python {
struct DepthWire {InstrumentRules rules;BookSession session;std::uint64_t revision;std::size_t requested_depth;bool bid_truncated,ask_truncated;std::vector<DepthLevel> bids,asks;};
struct SnapshotWire {Identity run_id;std::size_t journal_prefix;DepthWire book;};
struct BookValues {analytics::Metric best_bid,best_ask,spread,midpoint,microprice,top_imbalance,bid_depth,ask_depth,depth_imbalance;};
struct BookResult {analytics::SnapshotReference source;std::size_t depth;BookValues metrics;};
struct FlowResult {analytics::FlowConfig config;EventTimestamp as_of;analytics::FlowSummary summary;std::vector<analytics::SignedTrade> trades;std::vector<analytics::SnapshotReference> parents;};
struct ScheduleWire {execution::PlanConfig config;execution::Algorithm algorithm;bool oracle;Available<Identity> profile;Available<SimulationTime> profile_available_at;std::vector<execution::ChildSlice> children;std::vector<std::uint64_t> weights;std::vector<execution::VolumePoint> volumes;std::uint64_t participation_numerator,participation_denominator;};
struct CostResult {execution::CostConfig config;execution::CostSummary summary;std::vector<execution::CostFill> parents;};
struct SimulationWire {simulation::SimConfig config;SimulationTime now;simulation::Conservation conservation;std::vector<simulation::Resting> exchange_orders;std::vector<simulation::SimFill> exchange_fills;std::vector<simulation::ClientReport> client_reports;std::string canonical;};
#define F(N) Field<&T::N>{#N}
#define RECORD(TYPE,...) template<>struct Record<TYPE>{static auto fields(){using T [[maybe_unused]]=TYPE;return std::tuple{__VA_ARGS__};}};
RECORD(DepthWire,F(rules),F(session),F(revision),F(requested_depth),F(bid_truncated),F(ask_truncated),F(bids),F(asks))
RECORD(SnapshotWire,F(run_id),F(journal_prefix),F(book))
RECORD(BookValues,F(best_bid),F(best_ask),F(spread),F(midpoint),F(microprice),F(top_imbalance),F(bid_depth),F(ask_depth),F(depth_imbalance))
RECORD(BookResult,F(source),F(depth),F(metrics))
RECORD(FlowResult,F(config),F(as_of),F(summary),F(trades),F(parents))
RECORD(ScheduleWire,F(config),F(algorithm),F(oracle),F(profile),F(profile_available_at),F(children),F(weights),F(volumes),F(participation_numerator),F(participation_denominator))
RECORD(CostResult,F(config),F(summary),F(parents))
RECORD(SimulationWire,F(config),F(now),F(conservation),F(exchange_orders),F(exchange_fills),F(client_reports),F(canonical))
#undef RECORD
#undef F
py::object simulation_wire(const simulation::Simulator&);
} // namespace gig::python
