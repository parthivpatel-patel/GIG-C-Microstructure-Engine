#include <iostream>
#include <string_view>
#include "gig/memory/tracked_resource.hpp"
#include "fixtures/synthetic/book_events.hpp"
#include "tests/support/book_reference.hpp"
using namespace gig;using namespace gig::fixtures;
namespace {
std::size_t checks=0,failures=0;
void check(bool ok,const char* label) { ++checks;if (!ok) { ++failures;std::cerr << "FAIL: " << label << '\n'; } }
void apply(OrderBook& book,const MarketEvent& event) { must(book.apply(event));check(!book.check_invariants(),"all invariants after mutation"); }
void reject(OrderBook& book,const MarketEvent& event,ErrorCode code) {
    const auto before=state(book);auto error=book.apply(event);
    check(error.code==code,"expected mutation error");check(state(book)==before,"strong input-failure rollback");check(!book.check_invariants(),"failed-mutation invariants");
}
void compare(const OrderBook& book,const test::ReferenceBook& ref) {
    check(book.order_count()==ref.orders.size() && book.remaining()==ref.remaining(),"reference book totals");
    check(book.ledger()==ref.ledger,"reference ledger");
    for (const auto& expected:ref.orders) {
        auto actual=book.find(number<OrderId>(expected.id));
        check(actual && actual->order.side==expected.side && actual->order.price_ticks.value()==expected.price &&
              actual->order.quantity.value()==expected.quantity && actual->priority==expected.priority,"reference order/FIFO rank");
    }
    auto depth=take(book.depth(64));auto sorted=ref.sorted();
    std::vector<DepthLevel> bids,asks;
    for (const auto& x:sorted) {
        auto& levels=x.side==Side::buy?bids:asks;
        if (!levels.empty() && levels.back().price_ticks.value()==x.price) {
            levels.back().quantity=number<QuantityLots>(levels.back().quantity.value()+x.quantity);++levels.back().order_count;
        } else levels.push_back({number<PriceTicks>(x.price),number<QuantityLots>(x.quantity),1});
    }
    check(std::equal(bids.begin(),bids.end(),depth.bids.begin(),depth.bids.end()),"reference bid depth");
    check(std::equal(asks.begin(),asks.end(),depth.asks.begin(),depth.asks.end()),"reference ask depth");
    check(!book.check_invariants(),"reference invariant scan");
}
std::uint64_t rng(std::uint64_t& x) { x^=x<<13U;x^=x>>7U;x^=x<<17U;return x; }
}
int main(int argc,char** argv) {
    if (argc!=2) return 2;
    try {
        const std::string_view group{argv[1]};
        TrackedResource resource;
        auto book=take(OrderBook::create(rules(),book_session(),{},&resource));
        if (group=="basic") {
            check(!book.best_bid() && !book.best_ask(),"empty sides");auto d=take(book.depth(1));check(d.bids.empty() && d.asks.empty(),"empty snapshot");
            apply(book,book_event(add(1)));check(book.best_bid()->quantity.value()==10 && !book.best_ask(),"one-sided best");
            apply(book,book_event(add(2)));apply(book,book_event(add(3,Side::buy,101,5)));apply(book,book_event(add(4,Side::sell,200,7)));
            check(book.remaining()==32 && book.order_count()==4,"book aggregate");d=take(book.depth(1));check(d.bids[0].price_ticks.value()==101 && d.bid_truncated && !d.ask_truncated,"bounded ordered depth");
            reject(book,book_event(add(1)),ErrorCode::duplicate);
            reject(book,book_event(add(5,Side::buy,201)),ErrorCode::crossed_quote);
            apply(book,book_event(add(6,Side::buy,200)));check(book.find(number<OrderId>(6)).has_value(),"locked book allowed without matching");
            check(book.order_count()==5,"no automatic matching");
            auto wrong=book_event(add(7),0,1,{text("different-session"),0});reject(book,wrong,ErrorCode::session_boundary);
            wrong=book_event(add(7));wrong.metadata.instrument=Available<InstrumentId>::known(number<InstrumentId>(2));reject(book,wrong,ErrorCode::identity_mismatch);
        } else if (group=="cancel_execute") {
            seed(book);const auto priority=book.find(number<OrderId>(2))->priority;
            apply(book,book_event(CancelOrder{number<OrderId>(1),number<QuantityLots>(3)}));check(book.find(number<OrderId>(1))->order.quantity.value()==7,"partial cancel");
            apply(book,book_event(Trade{BookExecution{number<OrderId>(2),Side::buy,number<PriceTicks>(100),number<QuantityLots>(4)}}));
            check(book.find(number<OrderId>(2))->priority==priority && book.find(number<OrderId>(1)).has_value(),"identified non-head fill preserves FIFO");
            const auto quantities=book.remaining();apply(book,book_event(Trade{TradePrint{number<PriceTicks>(100),number<QuantityLots>(4),{}}}));
            check(book.remaining()==quantities,"print-only trade does not decrement");
            reject(book,book_event(CancelOrder{number<OrderId>(1),number<QuantityLots>(8)}),ErrorCode::underflow);
            reject(book,book_event(CancelOrder{number<OrderId>(99),CancelAll{}}),ErrorCode::not_found);
            reject(book,book_event(Trade{BookExecution{number<OrderId>(2),Side::sell,number<PriceTicks>(100),number<QuantityLots>(1)}}),ErrorCode::identity_mismatch);
            apply(book,book_event(CancelOrder{number<OrderId>(1),CancelAll{}}));
            apply(book,book_event(Trade{BookExecution{number<OrderId>(2),Side::buy,number<PriceTicks>(100),number<QuantityLots>(6)}}));
            check(!book.best_bid() && book.best_ask().has_value(),"empty bid level removed");check(book.ledger().cancelled==10 && book.ledger().executed==10,"quantity categories");
        } else if (group=="replace") {
            seed(book);const auto priority=book.find(number<OrderId>(1))->priority;
            apply(book,book_event(ReplaceOrder{number<OrderId>(1),number<OrderId>(4),Side::buy,number<PriceTicks>(100),number<QuantityLots>(5),ReplacePriority::retain_only_same_price_reduction}));
            check(!book.find(number<OrderId>(1)) && book.find(number<OrderId>(4))->priority==priority,"retained-priority ID change");
            reject(book,book_event(ReplaceOrder{number<OrderId>(4),number<OrderId>(4),Side::buy,number<PriceTicks>(100),number<QuantityLots>(6),ReplacePriority::retain_only_same_price_reduction}),ErrorCode::priority_violation);
            reject(book,book_event(ReplaceOrder{number<OrderId>(4),number<OrderId>(2),Side::buy,number<PriceTicks>(100),number<QuantityLots>(5),ReplacePriority::lose}),ErrorCode::duplicate);
            apply(book,book_event(ReplaceOrder{number<OrderId>(4),number<OrderId>(4),Side::buy,number<PriceTicks>(100),number<QuantityLots>(20),ReplacePriority::lose}));
            check(book.find(number<OrderId>(4))->priority>book.find(number<OrderId>(2))->priority,"increase loses priority");
            apply(book,book_event(ReplaceOrder{number<OrderId>(4),number<OrderId>(5),Side::buy,number<PriceTicks>(101),number<QuantityLots>(4),ReplacePriority::lose}));
            reject(book,book_event(ReplaceOrder{number<OrderId>(5),number<OrderId>(5),Side::sell,number<PriceTicks>(99),number<QuantityLots>(4),ReplacePriority::lose}),ErrorCode::crossed_quote);
        } else if (group=="boundaries") {
            apply(book,book_event(add(1,Side::buy,100,UINT64_MAX)));
            reject(book,book_event(add(2,Side::buy,100,1)),ErrorCode::overflow);
            apply(book,book_event(CancelOrder{number<OrderId>(1),number<QuantityLots>(1)}));
            reject(book,book_event(add(2,Side::buy,100,1)),ErrorCode::overflow); // Lifetime ledger cannot wrap.
            auto limited=take(OrderBook::create(rules(),book_session(),{1,1,1},&resource));apply(limited,book_event(add(1)));
            reject(limited,book_event(add(2)),ErrorCode::capacity);
            apply(limited,book_event(ReplaceOrder{number<OrderId>(1),number<OrderId>(2),Side::buy,number<PriceTicks>(101),number<QuantityLots>(10),ReplacePriority::lose}));
            check(limited.order_count()==1 && limited.best_bid()->price_ticks.value()==101,"replace can reuse level capacity");
            check(!limited.depth(0) && !limited.depth(2),"depth bounds");
            auto next=BookSession{text("next-session"),1};must(limited.apply(book_event(BookReset{ResetReason::session_start,1}),next));
            check(limited.remaining()==0 && limited.session()==next,"explicit session reset");
            apply(limited,book_event(add(1),0,1,next));check(!limited.check_invariants(),"ID reuse only in reset scope");
        } else if (group=="recovery") {
            seed(book);const auto before=state(book);auto e=recovery_event();
            reject(book,e,ErrorCode::unsupported);
            must(book.recover(e,book_session()));check(!book.check_invariants(),"recovery invariants");
            check(book.order_count()==2 && book.remaining()==30 && !book.find(number<OrderId>(1)),"snapshot replaces, not merges");
            check(book.find(number<OrderId>(8))->priority<book.find(number<OrderId>(7))->priority,"recovered FIFO by explicit ranks");
            check(book.ledger().discarded==30 && book.ledger().recovered==30,"recovery conservation");
            const auto recovered=state(book);auto s=std::get<Snapshot>(e.payload);s.kind=SnapshotKind::aggregated;s.orders={};e.payload=s;
            check(book.recover(e,book_session()).code==ErrorCode::unsupported && state(book)==recovered,"aggregate recovery forbidden");
            e=recovery_event();std::get<Snapshot>(e.payload).orders.items[0]->priority_index=UINT64_MAX;
            check(book.recover(e,book_session()).code==ErrorCode::overflow && state(book)==recovered,"priority wrap recovery rollback");
            check(before!=recovered,"canonical captures state transition");
        } else if (group=="allocations") {
            std::size_t failed_sites=0;
            for (int scenario=0;scenario<12;++scenario) {
                bool success=false;
                for (std::size_t site=0;site<128;++site) {
                    TrackedResource r;
                    {
                        auto b=take(OrderBook::create(rules(),book_session(),{},&r));seed(b);
                        if (scenario==10) { must(b.apply(book_event(add(4))));must(b.apply(book_event(add(5)))); }
                        const auto before=state(b);const auto previous_metadata=b.last_metadata();const auto live=r.stats().live_bytes;
                        r.fail_after(site);Error error;
                        switch (scenario) {
                        case 0:error=b.apply(book_event(add(4,Side::buy,101)));break;
                        case 1:error=b.apply(book_event(add(4)));break;
                        case 2:error=b.apply(book_event(ReplaceOrder{number<OrderId>(1),number<OrderId>(4),Side::buy,number<PriceTicks>(101),number<QuantityLots>(20),ReplacePriority::lose}));break;
                        case 3:error=b.apply(book_event(ReplaceOrder{number<OrderId>(1),number<OrderId>(1),Side::buy,number<PriceTicks>(100),number<QuantityLots>(20),ReplacePriority::lose}));break;
                        case 4:error=b.apply(book_event(ReplaceOrder{number<OrderId>(1),number<OrderId>(4),Side::buy,number<PriceTicks>(100),number<QuantityLots>(5),ReplacePriority::retain_only_same_price_reduction}));break;
                        case 5:error=b.apply(book_event(CancelOrder{number<OrderId>(1),CancelAll{}}));break;
                        case 6:error=b.apply(book_event(Trade{BookExecution{number<OrderId>(1),Side::buy,number<PriceTicks>(100),number<QuantityLots>(4)}}));break;
                        case 7:error=b.apply(book_event(BookReset{ResetReason::manual,1}));break;
                        case 8:error=b.recover(recovery_event(),book_session());break;
                        case 9:{auto d=b.depth(10);error=d.error;break;}
                        case 10:error=b.apply(book_event(add(6,Side::buy,102)));break;
                        default:{auto out=b.canonical();error=out.error;break;}
                        }
                        r.disable_failure();check(!b.check_invariants(),"fault injection invariants");
                        if (error) {
                            check(error.code==ErrorCode::resource_exhausted,"allocation failure classified");
                            check(state(b)==before && b.last_metadata()==previous_metadata && r.stats().live_bytes==live,"all allocation failures preserve state and release staging");++failed_sites;
                        } else success=true;
                    }
                    check(r.stats().live_bytes==0 && r.stats().live_blocks==0,"all tracked allocations released");
                    if (success) break;
                }
                check(success,"every allocation site exhausted to eventual success");
            }
            TrackedResource budget(std::pmr::get_default_resource(),1);check(!OrderBook::create(rules(),book_session(),{},&budget),"memory budget failure");
            TrackedResource construction;construction.fail_after(0);check(!OrderBook::create(rules(),book_session(),{},&construction),"construction failure injection");
            std::cout << "allocation failure sites exercised=" << failed_sites << '\n';
        } else if (group=="reference") {
            for (const auto seed_value:{1ULL,42ULL,1729ULL,999ULL}) {
                auto b=take(OrderBook::create(rules(),book_session()));test::ReferenceBook reference;std::uint64_t state_rng=seed_value,next_id=1;
                for (int step=0;step<5000;++step) {
                    EventPayload payload=add(next_id);
                    const auto choice=rng(state_rng)%5;
                    if (reference.orders.empty() || (choice==0 && reference.orders.size()<64)) {
                        const auto side=rng(state_rng)%2==0?Side::buy:Side::sell;
                        payload=add(next_id++,side,static_cast<std::int64_t>((side==Side::buy?100:200)+rng(state_rng)%8),rng(state_rng)%50+1);
                    } else {
                        const auto item=reference.orders[static_cast<std::size_t>(rng(state_rng)%reference.orders.size())];
                        const auto amount=rng(state_rng)%item.quantity+1;
                        if (choice==1) payload=CancelOrder{number<OrderId>(item.id),number<QuantityLots>(amount)};
                        else if (choice==2) payload=Trade{BookExecution{number<OrderId>(item.id),item.side,number<PriceTicks>(item.price),number<QuantityLots>(amount)}};
                        else {
                            const bool retain=choice==3;
                            payload=ReplaceOrder{number<OrderId>(item.id),number<OrderId>(item.id),item.side,number<PriceTicks>(retain?item.price:static_cast<std::int64_t>((item.side==Side::buy?100:200)+rng(state_rng)%8)),number<QuantityLots>(retain?amount:rng(state_rng)%50+1),retain?ReplacePriority::retain_only_same_price_reduction:ReplacePriority::lose};
                        }
                    }
                    check(reference.apply(payload),"reference generated valid operation");
                    auto input=book_event(payload);input.metadata.provenance.generator_seed=Available<std::uint64_t>::known(seed_value);
                    input.metadata.provenance.lineage.items[0]->operation=text("phase2-random-operations");
                    must(b.apply(input));check(b.last_metadata()->provenance.generator_seed.data==seed_value,"actual randomized seed preserved");compare(b,reference);
                }
            }
            std::cout << "reference operations=20000, seeds=1,42,1729,999\n";
        } else return 2;
    } catch (const std::exception& e) { std::cerr << "unexpected test exception: " << e.what() << '\n';return 1; }
    std::cout << argv[1] << ": " << checks << " checks, " << failures << " failures\n";
    return failures==0?0:1;
}
