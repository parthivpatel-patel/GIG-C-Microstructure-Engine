#include "wire.hpp"
#include <stdexcept>
#include "gig/market_data/aggregate_depth.hpp"
#include "gig/memory/tracked_resource.hpp"
namespace gig::python {
namespace {
std::vector<market_data::Level> levels(py::handle h){
    if(!PyList_CheckExact(h.ptr())||py::len(h)>4096)bad(ErrorCode::capacity,"aggregate.levels");
    std::vector<market_data::Level> result;result.reserve(py::len(h));
    for(auto item:py::reinterpret_borrow<py::list>(h)){auto d=object(item,{"price_ticks","quantity"});result.push_back({read<std::int64_t>(d["price_ticks"]),read<std::uint64_t>(d["quantity"])});}return result;
}
py::object fraction(const std::optional<exact::Fraction>& f){if(!f)return py::none();py::dict d;d["numerator"]=exact::decimal(f->numerator());d["denominator"]=exact::decimal(f->denominator());return d;}
class NativeAggregate {
    TrackedResource memory_;market_data::AggregateDepth book_;
    py::dict value(){
        py::dict out;auto side=[](std::span<const market_data::Level> values){py::list rows;for(auto l:values){py::dict d;d["price_ticks"]=write(l.price_ticks);d["quantity"]=write(l.quantity);rows.append(d);}return rows;};
        out["bids"]=side(book_.bids());out["asks"]=side(book_.asks());out["revision"]=write(book_.revision());out["sequence"]=write(book_.sequence());out["initialized"]=book_.initialized();
        const auto m=take(book_.metrics());py::dict metrics;metrics["spread"]=fraction(m.spread);metrics["midpoint"]=fraction(m.midpoint);metrics["microprice"]=fraction(m.microprice);metrics["depth_imbalance"]=fraction(m.depth_imbalance);metrics["bid_depth"]=fraction(m.bid_depth);metrics["ask_depth"]=fraction(m.ask_depth);
        out["metrics"]=metrics;out["locked"]=m.locked;out["crossed"]=m.crossed;out["pmr_live_bytes"]=write(memory_.stats().live_bytes);out["pmr_peak_bytes"]=write(memory_.stats().peak_bytes);return out;
    }
public:
    NativeAggregate(std::size_t n,std::size_t budget):memory_(std::pmr::get_default_resource(),budget),book_(n,&memory_){if(budget>67108864)throw std::invalid_argument("aggregate.memory_budget");}
    NativeAggregate(const market_data::AggregateStateImage& image,std::size_t n,std::size_t budget):NativeAggregate(n,budget){book_=take(market_data::AggregateDepth::restore(image,n,&memory_));}
    py::dict snapshot(py::handle b,py::handle a,py::handle seq){return mutate([&](){auto bids=levels(b),asks=levels(a);return book_.snapshot(bids,asks,read<std::optional<std::uint64_t>>(seq));});}
    py::dict update(py::handle b,py::handle a,py::handle seq){return mutate([&](){auto bids=levels(b),asks=levels(a);return book_.update(bids,asks,read<std::optional<std::uint64_t>>(seq));});}
    py::dict state(){return api([&](){return value();});}
    py::dict checkpoint(){return api([&](){auto image=take(book_.checkpoint(&memory_));py::dict out;
        auto side=[](const auto& rows){py::list out;for(const auto l:rows){py::dict d;d["price_ticks"]=write(l.price_ticks);d["quantity"]=write(l.quantity);out.append(d);}return out;};
        out["version"]=write(image.version);out["max_levels"]=write(image.max_levels);out["sequence"]=write(image.sequence);
        out["revision"]=write(image.revision);out["initialized"]=image.initialized;out["bids"]=side(image.bids);out["asks"]=side(image.asks);return out;});}
};
}
void bind_depth(py::module_&m){py::class_<NativeAggregate>(m,"AggregateDepth")
    .def(py::init<std::size_t,std::size_t>(),py::arg("max_levels")=1024,py::arg("budget")=1048576)
    .def("snapshot",&NativeAggregate::snapshot,py::arg("bids"),py::arg("asks"),py::arg("sequence")=py::none())
    .def("update",&NativeAggregate::update,py::arg("bids"),py::arg("asks"),py::arg("sequence")=py::none())
    .def("state",&NativeAggregate::state).def("checkpoint",&NativeAggregate::checkpoint);
    m.def("restore_aggregate",[](py::handle value,py::handle expected,py::handle budget){return api([&](){
        const auto d=object(value,{"version","max_levels","sequence","revision","initialized","bids","asks"});
        if(!PyBool_Check(d["initialized"].ptr()))bad(ErrorCode::malformed,"aggregate.initialized");
        market_data::AggregateStateImage image(std::pmr::get_default_resource());image.version=read<std::uint32_t>(d["version"]);
        image.max_levels=read<std::size_t>(d["max_levels"]);image.sequence=read<std::optional<std::uint64_t>>(d["sequence"]);
        image.revision=read<std::uint64_t>(d["revision"]);image.initialized=py::cast<bool>(d["initialized"]);
        const auto bids=levels(d["bids"]),asks=levels(d["asks"]);image.bids.assign(bids.begin(),bids.end());image.asks.assign(asks.begin(),asks.end());
        return py::cast(std::make_unique<NativeAggregate>(image,read<std::size_t>(expected),read<std::size_t>(budget)));
    });},py::arg("image"),py::arg("expected_max_levels"),py::arg("budget"));}
}
