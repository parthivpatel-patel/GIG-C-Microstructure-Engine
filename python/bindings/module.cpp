#include "results.hpp"
#include "gig_python_build_info.hpp"
#include "gig/detail/canonical.hpp"
#include "gig/memory/tracked_resource.hpp"
namespace gig::python {
class NativeReplay {
    TrackedResource memory_;
    ReplayEngine engine_;
public:
    NativeReplay(InstrumentRules r,ReplayConfig c,BookLimits l,std::size_t budget):memory_(std::pmr::get_default_resource(),budget),engine_(take(ReplayEngine::create(r,c,l,&memory_))) {if(l.max_snapshot_depth>4096)bad(ErrorCode::capacity,"binding.snapshot_depth");}
    py::dict apply(py::handle event){return mutate([&](){auto e=read<MarketEvent>(body(event,"gig.event"));return engine_.apply(e);});}
    py::dict reset(py::handle event,py::handle plan){return mutate([&](){auto e=read<MarketEvent>(body(event,"gig.event"));auto p=read<RestartPlan>(plan);return engine_.reset(e,p);});}
    py::dict recover(py::handle event){return mutate([&](){auto e=read<MarketEvent>(body(event,"gig.event"));return engine_.recover(e);});}
    py::dict snapshot(py::handle depth){return api([&](){return snapshot_wire(take(engine_.depth(read<std::size_t>(depth))));});}
    py::dict metrics(py::handle depth){return api([&](){auto d=read<std::size_t>(depth);auto snapshot=take(engine_.depth(d));return book_metrics_wire(take(analytics::calculate(snapshot,d)));});}
    py::dict canonical(){return api([&]()->py::object{auto s=take(engine_.canonical());if(s.size()>33554432)bad(ErrorCode::capacity,"binding.canonical_export");return py::str(s.data(),s.size());});}
    py::dict status(){return api([&]()->py::object{py::dict d;d["needs_recovery"]=engine_.needs_recovery();d["journal_size"]=write(engine_.journal_size());d["pmr_live_bytes"]=write(memory_.stats().live_bytes);d["pmr_peak_bytes"]=write(memory_.stats().peak_bytes);d["pmr_allocations"]=write(memory_.stats().allocations);d["pmr_deallocations"]=write(memory_.stats().deallocations);return d;});}
};
class NativeSimulation {
    TrackedResource memory_;simulation::Simulator model_;
public:
    NativeSimulation(simulation::SimConfig c,std::size_t budget):memory_(std::pmr::get_default_resource(),budget),model_(take(simulation::Simulator::create(c,&memory_))){}
    py::dict submit(py::handle t,py::handle o){return mutate([&](){return model_.submit_at(read<SimulationTime>(t),read<simulation::SimOrder>(o));});}
    py::dict cancel(py::handle t,py::handle id){return mutate([&](){return model_.cancel_at(read<SimulationTime>(t),read<OrderId>(id));});}
    py::dict advance(py::handle t){return mutate([&](){return model_.advance_to(read<SimulationTime>(t));});}
    py::dict snapshot(){return api([&](){return simulation_wire(model_);});}
    py::dict canonical(){return api([&]()->py::object{auto c=take(model_.canonical());if(c.size()>33554432)bad(ErrorCode::capacity,"binding.canonical_export");return py::str(c.data(),c.size());});}
    py::dict queue(py::handle id){return api([&](){return write(model_.exchange_queue_position(read<OrderId>(id)));});}
};
void bind_schemas(py::module_&);
PYBIND11_MODULE(_native,m){
    m.attr("__version__")="0.1.1";m.attr("schema_version")="1.0";m.attr("__compiler__")=__VERSION__;m.attr("__build_type__")=GIG_PYTHON_BUILD_TYPE;m.attr("__config_flags__")=GIG_PYTHON_CONFIG_FLAGS;m.attr("__target_flags__")=GIG_PYTHON_TARGET_FLAGS;m.attr("__core_flags__")=GIG_PYTHON_CORE_FLAGS;m.attr("__python__")=PY_VERSION;m.attr("__pybind11__")=std::to_string(PYBIND11_VERSION_MAJOR)+"."+std::to_string(PYBIND11_VERSION_MINOR)+"."+std::to_string(PYBIND11_VERSION_PATCH);
    py::class_<NativeReplay>(m,"_Replay").def("apply",&NativeReplay::apply).def("reset",&NativeReplay::reset).def("recover",&NativeReplay::recover).def("snapshot",&NativeReplay::snapshot).def("metrics",&NativeReplay::metrics).def("canonical",&NativeReplay::canonical).def("status",&NativeReplay::status);
    py::class_<NativeSimulation>(m,"_Simulation").def("submit",&NativeSimulation::submit).def("cancel",&NativeSimulation::cancel).def("advance",&NativeSimulation::advance).def("snapshot",&NativeSimulation::snapshot).def("canonical",&NativeSimulation::canonical).def("queue",&NativeSimulation::queue);
    m.def("new_replay",[](py::handle rules,py::handle config,py::handle limits,py::handle budget){return api([&](){return py::cast(std::make_unique<NativeReplay>(read<InstrumentRules>(rules),read<ReplayConfig>(config),read<BookLimits>(limits),read<std::size_t>(budget)));});});
    m.def("new_simulation",[](py::handle config,py::handle budget){return api([&](){return py::cast(std::make_unique<NativeSimulation>(read<simulation::SimConfig>(config),read<std::size_t>(budget)));});});
    m.def("validate_rules",[](py::handle rules){return api([&]()->py::object{auto r=read<InstrumentRules>(rules);require(validate(r));return write(r);});});
    m.def("event_roundtrip",[](py::handle value,py::handle rules,bool inspect){return api([&](){auto e=read<MarketEvent>(body(value,"gig.event"));auto r=read<InstrumentRules>(rules);require(validate(e,r,inspect?ValidationMode::inspect_incomplete:ValidationMode::complete));return envelope("gig.event",write(e));});});
    m.def("event_canonical",[](py::handle value,py::handle rules){return api([&]()->py::object{auto e=read<MarketEvent>(body(value,"gig.event"));require(validate(e,read<InstrumentRules>(rules)));std::pmr::string c;detail::CanonicalWriter w(c);w.raw("gig.event.v1;");detail::canonical_event(w,e);return py::str(c.data(),c.size());});});
    m.def("book_analytics",[](py::handle value,py::handle depth){return api([&](){auto s=snapshot_read(value);return book_metrics_wire(take(analytics::calculate(s,read<std::size_t>(depth))));});});
    m.def("flow_analytics",[](py::handle quotes,py::handle trades,py::handle config,py::handle asof){return api([&](){auto q=read<std::vector<analytics::FlowQuote>>(quotes);auto t=read<std::vector<analytics::FlowTrade>>(trades);return flow_metrics_wire(take(analytics::calculate_flow(q,t,read<analytics::FlowConfig>(config),read<EventTimestamp>(asof))));});});
    m.def("twap",[](py::handle c){return api([&](){return schedule_wire(take(execution::twap(read<execution::PlanConfig>(c))));});});
    m.def("vwap",[](py::handle c,py::handle w,py::handle artifact,py::handle available,py::handle kind){return api([&](){auto weights=read<std::vector<std::uint64_t>>(w);return schedule_wire(take(execution::vwap(read<execution::PlanConfig>(c),weights,read<Identity>(artifact),read<SimulationTime>(available),read<execution::VolumeProfile>(kind))));});});
    m.def("pov",[](py::handle c,py::handle v,py::handle n,py::handle d){return api([&](){auto volume=read<std::vector<execution::VolumePoint>>(v);return schedule_wire(take(execution::pov(read<execution::PlanConfig>(c),volume,read<std::uint64_t>(n),read<std::uint64_t>(d))));});});
    m.def("simulate_plan",[](py::handle p,py::handle c,py::handle l,py::handle finish){return api([&]()->py::object{auto plan=schedule_read(p);auto liquidity=read<std::vector<simulation::SimOrder>>(l);auto run=take(execution::simulate(plan,read<simulation::SimConfig>(c),liquidity,read<SimulationTime>(finish)));py::dict d;d["plan"]=schedule_wire(run.plan);d["simulation"]=simulation_wire(run.simulator);return d;});});
    m.def("transaction_costs",[](py::handle c,py::handle f){return api([&](){auto fills=read<std::vector<execution::CostFill>>(f);return costs_wire(take(execution::transaction_costs(read<execution::CostConfig>(c),fills)));});});
    m.def("fraction_roundtrip",[](py::handle value){return api([&](){return write(read<exact::Fraction>(value));});});
    bind_schemas(m);
}
} // namespace gig::python
