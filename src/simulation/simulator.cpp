#include "gig/simulation/simulator.hpp"
#include "gig/detail/canonical.hpp"
#include <algorithm>
#include <cassert>
#include <variant>
namespace gig::simulation {
namespace {
struct Failure{Error error;};
[[noreturn]] void fail(ErrorCode code,std::string_view field){throw Failure{{code,field}};}
std::uint64_t add(std::uint64_t a,std::uint64_t b){auto r=types::detail::add(a,b);if(!r)fail(r.error.code,"simulation.quantity");return *r.data;}
QuantityLots lots(std::uint64_t n){return *QuantityLots::make(n).data;}
SimulationTime time(std::int64_t n){auto r=SimulationTime::make(n);if(!r)fail(r.error.code,"simulation.time");return *r.data;}
struct Arrival{SimOrder order;std::size_t command;};
struct Cancellation{OrderId id;};
using EventPayload=std::variant<Arrival,Cancellation,ClientReport>;
struct Scheduled{SimulationTime when;std::uint64_t ordinal;EventPayload payload;};
struct Command{SimulationTime when;std::optional<SimOrder> order;std::optional<OrderId> cancel;};
bool earlier(const Scheduled& a,const Scheduled& b){return a.when<b.when || (a.when==b.when && a.ordinal<b.ordinal);}
Error valid_order(const SimOrder& o,const InstrumentRules& r){
    if(o.side!=Side::buy && o.side!=Side::sell)return {ErrorCode::invalid_enum,"simulation.side"};
    if(o.tif!=TimeInForce::gtc && o.tif!=TimeInForce::ioc && o.tif!=TimeInForce::fok)return {ErrorCode::invalid_enum,"simulation.tif"};
    if(o.quantity.value()==0 || o.quantity>r.maximum_quantity || o.limit<r.minimum_price || o.limit>r.maximum_price)return {ErrorCode::invalid_range,"simulation.order"};
    if(o.post_only && o.tif!=TimeInForce::gtc)return {ErrorCode::unsupported,"simulation.post_only_tif"};
    return {};
}
void write_order(detail::CanonicalWriter& w,const SimOrder& o){w.number(o.id.value());w.number(static_cast<unsigned>(o.side));w.number(o.limit.value());w.number(o.quantity.value());w.number(static_cast<unsigned>(o.tif));w.number(static_cast<unsigned>(o.post_only));}
void write_report(detail::CanonicalWriter& w,const ClientReport& r){w.token(r.run_id);w.number(static_cast<unsigned>(r.kind));w.number(static_cast<unsigned>(r.reason));w.number(r.order.value());w.number(r.delivered_at.value());w.number(r.quantity.value());w.number(static_cast<unsigned>(r.fill_index.has_value()));if(r.fill_index)w.number(*r.fill_index);}
}
struct Simulator::State {
    SimulationTime now{*SimulationTime::make(0).data};std::uint64_t rng,ordinal{},priority{};Conservation ledger;
    std::pmr::vector<Resting> orders;std::pmr::vector<Scheduled> queue;std::pmr::vector<SimFill> fills;
    std::pmr::vector<ClientReport> reports;std::pmr::vector<OrderId> issued;std::pmr::vector<Command> commands;
    State(std::uint64_t seed,std::pmr::memory_resource* r):rng(seed),orders(r),queue(r),fills(r),reports(r),issued(r),commands(r){}
    State(const State& s,std::pmr::memory_resource* r):now(s.now),rng(s.rng),ordinal(s.ordinal),priority(s.priority),ledger(s.ledger),orders(s.orders,r),queue(s.queue,r),fills(s.fills,r),reports(s.reports,r),issued(s.issued,r),commands(s.commands,r){}
    SimulationTime after(SimulationTime t,const Latency& latency){
        rng^=rng<<13U;rng^=rng>>7U;rng^=rng<<17U;
        const auto jitter=rng%(static_cast<std::uint64_t>(latency.jitter.value())+1U);
        auto duration=types::detail::add(latency.base.value(),static_cast<std::int64_t>(jitter));if(!duration)fail(ErrorCode::overflow,"simulation.latency");
        auto result=types::detail::add(t.value(),*duration.data);if(!result)fail(ErrorCode::overflow,"simulation.time");return time(*result.data);
    }
    void schedule(SimulationTime at,EventPayload payload,const SimConfig& c){
        if(queue.size()>=c.max_events)fail(ErrorCode::capacity,"simulation.events");
        if(ordinal==UINT64_MAX)fail(ErrorCode::overflow,"simulation.ordinal");
        Scheduled s{at,ordinal++,std::move(payload)};auto position=std::lower_bound(queue.begin(),queue.end(),s,earlier);queue.insert(position,std::move(s));
    }
    void report(ReportKind kind,RejectReason reason,OrderId id,std::uint64_t quantity,const SimConfig& c,std::optional<std::size_t> index={}){
        const auto at=after(now,kind==ReportKind::fill?c.execution:c.acknowledgment);
        schedule(at,ClientReport{c.run_id,kind,reason,id,at,lots(quantity),index},c);
        if(index){
            // One modeled execution-report latency per fill, shared by both counterparties.
            // Keep the original taker-first tie order and RNG draw sequence.
            auto& fill=fills[*index];fill.reported_at=at;
            schedule(at,ClientReport{c.run_id,kind,reason,fill.maker,at,lots(quantity),index},c);
        }
    }
    std::optional<std::size_t> best(const SimOrder& incoming)const{
        std::optional<std::size_t> result;
        for(std::size_t i=0;i<orders.size();++i){const auto& o=orders[i];
            if(o.order.side==incoming.side || (incoming.side==Side::buy?o.order.limit>incoming.limit:o.order.limit<incoming.limit))continue;
            if(!result || (incoming.side==Side::buy?o.order.limit<orders[*result].order.limit:o.order.limit>orders[*result].order.limit) || (o.order.limit==orders[*result].order.limit && o.priority<orders[*result].priority))result=i;
        }return result;
    }
    void arrive(Arrival arrival,const SimConfig& c){
        auto incoming=arrival.order;const auto requested=incoming.quantity.value();
        bool reject=false;RejectReason reason=RejectReason::none;
        if(incoming.post_only && best(incoming)){reject=true;reason=RejectReason::post_only_would_take;}
        if(incoming.tif==TimeInForce::fok){std::uint64_t available=0;for(const auto& o:orders){
            if(o.order.side!=incoming.side && (incoming.side==Side::buy?o.order.limit<=incoming.limit:o.order.limit>=incoming.limit))available+=std::min(requested-available,o.order.quantity.value());
            if(available==requested)break;
        }if(available<requested){reject=true;reason=RejectReason::fok_insufficient;}}
        if(reject){ledger.rejected=add(ledger.rejected,requested);report(ReportKind::rejected,reason,incoming.id,requested,c);return;}
        report(ReportKind::accepted,RejectReason::none,incoming.id,requested,c);
        auto remaining=requested;
        while(remaining){auto index=best(incoming);if(!index)break;auto& maker=orders[*index];const auto quantity=std::min(remaining,maker.order.quantity.value());
            if(fills.size()>=c.max_fills)fail(ErrorCode::capacity,"simulation.fills");
            ledger.executed_sides=add(ledger.executed_sides,add(quantity,quantity));
            fills.push_back({c.run_id,c.seed,maker.order.id,incoming.id,incoming.side,maker.order.limit,lots(quantity),now,now,maker.source_command,arrival.command});
            report(ReportKind::fill,RejectReason::none,incoming.id,quantity,c,fills.size()-1);
            remaining-=quantity;maker.order.quantity=lots(maker.order.quantity.value()-quantity);if(maker.order.quantity.value()==0)orders.erase(orders.begin()+static_cast<std::ptrdiff_t>(*index));
        }
        if(remaining){
            if(incoming.tif==TimeInForce::ioc){ledger.expired=add(ledger.expired,remaining);report(ReportKind::expired,RejectReason::none,incoming.id,remaining,c);}
            else {if(incoming.tif==TimeInForce::fok)fail(ErrorCode::inconsistent_state,"simulation.fok");
                if(orders.size()>=c.max_orders)fail(ErrorCode::capacity,"simulation.orders");
                if(priority==UINT64_MAX)fail(ErrorCode::overflow,"simulation.priority");
                incoming.quantity=lots(remaining);orders.push_back({incoming,priority++,arrival.command});}
        }
    }
    void cancel(OrderId id,const SimConfig& c){
        auto i=std::find_if(orders.begin(),orders.end(),[&](const auto& o){return o.order.id==id;});
        if(i==orders.end()){report(ReportKind::cancel_rejected,RejectReason::not_active,id,0,c);return;}
        const auto quantity=i->order.quantity.value();ledger.cancelled=add(ledger.cancelled,quantity);orders.erase(i);report(ReportKind::cancelled,RejectReason::none,id,quantity,c);
    }
    void process(SimulationTime target,const SimConfig& c){
        while(!queue.empty() && queue.front().when<=target){auto event=queue.front();queue.erase(queue.begin());now=event.when;
            std::visit([&](const auto& payload){using T=std::decay_t<decltype(payload)>;
                if constexpr(std::same_as<T,Arrival>)arrive(payload,c);
                else if constexpr(std::same_as<T,Cancellation>)cancel(payload.id,c);
                else {if(reports.size()>=c.max_reports)fail(ErrorCode::capacity,"simulation.reports");reports.push_back(payload);}
            },event.payload);
        }now=target;
    }
};
void Simulator::Deleter::operator()(State* p)const noexcept{if(p){std::pmr::polymorphic_allocator<State> a(resource);a.delete_object(p);}}
Simulator::Simulator(SimConfig c,std::pmr::memory_resource* r,StatePtr s)noexcept:config_(c),resource_(r),state_(std::move(s)){}
Simulator::~Simulator()=default;Simulator::Simulator(Simulator&&)noexcept=default;Simulator& Simulator::operator=(Simulator&&)noexcept=default;
Result<Simulator> Simulator::create(SimConfig c,std::pmr::memory_resource* r)noexcept{
    if(auto e=validate(c.rules))return Result<Simulator>::failure(e.code,e.field);
    if(!r || c.seed==0)return Result<Simulator>::failure(ErrorCode::invalid_range,"simulation.config");
    for(auto n:{c.max_orders,c.max_events,c.max_fills,c.max_commands,c.max_reports})if(n==0 || n>100000)return Result<Simulator>::failure(ErrorCode::capacity,"simulation.limits");
    for(const auto l:{c.arrival,c.cancel,c.acknowledgment,c.execution})if(!types::detail::add(l.base.value(),l.jitter.value()))return Result<Simulator>::failure(ErrorCode::overflow,"simulation.latency");
    try{std::pmr::polymorphic_allocator<State> a(r);return Result<Simulator>::success(Simulator(c,r,StatePtr(a.new_object<State>(c.seed,r),Deleter{r})));}
    catch(const std::bad_alloc&){return Result<Simulator>::failure(ErrorCode::resource_exhausted,"simulation.create");}
}
Error Simulator::command(SimulationTime at,std::optional<SimOrder> order,std::optional<OrderId> cancel)noexcept{
    if(at<state_->now)return {ErrorCode::ordering_error,"simulation.past_decision"};
    if(order){if(auto e=valid_order(*order,config_.rules))return e;if(std::find(state_->issued.begin(),state_->issued.end(),order->id)!=state_->issued.end())return {ErrorCode::duplicate,"simulation.order_id"};}
    try{
        std::pmr::polymorphic_allocator<State> a(resource_);StatePtr staged(a.new_object<State>(*state_,resource_),Deleter{resource_});
        if(staged->commands.size()>=config_.max_commands)fail(ErrorCode::capacity,"simulation.commands");
        staged->process(at,config_);const auto index=staged->commands.size();staged->commands.push_back({at,order,cancel});
        if(order){std::size_t pending=0;for(const auto& e:staged->queue)if(std::holds_alternative<Arrival>(e.payload))++pending;
            if(pending+staged->orders.size()>=config_.max_orders)fail(ErrorCode::capacity,"simulation.orders");
            staged->ledger.submitted=add(staged->ledger.submitted,order->quantity.value());staged->issued.push_back(order->id);
            staged->schedule(staged->after(at,config_.arrival),Arrival{*order,index},config_);
        }else if(cancel)staged->schedule(staged->after(at,config_.cancel),Cancellation{*cancel},config_);
        state_.swap(staged);assert(!check_invariants());return {};
    }catch(const Failure& e){return e.error;}catch(const std::bad_alloc&){return {ErrorCode::resource_exhausted,"simulation.stage"};}
}
Error Simulator::submit_at(SimulationTime at,const SimOrder& o)noexcept{return command(at,o,{});}
Error Simulator::cancel_at(SimulationTime at,OrderId id)noexcept{return command(at,{},id);}
Error Simulator::advance_to(SimulationTime at)noexcept{return command(at,{},{});}
SimulationTime Simulator::now()const noexcept{return state_->now;}
Conservation Simulator::conservation()const noexcept{return state_->ledger;}
std::span<const Resting> Simulator::exchange_orders()const noexcept{return state_->orders;}
std::span<const SimFill> Simulator::exchange_fills()const noexcept{return state_->fills;}
std::span<const ClientReport> Simulator::client_reports()const noexcept{return state_->reports;}
std::optional<QueuePosition> Simulator::exchange_queue_position(OrderId id)const noexcept{
    const auto& v=state_->orders;auto found=std::find_if(v.begin(),v.end(),[&](const auto& x){return x.order.id==id;});if(found==v.end())return {};
    QueuePosition result{};for(const auto& x:v)if(x.order.side==found->order.side && x.order.limit==found->order.limit && x.priority<found->priority){++result.orders_ahead;result.quantity_ahead+=x.order.quantity.value();}return result;
}
Error Simulator::check_invariants()const noexcept{
    const auto& s=*state_;if(s.orders.size()>config_.max_orders || s.queue.size()>config_.max_events || s.fills.size()>config_.max_fills || s.commands.size()>config_.max_commands || s.reports.size()>config_.max_reports)return {ErrorCode::inconsistent_state,"simulation.limits"};
    std::uint64_t outstanding=0;std::size_t pending_count=0;
    for(std::size_t i=0;i<s.orders.size();++i){const auto& o=s.orders[i];if(valid_order(o.order,config_.rules) || o.order.tif!=TimeInForce::gtc || o.priority>=s.priority || (i && s.orders[i-1].priority>=o.priority) || o.source_command>=s.commands.size())return {ErrorCode::inconsistent_state,"simulation.order"};
        for(std::size_t j=0;j<i;++j)if(o.order.id==s.orders[j].order.id || o.priority==s.orders[j].priority || (o.order.side!=s.orders[j].order.side && (o.order.side==Side::buy?o.order.limit>=s.orders[j].order.limit:o.order.limit<=s.orders[j].order.limit)))return {ErrorCode::inconsistent_state,"simulation.priority_or_cross"};
        auto sum=types::detail::add(outstanding,o.order.quantity.value());if(!sum)return {ErrorCode::overflow,"simulation.invariant"};outstanding=*sum.data;
    }
    for(std::size_t i=0;i<s.queue.size();++i){const auto& e=s.queue[i];if(e.when<s.now || (i && !earlier(s.queue[i-1],e)))return {ErrorCode::inconsistent_state,"simulation.scheduler"};
        if(auto p=std::get_if<Arrival>(&e.payload)){
            ++pending_count;
            if(valid_order(p->order,config_.rules) || p->command>=s.commands.size() || std::any_of(s.orders.begin(),s.orders.end(),[&](const auto& o){return o.order.id==p->order.id;}))return {ErrorCode::inconsistent_state,"simulation.pending"};
            for(std::size_t j=0;j<i;++j)if(auto other=std::get_if<Arrival>(&s.queue[j].payload);other && other->order.id==p->order.id)return {ErrorCode::duplicate,"simulation.pending"};
            auto sum=types::detail::add(outstanding,p->order.quantity.value());if(!sum)return {ErrorCode::overflow,"simulation.invariant"};outstanding=*sum.data;}
    }
    if(pending_count+s.orders.size()>config_.max_orders)return {ErrorCode::inconsistent_state,"simulation.pending_limit"};
    std::uint64_t executed=0;
    for(const auto& f:s.fills){auto twice=types::detail::add(f.quantity.value(),f.quantity.value());if(!twice)return {ErrorCode::overflow,"simulation.fill_total"};auto sum=types::detail::add(executed,*twice.data);if(!sum)return {ErrorCode::overflow,"simulation.fill_total"};executed=*sum.data;}
    if(executed!=s.ledger.executed_sides)return {ErrorCode::inconsistent_state,"simulation.fill_total"};
    auto total=types::detail::add(outstanding,s.ledger.executed_sides);if(!total)return {ErrorCode::overflow,"simulation.invariant"};
    for(auto n:{s.ledger.cancelled,s.ledger.expired,s.ledger.rejected}){total=types::detail::add(*total.data,n);if(!total)return {ErrorCode::overflow,"simulation.invariant"};}
    if(*total.data!=s.ledger.submitted)return {ErrorCode::inconsistent_state,"simulation.conservation"};
    for(const auto& r:s.reports)if(r.delivered_at>s.now || (r.fill_index && *r.fill_index>=s.fills.size()))return {ErrorCode::inconsistent_state,"simulation.report"};
    for(const auto& f:s.fills)if(f.quantity.value()==0 || f.matched_at>s.now || f.reported_at<f.matched_at || f.maker_command>=s.commands.size() || f.taker_command>=s.commands.size())return {ErrorCode::inconsistent_state,"simulation.fill"};
    return {};
}
Result<std::pmr::string> Simulator::canonical()const noexcept{
    try{std::pmr::string out(resource_);detail::CanonicalWriter w(out);w.raw("gig.simulated.v2;");w.token(config_.run_id);w.number(config_.seed);detail::canonical_rules(w,config_.rules);
        for(const auto l:{config_.arrival,config_.cancel,config_.acknowledgment,config_.execution}){w.number(l.base.value());w.number(l.jitter.value());}
        for(auto n:{config_.max_orders,config_.max_events,config_.max_fills,config_.max_commands,config_.max_reports})w.number(n);
        w.number(state_->now.value());w.number(state_->rng);w.number(state_->ordinal);w.number(state_->priority);
        const auto& l=state_->ledger;for(auto n:{l.submitted,l.executed_sides,l.cancelled,l.expired,l.rejected})w.number(n);
        w.number(state_->commands.size());for(const auto& c:state_->commands){w.number(c.when.value());w.number(static_cast<unsigned>(c.order.has_value()));if(c.order)write_order(w,*c.order);w.number(static_cast<unsigned>(c.cancel.has_value()));if(c.cancel)w.number(c.cancel->value());}
        w.number(state_->orders.size());for(const auto& o:state_->orders){write_order(w,o.order);w.number(o.priority);w.number(o.source_command);}
        w.number(state_->issued.size());for(auto id:state_->issued)w.number(id.value());
        w.number(state_->queue.size());for(const auto& e:state_->queue){w.number(e.when.value());w.number(e.ordinal);w.number(e.payload.index());std::visit([&](const auto& p){using T=std::decay_t<decltype(p)>;if constexpr(std::same_as<T,Arrival>){write_order(w,p.order);w.number(p.command);}else if constexpr(std::same_as<T,Cancellation>)w.number(p.id.value());else write_report(w,p);},e.payload);}
        w.number(state_->fills.size());for(const auto& f:state_->fills){w.token(f.run_id);w.number(f.seed);w.number(f.maker.value());w.number(f.taker.value());w.number(static_cast<unsigned>(f.taker_side));w.number(f.price.value());w.number(f.quantity.value());w.number(f.matched_at.value());w.number(f.reported_at.value());w.number(f.maker_command);w.number(f.taker_command);}
        w.number(state_->reports.size());for(const auto& r:state_->reports)write_report(w,r);
        return Result<std::pmr::string>::success(std::move(out));
    }catch(const std::bad_alloc&){return Result<std::pmr::string>::failure(ErrorCode::resource_exhausted,"simulation.canonical");}
}
} // namespace gig::simulation
