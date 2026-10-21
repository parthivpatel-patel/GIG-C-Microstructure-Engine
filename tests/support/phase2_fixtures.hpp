#pragma once
#include <string>
#include "fixtures/synthetic/phase1.hpp"
#include "gig/book/order_book.hpp"
namespace gig::fixtures {
template<class T> T take(Result<T> result) {
    if (!result) throw std::runtime_error(std::string("fixture failure: ")+std::string(result.error.field));
    return std::move(*result.data);
}
inline BookSession book_session() { return {text("fixture-session"),0}; }
inline MarketEvent book_event(EventPayload payload,std::uint64_t sequence=0,std::uint64_t stream=1,BookSession session=book_session()) {
    auto m=metadata();m.sequence=Available<SequenceNumber>::known(number<SequenceNumber>(sequence));
    m.scope=Available<StreamScope>::known({number<StreamId>(stream),session.session,session.epoch,SequenceUnit::message});
    m.capture_ordinal=Available<std::uint64_t>::known(sequence);
    m.source_record=Available<Identity>::known(text("record:"+std::to_string(stream)+":"+std::to_string(sequence)));
    m.provenance.generator_seed=Available<std::uint64_t>::known(1729);
    return {m,std::move(payload)};
}
inline AddOrder add(std::uint64_t id,Side side=Side::buy,std::int64_t price=100,std::uint64_t quantity=10) {
    return {number<OrderId>(id),side,number<PriceTicks>(price),number<QuantityLots>(quantity)};
}
inline std::string state(const OrderBook& book) { const auto out=take(book.canonical());return {out.begin(),out.end()}; }
inline void must(Error error) { if (error) throw std::runtime_error(std::string(error.field)); }
inline void seed(OrderBook& book) {
    must(book.apply(book_event(add(1))));must(book.apply(book_event(add(2))));must(book.apply(book_event(add(3,Side::sell,200))));
}
inline MarketEvent recovery_event(std::uint64_t sequence=0,BookSession session=book_session()) {
    Snapshot snap{SnapshotKind::order_level,SnapshotCoverage::complete,0,{},{},{}};
    must(snap.orders.append({add(7,Side::buy,90,20),5}));
    must(snap.orders.append({add(8,Side::buy,90,10),3})); // Deliberately unsorted input FIFO ranks.
    must(snap.boundaries.append({{number<StreamId>(1),session.session,session.epoch,SequenceUnit::message},number<SequenceNumber>(sequence),0,1}));
    return book_event(snap,sequence,1,session);
}
} // namespace gig::fixtures
