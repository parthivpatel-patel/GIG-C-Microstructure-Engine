#include "gig/itch/binary_file.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <iostream>
#include <vector>
#include <stdexcept>
using namespace gig::itch;
namespace {
void check(bool b,const char* s) { if(!b) throw std::runtime_error(s); }
std::vector<std::byte> bytes(std::initializer_list<unsigned> xs) { std::vector<std::byte> out;for(auto x:xs)out.push_back(static_cast<std::byte>(x));return out; }
BinaryFileFramer make(FramerLimits l={},ByteOffset o=ByteOffset{},RecordOrdinal n=RecordOrdinal{}) {
    auto r=BinaryFileFramer::create(l,o,n);check(bool(r),"create");return std::move(*r.data);
}
void basic() {
    const auto stream=bytes({0,3,1,2,3,0,1,9,0,0});
    for(std::size_t chunk=1;chunk<=stream.size();++chunk) {
        auto f=make();std::size_t at=0,count=0;
        while(at<stream.size()) {
            const auto r=f.feed(std::span(stream).subspan(at,std::min(chunk,stream.size()-at)));
            check(r.status!=FrameStatus::error && r.consumed>0,"progress");at+=r.consumed;
            if(r.frame) {check(r.frame->location.ordinal.value()==count,"ordinal");
                check(r.frame->location.frame_offset.value()==(count==0?0:5),"offset");
                check(r.frame->payload.size()==(count==0?3:1),"length");
                check(r.frame->payload[0]==static_cast<std::byte>(count==0?1:9),"payload");++count;}
        }
        const auto end=f.finish();check(count==2 && end.session_complete && !end.error,"termination");
        check(f.finish().session_complete,"idempotent finish");
        check(f.feed({}).error.code==Code::already_finished,"sealed");
    }
}
void golden() {
    const auto data=bytes({0,12,83,0,0,0,0,0,0,0,0,0,1,79,0,0});
    auto f=make();auto r=f.feed(data);check(r.frame && r.consumed==14,"literal golden frame");
    check(r.frame->location.payload_offset.value()==2 && r.frame->payload[10]==std::byte{1} && r.frame->payload[11]==std::byte{'O'},"literal golden fields");
    check(f.feed(std::span(data).subspan(14)).status==FrameStatus::terminal && f.position().value()==16,"literal golden terminal");
    std::vector<std::byte> largest(65539,std::byte{0xFF});largest[65537]=largest[65538]=std::byte{0};
    auto max=make();r=max.feed(largest);check(r.frame && r.frame->payload.size()==65535 && r.consumed==65537,"max length opaque");
    check(max.feed(std::span(largest).subspan(r.consumed)).status==FrameStatus::terminal && !max.finish().error,"max length terminal");
}
void errors() {
    auto f=make();check(f.finish().error.code==Code::missing_terminator,"empty EOF");
    for(std::size_t n=1;n<5;++n) {
        auto x=make();auto b=bytes({0,3,1,2,3});x.feed(std::span(b).first(n));
        auto end=x.finish();check(end.error.code==(n==1?Code::truncated_length:Code::truncated_payload),"truncation code");
        check(end.error.offset.value()==(n==1?0:2),"truncation offset");
        auto y=make();y.feed(std::span(b).first(n));auto cut=y.finish(EndKind::bounded_prefix);
        check(!cut.error && cut.bounded_prefix && !cut.session_complete && cut.residual_bytes==n,"bounded cutoff");
    }
    auto z=make();auto term=bytes({0,0,0,0});auto r=z.feed(term);check(r.consumed==2 && r.status==FrameStatus::terminal,"terminator");
    r=z.feed(std::span(term).subspan(2));check(r.error.code==Code::trailing_after_terminator && r.error.offset.value()==2,"duplicate terminator");
    check(z.feed({}).error==r.error,"sticky error");
    check(!z.finish().session_complete,"error cannot certify complete session");
    auto bounded=make();bounded.feed(bytes({0,0}));
    check(!bounded.finish(EndKind::bounded_prefix).session_complete,"prefix cannot certify complete source");
    auto bad=make();check(bad.finish(static_cast<EndKind>(99)).error.code==Code::invalid_enum,"invalid end enum");
}
void limits() {
    FramerLimits l;l.max_payload_bytes=3;l.buffer_bytes=3;
    auto f=make(l);auto b=bytes({0,4});auto r=f.feed(b);
    check(r.error.code==Code::record_too_large && r.consumed==2 && r.error.offset.value()==0,"oversize");
    auto cap=make(l);check(cap.feed(bytes({0,3,1,2,3})).status==FrameStatus::record,"payload exact cap");
    l.max_records=1;auto one=make(l);check(one.feed(bytes({0,1,8})).frame.has_value(),"record exact cap");
    check(one.feed(bytes({0,1})).error.code==Code::record_limit,"record cap plus one");
    l.max_records=0;auto n=make(l);check(n.feed(bytes({0,1})).error.code==Code::record_limit,"records");
    auto t=make(l);check(t.feed(bytes({0,0})).status==FrameStatus::terminal,"terminal no records");
    l.max_records=1;l.max_stream_bytes=3;auto s=make(l);r=s.feed(bytes({0,2,1,2}));
    check(r.error.code==Code::stream_limit && r.consumed==3 && s.position().value()==3,"stream cap");
    auto o=make({},ByteOffset{UINT64_MAX-1});r=o.feed(bytes({0,1}));
    check(r.error.code==Code::offset_overflow && r.consumed==1,"offset overflow");
    auto q=make({},ByteOffset{},RecordOrdinal{UINT64_MAX});r=q.feed(bytes({0,1,9}));
    check(r.frame && r.frame->location.ordinal.value()==UINT64_MAX,"last ordinal valid");
    check(q.feed(bytes({0,1})).error.code==Code::ordinal_overflow,"ordinal overflow");
    auto qt=make({},ByteOffset{},RecordOrdinal{UINT64_MAX});qt.feed(bytes({0,1,9}));check(qt.feed(bytes({0,0})).status==FrameStatus::terminal,"ordinal terminal");
    auto exact=make({3,3,1,2});check(exact.feed(bytes({0,0})).status==FrameStatus::terminal && !exact.finish().error,"stream exact cap");
    auto zero=make({3,3,1,0});check(zero.feed(bytes({0})).error.code==Code::stream_limit,"zero stream budget");
    l.buffer_bytes=2;check(!BinaryFileFramer::create(l),"invalid buffer");
    l.buffer_bytes=65536;check(!BinaryFileFramer::create(l),"oversized buffer");
}
void allocation() {
    gig::TrackedResource resource;
    {
        auto r=BinaryFileFramer::create({},ByteOffset{},RecordOrdinal{},&resource);check(bool(r),"pmr create");
        const auto stats=resource.stats();check(stats.allocations==1 && stats.live_bytes==65535,"bounded allocation");
        const auto input=bytes({0,1,7,0,0});for(auto b:input) r.data->feed({&b,1});r.data->finish();
        check(resource.stats()==stats,"no incremental allocation");
        auto moved=std::move(*r.data);check(r.data->feed({}).error.code==Code::invalid_config,"moved-from safety");
        check(moved.terminated() && r.data->allocated_payload_bytes()==0,"move preserves state");
        auto err=BinaryFileFramer::create({},ByteOffset{},RecordOrdinal{},&resource);
        const auto before=resource.stats();err.data->feed(bytes({0,1,8,0,0}));err.data->feed(bytes({1}));err.data->finish();
        check(resource.stats()==before,"errors allocate nothing");
    }
    check(resource.stats().live_bytes==0 && resource.stats().deallocations==2,"buffer released");
    resource.fail_after(0);auto fail=BinaryFileFramer::create({},ByteOffset{},RecordOrdinal{},&resource);
    check(!fail && fail.error.code==Code::resource_exhausted,"allocation failure typed");
    check(!BinaryFileFramer::create({},ByteOffset{},RecordOrdinal{},nullptr),"null resource");
}
void properties() {
    // Fixed LCG; no unspecified argument evaluation and no external data.
    std::uint64_t seed=0x12345;auto next=[&](){seed=seed*6364136223846793005ULL+1;return seed;};
    for(unsigned trial=0;trial<10000;++trial) {
        const auto len=static_cast<std::size_t>(next()%64+1);std::vector<std::byte> input{std::byte{0},static_cast<std::byte>(len)};
        for(std::size_t i=0;i<len;++i)input.push_back(static_cast<std::byte>(next()&255));
        input.push_back(std::byte{0});input.push_back(std::byte{0});
        auto f=make();std::size_t at=0,seen=0;
        while(at<input.size()) {
            auto n=std::min<std::size_t>(static_cast<std::size_t>(next()%13+1),input.size()-at);
            auto r=f.feed(std::span(input).subspan(at,n));check(!r.error && r.consumed>0,"property progress");at+=r.consumed;
            if(r.frame){++seen;check(r.frame->payload.size()==len,"property len");for(std::size_t i=0;i<len;++i)check(r.frame->payload[i]==input[i+2],"property bytes");}
        }
        check(seen==1 && f.finish().session_complete,"property terminal");
    }
}
}
int main(int argc,char** argv) {
    try {const std::string_view name=argc>1?argv[1]:"all";
        if(name=="all"||name=="basic"){basic();golden();}
        if(name=="all"||name=="errors")errors();
        if(name=="all"||name=="limits")limits();
        if(name=="all"||name=="allocation")allocation();
        if(name=="all"||name=="properties")properties();
        std::cout<<"BinaryFile "<<name<<" passed\n";return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
