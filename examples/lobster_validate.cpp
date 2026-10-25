#include "gig/lobster/reconstruction.hpp"
#include "gig/itch/sha256.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <fstream>
#include <cstdlib>
#include <iostream>
#include <string>
using namespace gig::lobster;
namespace {
gig::Identity id(std::string_view s){auto x=gig::Identity::make(s);if(!x)throw std::runtime_error("identity");return *x.data;}
gig::Digest digest(std::string_view s){auto x=gig::Digest::make(s);if(!x)throw std::runtime_error("digest");return *x.data;}
struct Reader {
    std::ifstream stream;gig::itch::Sha256 hash;std::uint64_t& bytes;std::uint64_t max_bytes;std::size_t max_line;
    Reader(const char* path,std::uint64_t& n,std::uint64_t limit,std::size_t line):stream(path,std::ios::binary),bytes(n),max_bytes(limit),max_line(line){if(!stream)throw std::runtime_error("input_open");}
    bool line(std::string& out){out.clear();char c{};while(stream.get(c)){if(bytes==max_bytes)throw std::runtime_error("input_byte_budget");++bytes;if(out.size()==max_line)throw std::runtime_error("line_budget");out.push_back(c);if(c=='\n')break;}if(stream.bad())throw std::runtime_error("input_read");if(out.empty())return false;if(!hash.update(std::as_bytes(std::span(out.data(),out.size()))))throw std::runtime_error("hash_budget");return true;}
    std::string checksum()const{const auto h=gig::itch::hex_digest(hash.finish());return {h.data(),h.size()};}
};
}
// Gate is operator assertion, not a legal permission verifier. Public wrapper
// requires a separately supplied permission record before using private inputs.
int main(int argc,char** argv){try{
    if(argc<7||argc>10)return 2;
    const std::string_view mode=argv[1];if(mode!="--authored"&&mode!="--authorized-private")return 2;
    const std::uint64_t max_rows=argc>7?std::stoull(argv[7]):1000000;
    const std::uint64_t max_bytes=argc>8?std::stoull(argv[8]):128ULL*1024ULL*1024ULL;
    const std::size_t memory_limit=argc>9?std::stoull(argv[9]):64U*1024U*1024U;
    if(memory_limit<4096||memory_limit>128U*1024U*1024U)return 2;
    Limits limits;limits.max_records=max_rows;limits.max_bytes=max_bytes;
    if(const char* v=std::getenv("GIG_LOBSTER_TIMEOUT_MS"))limits.max_milliseconds=std::stoull(v);
    if(const char* v=std::getenv("GIG_LOBSTER_LINE_LIMIT"))limits.max_line_bytes=std::stoull(v);
    const auto* dataset=std::getenv("GIG_LOBSTER_DATASET_ID");const auto* session=std::getenv("GIG_LOBSTER_SESSION_ID");const auto* permission=std::getenv("GIG_LOBSTER_PERMISSION_REF");
    if(mode=="--authorized-private"&&(!dataset||!session||!permission))return 2;
    gig::TrackedResource memory(std::pmr::get_default_resource(),memory_limit);
    const auto origin=mode=="--authored"?gig::Origin::synthetic:gig::Origin::observed;
    SourceBinding binding{id(dataset?dataset:"authored-lobster-pair"),id(session?session:"authored-session"),id(permission?permission:"authored-fixture-permitted"),digest(argv[6]),digest(argv[4]),digest(argv[5]),origin,0};
    auto reconstruction=KnownSubset::create(binding,limits,100000,&memory);if(!reconstruction){std::cerr<<reconstruction.error.field<<'\n';return 2;}
    std::uint64_t input_bytes=0;Reader messages(argv[2],input_bytes,max_bytes,limits.max_line_bytes),book(argv[3],input_bytes,max_bytes,limits.max_line_bytes);
    std::string ml,bl;ml.reserve(4096);bl.reserve(4096);const auto start=std::chrono::steady_clock::now();
    while(true){const bool a=messages.line(ml),b=book.line(bl);if(!a||!b){const auto error=reconstruction.data->finish(!a,!b);if(error){std::cerr<<error.field<<'\n';return 2;}break;}
        const auto step=reconstruction.data->process(ml,bl);if(!step){std::cerr<<step.error.field<<'\n';return 2;}
    }
    if(messages.checksum()!=argv[4]||book.checksum()!=argv[5]){std::cerr<<"input_checksum\n";return 2;}
    const auto& s=reconstruction.data->summary();const auto& p=reconstruction.data->parsing();
    const auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now()-start).count();
    std::cout<<"{\"schema\":\"gig.lobster.analysis.v1\",\"origin\":\""<<(origin==gig::Origin::synthetic?"synthetic":"observed")<<"\",\"initialization\":\"unknown\",\"full_l3_complete\":false,\"rows\":"<<s.rows<<",\"native\":"<<s.native<<",\"external\":"<<s.external<<",\"unknown_order\":"<<s.unknown<<",\"inconsistent\":"<<s.inconsistent<<",\"unsupported\":"<<s.unsupported<<",\"blocked\":"<<s.blocked<<",\"native_rejected\":"<<s.native_rejected<<",\"resource_rejected\":"<<s.resource_rejected<<",\"quantity_eligible\":"<<s.quantity_eligible<<",\"quantity_matches\":"<<s.quantity_matches<<",\"best_eligible\":"<<s.best_eligible<<",\"best_matches\":"<<s.best_matches<<",\"depth_eligible\":"<<s.depth_eligible<<",\"depth_matches\":"<<s.depth_matches<<",\"lower_bound_checks\":"<<s.lower_bound_checks<<",\"lower_bound_violations\":"<<s.lower_bound_violations<<",\"equal_level_quantities\":"<<s.equal_level_quantities<<",\"first_mismatch\":";
    if(s.first_mismatch)std::cout<<*s.first_mismatch;else std::cout<<"null";
    std::cout<<",\"locked\":"<<p.locked<<",\"crossed\":"<<p.crossed<<",\"zero_volume\":"<<p.zero_volume<<",\"missing_levels\":"<<p.missing_levels<<",\"prefix_blocked\":"<<(s.prefix_blocked?"true":"false")<<",\"input_bytes\":"<<input_bytes<<",\"pmr_peak_bytes\":"<<memory.stats().peak_bytes<<",\"allocations\":"<<memory.stats().allocations<<",\"analysis_ns\":"<<ns<<",\"row_time_first\":";
    if(p.first)std::cout<<p.first->value;else std::cout<<"null";std::cout<<",\"row_time_last\":";if(p.last)std::cout<<p.last->value;else std::cout<<"null";std::cout<<",\"event_codes\":[";for(std::size_t i=0;i<8;++i){if(i)std::cout<<',';std::cout<<p.codes[i];}std::cout<<"],\"tied_timestamps\":"<<p.tied_timestamps<<",\"zero_volume_levels\":"<<p.zero_volume_levels<<",\"price4_min\":";if(p.price4_min)std::cout<<*p.price4_min;else std::cout<<"null";std::cout<<",\"price4_max\":";if(p.price4_max)std::cout<<*p.price4_max;else std::cout<<"null";std::cout<<",\"shares_min\":";if(p.shares_min)std::cout<<*p.shares_min;else std::cout<<"null";std::cout<<",\"shares_max\":";if(p.shares_max)std::cout<<*p.shares_max;else std::cout<<"null";std::cout<<",\"share_histogram\":[";for(std::size_t i=0;i<65;++i){if(i)std::cout<<',';std::cout<<p.share_histogram[i];}std::cout<<"]}\n";
    return 0;
}catch(const std::exception&){std::cerr<<"bounded_input_or_resource_failure\n";return 2;}}
