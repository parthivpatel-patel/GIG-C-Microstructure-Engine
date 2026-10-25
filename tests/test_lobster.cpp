#include "gig/lobster/adapter.hpp"
#include <iostream>
#include <sstream>
#include <string>
#include <stdexcept>
#include <chrono>
#include "support/lobster_checks.hpp"
using namespace gig::lobster;
namespace {
void check(bool v,const char* message){if(!v)throw std::runtime_error(message);}
std::string reference(){return "110,10,100,20,120,11,90,21,130,12,80,22,140,13,70,23,150,14,60,24";}
void tests(){
    gig::lobster::test::reconstruction_checks();
    auto m=parse_message("34200.123456789,1,19,10,100,1");check(m&&m.data->time.value==34200123456789ULL&&m.data->kind==Kind::add,"message exact nanoseconds");
    for(auto code:{1,2,3,4,5})check(bool(parse_message("1,"+std::to_string(code)+",12,3,100,-1")),"all ordinary types");
    for(auto price:{-1,0,1}){auto h=parse_message("1,7,0,0,"+std::to_string(price)+",-1");check(h&&h.data->kind==Kind::halt,"halt flags");}
    auto u=parse_message("1,6,0,0,0,0");check(u&&u.data->kind==Kind::unsupported,"undocumented6 explicit unsupported");
    for(const auto bad:{"86400,1,1,1,1,1","1.1234567890,1,1,1,1,1","1e2,1,1,1,1,1","1,1,1,0,100,1","1,1,-1,1,100,1","1,1,1,1,100,0","1,1,1,1,100,1,9","1,7,1,0,-1,-1","1,1,18446744073709551616,1,100,1"})check(!parse_message(bad),"invalid message rejected");
    auto r=parse_reference(reference());check(r&&r.data->asks[4].price.value==150&&r.data->bids[0].quantity.value==20,"twenty column reference");
    check(!parse_reference("110,10,100,20"),"truncated reference");
    auto unordered=reference();unordered.replace(unordered.find("120"),3,"109");check(!parse_reference(unordered),"ask ordering");
    std::string sentinels;for(int i=0;i<5;++i){if(i)sentinels+=',';sentinels+="9999999999,0,-9999999999,0";}auto empty=parse_reference(sentinels);check(empty&&empty.data->missing_levels==10,"sentinel levels exact");
    auto zero=reference();zero.replace(4,2,"0");auto anomalous=parse_reference(zero);check(anomalous&&anomalous.data->zero_volume,"zero visible volume observation retained");
    auto crossed=reference();crossed.replace(crossed.find("100"),3,"115");auto c=parse_reference(crossed);check(c&&c.data->crossed,"crossed observation preserved");
    auto stream=PairedValidator::create();check(bool(stream),"paired create");check(bool(stream.data->accept("1,1,11,10,100,1",reference())),"paired accept");const auto accepted=stream.data->summary().accepted;
    check(!stream.data->accept("1,1,12,10,100,1","bad")&&stream.data->summary().accepted==accepted,"pair invalid reference does not advance accepted state");
    check(!stream.data->accept("2,1,12,10,100,1",reference()),"stopped parser no skip");
    auto limit=PairedValidator::create({1024,1,4096,120000,1});check(bool(limit)&&bool(limit.data->accept("1,1,11,10,100,1",reference())),"row cap first");check(!limit.data->accept("2,1,12,10,100,1",reference()),"row cap enforced");
    auto aligned=PairedValidator::create();check(bool(aligned)&&bool(aligned.data->finish(true,false)),"alignment mismatch rejected");
    auto equal=PairedValidator::create();check(bool(equal.data->accept("1,1,11,10,100,1",reference()))&&bool(equal.data->accept("1,1,12,10,100,1",reference())),"timestamp ties preserve capture order");check(!equal.data->accept("0,1,13,10,100,1",reference()),"time regression");
    std::cout<<"lobster authored parser/resource/atomicity checks passed\n";
}
}
int main(int argc,char** argv){try{
    if(argc==1){tests();return 0;}
    if(argc==3&&std::string_view(argv[1])=="--parser-benchmark"){
        const auto n=std::stoull(argv[2]);if(n==0||n>1000000)return 2;
        const auto row=reference();const auto start=std::chrono::steady_clock::now();std::uint64_t checksum=0;
        for(std::uint64_t i=0;i<n;++i){const auto m=parse_message("34200.123456789,1,19,10,100,1");const auto r=parse_reference(row);if(!m||!r)return 2;checksum+=m.data->quantity.value+r.data->bids[0].quantity.value;}
        const auto valid=std::chrono::steady_clock::now();std::uint64_t errors=0;
        for(std::uint64_t i=0;i<n;++i){errors+=!parse_message("invalid")?1U:0U;errors+=!parse_reference("invalid")?1U:0U;}
        const auto finish=std::chrono::steady_clock::now();
        std::cout<<"{\"pairs\":"<<n<<",\"checksum\":"<<checksum<<",\"errors\":"<<errors<<",\"valid_ns\":"<<std::chrono::duration_cast<std::chrono::nanoseconds>(valid-start).count()<<",\"invalid_ns\":"<<std::chrono::duration_cast<std::chrono::nanoseconds>(finish-valid).count()<<"}\n";return 0;
    }
    if(argc!=2||std::string_view(argv[1])!="--parser-fixtures")return 2;
    std::string line;line.reserve(4100);char c{};
    while(std::cin.get(c)){if(c!='\n'){if(line.size()>=4098)return 2;line.push_back(c);continue;}
        if(line.size()<2)return 2;
        if(line[0]=='M'){const auto result=parse_message(std::string_view(line).substr(2));if(!result)std::cout<<"null\n";else {const auto& m=*result.data;std::cout<<'['<<m.time.value<<','<<m.code<<','<<m.order<<','<<m.quantity.value<<','<<m.price.value<<','<<m.direction<<','<<static_cast<unsigned>(m.kind)<<"]\n";}}
        else {const auto result=parse_reference(std::string_view(line).substr(2));if(!result)std::cout<<"null\n";else {const auto&r=*result.data;std::cout<<'[';for(std::size_t i=0;i<5;++i){if(i)std::cout<<',';std::cout<<'['<<r.asks[i].price.value<<','<<r.asks[i].quantity.value<<','<<r.bids[i].price.value<<','<<r.bids[i].quantity.value<<']';}std::cout<<','<<r.missing_levels<<','<<r.locked<<','<<r.crossed<<','<<r.zero_volume<<"]\n";}}
        line.clear();
    }
    return line.empty()?0:2;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
