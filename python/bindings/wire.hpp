#pragma once
#include <pybind11/pybind11.h>
#include <charconv>
#include <iomanip>
#include <locale>
#include <sstream>
#include <tuple>
#include "gig/analytics/flow_metrics.hpp"
#include "gig/execution/execution.hpp"
namespace gig::python {
namespace py=pybind11;
struct WireFailure {Error error;};
[[noreturn]] inline void bad(ErrorCode code,std::string_view field){throw WireFailure{{code,field}};}
inline void require(Error error){if(error)throw WireFailure{error};}
template<class T>T take(Result<T> result){if(!result)throw WireFailure{result.error};return std::move(*result.data);}
inline py::dict object(py::handle h,std::initializer_list<const char*> keys){
    if(!PyDict_CheckExact(h.ptr()))bad(ErrorCode::malformed,"wire.object");
    auto d=py::reinterpret_borrow<py::dict>(h);
    if(d.size()!=keys.size())bad(ErrorCode::malformed,"wire.keys");
    for(auto key:keys)if(!d.contains(key))bad(ErrorCode::malformed,"wire.keys");
    return d;
}
inline std::string text(py::handle h,std::size_t max=128){if(!PyUnicode_CheckExact(h.ptr()) || py::len(h)>max)bad(ErrorCode::malformed,"wire.string");return py::cast<std::string>(h);}
inline std::string digits(py::handle h,std::size_t max=40){auto s=text(h,max);if(s.empty() || s=="-0" || s.front()=='+')bad(ErrorCode::malformed,"wire.integer");auto offset=s.front()=='-'?1U:0U;if(offset==s.size() || (s[offset]=='0' && s.size()-offset>1))bad(ErrorCode::malformed,"wire.integer");for(std::size_t i=offset;i<s.size();++i)if(s[i]<'0' || s[i]>'9')bad(ErrorCode::malformed,"wire.integer");return s;}
template<class T,class Enable=void>struct Codec;
template<class T>T read(py::handle h){return Codec<T>::get(h);}
template<class T>py::object write(const T& value){return Codec<T>::put(value);}
template<class T>struct Codec<T,std::enable_if_t<std::is_integral_v<T> && !std::is_same_v<T,bool>>>{
    static T get(py::handle h){auto s=digits(h,20);T n{};auto r=std::from_chars(s.data(),s.data()+s.size(),n);if(r.ec!=std::errc{} || r.ptr!=s.data()+s.size())bad(ErrorCode::invalid_range,"wire.integer_range");return n;}
    static py::object put(T n){return py::str(std::to_string(n));}
};
template<>struct Codec<std::string>{static std::string get(py::handle h){return text(h,33554432);}static py::object put(const std::string& s){return py::str(s);}};
template<>struct Codec<bool>{static bool get(py::handle h){if(!PyBool_Check(h.ptr()))bad(ErrorCode::malformed,"wire.boolean");return py::cast<bool>(h);}static py::object put(bool b){return py::bool_(b);}};
template<class E>inline constexpr unsigned enum_max=255;
#define ENUM_MAX(T,N) template<>inline constexpr unsigned enum_max<T> = N;
ENUM_MAX(MissingReason,3) ENUM_MAX(Side,1) ENUM_MAX(ClockDomain,3) ENUM_MAX(SequenceUnit,1)
ENUM_MAX(Origin,1) ENUM_MAX(Source,4) ENUM_MAX(TransformationKind,4) ENUM_MAX(types::TimestampUnit,3)
ENUM_MAX(ReplacePriority,1) ENUM_MAX(ResetReason,3) ENUM_MAX(SnapshotKind,1) ENUM_MAX(SnapshotCoverage,1) ENUM_MAX(SessionAction,3)
ENUM_MAX(OrderingPolicy,1) ENUM_MAX(InitialBookState,1) ENUM_MAX(analytics::Unavailable,10) ENUM_MAX(analytics::TradeSign,2)
ENUM_MAX(simulation::TimeInForce,2) ENUM_MAX(simulation::ReportKind,5) ENUM_MAX(simulation::RejectReason,3) ENUM_MAX(execution::Algorithm,2) ENUM_MAX(execution::VolumeProfile,1)
#undef ENUM_MAX
template<class E>struct Codec<E,std::enable_if_t<std::is_enum_v<E>>>{static E get(py::handle h){auto n=read<std::uint32_t>(h);if(n>enum_max<E>)bad(ErrorCode::invalid_enum,"wire.enum");return static_cast<E>(n);}static py::object put(E e){return write(static_cast<unsigned>(e));}};
template<class Tag,std::integral R,R Min,bool A>struct Codec<types::Scalar<Tag,R,Min,A>>{
    using T=types::Scalar<Tag,R,Min,A>;static T get(py::handle h){return take(T::make(read<R>(h)));}static py::object put(T x){return write(x.value());}
};
template<std::size_t N>struct Codec<Token<N>>{static Token<N> get(py::handle h){return take(Token<N>::make(text(h,N)));}static py::object put(const Token<N>& s){return py::str(s.view());}};
template<class T>struct Codec<std::optional<T>>{static std::optional<T> get(py::handle h){if(h.is_none())return {};return read<T>(h);}static py::object put(const std::optional<T>& x){return x?write(*x):py::none();}};
template<class T>struct Codec<Available<T>>{
    static Available<T> get(py::handle h){auto d=object(h,{"reason","value"});auto reason=read<MissingReason>(d["reason"]);if(reason==MissingReason::none){if(d["value"].is_none())bad(ErrorCode::inconsistent_metadata,"wire.available");return Available<T>::known(read<T>(d["value"]));}if(!d["value"].is_none())bad(ErrorCode::inconsistent_metadata,"wire.available");return Available<T>::missing(reason);}
    static py::object put(const Available<T>& x){py::dict d;d["reason"]=write(x.reason);d["value"]=x.data?write(*x.data):py::none();return d;}
};
template<class T,std::size_t N>struct Codec<BoundedList<T,N>>{
    static BoundedList<T,N> get(py::handle h){if(!PyList_CheckExact(h.ptr()) || py::len(h)>N)bad(ErrorCode::capacity,"wire.list");BoundedList<T,N> result;for(auto item:py::reinterpret_borrow<py::list>(h))require(result.append(read<T>(item)));return result;}
    static py::object put(const BoundedList<T,N>& x){py::list out;for(std::size_t i=0;i<x.count;++i)out.append(write(*x.items[i]));return out;}
};
template<class T,class A>struct Codec<std::vector<T,A>>{
    static std::vector<T,A> get(py::handle h){if(!PyList_CheckExact(h.ptr()) || py::len(h)>4096)bad(ErrorCode::capacity,"wire.list");std::vector<T,A> out;out.reserve(py::len(h));for(auto x:py::reinterpret_borrow<py::list>(h))out.push_back(read<T>(x));return out;}
    static py::object put(const std::vector<T,A>& x){py::list out;for(const auto& value:x)out.append(write(value));return out;}
};
template<class... Ts>struct Codec<std::variant<Ts...>>{
    using V=std::variant<Ts...>;
    template<std::size_t I=0>static V at(std::size_t index,py::handle h){if constexpr(I<sizeof...(Ts)){if(index==I)return V(std::in_place_index<I>,read<std::variant_alternative_t<I,V>>(h));return at<I+1>(index,h);}else bad(ErrorCode::unsupported,"wire.variant_tag");}
    static V get(py::handle h){auto d=object(h,{"tag","value"});return at(read<std::size_t>(d["tag"]),d["value"]);}
    static py::object put(const V& v){py::dict d;d["tag"]=write(v.index());std::visit([&](const auto& x){d["value"]=write(x);},v);return d;}
};
template<>struct Codec<exact::Fraction>{
    static exact::Wide wide(py::handle h){auto s=digits(h,40);bool negative=s[0]=='-';exact::Wide n=0;for(std::size_t i=negative?1U:0U;i<s.size();++i)n=exact::checked_add(exact::checked_mul(n,10),s[i]-'0');return negative?-n:n;}
    static exact::Fraction get(py::handle h){auto d=object(h,{"numerator","denominator"});return exact::Fraction::ratio(wide(d["numerator"]),wide(d["denominator"]));}
    static py::object put(exact::Fraction f){py::dict d;d["numerator"]=py::str(exact::decimal(f.numerator()));d["denominator"]=py::str(exact::decimal(f.denominator()));return d;}
};
template<>struct Codec<long double>{static py::object put(long double x){std::ostringstream out;out.imbue(std::locale::classic());out<<std::setprecision(std::numeric_limits<long double>::max_digits10)<<x;return py::str(out.str());}};
template<auto Member>struct Field{const char* name;};
template<class T>struct Record;
template<class T,auto M>auto field_read(py::dict d,Field<M> f){return read<std::remove_cvref_t<decltype(std::declval<T>().*M)>>(d[f.name]);}
template<class T,auto M>void field_write(py::dict& d,const T& x,Field<M> f){d[f.name]=write(x.*M);}
template<class T>struct Codec<T,std::void_t<decltype(Record<T>::fields())>>{
    static T get(py::handle h){return std::apply([&](auto... f){auto d=object(h,{f.name...});return T{field_read<T>(d,f)...};},Record<T>::fields());}
    static py::object put(const T& x){py::dict d;std::apply([&](auto... f){(field_write(d,x,f),...);},Record<T>::fields());return d;}
};
#define F(N) Field<&T::N>{#N}
#define RECORD(TYPE,...) template<>struct Record<TYPE>{static auto fields(){using T [[maybe_unused]]=TYPE;return std::tuple{__VA_ARGS__};}};
RECORD(types::UnitScale,F(numerator),F(denominator))
RECORD(Clock,F(domain),F(identity))
RECORD(StreamScope,F(stream),F(session),F(epoch),F(unit))
RECORD(DatasetIdentity,F(identity),F(version),F(license_reference),F(sha256))
RECORD(Transformation,F(kind),F(operation),F(version))
RECORD(ParentArtifact,F(identity),F(sha256))
RECORD(Provenance,F(dataset),F(origin),F(source),F(generator_seed),F(lineage),F(parents))
RECORD(Metadata,F(schema_version),F(instrument),F(venue),F(scope),F(sequence),F(subevent_index),F(subevent_count),F(event_time),F(receive_time),F(source_record),F(capture_ordinal),F(provenance))
RECORD(InstrumentRules,F(instrument),F(venue),F(minimum_price),F(maximum_price),F(maximum_quantity),F(tick_size),F(lot_size))
RECORD(AddOrder,F(order_id),F(side),F(price_ticks),F(quantity))
RECORD(CancelAll)
RECORD(CancelOrder,F(order_id),F(amount))
RECORD(ReplaceOrder,F(old_order_id),F(new_order_id),F(side),F(price_ticks),F(quantity),F(priority))
RECORD(TradePrint,F(price_ticks),F(quantity),F(aggressor))
RECORD(BookExecution,F(resting_order_id),F(resting_side),F(price_ticks),F(quantity))
RECORD(Trade,F(details))
RECORD(QuoteLevel,F(price_ticks),F(quantity))
RECORD(Quote,F(bid),F(ask))
RECORD(BookReset,F(reason),F(next_epoch))
RECORD(SnapshotOrder,F(order),F(priority_index))
RECORD(SnapshotLevel,F(side),F(price_ticks),F(quantity))
RECORD(SequenceBoundary,F(scope),F(sequence),F(last_subevent),F(subevent_count))
RECORD(Snapshot,F(kind),F(coverage),F(depth),F(orders),F(levels),F(boundaries))
RECORD(SessionEvent,F(action),F(reason))
RECORD(UnsupportedEvent,F(wire_type))
RECORD(MarketEvent,F(metadata),F(payload))
RECORD(BookSession,F(session),F(epoch))
RECORD(BookLimits,F(max_orders),F(max_levels),F(max_snapshot_depth))
RECORD(DepthLevel,F(price_ticks),F(quantity),F(order_count))
RECORD(StreamStart,F(venue),F(scope),F(dataset),F(dataset_version),F(first_sequence),F(rank))
RECORD(ReplayConfig,F(run_id),F(session),F(streams),F(ordering),F(timestamp_clock),F(additional_instruments),F(max_journal_records),F(initial_state))
RECORD(analytics::Metric,F(value),F(unavailable))
RECORD(analytics::SnapshotReference,F(run_id),F(journal_prefix),F(revision),F(rules),F(session))
RECORD(analytics::FlowQuote,F(source),F(timestamp),F(utc_clock),F(bid),F(ask))
RECORD(analytics::FlowTrade,F(source),F(timestamp),F(utc_clock),F(price),F(quantity))
RECORD(analytics::FlowConfig,F(utc_clock),F(window),F(quote_lag),F(horizon),F(max_quote_age),F(sampling_interval),F(continuity_complete),F(complete_top_updates))
RECORD(analytics::SignedTrade,F(source),F(sign),F(effective_spread),F(realized_spread),F(price_impact))
RECORD(analytics::FlowSummary,F(ofi),F(trade_intensity),F(quote_intensity),F(window_return),F(realized_variance),F(realized_volatility))
RECORD(simulation::SimOrder,F(id),F(side),F(limit),F(quantity),F(tif),F(post_only))
RECORD(simulation::Latency,F(base),F(jitter))
RECORD(simulation::SimConfig,F(run_id),F(rules),F(seed),F(arrival),F(cancel),F(acknowledgment),F(execution),F(max_orders),F(max_events),F(max_fills),F(max_commands),F(max_reports))
RECORD(simulation::Resting,F(order),F(priority),F(source_command))
RECORD(simulation::SimFill,F(run_id),F(seed),F(maker),F(taker),F(taker_side),F(price),F(quantity),F(matched_at),F(reported_at),F(maker_command),F(taker_command))
RECORD(simulation::ClientReport,F(run_id),F(kind),F(reason),F(order),F(delivered_at),F(quantity),F(fill_index))
RECORD(simulation::Conservation,F(submitted),F(executed_sides),F(cancelled),F(expired),F(rejected))
RECORD(simulation::QueuePosition,F(orders_ahead),F(quantity_ahead))
RECORD(execution::PlanConfig,F(run_id),F(assumptions_id),F(rules),F(side),F(limit),F(target),F(inventory_limit),F(max_child),F(start),F(end),F(bins),F(first_child_id),F(tif),F(post_only))
RECORD(execution::ChildSlice,F(decision_time),F(order))
RECORD(execution::VolumePoint,F(available_at),F(lots),F(source_artifact),F(ordinal))
RECORD(execution::PriceBenchmark,F(midpoint),F(available_at),F(source_artifact))
RECORD(execution::CostFill,F(fill),F(child),F(decision_time),F(decision_benchmark),F(fee_ticks_per_lot))
RECORD(execution::CostConfig,F(run_id),F(simulation_run_id),F(rules),F(side),F(target),F(arrival),F(terminal),F(as_of))
RECORD(execution::CostSummary,F(filled_lots),F(unfilled_lots),F(execution_vwap),F(gross_notional),F(delay_cost),F(spread_cost),F(fees),F(slippage),F(opportunity_cost),F(implementation_shortfall),F(currency_shortfall))
#undef RECORD
#undef F
template<class T>struct Record<Timestamp<T>>{static auto fields(){using U=Timestamp<T>;return std::tuple{Field<&U::nanoseconds>{"nanoseconds"},Field<&U::clock>{"clock"},Field<&U::precision>{"precision"}};}};
inline py::object envelope(std::string_view schema,py::object data){py::dict d;d["schema"]=py::str(schema);d["version"]="1.0";d["data"]=std::move(data);return d;}
inline py::handle body(py::handle h,std::string_view schema){auto d=object(h,{"schema","version","data"});if(text(d["schema"],64)!=schema)bad(ErrorCode::identity_mismatch,"wire.schema");if(text(d["version"],16)!="1.0")bad(ErrorCode::unsupported,"wire.version");return d["data"];}
inline py::dict ok(py::object value){py::dict d;d["ok"]=true;d["value"]=std::move(value);return d;}
inline py::dict error(Error e){py::dict result,detail;detail["code"]=write(static_cast<unsigned>(e.code));detail["field"]=py::str(e.field);detail["index"]=e.index?write(*e.index):py::none();result["ok"]=false;result["error"]=detail;return result;}
template<class F>py::dict api(F&& f){try{return ok(f());}catch(const WireFailure& e){return error(e.error);}catch(const exact::ArithmeticFailure& e){return error({e.code,"wire.exact_capacity"});}catch(const std::bad_alloc&){return error({ErrorCode::resource_exhausted,"binding.allocation"});}catch(py::error_already_set& e){const bool memory=e.matches(PyExc_MemoryError);e.restore();PyErr_Clear();return error({memory?ErrorCode::resource_exhausted:ErrorCode::malformed,"wire.python_type"});}catch(const std::exception&){return error({ErrorCode::inconsistent_state,"binding.internal"});}}
// Allocate publication envelope BEFORE a mutation can commit.
template<class F>py::dict mutate(F&& f){auto success=ok(py::none());return [&](){try{auto e=f();return e?error(e):success;}catch(const WireFailure& e){return error(e.error);}catch(const exact::ArithmeticFailure& e){return error({e.code,"wire.exact_capacity"});}catch(const std::bad_alloc&){return error({ErrorCode::resource_exhausted,"binding.allocation"});}catch(py::error_already_set& e){const bool memory=e.matches(PyExc_MemoryError);e.restore();PyErr_Clear();return error({memory?ErrorCode::resource_exhausted:ErrorCode::malformed,"wire.python_type"});}catch(const std::exception&){return error({ErrorCode::inconsistent_state,"binding.internal"});}}();}
py::object snapshot_wire(const ReplaySnapshot&);
ReplaySnapshot snapshot_read(py::handle);
py::object book_metrics_wire(const analytics::BookMetrics&);
py::object flow_metrics_wire(const analytics::FlowMetrics&);
py::object schedule_wire(const execution::Schedule&);
execution::Schedule schedule_read(py::handle);
py::object costs_wire(const execution::CostReport&);
} // namespace gig::python
