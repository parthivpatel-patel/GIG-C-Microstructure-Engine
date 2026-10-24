#include "memory_stats.hpp"
#include <algorithm>
#include <charconv>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <string_view>
#include <vector>
#if defined(__linux__)
#include <sys/resource.h>
#endif
#include "copy_probe.hpp"
#include "fixtures/synthetic/phase2_workload.hpp"
#include "gig/detail/canonical.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "tests/support/book_reference.hpp"
using namespace gig;using namespace gig::fixtures;
namespace {
using BenchClock=std::chrono::steady_clock;
std::uint64_t argument(const char* text,std::uint64_t max) {
    const std::string_view s(text);std::uint64_t out{};auto result=std::from_chars(s.data(),s.data()+s.size(),out);
    if (result.ec!=std::errc{} || result.ptr!=s.data()+s.size() || out==0 || out>max) throw std::invalid_argument("argument out of range");
    return out;
}
void require(bool condition,const char* label) {if (!condition) throw std::runtime_error(label);}
std::int64_t elapsed(BenchClock::time_point a,BenchClock::time_point b) {
    const auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(b-a).count();require(ns>0,"timer resolution insufficient");return ns;
}
void oracle(const OrderBook& actual,const test::ReferenceBook& reference) {
    require(!actual.check_invariants(),"benchmark invariant failure");
    require(actual.order_count()==reference.orders.size() && actual.remaining()==reference.remaining() && actual.ledger()==reference.ledger,"benchmark reference totals mismatch");
    for (const auto& expected:reference.orders) {
        const auto found=actual.find(number<OrderId>(expected.id));
        require(found && found->order.side==expected.side && found->order.price_ticks.value()==expected.price && found->order.quantity.value()==expected.quantity && found->priority==expected.priority,"benchmark reference order/FIFO mismatch");
    }
    auto snapshot=take(actual.depth(8));auto sorted=reference.sorted();
    for (const auto side:{Side::buy,Side::sell}) {
        std::vector<DepthLevel> levels;
        for (const auto& order:sorted) if (order.side==side) {
            if (!levels.empty() && levels.back().price_ticks.value()==order.price) {
                levels.back().quantity=number<QuantityLots>(levels.back().quantity.value()+order.quantity);++levels.back().order_count;
            } else levels.push_back({number<PriceTicks>(order.price),number<QuantityLots>(order.quantity),1});
        }
        const auto& observed=side==Side::buy?snapshot.bids:snapshot.asks;
        require(observed.size()==std::min(std::size_t{8},levels.size()),"benchmark depth length mismatch");
        for (std::size_t i=0;i<observed.size();++i) require(observed[i]==levels[i],"benchmark independent depth mismatch");
    }
}
void seed_book(OrderBook& b,const Phase2Workload& w) {for (const auto& e:w.adds) must(b.apply(e));}
void preflight(const Phase2Workload& w) {
    require(bool(make_validated(w.copy_snapshot,rules())),"snapshot-copy fixture invalid");
    require(probe_event_copy(w.copy_snapshot)==(w.copy_snapshot.metadata.sequence.data->value() ^ *w.copy_snapshot.metadata.provenance.generator_seed.data ^ static_cast<std::uint64_t>(w.copy_snapshot.payload.index()) ^ static_cast<std::uint64_t>(w.copy_snapshot.metadata.source_record.data->view().size())),"snapshot copy probe mismatch");
    auto book=take(OrderBook::create(rules(),book_session()));test::ReferenceBook reference;
    for (const auto& e:w.adds) {require(reference.apply(e.payload),"reference rejected add fixture");must(book.apply(e));oracle(book,reference);}
    for (const auto& e:w.executions) {require(reference.apply(e.payload),"reference rejected execution fixture");must(book.apply(e));oracle(book,reference);}
    // Fresh full-cancel workload, not cancellation of already-partially-filled fixtures.
    auto cancelled=take(OrderBook::create(rules(),book_session()));test::ReferenceBook cancels;
    for (const auto& e:w.adds) {require(cancels.apply(e.payload),"reference rejected seed");must(cancelled.apply(e));}
    for (const auto& e:w.cancels) {require(cancels.apply(e.payload),"reference rejected cancel fixture");must(cancelled.apply(e));oracle(cancelled,cancels);}
    auto replay=take(ReplayEngine::create(rules(),w.config));test::ReferenceBook replay_reference;
    for (const auto& e:w.replay) {require(replay_reference.apply(e.payload),"reference rejected replay fixture");must(replay.apply(e));oracle(replay.book(),replay_reference);}
    require(replay.journal_size()==w.replay.size() && !replay.needs_recovery(),"benchmark replay continuity mismatch");
    std::vector<MarketEvent> copied(w.adds);require(copied==w.adds,"owned event copy mismatch");
    for (const auto& e:w.adds) require(probe_event_copy(e)==(e.metadata.sequence.data->value() ^ *e.metadata.provenance.generator_seed.data ^ static_cast<std::uint64_t>(e.payload.index()) ^ static_cast<std::uint64_t>(e.metadata.source_record.data->view().size())),"copy probe mismatch");
}
struct Sample {
    std::int64_t ns;
    std::size_t allocations,deallocations,live_before,live_after,peak;
    std::uint64_t checksum;
};
struct Measurements {std::vector<Sample> bulk;std::vector<std::int64_t> latency;};
template<class Operation> Sample timed(std::size_t count,bool per_operation,Operation operation,TrackedResource& resource,std::vector<std::int64_t>& samples) {
    const auto before=resource.stats();std::uint64_t checksum=0;
    // The latency vector is reserved by the driver before this timer starts.
    const auto start=BenchClock::now();
    for (std::size_t i=0;i<count;++i) {
        if (per_operation) {const auto a=BenchClock::now();checksum^=operation(i);const auto b=BenchClock::now();samples.push_back(elapsed(a,b));}
        else checksum^=operation(i);
    }
    const auto end=BenchClock::now();const auto after=resource.stats();
    return {elapsed(start,end),after.allocations-before.allocations,after.deallocations-before.deallocations,before.live_bytes,after.live_bytes,after.peak_bytes,checksum};
}
Sample run_case(std::string_view name,const Phase2Workload& w,bool latency,std::vector<std::int64_t>& times) {
    TrackedResource resource(std::pmr::get_default_resource(),128U*1024U*1024U);
    if (name=="replay") {
        auto replay=take(ReplayEngine::create(rules(),w.config,{},&resource));
        const auto result=timed(w.replay.size(),latency,[&](std::size_t i){must(replay.apply(w.replay[i]));return replay.book().remaining()^static_cast<std::uint64_t>(replay.journal_size());},resource,times);
        require(!replay.needs_recovery() && !replay.book().check_invariants() && replay.journal_size()==w.replay.size(),"timed replay result mismatch");
        std::uint64_t expected=0;for (std::size_t i=0;i<w.adds.size();++i) if (i%2!=0) expected+=std::get<AddOrder>(w.adds[i].payload).quantity.value()-1;
        require(replay.book().remaining()==expected,"timed replay conservation mismatch");return result;
    }
    if (name=="event_copy_add" || name=="event_copy_snapshot" || name=="payload_copy") {
        if (name=="payload_copy") return timed(w.adds.size(),latency,[&](std::size_t i){return probe_payload_copy(std::get<AddOrder>(w.adds[i].payload));},resource,times);
        return timed(w.adds.size(),latency,[&](std::size_t i){return probe_event_copy(name=="event_copy_add"?w.adds[i]:w.copy_snapshot);},resource,times);
    }
    auto book=take(OrderBook::create(rules(),book_session(),{},&resource));
    if (name!="add") seed_book(book,w); // Setup excluded from operation timing/allocation delta.
    if (name=="depth_snapshot") return timed(w.adds.size(),latency,[&](std::size_t){auto d=take(book.depth(8));std::uint64_t sum=0;for (const auto& l:d.bids) sum+=l.quantity.value();for (const auto& l:d.asks) sum+=l.quantity.value();return sum;},resource,times);
    const auto& events=name=="add"?w.adds:(name=="cancel"?w.cancels:w.executions);
    const auto result=timed(events.size(),latency,[&](std::size_t i){must(book.apply(events[i]));return book.remaining()^static_cast<std::uint64_t>(book.order_count());},resource,times);
    require(!book.check_invariants(),"timed mutation invariants");
    if (name=="add") require(book.order_count()==w.adds.size(),"timed add count");
    if (name=="cancel") require(book.order_count()==0 && book.remaining()==0,"timed cancel count");
    if (name=="execution") {std::uint64_t expected=0;for (const auto& e:w.adds) expected+=std::get<AddOrder>(e.payload).quantity.value()-1;require(book.remaining()==expected && book.order_count()==w.adds.size(),"timed identified-execution result");}
    return result;
}
void write_file(const std::filesystem::path& path,std::string_view bytes) {
    require(!std::filesystem::exists(path),"refusing to overwrite benchmark artifact");std::ofstream out(path,std::ios::binary);out.exceptions(std::ios::badbit|std::ios::failbit);out.write(bytes.data(),static_cast<std::streamsize>(bytes.size()));
}
void artifacts(const Phase2Workload& w,const std::filesystem::path& directory) {
    std::pmr::string data;detail::CanonicalWriter writer(data);writer.raw("gig.phase2.workload.v2;");writer.number(w.seed);
    for (const auto* list:{&w.adds,&w.cancels,&w.executions,&w.replay}) {writer.number(list->size());for (const auto& e:*list) detail::canonical_event(writer,e);}
    detail::canonical_event(writer,w.copy_snapshot);write_file(directory/"workload.canonical",data);
    auto replay=take(ReplayEngine::create(rules(),w.config));auto batch=replay.run(w.replay);require(bool(batch),"artifact replay failed");
    auto canonical=take(replay.canonical());write_file(directory/"replay.canonical",canonical);
}
void emit_stats(const Sample& s) {
    std::cout << "{\"elapsed_ns\":" << s.ns << ",\"allocations\":" << s.allocations << ",\"deallocations\":" << s.deallocations
              << ",\"pmr_live_bytes_before\":" << s.live_before << ",\"pmr_live_bytes_after\":" << s.live_after << ",\"pmr_peak_bytes_including_setup\":" << s.peak << ",\"checksum\":" << s.checksum << '}';
}
}
int main(int argc,char** argv) {
    try {
        if (argc!=6) throw std::invalid_argument("usage: orders repetitions warmup seed output-directory");
        const auto count=static_cast<std::size_t>(argument(argv[1],2048));
        const auto repeats=argument(argv[2],30),warmup=argument(argv[3],10),seed=argument(argv[4],UINT64_MAX);
        const std::filesystem::path directory(argv[5]);require(std::filesystem::is_directory(directory),"artifact directory must exist");
        auto w=phase2_workload(count,seed);preflight(w);artifacts(w,directory);
        std::vector<std::int64_t> timer;
        for (int i=0;i<10000;++i) {const auto a=BenchClock::now();const auto b=BenchClock::now();timer.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(b-a).count());}
        const std::array<std::string_view,8> names{"add","cancel","execution","depth_snapshot","replay","event_copy_add","event_copy_snapshot","payload_copy"};
        std::cout << "{\"phase2_correctness_validated\":true,\"workload_version\":2,\"orders\":" << count << ",\"seed\":" << seed << ",\"warmup\":" << warmup << ",\"repetitions\":" << repeats << ",\"threads\":1,"
                  << "\"sizeof_market_event\":" << sizeof(MarketEvent) << ",\"sizeof_metadata\":" << sizeof(Metadata) << ",\"sizeof_add_order\":" << sizeof(AddOrder) << ",\"sizeof_journal_entry\":" << sizeof(JournalEntry) << ",\"physical_journal_record_bytes\":" << ReplayEngine::journal_record_bytes()
                  << ",\"sizeof_order_book\":" << sizeof(OrderBook) << ",\"sizeof_replay_engine\":" << sizeof(ReplayEngine)
                  << ",\"input_event_storage_bytes\":" << (w.adds.capacity()+w.cancels.capacity()+w.executions.capacity()+w.replay.capacity())*sizeof(MarketEvent)
                  << ",\"payload_storage_control_bytes\":" << count*sizeof(AddOrder) << ",\"standard_library\":\""
#if defined(__GLIBCXX__)
                  << "libstdc++-" << __GLIBCXX__
#elif defined(_LIBCPP_VERSION)
                  << "libc++-" << _LIBCPP_VERSION
#else
                  << "unknown"
#endif
                  << "\",\"measurements\":{";
        for (std::size_t k=0;k<names.size();++k) {
            const auto name=names[k];const auto operations=name=="replay"?w.replay.size():count;
            Measurements m;m.bulk.reserve(static_cast<std::size_t>(repeats));m.latency.reserve(operations*static_cast<std::size_t>(repeats));
            for (std::uint64_t r=0;r<warmup;++r) {std::vector<std::int64_t> unused;static_cast<void>(run_case(name,w,false,unused));}
            for (std::uint64_t r=0;r<repeats;++r) {m.bulk.push_back(run_case(name,w,false,m.latency));static_cast<void>(run_case(name,w,true,m.latency));}
            if (k!=0) std::cout << ',';
            std::cout << '"' << name << "\":{\"operations_per_repetition\":" << operations << ",\"bulk_samples\":[";
            for (std::size_t i=0;i<m.bulk.size();++i) {if (i!=0) std::cout << ',';emit_stats(m.bulk[i]);}
            std::cout << "],\"service_time_ns\":[";for (std::size_t i=0;i<m.latency.size();++i) {if (i!=0) std::cout << ',';std::cout << m.latency[i];}std::cout << "]}";
        }
        std::cout << "},\"timer_pair_ns\":[";for (std::size_t i=0;i<timer.size();++i) {if (i!=0) std::cout << ',';std::cout << timer[i];}
        std::cout << "],\"process_peak_rss_bytes\":";
#if defined(__linux__)
        struct rusage usage{};if (getrusage(RUSAGE_SELF,&usage)==0) std::cout << static_cast<std::uint64_t>(usage.ru_maxrss)*1024U;else std::cout << "null";
#else
        std::cout << "null";
#endif
        gig::benchmark_memory::emit_native_peak_rss();
        std::cout << "}\n";return 0;
    } catch (const std::exception& error) {std::cerr << error.what() << '\n';return 1;}
}
