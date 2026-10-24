#include <iostream>
#include <map>
#include <stdexcept>
#include "gig/memory/tracked_resource.hpp"
#include "fixtures/synthetic/replay_events.hpp"
using namespace gig;using namespace gig::fixtures;
namespace {
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
ReplayEngine engine(std::pmr::memory_resource* r){auto c=replay_config();c.max_journal_records=2048;return take(ReplayEngine::create(rules(),c,{},r));}
void trace(bool emit){
 TrackedResource r;
 {
 auto e=engine(&r);std::map<std::uint64_t,std::uint64_t> expected;std::uint64_t seq=0,epoch=0;
 for(std::size_t i=0;i<128;++i){
  const auto current=epoch?BookSession{text("phase5-trace"),epoch}:book_session();
  if(i%17==16){const BookSession next{text("phase5-trace"),epoch+1};must(e.reset(replay_event(BookReset{ResetReason::manual,epoch+1},seq,i,1,current),restart_plan(1,next)));++epoch;seq=0;expected.clear();}
  else if(i%23==22){must(e.recover(replay_recovery(1,seq,i,current)));++seq;expected={{7,20},{8,10}};}
  else if(i%3==0){const auto id=1000+i;must(e.apply(replay_event(add(id,Side::buy,100,10),seq,i,1,current)));expected.emplace(id,10);++seq;}
  else {auto observation=replay_event(SessionEvent{SessionAction::halt,Available<Identity>::known(text("audit;:"))},seq,i,1,current);observation.metadata.provenance.generator_seed=Available<std::uint64_t>::known(9000+i);must(e.apply(observation));++seq;}
  std::uint64_t qty=0;for(const auto& [id,q]:expected){qty+=q;const auto order=e.book().find(number<OrderId>(id));require(order&&order->order.quantity.value()==q,"independent identity/quantity");}
  require(e.book().order_count()==expected.size()&&e.book().remaining()==qty,"independent model totals");
  require(e.journal_size()==i+1&&!e.needs_recovery(),"independent source count");
  require(e.cursor(number<StreamId>(1))->expected.value()==seq,"independent sequence");
  if(emit)std::cout<<state(e)<<'\n';
 }
 }
 require(r.stats().live_bytes==0&&r.stats().live_blocks==0,"trace cleanup");
}
void failures(){
 std::size_t count=0;
 for(std::size_t prefix: {std::size_t{0},std::size_t{1},std::size_t{2},std::size_t{3},std::size_t{4},std::size_t{8}}){
  bool done=false;
  for(std::size_t site=0;site<64&&!done;++site){TrackedResource r;
   {auto e=engine(&r);std::uint64_t epoch=0;
    for(std::size_t i=0;i<prefix;++i){const auto current=epoch?BookSession{text("fault-session"),epoch}:book_session();const BookSession next{text("fault-session"),epoch+1};must(e.reset(replay_event(BookReset{ResetReason::manual,epoch+1},0,i,1,current),restart_plan(1,next)));++epoch;}
    const auto current=epoch?BookSession{text("fault-session"),epoch}:book_session();const BookSession next{text("fault-session"),epoch+1};auto event=replay_event(BookReset{ResetReason::manual,epoch+1},0,prefix,1,current);auto plan=restart_plan(1,next);const auto before=state(e);
    r.fail_after(site);auto error=e.reset(event,plan);r.disable_failure();
    if(error){require(error.code==ErrorCode::resource_exhausted&&state(e)==before,"joint journal/reset failure atomicity");++count;must(e.reset(event,plan));}
    else done=true;
    require(e.journal_size()==prefix+1&&e.book().session()==next&&!e.needs_recovery(),"exactly once after retry");
    auto moved=std::move(e);require(moved.journal_size()==prefix+1&&state(moved).find("gig.replay.v1;")==0,"moved restart ownership");
   }require(r.stats().live_bytes==0&&r.stats().live_blocks==0,"fault cleanup");
  }require(done,"all fault sites exhausted");
 }
 std::cout<<"reset allocation failure sites="<<count<<'\n';
}
}
int main(int argc,char** argv){try{if(argc!=2)return 2;const std::string_view mode(argv[1]);if(mode=="emit")trace(true);else if(mode=="model")trace(false);else if(mode=="allocation")failures();else return 2;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
