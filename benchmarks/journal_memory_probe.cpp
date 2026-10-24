#include <chrono>
#include <charconv>
#include <iostream>
#include <stdexcept>
#include "gig/memory/tracked_resource.hpp"
#include "fixtures/synthetic/replay_events.hpp"
using namespace gig; using namespace gig::fixtures;
int main(int argc,char** argv) {
    try {
        if(argc!=3) throw std::runtime_error("usage: journal_memory_probe records reset_every");
        std::size_t n{},every{};
        for(int i=1;i<3;++i){const std::string_view s(argv[i]);auto& v=i==1?n:every;const auto out=std::from_chars(s.data(),s.data()+s.size(),v);if(out.ec!=std::errc{}||out.ptr!=s.data()+s.size())throw std::runtime_error("invalid integer");}
        if(n==0||n>8192||every>n)throw std::runtime_error("argument out of range");
        TrackedResource memory; std::size_t initial{},live{},peak{},allocations{},resets{};
        std::uint64_t epoch{},seq{};
        const auto start=std::chrono::steady_clock::now();
        std::size_t record_bytes=sizeof(JournalEntry),record_capacity=1,plan_bytes=0,plan_capacity=0;
        {
            auto config=replay_config();config.max_journal_records=n;
            auto e=take(ReplayEngine::create(rules(),config,{},&memory));initial=memory.stats().live_bytes;
            for(std::size_t i=0;i<n;++i){
                const BookSession session{text("phase5-journal"),epoch};
                // First scope uses the declared fixture session; subsequent epochs use the authored reset session.
                const auto current=epoch?session:book_session();
                if(every&&(i+1)%every==0){const BookSession next{text("phase5-journal"),epoch+1};must(e.reset(replay_event(BookReset{ResetReason::manual,epoch+1},seq,i,1,current),restart_plan(1,next)));++epoch;seq=0;++resets;}
                else {must(e.apply(replay_event(SessionEvent{SessionAction::halt,{}},seq,i,1,current)));++seq;}
            }
            if(e.journal_size()!=n||e.book().order_count()!=0||e.needs_recovery())throw std::runtime_error("independent count/state mismatch");
#ifdef GIG_PHASE5_BASELINE
            while(record_capacity<n)record_capacity=std::min(n,record_capacity*2);
#else
            const auto storage=e.journal_storage();record_bytes=storage.record_bytes;record_capacity=storage.record_capacity;plan_bytes=storage.restart_bytes;plan_capacity=storage.restart_capacity;
            if(storage.records!=n||storage.restarts!=resets)throw std::runtime_error("storage accounting mismatch");
#endif
            live=memory.stats().live_bytes;peak=memory.stats().peak_bytes;allocations=memory.stats().allocations;
            if(live-initial!=record_capacity*record_bytes+plan_capacity*plan_bytes)throw std::runtime_error("independent byte ledger mismatch");
        }
        if(memory.stats().live_bytes||memory.stats().live_blocks)throw std::runtime_error("leak");
        const auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-start).count();
        std::cout<<"{\"records\":"<<n<<",\"reset_every\":"<<every<<",\"resets\":"<<resets<<",\"record_bytes\":"<<record_bytes<<",\"record_capacity\":"<<record_capacity<<",\"restart_bytes\":"<<plan_bytes<<",\"restart_capacity\":"<<plan_capacity<<",\"logical_entry_bytes\":"<<sizeof(JournalEntry)<<",\"engine_object_bytes\":"<<sizeof(ReplayEngine)<<",\"snapshot_bytes\":"<<sizeof(Snapshot)<<",\"metadata_bytes\":"<<sizeof(Metadata)<<",\"initial_pmr_bytes\":"<<initial<<",\"live_pmr_bytes\":"<<live<<",\"peak_pmr_bytes\":"<<peak<<",\"allocations\":"<<allocations<<",\"post_destroy_live_bytes\":0,\"elapsed_ns\":"<<ns<<"}\n";
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
