#include "results.hpp"
namespace gig::python {
namespace {
py::dict simple(const char* type){py::dict d;d["type"]=type;return d;}
py::dict obj_schema(py::dict properties){auto d=simple("object");py::list keys;for(auto pair:properties)keys.append(pair.first);d["properties"]=properties;d["required"]=keys;d["additionalProperties"]=false;return d;}
py::dict constant(py::object value){py::dict d;d["const"]=std::move(value);return d;}
template<class T,class Enable=void>struct Schema;
template<class T>py::dict schema(){return Schema<T>::get();}
template<class T>struct Schema<T,std::enable_if_t<std::is_integral_v<T> && !std::is_same_v<T,bool>>>{static py::dict get(){auto d=simple("string");d["pattern"]=std::is_signed_v<T>?"^(0|-?[1-9][0-9]*)$":"^(0|[1-9][0-9]*)$";d["maxLength"]=20;d["x-integer-minimum"]=std::to_string(std::numeric_limits<T>::min());d["x-integer-maximum"]=std::to_string(std::numeric_limits<T>::max());return d;}};
template<>struct Schema<bool>{static py::dict get(){return simple("boolean");}};
template<>struct Schema<std::string>{static py::dict get(){auto d=simple("string");d["maxLength"]=33554432;return d;}};
template<class E>struct Schema<E,std::enable_if_t<std::is_enum_v<E>>>{static py::dict get(){py::dict d;py::list choices;for(unsigned i=0;i<=enum_max<E>;++i)choices.append(write(i));d["enum"]=choices;return d;}};
template<class Tag,std::integral R,R Min,bool A>struct Schema<types::Scalar<Tag,R,Min,A>>{static py::dict get(){auto d=schema<R>();d["x-integer-minimum"]=std::to_string(Min);return d;}};
template<std::size_t N>struct Schema<Token<N>>{static py::dict get(){auto d=simple("string");d["minLength"]=1;d["maxLength"]=N;d["pattern"]="^[!-~]+$";return d;}};
template<class T>struct Schema<std::optional<T>>{static py::dict get(){py::dict d;py::list cases;cases.append(schema<T>());cases.append(simple("null"));d["anyOf"]=cases;return d;}};
template<class T>struct Schema<Available<T>>{static py::dict get(){py::dict known,missing;known["reason"]=constant(py::str("0"));known["value"]=schema<T>();py::dict reason;py::list reasons;reasons.append("1");reasons.append("2");reasons.append("3");reason["enum"]=reasons;missing["reason"]=reason;missing["value"]=simple("null");py::list cases;cases.append(obj_schema(known));cases.append(obj_schema(missing));py::dict d;d["oneOf"]=cases;return d;}};
template<class T,std::size_t N>struct Schema<BoundedList<T,N>>{static py::dict get(){auto d=simple("array");d["items"]=schema<T>();d["maxItems"]=N;return d;}};
template<class T,class A>struct Schema<std::vector<T,A>>{static py::dict get(){auto d=simple("array");d["items"]=schema<T>();d["maxItems"]=100000;d["x-operational-input-limit"]="4096 where used as bounded operational input; output limits follow native configuration";return d;}};
template<class... Ts>struct Schema<std::variant<Ts...>>{
    static py::dict get(){py::list choices;std::size_t i=0;([&](){py::dict p;p["tag"]=constant(write(i++));p["value"]=schema<Ts>();choices.append(obj_schema(p));}(),...);py::dict d;d["oneOf"]=choices;return d;}
};
template<>struct Schema<exact::Fraction>{static py::dict get(){py::dict p;auto n=simple("string"),d=simple("string");n["pattern"]="^(0|-?[1-9][0-9]*)$";n["maxLength"]=40;n["x-integer-minimum"]=exact::decimal(-exact::maximum);n["x-integer-maximum"]=exact::decimal(exact::maximum);d["pattern"]="^[1-9][0-9]*$";d["maxLength"]=39;d["x-integer-minimum"]="1";d["x-integer-maximum"]=exact::decimal(exact::maximum);p["numerator"]=n;p["denominator"]=d;auto result=obj_schema(p);result["x-exact-capacity"]="symmetric signed 127-bit magnitude, reduced by native adapter";return result;}};
template<>struct Schema<long double>{static py::dict get(){auto d=simple("string");d["pattern"]="^-?[0-9]+(\\.[0-9]+)?([eE][+-]?[0-9]+)?$";d["x-approximate"]="finite long-double sqrt, not an exact rational/cross-platform last-bit claim";return d;}};
template<class T,auto Member>void add_property(py::dict& d,Field<Member> field){d[field.name]=schema<std::remove_cvref_t<decltype(std::declval<T>().*Member)>>();}
template<class T>struct Schema<T,std::void_t<decltype(Record<T>::fields())>>{static py::dict get(){py::dict p;std::apply([&](auto... f){(add_property<T>(p,f),...);},Record<T>::fields());if constexpr(std::same_as<T,Metadata>)p["schema_version"]=constant(py::str("1"));return obj_schema(p);}};
template<>struct Schema<analytics::Metric>{static py::dict get(){py::dict known,missing;known["value"]=schema<exact::Fraction>();known["unavailable"]=constant(py::str("0"));missing["value"]=simple("null");py::dict reason;py::list values;for(unsigned i=1;i<=enum_max<analytics::Unavailable>;++i)values.append(write(i));reason["enum"]=values;missing["unavailable"]=reason;py::list choices;choices.append(obj_schema(known));choices.append(obj_schema(missing));py::dict d;d["oneOf"]=choices;return d;}};
py::dict root(std::string_view name,py::dict data){py::dict props;props["schema"]=constant(py::str(name));props["version"]=constant(py::str("1.0"));props["data"]=data;auto result=obj_schema(props);result["$schema"]="https://json-schema.org/draft/2020-12/schema";result["$id"]=py::str(std::string("urn:")+std::string(name)+":1.0");return result;}
}
void bind_schemas(py::module_& m){m.def("schema_catalog",[](){py::dict out;
    out["gig.event"]=root("gig.event",schema<MarketEvent>());
    out["gig.book_snapshot"]=root("gig.book_snapshot",schema<SnapshotWire>());
    py::list metric_types;for(const auto& pair:std::initializer_list<std::pair<const char*,py::dict>>{{"book",schema<BookResult>()},{"flow",schema<FlowResult>()},{"cost",schema<CostResult>()}}){py::dict p;p["kind"]=constant(py::str(pair.first));p["result"]=pair.second;metric_types.append(obj_schema(p));}py::dict metrics;metrics["oneOf"]=metric_types;out["gig.metric_result"]=root("gig.metric_result",metrics);
    out["gig.execution_schedule"]=root("gig.execution_schedule",schema<ScheduleWire>());
    py::dict simulated;simulated["origin"]=constant(py::str("synthetic"));simulated["transformation"]=constant(py::str("simulated"));simulated["state"]=schema<SimulationWire>();out["gig.simulation_output"]=root("gig.simulation_output",obj_schema(simulated));
    out["instrument_rules"]=schema<InstrumentRules>();out["replay_config"]=schema<ReplayConfig>();out["simulation_config"]=schema<simulation::SimConfig>();out["plan_config"]=schema<execution::PlanConfig>();out["cost_config"]=schema<execution::CostConfig>();out["flow_config"]=schema<analytics::FlowConfig>();out["flow_quote"]=schema<analytics::FlowQuote>();out["flow_trade"]=schema<analytics::FlowTrade>();return out;
});}
} // namespace gig::python
