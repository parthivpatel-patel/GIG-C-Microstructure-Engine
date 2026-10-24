#include "gig/execution/execution.hpp"
#include <algorithm>
namespace gig::execution {
namespace {
using exact::Wide;using exact::Unsigned;
struct Failure{Error error;};
[[noreturn]]void fail(ErrorCode c,std::string_view field){throw Failure{{c,field}};}
Error validate_plan(const PlanConfig& c,std::pmr::memory_resource* r){
    if(auto e=validate(c.rules))return e;
    if(!r || c.target.value()==0 || c.target>c.inventory_limit || c.max_child.value()==0 || c.max_child>c.rules.maximum_quantity || c.bins==0 || c.bins>4096 || c.end<=c.start || c.end.value()-c.start.value()<c.bins)return {ErrorCode::invalid_range,"execution.config"};
    if(c.side!=Side::buy && c.side!=Side::sell)return {ErrorCode::invalid_enum,"execution.side"};
    if(c.limit<c.rules.minimum_price || c.limit>c.rules.maximum_price)return {ErrorCode::invalid_range,"execution.limit"};
    if(c.tif!=simulation::TimeInForce::gtc && c.tif!=simulation::TimeInForce::ioc && c.tif!=simulation::TimeInForce::fok)return {ErrorCode::invalid_enum,"execution.tif"};
    if(c.post_only && c.tif!=simulation::TimeInForce::gtc)return {ErrorCode::unsupported,"execution.post_only_tif"};
    return {};
}
void append(std::pmr::vector<ChildSlice>& out,const PlanConfig& c,SimulationTime time,std::uint64_t quantity){
    const auto chunks=quantity/c.max_child.value()+(quantity%c.max_child.value()!=0?1U:0U);
    if(chunks>4096-out.size())fail(ErrorCode::capacity,"execution.children");
    while(quantity){const auto q=std::min(quantity,c.max_child.value());auto id=types::detail::add(c.first_child_id.value(),static_cast<std::uint64_t>(out.size()));if(!id)fail(ErrorCode::overflow,"execution.child_id");
        out.push_back({time,{*OrderId::make(*id.data).data,c.side,c.limit,*QuantityLots::make(q).data,c.tif,c.post_only}});quantity-=q;}
}
Result<Schedule> weighted(PlanConfig c,std::span<const std::uint64_t> weights,Available<Identity> artifact,Algorithm algorithm,bool oracle,std::pmr::memory_resource* resource,Available<SimulationTime> profile_time=Available<SimulationTime>::missing(MissingReason::not_applicable)){
    if(auto e=validate_plan(c,resource))return Result<Schedule>::failure(e.code,e.field);
    if(weights.size()!=c.bins)return Result<Schedule>::failure(ErrorCode::invalid_range,"execution.weights");
    try{
        Unsigned total=0;for(auto w:weights)total+=w;if(!total)return Result<Schedule>::failure(ErrorCode::invalid_range,"execution.zero_volume_profile");
        std::pmr::vector<std::uint64_t> allocations(resource);std::pmr::vector<std::pair<Unsigned,std::size_t>> remainder(resource);
        allocations.reserve(c.bins);remainder.reserve(c.bins);std::uint64_t distributed=0;
        for(std::size_t i=0;i<weights.size();++i){auto product=static_cast<Unsigned>(c.target.value())*weights[i];auto q=static_cast<std::uint64_t>(product/total);allocations.push_back(q);distributed+=q;remainder.emplace_back(product%total,i);}
        std::sort(remainder.begin(),remainder.end(),[](auto a,auto b){return a.first>b.first || (a.first==b.first && a.second<b.second);});
        const auto extra=c.target.value()-distributed;if(extra>remainder.size())fail(ErrorCode::inconsistent_state,"execution.apportionment");
        for(std::uint64_t i=0;i<extra;++i)++allocations[remainder[static_cast<std::size_t>(i)].second];
        std::pmr::vector<ChildSlice> slices(resource);
        for(std::size_t i=0;i<weights.size();++i){const auto offset=static_cast<Wide>(c.end.value()-c.start.value())*static_cast<Wide>(i)/c.bins;const auto time=*SimulationTime::make(c.start.value()+static_cast<std::int64_t>(offset)).data;append(slices,c,time,allocations[i]);}
        return Result<Schedule>::success(Schedule(c,algorithm,oracle,artifact,std::move(slices),std::pmr::vector<std::uint64_t>(weights.begin(),weights.end(),resource),std::pmr::vector<VolumePoint>(resource),0,1,profile_time));
    }catch(const Failure& e){return Result<Schedule>::failure(e.error.code,e.error.field);}catch(const std::bad_alloc&){return Result<Schedule>::failure(ErrorCode::resource_exhausted,"execution.plan");}
}
}
Result<Schedule> twap(PlanConfig c,std::pmr::memory_resource* r)noexcept{
    if(auto e=validate_plan(c,r))return Result<Schedule>::failure(e.code,e.field);
    try{std::pmr::vector<std::uint64_t> weights(c.bins,1,r);return weighted(c,weights,Available<Identity>::missing(MissingReason::not_applicable),Algorithm::twap,false,r);}catch(const std::bad_alloc&){return Result<Schedule>::failure(ErrorCode::resource_exhausted,"execution.twap");}
}
Result<Schedule> vwap(PlanConfig c,std::span<const std::uint64_t> weights,Identity artifact,SimulationTime available,VolumeProfile profile,std::pmr::memory_resource* r)noexcept{
    if(profile!=VolumeProfile::ex_ante_forecast && profile!=VolumeProfile::oracle_hindsight)return Result<Schedule>::failure(ErrorCode::invalid_enum,"execution.profile_kind");
    if(profile==VolumeProfile::ex_ante_forecast && available>c.start)return Result<Schedule>::failure(ErrorCode::ordering_error,"execution.future_volume_profile");
    return weighted(c,weights,Available<Identity>::known(artifact),Algorithm::vwap,profile==VolumeProfile::oracle_hindsight,r,Available<SimulationTime>::known(available));
}
Result<Schedule> pov(PlanConfig c,std::span<const VolumePoint> volume,std::uint64_t numerator,std::uint64_t denominator,std::pmr::memory_resource* r)noexcept{
    if(auto e=validate_plan(c,r))return Result<Schedule>::failure(e.code,e.field);
    if(denominator==0 || numerator>denominator || volume.size()>4096)return Result<Schedule>::failure(ErrorCode::invalid_range,"execution.participation");
    try{
        std::pmr::vector<ChildSlice> slices(r);std::uint64_t cumulative=0,submitted=0;
        for(std::size_t i=0;i<volume.size();++i){const auto& v=volume[i];if(v.available_at<c.start || v.available_at>c.end || (i && (v.available_at<volume[i-1].available_at || v.ordinal<=volume[i-1].ordinal)))fail(ErrorCode::ordering_error,"execution.causal_volume");
            auto sum=types::detail::add(cumulative,v.lots.value());if(!sum)fail(ErrorCode::overflow,"execution.volume");cumulative=*sum.data;
            auto budget=static_cast<std::uint64_t>(static_cast<Unsigned>(cumulative)*numerator/denominator);auto wanted=std::min(c.target.value(),budget);
            append(slices,c,v.available_at,wanted-submitted);submitted=wanted;
        }
        return Result<Schedule>::success(Schedule(c,Algorithm::pov,false,Available<Identity>::missing(MissingReason::not_applicable),std::move(slices),std::pmr::vector<std::uint64_t>(r),std::pmr::vector<VolumePoint>(volume.begin(),volume.end(),r),numerator,denominator));
    }catch(const Failure& e){return Result<Schedule>::failure(e.error.code,e.error.field);}catch(const std::bad_alloc&){return Result<Schedule>::failure(ErrorCode::resource_exhausted,"execution.pov");}
}
Result<ExecutionRun> simulate(const Schedule& plan,simulation::SimConfig config,std::span<const simulation::SimOrder> liquidity,SimulationTime finish,std::pmr::memory_resource* r)noexcept{
    if(config.rules!=plan.config().rules || config.run_id!=plan.config().run_id || finish<plan.config().end || liquidity.size()>4096)return Result<ExecutionRun>::failure(ErrorCode::identity_mismatch,"execution.simulation_config");
    try{
        auto rebuilt=[&]()->Result<Schedule>{
            switch(plan.algorithm()){
                case Algorithm::twap:return twap(plan.config(),r);
                case Algorithm::vwap:
                    if(!plan.profile().data || !plan.profile_available_at().data)return Result<Schedule>::failure(ErrorCode::missing_metadata,"execution.profile");
                    return vwap(plan.config(),plan.weights(),*plan.profile().data,*plan.profile_available_at().data,plan.oracle()?VolumeProfile::oracle_hindsight:VolumeProfile::ex_ante_forecast,r);
                case Algorithm::pov:return pov(plan.config(),plan.volumes(),plan.participation_numerator(),plan.participation_denominator(),r);
            }return Result<Schedule>::failure(ErrorCode::invalid_enum,"execution.algorithm");
        }();
        if(!rebuilt)return Result<ExecutionRun>::failure(rebuilt.error.code,rebuilt.error.field);
        if(plan.children()!=rebuilt.data->children() || plan.weights()!=rebuilt.data->weights() || plan.volumes()!=rebuilt.data->volumes() || plan.profile()!=rebuilt.data->profile() || plan.profile_available_at()!=rebuilt.data->profile_available_at() || plan.oracle()!=rebuilt.data->oracle() || plan.participation_numerator()!=rebuilt.data->participation_numerator() || plan.participation_denominator()!=rebuilt.data->participation_denominator())return Result<ExecutionRun>::failure(ErrorCode::inconsistent_state,"execution.plan");
        auto model=simulation::Simulator::create(config,r);if(!model)return Result<ExecutionRun>::failure(model.error.code,model.error.field);
        for(const auto& o:liquidity)if(auto e=model.data->submit_at(*SimulationTime::make(0).data,o))return Result<ExecutionRun>::failure(e.code,e.field);
        for(const auto& slice:plan.children())if(auto e=model.data->submit_at(slice.decision_time,slice.order))return Result<ExecutionRun>::failure(e.code,e.field);
        if(auto e=model.data->advance_to(finish))return Result<ExecutionRun>::failure(e.code,e.field);
        return Result<ExecutionRun>::success(ExecutionRun{std::move(*rebuilt.data),std::move(*model.data)});
    }catch(const std::bad_alloc&){return Result<ExecutionRun>::failure(ErrorCode::resource_exhausted,"execution.run");}
}
Result<CostReport> transaction_costs(CostConfig c,std::span<const CostFill> fills,std::pmr::memory_resource* r)noexcept{
    if(auto e=validate(c.rules))return Result<CostReport>::failure(e.code,e.field);
    if(!r || c.target.value()==0 || fills.size()>4096 || c.arrival.available_at>c.as_of || c.terminal.available_at>c.as_of)return Result<CostReport>::failure(ErrorCode::invalid_range,"cost.config");
    if(c.side!=Side::buy && c.side!=Side::sell)return Result<CostReport>::failure(ErrorCode::invalid_enum,"cost.side");
    const auto benchmark_valid=[&](const PriceBenchmark& b){auto q=b.midpoint.numerator()/b.midpoint.denominator(),rem=b.midpoint.numerator()%b.midpoint.denominator();return !(q<c.rules.minimum_price.value() || (q==c.rules.minimum_price.value() && rem<0) || q>c.rules.maximum_price.value() || (q==c.rules.maximum_price.value() && rem>0));};
    if(!benchmark_valid(c.arrival) || !benchmark_valid(c.terminal) || c.terminal.available_at<c.arrival.available_at)return Result<CostReport>::failure(ErrorCode::invalid_range,"cost.benchmark");
    try{
        const Fraction sign(c.side==Side::buy?1:-1);std::uint64_t executed=0;Fraction notional,delay,spread,fees;
        for(std::size_t i=0;i<fills.size();++i){const auto& row=fills[i];const auto& f=row.fill;
            if(f.run_id!=c.simulation_run_id || f.seed==0 || (i && f.seed!=fills[0].fill.seed) || f.maker==f.taker || f.maker_command==f.taker_command || (row.child!=f.maker && row.child!=f.taker))return Result<CostReport>::failure(ErrorCode::identity_mismatch,"cost.fill_source",i);
            const auto side=row.child==f.taker?f.taker_side:(f.taker_side==Side::buy?Side::sell:Side::buy);
            if((f.taker_side!=Side::buy && f.taker_side!=Side::sell) || side!=c.side || f.quantity.value()==0 || f.quantity>c.rules.maximum_quantity || f.price<c.rules.minimum_price || f.price>c.rules.maximum_price)return Result<CostReport>::failure(ErrorCode::invalid_range,"cost.fill",i);
            if(!benchmark_valid(row.decision_benchmark))return Result<CostReport>::failure(ErrorCode::invalid_range,"cost.decision_benchmark",i);
            if(row.decision_benchmark.available_at>row.decision_time || c.arrival.available_at>row.decision_time || row.decision_time>f.matched_at || f.matched_at>f.reported_at || f.reported_at>c.as_of)return Result<CostReport>::failure(ErrorCode::ordering_error,"cost.future_information",i);
            for(std::size_t j=0;j<i;++j)if(f.maker==fills[j].fill.maker && f.taker==fills[j].fill.taker && f.maker_command==fills[j].fill.maker_command && f.taker_command==fills[j].fill.taker_command)return Result<CostReport>::failure(ErrorCode::duplicate,"cost.fill",i);
            auto sum=types::detail::add(executed,f.quantity.value());if(!sum || *sum.data>c.target.value())return Result<CostReport>::failure(ErrorCode::overflow,"cost.inventory",i);executed=*sum.data;
            const auto q=Fraction::whole(f.quantity.value());notional=notional+Fraction(f.price.value())*q;
            delay=delay+sign*(row.decision_benchmark.midpoint-c.arrival.midpoint)*q;
            spread=spread+sign*(Fraction(f.price.value())-row.decision_benchmark.midpoint)*q;fees=fees+row.fee_ticks_per_lot*q;
        }
        auto unfilled=c.target.value()-executed;auto slippage=delay+spread;auto opportunity=sign*(c.terminal.midpoint-c.arrival.midpoint)*Fraction::whole(unfilled);auto shortfall=slippage+fees+opportunity;
        auto currency=shortfall*Fraction::ratio(c.rules.tick_size.numerator,c.rules.tick_size.denominator)*Fraction::ratio(c.rules.lot_size.numerator,c.rules.lot_size.denominator);
        CostSummary summary{executed,unfilled,executed?analytics::Metric::known(notional/Fraction::whole(executed)):analytics::Metric::missing(analytics::Unavailable::zero_denominator),notional,delay,spread,fees,slippage,opportunity,shortfall,currency};
        return Result<CostReport>::success(CostReport(c,summary,std::pmr::vector<CostFill>(fills.begin(),fills.end(),r)));
    }catch(const exact::ArithmeticFailure& e){return Result<CostReport>::failure(e.code,"cost.exact_capacity");}catch(const std::bad_alloc&){return Result<CostReport>::failure(ErrorCode::resource_exhausted,"cost.output");}
}
} // namespace gig::execution
