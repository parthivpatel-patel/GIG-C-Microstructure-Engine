#include "gig/itch/streaming.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <algorithm>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace {
using namespace gig::itch;
using Bytes=std::vector<std::byte>;
template<class T>T scalar(std::uint64_t n){return *T::make(n).data;}
gig::Identity identity(std::string_view s){return *gig::Identity::make(s).data;}
SourceIdentity source_identity(std::string_view s){return *SourceIdentity::make(s).data;}
Text<8> stock(std::string_view s){Text<8> result;std::copy(s.begin(),s.end(),result.bytes.begin());return result;}
std::string hex(std::string_view s){constexpr char digits[]="0123456789abcdef";std::string result;for(char v:s){const auto c=static_cast<unsigned char>(v);result+=digits[c>>4];result+=digits[c&15];}return result;}
void raw(Bytes&b,std::uint64_t n,unsigned width){for(unsigned i=width;i>0;--i)b.push_back(static_cast<std::byte>((n>>((i-1)*8U))&255U));}
void text(Bytes&b,std::string_view s){for(char c:s)b.push_back(static_cast<std::byte>(c));}
std::string directory_hex(const StockDirectory& d){Bytes b;text(b,d.stock.view());raw(b,static_cast<unsigned char>(d.market_category),1);raw(b,static_cast<unsigned char>(d.financial_status),1);raw(b,d.round_lot_size,4);raw(b,static_cast<unsigned char>(d.round_lots_only),1);raw(b,static_cast<unsigned char>(d.issue_classification),1);text(b,d.issue_subtype.view());for(char c:{d.authenticity,d.short_sale_threshold,d.ipo_flag,d.luld_tier,d.etp_flag})raw(b,static_cast<unsigned char>(c),1);raw(b,d.etp_leverage,4);raw(b,static_cast<unsigned char>(d.inverse),1);return hex({reinterpret_cast<const char*>(b.data()),b.size()});}
ReconstructionConfig configuration(unsigned flags,gig::types::UnitScale tick,gig::types::UnitScale lots,std::string_view digest_text){
    const auto source=source_identity("synthetic-l3"),session=source_identity("synthetic-day");
    std::array<std::byte,32> digest{};for(std::size_t i=0;i<32;++i)digest[i]=static_cast<std::byte>(std::stoul(std::string(digest_text.substr(i*2,2)),nullptr,16));
    Provenance provenance{Origin::synthetic,source,digest,0x503147};
    ContextPolicy policy;policy.max_directories=8;policy.max_lifetime_orders=512;policy.max_matches=512;
    policy.allow_equal_cancel=(flags&2U)!=0;policy.require_monotonic_timestamps=(flags&4U)!=0;
    // The context's exact integer wire hints are configured separately from native
    // Fraction units. The adapter still performs its own checked conversion.
    const auto quantum=tick.numerator*10000;
    if(quantum%tick.denominator==0&&quantum/tick.denominator<=UINT32_MAX)policy.price_quantum=static_cast<std::uint32_t>(quantum/tick.denominator);
    if(lots.numerator%lots.denominator==0&&lots.numerator/lots.denominator<=UINT32_MAX)policy.lot_size=static_cast<std::uint32_t>(lots.numerator/lots.denominator);
    InitializationEvidence evidence{InitialStateKind::authored_empty,source,session,source_identity("independent-fixture-v1"),identity("l3-fixture"),identity("1"),identity("synthetic-private-evaluation"),*gig::Digest::make(digest_text).data,0x503147,{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}},true};
    ReconstructionConfig result{{source,session,provenance,Initialization::synthetic_history_declared},policy,evidence,identity("l3-oracle-run"),{},2,1024,2*1024*1024,(flags&1U)!=0};
    for(std::size_t i=0;i<2;++i){gig::InstrumentRules rules{scalar<gig::InstrumentId>(i+1),scalar<gig::VenueId>(1),*gig::PriceTicks::make(1).data,*gig::PriceTicks::make(INT64_MAX).data,scalar<gig::QuantityLots>(UINT64_MAX),tick,lots};result.bindings[i]=BookBinding{stock(i==0?"TEST    ":"TWO     "),StockLocate{static_cast<std::uint16_t>(i+1)},rules,scalar<gig::StreamId>(i+1),{128,128,128},512};}
    return result;
}
std::string category(const ReconstructionStep& step){
    if(step.committed)return step.disposition==SourceDisposition::native_committed?"native":"external";
    if(step.context_error.source_error.code==Code::unknown_type||step.context_error.source_error.code==Code::unsupported_type)return "unsupported";
    if(step.context_error.source_error.code!=Code::none)return "source";
    if(step.context_error.code==ContextCode::unsupported_source)return "unsupported";
    if(step.disposition==SourceDisposition::source_rejected)return "source";
    if(step.disposition==SourceDisposition::context_rejected)return "context";
    if(step.native_error.code==gig::ErrorCode::crossed_quote)return "native";
    if(step.native_error.code==gig::ErrorCode::off_unit||step.native_error.code==gig::ErrorCode::overflow||step.native_error.code==gig::ErrorCode::invalid_range)return "numeric";
    if(step.native_error.code==gig::ErrorCode::identity_mismatch)return "binding";
    return "projection";
}
void outcome(const ReconstructionStep& step,const SyntheticReconstructor& r){
    const auto& summary=r.summary();const auto& c=r.context();
    std::uint64_t offset=0;if(c.summary().last_location){const auto& receipt=r.receipts().back();const auto length=expected_length(receipt.source.type);offset=receipt.source.location.payload_offset.value()+(length?*length:0);}
    unsigned stage=0;for(const auto& receipt:r.receipts())if(receipt.source.type=='S')++stage;
    std::cout<<"{\"committed\":"<<(step.committed?"true":"false")<<",\"category\":\""<<category(step)<<"\",\"book\":";if(step.book_index&&step.committed&&step.disposition==SourceDisposition::native_committed)std::cout<<*step.book_index;else std::cout<<"null";
    const auto position=[](const std::optional<Location>& location){if(location)std::cout<<'['<<location->frame_offset.value()<<','<<location->payload_offset.value()<<','<<location->ordinal.value()<<']';else std::cout<<"null";};
    std::cout<<",\"source_summary\":{\"considered\":"<<summary.considered<<",\"context_committed\":"<<summary.context_committed<<",\"rejected\":"<<summary.rejected<<",\"pending\":"<<(summary.pending?"true":"false")<<",\"input_complete\":"<<(summary.input_complete?"true":"false")<<",\"finished\":"<<(summary.finished?"true":"false")<<",\"initialization_verified\":"<<(summary.initialization_verified?"true":"false")<<",\"unconsidered_record\":"<<(summary.unconsidered_record?"true":"false")<<",\"eligibility\":"<<static_cast<unsigned>(summary.eligibility)<<",\"physical\":";position(summary.physical_position);std::cout<<",\"committed_position\":";position(summary.committed_position);std::cout<<",\"native_counts\":["<<summary.native_counts[0]<<','<<summary.native_counts[1]<<"]},\"context_incomplete\":"<<(c.summary().initialization_incomplete?"true":"false")<<",\"context_session_incomplete\":"<<(c.summary().session_incomplete?"true":"false");
    std::cout<<",\"accepted\":"<<c.summary().accepted_records<<",\"offset\":"<<offset<<",\"native\":"<<summary.native_committed<<",\"external\":"<<summary.external_observations<<",\"stage\":"<<stage<<",\"last_timestamp\":";if(c.summary().last_timestamp)std::cout<<c.summary().last_timestamp->value();else std::cout<<"null";
    std::cout<<",\"directories\":[";bool comma=false;for(const auto& d:c.directories()){if(comma)std::cout<<',';comma=true;std::cout<<'['<<d.locate.value()<<",\""<<directory_hex(d.directory)<<"\"]";}
    std::cout<<"],\"context_orders\":[";comma=false;for(const auto&o:c.orders()){if(comma)std::cout<<',';comma=true;std::cout<<'['<<o.reference.value()<<','<<o.locate.value()<<','<<static_cast<unsigned>(o.side)<<','<<o.remaining.value()<<','<<o.resting_price.value()<<','<<o.arrival.value()<<','<<(o.active?1:0)<<",\""<<(o.attribution?hex(o.attribution->view()):"")<<"\"]";}
    std::cout<<"],\"matches\":[";comma=false;for(const auto&m:c.matches()){if(comma)std::cout<<',';comma=true;std::cout<<'['<<m.number.value()<<','<<m.locate.value()<<','<<static_cast<unsigned>(m.kind)<<','<<(m.broken?1:0)<<']';}
    std::cout<<"],\"receipts\":[";comma=false;for(const auto& receipt:r.receipts()){if(comma)std::cout<<',';comma=true;const auto& raw=receipt.source;std::cout<<'['<<raw.location.ordinal.value()<<','<<raw.location.frame_offset.value()<<','<<raw.location.payload_offset.value()<<','<<static_cast<unsigned>(raw.type)<<','<<raw.header.stock_locate.value()<<','<<raw.header.tracking_number.value()<<','<<raw.header.timestamp.value()<<',';if(receipt.disposition==SourceDisposition::native_committed&&receipt.book_index)std::cout<<*receipt.book_index;else std::cout<<"null";std::cout<<',';if(receipt.native_sequence)std::cout<<*receipt.native_sequence;else std::cout<<"null";std::cout<<']';}
    std::cout<<"],\"books\":[";
    for(std::size_t index=0;index<2;++index){if(index)std::cout<<',';const auto* engine=r.engine(index);const auto& book=engine->book();std::vector<gig::RestingOrder> orders;for(const auto&o:c.orders()){auto id=gig::OrderId::make(o.reference.value());if(id){const auto found=book.find(*id.data);if(found)orders.push_back(*found);}}
        std::sort(orders.begin(),orders.end(),[](const auto&a,const auto&b){return a.order.order_id<b.order.order_id;});
        std::cout<<"{\"needs_recovery\":"<<(engine->needs_recovery()?"true":"false")<<",\"orders\":[";comma=false;for(const auto&o:orders){if(comma)std::cout<<',';comma=true;std::cout<<'['<<o.order.order_id.value()<<','<<(o.order.side==gig::Side::buy?66:83)<<','<<o.order.price_ticks.value()<<','<<o.order.quantity.value()<<','<<o.priority<<']';}
        const auto l=book.ledger();std::cout<<"],\"revision\":"<<book.revision()<<",\"journal\":"<<engine->journal_size()<<",\"remaining\":"<<book.remaining()<<",\"count\":"<<book.order_count()<<",\"ledger\":["<<l.added<<','<<l.cancelled<<','<<l.executed<<','<<l.discarded<<','<<l.recovered<<','<<l.replacement_in<<','<<l.replacement_out<<','<<l.total_in<<','<<l.total_out<<']';
        const auto depth=book.depth(128);if(!depth){std::cerr<<"depth failed\n";std::exit(3);}std::cout<<",\"bids\":[";comma=false;for(const auto& d:depth.data->bids){if(comma)std::cout<<',';comma=true;std::cout<<'['<<d.price_ticks.value()<<','<<d.quantity.value()<<','<<d.order_count<<']';}std::cout<<"],\"asks\":[";comma=false;for(const auto&d:depth.data->asks){if(comma)std::cout<<',';comma=true;std::cout<<'['<<d.price_ticks.value()<<','<<d.quantity.value()<<','<<d.order_count<<']';}
        std::cout<<"],\"capture\":";if(book.last_metadata()&&book.last_metadata()->capture_ordinal.data)std::cout<<*book.last_metadata()->capture_ordinal.data;else std::cout<<"null";
        std::cout<<",\"metadata\":";if(!book.last_metadata())std::cout<<"null";else{const auto& m=*book.last_metadata();const auto& p=m.provenance;const auto& d=*p.dataset.data;std::cout<<"{\"instrument\":"<<m.instrument.data->value()<<",\"venue\":"<<m.venue.data->value()<<",\"stream\":"<<m.scope.data->stream.value()<<",\"sequence\":"<<m.sequence.data->value()<<",\"capture\":"<<*m.capture_ordinal.data<<",\"source_record\":\""<<m.source_record.data->view()<<"\",\"event_time\":";if(m.event_time.data)std::cout<<m.event_time.data->nanoseconds.value();else std::cout<<"null";std::cout<<",\"receive_time\":";if(m.receive_time.data)std::cout<<m.receive_time.data->nanoseconds.value();else std::cout<<"null";std::cout<<",\"session\":\""<<m.scope.data->session.view()<<"\",\"epoch\":"<<m.scope.data->epoch<<",\"unit\":"<<static_cast<unsigned>(m.scope.data->unit)<<",\"dataset\":\""<<d.identity.view()<<"\",\"version\":\""<<d.version.data->view()<<"\",\"license\":\""<<d.license_reference.data->view()<<"\",\"digest\":\""<<d.sha256.data->view()<<"\",\"origin\":"<<static_cast<unsigned>(*p.origin.data)<<",\"source\":"<<static_cast<unsigned>(*p.source.data)<<",\"seed\":"<<*p.generator_seed.data<<",\"lineage\":[";for(std::size_t j=0;j<p.lineage.count;++j){if(j)std::cout<<',';std::cout<<static_cast<unsigned>(p.lineage.items[j]->kind);}std::cout<<"],\"parent\":\""<<p.parents.items[0]->identity.view()<<"\"}";}
        std::cout<<'}';
    }
    std::cout<<"]}";
}
}
namespace {
Bytes unhex(std::string_view encoded){Bytes bytes;if(encoded=="-")return bytes;for(std::size_t i=0;i<encoded.size();i+=2)bytes.push_back(static_cast<std::byte>(std::stoul(std::string(encoded.substr(i,2)),nullptr,16)));return bytes;}
Sha256Digest digest(std::string_view encoded){const auto bytes=unhex(encoded);if(bytes.size()!=32)throw std::runtime_error("driver digest width");Sha256Digest out{};std::copy(bytes.begin(),bytes.end(),out.begin());return out;}
std::string hex_digest_text(Sha256Digest value){const auto bytes=hex_digest(value);return {bytes.data(),bytes.size()};}
ReconstructionStep last_step(const StreamingReconstructor& stream){
    const auto summary=stream.summary();if(summary.error.code==StreamingCode::reconstruction)return summary.error.reconstruction;
    ReconstructionStep step;const auto receipts=stream.reconstruction().receipts();if(!receipts.empty()){const auto& receipt=receipts.back();step.disposition=receipt.disposition;step.book_index=receipt.book_index;step.native_sequence=receipt.native_sequence;step.committed=true;}return step;
}
void stream_summary(const StreamingSummary& s){std::cout<<"{\"compressed\":"<<s.compressed_bytes<<",\"decompressed\":"<<s.decompressed_bytes<<",\"framing\":"<<s.framing_bytes<<",\"accepted_prefix\":"<<s.accepted_prefix_bytes<<",\"source_records\":"<<s.source_records<<",\"accepted_records\":"<<s.accepted_records<<",\"native_records\":"<<s.native_records<<",\"external_observations\":"<<s.external_observations<<",\"compressed_sha256\":\""<<hex_digest_text(s.compressed_sha256)<<"\",\"decompressed_sha256\":\""<<hex_digest_text(s.decompressed_sha256)<<"\",\"accepted_prefix_sha256\":\""<<hex_digest_text(s.accepted_prefix_sha256)<<"\",\"gzip_verified\":"<<(s.gzip_member_verified?"true":"false")<<",\"framer_terminated\":"<<(s.framer_terminated?"true":"false")<<",\"compressed_identity\":"<<(s.compressed_identity_verified?"true":"false")<<",\"decompressed_identity\":"<<(s.decompressed_identity_verified?"true":"false")<<",\"source_complete\":"<<(s.source_complete?"true":"false")<<",\"publication_eligible\":"<<(s.publication_eligible?"true":"false")<<",\"paused\":"<<(s.paused?"true":"false")<<",\"finished\":"<<(s.finished?"true":"false")<<",\"bounded_prefix\":"<<(s.bounded_prefix?"true":"false")<<",\"residual\":"<<s.residual_frame_bytes<<",\"buffered_output_bytes\":"<<s.buffered_output_bytes<<",\"observed_gzip_error\":"<<static_cast<unsigned>(s.observed_gzip_error.code)<<",\"error\":"<<static_cast<unsigned>(s.error.code)<<",\"gzip_error\":"<<static_cast<unsigned>(s.error.gzip.code)<<",\"framing_error\":"<<static_cast<unsigned>(s.error.framing.code)<<'}';}
void drive(StreamingReconstructor& stream,std::span<const std::byte> bytes,std::size_t chunk,std::size_t& offset){
    while(offset<bytes.size()){
        const auto size=std::min(chunk,bytes.size()-offset);const auto result=stream.feed(bytes.subspan(offset,size));offset+=result.consumed;
        if(result.error||result.paused)return;
        if(result.consumed==0)throw std::runtime_error("stream driver made no progress");
    }
    // Inflate can retain output even after consuming all offered compressed bytes.
    // Empty calls drain that bounded output; completion/errors remain explicit.
    for(std::size_t attempt=0;attempt<65536;++attempt){const auto before=stream.summary();const auto result=stream.feed({});const auto after=stream.summary();if(result.error||result.paused)return;if(after.decompressed_bytes==before.decompressed_bytes&&after.source_records==before.source_records)return;}
    throw std::runtime_error("stream driver drain did not terminate");
}
}
int main(){try{std::string line;while(std::getline(std::cin,line)){gig::TrackedResource resource(std::pmr::get_default_resource(),128*1024*1024);{
    std::istringstream input(line);std::size_t chunk{},output_buffer{};unsigned end{};std::uint64_t compressed_limit{},decompressed_limit{},ratio{},slack{},header_limit{};std::int64_t pause{-1};std::string fixture_digest,compressed_digest,encoded;
    input>>chunk>>end>>compressed_limit>>decompressed_limit>>ratio>>slack>>header_limit>>output_buffer>>pause>>fixture_digest>>compressed_digest>>encoded;
    if(!input||chunk==0)throw std::runtime_error("driver protocol");
    const auto bytes=unhex(encoded);
    StreamingConfig cfg{configuration(1,{1,100},{1,1},fixture_digest),{output_buffer,compressed_limit,decompressed_limit,ratio,slack,header_limit},{},digest(compressed_digest)};
    auto created=StreamingReconstructor::create(cfg,&resource);if(!created){std::cerr<<"stream create: "<<static_cast<unsigned>(created.error.code)<<':'<<created.error.field<<'\n';return 2;}auto& stream=*created.data;
    bool restart_verified=false;std::size_t offset=0;
    if(pause>=0){if(stream.pause_after(static_cast<std::uint64_t>(pause)))throw std::runtime_error("driver pause contract");}
    drive(stream,bytes,chunk,offset);
    if(pause>=0){
        if(!stream.summary().paused)throw std::runtime_error("driver source failed before checkpoint");
        const auto code=*gig::Digest::make(std::string(64,'7')).data;const auto checkpoint=stream.checkpoint(code);if(!checkpoint)throw std::runtime_error("driver checkpoint capture");
        auto rebuilt=StreamingReconstructor::create(cfg,&resource);if(!rebuilt)throw std::runtime_error("driver restart creation");auto& replay=*rebuilt.data;
        if(replay.pause_after(static_cast<std::uint64_t>(pause)))throw std::runtime_error("driver restart pause");
        std::size_t replay_offset=0;drive(replay,bytes,chunk,replay_offset);
        if(replay.verify_checkpoint(*checkpoint.data,code))throw std::runtime_error("driver replay checkpoint mismatch");
        if(replay.resume()||stream.resume())throw std::runtime_error("driver resume");
        drive(replay,bytes,chunk,replay_offset);drive(stream,bytes,chunk,offset);
        const auto replay_summary=replay.finish(static_cast<EndKind>(end));const auto original_summary=stream.finish(static_cast<EndKind>(end));
        if(replay_summary.accepted_prefix_sha256!=original_summary.accepted_prefix_sha256||replay_summary.source_complete!=original_summary.source_complete||replay_summary.source_records!=original_summary.source_records)throw std::runtime_error("driver restarted full prefix differs");
        for(std::size_t i=0;i<2;++i){const auto a=replay.reconstruction().engine(i)->canonical();const auto b=stream.reconstruction().engine(i)->canonical();if(!a||!b||*a.data!=*b.data)throw std::runtime_error("driver restarted native state differs");}
        restart_verified=true;
    }
    const auto summary=stream.finish(static_cast<EndKind>(end));std::cout<<"{\"stream\":";stream_summary(summary);std::cout<<",\"restart_verified\":"<<(restart_verified?"true":"false")<<",\"source\":";outcome(last_step(stream),stream.reconstruction());std::cout<<"}\n";
}if(resource.stats().live_bytes!=0)throw std::runtime_error("stream driver PMR leak");}return 0;}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 3;}}
