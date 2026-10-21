#include <iostream>
#include <string_view>
#include <type_traits>
#include "fixtures/synthetic/phase1.hpp"
using namespace gig; using namespace gig::fixtures;
static_assert(noexcept(validate(std::declval<const MarketEvent&>(),std::declval<const InstrumentRules&>())));
static_assert(noexcept(make_validated(std::declval<const MarketEvent&>(),std::declval<const InstrumentRules&>())));
static_assert(!std::is_default_constructible_v<ValidatedEvent>);
namespace {
int checks=0,failures=0;
void check(bool ok,const char* label) { ++checks;if (!ok) { ++failures;std::cerr << "FAIL " << label << '\n'; } }
void error(const MarketEvent& e,ErrorCode expected,const char* label) {
    const auto before=e;
    const auto result=make_validated(e,rules());
    check(!result && result.error.code==expected && !result.error.field.empty(),label);
    check(e==before,"rejection preserves input");
}
void valid_payload(EventPayload payload) {
    auto e=event();e.payload=payload;
    const auto result=make_validated(e,rules());
    check(bool(result),"valid payload");
    if (result) { check(result.data->event()==e,"validated copy preserves metadata and payload");check(result.data->rules()==rules(),"validated context retained"); }
}
}
int main(int argc,char** argv) {
    if (argc!=2) return 2;
    const std::string_view name{argv[1]};
    if (name=="add") {
        valid_payload(order());auto e=event();
        for (unsigned i=2;i<=255;++i) { auto a=order();a.side=static_cast<Side>(i);e.payload=a;error(e,ErrorCode::invalid_enum,"invalid side"); }
        auto a=order();a.quantity=number<QuantityLots>(0);e.payload=a;error(e,ErrorCode::invalid_range,"zero quantity");
        auto r=rules();r.minimum_price=number<PriceTicks>(-10);a.price_ticks=number<PriceTicks>(-1);a.quantity=number<QuantityLots>(1);e.payload=a;
        check(!validate(e,r),"negative instrument prices supported explicitly");
        r.minimum_price=number<PriceTicks>(INT64_MIN);r.maximum_price=number<PriceTicks>(INT64_MAX);a.price_ticks=number<PriceTicks>(INT64_MIN);a.quantity=number<QuantityLots>(UINT64_MAX);e.payload=a;
        check(!validate(e,r),"numeric extrema within explicit instrument bounds");
        r.maximum_quantity=number<QuantityLots>(1);check(validate(e,r).code==ErrorCode::invalid_range,"quantity cap");
    } else if (name=="cancel") {
        valid_payload(CancelOrder{number<OrderId>(1),CancelAll{}});
        valid_payload(CancelOrder{number<OrderId>(1),number<QuantityLots>(5)});
        auto e=event();e.payload=CancelOrder{number<OrderId>(1),number<QuantityLots>(0)};error(e,ErrorCode::invalid_range,"zero cancel");
    } else if (name=="replace") {
        ReplaceOrder a{number<OrderId>(1),number<OrderId>(2),Side::sell,number<PriceTicks>(101),number<QuantityLots>(10),ReplacePriority::lose};
        valid_payload(a);a.new_order_id=a.old_order_id;a.priority=ReplacePriority::retain_only_same_price_reduction;valid_payload(a);
        auto e=event();a.priority=static_cast<ReplacePriority>(255);e.payload=a;error(e,ErrorCode::invalid_enum,"priority enum");
        a.priority=ReplacePriority::lose;a.side=static_cast<Side>(255);e.payload=a;error(e,ErrorCode::invalid_enum,"replace side");
        a.side=Side::buy;a.quantity=number<QuantityLots>(0);e.payload=a;error(e,ErrorCode::invalid_range,"zero replace");
    } else if (name=="trade") {
        TradePrint print{number<PriceTicks>(100),number<QuantityLots>(10),Available<Side>::missing(MissingReason::not_reported)};
        valid_payload(Trade{print});print.aggressor=Available<Side>::known(Side::sell);valid_payload(Trade{print});
        auto e=event();print.aggressor=Available<Side>::known(static_cast<Side>(255));e.payload=Trade{print};error(e,ErrorCode::invalid_enum,"aggressor enum");
        BookExecution execution{number<OrderId>(1),Side::buy,number<PriceTicks>(100),number<QuantityLots>(1)};
        valid_payload(Trade{execution});execution.resting_side=static_cast<Side>(3);e.payload=Trade{execution};error(e,ErrorCode::invalid_enum,"resting side");
        execution.resting_side=Side::buy;execution.quantity=number<QuantityLots>(0);e.payload=Trade{execution};error(e,ErrorCode::invalid_range,"execution zero");
        check(std::variant_size_v<decltype(Trade::details)> == 2,"trade alternatives distinct");
    } else if (name=="quote") {
        valid_payload(Quote{});
        Quote q{QuoteLevel{number<PriceTicks>(100),number<QuantityLots>(1)},std::nullopt};valid_payload(q);
        q.ask=QuoteLevel{number<PriceTicks>(101),number<QuantityLots>(2)};valid_payload(q);
        q.ask->price_ticks=number<PriceTicks>(100);valid_payload(q);
        q.ask->price_ticks=number<PriceTicks>(99);auto e=event();e.payload=q;error(e,ErrorCode::crossed_quote,"crossed quote");
        q.ask->price_ticks=number<PriceTicks>(101);q.ask->quantity=number<QuantityLots>(0);e.payload=q;error(e,ErrorCode::invalid_range,"zero quote");
    } else if (name=="reset") {
        for (const auto reason:{ResetReason::session_start,ResetReason::sequence_gap,ResetReason::recovery,ResetReason::manual}) valid_payload(BookReset{reason,1});
        auto e=event();e.payload=BookReset{ResetReason::manual,0};error(e,ErrorCode::invalid_range,"epoch must advance");
        e.metadata.scope.data->epoch=UINT64_MAX;e.payload=BookReset{ResetReason::manual,UINT64_MAX};error(e,ErrorCode::invalid_range,"epoch cannot wrap");
        e=event();e.payload=BookReset{static_cast<ResetReason>(255),1};error(e,ErrorCode::invalid_enum,"reset enum");
    } else if (name=="session") {
        for (const auto action:{SessionAction::open,SessionAction::halt,SessionAction::resume,SessionAction::close})
            valid_payload(SessionEvent{action,Available<Identity>::missing(MissingReason::not_reported)});
        auto e=event();e.payload=SessionEvent{static_cast<SessionAction>(255),{}};error(e,ErrorCode::invalid_enum,"session enum");
    } else if (name=="snapshot") {
        auto s=snapshot();valid_payload(s);valid_payload(snapshot(SnapshotKind::aggregated));
        auto e=event();
        check(!s.orders.append(*s.orders.items[0]),"append duplicate fixture");e.payload=s;error(e,ErrorCode::duplicate,"duplicate snapshot ID");
        s=snapshot();s.orders.items[0]->order.side=static_cast<Side>(255);e.payload=s;error(e,ErrorCode::invalid_enum,"snapshot side");
        s=snapshot();s.orders.count=65;e.payload=s;error(e,ErrorCode::capacity,"snapshot capacity");
        s=snapshot();s.orders.items[1]=s.orders.items[0];e.payload=s;error(e,ErrorCode::inconsistent_metadata,"hidden suffix order");
        s=snapshot();s.coverage=SnapshotCoverage::bounded_depth;s.depth=1;valid_payload(s);
        s.depth=0;e.payload=s;error(e,ErrorCode::inconsistent_metadata,"bounded depth zero");
        s=snapshot();s.boundaries={};e.payload=s;error(e,ErrorCode::missing_metadata,"snapshot boundaries required");
        s=snapshot();check(!s.boundaries.append(*s.boundaries.items[0]),"duplicate boundary fixture");e.payload=s;error(e,ErrorCode::duplicate,"duplicate boundary");
        s=snapshot();s.boundaries.items[0]->last_subevent=1;e.payload=s;error(e,ErrorCode::invalid_range,"boundary subevent");
        s=snapshot();s.boundaries.items[0]->sequence=number<SequenceNumber>(1);e.payload=s;error(e,ErrorCode::invalid_range,"future boundary");
        s=snapshot(SnapshotKind::aggregated);check(!s.levels.append(*s.levels.items[0]),"duplicate level fixture");e.payload=s;error(e,ErrorCode::duplicate,"duplicate aggregate");
        s=snapshot();auto a=order();a.order_id=number<OrderId>(2);check(!s.orders.append({a,0}),"priority fixture");e.payload=s;error(e,ErrorCode::duplicate,"duplicate priority");
        s=snapshot(SnapshotKind::aggregated);check(!s.levels.append({Side::sell,number<PriceTicks>(99),number<QuantityLots>(1)}),"cross fixture");e.payload=s;error(e,ErrorCode::crossed_quote,"crossed snapshot");
        s=snapshot();s.orders={};valid_payload(s);
        s=snapshot();s.levels.items[0]=SnapshotLevel{Side::buy,number<PriceTicks>(100),number<QuantityLots>(1)};s.levels.count=1;e.payload=s;error(e,ErrorCode::inconsistent_metadata,"mixed snapshot representation");
        s=snapshot();e=event();e.metadata.subevent_count=2;s.boundaries.items[0]->subevent_count=2;s.boundaries.items[0]->last_subevent=1;e.payload=s;error(e,ErrorCode::invalid_range,"same-sequence future subevent");
        e=event();
        s=snapshot();s.orders.items[0]->order.quantity=number<QuantityLots>(UINT64_MAX);
        a=order();a.order_id=number<OrderId>(2);check(!s.orders.append({a,1}),"overflow fixture");e.payload=s;error(e,ErrorCode::overflow,"snapshot level sum overflow");
        s=snapshot();s.coverage=SnapshotCoverage::bounded_depth;s.depth=1;
        a=order();a.order_id=number<OrderId>(2);a.price_ticks=number<PriceTicks>(99);check(!s.orders.append({a,1}),"depth fixture");e.payload=s;error(e,ErrorCode::invalid_range,"actual depth exceeds declared depth");
        s=snapshot();s.kind=static_cast<SnapshotKind>(255);e.payload=s;error(e,ErrorCode::invalid_enum,"snapshot kind enum");
        s=snapshot();s.coverage=static_cast<SnapshotCoverage>(255);e.payload=s;error(e,ErrorCode::invalid_enum,"snapshot coverage enum");
    } else if (name=="metadata") {
        auto e=event();valid_payload(e.payload);
        e.metadata.instrument={};error(e,ErrorCode::missing_metadata,"missing instrument");
        check(!validate(e,rules(),ValidationMode::inspect_incomplete),"explicit incomplete inspect");
        check(!validate(Metadata{},ValidationMode::inspect_incomplete),"unknown metadata represented");
        e=event();e.metadata.instrument=Available<InstrumentId>::known(number<InstrumentId>(2));error(e,ErrorCode::identity_mismatch,"instrument mismatch");
        e=event();e.metadata.venue=Available<VenueId>::known(number<VenueId>(2));error(e,ErrorCode::identity_mismatch,"venue mismatch");
        e=event();e.metadata.scope={};error(e,ErrorCode::missing_metadata,"missing scope");
        e=event();e.metadata.sequence={};error(e,ErrorCode::missing_metadata,"missing sequence");
        e=event();e.metadata.source_record={};error(e,ErrorCode::missing_metadata,"missing record");
        e=event();e.metadata.event_time={};e.metadata.receive_time={};check(bool(make_validated(e,rules())),"timestamps explicitly missing");
        e.metadata.event_time.reason=MissingReason::none;error(e,ErrorCode::inconsistent_metadata,"missing without reason");
        e=event();e.metadata.instrument.reason=static_cast<MissingReason>(255);error(e,ErrorCode::invalid_enum,"missing reason enum");
        e=event();e.metadata.schema_version=2;error(e,ErrorCode::unsupported,"schema unsupported");
        e=event();e.metadata.subevent_count=0;error(e,ErrorCode::invalid_range,"subevent count");
        e=event();e.metadata.subevent_index=1;error(e,ErrorCode::invalid_range,"subevent index");
        e=event();e.metadata.scope.data->unit=SequenceUnit::event;e.metadata.subevent_count=2;error(e,ErrorCode::inconsistent_metadata,"event unit cannot contain subevents");
        e=event();e.metadata.scope.data->unit=static_cast<SequenceUnit>(255);error(e,ErrorCode::invalid_enum,"sequence unit enum");
        e=event();e.payload=UnsupportedEvent{999};error(e,ErrorCode::unsupported,"unsupported wire payload");
        check(validate(event(),rules(),static_cast<ValidationMode>(255)).code==ErrorCode::invalid_enum,"validation mode enum");
        auto r=rules();r.tick_size={0,1};check(validate(event(),r).code==ErrorCode::invalid_range,"invalid instrument scale");
        r=rules();r.minimum_price=number<PriceTicks>(200);r.maximum_price=number<PriceTicks>(100);check(bool(validate(r)),"inverted instrument range");
        check(!Identity::make("") && !Identity::make("has space") && !Identity::make(std::string_view("a\0b",3)),"token malformed");
        std::array<char,129> over{};over.fill('a');check(!Identity::make({over.data(),over.size()}),"token length cap");
    } else if (name=="timestamps") {
        auto e=event();
        e.metadata.event_time.data->nanoseconds=number<EventTimestamp>(INT64_MIN);
        e.metadata.receive_time.data->nanoseconds=number<ReceiveTimestamp>(INT64_MAX);
        check(bool(make_validated(e,rules())),"timestamps full int64 range");
        e=event();e.metadata.event_time.data->clock.data->domain=ClockDomain::venue_utc_unsynchronized;
        e.metadata.event_time.data->nanoseconds=number<EventTimestamp>(10000);check(bool(make_validated(e,rules())),"no cross-clock receive ordering assumption");
        e.metadata.receive_time.data->clock.data->domain=ClockDomain::monotonic;error(e,ErrorCode::unsupported,"receive clock unsupported");
        e=event();e.metadata.event_time.data->clock.data->domain=static_cast<ClockDomain>(255);error(e,ErrorCode::invalid_enum,"clock enum");
        e=event();e.metadata.event_time.data->precision=Available<types::TimestampUnit>::known(static_cast<types::TimestampUnit>(255));error(e,ErrorCode::invalid_enum,"precision enum");
        e=event();e.metadata.event_time.data->nanoseconds=number<EventTimestamp>(1);e.metadata.event_time.data->precision=Available<types::TimestampUnit>::known(types::TimestampUnit::microseconds);error(e,ErrorCode::inconsistent_metadata,"precision mismatch");
        e.metadata.event_time.data->nanoseconds=number<EventTimestamp>(-1000);check(bool(make_validated(e,rules())),"negative aligned time");
        e=event();e.metadata.event_time.data->precision={};error(e,ErrorCode::missing_metadata,"known time missing precision");
        check(!validate(e,rules(),ValidationMode::inspect_incomplete),"unknown precision preserves known timestamp");
        e.metadata.event_time.data->clock={};check(!validate(e,rules(),ValidationMode::inspect_incomplete),"unknown clock preserves known timestamp");
    } else if (name=="provenance") {
        auto e=event();auto checked=make_validated(e,rules());check(bool(checked),"synthetic provenance");
        e.metadata.provenance.generator_seed=Available<std::uint64_t>::known(42);
        if (checked) check(checked.data->event().metadata.provenance.generator_seed.data==0,"validated ownership independent of draft edits");
        e.metadata.provenance.generator_seed={};error(e,ErrorCode::missing_metadata,"synthetic seed required");
        e=event();e.metadata.provenance.dataset={};error(e,ErrorCode::missing_metadata,"dataset missing");
        e=event();e.metadata.provenance.origin=Available<Origin>::known(static_cast<Origin>(255));error(e,ErrorCode::invalid_enum,"origin enum");
        e=event();e.metadata.provenance.source=Available<Source>::known(static_cast<Source>(255));error(e,ErrorCode::invalid_enum,"source enum");
        e=event();e.metadata.provenance.lineage.items[0]->kind=static_cast<TransformationKind>(255);error(e,ErrorCode::invalid_enum,"lineage enum");
        e=event();e.metadata.provenance.lineage={};error(e,ErrorCode::missing_metadata,"lineage missing");
        e=event();e.metadata.provenance.origin=Available<Origin>::known(Origin::observed);error(e,ErrorCode::inconsistent_metadata,"cannot relabel generated observed");
        e.metadata.provenance.generator_seed={};e.metadata.provenance.source=Available<Source>::known(Source::exchange);
        e.metadata.provenance.lineage.items[0]->kind=TransformationKind::observed;
        check(bool(make_validated(e,rules())),"observed root supported without fabricated seed");
        check(!e.metadata.provenance.lineage.append({TransformationKind::normalized,text("normalize"),text("1")}),"derived fixture");
        error(e,ErrorCode::missing_metadata,"derived needs parent");
        check(!e.metadata.provenance.parents.append({text("source-artifact"),{}}),"parent fixture");
        check(bool(make_validated(e,rules())),"observed lineage and parent retained");
        checked=make_validated(e,rules());if (checked) check(checked.data->event()==e,"full derived provenance equality");
        check(!e.metadata.provenance.parents.append(*e.metadata.provenance.parents.items[0]),"duplicate parent fixture");error(e,ErrorCode::duplicate,"duplicate parents");
        e=event();e.metadata.provenance.dataset.data->sha256=Available<Digest>::known(*Digest::make("abc").data);error(e,ErrorCode::malformed,"digest length");
        std::array<char,64> chars{};chars.fill('a');auto digest=*Digest::make({chars.data(),chars.size()}).data;
        e.metadata.provenance.dataset.data->sha256=Available<Digest>::known(digest);check(bool(make_validated(e,rules())),"hex digest syntax only, not authenticity claim");
        chars.fill('g');e.metadata.provenance.dataset.data->sha256=Available<Digest>::known(*Digest::make({chars.data(),chars.size()}).data);error(e,ErrorCode::malformed,"digest hex");
        e=event();e.metadata.provenance.dataset.data->version={};error(e,ErrorCode::missing_metadata,"dataset version missing");
        check(!validate(e,rules(),ValidationMode::inspect_incomplete),"known dataset unknown version retained");
        e=event();e.metadata.provenance.dataset.data->license_reference={};error(e,ErrorCode::missing_metadata,"license missing");
        e=event();e.metadata.provenance.origin={};error(e,ErrorCode::missing_metadata,"origin missing");
        e=event();e.metadata.provenance.source={};error(e,ErrorCode::missing_metadata,"source missing");
        e=event();e.metadata.provenance.lineage.count=9;error(e,ErrorCode::capacity,"lineage capacity");
        e=event();e.metadata.provenance.generator_seed.reason=MissingReason::unavailable;error(e,ErrorCode::inconsistent_metadata,"seed reason inconsistent");
        e=event();e.metadata.provenance.parents.count=9;error(e,ErrorCode::capacity,"parent capacity");
    } else return 2;
    std::cout << "owned MarketEvent bytes=" << sizeof(MarketEvent) << "\n";
    std::cout << name << ": " << checks << " checks, " << failures << " failures\n";
    return failures==0?0:1;
}
