#include <iostream>
#include <sstream>
#include "gig/analytics/book_metrics.hpp"
#include "fixtures/synthetic/book_events.hpp"
using namespace gig;using namespace gig::analytics;using namespace gig::fixtures;
namespace {
void check(bool ok) {if (!ok) throw std::runtime_error("book metrics assertion");}
ReplaySnapshot frame(std::int64_t bid,std::int64_t ask,std::uint64_t bq,std::uint64_t aq) {
    auto r=rules();r.minimum_price=number<PriceTicks>(INT64_MIN);
    DepthSnapshot b(r,book_session(),17,2,std::pmr::get_default_resource());
    if (bq) b.bids.push_back({number<PriceTicks>(bid),number<QuantityLots>(bq),1});
    if (aq) b.asks.push_back({number<PriceTicks>(ask),number<QuantityLots>(aq),1});
    return {text("analytics-fixture-run"),23,std::move(b)};
}
void emit(const BookMetrics& m) {for (std::size_t i=0;i<9;++i) {if (i) std::cout << ' ';const auto& x=m.get(static_cast<BookMetric>(i));std::cout << (x.value?x.value->str():"NA");}std::cout << '\n';}
}
int main(int argc,char** argv) {
    try {
        if (argc==2 && std::string_view(argv[1])=="reference") {
            std::int64_t bid{},ask{};std::uint64_t bq{},aq{};
            while (std::cin>>bid>>ask>>bq>>aq) {auto f=frame(bid,ask,bq,aq);auto m=calculate(f,1);if (!m) std::cout << "error\n";else emit(*m.data);}return 0;
        }
        auto f=frame(100,101,30,10);auto m=take(calculate(f,1));
        check(m.get(BookMetric::midpoint).value->str()=="201/2");check(m.get(BookMetric::microprice).value->str()=="403/4");
        check(m.get(BookMetric::top_imbalance).value->str()=="1/2");check(m.source().revision==17 && m.source().journal_prefix==23 && m.source().run_id==f.run_id);
        check(!calculate(f,0) && !calculate(f,3));check(!calculate(f,2).data->get(BookMetric::depth_imbalance).value);
        auto empty=frame(0,0,0,0);auto e=take(calculate(empty,1));check(e.get(BookMetric::midpoint).unavailable==Unavailable::empty_book && e.get(BookMetric::bid_depth).value->str()=="0/1");
        auto one=frame(100,0,10,0);check(take(calculate(one,1)).get(BookMetric::midpoint).unavailable==Unavailable::one_sided);
        auto locked=frame(100,100,10,20);check(take(calculate(locked,1)).get(BookMetric::spread).value->str()=="0/1");
        f.book.bids.push_back(f.book.bids.front());check(!calculate(f,1));f.book.bids.pop_back();
        f.book.bids.front().quantity=number<QuantityLots>(0);check(!calculate(f,1));
        auto extreme=frame(INT64_MIN,INT64_MAX,UINT64_MAX-1,1);check(bool(calculate(extreme,1)));
        extreme.book.asks.front().quantity=number<QuantityLots>(2);check(!calculate(extreme,1));
        auto book=take(OrderBook::create(rules(),book_session()));seed(book);auto before=state(book);auto snap=take(book.depth(2));
        auto result=calculate({text("nonmutating-run"),3,std::move(snap)},1);check(bool(result) && state(book)==before);
        bool overflow=false;try {static_cast<void>(exact::Fraction::whole(exact::maximum)+exact::Fraction(1));}catch(const exact::ArithmeticFailure&){overflow=true;}check(overflow);
        bool zero=false;try {static_cast<void>(exact::Fraction(1)/exact::Fraction(0));}catch(const exact::ArithmeticFailure&){zero=true;}check(zero);
        std::cout << "PASS: hand calculations, missing states, malformed snapshots, exact boundaries, provenance and nonmutation\n";
    } catch (const std::exception& e) {std::cerr << e.what() << '\n';return 1;}
}
