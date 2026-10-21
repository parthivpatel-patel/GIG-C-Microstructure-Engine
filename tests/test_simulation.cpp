#include <iostream>
#include "fixtures/synthetic/simulation.hpp"
#include "gig/memory/tracked_resource.hpp"
using namespace gig;using namespace gig::fixtures;using namespace gig::simulation;
namespace {
std::size_t checks=0;
void check(bool x){++checks;if(!x)throw std::runtime_error("simulation assertion #"+std::to_string(checks));}
void basic(){
    auto e=take(Simulator::create(sim_config()));must(e.submit_at(sim_time(0),sim_order(1,Side::sell,100,10)));must(e.submit_at(sim_time(0),sim_order(2,Side::sell,100,20)));must(e.advance_to(sim_time(0)));
    check(e.exchange_queue_position(number<OrderId>(2))==QueuePosition{1,10});
    must(e.submit_at(sim_time(0),sim_order(3,Side::buy,101,15)));must(e.advance_to(sim_time(0)));
    check(e.exchange_fills().size()==2 && e.exchange_fills()[0].maker.value()==1 && e.exchange_fills()[0].quantity.value()==10 && e.exchange_fills()[1].maker.value()==2 && e.exchange_fills()[1].quantity.value()==5);
    check(e.exchange_orders().size()==1 && e.exchange_orders()[0].order.quantity.value()==15 && e.exchange_queue_position(number<OrderId>(2))==QueuePosition{0,0});
    check(e.exchange_fills()[0].price.value()==100 && e.exchange_fills()[0].run_id==e.config().run_id && e.exchange_fills()[0].seed==1729);
    must(e.cancel_at(sim_time(0),number<OrderId>(2)));must(e.advance_to(sim_time(0)));check(e.exchange_orders().empty() && e.conservation()==Conservation{45,30,15,0,0});check(!e.check_invariants());
}
void reports(){
    auto c=sim_config();c.acknowledgment.base=number<Duration>(7);c.execution.base=number<Duration>(5);
    auto e=take(Simulator::create(c));
    must(e.submit_at(sim_time(0),sim_order(1,Side::sell,100,10)));
    must(e.submit_at(sim_time(0),sim_order(2,Side::sell,100,20)));
    must(e.submit_at(sim_time(0),sim_order(3,Side::buy,101,15,TimeInForce::ioc)));
    must(e.advance_to(sim_time(0)));check(e.exchange_fills().size()==2 && e.client_reports().empty());
    must(e.advance_to(sim_time(4)));check(e.client_reports().empty());
    must(e.advance_to(sim_time(5)));
    std::array<std::uint64_t,4> filled{};
    for(const auto& r:e.client_reports()){
        check(r.kind==ReportKind::fill && r.fill_index && r.delivered_at==sim_time(5));
        const auto& f=e.exchange_fills()[*r.fill_index];
        check((r.order==f.maker || r.order==f.taker) && r.quantity==f.quantity && f.reported_at==r.delivered_at);
        filled[static_cast<std::size_t>(r.order.value())]+=r.quantity.value();
    }
    check(filled[1]==10 && filled[2]==5 && filled[3]==15);
    // Both sides are delivered before ACK; later cancellation removes only residual maker quantity.
    must(e.cancel_at(sim_time(5),number<OrderId>(2)));must(e.advance_to(sim_time(20)));
    std::array<std::int64_t,4> remaining{};
    for(const auto& r:e.client_reports()){
        const auto id=static_cast<std::size_t>(r.order.value());
        if(r.kind==ReportKind::accepted)remaining[id]+=static_cast<std::int64_t>(r.quantity.value());
        if(r.kind==ReportKind::fill || r.kind==ReportKind::cancelled || r.kind==ReportKind::expired)remaining[id]-=static_cast<std::int64_t>(r.quantity.value());
    }
    check(remaining[1]==0 && remaining[2]==0 && remaining[3]==0 && e.exchange_orders().empty());
    // The second counterparty report must participate in atomic queue/report capacity checks.
    for(bool queued:{true,false}){
        auto limited=sim_config();if(queued)limited.max_events=2;else limited.max_reports=3;
        auto model=take(Simulator::create(limited));must(model.submit_at(sim_time(0),sim_order(1,Side::sell,100,10)));must(model.advance_to(sim_time(0)));
        must(model.submit_at(sim_time(0),sim_order(2,Side::buy,100,10)));const auto before=sim_state(model);
        check(model.advance_to(sim_time(0)).code==ErrorCode::capacity && sim_state(model)==before && !model.check_invariants());
    }
}
void tif(){
    auto e=take(Simulator::create(sim_config()));must(e.submit_at(sim_time(0),sim_order(1,Side::sell,100,10)));must(e.advance_to(sim_time(0)));
    must(e.submit_at(sim_time(0),sim_order(2,Side::buy,100,11,TimeInForce::fok)));must(e.advance_to(sim_time(0)));check(e.exchange_fills().empty() && e.conservation().rejected==11);
    must(e.submit_at(sim_time(0),sim_order(3,Side::buy,101,2,TimeInForce::gtc,true)));must(e.advance_to(sim_time(0)));check(e.exchange_fills().empty() && e.conservation().rejected==13);
    must(e.submit_at(sim_time(0),sim_order(4,Side::buy,100,15,TimeInForce::ioc)));must(e.advance_to(sim_time(0)));check(e.exchange_fills().size()==1 && e.conservation().expired==5 && e.exchange_orders().empty());
    auto bad=sim_order(5,Side::buy,100,1);bad.tif=static_cast<TimeInForce>(255);auto before=sim_state(e);check(e.submit_at(sim_time(0),bad).code==ErrorCode::invalid_enum && sim_state(e)==before);
    bad=sim_order(5,Side::buy,100,1);bad.side=static_cast<Side>(255);check(e.submit_at(sim_time(0),bad).code==ErrorCode::invalid_enum);
    check(e.submit_at(sim_time(0),sim_order(1,Side::buy,100,1)).code==ErrorCode::duplicate);
    check(bool(e.submit_at(sim_time(0),sim_order(5,Side::buy,100,0))));
    auto full=take(Simulator::create(sim_config()));must(full.submit_at(sim_time(0),sim_order(1,Side::sell,99,2)));must(full.submit_at(sim_time(0),sim_order(2,Side::sell,100,3)));must(full.submit_at(sim_time(0),sim_order(3,Side::buy,100,5,TimeInForce::fok)));must(full.advance_to(sim_time(0)));check(full.exchange_orders().empty() && full.exchange_fills().size()==2);
}
void latency(){
    auto c=sim_config();c.arrival.base=number<Duration>(5);c.acknowledgment.base=number<Duration>(2);c.execution.base=number<Duration>(7);
    auto e=take(Simulator::create(c));must(e.submit_at(sim_time(0),sim_order(1,Side::sell,100,10)));must(e.cancel_at(sim_time(1),number<OrderId>(1)));must(e.advance_to(sim_time(4)));
    check(e.exchange_orders().empty() && e.client_reports().size()==1 && e.client_reports()[0].kind==ReportKind::cancel_rejected);
    must(e.advance_to(sim_time(5)));check(e.exchange_orders().size()==1 && e.client_reports().size()==1);must(e.advance_to(sim_time(7)));check(e.client_reports().back().kind==ReportKind::accepted);
    must(e.submit_at(sim_time(7),sim_order(2,Side::buy,100,10)));must(e.advance_to(sim_time(12)));check(e.exchange_fills().size()==1 && e.client_reports().size()==2);
    must(e.cancel_at(sim_time(13),number<OrderId>(1)));must(e.advance_to(sim_time(18)));for(const auto& r:e.client_reports())check(r.kind!=ReportKind::fill);
    must(e.advance_to(sim_time(19)));check(e.client_reports().back().kind==ReportKind::fill && e.exchange_fills()[0].reported_at==sim_time(19));
    auto before=sim_state(e);check(e.advance_to(sim_time(18)).code==ErrorCode::ordering_error && sim_state(e)==before);
    c=sim_config();c.arrival.jitter=number<Duration>(10);c.cancel.jitter=number<Duration>(5);c.acknowledgment.jitter=number<Duration>(10);c.execution.jitter=number<Duration>(10);
    auto a=take(Simulator::create(c)),b=take(Simulator::create(c));for(auto* s:{&a,&b}){for(std::uint64_t i=1;i<=20;++i)must(s->submit_at(sim_time(0),sim_order(i,i%2?Side::sell:Side::buy,100,2)));must(s->advance_to(sim_time(100)));}
    check(sim_state(a)==sim_state(b));c.seed=42;auto different=take(Simulator::create(c));check(sim_state(different)!=sim_state(a));
    c=sim_config();c.arrival.base=number<Duration>(1);auto near_end=take(Simulator::create(c));before=sim_state(near_end);check(near_end.submit_at(sim_time(INT64_MAX),sim_order(1,Side::buy,100,1)).code==ErrorCode::overflow && sim_state(near_end)==before);
}
void faults(){
    std::size_t reached=0;
    for(std::size_t n=0;n<100;++n){TrackedResource memory;{
        auto c=sim_config();c.arrival.base=number<Duration>(10);auto e=take(Simulator::create(c,&memory));must(e.submit_at(sim_time(0),sim_order(1,Side::sell,100,5)));must(e.submit_at(sim_time(0),sim_order(2,Side::sell,100,5)));must(e.advance_to(sim_time(10)));must(e.submit_at(sim_time(10),sim_order(3,Side::buy,100,10)));
        const auto before=sim_state(e);const auto live=memory.stats().live_bytes;memory.fail_after(n);auto error=e.advance_to(sim_time(20));memory.disable_failure();
        if(!error){check(e.exchange_fills().size()==2 && !e.check_invariants());reached=n;break;}
        check(error.code==ErrorCode::resource_exhausted && sim_state(e)==before && !e.check_invariants() && memory.stats().live_bytes==live);
        memory.fail_after(0);check(!e.canonical());memory.disable_failure();check(sim_state(e)==before);
    }check(memory.stats().live_bytes==0);}
    check(reached>5);
    std::size_t additional=0;
    for(int operation=0;operation<2;++operation){bool completed=false;for(std::size_t n=0;n<100 && !completed;++n){TrackedResource memory;{
        auto e=take(Simulator::create(sim_config(),&memory));must(e.submit_at(sim_time(0),sim_order(1,Side::sell,100,10)));must(e.advance_to(sim_time(0)));auto before=sim_state(e);auto live=memory.stats().live_bytes;
        memory.fail_after(n);auto error=operation==0?e.submit_at(sim_time(0),sim_order(2,Side::buy,100,5)):e.cancel_at(sim_time(0),number<OrderId>(1));memory.disable_failure();
        if(!error){completed=true;additional+=n;}else check(error.code==ErrorCode::resource_exhausted && sim_state(e)==before && !e.check_invariants() && memory.stats().live_bytes==live);
    }check(memory.stats().live_bytes==0);}check(completed);}
    std::cout<<"real allocation failure positions="<<reached+additional<<'\n';
    auto c=sim_config();c.max_events=1;auto e=take(Simulator::create(c));must(e.submit_at(sim_time(0),sim_order(1,Side::sell,100,1)));must(e.advance_to(sim_time(0)));must(e.submit_at(sim_time(0),sim_order(2,Side::buy,100,1)));auto before=sim_state(e);check(e.advance_to(sim_time(0)).code==ErrorCode::capacity && sim_state(e)==before);
    c=sim_config();auto huge=take(Simulator::create(c));must(huge.submit_at(sim_time(0),sim_order(1,Side::buy,100,UINT64_MAX)));before=sim_state(huge);check(huge.submit_at(sim_time(0),sim_order(2,Side::buy,100,1)).code==ErrorCode::overflow && sim_state(huge)==before);
    c.seed=0;check(!Simulator::create(c));check(!Simulator::create(sim_config(),nullptr));
}
}
int main(int argc,char** argv){try{
    if(argc==2 && std::string_view(argv[1])=="reference"){
        auto e=take(Simulator::create(sim_config()));std::uint64_t id{},q{};int side{},tif{},post{};std::int64_t price{};
        char operation{};
        while(std::cin>>operation){
            if(operation=='S'){if(!(std::cin>>id>>side>>price>>q>>tif>>post))return 1;must(e.submit_at(sim_time(0),sim_order(id,side==0?Side::buy:Side::sell,price,q,static_cast<TimeInForce>(tif),post!=0)));}
            else if(operation=='C'){if(!(std::cin>>id))return 1;must(e.cancel_at(sim_time(0),number<OrderId>(id)));}else return 1;
            must(e.advance_to(sim_time(0)));check(!e.check_invariants());
            std::cout<<e.exchange_orders().size();for(const auto& o:e.exchange_orders())std::cout<<' '<<o.order.id.value()<<':'<<static_cast<int>(o.order.side)<<':'<<o.order.limit.value()<<':'<<o.order.quantity.value()<<':'<<o.priority;
            std::cout<<" |";for(const auto& f:e.exchange_fills())std::cout<<' '<<f.maker.value()<<':'<<f.taker.value()<<':'<<f.price.value()<<':'<<f.quantity.value();auto l=e.conservation();std::cout<<" | "<<l.submitted<<':'<<l.executed_sides<<':'<<l.cancelled<<':'<<l.expired<<':'<<l.rejected<<" |";
            for(const auto& r:e.client_reports())std::cout<<' '<<r.order.value()<<':'<<static_cast<unsigned>(r.kind)<<':'<<static_cast<unsigned>(r.reason)<<':'<<r.quantity.value()<<':'<<(r.fill_index?std::to_string(*r.fill_index):"-");
            std::cout<<'\n';
        }return 0;
    }
    std::string_view group=argc==2?argv[1]:"basic";if(group=="basic")basic();else if(group=="reports")reports();else if(group=="tif")tif();else if(group=="latency")latency();else if(group=="faults")faults();else return 1;
    std::cout<<"PASS: "<<group<<", "<<checks<<" checks\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
