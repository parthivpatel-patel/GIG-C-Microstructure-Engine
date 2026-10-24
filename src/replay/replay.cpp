#include "gig/replay/replay.hpp"
#include "gig/detail/canonical.hpp"
#include <algorithm>
#include <cassert>
#include <stdexcept>

namespace gig {
namespace {
template<class T,std::size_t N> Error valid_list(const BoundedList<T,N>& x,std::string_view field) noexcept {
    if (x.count>N) return {ErrorCode::capacity,field};
    for (std::size_t i=0;i<N;++i) if (x.items[i].has_value()!=(i<x.count)) return {ErrorCode::inconsistent_metadata,field,i};
    return {};
}
Error plan_check(const RestartPlan& plan,BookSession session,VenueId venue) noexcept {
    if (const auto e=valid_list(plan,"streams")) return e;
    if (plan.count==0) return {ErrorCode::missing_metadata,"streams"};
    for (std::size_t i=0;i<plan.count;++i) {
        const auto& s=*plan.items[i];
        if (s.venue!=venue || s.scope.session!=session.session || s.scope.epoch!=session.epoch) return {ErrorCode::session_boundary,"streams.scope",i};
        if (s.scope.unit!=SequenceUnit::event && s.scope.unit!=SequenceUnit::message) return {ErrorCode::invalid_enum,"streams.unit",i};
        for (std::size_t j=0;j<i;++j) if (s.scope.stream==plan.items[j]->scope.stream || s.rank==plan.items[j]->rank) return {ErrorCode::duplicate,"streams.id_or_rank",i};
    }
    return {};
}
StreamCursor cursor_start(const StreamStart& start) noexcept { return {start,start.first_sequence,0,0,std::nullopt,0,0,false}; }
void consume(StreamCursor& c,SequenceNumber seq,std::uint32_t sub,std::uint32_t count) noexcept {
    c.last_sequence=seq;c.last_subevent=sub;c.last_message_count=count;
    if (sub==count-1) {
        c.next_subevent=0;c.message_count=0;
        const auto next=types::next_sequence(seq);
        if (next) c.expected=*next.data;else {c.expected=seq;c.exhausted=true;}
    } else {c.expected=seq;c.next_subevent=sub+1;c.message_count=count;}
}
void write_start(detail::CanonicalWriter& w,const StreamStart& s) {
    w.number(s.venue.value());detail::canonical_scope(w,s.scope);w.token(s.dataset);w.token(s.dataset_version);w.number(s.first_sequence.value());w.number(s.rank);
}
}
ReplayEngine::ReplayEngine(OrderBook book,ReplayConfig config,std::pmr::memory_resource* resource) noexcept
    :book_(std::move(book)),config_(config),resource_(resource),journal_(resource),restart_plans_(resource) {
    if (config_.initial_state==InitialBookState::requires_snapshot) continuity_error_=Error{ErrorCode::recovery_required,"initial_snapshot_required"};
    for (std::size_t i=0;i<config_.streams.count;++i) {
        cursors_.items[i]=cursor_start(*config_.streams.items[i]);++cursors_.count;
    }
}
Result<ReplayEngine> ReplayEngine::create(InstrumentRules rules,ReplayConfig config,BookLimits limits,std::pmr::memory_resource* resource) noexcept {
    if (const auto e=plan_check(config.streams,config.session,rules.venue)) return Result<ReplayEngine>::failure(e.code,e.field,e.index);
    if (config.ordering!=OrderingPolicy::capture_ordinal && config.ordering!=OrderingPolicy::timestamp_rank) return Result<ReplayEngine>::failure(ErrorCode::invalid_enum,"ordering_policy");
    if (config.initial_state!=InitialBookState::requires_snapshot && config.initial_state!=InitialBookState::declared_empty) return Result<ReplayEngine>::failure(ErrorCode::invalid_enum,"initial_book_state");
    if (config.max_journal_records==0 || config.max_journal_records>100000) return Result<ReplayEngine>::failure(ErrorCode::capacity,"journal.limit");
    if (static_cast<unsigned>(config.timestamp_clock.reason)>static_cast<unsigned>(MissingReason::not_applicable) ||
        config.timestamp_clock.data.has_value()!=(config.timestamp_clock.reason==MissingReason::none)) return Result<ReplayEngine>::failure(ErrorCode::inconsistent_metadata,"timestamp_clock");
    if (config.ordering==OrderingPolicy::timestamp_rank && !config.timestamp_clock.data) return Result<ReplayEngine>::failure(ErrorCode::missing_metadata,"timestamp_clock");
    if (const auto e=valid_list(config.additional_instruments,"additional_instruments")) return Result<ReplayEngine>::failure(e.code,e.field,e.index);
    for (std::size_t i=0;i<config.additional_instruments.count;++i) {
        const auto& r=*config.additional_instruments.items[i];
        if (const auto e=validate(r)) return Result<ReplayEngine>::failure(e.code,e.field,i);
        if (r.venue!=rules.venue || r.instrument==rules.instrument) return Result<ReplayEngine>::failure(ErrorCode::duplicate,"additional_instruments",i);
        for (std::size_t j=0;j<i;++j) if (r.instrument==config.additional_instruments.items[j]->instrument) return Result<ReplayEngine>::failure(ErrorCode::duplicate,"additional_instruments",i);
    }
    auto book=OrderBook::create(rules,config.session,limits,resource);
    if (!book) return Result<ReplayEngine>::failure(book.error.code,book.error.field);
    return Result<ReplayEngine>::success(ReplayEngine(std::move(*book.data),config,resource));
}
std::optional<std::size_t> ReplayEngine::stream_index(StreamId stream) const noexcept {
    for (std::size_t i=0;i<cursors_.count;++i) if (cursors_.items[i]->start.scope.stream==stream) return i;
    return std::nullopt;
}
std::optional<StreamCursor> ReplayEngine::cursor(StreamId stream) const noexcept {
    const auto i=stream_index(stream);return i?cursors_.items[*i]:std::nullopt;
}
Error ReplayEngine::source_check(const StreamStart& s,const Metadata& m,bool allow_new_scope) const noexcept {
    const auto& d=*m.provenance.dataset.data;
    if (*m.venue.data!=s.venue || d.identity!=s.dataset || *d.version.data!=s.dataset_version) return {ErrorCode::identity_mismatch,"stream.dataset_or_venue"};
    if (m.scope.data->stream!=s.scope.stream || m.scope.data->unit!=s.scope.unit) return {ErrorCode::identity_mismatch,"stream.scope"};
    if (!allow_new_scope && *m.scope.data!=s.scope) return {ErrorCode::session_boundary,"stream.session_or_epoch"};
    return {};
}
Result<StreamCursor> ReplayEngine::advance(const StreamCursor& current,const Metadata& m) const noexcept {
    if (const auto e=source_check(current.start,m)) return Result<StreamCursor>::failure(e.code,e.field);
    const auto seq=*m.sequence.data;
    if (current.last_sequence && seq==*current.last_sequence && m.subevent_index==current.last_subevent)
        return Result<StreamCursor>::failure(ErrorCode::sequence_duplicate,"sequence");
    if (current.exhausted) return Result<StreamCursor>::failure(ErrorCode::sequence_exhausted,"sequence");
    if (seq<current.expected || (seq==current.expected && m.subevent_index<current.next_subevent))
        return Result<StreamCursor>::failure(ErrorCode::sequence_regression,"sequence");
    if (seq>current.expected || m.subevent_index>current.next_subevent) return Result<StreamCursor>::failure(ErrorCode::sequence_gap,"sequence");
    if (current.next_subevent!=0 && m.subevent_count!=current.message_count)
        return Result<StreamCursor>::failure(ErrorCode::inconsistent_metadata,"sequence.message_count");
    auto next=current;consume(next,seq,m.subevent_index,m.subevent_count);return Result<StreamCursor>::success(next);
}
Error ReplayEngine::order_check(const Metadata& m,std::uint32_t rank) const noexcept {
    if (config_.ordering==OrderingPolicy::capture_ordinal) {
        if (!m.capture_ordinal.data) return {ErrorCode::missing_metadata,"capture_ordinal"};
        if (last_ordinal_ && *m.capture_ordinal.data<=*last_ordinal_) return {ErrorCode::ordering_error,"capture_ordinal"};
    } else {
        if (!m.event_time.data || !m.event_time.data->clock.data) return {ErrorCode::missing_metadata,"ordering.event_time"};
        const auto& time=*m.event_time.data;
        if (time.clock.data->domain!=ClockDomain::utc || time.clock.data->identity!=*config_.timestamp_clock.data)
            return {ErrorCode::unsupported,"ordering.common_utc_clock"};
        const OrderKey key{time.nanoseconds.value(),rank,m.sequence.data->value(),m.subevent_index};
        if (last_key_ && key<=*last_key_) return {ErrorCode::ordering_error,"timestamp_rank_key"};
    }
    return {};
}
void ReplayEngine::order_commit(const Metadata& m,std::uint32_t rank) noexcept {
    if (config_.ordering==OrderingPolicy::capture_ordinal) last_ordinal_=*m.capture_ordinal.data;
    else last_key_=OrderKey{m.event_time.data->nanoseconds.value(),rank,m.sequence.data->value(),m.subevent_index};
}
Error ReplayEngine::reserve_record() noexcept {
    static_assert(std::is_nothrow_copy_constructible_v<JournalRecord>);
    static_assert(std::is_nothrow_move_constructible_v<JournalRecord>);
    static_assert(std::is_nothrow_copy_constructible_v<RestartPlan>);
    if (journal_.size()>=config_.max_journal_records) return {ErrorCode::capacity,"journal.records"};
    try {
        if (journal_.size()==journal_.capacity()) journal_.reserve(std::min(config_.max_journal_records,std::max(journal_.size()+1,journal_.capacity()*2)));
        return {};
    } catch (const std::bad_alloc&) { return {ErrorCode::resource_exhausted,"journal"}; }
      catch (const std::length_error&) { return {ErrorCode::capacity,"journal"}; }
}
Error ReplayEngine::reserve_restart() noexcept {
    // Only reset records own plans; both vectors are prepared before native mutation.
    // The same record cap bounds this archive; indices survive vector reallocation.
    if (restart_plans_.size()>=config_.max_journal_records) return {ErrorCode::capacity,"journal.restarts"};
    try {
        if (restart_plans_.size()==restart_plans_.capacity())
            restart_plans_.reserve(std::min(config_.max_journal_records,
                std::max(restart_plans_.size()+1,restart_plans_.capacity()*2)));
        return {};
    } catch (const std::bad_alloc&) { return {ErrorCode::resource_exhausted,"journal.restarts"}; }
      catch (const std::length_error&) { return {ErrorCode::capacity,"journal.restarts"}; }
}
const InstrumentRules* ReplayEngine::instrument_rules(const Metadata& m) const noexcept {
    if (*m.instrument.data==book_.rules().instrument) return &book_.rules();
    for (std::size_t i=0;i<config_.additional_instruments.count;++i)
        if (*m.instrument.data==config_.additional_instruments.items[i]->instrument) return &*config_.additional_instruments.items[i];
    return nullptr;
}
Error ReplayEngine::stop(Error error) noexcept { continuity_error_=error;return error; }
Error ReplayEngine::apply(const MarketEvent& event) noexcept {
    if (needs_recovery()) return {ErrorCode::recovery_required,"replay"};
    if (const auto e=validate(event.metadata)) return e;
    const auto found=stream_index(event.metadata.scope.data->stream);
    if (!found) return stop({ErrorCode::identity_mismatch,"unconfigured_stream"});
    auto next=advance(*cursors_.items[*found],event.metadata);
    if (!next) return stop(next.error);
    if (const auto e=order_check(event.metadata,next.data->start.rank)) return stop(e);
    const auto* rules=instrument_rules(event.metadata);
    if (!rules) return {ErrorCode::unsupported,"unconfigured_instrument"};
    if (const auto e=validate(event,*rules)) return e;
    if (std::holds_alternative<BookReset>(event.payload) || std::holds_alternative<Snapshot>(event.payload))
        return {ErrorCode::unsupported,"explicit_reset_or_recovery_required"};
    if (const auto e=reserve_record()) return e;
    const bool target=rules->instrument==book_.rules().instrument;
    if (target) if (const auto e=book_.apply(event)) return e;
    // Capacity is reserved; all stored values/cursors have nonthrowing copy constructors.
    journal_.push_back({event,target?JournalDisposition::book_event:JournalDisposition::filtered_instrument,std::nullopt});
    cursors_.items[*found]=*next.data;order_commit(event.metadata,next.data->start.rank);
    assert(!book_.check_invariants());return {};
}
ReplayBatchResult ReplayEngine::run(std::span<const MarketEvent> events) noexcept {
    if (needs_recovery()) return {0,{ErrorCode::recovery_required,"replay.run"},std::nullopt};
    for (std::size_t i=0;i<events.size();++i) if (const auto e=apply(events[i])) return {i,e,i};
    return {events.size(),{},std::nullopt};
}
Error ReplayEngine::reset(const MarketEvent& event,const RestartPlan& starts) noexcept {
    if (needs_recovery()) return {ErrorCode::recovery_required,"replay.reset"};
    if (const auto e=validate(event,book_.rules())) return e;
    const auto* reset=std::get_if<BookReset>(&event.payload);
    if (!reset) return {ErrorCode::unsupported,"reset.payload"};
    const auto found=stream_index(event.metadata.scope.data->stream);
    if (!found) return stop({ErrorCode::identity_mismatch,"reset.stream"});
    auto advanced=advance(*cursors_.items[*found],event.metadata);if (!advanced) return stop(advanced.error);
    if (const auto e=order_check(event.metadata,advanced.data->start.rank)) return stop(e);
    if (starts.count==0 || starts.count>8 || !starts.items[0]) return {ErrorCode::missing_metadata,"reset.starts"};
    const BookSession next_session{starts.items[0]->scope.session,reset->next_epoch};
    if (const auto e=plan_check(starts,next_session,book_.rules().venue)) return e;
    if (starts.count!=cursors_.count) return {ErrorCode::missing_metadata,"reset.all_streams"};
    if (advanced.data->next_subevent!=0) return {ErrorCode::session_boundary,"reset.mid_message"};
    auto next=cursors_;
    for (std::size_t i=0;i<cursors_.count;++i) {
        const auto& old=*cursors_.items[i];
        if (i!=*found && old.next_subevent!=0) return {ErrorCode::session_boundary,"reset.pending_message"};
        bool seen=false;
        for (std::size_t j=0;j<starts.count;++j) if (starts.items[j]->scope.stream==old.start.scope.stream) {
            const auto& s=*starts.items[j];
            if (s.venue!=old.start.venue || s.dataset!=old.start.dataset || s.dataset_version!=old.start.dataset_version ||
                s.rank!=old.start.rank || s.scope.unit!=old.start.scope.unit) return {ErrorCode::identity_mismatch,"reset.source"};
            next.items[i]=cursor_start(s);seen=true;break;
        }
        if (!seen) return {ErrorCode::missing_metadata,"reset.all_streams"};
    }
    if (const auto e=reserve_record()) return e;
    if (const auto e=reserve_restart()) return e;
    if (const auto e=book_.apply(event,next_session)) return e;
    // Reserved storage and nothrow value copies make the joint append infallible.
    const auto index=restart_plans_.size();
    restart_plans_.push_back(starts);
    journal_.push_back({event,JournalDisposition::reset,index});cursors_=next;
    order_commit(event.metadata,advanced.data->start.rank);return {};
}
Error ReplayEngine::recover(const MarketEvent& event) noexcept {
    if (const auto e=validate(event,book_.rules())) return e;
    const auto* snapshot=std::get_if<Snapshot>(&event.payload);
    if (!snapshot || snapshot->kind!=SnapshotKind::order_level || snapshot->coverage!=SnapshotCoverage::complete)
        return {ErrorCode::unsupported,"recovery.complete_order_snapshot"};
    const auto found=stream_index(event.metadata.scope.data->stream);
    if (!found) return {ErrorCode::identity_mismatch,"recovery.stream"};
    if (const auto e=source_check(cursors_.items[*found]->start,event.metadata,true)) return e;
    if (const auto e=order_check(event.metadata,cursors_.items[*found]->start.rank)) return e;
    if (snapshot->boundaries.count!=cursors_.count) return {ErrorCode::missing_metadata,"recovery.all_stream_boundaries"};
    const BookSession session{event.metadata.scope.data->session,event.metadata.scope.data->epoch};
    auto next=cursors_;
    for (std::size_t i=0;i<cursors_.count;++i) {
        const auto& old=*cursors_.items[i];bool seen=false;
        for (std::size_t j=0;j<snapshot->boundaries.count;++j) {
            const auto& b=*snapshot->boundaries.items[j];if (b.scope.stream!=old.start.scope.stream) continue;
            if (b.scope.session!=session.session || b.scope.epoch!=session.epoch || b.scope.unit!=old.start.scope.unit)
                return {ErrorCode::session_boundary,"recovery.boundary_scope",j};
            const bool same=b.scope==old.start.scope;
            if ((!same && b.scope.epoch<=old.start.scope.epoch) || (same && old.last_sequence &&
                (b.sequence<*old.last_sequence || (b.sequence==*old.last_sequence && b.last_subevent<old.last_subevent))))
                return {ErrorCode::sequence_regression,"recovery.boundary",j};
            if (same && !old.last_sequence && b.sequence<old.expected &&
                (b.sequence.value()==UINT64_MAX || b.sequence.value()+1<old.expected.value() || b.last_subevent+1!=b.subevent_count))
                return {ErrorCode::sequence_regression,"recovery.initial_boundary",j};
            if (same && old.last_sequence && b.sequence==*old.last_sequence && b.subevent_count!=old.last_message_count)
                return {ErrorCode::inconsistent_metadata,"recovery.message_count",j};
            if (i==*found && same && old.last_sequence && b.sequence==*old.last_sequence && b.last_subevent==old.last_subevent)
                return {ErrorCode::sequence_duplicate,"recovery.source_boundary",j};
            if (i==*found && (b.sequence!=*event.metadata.sequence.data || b.last_subevent!=event.metadata.subevent_index || b.subevent_count!=event.metadata.subevent_count))
                return {ErrorCode::inconsistent_metadata,"recovery.source_boundary",j};
            auto restored=old;restored.start.scope=b.scope;restored.exhausted=false;
            consume(restored,b.sequence,b.last_subevent,b.subevent_count);next.items[i]=restored;seen=true;break;
        }
        if (!seen) return {ErrorCode::missing_metadata,"recovery.all_stream_boundaries",i};
    }
    if (const auto e=reserve_record()) return e;
    if (const auto e=book_.recover(event,session)) return e;
    journal_.push_back({event,JournalDisposition::recovery,std::nullopt});cursors_=next;
    order_commit(event.metadata,cursors_.items[*found]->start.rank);continuity_error_.reset();return {};
}
Result<ReplaySnapshot> ReplayEngine::depth(std::size_t requested) const noexcept {
    if (needs_recovery()) return Result<ReplaySnapshot>::failure(ErrorCode::recovery_required,"snapshot.continuity");
    auto book=book_.depth(requested);if (!book) return Result<ReplaySnapshot>::failure(book.error.code,book.error.field);
    return Result<ReplaySnapshot>::success({config_.run_id,journal_.size(),std::move(*book.data)});
}
Result<std::pmr::string> ReplayEngine::canonical() const noexcept {
    try {
        std::pmr::string out(resource_);detail::CanonicalWriter w(out);w.raw("gig.replay.v1;");w.token(config_.run_id);
        w.enumeration(config_.ordering);w.enumeration(config_.initial_state);w.number(config_.max_journal_records);
        w.token(config_.session.session);w.number(config_.session.epoch);
        w.available(config_.timestamp_clock,[&](const auto& clock){w.token(clock);});
        w.list(config_.additional_instruments,[&](const auto& r){detail::canonical_rules(w,r);});
        w.list(config_.streams,[&](const auto& s){write_start(w,s);});
        w.number(static_cast<unsigned>(needs_recovery()));
        if (continuity_error_) {w.enumeration(continuity_error_->code);w.token(continuity_error_->field);w.number(static_cast<unsigned>(continuity_error_->index.has_value()));if (continuity_error_->index) w.number(*continuity_error_->index);}
        w.number(static_cast<unsigned>(last_ordinal_.has_value()));if (last_ordinal_) w.number(*last_ordinal_);
        w.number(static_cast<unsigned>(last_key_.has_value()));if (last_key_) {w.number(last_key_->timestamp);w.number(last_key_->rank);w.number(last_key_->sequence);w.number(last_key_->subevent);}
        w.list(cursors_,[&](const auto& c){write_start(w,c.start);w.number(c.expected.value());w.number(c.next_subevent);w.number(c.message_count);
            w.number(static_cast<unsigned>(c.last_sequence.has_value()));if (c.last_sequence) w.number(c.last_sequence->value());w.number(c.last_subevent);w.number(c.last_message_count);w.number(static_cast<unsigned>(c.exhausted));});
        w.number(journal_.size());
        for (const auto& record:journal_) {w.enumeration(record.disposition);detail::canonical_event(w,record.event);w.number(static_cast<unsigned>(record.restart_index.has_value()));
            if (record.restart_index) w.list(restart_plans_[*record.restart_index],[&](const auto& s){write_start(w,s);});}
        const auto book=book_.canonical();if (!book) return Result<std::pmr::string>::failure(book.error.code,book.error.field);
        w.token(std::string_view(*book.data));return Result<std::pmr::string>::success(std::move(out));
    } catch (const std::bad_alloc&) { return Result<std::pmr::string>::failure(ErrorCode::resource_exhausted,"replay.canonical"); }
      catch (const std::length_error&) { return Result<std::pmr::string>::failure(ErrorCode::capacity,"replay.canonical"); }
}
static_assert(std::is_nothrow_copy_constructible_v<JournalEntry>);
static_assert(std::is_nothrow_move_constructible_v<ReplayEngine>);
} // namespace gig
