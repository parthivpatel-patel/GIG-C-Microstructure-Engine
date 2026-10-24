#include "gig/itch/decoder.hpp"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace gig::itch;
namespace {
using Clock=std::chrono::steady_clock;
void require(bool v){if(!v)throw std::runtime_error("decode measurement contract");}
void put(std::array<std::byte,36>& b,std::size_t at,std::uint64_t n,std::size_t width){for(std::size_t i=0;i<width;++i){b[at+width-i-1]=static_cast<std::byte>(n&255);n>>=8;}}
}
int main(int argc,char** argv){try{
 std::size_t samples=10000;if(argc==2){std::size_t used=0;samples=std::stoull(argv[1],&used);require(used==std::string_view(argv[1]).size());}require(argc<=2&&samples>0&&samples<=100000);
 std::array<std::byte,36> payload{};payload[0]=std::byte{'A'};put(payload,1,1,2);put(payload,5,1,6);put(payload,11,1,8);payload[19]=std::byte{'B'};put(payload,20,100,4);for(std::size_t i=24;i<32;++i)payload[i]=std::byte{' '};payload[24]=std::byte{'X'};put(payload,32,10000,4);
 std::uint64_t checksum=0;for(unsigned warm=0;warm<2;++warm)for(std::size_t i=0;i<samples;++i){const auto d=decode(payload);require(bool(d));checksum+=std::get<AddOrder>(d.data->message).price.value();}require(checksum==samples*20000);
 std::vector<std::int64_t> elapsed(samples);checksum=0;for(std::size_t i=0;i<samples;++i){const auto begin=Clock::now();const auto d=decode(payload);const auto end=Clock::now();require(bool(d));const auto& a=std::get<AddOrder>(d.data->message);checksum+=a.price.value()+a.shares.value()+a.order_reference.value()+d.data->header.timestamp.value()+d.data->header.stock_locate.value();elapsed[i]=std::chrono::duration_cast<std::chrono::nanoseconds>(end-begin).count();require(elapsed[i]>=0);}
 require(checksum==samples*10103);auto invalid=payload;invalid[19]=std::byte{'?'};require(decode(invalid).error.code==Code::invalid_enum);
 auto sorted=elapsed;std::sort(sorted.begin(),sorted.end());const auto quantile=[&](std::size_t percent){return sorted[(percent*samples+99)/100-1];};const auto start=Clock::now();const auto stop=Clock::now();const auto overhead=std::chrono::duration_cast<std::chrono::nanoseconds>(stop-start).count();
 std::cout<<"{\"workload\":\"synthetic_single_A_stateless_decode_v1\",\"scope\":\"decode_call_with_two_steady_clock_reads_no_framer_or_book\",\"samples\":"<<samples<<",\"warmup_batches\":2,\"checksum\":"<<checksum<<",\"seed\":null,\"p50_ns\":"<<quantile(50)<<",\"p95_ns\":"<<quantile(95)<<",\"p99_ns\":"<<quantile(99)<<",\"worst_ns\":"<<sorted.back()<<",\"clock_pair_probe_ns\":"<<overhead<<",\"clock_overhead_subtracted\":false,\"elapsed_ns\":[";
 for(std::size_t i=0;i<elapsed.size();++i){if(i)std::cout<<',';std::cout<<elapsed[i];}std::cout<<"]}\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
