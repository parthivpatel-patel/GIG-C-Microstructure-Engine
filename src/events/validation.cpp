#include "gig/events/contracts.hpp"
#include <type_traits>

namespace gig {
namespace {
template<class E> bool enum_to(E value,E last) noexcept {
    return static_cast<std::underlying_type_t<E>>(value)<=static_cast<std::underlying_type_t<E>>(last);
}
Error side(Side value) noexcept { return enum_to(value,Side::sell)?Error{}:Error{ErrorCode::invalid_enum,"side"}; }
template<class T> Error available(const Available<T>& value,std::string_view field,bool required=false) noexcept {
    if (!enum_to(value.reason,MissingReason::not_applicable)) return {ErrorCode::invalid_enum,field};
    if (value.data.has_value()!=(value.reason==MissingReason::none)) return {ErrorCode::inconsistent_metadata,field};
    if (required && !value.data) return {ErrorCode::missing_metadata,field};
    return {};
}
template<class T,std::size_t N> Error list(const BoundedList<T,N>& values,std::string_view field) noexcept {
    if (values.count>N) return {ErrorCode::capacity,field,values.count};
    for (std::size_t i=0;i<N;++i)
        if (values.items[i].has_value()!=(i<values.count)) return {ErrorCode::inconsistent_metadata,field,i};
    return {};
}
Error digest(const Available<Digest>& value,std::string_view field) noexcept {
    if (const auto e=available(value,field)) return e;
    if (value.data) {
        const auto text=value.data->view();
        if (text.size()!=64) return {ErrorCode::malformed,field};
        for (const char c:text) if (!((c>='0' && c<='9') || (c>='a' && c<='f'))) return {ErrorCode::malformed,field};
    }
    return {};
}
Error scope(const StreamScope& value) noexcept {
    return enum_to(value.unit,SequenceUnit::event)?Error{}:Error{ErrorCode::invalid_enum,"scope.unit"};
}
template<class T> Error timestamp(const Available<Timestamp<T>>& value,std::string_view field,bool complete) noexcept {
    if (const auto e=available(value,field)) return e;
    if (!value.data) return {};
    const auto& stamp=*value.data;
    if (const auto e=available(stamp.clock,"timestamp.clock",complete)) return e;
    if (const auto e=available(stamp.precision,"timestamp.precision",complete)) return e;
    if (stamp.clock.data) {
        const auto domain=stamp.clock.data->domain;
        if (!enum_to(domain,ClockDomain::simulation)) return {ErrorCode::invalid_enum,field};
        if (domain!=ClockDomain::utc && !(std::same_as<T,EventTimestamp> && domain==ClockDomain::venue_utc_unsynchronized))
            return {ErrorCode::unsupported,field};
    }
    if (!stamp.precision.data) return {};
    const auto precision=*stamp.precision.data;
    if (!enum_to(precision,types::TimestampUnit::seconds)) return {ErrorCode::invalid_enum,field};
    std::int64_t resolution=1;
    switch (precision) {
    case types::TimestampUnit::nanoseconds: break;
    case types::TimestampUnit::microseconds: resolution=1000; break;
    case types::TimestampUnit::milliseconds: resolution=1000000; break;
    case types::TimestampUnit::seconds: resolution=1000000000; break;
    }
    if (stamp.nanoseconds.value()%resolution!=0) return {ErrorCode::inconsistent_metadata,field};
    return {};
}
Error price(PriceTicks value,const InstrumentRules& rules) noexcept {
    return value<rules.minimum_price || value>rules.maximum_price ? Error{ErrorCode::invalid_range,"price_ticks"}:Error{};
}
Error quantity(QuantityLots value,const InstrumentRules& rules) noexcept {
    return value.value()==0 || value>rules.maximum_quantity ? Error{ErrorCode::invalid_range,"quantity"}:Error{};
}
Error priced_quantity(PriceTicks p,QuantityLots q,const InstrumentRules& rules) noexcept {
    if (const auto e=price(p,rules)) return e;
    return quantity(q,rules);
}
Error provenance(const Provenance& p,bool complete) noexcept {
    if (const auto e=available(p.dataset,"provenance.dataset",complete)) return e;
    if (const auto e=available(p.origin,"provenance.origin",complete)) return e;
    if (const auto e=available(p.source,"provenance.source",complete)) return e;
    if (const auto e=available(p.generator_seed,"provenance.generator_seed")) return e;
    if (const auto e=list(p.lineage,"provenance.lineage")) return e;
    if (const auto e=list(p.parents,"provenance.parents")) return e;
    if (p.dataset.data) {
        if (const auto e=available(p.dataset.data->version,"provenance.dataset.version",complete)) return e;
        if (const auto e=available(p.dataset.data->license_reference,"provenance.dataset.license_reference",complete)) return e;
        if (const auto e=digest(p.dataset.data->sha256,"provenance.dataset.sha256")) return e;
    }
    if (p.origin.data && !enum_to(*p.origin.data,Origin::observed)) return {ErrorCode::invalid_enum,"provenance.origin"};
    if (p.source.data && !enum_to(*p.source.data,Source::public_dataset)) return {ErrorCode::invalid_enum,"provenance.source"};
    if (complete && p.lineage.count==0) return {ErrorCode::missing_metadata,"provenance.lineage"};
    bool generated=false,observed=false,derived=false;
    for (std::size_t i=0;i<p.lineage.count;++i) {
        const auto kind=p.lineage.items[i]->kind;
        if (!enum_to(kind,TransformationKind::simulated)) return {ErrorCode::invalid_enum,"provenance.lineage",i};
        generated=generated || kind==TransformationKind::generated;
        observed=observed || kind==TransformationKind::observed;
        derived=derived || kind==TransformationKind::normalized || kind==TransformationKind::reconstructed || kind==TransformationKind::simulated;
    }
    if (p.origin.data && *p.origin.data==Origin::synthetic) {
        if (observed || (p.source.data && *p.source.data!=Source::generator)) return {ErrorCode::inconsistent_metadata,"provenance.origin"};
        if (complete && (!generated || !p.generator_seed.data)) return {ErrorCode::missing_metadata,"provenance.generator_seed"};
    }
    if (p.origin.data && *p.origin.data==Origin::observed) {
        if (generated || p.generator_seed.data || (p.source.data && *p.source.data==Source::generator)) return {ErrorCode::inconsistent_metadata,"provenance.origin"};
        if (complete && !observed) return {ErrorCode::missing_metadata,"provenance.lineage"};
    }
    if (complete && derived && p.parents.count==0) return {ErrorCode::missing_metadata,"provenance.parents"};
    for (std::size_t i=0;i<p.parents.count;++i) {
        if (const auto e=digest(p.parents.items[i]->sha256,"provenance.parents.sha256")) return {e.code,e.field,i};
        for (std::size_t j=0;j<i;++j)
            if (p.parents.items[j]->identity==p.parents.items[i]->identity) return {ErrorCode::duplicate,"provenance.parents",i};
    }
    return {};
}
Error snapshot(const Snapshot& snap,const InstrumentRules& rules,const Metadata& metadata) noexcept {
    if (!enum_to(snap.kind,SnapshotKind::aggregated) || !enum_to(snap.coverage,SnapshotCoverage::bounded_depth))
        return {ErrorCode::invalid_enum,"snapshot.kind_or_coverage"};
    if (const auto e=list(snap.orders,"snapshot.orders")) return e;
    if (const auto e=list(snap.levels,"snapshot.levels")) return e;
    if (const auto e=list(snap.boundaries,"snapshot.boundaries")) return e;
    if ((snap.coverage==SnapshotCoverage::complete && snap.depth!=0) ||
        (snap.coverage==SnapshotCoverage::bounded_depth && snap.depth==0)) return {ErrorCode::inconsistent_metadata,"snapshot.depth"};
    if (snap.boundaries.count==0) return {ErrorCode::missing_metadata,"snapshot.boundaries"};
    if ((snap.kind==SnapshotKind::order_level && snap.levels.count!=0) ||
        (snap.kind==SnapshotKind::aggregated && snap.orders.count!=0)) return {ErrorCode::inconsistent_metadata,"snapshot.representation"};
    for (std::size_t i=0;i<snap.boundaries.count;++i) {
        const auto& b=*snap.boundaries.items[i];
        if (const auto e=scope(b.scope)) return e;
        if (b.subevent_count==0 || b.last_subevent>=b.subevent_count ||
            (b.scope.unit==SequenceUnit::event && (b.last_subevent!=0 || b.subevent_count!=1)))
            return {ErrorCode::invalid_range,"snapshot.boundary.subevent",i};
        if (metadata.scope.data && b.scope.stream==metadata.scope.data->stream) {
            if (b.scope!=*metadata.scope.data) return {ErrorCode::inconsistent_metadata,"snapshot.boundary.scope",i};
            if (metadata.sequence.data && (b.sequence>*metadata.sequence.data ||
                (b.sequence==*metadata.sequence.data && b.last_subevent>metadata.subevent_index))) return {ErrorCode::invalid_range,"snapshot.boundary.sequence",i};
        }
        for (std::size_t j=0;j<i;++j)
            if (b.scope.stream==snap.boundaries.items[j]->scope.stream) return {ErrorCode::duplicate,"snapshot.boundaries",i};
    }
    std::optional<PriceTicks> bid,ask;
    std::size_t bid_levels=0,ask_levels=0;
    const auto best=[&bid,&ask](Side s,PriceTicks p) {
        if (s==Side::buy && (!bid || p>*bid)) bid=p;
        if (s==Side::sell && (!ask || p<*ask)) ask=p;
    };
    for (std::size_t i=0;i<snap.orders.count;++i) {
        const auto& a=*snap.orders.items[i];
        if (const auto e=validate(a.order,rules)) return {e.code,e.field,i};
        best(a.order.side,a.order.price_ticks);
        bool first_level=true;
        std::uint64_t level_quantity=0;
        for (std::size_t j=0;j<snap.orders.count;++j) {
            const auto& b=*snap.orders.items[j];
            if (a.order.side==b.order.side && a.order.price_ticks==b.order.price_ticks) {
                if (j<i) first_level=false;
                const auto total=types::detail::add(level_quantity,b.order.quantity.value());
                if (!total) return {ErrorCode::overflow,"snapshot.level_quantity",i};
                level_quantity=*total.data;
            }
        }
        if (first_level) { if (a.order.side==Side::buy) ++bid_levels; else ++ask_levels; }
        for (std::size_t j=0;j<i;++j) {
            const auto& b=*snap.orders.items[j];
            if (a.order.order_id==b.order.order_id) return {ErrorCode::duplicate,"snapshot.order_id",i};
            if (a.order.side==b.order.side && a.order.price_ticks==b.order.price_ticks && a.priority_index==b.priority_index)
                return {ErrorCode::duplicate,"snapshot.priority",i};
        }
    }
    for (std::size_t i=0;i<snap.levels.count;++i) {
        const auto& a=*snap.levels.items[i];
        if (const auto e=side(a.side)) return {e.code,e.field,i};
        if (const auto e=priced_quantity(a.price_ticks,a.quantity,rules)) return {e.code,e.field,i};
        best(a.side,a.price_ticks);
        if (a.side==Side::buy) ++bid_levels; else ++ask_levels;
        for (std::size_t j=0;j<i;++j) {
            const auto& b=*snap.levels.items[j];
            if (a.side==b.side && a.price_ticks==b.price_ticks) return {ErrorCode::duplicate,"snapshot.level",i};
        }
    }
    if (snap.coverage==SnapshotCoverage::bounded_depth && (bid_levels>snap.depth || ask_levels>snap.depth))
        return {ErrorCode::invalid_range,"snapshot.depth"};
    if (bid && ask && *bid>*ask) return {ErrorCode::crossed_quote,"snapshot"};
    return {};
}
} // namespace

Error validate(const InstrumentRules& rules) noexcept {
    if (!rules.tick_size.valid() || !rules.lot_size.valid() || rules.minimum_price>rules.maximum_price || rules.maximum_quantity.value()==0)
        return {ErrorCode::invalid_range,"instrument_rules"};
    return {};
}
Error validate(const AddOrder& order,const InstrumentRules& rules) noexcept {
    if (const auto e=validate(rules)) return e;
    if (const auto e=side(order.side)) return e;
    return priced_quantity(order.price_ticks,order.quantity,rules);
}
Error validate(const Metadata& m,ValidationMode mode) noexcept {
    if (!enum_to(mode,ValidationMode::inspect_incomplete)) return {ErrorCode::invalid_enum,"validation_mode"};
    const bool complete=mode==ValidationMode::complete;
    if (m.schema_version!=1) return {ErrorCode::unsupported,"schema_version"};
    if (const auto e=available(m.instrument,"instrument",complete)) return e;
    if (const auto e=available(m.venue,"venue",complete)) return e;
    if (const auto e=available(m.scope,"scope",complete)) return e;
    if (const auto e=available(m.sequence,"sequence",complete)) return e;
    if (const auto e=available(m.source_record,"source_record",complete)) return e;
    if (const auto e=available(m.capture_ordinal,"capture_ordinal")) return e;
    if (const auto e=timestamp(m.event_time,"event_time",complete)) return e;
    if (const auto e=timestamp(m.receive_time,"receive_time",complete)) return e;
    if (m.subevent_count==0 || m.subevent_index>=m.subevent_count) return {ErrorCode::invalid_range,"subevent"};
    if (m.scope.data) {
        if (const auto e=scope(*m.scope.data)) return e;
        if (m.scope.data->unit==SequenceUnit::event && (m.subevent_index!=0 || m.subevent_count!=1)) return {ErrorCode::inconsistent_metadata,"subevent"};
    }
    return provenance(m.provenance,complete);
}
Error validate(const MarketEvent& event,const InstrumentRules& rules,ValidationMode mode) noexcept {
    if (const auto e=validate(rules)) return e;
    if (const auto e=validate(event.metadata,mode)) return e;
    const auto& m=event.metadata;
    if ((m.instrument.data && *m.instrument.data!=rules.instrument) || (m.venue.data && *m.venue.data!=rules.venue))
        return {ErrorCode::identity_mismatch,"instrument_or_venue"};
    if (event.payload.valueless_by_exception()) return {ErrorCode::unsupported,"payload"};
    return std::visit([&](const auto& payload)->Error {
        using T=std::decay_t<decltype(payload)>;
        if constexpr (std::same_as<T,AddOrder>) return validate(payload,rules);
        else if constexpr (std::same_as<T,CancelOrder>) {
            if (payload.amount.valueless_by_exception()) return {ErrorCode::unsupported,"cancel.amount"};
            if (const auto* q=std::get_if<QuantityLots>(&payload.amount)) return quantity(*q,rules);
            return {};
        } else if constexpr (std::same_as<T,ReplaceOrder>) {
            if (!enum_to(payload.priority,ReplacePriority::retain_only_same_price_reduction)) return {ErrorCode::invalid_enum,"replace.priority"};
            if (const auto e=side(payload.side)) return e;
            return priced_quantity(payload.price_ticks,payload.quantity,rules);
        } else if constexpr (std::same_as<T,Trade>) {
            if (payload.details.valueless_by_exception()) return {ErrorCode::unsupported,"trade.details"};
            return std::visit([&](const auto& trade)->Error {
                using U=std::decay_t<decltype(trade)>;
                if constexpr (std::same_as<U,TradePrint>) {
                    if (const auto e=available(trade.aggressor,"trade.aggressor")) return e;
                    if (trade.aggressor.data) if (const auto e=side(*trade.aggressor.data)) return e;
                } else if (const auto e=side(trade.resting_side)) return e;
                return priced_quantity(trade.price_ticks,trade.quantity,rules);
            },payload.details);
        } else if constexpr (std::same_as<T,Quote>) {
            if (payload.bid) if (const auto e=priced_quantity(payload.bid->price_ticks,payload.bid->quantity,rules)) return e;
            if (payload.ask) if (const auto e=priced_quantity(payload.ask->price_ticks,payload.ask->quantity,rules)) return e;
            if (payload.bid && payload.ask && payload.bid->price_ticks>payload.ask->price_ticks) return {ErrorCode::crossed_quote,"quote"};
            return {};
        } else if constexpr (std::same_as<T,BookReset>) {
            if (!enum_to(payload.reason,ResetReason::manual)) return {ErrorCode::invalid_enum,"reset.reason"};
            if (m.scope.data && payload.next_epoch<=m.scope.data->epoch) return {ErrorCode::invalid_range,"reset.next_epoch"};
            return {};
        } else if constexpr (std::same_as<T,Snapshot>) return snapshot(payload,rules,m);
        else if constexpr (std::same_as<T,SessionEvent>) {
            if (!enum_to(payload.action,SessionAction::close)) return {ErrorCode::invalid_enum,"session.action"};
            return available(payload.reason,"session.reason");
        } else return {ErrorCode::unsupported,"payload.wire_type"};
    },event.payload);
}
Result<ValidatedEvent> make_validated(const MarketEvent& event,const InstrumentRules& rules) noexcept {
    if (const auto e=validate(event,rules)) return Result<ValidatedEvent>::failure(e.code,e.field,e.index);
    return Result<ValidatedEvent>::success(ValidatedEvent(event,rules));
}
static_assert(std::is_nothrow_copy_constructible_v<MarketEvent>);
static_assert(std::is_nothrow_copy_constructible_v<ValidatedEvent>);
} // namespace gig
