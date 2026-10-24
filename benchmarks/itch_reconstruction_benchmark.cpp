#include "gig/itch/reconstruction.hpp"
#include "gig/itch/sha256.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <algorithm>
#include <charconv>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {


using namespace gig::itch;
using Bytes=std::vector<std::byte>;
constexpr std::uint64_t seed=0x503147;
void require(bool v,const char* message){if(!v)throw std::runtime_error(message);}
template<class T,class I>T scalar(I n){const auto r=T::make(n);require(bool(r),"scalar");return *r.data;}
gig::Identity id(std::string_view s){return scalar<gig::Identity>(s);}
SourceIdentity source_id(std::string_view s){const auto r=SourceIdentity::make(s);require(bool(r),"source");return *r.data;}
void put(Bytes& p,std::size_t at,std::uint64_t n,std::size_t width){for(std::size_t i=0;i<width;++i){p[at+width-i-1]=static_cast<std::byte>(n&255U);n>>=8;}}
void text(Bytes& p,std::size_t at,std::string_view s){for(char c:s)p[at++]=static_cast<std::byte>(c);}
Text<8> stock(std::string_view s){Text<8> out;require(s.size()==8,"stock size");std::copy(s.begin(),s.end(),out.bytes.begin());return out;}
Bytes event(char type,std::uint16_t locate){Bytes p(*expected_length(static_cast<std::uint8_t>(type)),std::byte{});p[0]=static_cast<std::byte>(type);put(p,1,locate,2);put(p,3,seed&65535U,2);put(p,5,1,6);return p;}
struct Fixture {std::vector<Bytes> records;Bytes framed;std::array<std::byte,32> digest;std::string digest_hex;};
Fixture fixture(std::size_t n){
    Fixture result;auto& v=result.records;v.reserve(n*8+3);auto s=event('S',0);s[11]=std::byte{'O'};v.push_back(s);
    for(std::uint16_t book=1;book<=2;++book){auto r=event('R',book);text(r,11,book==1?"TEST    ":"TWO     ");r[19]=std::byte{'Q'};r[20]=std::byte{'N'};put(r,21,100,4);text(r,25,"NC  PNN1N");r[38]=std::byte{'N'};v.push_back(r);}
    for(char phase:{'A','X','U','E'})for(std::size_t i=0;i<n;++i)for(std::uint16_t book=1;book<=2;++book){
        const auto old=i*4+book;const auto next=old+2;auto p=event(phase,book);
        put(p,11,phase=='E'?next:old,8);
        if(phase=='A'){p[19]=book==1?std::byte{'B'}:std::byte{'S'};put(p,20,10,4);text(p,24,book==1?"TEST    ":"TWO     ");put(p,32,book==1?1000:2000,4);}
        else if(phase=='X')put(p,19,3,4);
        else if(phase=='U'){put(p,19,next,8);put(p,27,8,4);put(p,31,book==1?1001:1999,4);}
        else{put(p,19,8,4);put(p,23,i*2+book,8);}
        v.push_back(p);
    }
    for(const auto& p:v){result.framed.push_back(static_cast<std::byte>(p.size()>>8U));result.framed.push_back(static_cast<std::byte>(p.size()&255U));result.framed.insert(result.framed.end(),p.begin(),p.end());}
    result.digest=sha256(result.framed);
    constexpr char digits[]="0123456789abcdef";for(auto b:result.digest){const auto c=std::to_integer<unsigned>(b);result.digest_hex+=digits[c>>4U];result.digest_hex+=digits[c&15U];}
    return result;
}
ReconstructionConfig configuration(std::size_t n,const Fixture& f){
    const auto source=source_id("synthetic-l3-benchmark"),session=source_id("authored-prefix-session");
    Provenance provenance{Origin::synthetic,source,f.digest,seed};
    ContextPolicy policy;policy.max_directories=2;policy.max_lifetime_orders=n*4;policy.max_matches=n*2;
    InitializationEvidence evidence{InitialStateKind::authored_empty,source,session,source_id("literal-l3-lifecycle-v1"),id("synthetic-l3-lifecycle-v1"),id("1"),id("private-authored-synthetic-fixture"),scalar<gig::Digest>(f.digest_hex),seed,policy.first_location,true};
    ReconstructionConfig c{{source,session,provenance,Initialization::synthetic_history_declared},policy,evidence,id("l3-benchmark-run"),{}};
    c.max_source_records=f.records.size();
    for(std::size_t i=0;i<2;++i){gig::InstrumentRules rules{scalar<gig::InstrumentId>(i+1),scalar<gig::VenueId>(1),scalar<gig::PriceTicks>(1),scalar<gig::PriceTicks>(2000000000),scalar<gig::QuantityLots>(UINT64_MAX),{1,10000},{1,1}};
        c.bindings[i]=BookBinding{stock(i==0?"TEST    ":"TWO     "),StockLocate{static_cast<std::uint16_t>(i+1)},rules,scalar<gig::StreamId>(i+1),{n,std::min(n,std::size_t{2}),std::min(n,std::size_t{2})},n*4};}
    return c;
}
struct Measurement {
    std::uint64_t checksum{};
    ReconstructionSummary summary{};
    ContextSummary context{};
    gig::TrackedResource::Stats before_destroy{},after_destroy{};
    std::array<gig::QuantityLedger,2> ledgers{};
    std::array<std::size_t,2> journals{};
    std::uint64_t receipt_fnv{14695981039346656037ULL};
};
Measurement run(const Fixture& f,std::size_t n){
    gig::TrackedResource resource(std::pmr::get_default_resource(),128U*1024U*1024U);Measurement out;
    {
        const auto c=configuration(n,f);auto made=SyntheticReconstructor::create(c,&resource);if(!made){std::cerr<<"create error="<<static_cast<unsigned>(made.error.code)<<" field="<<made.error.field<<'\n';throw std::runtime_error("create");}auto& r=*made.data;
        std::uint64_t offset=0,ordinal=0;
        for(const auto& p:f.records){const auto step=r.process(p,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},c.source.provenance);require(step.committed,"process");
            out.checksum+=r.engine(0)->book().remaining()+r.engine(1)->book().remaining();offset+=p.size()+2;++ordinal;}
        out.summary=r.finish(ContextEnd::bounded_prefix);out.context=r.context().summary();
        require(out.summary.context_committed==f.records.size()&&out.summary.native_committed==n*8&&out.summary.external_observations==3,"source accounting");
        require(out.context.lifetime_orders==n*4&&out.context.active_orders==0&&out.context.matches==n*2&&out.context.initialization_incomplete,"context accounting");
        require(!out.summary.input_complete&&out.summary.finished&&out.summary.eligibility==ReconstructionEligibility::stopped_at_valid_prefix,"bounded prefix");
        for(std::size_t i=0;i<2;++i){const auto* e=r.engine(i);require(!e->needs_recovery()&&!e->book().check_invariants()&&e->book().remaining()==0&&e->book().order_count()==0&&e->book().revision()==n*4,"book invariants");
            out.ledgers[i]=e->book().ledger();out.journals[i]=e->journal_size();const auto l=out.ledgers[i];require(l.added==n*10&&l.cancelled==n*3&&l.executed==n*8&&l.replacement_out==n*7&&l.replacement_in==n*8&&l.total_in==n*18&&l.total_out==n*18&&out.journals[i]==n*4,"ledger oracle");}
        // Fixed-width mapping fingerprint, independent of object layout and padding.
        const auto mix=[&](std::uint64_t x){for(unsigned j=0;j<8;++j){out.receipt_fnv^=x&255U;out.receipt_fnv*=1099511628211ULL;x>>=8U;}};
        for(const auto& receipt:r.receipts()){mix(receipt.source.location.ordinal.value());mix(static_cast<std::uint64_t>(receipt.disposition));mix(receipt.book_index?*receipt.book_index:UINT64_MAX);mix(receipt.native_sequence?*receipt.native_sequence:UINT64_MAX);}
        out.before_destroy=resource.stats();
    }
    out.after_destroy=resource.stats();require(out.after_destroy.live_bytes==0&&out.after_destroy.live_blocks==0,"released PMR memory");return out;
}
std::size_t argument(const char* value,std::size_t maximum){const std::string_view s(value);std::size_t out{};const auto r=std::from_chars(s.data(),s.data()+s.size(),out);require(r.ec==std::errc{}&&r.ptr==s.data()+s.size()&&out>0&&out<=maximum,"argument out of range");return out;}
}
int main(int argc,char** argv){try{
    const auto n=argc>1?argument(argv[1],256):32;const auto repetitions=argc>2?argument(argv[2],100):7;require(argc<=3&&repetitions>=3,"arguments");
    const auto f=fixture(n);const auto preflight=run(f,n);(void)run(f,n);std::vector<std::int64_t> elapsed;elapsed.reserve(repetitions);
    for(std::size_t i=0;i<repetitions;++i){const auto begin=std::chrono::steady_clock::now();const auto current=run(f,n);const auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-begin).count();require(ns>0&&current.checksum==preflight.checksum&&current.receipt_fnv==preflight.receipt_fnv,"determinism");elapsed.push_back(ns);}
    auto sorted=elapsed;std::sort(sorted.begin(),sorted.end());const auto median=sorted[sorted.size()/2];
    std::cout<<"{\"workload\":\"synthetic_two_book_reconstruction_v1\",\"scope\":\"create_decode_context_native_journal_receipts_validate_destroy\",\"orders_per_symbol\":"<<n<<",\"symbols\":2,\"records\":"<<f.records.size()<<",\"input_bytes\":"<<f.framed.size()<<",\"fixture_sha256\":\""<<f.digest_hex<<"\",\"seed\":"<<seed<<",\"native_records\":"<<preflight.summary.native_committed<<",\"external_records\":3,\"checksum\":"<<preflight.checksum<<",\"receipt_fnv1a64\":"<<preflight.receipt_fnv<<",\"lifetime_orders\":"<<preflight.context.lifetime_orders<<",\"matches\":"<<preflight.context.matches<<",\"context_reserved_bytes\":"<<preflight.context.reserved_bytes<<",\"allocations\":"<<preflight.before_destroy.allocations<<",\"allocation_attempts\":"<<preflight.before_destroy.attempts<<",\"live_bytes_before_destroy\":"<<preflight.before_destroy.live_bytes<<",\"peak_pmr_bytes\":"<<preflight.before_destroy.peak_bytes<<",\"live_bytes_after_destroy\":"<<preflight.after_destroy.live_bytes<<",\"deallocations\":"<<preflight.after_destroy.deallocations<<",\"pmr_budget_bytes\":134217728,\"source_receipt_bytes\":"<<sizeof(SourceReceipt)<<",\"prepared_context_bytes\":"<<sizeof(PreparedContext)<<",\"source_context_bytes\":"<<sizeof(SourceContext)<<",\"reconstructor_bytes\":"<<sizeof(SyntheticReconstructor)<<",\"journal_entry_bytes\":"<<gig::ReplayEngine::journal_record_bytes()<<",\"journal_records_per_symbol\":"<<n*4<<",\"journal_element_bytes\":"<<n*8*gig::ReplayEngine::journal_record_bytes()<<",\"warmups\":2,\"repetitions\":"<<repetitions<<",\"elapsed_ns\":[";
    for(std::size_t i=0;i<elapsed.size();++i){if(i)std::cout<<',';std::cout<<elapsed[i];}std::cout<<"],\"median_ns_per_record\":"<<static_cast<double>(median)/static_cast<double>(f.records.size())<<",\"throughput_records_per_second\":"<<static_cast<double>(f.records.size())*1e9/static_cast<double>(median)<<",\"compiler\":\""<<
#if defined(__clang__)
    "Clang "<<__clang_version__<<
#elif defined(__GNUC__)
    "GCC "<<__VERSION__<<
#else
    "unknown"<<
#endif
    "\",\"build_configuration\":\""<<
#if defined(NDEBUG)
    "Release"<<
#else
    "Debug"<<
#endif
    "\",\"container_complete\":false,\"initialization\":\"authored_complete_empty_synthetic\"}\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
