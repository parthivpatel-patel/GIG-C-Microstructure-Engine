#pragma once
// Synthetic fixtures only. Not a production adapter, clock observation or data source.
#include <stdexcept>
#include "gig/market_event.hpp"
namespace gig::fixtures {
template<class T,std::integral I> constexpr T number(I value) {
    auto r=T::make(value);
    if (!r) throw std::logic_error("invalid fixture number");
    return *r.data;
}
constexpr Identity text(std::string_view value) {
    auto r=Identity::make(value);
    if (!r) throw std::logic_error("invalid fixture identity");
    return *r.data;
}
inline InstrumentRules rules() {
    return {number<InstrumentId>(1),number<VenueId>(1),number<PriceTicks>(1),number<PriceTicks>(INT64_MAX),
        number<QuantityLots>(UINT64_MAX),{1,100},{1,1}};
}
inline Metadata metadata() {
    Metadata m;
    m.instrument=Available<InstrumentId>::known(number<InstrumentId>(1));
    m.venue=Available<VenueId>::known(number<VenueId>(1));
    m.scope=Available<StreamScope>::known({number<StreamId>(1),text("fixture-session"),0,SequenceUnit::message});
    m.sequence=Available<SequenceNumber>::known(number<SequenceNumber>(0));
    m.event_time=Available<Timestamp<EventTimestamp>>::known({number<EventTimestamp>(0),Available<Clock>::known({ClockDomain::utc,text("fixture-clock")}),Available<types::TimestampUnit>::known(types::TimestampUnit::nanoseconds)});
    m.receive_time=Available<Timestamp<ReceiveTimestamp>>::known({number<ReceiveTimestamp>(10),Available<Clock>::known({ClockDomain::utc,text("fixture-clock")}),Available<types::TimestampUnit>::known(types::TimestampUnit::nanoseconds)});
    m.source_record=Available<Identity>::known(text("fixture:record:0"));
    m.capture_ordinal=Available<std::uint64_t>::known(0);
    m.provenance.dataset=Available<DatasetIdentity>::known({text("phase1-synthetic"),Available<Identity>::known(text("1")),Available<Identity>::known(text("synthetic-fixture:no-external-data")),Available<Digest>::missing(MissingReason::not_applicable)});
    m.provenance.origin=Available<Origin>::known(Origin::synthetic);
    m.provenance.source=Available<Source>::known(Source::generator);
    m.provenance.generator_seed=Available<std::uint64_t>::known(0);
    if (m.provenance.lineage.append({TransformationKind::generated,text("phase1-fixture"),text("1")})) throw std::logic_error("fixture lineage capacity");
    return m;
}
inline AddOrder order() { return {number<OrderId>(1),Side::buy,number<PriceTicks>(100),number<QuantityLots>(10)}; }
inline MarketEvent event() { return {metadata(),order()}; }
inline Snapshot snapshot(SnapshotKind kind=SnapshotKind::order_level) {
    Snapshot result{kind,SnapshotCoverage::complete,0,{},{},{}};
    const auto m=metadata();
    if (result.boundaries.append({*m.scope.data,*m.sequence.data,0,1})) throw std::logic_error("fixture boundary");
    if (kind==SnapshotKind::order_level) {
        if (result.orders.append({order(),0})) throw std::logic_error("fixture order");
    } else if (result.levels.append({Side::buy,number<PriceTicks>(100),number<QuantityLots>(10)})) throw std::logic_error("fixture level");
    return result;
}
} // namespace gig::fixtures
