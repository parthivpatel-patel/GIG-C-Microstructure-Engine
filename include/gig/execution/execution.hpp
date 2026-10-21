#pragma once
#include "gig/analytics/book_metrics.hpp"
#include "gig/simulation/simulator.hpp"
namespace gig::execution {
using exact::Fraction;
enum class Algorithm { twap,vwap,pov };
enum class VolumeProfile { ex_ante_forecast,oracle_hindsight };
struct PlanConfig {
    Identity run_id,assumptions_id;InstrumentRules rules;Side side;PriceTicks limit;
    QuantityLots target,inventory_limit,max_child;SimulationTime start,end;std::uint32_t bins;OrderId first_child_id;simulation::TimeInForce tif{simulation::TimeInForce::ioc};bool post_only{};
};
struct ChildSlice {SimulationTime decision_time;simulation::SimOrder order;bool operator==(const ChildSlice&)const=default;};
struct VolumePoint {SimulationTime available_at;QuantityLots lots;Identity source_artifact;std::uint64_t ordinal;bool operator==(const VolumePoint&)const=default;};
class Schedule {
    PlanConfig config_;Algorithm algorithm_;bool oracle_;Available<Identity> profile_;Available<SimulationTime> profile_available_;
    std::pmr::vector<ChildSlice> children_;std::pmr::vector<std::uint64_t> weights_;std::pmr::vector<VolumePoint> volumes_;
    std::uint64_t participation_numerator_,participation_denominator_;
public:
    Schedule(PlanConfig c,Algorithm a,bool oracle,Available<Identity> profile,std::pmr::vector<ChildSlice> slices,std::pmr::vector<std::uint64_t> weights,std::pmr::vector<VolumePoint> volumes,std::uint64_t pn=0,std::uint64_t pd=1,Available<SimulationTime> profile_available=Available<SimulationTime>::missing(MissingReason::not_applicable))
        :config_(c),algorithm_(a),oracle_(oracle),profile_(profile),profile_available_(profile_available),children_(std::move(slices)),weights_(std::move(weights)),volumes_(std::move(volumes)),participation_numerator_(pn),participation_denominator_(pd){}
    const PlanConfig& config()const noexcept{return config_;}
    Algorithm algorithm()const noexcept{return algorithm_;}bool oracle()const noexcept{return oracle_;}
    const Available<Identity>& profile()const noexcept{return profile_;}
    const Available<SimulationTime>& profile_available_at()const noexcept{return profile_available_;}
    const std::pmr::vector<ChildSlice>& children()const noexcept{return children_;}
    const std::pmr::vector<std::uint64_t>& weights()const noexcept{return weights_;}
    const std::pmr::vector<VolumePoint>& volumes()const noexcept{return volumes_;}
    std::uint64_t participation_numerator()const noexcept{return participation_numerator_;}
    std::uint64_t participation_denominator()const noexcept{return participation_denominator_;}
};
Result<Schedule> twap(PlanConfig,std::pmr::memory_resource* =std::pmr::get_default_resource())noexcept;
Result<Schedule> vwap(PlanConfig,std::span<const std::uint64_t> weights,Identity profile_artifact,SimulationTime profile_available_at,VolumeProfile,std::pmr::memory_resource* =std::pmr::get_default_resource())noexcept;
Result<Schedule> pov(PlanConfig,std::span<const VolumePoint>,std::uint64_t numerator,std::uint64_t denominator,std::pmr::memory_resource* =std::pmr::get_default_resource())noexcept;
struct ExecutionRun {Schedule plan;simulation::Simulator simulator;};
Result<ExecutionRun> simulate(const Schedule&,simulation::SimConfig,std::span<const simulation::SimOrder> initial_liquidity,SimulationTime finish,std::pmr::memory_resource* =std::pmr::get_default_resource())noexcept;
struct PriceBenchmark {Fraction midpoint;SimulationTime available_at;Identity source_artifact;};
struct CostFill {
    simulation::SimFill fill;OrderId child;SimulationTime decision_time;PriceBenchmark decision_benchmark;Fraction fee_ticks_per_lot;
};
struct CostConfig {
    Identity run_id,simulation_run_id;InstrumentRules rules;Side side;QuantityLots target;
    PriceBenchmark arrival,terminal;SimulationTime as_of;
};
struct CostSummary {
    std::uint64_t filled_lots,unfilled_lots;
    analytics::Metric execution_vwap;
    Fraction gross_notional,delay_cost,spread_cost,fees,slippage,opportunity_cost,implementation_shortfall,currency_shortfall;
};
class CostReport {
    CostConfig config_;CostSummary summary_;std::pmr::vector<CostFill> parents_;
public:
    CostReport(CostConfig c,CostSummary s,std::pmr::vector<CostFill> p):config_(c),summary_(s),parents_(std::move(p)){}
    const CostConfig& config()const noexcept{return config_;}const CostSummary& summary()const noexcept{return summary_;}
    const std::pmr::vector<CostFill>& parents()const noexcept{return parents_;}
};
Result<CostReport> transaction_costs(CostConfig,std::span<const CostFill>,std::pmr::memory_resource* =std::pmr::get_default_resource())noexcept;
} // namespace gig::execution
