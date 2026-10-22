#include "gig/itch/binary_file.hpp"
#include "gig/itch/decoder.hpp"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace gig::itch;
namespace {
void put(std::vector<std::byte>& v,std::size_t at,std::uint64_t n,std::size_t width) {
    for(std::size_t i=0;i<width;++i){v[at+width-i-1]=static_cast<std::byte>(n&255);n>>=8;}
}
std::vector<std::byte> fixture(std::size_t count) {
    std::vector<std::byte> v(count*38+2);
    for(std::size_t i=0;i<count;++i) {
        const auto at=i*38;put(v,at,36,2);v[at+2]=std::byte{'A'};
        put(v,at+3,1,2);put(v,at+5,i%65536,2);put(v,at+7,i+1,6);
        put(v,at+13,i+1,8);v[at+21]=std::byte{'B'};put(v,at+22,100,4);
        for(std::size_t k=0;k<8;++k)v[at+26+k]=static_cast<std::byte>(k==0?'X':' ');
        put(v,at+34,1000000,4);
    }
    return v;
}
std::uint64_t run(std::span<const std::byte> input,std::size_t expected) {
    auto made=BinaryFileFramer::create({65535,65535,expected,static_cast<std::uint64_t>(input.size())});
    if(!made)throw std::runtime_error("framer allocation");
    auto& f=*made.data;std::size_t at=0,count=0;std::uint64_t sum=0;
    while(at<input.size()) {
        auto framed=f.feed(input.subspan(at,std::min<std::size_t>(4093,input.size()-at)));
        if(framed.error || framed.consumed==0)throw std::runtime_error("framing");
        at+=framed.consumed;
        if(framed.frame) {
            auto decoded=decode(framed.frame->payload,framed.frame->location);
            if(!decoded || decoded.data->type!='A')throw std::runtime_error("decoding");
            const auto& a=std::get<AddOrder>(decoded.data->message);
            sum+=a.order_reference.value()+a.shares.value()+a.price.value()+decoded.data->header.timestamp.value();++count;
        }
    }
    const auto end=f.finish();if(end.error || !end.session_complete || count!=expected)throw std::runtime_error("completion");return sum;
}
}
int main(int argc,char** argv) {
    try {
        std::size_t n=20000,reps=7;
        if(argc>1) {std::size_t used=0;n=std::stoull(argv[1],&used);if(used!=std::string_view(argv[1]).size())throw std::runtime_error("argument");}
        if(argc>2) {std::size_t used=0;reps=std::stoull(argv[2],&used);if(used!=std::string_view(argv[2]).size())throw std::runtime_error("argument");}
        if(argc>3 || n==0 || n>100000 || reps==0 || reps>100)throw std::runtime_error("argument range");
        const auto input=fixture(n);const auto expected=static_cast<std::uint64_t>(n)*(n+1)+static_cast<std::uint64_t>(n)*1000100;
        if(run(input,n)!=expected)throw std::runtime_error("independent sum mismatch");
        std::vector<double> times;
        for(std::size_t r=0;r<reps;++r){auto begin=std::chrono::steady_clock::now();if(run(input,n)!=expected)throw std::runtime_error("sum mismatch");
            times.push_back(std::chrono::duration<double,std::nano>(std::chrono::steady_clock::now()-begin).count()/static_cast<double>(n));}
        std::sort(times.begin(),times.end());
        std::uint64_t fingerprint=14695981039346656037ULL;for(auto b:input){fingerprint^=std::to_integer<unsigned>(b);fingerprint*=1099511628211ULL;}
        std::cout<<"{\"workload\":\"synthetic_itch_A_framing_decode_v1\",\"compiler\":\""<<
#if defined(__clang__)
        "Clang "<<__clang_version__<<
#elif defined(__GNUC__)
        "GCC "<<__VERSION__<<
#else
        "unknown"<<
#endif
        "\",\"records\":"<<n<<",\"bytes\":"<<input.size()<<",\"repetitions\":"<<reps<<",\"checksum\":"<<expected
        <<",\"fixture_fnv1a64\":"<<fingerprint<<",\"buffer_bytes\":65535,\"decoded_record_bytes\":"<<sizeof(DecodedRecord)
        <<",\"median_ns_per_record\":"<<times[times.size()/2]<<",\"minimum_ns_per_record\":"<<times.front()<<"}\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
