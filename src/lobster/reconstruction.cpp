#include "gig/lobster/reconstruction.hpp"
#include <algorithm>
#include <charconv>
#include <limits>
namespace gig::lobster {
namespace {
bool hex(gig::Digest d) noexcept {const auto s=d.view();return s.size()==64&&std::all_of(s.begin(),s.end(),[](char c){return (c>='0'&&c<='9')||(c>='a'&&c<='f');});}
std::optional<std::uint64_t> quantity(const std::array<Level,5>& levels,std::int64_t price) noexcept {for(const auto& l:levels)if(!l.missing&&l.price.value==price)return l.quantity.value;return {};}
template<class T>T number(std::uint64_t value) noexcept{return *T::make(value).data;}
gig::Identity identity(std::string_view v) noexcept{return *gig::Identity::make(v).data;}
}
Effect reference_effect(const Reference& before,const Message& m,const Reference& after) noexcept {
    Effect result{};
    if(before.crossed||after.crossed||before.locked||after.locked||before.zero_volume||after.zero_volume){result.exclusion="anomalous_reference";return result;}
    if(m.kind==Kind::unsupported){result.exclusion="unsupported_event";return result;}
    if(m.kind==Kind::hidden_execution||m.kind==Kind::halt){result.depth_eligible=result.best_eligible=true;result.depth_match=before.asks==after.asks&&before.bids==after.bids;result.best_match=before.asks[0]==after.asks[0]&&before.bids[0]==after.bids[0];return result;}
    const bool bid=m.direction==1;const auto& old=bid?before.bids:before.asks;const auto& current=bid?after.bids:after.asks;
    auto qty=quantity(old,m.price.value);std::size_t occupied=0;for(const auto& l:old)occupied+=l.missing?0U:1U;
    if(!qty){
        if(m.kind!=Kind::add){result.exclusion="outside_previous_depth";return result;}
        if(occupied==5&&(bid?m.price.value<old[4].price.value:m.price.value>old[4].price.value)){
            result.best_eligible=result.depth_eligible=true;result.best_match=before.asks[0]==after.asks[0]&&before.bids[0]==after.bids[0];result.depth_match=before.asks==after.asks&&before.bids==after.bids;return result;
        }
        qty=0;
    }
    result.quantity_eligible=true;std::uint64_t next{};
    if(m.kind==Kind::add){if(m.quantity.value>UINT64_MAX-*qty){result.quantity_eligible=false;result.exclusion="aggregate_overflow";return result;}next=*qty+m.quantity.value;}
    else {if(m.quantity.value>*qty){result.quantity_match=false;result.exclusion="aggregate_underflow_contradiction";return result;}next=*qty-m.quantity.value;}
    result.quantity_match=quantity(current,m.price.value).value_or(0)==next;
    std::array<Level,6> expected{};std::size_t count=0;
    for(const auto& l:old)if(!l.missing&&l.price.value!=m.price.value)expected[count++]=l;
    if(next)expected[count++]={m.price,Shares{next},false};
    std::sort(expected.begin(),expected.begin()+static_cast<std::ptrdiff_t>(count),[&](const auto& a,const auto& b){return bid?a.price.value>b.price.value:a.price.value<b.price.value;});
    result.best_eligible=count>0;const auto& other=bid?before.asks:before.bids;const auto& other_current=bid?after.asks:after.bids;
    result.best_match=result.best_eligible&&expected[0]==current[0]&&other[0]==other_current[0];
    result.depth_eligible=next>0||occupied<5;
    if(result.depth_eligible){std::array<Level,5> wanted{};for(std::size_t i=0;i<5;++i)wanted[i]=i<count?expected[i]:Level{Price4{bid?-9999999999LL:9999999999LL},Shares{0},true};result.depth_match=wanted==current&&other==other_current;}
    return result;
}
KnownSubset::KnownSubset(SourceBinding s,gig::OrderBook b,PairedValidator v,std::pmr::memory_resource* memory,std::size_t lifetime) noexcept:source_(std::move(s)),book_(std::move(b)),validator_(std::move(v)),seen_(memory),lifetime_limit_(lifetime){}
gig::Result<KnownSubset> KnownSubset::create(SourceBinding s,Limits limits,std::size_t lifetime,std::pmr::memory_resource* memory,bool complete) noexcept {
    if(!memory||complete||lifetime==0||lifetime>100000||!hex(s.dataset_sha)||!hex(s.message_sha)||!hex(s.reference_sha)||static_cast<unsigned>(s.origin)>1)return gig::Result<KnownSubset>::failure(gig::ErrorCode::invalid_range,"lobster.subset.config");
    auto validator=PairedValidator::create(limits);if(!validator)return gig::Result<KnownSubset>::failure(validator.error.code,validator.error.field);
    gig::InstrumentRules rules{number<gig::InstrumentId>(1),number<gig::VenueId>(1),*gig::PriceTicks::make(1).data,*gig::PriceTicks::make(INT64_MAX).data,number<gig::QuantityLots>(UINT64_MAX),{1,10000},{1,1}};
    auto book=gig::OrderBook::create(rules,{s.session,0},{lifetime,lifetime,5},memory);if(!book)return gig::Result<KnownSubset>::failure(book.error.code,book.error.field);
    try {KnownSubset out(std::move(s),std::move(*book.data),std::move(*validator.data),memory,lifetime);out.seen_.reserve(lifetime);return gig::Result<KnownSubset>::success(std::move(out));}
    catch(...){return gig::Result<KnownSubset>::failure(gig::ErrorCode::resource_exhausted,"lobster.subset.storage");}
}
gig::Result<Step> KnownSubset::process(std::string_view message,std::string_view reference) noexcept {
    const auto pair=validator_.accept(message,reference);if(!pair)return gig::Result<Step>::failure(pair.error.code,pair.error.field);
    const auto& m=pair.data->message;const auto& ref=pair.data->reference;Step step{m,Disposition::external,{}};
    if(previous_)step.effect=reference_effect(*previous_,m,ref);else step.effect.exclusion="first_row_no_pre_state";
    const auto row=summary_.rows++;
    if(step.effect.quantity_eligible){++summary_.quantity_eligible;summary_.quantity_matches+=step.effect.quantity_match?1U:0U;}
    if(step.effect.best_eligible){++summary_.best_eligible;summary_.best_matches+=step.effect.best_match?1U:0U;}
    if(step.effect.depth_eligible){++summary_.depth_eligible;summary_.depth_matches+=step.effect.depth_match?1U:0U;}
    const bool effect_mismatch=(step.effect.quantity_eligible&&!step.effect.quantity_match)||(step.effect.best_eligible&&!step.effect.best_match)||(step.effect.depth_eligible&&!step.effect.depth_match);
    if(effect_mismatch&&!summary_.first_mismatch)summary_.first_mismatch=row;
    previous_=ref;
    if(m.kind==Kind::unsupported){step.disposition=Disposition::unsupported;++summary_.unsupported;summary_.prefix_blocked=true;}
    else if(m.kind==Kind::hidden_execution||m.kind==Kind::halt){++summary_.external;}
    else if(summary_.prefix_blocked){step.disposition=Disposition::prefix_blocked;++summary_.blocked;}
    else {
        const auto id=number<gig::OrderId>(m.order);const auto existing=book_.find(id);const auto marker=std::find_if(seen_.begin(),seen_.end(),[&](const auto& item){return item.id==id;});const auto side=m.direction==1?gig::Side::buy:gig::Side::sell;
        if(m.kind!=Kind::add&&!existing){
            if(marker!=seen_.end()&&marker->known_submission){step.disposition=Disposition::inconsistent_history;++summary_.inconsistent;summary_.prefix_blocked=true;}
            else if(marker==seen_.end()&&seen_.size()==lifetime_limit_){step.disposition=Disposition::resource_rejected;step.native_error={gig::ErrorCode::capacity,"lobster.lifetime"};++summary_.resource_rejected;summary_.prefix_blocked=true;}
            else {step.disposition=Disposition::unknown_order;++summary_.unknown;if(marker==seen_.end())seen_.push_back({id,false});}
        }
        else if((m.kind==Kind::add&&marker!=seen_.end())||(existing&&(existing->order.side!=side||existing->order.price_ticks.value()!=m.price.value||(m.kind==Kind::erase?existing->order.quantity.value()!=m.quantity.value:m.quantity.value>existing->order.quantity.value())||(m.kind==Kind::cancel&&m.quantity.value==existing->order.quantity.value())))){
            step.disposition=Disposition::inconsistent_history;++summary_.inconsistent;summary_.prefix_blocked=true;
        }else if(m.kind==Kind::add&&seen_.size()==lifetime_limit_){step.disposition=Disposition::resource_rejected;step.native_error={gig::ErrorCode::capacity,"lobster.lifetime"};++summary_.resource_rejected;summary_.prefix_blocked=true;
        }else {
            gig::Metadata meta;meta.instrument=gig::Available<gig::InstrumentId>::known(book_.rules().instrument);meta.venue=gig::Available<gig::VenueId>::known(book_.rules().venue);
            meta.scope=gig::Available<gig::StreamScope>::known({number<gig::StreamId>(1),source_.session,0,gig::SequenceUnit::event});meta.sequence=gig::Available<gig::SequenceNumber>::known(number<gig::SequenceNumber>(summary_.native));meta.capture_ordinal=gig::Available<std::uint64_t>::known(row);
            std::array<char,40> name{};constexpr std::string_view prefix="lobster-row:";std::copy(prefix.begin(),prefix.end(),name.begin());const auto suffix=std::to_chars(name.data()+prefix.size(),name.data()+name.size(),row);meta.source_record=gig::Available<gig::Identity>::known(identity({name.data(),static_cast<std::size_t>(suffix.ptr-name.data())}));
            meta.event_time=gig::Available<gig::Timestamp<gig::EventTimestamp>>::missing(gig::MissingReason::unavailable);meta.receive_time=gig::Available<gig::Timestamp<gig::ReceiveTimestamp>>::missing(gig::MissingReason::unavailable);
            auto& p=meta.provenance;p.origin=gig::Available<gig::Origin>::known(source_.origin);p.source=gig::Available<gig::Source>::known(source_.origin==gig::Origin::synthetic?gig::Source::generator:gig::Source::public_dataset);
            p.dataset=gig::Available<gig::DatasetIdentity>::known({source_.dataset,gig::Available<gig::Identity>::known(identity(source_.dataset_sha.view())),gig::Available<gig::Identity>::known(source_.permission),gig::Available<gig::Digest>::known(source_.dataset_sha)});
            if(source_.origin==gig::Origin::synthetic)p.generator_seed=gig::Available<std::uint64_t>::known(source_.generator_seed);
            (void)p.lineage.append({source_.origin==gig::Origin::synthetic?gig::TransformationKind::generated:gig::TransformationKind::observed,identity("lobster-source"),identity("1")});(void)p.lineage.append({gig::TransformationKind::normalized,identity("lobster-known-subset"),identity("1")});
            (void)p.parents.append({identity("message-artifact"),gig::Available<gig::Digest>::known(source_.message_sha)});(void)p.parents.append({identity("reference-artifact"),gig::Available<gig::Digest>::known(source_.reference_sha)});
            const auto price=*gig::PriceTicks::make(m.price.value).data;const auto qty=number<gig::QuantityLots>(m.quantity.value);
            gig::MarketEvent event{meta,gig::AddOrder{id,side,price,qty}};
            if(m.kind==Kind::cancel)event.payload=gig::CancelOrder{id,qty};
            if(m.kind==Kind::erase)event.payload=gig::CancelOrder{id,gig::CancelAll{}};
            if(m.kind==Kind::visible_execution)event.payload=gig::Trade{gig::BookExecution{id,side,price,qty}};
            step.native_error=book_.apply(event);
            if(step.native_error){step.disposition=Disposition::native_rejected;++summary_.native_rejected;summary_.prefix_blocked=true;}
            else {step.disposition=Disposition::native;++summary_.native;if(m.kind==Kind::add)seen_.push_back({id,true});}
        }
    }
    std::array<std::uint64_t,10> sums{};
    if(!summary_.prefix_blocked)for(const auto& item:seen_){const auto order=book_.find(item.id);if(!order)continue;const auto& levels=order->order.side==gig::Side::buy?ref.bids:ref.asks;bool visible=false;
        for(std::size_t i=0;i<5;++i)if(!levels[i].missing&&levels[i].price.value==order->order.price_ticks.value()){
            const auto slot=i+(order->order.side==gig::Side::buy?5U:0U);sums[slot]+=order->order.quantity.value();visible=true;break;}
        if(!visible){step.coverage_lost=true;summary_.prefix_blocked=true;}
    }
    if(!summary_.prefix_blocked){for(std::size_t i=0;i<10;++i)if(sums[i]){const auto qty=i<5?ref.asks[i].quantity.value:ref.bids[i-5].quantity.value;++step.lower_bound_checks;step.lower_bound_violations+=sums[i]>qty?1U:0U;step.equal_level_quantities+=sums[i]==qty?1U:0U;}}
    summary_.lower_bound_checks+=step.lower_bound_checks;summary_.lower_bound_violations+=step.lower_bound_violations;summary_.equal_level_quantities+=step.equal_level_quantities;
    if(step.lower_bound_violations){summary_.prefix_blocked=true;if(!summary_.first_mismatch)summary_.first_mismatch=row;}
    return gig::Result<Step>::success(step);
}
} // namespace gig::lobster
