#include "gig/market_data/aggregate_depth.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <array>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
using gig::market_data::Level;using gig::market_data::AggregateDepth;
namespace {
void check(bool ok,const char*s){if(!ok)throw std::runtime_error(s);}
template<std::size_t N,std::size_t M>gig::Error snapshot(AggregateDepth&b,const Level(&bid)[N],const Level(&ask)[M],std::optional<std::uint64_t>s={}){return b.snapshot(bid,ask,s);}
void tests(){
    AggregateDepth b(8);check(bool(b.update({},{})),"update before snapshot refused");
    const Level bid[]={{90,9},{100,30}},ask[]={{120,7},{101,10}};
    check(!snapshot(b,bid,ask,4),"snapshot accepted");check(b.bids()[0]==Level{100,30}&&b.asks()[0]==Level{101,10},"sorted exact levels");
    auto m=*b.metrics().data;check(m.midpoint->str()=="201/2"&&m.microprice->str()=="403/4","independent rational expected");check(m.bid_depth.str()=="39/1"&&m.ask_depth.str()=="17/1"&&m.depth_imbalance->str()=="11/28","independent depth expected");
    const Level remove[]={{100,0}},replace[]={{101,8}};check(!b.update(remove,replace,5),"delete/absolute replacement");check(b.bids().size()==1&&b.asks()[0].quantity==8,"no delta semantics");
    const auto before=b.revision();const auto qty=b.asks()[0].quantity;check(bool(b.update({},replace,7))&&b.revision()==before&&b.asks()[0].quantity==qty,"gap atomic");check(bool(b.update({},replace,5)),"duplicate sequence");check(bool(b.update({},replace)),"sequence presence cannot change");
    const Level duplicate[]={{99,1},{99,2}},invalid[]={{0,1}};check(bool(b.update(duplicate,{},6))&&b.revision()==before,"duplicate price atomic");check(bool(b.update(invalid,{},6))&&b.revision()==before,"invalid price atomic");
    AggregateDepth crossed;const Level cb[]={{102,1}},ca[]={{101,1}};check(!snapshot(crossed,cb,ca),"crossed observations retained");check(crossed.metrics().data->crossed&&crossed.metrics().data->spread->str()=="-1/1","cross diagnostic");check(!crossed.snapshot({},{}),"empty snapshot");check(!crossed.metrics().data->midpoint,"missing quote not invented");
    AggregateDepth maximum;const Level mb[]={{std::numeric_limits<std::int64_t>::max(),std::numeric_limits<std::uint64_t>::max()}},ma[]={{std::numeric_limits<std::int64_t>::max()-1,std::numeric_limits<std::uint64_t>::max()}};check(!snapshot(maximum,mb,ma),"large reduced weighted sum exact");check(maximum.metrics().data->microprice->str()=="18446744073709551613/2","large independent midpoint");const auto rev=maximum.revision();const Level overflowing[]={{std::numeric_limits<std::int64_t>::max()-1,std::numeric_limits<std::uint64_t>::max()-1}};check(bool(maximum.update({},overflowing)),"irreducible fraction capacity rejected");check(maximum.revision()==rev&&maximum.asks()[0].quantity==std::numeric_limits<std::uint64_t>::max(),"overflow update atomic");
    // Independent map oracle. The authored sequence avoids implementation sorting/metric code.
    AggregateDepth differential(64);check(!differential.snapshot({},{}),"oracle initialization");std::map<std::int64_t,std::uint64_t> bids,asks;
    for(std::uint64_t i=0;i<10000;++i){const auto price=static_cast<std::int64_t>(100+(i*17)%50);const auto q=i%7==0?0:i%37+1;const Level update[]={{price,q}};const bool bid_side=i%2==0;check(!differential.update(bid_side?std::span<const Level>(update):std::span<const Level>{},bid_side?std::span<const Level>{}:std::span<const Level>(update)),"oracle transition");auto& side=bid_side?bids:asks;if(q)side[price]=q;else side.erase(price);check(differential.bids().size()==bids.size()&&differential.asks().size()==asks.size(),"oracle counts");std::size_t at=0;for(auto it=bids.rbegin();it!=bids.rend();++it)check(differential.bids()[at++]==Level{it->first,it->second},"oracle bid level");at=0;for(auto [p,size]:asks)check(differential.asks()[at++]==Level{p,size},"oracle ask level");std::uint64_t bsum=0,asum=0;for(auto [p,size]:bids){(void)p;bsum+=size;}for(auto [p,size]:asks){(void)p;asum+=size;}const auto metrics=*differential.metrics().data;check(metrics.bid_depth==gig::exact::Fraction::whole(bsum)&&metrics.ask_depth==gig::exact::Fraction::whole(asum),"oracle quantity sums");}
    AggregateDepth full(2);const Level fb[]={{100,1},{99,1}},fa[]={{101,1}};check(!snapshot(full,fb,fa),"full initial");const Level fbup[]={{101,3},{99,0}};check(!full.update(fbup,{}),"delete before add at full capacity");check(full.bids()[0]==Level{101,3},"full absolute transaction");
    std::size_t failed=0,succeeded=0;
    for(std::size_t n=0;n<4;++n){gig::TrackedResource memory;{AggregateDepth atomic(8,&memory);check(!snapshot(atomic,bid,ask),"allocation initial");memory.fail_after(n);auto error=atomic.update(remove,replace);if(error){++failed;check(atomic.revision()==1&&atomic.bids().size()==2&&atomic.asks()[0].quantity==10,"allocation rollback");}else ++succeeded;memory.disable_failure();}check(memory.stats().live_bytes==0&&memory.stats().live_blocks==0,"allocation cleanup");}
    check(failed==2&&succeeded==2,"real allocation failure sweep");
    gig::TrackedResource tiny(std::pmr::get_default_resource(),1);AggregateDepth limited(8,&tiny);check(bool(snapshot(limited,bid,ask))&&limited.revision()==0,"budget bound");
    std::cout<<"aggregate-depth:10000 independent transitions;2 injected failures;2 successful sweeps;exact metrics/sequence/atomicity/budgets pass\n";
}
}
int main(){try{tests();return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
