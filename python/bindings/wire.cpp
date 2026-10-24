#include "results.hpp"
namespace gig::python {
py::object snapshot_wire(const ReplaySnapshot& s){
    py::dict b;b["rules"]=write(s.book.rules);b["session"]=write(s.book.session);b["revision"]=write(s.book.revision);b["requested_depth"]=write(s.book.requested_depth);b["bid_truncated"]=write(s.book.bid_truncated);b["ask_truncated"]=write(s.book.ask_truncated);b["bids"]=write(s.book.bids);b["asks"]=write(s.book.asks);
    py::dict d;d["run_id"]=write(s.run_id);d["journal_prefix"]=write(s.journal_prefix);d["book"]=b;return envelope("gig.book_snapshot",d);
}
ReplaySnapshot snapshot_read(py::handle value){
    auto wire=read<SnapshotWire>(body(value,"gig.book_snapshot"));if(wire.book.requested_depth>4096)bad(ErrorCode::capacity,"binding.snapshot_depth");
    DepthSnapshot b(wire.book.rules,wire.book.session,wire.book.revision,wire.book.requested_depth,std::pmr::get_default_resource());b.bid_truncated=wire.book.bid_truncated;b.ask_truncated=wire.book.ask_truncated;b.bids.assign(wire.book.bids.begin(),wire.book.bids.end());b.asks.assign(wire.book.asks.begin(),wire.book.asks.end());return {wire.run_id,wire.journal_prefix,std::move(b)};
}
py::object book_metrics_wire(const analytics::BookMetrics& m){
    using M=analytics::BookMetric;BookValues values{m.get(M::best_bid),m.get(M::best_ask),m.get(M::spread),m.get(M::midpoint),m.get(M::microprice),m.get(M::top_imbalance),m.get(M::bid_depth),m.get(M::ask_depth),m.get(M::depth_imbalance)};
    py::dict d;d["kind"]="book";d["result"]=write(BookResult{m.source(),m.depth(),values});return envelope("gig.metric_result",d);
}
py::object flow_metrics_wire(const analytics::FlowMetrics& f){py::dict result;result["config"]=write(f.config());result["as_of"]=write(f.as_of());result["summary"]=write(f.summary());result["trades"]=write(f.trades());result["parents"]=write(f.parents());py::dict d;d["kind"]="flow";d["result"]=result;return envelope("gig.metric_result",d);}
py::object schedule_wire(const execution::Schedule& s){py::dict d;d["config"]=write(s.config());d["algorithm"]=write(s.algorithm());d["oracle"]=write(s.oracle());d["profile"]=write(s.profile());d["profile_available_at"]=write(s.profile_available_at());d["children"]=write(s.children());d["weights"]=write(s.weights());d["volumes"]=write(s.volumes());d["participation_numerator"]=write(s.participation_numerator());d["participation_denominator"]=write(s.participation_denominator());return envelope("gig.execution_schedule",d);}
execution::Schedule schedule_read(py::handle h){auto s=read<ScheduleWire>(body(h,"gig.execution_schedule"));return {s.config,s.algorithm,s.oracle,s.profile,std::pmr::vector<execution::ChildSlice>(s.children.begin(),s.children.end()),std::pmr::vector<std::uint64_t>(s.weights.begin(),s.weights.end()),std::pmr::vector<execution::VolumePoint>(s.volumes.begin(),s.volumes.end()),s.participation_numerator,s.participation_denominator,s.profile_available_at};}
py::object costs_wire(const execution::CostReport& c){py::dict result;result["config"]=write(c.config());result["summary"]=write(c.summary());result["parents"]=write(c.parents());py::dict d;d["kind"]="cost";d["result"]=result;return envelope("gig.metric_result",d);}
py::object simulation_wire(const simulation::Simulator& s){
    py::dict d;d["config"]=write(s.config());d["now"]=write(s.now());d["conservation"]=write(s.conservation());
    py::list orders,fills,reports;for(const auto& o:s.exchange_orders())orders.append(write(o));for(const auto& f:s.exchange_fills())fills.append(write(f));for(const auto& r:s.client_reports())reports.append(write(r));
    d["exchange_orders"]=orders;d["exchange_fills"]=fills;d["client_reports"]=reports;
    auto canonical=take(s.canonical());if(canonical.size()>33554432)bad(ErrorCode::capacity,"binding.canonical_export");d["canonical"]=py::str(canonical.data(),canonical.size());
    py::dict out;out["origin"]="synthetic";out["transformation"]="simulated";out["state"]=d;return envelope("gig.simulation_output",out);
}
} // namespace gig::python
