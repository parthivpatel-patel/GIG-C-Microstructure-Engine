#include "gig/itch/context.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace gig::itch;
namespace {
using Bytes=std::vector<std::byte>;
void put(Bytes& p,std::size_t at,std::uint64_t v,std::size_t w){for(std::size_t i=0;i<w;++i){p[at+w-i-1]=static_cast<std::byte>(v&255);v>>=8;}}
void text(Bytes& p,std::size_t at,std::string_view s){for(char c:s)p[at++]=static_cast<std::byte>(c);}
Bytes event(char t){Bytes p(*expected_length(static_cast<std::uint8_t>(t)),std::byte{});p[0]=static_cast<std::byte>(t);p[2]=std::byte{1};p[10]=std::byte{1};return p;}
std::vector<Bytes> fixture(std::size_t n){
    std::vector<Bytes> v;v.reserve(n*4+2);auto s=event('S');s[2]=std::byte{0};s[11]=std::byte{'O'};v.push_back(s);
    auto r=event('R');text(r,11,"TEST    ");r[19]=std::byte{'Q'};r[20]=std::byte{'N'};put(r,21,100,4);text(r,25,"NC  PNN1N");r[38]=std::byte{'N'};v.push_back(r);
    for(std::size_t i=0;i<n;++i){auto a=event('A');put(a,11,i*2+1,8);a[19]=std::byte{'B'};put(a,20,10,4);text(a,24,"TEST    ");put(a,32,1000,4);v.push_back(a);}
    for(std::size_t i=0;i<n;++i){auto x=event('X');put(x,11,i*2+1,8);put(x,19,3,4);v.push_back(x);}
    for(std::size_t i=0;i<n;++i){auto u=event('U');put(u,11,i*2+1,8);put(u,19,i*2+2,8);put(u,27,8,4);put(u,31,1001,4);v.push_back(u);}
    for(std::size_t i=0;i<n;++i){auto e=event('E');put(e,11,i*2+2,8);put(e,19,8,4);put(e,23,i+1,8);v.push_back(e);}return v;
}
struct Measurement {std::uint64_t checksum{};ContextSummary summary;gig::TrackedResource::Stats memory;};
Measurement run(const std::vector<Bytes>& v,std::size_t n){
    gig::TrackedResource resource;ContextPolicy policy;policy.max_directories=1;policy.max_lifetime_orders=n*2;policy.max_matches=n;
    auto made=SourceContext::create({*SourceIdentity::make("synthetic-benchmark").data,*SourceIdentity::make("session").data,{},Initialization::synthetic_history_declared},policy,&resource);
    if(!made)throw std::runtime_error("create");
    auto& context=*made.data;const auto initial=resource.stats();std::uint64_t offset=0,ordinal=0,checksum=0;
    for(const auto& p:v){auto r=context.apply(p,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}});
        if(!r.committed())throw std::runtime_error("normalize");
        if(r.record->after)checksum+=r.record->after->remaining.value();
        offset+=p.size()+2;++ordinal;}
    const auto s=context.finish(ContextEnd::bounded_prefix);
    if(checksum!=n*25 || s.accepted_records!=v.size() || s.active_orders!=0 || s.lifetime_orders!=n*2 || s.matches!=n || !s.initialization_incomplete || s.source_complete)throw std::runtime_error("independent reference");
    if(resource.stats()!=initial)throw std::runtime_error("incremental allocation");
    return {checksum,s,resource.stats()};
}
}
int main(int argc,char** argv){try{
    std::size_t n=512,repetitions=7;
    if(argc>1){std::size_t used=0;n=std::stoull(argv[1],&used);if(used!=std::string_view(argv[1]).size())throw std::runtime_error("argument");}
    if(argc>2){std::size_t used=0;repetitions=std::stoull(argv[2],&used);if(used!=std::string_view(argv[2]).size())throw std::runtime_error("argument");}
    if(argc>3||n==0||n>4096||repetitions<3||repetitions>100)throw std::runtime_error("arguments");
    const auto v=fixture(n);const auto preflight=run(v,n);run(v,n);std::vector<double> times;
    for(std::size_t i=0;i<repetitions;++i){const auto begin=std::chrono::steady_clock::now();const auto r=run(v,n);if(r.checksum!=preflight.checksum)throw std::runtime_error("determinism");times.push_back(std::chrono::duration<double,std::nano>(std::chrono::steady_clock::now()-begin).count()/static_cast<double>(v.size()));}
    std::sort(times.begin(),times.end());std::uint64_t fingerprint=14695981039346656037ULL;
    for(const auto& p:v){for(auto b:p){fingerprint^=std::to_integer<unsigned>(b);fingerprint*=1099511628211ULL;}}
    std::cout<<"{\"workload\":\"synthetic_context_lifecycle_v1\",\"orders\":"<<n<<",\"records\":"<<v.size()<<",\"checksum\":"<<preflight.checksum
    <<",\"fixture_fnv1a64\":"<<fingerprint<<",\"lifetime_orders\":"<<preflight.summary.lifetime_orders<<",\"retired_orders\":"<<preflight.summary.lifetime_orders-preflight.summary.active_orders
    <<",\"matches\":"<<preflight.summary.matches<<",\"reserved_bytes\":"<<preflight.summary.reserved_bytes<<",\"allocations\":"<<preflight.memory.allocations
    <<",\"order_state_bytes\":"<<sizeof(OrderState)<<",\"match_state_bytes\":"<<sizeof(MatchState)<<",\"directory_state_bytes\":"<<sizeof(DirectoryState)<<",\"normalized_record_bytes\":"<<sizeof(NormalizedRecord)
    <<",\"repetitions\":"<<repetitions<<",\"warmups\":2,\"median_ns_per_record\":"<<times[times.size()/2]<<",\"minimum_ns_per_record\":"<<times.front()<<",\"compiler\":\""<<
#if defined(__clang__)
    "Clang "<<__clang_version__<<
#elif defined(__GNUC__)
    "GCC "<<__VERSION__<<
#else
    "unknown"<<
#endif
    "\"}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
