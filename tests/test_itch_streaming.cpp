#include "gig/itch/streaming.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_gzip_fixture.hpp"
#include <iostream>
#include <string_view>

using namespace gig::itch;
namespace {
using namespace gig::itch::test;
using Bytes=std::vector<std::byte>;
Sha256Digest digest(std::string_view hex){check(hex.size()==64,"literal hash width");Sha256Digest out{};const auto nibble=[](char c)->unsigned{return c>='0'&&c<='9'?static_cast<unsigned>(c-'0'):static_cast<unsigned>(c-'a'+10);};for(std::size_t i=0;i<32;++i)out[i]=static_cast<std::byte>(nibble(hex[i*2])*16+nibble(hex[i*2+1]));return out;}
gig::Digest code_hash(){return *gig::Digest::make(std::string(64,'1')).data;}
struct Fixture {
    std::vector<Bytes> records;
    Bytes raw,compressed;
    StreamingConfig configuration;
    explicit Fixture(std::vector<Bytes> input=streaming_records(),bool terminal=true)
        :records(std::move(input)),raw(framed_records(records,terminal)),compressed(stored_gzip(raw)),configuration{config(),{},{},sha256(compressed)}{
        configuration.reconstruction.source.provenance.sha256=sha256(raw);
        const auto text=hex_digest(sha256(raw));configuration.reconstruction.initialization.fixture_sha256=*gig::Digest::make({text.data(),text.size()}).data;
        configuration.gzip.output_buffer_bytes=31;
    }
};
StreamingReconstructor pipeline(StreamingConfig c,std::pmr::memory_resource* resource=std::pmr::get_default_resource()){
    auto created=StreamingReconstructor::create(std::move(c),resource);check(bool(created),"streaming creation");return std::move(*created.data);
}
struct Pump {std::size_t consumed{};bool paused{};StreamingError error{};};
Pump pump(StreamingReconstructor& reader,std::span<const std::byte> bytes,std::size_t chunk){
    check(chunk>0,"positive compressed read size");Pump out;std::size_t calls=0;
    while(out.consumed<bytes.size()){
        const auto before=reader.summary();const auto next=reader.feed(bytes.subspan(out.consumed,std::min(chunk,bytes.size()-out.consumed)));
        check(next.consumed<=std::min(chunk,bytes.size()-out.consumed),"compressed consumed bound");out.consumed+=next.consumed;out.paused=next.paused;out.error=next.error;
        if(next.error||next.paused)return out;
        const auto after=reader.summary();check(next.consumed>0||after.decompressed_bytes!=before.decompressed_bytes||after.source_records!=before.source_records,"feed makes bounded progress");
        check(++calls<1000000,"finite feed loop");
    }
    // Also exercise the documented empty-input drain without inventing EOF.
    const auto drained=reader.feed({});out.paused=drained.paused;out.error=drained.error;return out;
}
void prefix_truth(const StreamingReconstructor& stream){
    const auto& r=stream.reconstruction();const auto n=r.context().summary().accepted_records;check(n<=18,"bounded literal prefix count");
    check(stream.summary().accepted_records==n&&r.receipts().size()==n,"pipeline/context/receipt accepted prefix agrees");
    check(stream.summary().source_records==r.summary().considered+(r.summary().unconsidered_record?1U:0U),"all complete physical frames accounted, including pending/rejected/cap+1");
    const auto& a=r.engine(0)->book();const auto& b=r.engine(1)->book();
    const auto first=a.find(number<gig::OrderId>(101)),second=a.find(number<gig::OrderId>(102)),third=a.find(number<gig::OrderId>(103)),other=b.find(number<gig::OrderId>(201));
    check(first.has_value()==(n>=4&&n<9),"literal101 active membership");if(first)check(first->order.quantity.value()==(n>=8?7U:10U)&&first->order.price_ticks.value()==100&&first->priority==0,"literal101 quantity/price/FIFO");
    check(second.has_value()==(n>=6&&n<10),"literal102 active membership");if(second)check(second->order.quantity.value()==(n>=7?16U:20U)&&second->order.price_ticks.value()==100&&second->priority==1,"literal102 nonhead execution and FIFO");
    check(third.has_value()==(n>=10),"literal103 replacement membership");if(third)check(third->order.quantity.value()==15&&third->order.price_ticks.value()==101&&third->priority==2,"literal103 replacement quantity/price/newpriority");
    check(other.has_value()==(n>=5),"literal second-symbol membership");if(other)check(other->order.quantity.value()==20&&other->order.price_ticks.value()==200&&other->order.side==gig::Side::sell&&other->priority==0,"literal second-symbol state");
    const std::uint64_t native_a=(n>=4?1U:0U)+(n>=6?1U:0U)+(n>=7?1U:0U)+(n>=8?1U:0U)+(n>=9?1U:0U)+(n>=10?1U:0U);
    const std::uint64_t native_b=n>=5?1U:0U;check(a.revision()==native_a&&r.engine(0)->journal_size()==native_a&&b.revision()==native_b&&r.engine(1)->journal_size()==native_b,"literal native journal/revision prefix");
    check(a.order_count()==static_cast<std::size_t>(first.has_value())+static_cast<std::size_t>(second.has_value())+static_cast<std::size_t>(third.has_value())&&b.order_count()==static_cast<std::size_t>(other.has_value()),"no extra native identities");
    check(r.summary().context_committed==r.summary().native_committed+r.summary().external_observations&&r.summary().considered==r.summary().context_committed+r.summary().rejected+(r.summary().pending?1U:0U),"disjoint source accounting");
    check(stream.summary().native_records==native_a+native_b&&stream.summary().external_observations==n-native_a-native_b,"pipeline source/native observation accounting");
    for(const auto& source:r.context().orders()){
        const auto* engine=r.engine(source.locate.value()==1?0:1);const auto native=engine->book().find(number<gig::OrderId>(source.reference.value()));
        check(native.has_value()==source.active,"source/native lifecycle agreement even after failure");if(native)check(native->order.quantity.value()==source.remaining.value()&&native->order.price_ticks.value()==source.resting_price.value(),"source/native exact resting state");
    }
    check(r.context().orders().size()==static_cast<std::size_t>(n>=4)+static_cast<std::size_t>(n>=5)+static_cast<std::size_t>(n>=6)+static_cast<std::size_t>(n>=10),"literal lifetime reference count");
    check(r.context().matches().size()==static_cast<std::size_t>(n>=7)+static_cast<std::size_t>(n>=11)+static_cast<std::size_t>(n>=12),"literal match count");
    if(n>=13)check(r.context().matches()[1].broken,"literal correction never restores book");
    if(n>=10)check(a.ledger()==gig::QuantityLedger{30,10,4,0,0,15,16,45,30},"independent literal final ledger");
    check(!a.check_invariants()&&!b.check_invariants(),"native invariants after streaming/failure");
    const auto records=streaming_records();std::uint64_t accepted_bytes=0;for(std::size_t i=0;i<static_cast<std::size_t>(n);++i)accepted_bytes+=records[i].size()+2;
    check(stream.summary().accepted_prefix_bytes==accepted_bytes,"exact complete-frame accepted bytes");
}
void complete_truth(StreamingReconstructor& reader,const Fixture& fixture){
    const auto end=reader.finish(EndKind::source_eof);check(!end.error&&end.source_complete&&end.publication_eligible,"complete validated source eligible");
    check(end.finished&&!end.bounded_prefix&&end.gzip_member_verified&&end.framer_terminated&&end.compressed_identity_verified&&end.decompressed_identity_verified,"independent completeness/integrity flags");
    check(end.compressed_bytes==fixture.compressed.size()&&end.decompressed_bytes==fixture.raw.size(),"exact complete input/output counts");
    check(end.compressed_sha256==fixture.configuration.compressed_sha256&&end.decompressed_sha256==*fixture.configuration.reconstruction.source.provenance.sha256,"actual identities match expected artifacts");
    check(end.source_records==18&&end.native_records==7&&end.external_observations==11,"literal final source accounting");prefix_truth(reader);
}
void basic(){
    Fixture f;check(f.raw.size()==507&&f.compressed.size()==530,"independent fixture lengths");
    check(sha256(f.raw)==digest("b0a3dfbda8636f10743ba71b082267aeaf52709a221e653e5d33d8d23feed2e5")&&sha256(f.compressed)==digest("73d9117e5adc97c2b506e2c129c02a7953bf2f7c3431f59371010248c07d8e20"),"independent Python hashlib fixture references");
    const std::string text="123456789";check(fixture_crc32(std::as_bytes(std::span{text.data(),text.size()}))==0xcbf43926U,"independent CRC known vector");
    auto reader=pipeline(f.configuration);check(!reader.summary().source_complete&&!reader.summary().publication_eligible,"no premature complete publication");
    check(!pump(reader,f.compressed,f.compressed.size()).error,"valid stored-block gzip");check(!reader.summary().source_complete,"EOF declaration required beyond trailer");complete_truth(reader,f);
    check(reader.summary().accepted_prefix_sha256==digest("8f6c0f588e049f6fe1ff443e44935621c93adedafd0904390dcd979ff3435991"),"independent accepted-prefix hash excludes BinaryFile terminator");
    const auto after=reader.feed({});check(after.error.code==StreamingCode::already_finished,"finished feed rejected");
    auto move_source=pipeline(f.configuration);auto moved=std::move(move_source);check(move_source.feed(f.compressed).error.code==StreamingCode::moved_from,"moved-from streaming safe");check(!pump(moved,f.compressed,13).error,"moved stream remains valid");complete_truth(moved,f);
    auto c=f.configuration;c.gzip.output_buffer_bytes=128;auto pause_source=pipeline(c);check(!pause_source.pause_after(4),"move test declared pause");const auto read=pump(pause_source,f.compressed,f.compressed.size());check(read.paused&&pause_source.summary().buffered_output_bytes>0,"move test has real owned output tail");auto checkpoint=pause_source.checkpoint(code_hash());check(bool(checkpoint),"move test checkpoint");auto moved_pause=std::move(pause_source);check(!moved_pause.verify_checkpoint(*checkpoint.data,code_hash()),"move preserves owned pending output and checkpoint");check(!moved_pause.resume()&&!pump(moved_pause,std::span<const std::byte>(f.compressed).subspan(read.consumed),19).error,"moved pause resumes exact source");complete_truth(moved_pause,f);

}
void fragments(){
    Fixture f;std::size_t schedules=0;
    for(std::size_t chunk=1;chunk<=f.compressed.size();++chunk){auto reader=pipeline(f.configuration);check(!pump(reader,f.compressed,chunk).error,"fragmented compressed input accepted");complete_truth(reader,f);++schedules;}
    for(std::size_t split=1;split<f.compressed.size();++split){auto reader=pipeline(f.configuration);check(!pump(reader,std::span<const std::byte>(f.compressed).first(split),split).error,"first split accepted");check(!pump(reader,std::span<const std::byte>(f.compressed).subspan(split),f.compressed.size()).error,"second split accepted");complete_truth(reader,f);++schedules;}
    for(std::size_t cut=0;cut<f.compressed.size();++cut){
        auto bounded=pipeline(f.configuration);check(!pump(bounded,std::span<const std::byte>(f.compressed).first(cut),7).error,"valid bounded compressed prefix");const auto prefix=bounded.finish(EndKind::bounded_prefix);check(!prefix.error&&prefix.bounded_prefix&&!prefix.source_complete&&!prefix.publication_eligible,"deliberate cutoff is explicitly incomplete");prefix_truth(bounded);
        auto truncated=pipeline(f.configuration);check(!pump(truncated,std::span<const std::byte>(f.compressed).first(cut),7).error,"prefix before EOF not falsely malformed");const auto eof=truncated.finish(EndKind::source_eof);check(eof.error&&!eof.source_complete&&!eof.publication_eligible,"EOF at every gzip interior byte fails integrity");prefix_truth(truncated);schedules+=2;
    }
    std::cout<<"streaming_fragment_and_cut_schedules="<<schedules<<" source_bytes="<<f.raw.size()<<" compressed_bytes="<<f.compressed.size()<<'\n';
}
StreamingError failed_input(const Fixture& f,std::span<const std::byte> input,std::size_t chunk=7){
    auto reader=pipeline(f.configuration);const auto fed=pump(reader,input,chunk);const auto end=reader.finish(EndKind::source_eof);check(fed.error||end.error,"invalid source rejected");check(!end.source_complete&&!end.publication_eligible,"failed source cannot publish complete result");return fed.error?fed.error:end.error;
}
void corruption(){
    Fixture f;
    for(std::size_t position:{std::size_t{0},std::size_t{2},std::size_t{3},std::size_t{10},f.compressed.size()-8,f.compressed.size()-4}){
        auto corrupt=f.compressed;if(position==2)corrupt[position]=std::byte{9};else if(position==3)corrupt[position]=std::byte{0x20};else if(position==10)corrupt[position]=std::byte{7};else corrupt[position]^=std::byte{1};
        const auto error=failed_input(f,corrupt);check(error.code==StreamingCode::gzip&&error.gzip.code==GzipCode::corrupt,"header/deflate/CRC/ISIZE corruption explicit");
    }
    auto concat=f.compressed;concat.insert(concat.end(),f.compressed.begin(),f.compressed.end());auto error=failed_input(f,concat);check(error.code==StreamingCode::gzip&&error.gzip.code==GzipCode::trailing_data,"concatenated member policy rejects second member");
    auto trailing=f.compressed;trailing.push_back(std::byte{0xff});error=failed_input(f,trailing);check(error.code==StreamingCode::gzip&&error.gzip.code==GzipCode::trailing_data,"trailing compressed byte rejected");
    Fixture no_terminal(streaming_records(),false);error=failed_input(no_terminal,no_terminal.compressed);check(error.code==StreamingCode::framing,"valid gzip cannot hide missing BinaryFile terminator");
    Fixture source_trailing;source_trailing.raw.push_back(std::byte{1});source_trailing.compressed=stored_gzip(source_trailing.raw);source_trailing.configuration.compressed_sha256=sha256(source_trailing.compressed);error=failed_input(source_trailing,source_trailing.compressed);check(error.code==StreamingCode::framing,"valid gzip cannot hide bytes after BinaryFile terminator");
    auto wrong_hash=f.configuration;wrong_hash.compressed_sha256[0]^=std::byte{1};auto reader=pipeline(wrong_hash);check(!pump(reader,f.compressed,11).error,"identity mismatch diagnosed after complete compressed source");check(reader.finish().error.code==StreamingCode::identity_mismatch,"wrong expected compressed identity fails completion");
    wrong_hash=f.configuration;(*wrong_hash.reconstruction.source.provenance.sha256)[0]^=std::byte{1};const auto hash_text=hex_digest(*wrong_hash.reconstruction.source.provenance.sha256);wrong_hash.reconstruction.initialization.fixture_sha256=*gig::Digest::make({hash_text.data(),hash_text.size()}).data;
    auto wrong_raw=pipeline(wrong_hash);check(!pump(wrong_raw,f.compressed,11).error,"consistent declared raw identity not falsely verified early");const auto invalid=wrong_raw.finish();check(invalid.error.code==StreamingCode::identity_mismatch&&!invalid.source_complete&&!invalid.decompressed_identity_verified,"wrong full BinaryFile identity fails publication");
}
void semantics(){
    auto records=std::vector<Bytes>{system(),directory(),directory(2,"TWO     ")};auto unsupported=records;unsupported.push_back(payload('H'));Fixture unsupported_fixture(unsupported);auto error=failed_input(unsupported_fixture,unsupported_fixture.compressed);check(error.code==StreamingCode::reconstruction&&error.reconstruction.disposition==SourceDisposition::source_rejected,"unsupported source type explicit pipeline stop");
    auto invalid=records;invalid.push_back(reduce('D',999));Fixture invalid_fixture(invalid);error=failed_input(invalid_fixture,invalid_fixture.compressed);check(error.code==StreamingCode::reconstruction&&error.reconstruction.context_error.code==ContextCode::missing_order,"invalid lifecycle explicit pipeline stop");
    auto crossed=records;crossed.push_back(add(101));crossed.push_back(add(102,10,99,1,'S'));Fixture cross_fixture(crossed);auto reader=pipeline(cross_fixture.configuration);const auto stopped=pump(reader,cross_fixture.compressed,7);check(stopped.error.code==StreamingCode::reconstruction&&stopped.error.reconstruction.native_error.code==gig::ErrorCode::crossed_quote,"native crossing rejection propagated");check(reader.reconstruction().context().summary().accepted_records==4&&reader.reconstruction().engine(0)->book().remaining()==10&&reader.reconstruction().receipts().size()==4,"native failure cannot commit context or source receipt");
    auto c=records;c.push_back(add(101));c.push_back(reduce('C',101,2,9));Fixture c_fixture(c);error=failed_input(c_fixture,c_fixture.compressed);check(error.code==StreamingCode::reconstruction&&error.reconstruction.native_error.code==gig::ErrorCode::unsupported,"C opt-in preserved through streaming");
    c_fixture.configuration.reconstruction.allow_c_book_only=true;auto allowed=pipeline(c_fixture.configuration);check(!pump(allowed,c_fixture.compressed,5).error,"explicit C book-only stream accepted");check(!allowed.finish().error&&allowed.reconstruction().engine(0)->book().remaining()==8,"streaming C does not force actual price into resting book");
    // More than one stored DEFLATE block, with bounded context and no invented orders.
    std::vector<Bytes> large{system(),directory()};for(std::size_t i=0;i<1800;++i)large.push_back(directory());Fixture multi_block(large);multi_block.configuration.reconstruction.max_source_records=2000;auto bounded=pipeline(multi_block.configuration);check(multi_block.raw.size()>65535&&!pump(bounded,multi_block.compressed,97).error,"multi-block incremental input accepted");const auto complete=bounded.finish();check(!complete.error&&complete.source_complete&&complete.source_records==large.size()&&complete.native_records==0&&bounded.reconstruction().engine(0)->book().order_count()==0,"large observation stream preserves exact source accounting");
}
void budgets(){
    Fixture f;auto exact=f.configuration;exact.gzip.max_compressed_bytes=f.compressed.size();exact.gzip.max_decompressed_bytes=f.raw.size();auto reader=pipeline(exact);check(!pump(reader,f.compressed,13).error,"exact gzip byte caps accepted");complete_truth(reader,f);
    for(bool compressed:{true,false}){auto c=f.configuration;if(compressed)c.gzip.max_compressed_bytes=f.compressed.size()-1;else c.gzip.max_decompressed_bytes=f.raw.size()-1;auto limited=pipeline(c);const auto fed=pump(limited,f.compressed,7);const auto end=limited.finish();const auto error=fed.error?fed.error:end.error;check(error.code==StreamingCode::gzip&&error.gzip.code==(compressed?GzipCode::compressed_limit:GzipCode::decompressed_limit),"byte cap+1 explicit resource stop");check(!end.source_complete&&!end.publication_eligible,"resource cutoff not complete source");prefix_truth(limited);}
    auto header=f.compressed;header[3]=std::byte{8};header.insert(header.begin()+10,65,std::byte{'n'});header[74]=std::byte{0};auto c=f.configuration;c.compressed_sha256=sha256(header);c.gzip.max_header_bytes=16;auto header_limited=pipeline(c);auto fed=pump(header_limited,header,3);check(fed.error.code==StreamingCode::gzip&&fed.error.gzip.code==GzipCode::header_limit,"long optional gzip header has explicit cap");
    // Independently produced Python gzip fixture: 4096 ASCII A bytes, high ratio.
    const std::string_view encoded="1f8b0800000000000203edc1010d000000c2a06cef5fca1e0e28000000e0dd004034a6fe00100000";Bytes bomb;for(std::size_t i=0;i<encoded.size();i+=2){const auto nibble=[](char x)->unsigned{return x>='0'&&x<='9'?static_cast<unsigned>(x-'0'):static_cast<unsigned>(x-'a'+10);};bomb.push_back(static_cast<std::byte>(nibble(encoded[i])*16+nibble(encoded[i+1])));}
    c=f.configuration;c.compressed_sha256=sha256(bomb);c.gzip.max_expansion_ratio=1;c.gzip.expansion_slack_bytes=0;c.gzip.output_buffer_bytes=64;auto expansion=pipeline(c);fed=pump(expansion,bomb,7);check(fed.error.code==StreamingCode::gzip&&fed.error.gzip.code==GzipCode::expansion_limit,"expansion limit protects before completing huge bogus frame");
    c=f.configuration;c.framing.max_records=4;auto frames=pipeline(c);fed=pump(frames,f.compressed,7);check(fed.error.code==StreamingCode::framing&&fed.error.framing.code==Code::record_limit&&frames.reconstruction().context().summary().accepted_records==4,"frame budget exact prefix, no silent skip");prefix_truth(frames);
    c=f.configuration;c.reconstruction.max_source_records=4;auto sources=pipeline(c);fed=pump(sources,f.compressed,7);check(fed.error.code==StreamingCode::reconstruction&&sources.reconstruction().context().summary().accepted_records==4,"reconstruction source cap enforced inside stream");prefix_truth(sources);
    c=f.configuration;c.reconstruction.bindings[0]->max_journal_records=1;auto journal=pipeline(c);fed=pump(journal,f.compressed,7);check(fed.error.code==StreamingCode::reconstruction&&journal.reconstruction().context().summary().accepted_records==5,"native journal cap preserves streaming accepted prefix");prefix_truth(journal);
    gig::TrackedResource tiny(std::pmr::get_default_resource(),64);check(!StreamingReconstructor::create(f.configuration,&tiny)&&tiny.stats().live_bytes==0,"entire pipeline hard PMR cap and rollback");
}
class ReentrantStreamResource final : public std::pmr::memory_resource {
public:
    StreamingReconstructor* owner{};bool armed{},called{},feed_rejected{},checkpoint_rejected{},finish_unchanged{};
private:
    void* do_allocate(std::size_t bytes,std::size_t alignment)override{
        if(armed&&owner){armed=false;called=true;const auto before=owner->reconstruction().summary();const auto attempted=owner->feed({});feed_rejected=attempted.error.code==StreamingCode::reentrant&&attempted.consumed==0;checkpoint_rejected=!owner->checkpoint(code_hash());const auto finish=owner->finish();finish_unchanged=!finish.finished&&owner->reconstruction().summary()==before;}
        return std::pmr::get_default_resource()->allocate(bytes,alignment);
    }
    void do_deallocate(void* pointer,std::size_t bytes,std::size_t alignment)override{std::pmr::get_default_resource()->deallocate(pointer,bytes,alignment);}
    bool do_is_equal(const std::pmr::memory_resource& other)const noexcept override{return this==&other;}
};
void allocation(){
    Fixture f;std::size_t create_sites=0,feed_sites=0;
    {gig::TrackedResource memory;{auto reader=StreamingReconstructor::create(f.configuration,&memory);check(bool(reader),"allocation baseline create");create_sites=memory.stats().attempts;}check(memory.stats().live_bytes==0,"baseline creation release");}
    for(std::size_t site=0;site<create_sites;++site){gig::TrackedResource memory;memory.fail_after(site);{auto reader=StreamingReconstructor::create(f.configuration,&memory);check(!reader,"every pipeline factory allocation failpoint observed");}check(memory.stats().live_bytes==0,"pipeline factory failpoint no leak");}
    {gig::TrackedResource memory;{auto reader=pipeline(f.configuration,&memory);const auto before=memory.stats().attempts;check(!pump(reader,f.compressed,11).error,"allocation baseline feed");complete_truth(reader,f);feed_sites=memory.stats().attempts-before;}check(memory.stats().live_bytes==0,"baseline feed release");}
    check(create_sites>0&&feed_sites>0,"actual allocator requests reached");
    for(std::size_t site=0;site<feed_sites;++site){gig::TrackedResource memory;{auto reader=pipeline(f.configuration,&memory);memory.fail_after(site);const auto fed=pump(reader,f.compressed,11);const auto end=reader.finish();memory.disable_failure();if(!(fed.error||end.error)){std::cerr<<"unreached feed allocation site="<<site<<" total="<<feed_sites<<'\n';throw std::runtime_error("every streaming feed allocation failure observed");}check(!end.source_complete&&!end.publication_eligible,"allocation-failed source cannot publish complete result");prefix_truth(reader);const auto accepted=reader.reconstruction().context().summary();const auto again=reader.feed(f.compressed);check(again.error&&again.consumed==0&&reader.reconstruction().context().summary()==accepted,"sticky failure never duplicates accepted source");}check(memory.stats().live_bytes==0,"failed pipeline releases all zlib/framer/context/native/receipt storage");}
    ReentrantStreamResource resource;{auto reader=pipeline(f.configuration,&resource);resource.owner=&reader;resource.armed=true;check(!pump(reader,f.compressed,11).error,"reentry fixture proceeds normally");complete_truth(reader,f);check(resource.called&&resource.feed_rejected&&resource.checkpoint_rejected&&resource.finish_unchanged,"allocation callback cannot reenter feed/checkpoint/finish accepted state");resource.owner=nullptr;}
    std::cout<<"streaming_allocation_sites create="<<create_sites<<" feed="<<feed_sites<<'\n';
}
void restart(){
    Fixture f;auto c=f.configuration;c.gzip.output_buffer_bytes=128;
    gig::TrackedResource memory;
    {
        auto original=pipeline(c,&memory);check(!original.pause_after(4),"declare exact accepted-frame pause");const auto original_read=pump(original,f.compressed,f.compressed.size());check(original_read.paused&&!original_read.error,"pause after accepted fourth frame");prefix_truth(original);
        check(original.summary().decompressed_bytes>original.summary().accepted_prefix_bytes,"pause retains actual bounded decompressed read-ahead");
        auto checkpoint=original.checkpoint(code_hash());check(bool(checkpoint)&&checkpoint.data->reconstruction.context_committed==4,"logical prefix checkpoint captured");
        auto restored=pipeline(c,&memory);check(!restored.pause_after(4),"fresh replay pause boundary");const auto restored_read=pump(restored,f.compressed,1);check(restored_read.paused&&!restored_read.error,"fresh replay reaches exact logical boundary");
        check(!restored.verify_checkpoint(*checkpoint.data,code_hash()),"checkpoint independent of compressed read-ahead/chunk schedule");prefix_truth(restored);
        auto modified=*checkpoint.data;modified.config.compressed_sha256[0]^=std::byte{1};check(bool(restored.verify_checkpoint(modified,code_hash())),"changed source identity rejected");
        modified=*checkpoint.data;modified.config.gzip.max_compressed_bytes+=1;check(bool(restored.verify_checkpoint(modified,code_hash())),"changed streaming resource/config identity rejected");
        modified=*checkpoint.data;modified.accepted_prefix_sha256[0]^=std::byte{1};check(bool(restored.verify_checkpoint(modified,code_hash())),"changed accepted prefix rejected");
        modified=*checkpoint.data;++modified.books[0]->ledger.added;check(bool(restored.verify_checkpoint(modified,code_hash())),"changed native descriptor rejected");
        check(bool(restored.verify_checkpoint(*checkpoint.data,*gig::Digest::make(std::string(64,'2')).data)),"changed implementation identity rejected");
        const auto accepted=original.reconstruction().summary();memory.fail_after(0);check(!original.checkpoint(code_hash()),"checkpoint query allocation failure explicit");memory.disable_failure();check(original.reconstruction().summary()==accepted,"failed checkpoint export does not uncommit state");
        check(!original.resume()&&!restored.resume(),"resume both owned accepted-prefix streams");
        check(!pump(original,std::span<const std::byte>(f.compressed).subspan(original_read.consumed),5).error,"original drains owned read-ahead before more compressed input");
        check(!pump(restored,std::span<const std::byte>(f.compressed).subspan(restored_read.consumed),17).error,"fresh replay resumes from its own physical position");complete_truth(original,f);complete_truth(restored,f);
        check(state(original.reconstruction())==state(restored.reconstruction()),"no missing/duplicate event after logical restart");
    }
    check(memory.stats().live_bytes==0,"checkpoint/restart simultaneous resource release");
    // A CRC error physically observed in decompressor read-ahead must not change
    // the earlier logical pause/checkpoint boundary. It remains visible and fatal
    // once that retained output is drained; it never certifies the source.
    auto corrupt=f.compressed;corrupt[corrupt.size()-8]^=std::byte{1};
    auto corrupt_config=f.configuration;corrupt_config.gzip.output_buffer_bytes=65536;corrupt_config.compressed_sha256=sha256(corrupt);
    auto bytewise=pipeline(corrupt_config);auto readahead=pipeline(corrupt_config);
    check(!bytewise.pause_after(4)&&!readahead.pause_after(4),"corrupt read-ahead logical pause configured");
    const auto bytewise_read=pump(bytewise,corrupt,1);const auto whole_read=pump(readahead,corrupt,corrupt.size());
    check(bytewise_read.paused&&!bytewise_read.error&&whole_read.paused&&!whole_read.error,"CRC beyond logical pause cannot poison accepted prefix");
    check(!bytewise.summary().observed_gzip_error&&readahead.summary().observed_gzip_error.code==GzipCode::corrupt,"physical gzip read-ahead diagnostic distinguished");
    check(!bytewise.summary().publication_eligible&&!readahead.summary().publication_eligible&&!readahead.summary().gzip_member_verified,"corrupt paused prefix never claims verified full source");
    auto corrupt_checkpoint=bytewise.checkpoint(code_hash());check(bool(corrupt_checkpoint)&&!readahead.verify_checkpoint(*corrupt_checkpoint.data,code_hash()),"provisional logical checkpoints identical across read-ahead schedules");
    check(!bytewise.resume()&&!readahead.resume(),"resume provisional corrupted sources");
    const auto small_tail=pump(bytewise,std::span<const std::byte>(corrupt).subspan(bytewise_read.consumed),1);
    const auto large_tail=pump(readahead,std::span<const std::byte>(corrupt).subspan(whole_read.consumed),corrupt.size());
    const auto small_end=bytewise.finish();const auto large_end=readahead.finish();
    check((small_tail.error||small_end.error)&&(large_tail.error||large_end.error),"deferred CRC failure must surface after resume");
    check(small_end.error.code==StreamingCode::gzip&&large_end.error.code==StreamingCode::gzip&&small_end.error.gzip.code==GzipCode::corrupt&&large_end.error.gzip.code==GzipCode::corrupt,"same final corrupt classification");
    check(!small_end.source_complete&&!large_end.source_complete&&!small_end.publication_eligible&&!large_end.publication_eligible,"deferred corrupt source cannot publish");
    check(small_end.accepted_records==18&&large_end.accepted_records==18&&small_end.accepted_prefix_sha256==large_end.accepted_prefix_sha256&&state(bytewise.reconstruction())==state(readahead.reconstruction()),"same retained logical remainder without hidden recovery");
    auto cutoff=pipeline(corrupt_config);check(!cutoff.pause_after(4),"paused EOF cutoff configured");check(pump(cutoff,corrupt,corrupt.size()).paused,"paused EOF cutoff reached");
    const auto bounded=cutoff.finish(EndKind::source_eof);check(!bounded.error&&bounded.bounded_prefix&&!bounded.source_complete&&!bounded.publication_eligible&&bounded.observed_gzip_error.code==GzipCode::corrupt&&cutoff.reconstruction().context().summary().bounded_prefix,"finish at deliberate pause is bounded prefix with physical diagnostic, not unexpected EOF");check(bool(cutoff.resume()),"finished cutoff cannot hot resume");
    auto changed_records=streaming_records();put(changed_records[3],20,11,4);Fixture changed(changed_records);changed.configuration=c;auto different=pipeline(changed.configuration);check(!different.pause_after(4),"changed fixture pause");check(pump(different,changed.compressed,7).paused,"changed source prefix can be independently inspected");
    auto original=pipeline(c);check(!original.pause_after(4),"reference source pause");check(pump(original,f.compressed,7).paused,"reference reaches pause");auto checkpoint=original.checkpoint(code_hash());check(bool(checkpoint)&&bool(different.verify_checkpoint(*checkpoint.data,code_hash())),"different actual source prefix cannot satisfy checkpoint");
}
}
int main(int argc,char** argv){try{const std::string_view group=argc>1?argv[1]:"all";
#define RUN(name) if(group=="all"||group==#name)name()
RUN(basic);RUN(fragments);RUN(corruption);RUN(semantics);RUN(budgets);RUN(allocation);RUN(restart);
#undef RUN
std::cout<<"streaming "<<group<<" passed\n";return 0;}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
