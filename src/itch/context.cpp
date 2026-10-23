#include "gig/itch/context.hpp"
#include <algorithm>
#include <atomic>
#include <limits>
#include <type_traits>

namespace gig::itch {
namespace {
static_assert(std::is_nothrow_copy_constructible_v<DirectoryState> && std::is_nothrow_copy_assignable_v<DirectoryState>);
static_assert(std::is_nothrow_copy_constructible_v<OrderState> && std::is_nothrow_copy_assignable_v<OrderState>);
static_assert(std::is_nothrow_copy_constructible_v<MatchState> && std::is_nothrow_copy_assignable_v<MatchState>);
static_assert(std::is_nothrow_copy_constructible_v<NormalizedRecord> && std::is_nothrow_move_constructible_v<NormalizedRecord>);
static_assert(std::is_nothrow_move_constructible_v<ContextResult>);
static_assert(std::is_nothrow_move_constructible_v<PreparedContext> && std::is_nothrow_move_constructible_v<ContextPreparation>);
// Distinguishes object lifetimes even when a caller reuses the same storage.
// This opaque guard never enters semantic output or deterministic serialization.
std::atomic<std::uint64_t> next_instance{1};
std::optional<std::uint64_t> allocate_instance() noexcept {
    auto current=next_instance.load(std::memory_order_relaxed);
    while(current!=UINT64_MAX){
        if(next_instance.compare_exchange_weak(current,current+1,std::memory_order_relaxed))return current;
    }
    return std::nullopt;
}
constexpr std::size_t absent=std::numeric_limits<std::size_t>::max();
ContextResult rejected(ContextStatus status,ContextCode code,Location location,std::string_view field,std::uint64_t expected=0,std::uint64_t actual=0) noexcept {
    return {status,std::nullopt,{code,location,field,expected,actual,{}}};
}
bool provenance_conflicts(const Provenance& a,const Provenance& b) noexcept {
    return (a.origin!=Origin::unspecified&&b.origin!=Origin::unspecified&&a.origin!=b.origin)
        ||(a.source&&b.source&&a.source!=b.source)||(a.sha256&&b.sha256&&a.sha256!=b.sha256)
        ||(a.generator_seed&&b.generator_seed&&a.generator_seed!=b.generator_seed);
}
}
SourceContext::SourceContext(SourceManifest m,ContextPolicy p,std::pmr::memory_resource* resource) noexcept
:manifest_(std::move(m)),policy_(p),directories_(resource),orders_(resource),matches_(resource) {}
SourceContext::SourceContext(SourceContext&& other) noexcept
:manifest_(std::move(other.manifest_)),policy_(other.policy_),directories_(std::move(other.directories_)),
 orders_(std::move(other.orders_)),matches_(std::move(other.matches_)),summary_(other.summary_),
 lifecycle_stage_(other.lifecycle_stage_),next_location_(other.next_location_),
 cursor_exhausted_(other.cursor_exhausted_),moved_from_(other.moved_from_),instance_(other.instance_) {other.moved_from_=true;}
std::optional<std::size_t> SourceContext::required_bytes(const ContextPolicy& p) noexcept {
    constexpr auto max=std::numeric_limits<std::size_t>::max();std::size_t total=0;
    const auto add=[&](std::size_t count,std::size_t size){if(count>(max-total)/size)return false;total+=count*size;return true;};
    if(!add(p.max_directories,sizeof(DirectoryState))||!add(p.max_lifetime_orders,sizeof(OrderState))||!add(p.max_matches,sizeof(MatchState)))return std::nullopt;
    return total;
}
Result<SourceContext> SourceContext::create(SourceManifest m,ContextPolicy p,std::pmr::memory_resource* resource) noexcept {
    const auto bytes=required_bytes(p);
    if(!resource||!bytes||*bytes>p.memory_budget_bytes||p.price_quantum==0||p.lot_size==0
        ||static_cast<unsigned>(p.decode_profile)>static_cast<unsigned>(DecodeProfile::administrative_observations_v3)
        ||p.first_location.frame_offset.value()>UINT64_MAX-2
        ||p.first_location.payload_offset.value()!=p.first_location.frame_offset.value()+2
        ||static_cast<unsigned>(m.initialization)>static_cast<unsigned>(Initialization::synthetic_history_declared)
        ||static_cast<unsigned>(m.provenance.origin)>static_cast<unsigned>(Origin::observed)
        ||(m.provenance.source&&*m.provenance.source!=m.source))
        return Result<SourceContext>::failure({Code::invalid_config,p.first_location.frame_offset,"context",p.memory_budget_bytes,bytes.value_or(UINT64_MAX)});
    try {
        SourceContext out(std::move(m),p,resource);
        const auto instance=allocate_instance();
        if(!instance)return Result<SourceContext>::failure({Code::resource_exhausted,p.first_location.frame_offset,"context.instance",0,UINT64_MAX});
        out.instance_=*instance;
        out.directories_.reserve(p.max_directories);out.orders_.reserve(p.max_lifetime_orders);out.matches_.reserve(p.max_matches);
        auto actual=p;actual.max_directories=out.directories_.capacity();actual.max_lifetime_orders=out.orders_.capacity();actual.max_matches=out.matches_.capacity();
        const auto reserved=required_bytes(actual);out.summary_.reserved_bytes=reserved.value_or(SIZE_MAX);
        if(!reserved||out.summary_.reserved_bytes>p.memory_budget_bytes)return Result<SourceContext>::failure({Code::resource_exhausted,p.first_location.frame_offset,"context.storage",p.memory_budget_bytes,out.summary_.reserved_bytes});
        return Result<SourceContext>::success(std::move(out));
    }catch(...){return Result<SourceContext>::failure({Code::resource_exhausted,p.first_location.frame_offset,"context.storage",bytes.value_or(0),0});}
}
ContextResult SourceContext::disposition(const Error& error,Location location)const noexcept {
    auto result=rejected(error.code==Code::unsupported_type||error.code==Code::unknown_type?ContextStatus::unsupported:ContextStatus::source_invalid,
        ContextCode::unsupported_source,location,error.field,error.expected,error.actual);
    result.error.source_error=error;return result;
}
ContextPreparation SourceContext::prepare(std::span<const std::byte> payload,Location location,Provenance provenance) const noexcept {
    if(moved_from_)return rejected(ContextStatus::context_invalid,ContextCode::invalid_config,location,"moved_from");
    auto decoded=decode(payload,location,provenance,policy_.decode_profile);if(!decoded)return disposition(decoded.error,location);
    if(summary_.finished)return rejected(ContextStatus::context_invalid,ContextCode::already_finished,location,"finished");
    const auto fail=[&](ContextCode c,std::string_view field,std::uint64_t expected=0,std::uint64_t actual=0){return rejected(ContextStatus::context_invalid,c,location,field,expected,actual);};
    const auto& raw=*decoded.data;
    if(provenance_conflicts(manifest_.provenance,raw.provenance)||(raw.provenance.source&&*raw.provenance.source!=manifest_.source))return fail(ContextCode::provenance_conflict,"provenance");
    if(cursor_exhausted_)return fail(ContextCode::discontinuity,"cursor_exhausted");
    Location expected=summary_.last_location?next_location_:policy_.first_location;
    if(location!=expected)return fail(ContextCode::discontinuity,"location",expected.ordinal.value(),location.ordinal.value());
    const auto timestamp=raw.header.timestamp.value();
    if((policy_.require_intraday_timestamps&&timestamp>=86400000000000ULL)
        ||(policy_.require_monotonic_timestamps&&summary_.last_timestamp&&timestamp<summary_.last_timestamp->value()))return fail(ContextCode::timestamp_policy,"timestamp");

    if(summary_.accepted_records==UINT64_MAX)return fail(ContextCode::capacity,"accepted_records");
    auto next_stage=lifecycle_stage_;
    if(policy_.require_lifecycle_order){
        if(lifecycle_stage_==6)return fail(ContextCode::lifecycle,"after_end_of_messages");
        if(raw.type!='S'&&lifecycle_stage_==0)return fail(ContextCode::lifecycle,"start_of_messages");
    }
    if(raw.type=='S'){
        if(raw.header.stock_locate.value()!=0)return fail(ContextCode::unknown_locate,"global_stock_locate",0,raw.header.stock_locate.value());
        if(policy_.require_lifecycle_order){
            constexpr std::string_view codes="OSQMEC";
            const auto code=std::get<SystemEvent>(raw.message).event_code;
            if(code!=codes[lifecycle_stage_])return fail(ContextCode::lifecycle,"system_event",static_cast<unsigned char>(codes[lifecycle_stage_]),static_cast<unsigned char>(code));
            next_stage=static_cast<std::uint8_t>(lifecycle_stage_+1);
        }
    }
    const auto locate=raw.header.stock_locate;
    const auto directory_it=std::find_if(directories_.begin(),directories_.end(),[&](const auto& d){return d.locate==locate;});
    const auto order_index=[&](OrderReference ref){const auto i=std::find_if(orders_.begin(),orders_.end(),[&](const auto& o){return o.reference==ref;});return i==orders_.end()?absent:static_cast<std::size_t>(i-orders_.begin());};
    const auto match_index=[&](MatchNumber number){const auto i=std::find_if(matches_.begin(),matches_.end(),[&](const auto& m){return m.number==number;});return i==matches_.end()?absent:static_cast<std::size_t>(i-matches_.begin());};
    NormalizedRecord normalized{raw,manifest_};normalized.policy=policy_;
    normalized.normalization_version=static_cast<std::uint32_t>(policy_.decode_profile)+1U;
    std::optional<DirectoryState> add_directory;std::optional<OrderState> add_order,update_order;
    std::optional<MatchState> add_match,update_match;
    std::size_t order_slot=absent,match_slot=absent;
    ContextCode operation_error=ContextCode::none;std::string_view operation_field;
    auto operation_fail=[&](ContextCode code,std::string_view field){if(operation_error==ContextCode::none){operation_error=code;operation_field=field;}};
    const auto require_directory=[&](const Text<8>* stock=nullptr){
        if(directory_it==directories_.end()){operation_fail(ContextCode::unknown_locate,"stock_locate");return;}
        if(stock&&directory_it->directory.stock!=*stock)operation_fail(ContextCode::stock_conflict,"stock");
    };
    const auto existing_order=[&](OrderReference reference)->std::optional<OrderState>{
        order_slot=order_index(reference);
        if(order_slot==absent){operation_fail(ContextCode::missing_order,"order_reference");return std::nullopt;}
        const auto order=orders_[order_slot];
        if(order.locate!=locate){operation_fail(ContextCode::stock_conflict,"stock_locate");return std::nullopt;}
        if(!order.active){operation_fail(ContextCode::inactive_order,"order_reference");return std::nullopt;}
        return order;
    };
    const auto generation_match=[&](MatchNumber number,MatchKind kind){
        if(match_index(number)!=absent)operation_fail(ContextCode::duplicate_match,"match_number");
        add_match=MatchState{number,locate,kind,false};
    };
    auto units=[&](Price4 price,std::uint64_t quantity){
        normalized.integration=IntegrationClass::exact_candidate;
        if(price.value()>0&&price.value()%policy_.price_quantum==0)normalized.price_ticks=price.value()/policy_.price_quantum;
        if(quantity>0&&quantity%policy_.lot_size==0)normalized.quantity_lots=quantity/policy_.lot_size;
    };
    switch(raw.type){
    case 'S':normalized.kind=SemanticKind::system;break;
    case 'L':normalized.kind=SemanticKind::participant_position;
        require_directory(&std::get<MarketParticipantPosition>(raw.message).stock);break;
    case 'h':normalized.kind=SemanticKind::operational_halt;
        require_directory(&std::get<OperationalHalt>(raw.message).stock);break;
    case 'N':normalized.kind=SemanticKind::retail_interest;
        require_directory(&std::get<RetailPriceImprovement>(raw.message).stock);break;
    case 'V':case 'W':
        normalized.kind=raw.type=='V'?SemanticKind::mwcb_levels:SemanticKind::mwcb_status;
        if(locate.value()!=0)operation_fail(ContextCode::unknown_locate,"global_stock_locate");
        break;
    case 'H':
        normalized.kind=SemanticKind::trading_action;
        require_directory(&std::get<StockTradingAction>(raw.message).stock);break;
    case 'Y':
        normalized.kind=SemanticKind::reg_sho_restriction;
        require_directory(&std::get<RegShoRestriction>(raw.message).stock);break;
    case 'R':{
        normalized.kind=SemanticKind::directory;const auto& d=std::get<StockDirectory>(raw.message);
        // Local identity admission policy only: a padding-only symbol establishes
        // no security identity. Wire decoding still preserves this source value.
        if(std::all_of(d.stock.bytes.begin(),d.stock.bytes.end(),[](char c){return c==' ';}))operation_fail(ContextCode::stock_conflict,"empty_stock");
        if(locate.value()==0)operation_fail(ContextCode::unknown_locate,"stock_locate");
        else if(directory_it!=directories_.end()){if(directory_it->directory!=d)operation_fail(ContextCode::directory_conflict,"directory");}
        else {
            if(std::any_of(directories_.begin(),directories_.end(),[&](const auto& prior){return prior.directory.stock==d.stock;}))operation_fail(ContextCode::directory_conflict,"stock_mapping");
            add_directory=DirectoryState{locate,d};
        }
        break;
    }
    case 'A':case 'F':{
        normalized.kind=SemanticKind::add;
        const auto& add=raw.type=='A'?std::get<AddOrder>(raw.message):std::get<AddAttributedOrder>(raw.message).order;
        require_directory(&add.stock);
        if(add.order_reference.value()==0)operation_fail(ContextCode::invalid_reference,"order_reference");
        else if(order_index(add.order_reference)!=absent)operation_fail(ContextCode::duplicate_reference,"order_reference");
        if(add.shares.value()==0)operation_fail(ContextCode::invalid_quantity,"shares");
        OrderState order{add.order_reference,locate,add.stock,add.side,add.shares,add.price,std::nullopt,location.ordinal,true};
        if(raw.type=='F')order.attribution=std::get<AddAttributedOrder>(raw.message).attribution;
        add_order=order;normalized.after=order;units(add.price,add.shares.value());break;
    }
    case 'E':case 'C':{
        normalized.kind=SemanticKind::execution;require_directory();
        const auto& e=raw.type=='E'?std::get<OrderExecuted>(raw.message):std::get<OrderExecutedWithPrice>(raw.message).execution;
        const auto before=existing_order(e.order_reference);
        if(e.executed_shares.value()==0)operation_fail(ContextCode::invalid_quantity,"executed_shares");
        generation_match(e.match_number,MatchKind::displayed_execution);
        if(before){
            normalized.before=before;auto after=*before;
            if(e.executed_shares.value()>before->remaining.value())operation_fail(ContextCode::quantity_underflow,"executed_shares");
            else{after.remaining=Shares{before->remaining.value()-e.executed_shares.value()};after.active=after.remaining.value()!=0;update_order=after;normalized.after=after;}
            units(before->resting_price,e.executed_shares.value());
            if(raw.type=='C'){
                const auto& c=std::get<OrderExecutedWithPrice>(raw.message);normalized.printable=c.printable;normalized.observed_execution_price=c.execution_price;
                if(c.execution_price!=before->resting_price)normalized.integration=IntegrationClass::book_only_projection;
            }
        }break;
    }
    case 'X':{
        normalized.kind=SemanticKind::cancel;require_directory();const auto& x=std::get<OrderCancel>(raw.message);const auto before=existing_order(x.order_reference);
        if(x.cancelled_shares.value()==0)operation_fail(ContextCode::invalid_quantity,"cancelled_shares");
        if(before){normalized.before=before;auto after=*before;
            if(x.cancelled_shares.value()>before->remaining.value())operation_fail(ContextCode::quantity_underflow,"cancelled_shares");
            else if(x.cancelled_shares==before->remaining&&!policy_.allow_equal_cancel)operation_fail(ContextCode::equal_cancel,"cancelled_shares");
            else{after.remaining=Shares{before->remaining.value()-x.cancelled_shares.value()};after.active=after.remaining.value()!=0;normalized.after=after;update_order=after;}
            units(before->resting_price,x.cancelled_shares.value());
        }break;
    }
    case 'D':{
        normalized.kind=SemanticKind::erase;require_directory();const auto before=existing_order(std::get<OrderDelete>(raw.message).order_reference);
        if(before){normalized.before=before;auto after=*before;after.remaining=Shares{0};after.active=false;normalized.after=after;update_order=after;units(before->resting_price,before->remaining.value());}break;
    }
    case 'U':{
        normalized.kind=SemanticKind::replace;require_directory();const auto& u=std::get<OrderReplace>(raw.message);const auto before=existing_order(u.original_reference);
        if(u.new_reference.value()==0)operation_fail(ContextCode::invalid_reference,"new_reference");
        else if(order_index(u.new_reference)!=absent)operation_fail(ContextCode::duplicate_reference,"new_reference");
        if(u.shares.value()==0)operation_fail(ContextCode::invalid_quantity,"shares");
        if(before){normalized.before=before;auto old=*before;old.active=false;old.remaining=Shares{0};update_order=old;
            auto next=*before;next.reference=u.new_reference;next.remaining=u.shares;next.resting_price=u.price;next.arrival=location.ordinal;next.active=true;
            normalized.after=next;add_order=next;units(u.price,u.shares.value());}break;
    }
    case 'P':{
        normalized.kind=SemanticKind::trade_print;const auto& p=std::get<Trade>(raw.message);require_directory(&p.stock);
        generation_match(p.match_number,MatchKind::non_displayed_trade);normalized.observed_execution_price=p.price;units(p.price,p.shares.value());break;
    }
    case 'Q':{
        normalized.kind=SemanticKind::cross_print;const auto& q=std::get<CrossTrade>(raw.message);require_directory(&q.stock);
        generation_match(q.match_number,MatchKind::cross);normalized.observed_execution_price=q.cross_price;units(q.cross_price,q.shares.value());
        normalized.integration=IntegrationClass::unsupported;break;
    }
    case 'B':{
        normalized.kind=SemanticKind::broken_trade;require_directory();match_slot=match_index(std::get<BrokenTrade>(raw.message).match_number);
        if(match_slot==absent)operation_fail(ContextCode::missing_match,"match_number");
        else if(matches_[match_slot].locate!=locate)operation_fail(ContextCode::stock_conflict,"stock_locate");
        else if(matches_[match_slot].kind==MatchKind::cross)return rejected(ContextStatus::unsupported,ContextCode::unsupported_source,location,"cross_break");
        else if(matches_[match_slot].broken)operation_fail(ContextCode::broken_match,"match_number");
        else{auto match=matches_[match_slot];match.broken=true;update_match=match;normalized.integration=IntegrationClass::unsupported;}
        break;
    }
    default:return rejected(ContextStatus::unsupported,ContextCode::unsupported_source,location,"type");
    }
    if(operation_error!=ContextCode::none)return fail(operation_error,operation_field);
    if((add_directory&&directories_.size()==policy_.max_directories)||(add_order&&orders_.size()==policy_.max_lifetime_orders)||(add_match&&matches_.size()==policy_.max_matches))return rejected(ContextStatus::resource_limit,ContextCode::capacity,location,"storage");
    ContextStatus status=ContextStatus::accepted;ContextError error{};
    if(normalized.integration==IntegrationClass::exact_candidate&&(!normalized.price_ticks||!normalized.quantity_lots)){
        status=ContextStatus::integration_ineligible;error={ContextCode::unit_conversion,location,"native_units",0,0,{}};
    }else if(normalized.integration==IntegrationClass::book_only_projection||normalized.integration==IntegrationClass::unsupported){
        status=ContextStatus::integration_ineligible;error={ContextCode::unsupported_source,location,"native_contract",0,0,{}};
    }
    PreparedContext token{this,instance_,summary_.accepted_records,{status,std::move(normalized),error}};
    token.add_directory_=add_directory;token.add_order_=add_order;token.update_order_=update_order;
    token.add_match_=add_match;token.update_match_=update_match;
    token.order_slot_=order_slot;token.match_slot_=match_slot;token.next_stage_=next_stage;
    const auto end=location.payload_offset.value()+payload.size();
    token.cursor_exhausted_=end>UINT64_MAX-2||location.ordinal.value()==UINT64_MAX;
    if(!token.cursor_exhausted_)token.next_location_={ByteOffset{end},ByteOffset{end+2},RecordOrdinal{location.ordinal.value()+1}};
    return {status,error,std::move(token)};
}
PreparedContext::PreparedContext(const SourceContext* owner,std::uint64_t instance,std::uint64_t generation,ContextResult result) noexcept
:owner_(owner),instance_(instance),generation_(generation),result_(std::move(result)),valid_(true) {}
PreparedContext::PreparedContext(PreparedContext&& other) noexcept
:owner_(other.owner_),instance_(other.instance_),generation_(other.generation_),result_(std::move(other.result_)),
 add_directory_(other.add_directory_),add_order_(other.add_order_),update_order_(other.update_order_),
 add_match_(other.add_match_),update_match_(other.update_match_),order_slot_(other.order_slot_),match_slot_(other.match_slot_),
 next_stage_(other.next_stage_),next_location_(other.next_location_),cursor_exhausted_(other.cursor_exhausted_),valid_(other.valid_) {other.valid_=false;}
ContextError SourceContext::validate_prepared(const PreparedContext& token)const noexcept {
    const auto location=token.result_.record?token.result_.record->source.location:Location{};
    if(!token.valid_||token.owner_!=this||token.instance_!=instance_||moved_from_)
        return {ContextCode::invalid_prepared,location,"prepared.owner",0,0,{}};
    if(summary_.finished||token.generation_!=summary_.accepted_records)
        return {ContextCode::stale_prepared,location,"prepared.generation",summary_.accepted_records,token.generation_,{}};
    return {};
}
ContextResult SourceContext::commit(PreparedContext&& token) noexcept {
    const auto error=validate_prepared(token);
    if(error.code!=ContextCode::none)return {ContextStatus::context_invalid,std::nullopt,error};
    return commit_validated(std::move(token));
}
ContextResult SourceContext::commit_validated(PreparedContext&& token) noexcept {
    // The owning adapter validates before its sole fallible native apply. Its private
    // context cannot move or change while that operation runs. No allocation or
    // input-dependent validation remains after successful native application.
    if(token.add_directory_)directories_.push_back(*token.add_directory_);
    if(token.update_order_)orders_[token.order_slot_]=*token.update_order_;
    if(token.add_order_)orders_.push_back(*token.add_order_);
    if(token.add_match_)matches_.push_back(*token.add_match_);
    if(token.update_match_)matches_[token.match_slot_]=*token.update_match_;
    lifecycle_stage_=token.next_stage_;
    ++summary_.accepted_records;summary_.directories=directories_.size();summary_.lifetime_orders=orders_.size();summary_.matches=matches_.size();
    summary_.active_orders=static_cast<std::size_t>(std::count_if(orders_.begin(),orders_.end(),[](const auto& o){return o.active;}));
    summary_.last_location=token.record().source.location;summary_.last_timestamp=token.record().source.header.timestamp;
    cursor_exhausted_=token.cursor_exhausted_;next_location_=token.next_location_;
    token.valid_=false;
    return std::move(token.result_);
}
ContextResult SourceContext::apply(std::span<const std::byte> payload,Location location,Provenance provenance) noexcept {
    auto prepared=prepare(payload,location,std::move(provenance));
    if(!prepared)return {prepared.status,std::nullopt,prepared.error};
    return commit_validated(std::move(*prepared.prepared));
}
ContextSummary SourceContext::finish(ContextEnd kind) noexcept {
    if(moved_from_){auto result=summary_;result.finish_error=ContextCode::invalid_config;return result;}
    if(summary_.finished)return summary_;
    if(kind!=ContextEnd::bounded_prefix&&kind!=ContextEnd::declared_source_complete&&kind!=ContextEnd::unexpected_eof){auto result=summary_;result.finish_error=ContextCode::invalid_config;return result;}
    summary_.finished=true;summary_.source_complete=kind==ContextEnd::declared_source_complete;
    summary_.bounded_prefix=kind==ContextEnd::bounded_prefix;
    summary_.session_incomplete=!(summary_.source_complete&&policy_.require_lifecycle_order&&lifecycle_stage_==6);
    return summary_;
}
} // namespace gig::itch
