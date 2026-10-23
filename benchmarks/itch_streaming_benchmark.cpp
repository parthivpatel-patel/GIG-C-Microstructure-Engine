#include "gig/itch/streaming.hpp"
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
std::string hex(std::span<const std::byte> bytes){constexpr char digits[]="0123456789abcdef";std::string out;for(auto b:bytes){const auto c=std::to_integer<unsigned>(b);out+=digits[c>>4U];out+=digits[c&15U];}return out;}
std::uint32_t crc32_reference(std::span<const std::byte> bytes){std::uint32_t crc=0xffffffffU;for(auto byte:bytes){crc^=std::to_integer<unsigned>(byte);for(unsigned bit=0;bit<8;++bit)crc=(crc>>1U)^((crc&1U)?0xedb88320U:0U);}return crc^0xffffffffU;}
void little(Bytes& bytes,std::uint64_t value,unsigned width){for(unsigned i=0;i<width;++i){bytes.push_back(static_cast<std::byte>(value&255U));value>>=8U;}}
Bytes gzip_stored(std::span<const std::byte> input){
    // RFC1952 header plus byte-aligned RFC1951 stored blocks. This independent
    // fixture encoder runs outside every timed pass and uses no compression API.
    Bytes out{std::byte{0x1f},std::byte{0x8b},std::byte{8},std::byte{0},std::byte{0},std::byte{0},std::byte{0},std::byte{0},std::byte{0},std::byte{255}};
    std::size_t offset=0;do{const auto length=std::min<std::size_t>(65535,input.size()-offset);const bool final=offset+length==input.size();out.push_back(final?std::byte{1}:std::byte{0});little(out,length,2);little(out,static_cast<std::uint16_t>(~static_cast<std::uint16_t>(length)),2);out.insert(out.end(),input.begin()+static_cast<std::ptrdiff_t>(offset),input.begin()+static_cast<std::ptrdiff_t>(offset+length));offset+=length;}while(offset<input.size());
    little(out,crc32_reference(input),4);little(out,input.size(),4);return out;
}
struct Fixture {std::vector<Bytes> records;Bytes framed,compressed;Sha256Digest digest{},compressed_digest{},prefix_digest{};std::string digest_hex;};
Fixture fixture(std::size_t n){
    Fixture result;auto& v=result.records;v.reserve(n*8+8);auto s=event('S',0);s[11]=std::byte{'O'};v.push_back(s);
    for(std::uint16_t book=1;book<=2;++book){auto r=event('R',book);text(r,11,book==1?"TEST    ":"TWO     ");r[19]=std::byte{'Q'};r[20]=std::byte{'N'};put(r,21,100,4);text(r,25,"NC  PNN1N");r[38]=std::byte{'N'};v.push_back(r);}
    for(char phase:{'A','X','U','E'})for(std::size_t i=0;i<n;++i)for(std::uint16_t book=1;book<=2;++book){
        const auto old=i*4+book;const auto next=old+2;auto p=event(phase,book);put(p,11,phase=='E'?next:old,8);
        if(phase=='A'){p[19]=book==1?std::byte{'B'}:std::byte{'S'};put(p,20,10,4);text(p,24,book==1?"TEST    ":"TWO     ");put(p,32,book==1?1000:2000,4);}
        else if(phase=='X')put(p,19,3,4);
        else if(phase=='U'){put(p,19,next,8);put(p,27,8,4);put(p,31,book==1?1001:1999,4);}
        else{put(p,19,8,4);put(p,23,i*2+book,8);}v.push_back(p);
    }
    for(char code:std::string_view("SQMEC")){auto p=event('S',0);p[11]=static_cast<std::byte>(code);v.push_back(p);}
    for(const auto& p:v){result.framed.push_back(static_cast<std::byte>(p.size()>>8U));result.framed.push_back(static_cast<std::byte>(p.size()&255U));result.framed.insert(result.framed.end(),p.begin(),p.end());}
    result.prefix_digest=sha256(result.framed);result.framed.push_back(std::byte{0});result.framed.push_back(std::byte{0});
    result.digest=sha256(result.framed);result.digest_hex=hex(result.digest);result.compressed=gzip_stored(result.framed);result.compressed_digest=sha256(result.compressed);return result;
}
ReconstructionConfig configuration(std::size_t n,const Fixture& f){
    const auto source=source_id("synthetic-streaming-benchmark"),session=source_id("authored-full-session");
    Provenance provenance{Origin::synthetic,source,f.digest,seed};
    ContextPolicy policy;policy.max_directories=2;policy.max_lifetime_orders=n*4;policy.max_matches=n*2;
    InitializationEvidence evidence{InitialStateKind::authored_empty,source,session,source_id("literal-streaming-lifecycle-v1"),id("synthetic-streaming-lifecycle-v1"),id("1"),id("private-authored-synthetic-fixture"),scalar<gig::Digest>(f.digest_hex),seed,policy.first_location,true};
    ReconstructionConfig c{{source,session,provenance,Initialization::synthetic_history_declared},policy,evidence,id("streaming-benchmark-run"),{}};
    c.max_source_records=f.records.size();
    for(std::size_t i=0;i<2;++i){gig::InstrumentRules rules{scalar<gig::InstrumentId>(i+1),scalar<gig::VenueId>(1),scalar<gig::PriceTicks>(1),scalar<gig::PriceTicks>(2000000000),scalar<gig::QuantityLots>(UINT64_MAX),{1,10000},{1,1}};
        c.bindings[i]=BookBinding{stock(i==0?"TEST    ":"TWO     "),StockLocate{static_cast<std::uint16_t>(i+1)},rules,scalar<gig::StreamId>(i+1),{n,std::min(n,std::size_t{2}),std::min(n,std::size_t{2})},n*4};}
    return c;
}
struct Measurement {
    StreamingSummary summary{};
    ContextSummary context{};
    gig::TrackedResource::Stats before_destroy{},after_destroy{};
    std::uint64_t receipt_fnv{14695981039346656037ULL};
};
Measurement run(const Fixture& f,std::size_t n,std::size_t chunk){
    gig::TrackedResource resource(std::pmr::get_default_resource(),128U*1024U*1024U);Measurement out;
    {
        const auto c=configuration(n,f);StreamingConfig config{c,{}, {},f.compressed_digest};
        config.gzip.output_buffer_bytes=1024;config.gzip.max_compressed_bytes=f.compressed.size();config.gzip.max_decompressed_bytes=f.framed.size();
        config.gzip.max_expansion_ratio=2;config.gzip.expansion_slack_bytes=64;config.gzip.max_header_bytes=64;
        config.framing={64,64,f.records.size(),f.framed.size()};
        auto made=StreamingReconstructor::create(config,&resource);if(!made){std::cerr<<"create error="<<static_cast<unsigned>(made.error.code)<<" field="<<made.error.field<<'\n';throw std::runtime_error("create");}auto& stream=*made.data;
        std::size_t offset=0;
        while(offset<f.compressed.size()){
            const auto size=std::min(chunk,f.compressed.size()-offset);const auto input=std::span<const std::byte>(f.compressed).subspan(offset,size);const auto feed=stream.feed(input);
            if(feed.error){std::cerr<<"streaming error="<<static_cast<unsigned>(feed.error.code)<<" gzip="<<static_cast<unsigned>(feed.error.gzip.code)<<" framing="<<static_cast<unsigned>(feed.error.framing.code)<<'\n';throw std::runtime_error("feed");}
            require(feed.consumed>0&&feed.consumed<=size&&!feed.paused,"stream progress");offset+=feed.consumed;
        }
        out.summary=stream.finish(EndKind::source_eof);const auto& r=stream.reconstruction();out.context=r.context().summary();
        require(!out.summary.error&&out.summary.source_complete&&out.summary.publication_eligible&&out.summary.finished&&!out.summary.bounded_prefix,"full authored source");
        require(out.summary.gzip_member_verified&&out.summary.framer_terminated&&out.summary.compressed_identity_verified&&out.summary.decompressed_identity_verified,"integrity assertions");
        require(out.summary.compressed_sha256==f.compressed_digest&&out.summary.decompressed_sha256==f.digest&&out.summary.accepted_prefix_sha256==f.prefix_digest,"hashes");
        require(out.summary.compressed_bytes==f.compressed.size()&&out.summary.decompressed_bytes==f.framed.size()&&out.summary.accepted_prefix_bytes+2==f.framed.size()&&out.summary.framing_bytes==f.framed.size(),"byte accounting");
        require(out.summary.accepted_records==f.records.size()&&out.summary.source_records==f.records.size()&&out.summary.native_records==n*8&&out.summary.external_observations==8,"source accounting");
        require(out.context.lifetime_orders==n*4&&out.context.active_orders==0&&out.context.matches==n*2&&out.context.initialization_incomplete&&!out.context.session_incomplete&&out.context.source_complete,"context accounting");
        for(std::size_t i=0;i<2;++i){const auto* e=r.engine(i);require(!e->needs_recovery()&&!e->book().check_invariants()&&e->book().remaining()==0&&e->book().order_count()==0&&e->book().revision()==n*4,"book invariants");
            const auto l=e->book().ledger();require(l.added==n*10&&l.cancelled==n*3&&l.executed==n*8&&l.replacement_out==n*7&&l.replacement_in==n*8&&l.total_in==n*18&&l.total_out==n*18&&e->journal_size()==n*4,"ledger oracle");}
        const auto mix=[&](std::uint64_t x){for(unsigned j=0;j<8;++j){out.receipt_fnv^=x&255U;out.receipt_fnv*=1099511628211ULL;x>>=8U;}};
        for(const auto& receipt:r.receipts()){mix(receipt.source.location.ordinal.value());mix(static_cast<std::uint64_t>(receipt.disposition));mix(receipt.book_index?*receipt.book_index:UINT64_MAX);mix(receipt.native_sequence?*receipt.native_sequence:UINT64_MAX);}
        out.before_destroy=resource.stats();
    }
    out.after_destroy=resource.stats();require(out.after_destroy.live_bytes==0&&out.after_destroy.live_blocks==0,"released PMR memory");return out;
}
std::size_t argument(const char* value,std::size_t maximum){const std::string_view s(value);std::size_t out{};const auto r=std::from_chars(s.data(),s.data()+s.size(),out);require(r.ec==std::errc{}&&r.ptr==s.data()+s.size()&&out>0&&out<=maximum,"argument out of range");return out;}
}
int main(int argc,char** argv){try{
    if(argc==3&&std::string_view(argv[1])=="--fixture"){const auto f=fixture(argument(argv[2],256));std::cout.write(reinterpret_cast<const char*>(f.compressed.data()),static_cast<std::streamsize>(f.compressed.size()));return 0;}
    const auto n=argc>1?argument(argv[1],256):32;const auto repetitions=argc>2?argument(argv[2],100):7;const auto chunk=argc>3?argument(argv[3],65536):17;require(argc<=4&&repetitions>=3,"arguments");
    const auto f=fixture(n);const auto preflight=run(f,n,chunk);(void)run(f,n,chunk);std::vector<std::int64_t> elapsed;elapsed.reserve(repetitions);
    for(std::size_t i=0;i<repetitions;++i){const auto begin=std::chrono::steady_clock::now();const auto current=run(f,n,chunk);const auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-begin).count();require(ns>0&&current.receipt_fnv==preflight.receipt_fnv&&current.summary.accepted_prefix_sha256==preflight.summary.accepted_prefix_sha256,"determinism");elapsed.push_back(ns);}
    auto sorted=elapsed;std::sort(sorted.begin(),sorted.end());const auto median=sorted[sorted.size()/2];
    std::cout<<"{\"workload\":\"synthetic_two_book_gzip_streaming_v1\",\"scope\":\"create_incremental_gzip_frame_decode_context_native_journal_receipts_EOF_validate_destroy\",\"compression_fixture\":\"manual_RFC1951_stored_blocks\",\"orders_per_symbol\":"<<n<<",\"symbols\":2,\"records\":"<<f.records.size()<<",\"compressed_bytes\":"<<f.compressed.size()<<",\"decompressed_bytes\":"<<f.framed.size()<<",\"accepted_prefix_bytes\":"<<preflight.summary.accepted_prefix_bytes<<",\"compressed_sha256\":\""<<hex(f.compressed_digest)<<"\",\"decompressed_sha256\":\""<<f.digest_hex<<"\",\"accepted_prefix_sha256\":\""<<hex(f.prefix_digest)<<"\",\"seed\":"<<seed<<",\"native_records\":"<<preflight.summary.native_records<<",\"external_records\":8,\"receipt_fnv1a64\":"<<preflight.receipt_fnv<<",\"lifetime_orders\":"<<preflight.context.lifetime_orders<<",\"active_orders\":0,\"retired_orders\":"<<preflight.context.lifetime_orders<<",\"matches\":"<<preflight.context.matches<<",\"context_reserved_bytes\":"<<preflight.context.reserved_bytes<<",\"allocations\":"<<preflight.before_destroy.allocations<<",\"allocation_attempts\":"<<preflight.before_destroy.attempts<<",\"live_bytes_before_destroy\":"<<preflight.before_destroy.live_bytes<<",\"peak_pmr_bytes\":"<<preflight.before_destroy.peak_bytes<<",\"live_bytes_after_destroy\":"<<preflight.after_destroy.live_bytes<<",\"deallocations\":"<<preflight.after_destroy.deallocations<<",\"pmr_budget_bytes\":134217728,\"receipt_budget_bytes\":2097152,\"compressed_input_budget_bytes\":"<<f.compressed.size()<<",\"decompressed_output_budget_bytes\":"<<f.framed.size()<<",\"max_expansion_ratio\":2,\"expansion_slack_bytes\":64,\"max_header_bytes\":64,\"input_chunk_bytes\":"<<chunk<<",\"gzip_output_buffer_bytes\":1024,\"framer_buffer_bytes\":64,\"source_receipt_bytes\":"<<sizeof(SourceReceipt)<<",\"prepared_context_bytes\":"<<sizeof(PreparedContext)<<",\"source_context_bytes\":"<<sizeof(SourceContext)<<",\"order_state_bytes\":"<<sizeof(OrderState)<<",\"match_state_bytes\":"<<sizeof(MatchState)<<",\"directory_state_bytes\":"<<sizeof(DirectoryState)<<",\"reconstructor_bytes\":"<<sizeof(SyntheticReconstructor)<<",\"streaming_reconstructor_bytes\":"<<sizeof(StreamingReconstructor)<<",\"gzip_reader_bytes\":"<<sizeof(GzipReader)<<",\"framer_object_bytes\":"<<sizeof(BinaryFileFramer)<<",\"journal_entry_bytes\":"<<sizeof(gig::JournalEntry)<<",\"journal_records_per_symbol\":"<<n*4<<",\"journal_element_bytes\":"<<n*8*sizeof(gig::JournalEntry)<<",\"warmups\":2,\"repetitions\":"<<repetitions<<",\"elapsed_ns\":[";
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
    "\",\"source_complete\":true,\"session_complete\":true,\"publication_eligible\":true,\"observed_market_validated\":false,\"initialization\":\"authored_complete_empty_synthetic\"}\n";
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
