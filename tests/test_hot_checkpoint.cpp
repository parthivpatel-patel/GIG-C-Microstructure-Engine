#include <iostream>
#include "gig/memory/tracked_resource.hpp"
#include "fixtures/synthetic/replay_events.hpp"
using namespace gig;using namespace gig::fixtures;
namespace {std::size_t checks=0,failures=0;void check(bool ok,const char* label){++checks;if(!ok){++failures;std::cerr<<"FAIL "<<label<<'\n';}}}
int main(){try{
 auto config=replay_config();const BookLimits limits{128,32,20};
 auto original=take(ReplayEngine::create(rules(),config,limits));
 canonical_workflow(original);const auto expected=state(original);auto image=take(original.checkpoint());
 auto restored=ReplayEngine::restore(image,rules(),config,limits,expected);check(bool(restored),"healthy full state restored after reset/recovery");
 if(restored){check(state(*restored.data)==expected,"identical journal,FIFO,ledger,cursors and canonical");check(!restored.data->book().check_invariants(),"restored invariants");
  auto next=replay_event(add(99),1,11,1,{text("next-session"),1});must(original.apply(next));must(restored.data->apply(next));check(state(original)==state(*restored.data),"same suffix after hot restoration");
  const auto duplicate=restored.data->apply(next);check(duplicate.code==ErrorCode::sequence_duplicate&&restored.data->needs_recovery(),"duplicates preserve strict stop");check(!restored.data->checkpoint(),"unhealthy image cannot become eligible");
 }
 auto bad=take(ReplayEngine::create(rules(),config,limits));must(bad.apply(replay_event(add(1),0,0)));must(bad.apply(replay_event(add(2),1,1)));auto clean=take(bad.checkpoint());const auto canonical=state(bad);
 ++clean.book.ledger.added;check(!ReplayEngine::restore(clean,rules(),config,limits,canonical),"corrupt ledger rejected");--clean.book.ledger.added;
 clean.book.orders[1].priority=clean.book.orders[0].priority;check(!ReplayEngine::restore(clean,rules(),config,limits,canonical),"corrupt FIFO rejected");clean=take(bad.checkpoint());
 clean.cursors.items[0]->expected=number<SequenceNumber>(99);check(!ReplayEngine::restore(clean,rules(),config,limits,canonical),"cursor mismatch rejected");clean=take(bad.checkpoint());
 check(!ReplayEngine::restore(clean,rules(),config,limits,canonical+"x"),"trusted canonical mismatch rejected");
 auto other=config;other.run_id=text("another-run");check(!ReplayEngine::restore(clean,rules(),other,limits,canonical),"expected config bound");
 TrackedResource memory;bool succeeded=false;std::size_t failures_injected=0;
 for(std::size_t at=0;at<256;++at){memory.fail_after(at);auto candidate=ReplayEngine::restore(clean,rules(),config,limits,canonical,&memory);if(candidate){succeeded=true;break;}++failures_injected;check(candidate.error.code==ErrorCode::resource_exhausted,"actual allocation failure reported");check(state(bad)==canonical,"allocation rejection cannot change accepted owner");check(memory.stats().live_bytes==0,"isolated failed restore frees memory");}
 memory.disable_failure();check(succeeded&&failures_injected>10,"allocation sweep reaches complete restore");check(memory.stats().live_bytes==0,"restored candidate frees memory");
 for(std::size_t at=0;at<16;++at){memory.fail_after(at);auto copy=bad.checkpoint(&memory);check(state(bad)==canonical,"capture failure never mutates owner");if(!copy)check(copy.error.code==ErrorCode::resource_exhausted,"capture allocation error");}
 memory.disable_failure();check(memory.stats().live_bytes==0,"capture allocations released");
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}std::cout<<"checks="<<checks<<" failures="<<failures<<'\n';return failures?1:0;}
