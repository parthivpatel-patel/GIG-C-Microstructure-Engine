#include "gig/itch/streaming.hpp"
#include "gig/itch/sha256.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "itch_gzip_fixture.hpp"
#include <charconv>
#include <iostream>
#include <string>

namespace {
using namespace gig::itch;
using namespace gig::itch::test;
constexpr std::size_t budget=128U*1024U*1024U;
std::string hex(std::span<const std::byte> bytes){constexpr char digits[]="0123456789abcdef";std::string s;for(auto b:bytes){const auto x=std::to_integer<unsigned>(b);s+=digits[x>>4U];s+=digits[x&15U];}return s;}
struct Fixture{std::vector<std::vector<std::byte>> records;std::vector<std::byte> raw,gzip;StreamingConfig config;std::size_t pause;};
Fixture fixture(std::size_t n){
    Fixture f{{},{},{},StreamingConfig{config(),{}, {},{}},0};f.records={system(),directory(),directory(2,"TWO     ")};
    for(std::size_t i=0;i<n;++i)for(std::uint16_t b=1;b<=2;++b)f.records.push_back(add(i*2+b,1000,b==1?100:200,b,b==1?'B':'S'));
    // Exactly1024 native records per book when n=128. Quantity remains positive.
    for(unsigned round=0;round<7;++round)for(std::size_t i=0;i<n;++i)for(std::uint16_t b=1;b<=2;++b)f.records.push_back(reduce('X',i*2+b,1,0,b));
    f.pause=f.records.size();for(char c:std::string_view("SQMEC"))f.records.push_back(system(c));
    f.raw=framed_records(f.records);f.gzip=stored_gzip(f.raw);
    auto c=config();c.context_policy=ContextPolicy{};c.max_source_records=4096;
    for(auto& b:c.bindings){b->limits={128,128,16};b->max_journal_records=1024;}
    const auto raw_hash=sha256(f.raw);c.source.provenance.sha256=raw_hash;c.initialization.fixture_sha256=number<gig::Digest>(hex(raw_hash));
    f.config=StreamingConfig{c,{}, {},sha256(f.gzip)};
    return f;
}
struct State{ReconstructionSummary source;ContextSummary context;std::array<std::uint64_t,2> revision,remaining;std::array<std::size_t,2> journal,orders;std::array<gig::QuantityLedger,2> ledger;bool operator==(const State&)const=default;};
State state(const StreamingReconstructor& stream){const auto& r=stream.reconstruction();State s{r.summary(),r.context().summary(),{},{},{},{},{}};for(std::size_t i=0;i<2;++i){const auto* e=r.engine(i);s.revision[i]=e->book().revision();s.remaining[i]=e->book().remaining();s.journal[i]=e->journal_size();s.orders[i]=e->book().order_count();s.ledger[i]=e->book().ledger();}return s;}
StreamingReconstructor make(const StreamingConfig& c,gig::TrackedResource& memory){auto out=StreamingReconstructor::create(c,&memory);check(bool(out),"profile creation");return std::move(*out.data);}
StreamingFeed feed(const Fixture& f,StreamingReconstructor& stream,std::size_t& offset,std::size_t chunk){StreamingFeed step;do{const auto count=std::min(chunk,f.gzip.size()-offset);step=stream.feed(std::span<const std::byte>(f.gzip).subspan(offset,count));offset+=step.consumed;if(step.error||step.paused||offset==f.gzip.size())return step;check(step.consumed>0,"feed progress");}while(true);}
void check_books(const StreamingReconstructor& stream,std::size_t n){const auto& r=stream.reconstruction();check(r.summary().native_committed==n*16,"native record oracle");for(std::size_t b=0;b<2;++b){const auto* e=r.engine(b);const auto& book=e->book();check(!book.check_invariants()&&book.order_count()==n&&book.remaining()==n*993&&book.revision()==n*8&&e->journal_size()==n*8,"book arithmetic oracle");check(book.ledger().added==n*1000&&book.ledger().cancelled==n*7&&book.ledger().total_in==n*1000&&book.ledger().total_out==n*7,"ledger oracle");for(std::size_t i=0;i<n;++i){const auto order=book.find(number<gig::OrderId>(i*2+b+1));check(order.has_value()&&order->order.quantity.value()==993&&order->priority==i,"identity quantity FIFO oracle");}}}
std::size_t allocation_checks(StreamingReconstructor& stream,gig::TrackedResource& memory){const auto old=state(stream);const auto bytes=memory.stats().live_bytes;std::size_t failures=0;const auto code=number<gig::Digest>(std::string(64,'1'));
    for(std::size_t fail=0;fail<256;++fail){memory.fail_after(fail);bool success=false;{auto c=stream.checkpoint(code);success=bool(c);if(!success){check(c.error.code==gig::ErrorCode::resource_exhausted,"checkpoint allocation error");++failures;}}memory.disable_failure();check(state(stream)==old&&memory.stats().live_bytes==bytes,"checkpoint failure atomicity");if(success)break;check(fail!=255,"checkpoint sweep bounded");}
    memory.fail_after(0);{auto d=stream.reconstruction().engine(0)->depth(16);check(!d&&d.error.code==gig::ErrorCode::resource_exhausted,"depth reached allocation failure");++failures;}memory.disable_failure();check(state(stream)==old&&memory.stats().live_bytes==bytes,"depth failure atomicity");return failures;
}
struct Stop{std::uint64_t framed{},accepted{},native{};std::size_t peak{};std::string field;};
Stop cap_stop(const Fixture& f,std::size_t cap,bool journal){gig::TrackedResource memory(std::pmr::get_default_resource(),cap);Stop out;{auto c=f.config;if(journal)for(auto& b:c.reconstruction.bindings)b->max_journal_records=1023;auto stream=make(c,memory);std::size_t offset=0;const auto step=feed(f,stream,offset,17);const auto summary=stream.finish();check(bool(step.error)&&bool(summary.error)&&!summary.publication_eligible&&!summary.source_complete,"cap explicit failure");const auto& r=stream.reconstruction();check(r.summary().context_committed==summary.accepted_records&&r.summary().native_committed==summary.native_records&&r.receipts().size()==summary.accepted_records,"cap accounting");for(std::size_t b=0;b<2;++b)check(!r.engine(b)->book().check_invariants()&&r.engine(b)->journal_size()==r.summary().native_counts[b],"cap native context consistency");out={summary.source_records,summary.accepted_records,summary.native_records,memory.stats().peak_bytes,std::string(summary.error.reconstruction.native_error.field)};}check(memory.stats().live_bytes==0,"cap cleanup");return out;}
}
int main(int argc,char** argv){try{
    std::size_t n=128;if(argc==2){const std::string_view x(argv[1]);const auto r=std::from_chars(x.data(),x.data()+x.size(),n);check(r.ec==std::errc{}&&r.ptr==x.data()+x.size()&&n==128,"only declared128-order profile supported");}check(argc<=2,"arguments");
    const auto f=fixture(n);gig::TrackedResource memory(std::pmr::get_default_resource(),budget);std::size_t first_peak=0,first_live=0,query_peak=0,query_live=0,coexist_peak=0,export_bytes=0,failures=0,allocations=0;const auto code=number<gig::Digest>(std::string(64,'1'));
    {
        auto original=make(f.config,memory);check(!original.pause_after(f.pause),"pause boundary");std::size_t a=0;check(feed(f,original,a,17).paused,"original paused");check_books(original,n);first_peak=memory.stats().peak_bytes;first_live=memory.stats().live_bytes;
        const auto baseline=state(original);{const auto x=original.reconstruction().engine(0)->canonical();const auto y=original.reconstruction().engine(1)->canonical();const auto depth=original.reconstruction().engine(0)->depth(16);check(bool(x)&&bool(y)&&bool(depth),"coexisting exports");export_bytes=x.data->size()+y.data->size();query_peak=memory.stats().peak_bytes;query_live=memory.stats().live_bytes;check(state(original)==baseline,"query nonmutation");}
        failures=allocation_checks(original,memory);check_books(original,n);
        auto checkpoint=original.checkpoint(code);check(bool(checkpoint),"checkpoint");
        auto restarted=make(f.config,memory);check(!restarted.pause_after(f.pause),"restart pause");std::size_t b=0;check(feed(f,restarted,b,65536).paused,"restart paused");check(!restarted.verify_checkpoint(*checkpoint.data,code),"restart descriptor equivalence");check_books(restarted,n);coexist_peak=memory.stats().peak_bytes;
        check(!original.resume()&&!restarted.resume(),"resume");check(!feed(f,original,a,17).error&&!feed(f,restarted,b,65536).error,"completion feed");const auto left=original.finish(),right=restarted.finish();check(left.publication_eligible&&right.publication_eligible&&left.accepted_prefix_sha256==right.accepted_prefix_sha256,"full restart publication");check(state(original)==state(restarted),"final semantic equivalence");check_books(original,n);allocations=memory.stats().allocations;
    }
    check(memory.stats().live_bytes==0&&memory.stats().live_blocks==0,"all profile storage released");
    const auto reduced=cap_stop(f,16U*1024U*1024U,false);check(reduced.peak<=16U*1024U*1024U,"PMR cap");
    Stop journal;if(n==128){journal=cap_stop(f,budget,true);check(journal.accepted==2049&&journal.native==2046&&journal.field=="journal.records","journal limit exact prefix");}
    gig::TrackedResource empty(std::pmr::get_default_resource(),0);check(!StreamingReconstructor::create(f.config,&empty)&&empty.stats().live_bytes==0,"zero-budget creation failure");
    std::cout<<"{\"schema\":\"gig.synthetic_profile_probe.v1\",\"orders_per_symbol\":"<<n<<",\"books\":2,\"records\":"<<f.records.size()<<",\"native_records\":"<<n*16<<",\"journal_records_per_book\":"<<n*8<<",\"journal_entry_bytes\":"<<sizeof(gig::JournalEntry)<<",\"journal_element_bytes\":"<<n*16*sizeof(gig::JournalEntry)<<",\"remaining_per_book\":"<<n*993<<",\"max_orders_per_book\":128,\"journal_limit_per_book\":1024,\"context_lifetime_limit\":"<<f.config.reconstruction.context_policy.max_lifetime_orders<<",\"source_limit\":4096,\"receipt_budget_bytes\":2097152,\"pmr_budget_bytes\":"<<budget<<",\"first_pipeline_peak_pmr\":"<<first_peak<<",\"first_pipeline_live_pmr\":"<<first_live<<",\"coexisting_query_live_pmr\":"<<query_live<<",\"coexisting_query_peak_pmr\":"<<query_peak<<",\"restart_coexistence_peak_pmr\":"<<coexist_peak<<",\"final_peak_pmr\":"<<memory.stats().peak_bytes<<",\"export_canonical_bytes\":"<<export_bytes<<",\"allocations\":"<<allocations<<",\"query_allocation_failures_reached\":"<<failures<<",\"post_destroy_live_bytes\":0,\"compressed_bytes\":"<<f.gzip.size()<<",\"decompressed_bytes\":"<<f.raw.size()<<",\"compressed_sha256\":\""<<hex(f.config.compressed_sha256)<<"\",\"decompressed_sha256\":\""<<hex(sha256(f.raw))<<"\",\"restart_equivalent\":true,\"publication_eligible\":true,\"reduced_pmr_stop\":{\"budget\":16777216,\"framed\":"<<reduced.framed<<",\"accepted\":"<<reduced.accepted<<",\"native\":"<<reduced.native<<",\"peak\":"<<reduced.peak<<"},\"journal_cap_stop\":{\"tested\":"<<(n==128?"true":"false")<<",\"limit\":1023,\"framed\":"<<journal.framed<<",\"accepted\":"<<journal.accepted<<",\"native\":"<<journal.native<<",\"field\":\""<<journal.field<<"\"},\"observed_market_validated\":false}\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
