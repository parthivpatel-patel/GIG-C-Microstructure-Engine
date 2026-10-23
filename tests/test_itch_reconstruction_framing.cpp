#include "support/itch_reconstruction_fixture.hpp"
#include "gig/itch/binary_file.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <iostream>

namespace {
using namespace gig::itch;
using namespace gig::itch::test;
using Bytes=std::vector<std::byte>;
struct Fixture {Bytes bytes;std::vector<std::size_t> ends;};
Fixture fixture(){
    // Authored source trace. All expected states below are literal arithmetic,
    // not a canonical result obtained from another production run.
    std::vector<Bytes> messages{system(),directory(),directory(2,"TWO     "),add(101,10),add(201,20,200,2,'S'),add(102,20),reduce('E',102,4,1),reduce('X',101,3),reduce('D',101),replace(102,103,15),trade(2),cross(3),broken(2)};
    for(char code:std::string_view{"SQMEC"})messages.push_back(system(code));
    Fixture out;
    for(const auto& message:messages){out.bytes.push_back(static_cast<std::byte>((message.size()>>8)&255));out.bytes.push_back(static_cast<std::byte>(message.size()&255));out.bytes.insert(out.bytes.end(),message.begin(),message.end());out.ends.push_back(out.bytes.size());}
    out.bytes.push_back(std::byte{});out.bytes.push_back(std::byte{});return out;
}
void prefix_truth(const SyntheticReconstructor& r,std::size_t n){
    check(r.context().summary().accepted_records==n&&r.receipts().size()==n,"all complete source frames accounted exactly once");
    const auto& a=r.engine(0)->book();const auto& b=r.engine(1)->book();
    const auto first=a.find(number<gig::OrderId>(101));const auto second=a.find(number<gig::OrderId>(102));const auto third=a.find(number<gig::OrderId>(103));
    check(first.has_value()==(n>=4&&n<9),"literal head identity by accepted boundary");
    if(first)check(first->order.quantity.value()==(n>=8?7U:10U)&&first->priority==0,"literal head quantity and priority");
    check(second.has_value()==(n>=6&&n<10),"literal second identity by accepted boundary");
    if(second)check(second->order.quantity.value()==(n>=7?16U:20U)&&second->priority==1,"identified second execution and priority");
    check(third.has_value()==(n>=10),"literal replacement identity");
    if(third)check(third->order.quantity.value()==15&&third->order.price_ticks.value()==101&&third->priority==2,"literal replacement state and lost priority");
    const std::uint64_t mutations=(n>=4?1U:0U)+(n>=6?1U:0U)+(n>=7?1U:0U)+(n>=8?1U:0U)+(n>=9?1U:0U)+(n>=10?1U:0U);
    check(a.revision()==mutations&&r.engine(0)->journal_size()==mutations,"literal per-book native prefix");
    check(a.order_count()==static_cast<std::size_t>(first.has_value())+static_cast<std::size_t>(second.has_value())+static_cast<std::size_t>(third.has_value()),"no extra native identity");
    const auto other=b.find(number<gig::OrderId>(201));check(other.has_value()==(n>=5),"second symbol isolated");
    if(other)check(other->order.side==gig::Side::sell&&other->order.price_ticks.value()==200&&other->order.quantity.value()==20&&other->priority==0,"literal second-symbol state");
    check(b.order_count()==(n>=5?1U:0U)&&b.revision()==(n>=5?1U:0U),"second book prefix");
    if(n>=10)check(a.ledger()==gig::QuantityLedger{30,10,4,0,0,15,16,45,30},"hand-derived complete six-step ledger");
    check(!a.check_invariants()&&!b.check_invariants(),"native invariants after each frame");
}
struct RunResult {Code framing_error;std::uint64_t accepted;bool container_complete,input_complete;};
RunResult run(const Fixture& f,std::size_t cut,std::size_t chunk,std::optional<std::size_t> split,EndKind end,bool trailing=false){
    gig::TrackedResource memory(std::pmr::get_default_resource(),128*1024*1024);
    RunResult result{};
    {
        auto reconstruction=reconstructor(config(),&memory);auto created=BinaryFileFramer::create({},ByteOffset{},RecordOrdinal{},&memory);check(bool(created),"framer creation");auto& framer=*created.data;
        std::size_t read=0;bool failed=false;
        while(read<cut&&!failed){const auto boundary=split&&read<*split?*split:cut;const auto count=std::min({chunk,cut-read,boundary-read});check(count>0,"bounded fragmented read progresses");const auto input=std::span<const std::byte>{f.bytes}.subspan(read,count);std::size_t used=0;
            while(used<input.size()){
                const auto decoded=framer.feed(input.subspan(used));used+=decoded.consumed;
                if(decoded.status==FrameStatus::error){result.framing_error=decoded.error.code;failed=true;break;}
                if(decoded.frame){const auto step=reconstruction.process(decoded.frame->payload,decoded.frame->location,config().source.provenance);check(step.committed,"complete authored frame accepted");prefix_truth(reconstruction,reconstruction.context().summary().accepted_records);}
                check(decoded.consumed>0||decoded.status==FrameStatus::error,"framer loop makes progress");
            }
            read+=used;
        }
        if(trailing){const std::array<std::byte,1> extra{std::byte{0xff}};const auto error=framer.feed(extra);check(error.status==FrameStatus::error&&error.error.code==Code::trailing_after_terminator,"terminal does not silently skip trailing bytes");result.framing_error=error.error.code;}
        const auto finish=framer.finish(end);if(finish.error)result.framing_error=finish.error.code;result.container_complete=finish.session_complete;
        const auto summary=reconstruction.finish(finish.session_complete?ContextEnd::declared_source_complete:end==EndKind::bounded_prefix?ContextEnd::bounded_prefix:ContextEnd::unexpected_eof);result.input_complete=summary.input_complete;
        result.accepted=reconstruction.context().summary().accepted_records;
        const auto expected=static_cast<std::uint64_t>(std::count_if(f.ends.begin(),f.ends.end(),[cut](auto n){return n<=cut;}));check(result.accepted==expected,"interior cuts publish only complete frames");
        prefix_truth(reconstruction,static_cast<std::size_t>(result.accepted));
    }
    check(memory.stats().live_bytes==0,"framer/context/books/receipts destruction releases memory");return result;
}
void framing(){
    const auto f=fixture();std::size_t schedules=0;
    for(std::size_t chunk=1;chunk<=f.bytes.size();++chunk){const auto result=run(f,f.bytes.size(),chunk,std::nullopt,EndKind::source_eof);check(result.framing_error==Code::none&&result.container_complete&&result.input_complete,"all chunk sizes yield complete source");++schedules;}
    for(std::size_t split=1;split<f.bytes.size();++split){const auto result=run(f,f.bytes.size(),f.bytes.size(),split,EndKind::source_eof);check(result.framing_error==Code::none&&result.accepted==f.ends.size(),"all two-part splits yield same accepted source");++schedules;}
    for(std::size_t cut=0;cut<f.bytes.size();++cut){const auto bounded=run(f,cut,7,std::nullopt,EndKind::bounded_prefix);check(bounded.framing_error==Code::none&&!bounded.container_complete&&!bounded.input_complete,"bounded cutoff explicitly incomplete, not malformed EOF");const auto eof=run(f,cut,7,std::nullopt,EndKind::source_eof);check(eof.framing_error!=Code::none&&!eof.container_complete&&!eof.input_complete,"EOF at every interior byte rejects truncation or absent terminator");check(eof.accepted==bounded.accepted,"bounded versus EOF accepted prefix identical");schedules+=2;}
    const auto tail=run(f,f.bytes.size(),3,std::nullopt,EndKind::source_eof,true);check(tail.framing_error==Code::trailing_after_terminator&&!tail.input_complete,"trailing input prevents complete publication");
    std::cout<<"framing source_bytes="<<f.bytes.size()<<" source_records="<<f.ends.size()<<" fragment_cut_schedules="<<schedules<<" trailing_controls=1\n";
}
void recovery_boundary(){
    // Native recovery is independently checked at its actual fixed bound. This
    // positive native snapshot does NOT confer a complete P1F context seed.
    Harness h;h.setup();h.accept(add(999));const auto metadata=*h.book().last_metadata();const gig::BookSession session{metadata.scope.data->session,metadata.scope.data->epoch};
    auto created=gig::OrderBook::create(h.book().rules(),session,{128,128,128});check(bool(created),"native recovery test book");auto& book=*created.data;
    gig::Snapshot snapshot{gig::SnapshotKind::order_level,gig::SnapshotCoverage::complete,0,{},{},{}};
    check(!snapshot.boundaries.append({*metadata.scope.data,*metadata.sequence.data,0,1}),"native source boundary");
    for(std::uint64_t i=0;i<64;++i)check(!snapshot.orders.append({{number<gig::OrderId>(i+1),gig::Side::buy,number<gig::PriceTicks>(100),number<gig::QuantityLots>(1)},i}),"append first64 complete orders");
    check(!book.recover({metadata,snapshot},session),"complete64 native snapshot accepted");check(book.order_count()==64&&book.remaining()==64&&book.ledger().recovered==64,"literal64-order recovery totals");
    for(std::uint64_t i=0;i<64;++i){const auto found=book.find(number<gig::OrderId>(i+1));check(found&&found->priority==i&&found->order.quantity.value()==1,"complete64 identities and FIFO ranks");}
    const auto before=book.canonical();check(bool(before),"recovery baseline canonical");
    const auto over=snapshot.orders.append({{number<gig::OrderId>(65),gig::Side::buy,number<gig::PriceTicks>(100),number<gig::QuantityLots>(1)},64});check(over.code==gig::ErrorCode::capacity&&snapshot.orders.count==64,"65th append rejects without truncating or changing64");
    auto malformed=snapshot;malformed.orders.count=65;check(book.recover({metadata,malformed},session).code==gig::ErrorCode::capacity,"claimed65 complete snapshot rejected atomically");
    auto aggregate=snapshot;aggregate.kind=gig::SnapshotKind::aggregated;check(bool(book.recover({metadata,aggregate},session)),"aggregate cannot establish native L3 seed");
    auto bounded=snapshot;bounded.coverage=gig::SnapshotCoverage::bounded_depth;check(bool(book.recover({metadata,bounded},session)),"bounded depth cannot establish native L3 seed");
    const auto after=book.canonical();check(after&&*before.data==*after.data,"all invalid recoveries preserve native64 state");
    auto unsupported=config();unsupported.initialization.kind=InitialStateKind::complete_seed;check(!SyntheticReconstructor::create(unsupported),"complete native snapshot is not complete global source context");
    std::cout<<"native_snapshot_exact64=passed over65=atomic_rejection adapter_complete_seed=unsupported\n";
}
}
int main(int argc,char** argv){try{const std::string_view group=argc>1?argv[1]:"all";if(group=="all"||group=="framing")framing();if(group=="all"||group=="recovery_boundary")recovery_boundary();return 0;}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
