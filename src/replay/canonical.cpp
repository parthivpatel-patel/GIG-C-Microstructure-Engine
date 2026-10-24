#include "gig/detail/canonical.hpp"
namespace gig::detail {
void canonical_scope(CanonicalWriter& w,const StreamScope& scope) {
    w.number(scope.stream.value());w.token(scope.session);w.number(scope.epoch);w.enumeration(scope.unit);
}
void canonical_rules(CanonicalWriter& w,const InstrumentRules& r) {
    w.number(r.instrument.value());w.number(r.venue.value());w.number(r.minimum_price.value());w.number(r.maximum_price.value());w.number(r.maximum_quantity.value());
    w.number(r.tick_size.numerator);w.number(r.tick_size.denominator);w.number(r.lot_size.numerator);w.number(r.lot_size.denominator);
}
namespace {
void add(CanonicalWriter& w,const AddOrder& p) { w.number(p.order_id.value());w.enumeration(p.side);w.number(p.price_ticks.value());w.number(p.quantity.value()); }
void priced(CanonicalWriter& w,PriceTicks p,QuantityLots q) { w.number(p.value());w.number(q.value()); }
template<class T> void stamp(CanonicalWriter& w,const Timestamp<T>& t) {
    w.number(t.nanoseconds.value());
    w.available(t.clock,[&](const Clock& c){w.enumeration(c.domain);w.token(c.identity);});
    w.available(t.precision,[&](auto p){w.enumeration(p);});
}
void metadata(CanonicalWriter& w,const Metadata& m) {
    w.number(m.schema_version);
    w.available(m.instrument,[&](auto id){w.number(id.value());});w.available(m.venue,[&](auto id){w.number(id.value());});
    w.available(m.scope,[&](const auto& s){canonical_scope(w,s);});w.available(m.sequence,[&](auto s){w.number(s.value());});
    w.number(m.subevent_index);w.number(m.subevent_count);
    w.available(m.event_time,[&](const auto& t){stamp(w,t);});w.available(m.receive_time,[&](const auto& t){stamp(w,t);});
    w.available(m.source_record,[&](const auto& id){w.token(id);});w.available(m.capture_ordinal,[&](auto n){w.number(n);});
    const auto& p=m.provenance;
    w.available(p.dataset,[&](const auto& d){w.token(d.identity);w.available(d.version,[&](const auto& v){w.token(v);});
        w.available(d.license_reference,[&](const auto& v){w.token(v);});w.available(d.sha256,[&](const auto& h){w.token(h);});});
    w.available(p.origin,[&](auto o){w.enumeration(o);});w.available(p.source,[&](auto s){w.enumeration(s);});
    w.available(p.generator_seed,[&](auto s){w.number(s);});
    w.list(p.lineage,[&](const auto& t){w.enumeration(t.kind);w.token(t.operation);w.token(t.version);});
    w.list(p.parents,[&](const auto& a){w.token(a.identity);w.available(a.sha256,[&](const auto& h){w.token(h);});});
}
}
void canonical_event(CanonicalWriter& w,const MarketEvent& event) {
    metadata(w,event.metadata);w.number(event.payload.index());
    std::visit([&](const auto& p) {
        using T=std::decay_t<decltype(p)>;
        if constexpr (std::same_as<T,AddOrder>) add(w,p);
        else if constexpr (std::same_as<T,CancelOrder>) {
            w.number(p.order_id.value());w.number(p.amount.index());if (auto q=std::get_if<QuantityLots>(&p.amount)) w.number(q->value());
        } else if constexpr (std::same_as<T,ReplaceOrder>) {
            w.number(p.old_order_id.value());w.number(p.new_order_id.value());w.enumeration(p.side);priced(w,p.price_ticks,p.quantity);w.enumeration(p.priority);
        } else if constexpr (std::same_as<T,Trade>) {
            w.number(p.details.index());std::visit([&](const auto& t){
                using U=std::decay_t<decltype(t)>;
                if constexpr (std::same_as<U,BookExecution>) {w.number(t.resting_order_id.value());w.enumeration(t.resting_side);}
                priced(w,t.price_ticks,t.quantity);
                if constexpr (std::same_as<U,TradePrint>) w.available(t.aggressor,[&](auto s){w.enumeration(s);});
            },p.details);
        } else if constexpr (std::same_as<T,Quote>) {
            for (const auto* level:{&p.bid,&p.ask}) {w.number(static_cast<unsigned>(level->has_value()));if (*level) priced(w,(*level)->price_ticks,(*level)->quantity);}
        } else if constexpr (std::same_as<T,BookReset>) {w.enumeration(p.reason);w.number(p.next_epoch);}
        else if constexpr (std::same_as<T,Snapshot>) {
            w.enumeration(p.kind);w.enumeration(p.coverage);w.number(p.depth);
            w.list(p.orders,[&](const auto& o){add(w,o.order);w.number(o.priority_index);});
            w.list(p.levels,[&](const auto& l){w.enumeration(l.side);priced(w,l.price_ticks,l.quantity);});
            w.list(p.boundaries,[&](const auto& b){canonical_scope(w,b.scope);w.number(b.sequence.value());w.number(b.last_subevent);w.number(b.subevent_count);});
        } else if constexpr (std::same_as<T,SessionEvent>) {w.enumeration(p.action);w.available(p.reason,[&](const auto& r){w.token(r);});}
        else w.number(p.wire_type);
    },event.payload);
}
} // namespace gig::detail
