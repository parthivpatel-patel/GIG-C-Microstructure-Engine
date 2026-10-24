#include "gig/itch/decoder.hpp"
#include <array>
#include <iostream>
#include <limits>
#include <type_traits>
#include <vector>
using namespace gig::itch;
namespace {
int failures=0;
void check(bool condition,const char* label){if(!condition){std::cerr<<"FAIL "<<label<<'\n';++failures;}}
std::vector<std::byte> record(char type){return std::vector<std::byte>(*expected_length(static_cast<std::uint8_t>(type)),std::byte{0});}
void put(std::vector<std::byte>& v,std::size_t offset,std::uint64_t n,std::size_t width){for(std::size_t i=0;i<width;++i){v[offset+width-i-1]=static_cast<std::byte>(n&255U);n>>=8U;}}
void text(std::vector<std::byte>& v,std::size_t at,std::string_view value){for(char c:value)v[at++]=static_cast<std::byte>(c);}
std::vector<std::byte> add(){auto v=record('A');v[0]=std::byte{'A'};put(v,11,1,8);v[19]=std::byte{'B'};put(v,20,1,4);text(v,24,"ABC     ");return v;}
}
int main(){
    static_assert(!std::is_convertible_v<Shares,Price4>);
    static_assert(!std::is_convertible_v<std::uint32_t,Shares>);
    static_assert(std::is_nothrow_move_constructible_v<DecodedRecord>);
    auto v=add();put(v,1,65535,2);put(v,3,65535,2);put(v,5,281474976710655ULL,6);put(v,11,UINT64_MAX,8);put(v,20,UINT32_MAX,4);put(v,32,2000000000,4);
    auto identity=SourceIdentity::make("synthetic-independent-test");
    Provenance provenance;provenance.origin=Origin::synthetic;provenance.source=*identity.data;provenance.generator_seed=42;provenance.sha256=std::array<std::byte,32>{std::byte{0xAB}};
    auto decoded=decode(v,{ByteOffset{10},ByteOffset{12},RecordOrdinal{3}},provenance);
    check(bool(decoded),"maxima decode");
    if(decoded){const auto& d=*decoded.data;const auto& a=std::get<AddOrder>(d.message);
        check(d.header.timestamp.value()==281474976710655ULL,"full48 time");check(a.price.value()==2000000000,"exact Price4 max");
        check(a.shares.value()==UINT32_MAX&&a.order_reference.value()==UINT64_MAX,"unsigned maxima");
        check(a.stock.view()=="ABC     ","padding preserved");check(d.provenance==provenance,"owned provenance");
        v[24]=std::byte{'Z'};check(a.stock.view()=="ABC     ","owned source text");}
    v=add();put(v,32,2000000001,4);auto bad=decode(v);check(!bad&&bad.error.code==Code::invalid_value&&bad.error.offset.value()==34,"price overflow field offset");
    v=add();v[19]=std::byte{'?'};bad=decode(v);check(!bad&&bad.error.code==Code::invalid_enum,"bad side");
    v=add();put(v,20,0,4);auto zero_shares=decode(v);
    check(zero_shares&&std::get<AddOrder>(zero_shares.data->message).shares.value()==0,"zero source shares retained for future semantic validation");
    v=add();put(v,11,0,8);auto zero_reference=decode(v);
    check(zero_reference&&std::get<AddOrder>(zero_reference.data->message).order_reference.value()==0,"zero source reference retained for future semantic validation");
    v=add();v[24]=std::byte{0};check(!decode(v),"non ASCII text");
    v=add();check(!decode(v,{ByteOffset{0},ByteOffset{0},RecordOrdinal{0}}),"invalid relation");
    check(!decode(v,{ByteOffset{UINT64_MAX},ByteOffset{1},RecordOrdinal{0}}),"frame offset overflow");
    check(!decode(v,{ByteOffset{UINT64_MAX-3},ByteOffset{UINT64_MAX-1},RecordOrdinal{0}}),"payload end overflow");
    check(!decode(std::span<const std::byte>{}),"empty payload");
    const std::array<std::pair<char,std::size_t>,23> lengths{{{'S',12},{'R',39},{'H',25},{'Y',20},{'L',26},{'V',35},{'W',12},{'K',28},{'J',35},{'h',21},{'A',36},{'F',40},{'E',31},{'C',36},{'X',23},{'D',19},{'U',35},{'P',44},{'Q',40},{'B',19},{'I',50},{'N',20},{'O',48}}};
    for(auto [type,size]:lengths){check(expected_length(static_cast<std::uint8_t>(type))==size,"known length");auto b=record(type);b[0]=static_cast<std::byte>(type);b.push_back(std::byte{0});auto r=decode(b);check(!r&&r.error.code==Code::length_mismatch,"known length checked first");}
    for(char type:std::string_view{"HYL VWKJhINO"}){if(type==' ')continue;auto b=record(type);b[0]=static_cast<std::byte>(type);auto r=decode(b);check(!r&&r.error.code==Code::unsupported_type,"known unsupported");}
    std::array unknown{std::byte{'?'}};bad=decode(unknown);check(!bad&&bad.error.code==Code::unknown_type,"unknown type");
    auto s=record('S');s[0]=std::byte{'S'};s[11]=std::byte{'O'};check(bool(decode(s)),"system event");s[11]=std::byte{'?'};check(!decode(s),"system enum");
    auto q=record('Q');q[0]=std::byte{'Q'};text(q,19,"ABC     ");q[39]=std::byte{'O'};check(bool(decode(q)),"zero cross quantity preserved");
    auto p=record('P');p[0]=std::byte{'P'};p[19]=std::byte{'B'};put(p,20,1,4);text(p,24,"ABC     ");check(bool(decode(p)),"reserved zero trade reference");
    auto b=record('B');b[0]=std::byte{'B'};check(bool(decode(b)),"zero raw broken match preserved");
    for(char type:std::string_view{"FECDXU"}){
        auto t=record(type);t[0]=static_cast<std::byte>(type);put(t,11,1,8);
        if(type=='F'){t=add();t.resize(40);t[0]=std::byte{'F'};text(t,36,"MPID");}
        if(type=='E'||type=='C'||type=='X')put(t,19,1,4);
        if(type=='C')t[31]=std::byte{'N'};
        if(type=='U'){put(t,19,2,8);put(t,27,1,4);}
        auto first=decode(t);auto second=decode(t);
        check(bool(first)&&first.data==second.data,"supported variant deterministic");
    }
    auto directory=record('R');directory[0]=std::byte{'R'};text(directory,11,"ABC     ");
    directory[19]=std::byte{'Q'};directory[20]=std::byte{'N'};put(directory,21,100,4);
    text(directory,25,"NC  P N1N");directory[38]=std::byte{'N'};
    auto rd=decode(directory);check(bool(rd),"directory fields");
    for(std::size_t field:std::array<std::size_t,10>{19,20,25,29,30,31,32,33,38,0}){
        if(field==0)continue;
        auto copy=directory;copy[field]=std::byte{'?'};
        check(!decode(copy),"directory finite enum rejected");
    }
    auto invalid_origin=provenance;invalid_origin.origin=static_cast<Origin>(255);
    check(!decode(add(),{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}},invalid_origin),"invalid provenance origin");
    auto prior=decode(add());auto malformed=add();malformed[19]=std::byte{'?'};
    check(!decode(malformed)&&prior.data==decode(add()).data,"failure leaves prior result intact");
    std::cout<<"sizeof DecodedRecord="<<sizeof(DecodedRecord)<<" Header="<<sizeof(Header)<<" Message="<<sizeof(Message)<<'\n';
    return failures==0?0:1;
}
