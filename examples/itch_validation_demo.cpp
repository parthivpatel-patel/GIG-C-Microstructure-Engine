// Offline authored synthetic end-to-end demonstration. No market data.
#include "gig/itch/streaming.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <algorithm>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using namespace gig::itch;
using Bytes=std::vector<std::byte>;
constexpr std::size_t pmr_budget=4U*1024U*1024U;
constexpr std::uint64_t seed=7707;
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
template<class T,class I>T number(I n){auto x=T::make(n);require(bool(x),"fixture number");return *x.data;}
gig::Identity identity(std::string_view s){auto x=gig::Identity::make(s);require(bool(x),"fixture identity");return *x.data;}
SourceIdentity source_id(std::string_view s){auto x=SourceIdentity::make(s);require(bool(x),"fixture source identity");return *x.data;}
Text<8> stock(std::string_view s){require(s.size()==8,"stock padding");Text<8> out;std::copy(s.begin(),s.end(),out.bytes.begin());return out;}
std::string hex(Sha256Digest value){const auto bytes=hex_digest(value);return {bytes.data(),bytes.size()};}
void put(Bytes& bytes,std::size_t at,std::uint64_t n,std::size_t width){require(at+width<=bytes.size(),"fixture boundary");for(std::size_t i=0;i<width;++i){bytes[at+width-i-1]=static_cast<std::byte>(n&255U);n>>=8U;}}
void text(Bytes& bytes,std::size_t at,std::string_view s){require(at+s.size()<=bytes.size(),"fixture text boundary");for(char c:s)bytes[at++]=static_cast<std::byte>(c);}
Bytes payload(char type,std::size_t length,std::uint16_t locate=1){Bytes bytes(length);bytes[0]=static_cast<std::byte>(type);put(bytes,1,locate,2);put(bytes,5,1,6);return bytes;}
Bytes system(char code='O'){auto bytes=payload('S',12,0);bytes[11]=static_cast<std::byte>(code);return bytes;}
Bytes directory(std::uint16_t locate,std::string_view symbol){auto bytes=payload('R',39,locate);text(bytes,11,symbol);bytes[19]=std::byte{'Q'};bytes[20]=std::byte{'N'};put(bytes,21,100,4);text(bytes,25,"NC  P N1N");bytes[38]=std::byte{'N'};return bytes;}
Bytes add(std::uint64_t id,std::uint32_t quantity,std::uint32_t price=100,std::uint16_t locate=1,char side='B'){auto bytes=payload('A',36,locate);put(bytes,11,id,8);bytes[19]=static_cast<std::byte>(side);put(bytes,20,quantity,4);text(bytes,24,locate==1?"TEST    ":"TWO     ");put(bytes,32,price,4);return bytes;}
Bytes reduce(char type,std::uint64_t id,std::uint32_t quantity=1){auto bytes=payload(type,type=='E'?31U:(type=='X'?23U:19U));put(bytes,11,id,8);if(type!='D')put(bytes,19,quantity,4);if(type=='E')put(bytes,23,1,8);return bytes;}
Bytes replace(){auto bytes=payload('U',35);put(bytes,11,102,8);put(bytes,19,103,8);put(bytes,27,15,4);put(bytes,31,101,4);return bytes;}
Bytes trade(){auto bytes=payload('P',44);bytes[19]=std::byte{'B'};put(bytes,20,3,4);text(bytes,24,"TEST    ");put(bytes,32,100,4);put(bytes,36,2,8);return bytes;}
Bytes cross(){auto bytes=payload('Q',40);text(bytes,19,"TEST    ");put(bytes,27,100,4);put(bytes,31,3,8);bytes[39]=std::byte{'O'};return bytes;}
Bytes broken(){auto bytes=payload('B',19);put(bytes,11,2,8);return bytes;}
std::vector<Bytes> records(){return {system(),directory(1,"TEST    "),directory(2,"TWO     "),add(101,10),add(201,20,200,2,'S'),add(102,20),reduce('E',102,4),reduce('X',101,3),reduce('D',101),replace(),trade(),cross(),broken(),system('S'),system('Q'),system('M'),system('E'),system('C')};}
Bytes binary_file(const std::vector<Bytes>& rows){Bytes bytes;for(const auto& row:rows){require(row.size()<=65535,"frame bound");bytes.push_back(static_cast<std::byte>(row.size()>>8U));bytes.push_back(static_cast<std::byte>(row.size()&255U));bytes.insert(bytes.end(),row.begin(),row.end());}bytes.push_back(std::byte{});bytes.push_back(std::byte{});return bytes;}
void little(Bytes& bytes,std::uint32_t value,unsigned width){for(unsigned i=0;i<width;++i){bytes.push_back(static_cast<std::byte>(value&255U));value>>=8U;}}
// Independent stored-DEFLATE/RFC1952 writer; no production encoder or zlib.
Bytes gzip(std::span<const std::byte> raw){require(raw.size()<=65535,"stored block bound");Bytes bytes{std::byte{31},std::byte{139},std::byte{8},std::byte{},std::byte{},std::byte{},std::byte{},std::byte{},std::byte{},std::byte{255},std::byte{1}};little(bytes,static_cast<std::uint32_t>(raw.size()),2);little(bytes,static_cast<std::uint32_t>(raw.size())^65535U,2);bytes.insert(bytes.end(),raw.begin(),raw.end());std::uint32_t crc=0xffffffffU;for(auto b:raw){crc^=std::to_integer<std::uint32_t>(b);for(unsigned i=0;i<8;++i)crc=(crc>>1U)^((crc&1U)!=0?0xedb88320U:0U);}little(bytes,crc^0xffffffffU,4);little(bytes,static_cast<std::uint32_t>(raw.size()),4);return bytes;}
StreamingConfig configuration(Sha256Digest raw,Sha256Digest compressed){
    const auto source=source_id("p1i-authored-source"),session=source_id("p1i-authored-session");
    Provenance provenance;provenance.origin=Origin::synthetic;provenance.source=source;provenance.sha256=raw;provenance.generator_seed=seed;
    ContextPolicy policy;policy.max_directories=2;policy.max_lifetime_orders=4;policy.max_matches=3;policy.memory_budget_bytes=4096;
    InitializationEvidence initial{InitialStateKind::authored_empty,source,session,source_id("p1i-literal-generator"),identity("p1i-h18"),identity("1"),identity("private-authored-synthetic"),*gig::Digest::make(hex(raw)).data,seed,policy.first_location,true};
    ReconstructionConfig reconstruction{{source,session,provenance,Initialization::synthetic_history_declared},policy,initial,identity("p1i-offline-demo"),{},2,32,65536,false};
    for(std::size_t i=0;i<2;++i){gig::InstrumentRules rules{number<gig::InstrumentId>(i+1),number<gig::VenueId>(1),number<gig::PriceTicks>(1),number<gig::PriceTicks>(2000000000),number<gig::QuantityLots>(UINT64_MAX),{1,10000},{1,1}};reconstruction.bindings[i]=BookBinding{stock(i==0?"TEST    ":"TWO     "),StockLocate{static_cast<std::uint16_t>(i+1)},rules,number<gig::StreamId>(i+1),{8,8,8},16};}
    FramerLimits framing;framing.max_payload_bytes=64;framing.buffer_bytes=64;framing.max_records=32;framing.max_stream_bytes=1024;
    return {reconstruction,{128,1024,1024,2,64,64},framing,compressed};
}
StreamingReconstructor make_stream(const StreamingConfig& config,gig::TrackedResource& memory){auto result=StreamingReconstructor::create(config,&memory);require(bool(result),"pipeline creation");return std::move(*result.data);}
void drive(StreamingReconstructor& stream,std::span<const std::byte> bytes,std::size_t chunk,std::size_t& offset){
    while(offset<bytes.size()){auto result=stream.feed(bytes.subspan(offset,std::min(chunk,bytes.size()-offset)));offset+=result.consumed;if(result.error||result.paused)return;require(result.consumed!=0,"compressed progress");}
    for(std::size_t i=0;i<1024;++i){const auto before=stream.summary();const auto result=stream.feed({});const auto after=stream.summary();if(result.error||result.paused)return;if(before.decompressed_bytes==after.decompressed_bytes&&before.source_records==after.source_records)return;}
    throw std::runtime_error("bounded output drain");
}
void boolean(std::ostream& out,bool value){out<<(value?"true":"false");}
void location(std::ostream& out,const std::optional<Location>& value){if(value)out<<'['<<value->frame_offset.value()<<','<<value->payload_offset.value()<<','<<value->ordinal.value()<<']';else out<<"null";}
void snapshot(std::ostream& out,const StreamingReconstructor& stream){
    const auto s=stream.summary();const auto& r=stream.reconstruction();const auto& c=r.context();const auto& rs=r.summary();const auto& cs=c.summary();
    out<<"{\"stream\":{\"compressed_bytes\":"<<s.compressed_bytes<<",\"decompressed_bytes\":"<<s.decompressed_bytes<<",\"framing_bytes\":"<<s.framing_bytes<<",\"accepted_prefix_bytes\":"<<s.accepted_prefix_bytes<<",\"source_records\":"<<s.source_records<<",\"accepted_records\":"<<s.accepted_records<<",\"native_records\":"<<s.native_records<<",\"external_observations\":"<<s.external_observations<<",\"compressed_sha256\":\""<<hex(s.compressed_sha256)<<"\",\"decompressed_sha256\":\""<<hex(s.decompressed_sha256)<<"\",\"accepted_prefix_sha256\":\""<<hex(s.accepted_prefix_sha256)<<"\"";
    const auto flag=[&](const char* name,bool value){out<<",\""<<name<<"\":";boolean(out,value);};
    flag("gzip_member_verified",s.gzip_member_verified);flag("framer_terminated",s.framer_terminated);flag("compressed_identity_verified",s.compressed_identity_verified);flag("decompressed_identity_verified",s.decompressed_identity_verified);flag("source_complete",s.source_complete);flag("publication_eligible",s.publication_eligible);flag("paused",s.paused);flag("finished",s.finished);flag("bounded_prefix",s.bounded_prefix);
    out<<",\"residual_frame_bytes\":"<<s.residual_frame_bytes<<",\"buffered_output_bytes\":"<<s.buffered_output_bytes<<",\"error_code\":"<<static_cast<unsigned>(s.error.code)<<",\"gzip_error_code\":"<<static_cast<unsigned>(s.error.gzip.code)<<",\"observed_gzip_error_code\":"<<static_cast<unsigned>(s.observed_gzip_error.code)<<"},\"source\":{\"considered\":"<<rs.considered<<",\"context_committed\":"<<rs.context_committed<<",\"native_committed\":"<<rs.native_committed<<",\"external_observations\":"<<rs.external_observations<<",\"rejected\":"<<rs.rejected<<",\"pending\":";boolean(out,rs.pending);out<<",\"unconsidered_record\":";boolean(out,rs.unconsidered_record);out<<",\"input_complete\":";boolean(out,rs.input_complete);out<<",\"initialization_verified\":";boolean(out,rs.initialization_verified);out<<",\"eligibility\":"<<static_cast<unsigned>(rs.eligibility)<<",\"physical_position\":";location(out,rs.physical_position);out<<",\"committed_position\":";location(out,rs.committed_position);
    out<<"},\"context\":{\"accepted_records\":"<<cs.accepted_records<<",\"directories\":"<<cs.directories<<",\"lifetime_orders\":"<<cs.lifetime_orders<<",\"active_orders\":"<<cs.active_orders<<",\"matches\":"<<cs.matches<<",\"initialization_incomplete\":";boolean(out,cs.initialization_incomplete);out<<",\"session_incomplete\":";boolean(out,cs.session_incomplete);out<<",\"source_complete\":";boolean(out,cs.source_complete);out<<",\"last_timestamp_ns\":";if(cs.last_timestamp)out<<cs.last_timestamp->value();else out<<"null";
    out<<",\"orders\":[";bool comma=false;for(const auto& o:c.orders()){if(comma)out<<',';comma=true;out<<'['<<o.reference.value()<<','<<o.locate.value()<<','<<static_cast<unsigned>(o.side)<<','<<o.remaining.value()<<','<<o.resting_price.value()<<','<<o.arrival.value()<<',';boolean(out,o.active);out<<']';}
    out<<"],\"match_references\":[";comma=false;for(const auto& m:c.matches()){if(comma)out<<',';comma=true;out<<'['<<m.number.value()<<','<<m.locate.value()<<','<<static_cast<unsigned>(m.kind)<<',';boolean(out,m.broken);out<<']';}
    out<<"]},\"receipts\":[";comma=false;for(const auto& receipt:r.receipts()){if(comma)out<<',';comma=true;out<<'['<<receipt.source.location.ordinal.value()<<','<<receipt.source.location.frame_offset.value()<<','<<receipt.source.location.payload_offset.value()<<','<<static_cast<unsigned>(receipt.source.type)<<','<<receipt.source.header.stock_locate.value()<<','<<receipt.source.header.tracking_number.value()<<','<<receipt.source.header.timestamp.value()<<',';if(receipt.book_index)out<<*receipt.book_index;else out<<"null";out<<',';if(receipt.native_sequence)out<<*receipt.native_sequence;else out<<"null";out<<']';}
    out<<"],\"books\":[";
    for(std::size_t i=0;i<2;++i){
        if(i)out<<',';
        const auto* engine=r.engine(i);require(engine!=nullptr,"bound book");const auto& book=engine->book();require(!book.check_invariants(),"native invariants");std::vector<gig::RestingOrder> orders;
        for(const auto& o:c.orders()){if(o.locate.value()!=i+1)continue;auto found=book.find(number<gig::OrderId>(o.reference.value()));if(found)orders.push_back(*found);}
        require(orders.size()==book.order_count(),"native enumeration completeness");std::sort(orders.begin(),orders.end(),[](const auto& a,const auto& b){return a.order.order_id<b.order.order_id;});
        out<<"{\"instrument_id\":"<<i+1<<",\"stock_locate\":"<<i+1<<",\"derived_sequence\":"<<rs.native_counts[i]<<",\"revision\":"<<book.revision()<<",\"journal_records\":"<<engine->journal_size()<<",\"order_count\":"<<book.order_count()<<",\"remaining_quantity\":"<<book.remaining()<<",\"needs_recovery\":";boolean(out,engine->needs_recovery());out<<",\"orders\":[";comma=false;
        for(const auto& o:orders){if(comma)out<<',';comma=true;out<<'['<<o.order.order_id.value()<<','<<(o.order.side==gig::Side::buy?66:83)<<','<<o.order.price_ticks.value()<<','<<o.order.quantity.value()<<','<<o.priority<<']';}
        auto depth=book.depth(8);require(bool(depth)&&!depth.data->bid_truncated&&!depth.data->ask_truncated,"complete depth");
        const auto levels=[&](const char* name,const auto& values){out<<"],\""<<name<<"\":[";bool first=true;for(const auto& level:values){if(!first)out<<',';first=false;out<<'['<<level.price_ticks.value()<<','<<level.quantity.value()<<','<<level.order_count<<']';}};
        levels("bids",depth.data->bids);levels("asks",depth.data->asks);const auto l=book.ledger();out<<"],\"ledger\":["<<l.added<<','<<l.cancelled<<','<<l.executed<<','<<l.discarded<<','<<l.recovered<<','<<l.replacement_in<<','<<l.replacement_out<<','<<l.total_in<<','<<l.total_out<<"],\"metadata\":";
        if(!book.last_metadata())out<<"null";else{const auto& m=*book.last_metadata();require(m.provenance.dataset.data&&m.provenance.generator_seed.data&&m.sequence.data&&m.scope.data&&m.source_record.data,"native provenance");const auto& d=*m.provenance.dataset.data;
            out<<"{\"capture_ordinal\":"<<*m.capture_ordinal.data<<",\"source_record\":\""<<m.source_record.data->view()<<"\",\"sequence\":"<<m.sequence.data->value()<<",\"stream_id\":"<<m.scope.data->stream.value()<<",\"session\":\""<<m.scope.data->session.view()<<"\",\"dataset\":\""<<d.identity.view()<<"\",\"version\":\""<<d.version.data->view()<<"\",\"sha256\":\""<<d.sha256.data->view()<<"\",\"generator_seed\":"<<*m.provenance.generator_seed.data<<",\"origin\":"<<static_cast<unsigned>(*m.provenance.origin.data)<<",\"event_timestamp\":null,\"receive_timestamp\":null}";}
        out<<'}';
    }
    out<<"]}";
}
} // namespace
int main(int argc,char** argv){
    try{
        require(argc==3,"usage: gig_itch_validation_demo valid|bounded|restart|corrupt IMPLEMENTATION_SHA256");const std::string mode=argv[1],code_text=argv[2];require(mode=="valid"||mode=="bounded"||mode=="restart"||mode=="corrupt","unknown scenario");require(code_text.size()==64&&std::all_of(code_text.begin(),code_text.end(),[](char c){return (c>='0'&&c<='9')||(c>='a'&&c<='f');}),"implementation SHA256 must be64 lowercase hex characters");auto code=gig::Digest::make(code_text);require(bool(code),"implementation SHA256");
        const auto rows=records();const auto raw=binary_file(rows);const auto expected=gzip(raw);auto input=expected;if(mode=="corrupt")input[input.size()-8]^=std::byte{1};const auto config=configuration(sha256(raw),sha256(expected));gig::TrackedResource memory(std::pmr::get_default_resource(),pmr_budget);std::ostringstream final,pause,replay;bool restart_verified=false;std::size_t offset=0,coexist_peak=0;
        {
            auto stream=make_stream(config,memory);if(mode=="bounded"||mode=="restart")require(!stream.pause_after(8),"pause declaration");drive(stream,input,17,offset);
            if(mode=="restart"){
                require(stream.summary().paused,"original paused");auto checkpoint=stream.checkpoint(*code.data);require(bool(checkpoint),"logical checkpoint");snapshot(pause,stream);auto restored=make_stream(config,memory);require(!restored.pause_after(8),"restart boundary");std::size_t replay_offset=0;drive(restored,input,1,replay_offset);require(!restored.verify_checkpoint(*checkpoint.data,*code.data),"replay checkpoint");restart_verified=true;require(!stream.resume()&&!restored.resume(),"resume");drive(stream,input,17,offset);drive(restored,input,1,replay_offset);const auto a=stream.finish(),b=restored.finish();require(!a.error&&!b.error&&a.publication_eligible&&b.publication_eligible&&a.accepted_prefix_sha256==b.accepted_prefix_sha256,"restarted source verified");
                for(std::size_t i=0;i<2;++i){const auto left=stream.reconstruction().engine(i)->canonical(),right=restored.reconstruction().engine(i)->canonical();require(bool(left)&&bool(right)&&*left.data==*right.data,"restarted canonical");}
                snapshot(replay,restored);coexist_peak=memory.stats().peak_bytes;
            }else stream.finish(mode=="bounded"?EndKind::bounded_prefix:EndKind::source_eof);
            snapshot(final,stream);
        }
        const auto stats=memory.stats();require(stats.live_bytes==0&&stats.live_blocks==0,"pipeline resource release");std::ostringstream out;
        out<<"{\"schema_version\":1,\"scenario\":\""<<mode<<"\",\"provenance\":{\"origin\":\"synthetic\",\"source\":\"p1i-authored-source\",\"session\":\"p1i-authored-session\",\"fixture\":\"p1i-h18\",\"fixture_version\":1,\"generator\":\"p1i-literal-generator\",\"generator_seed\":"<<seed<<",\"initialization\":\"authored_complete_empty\",\"implementation_sha256\":\""<<code_text<<"\",\"implementation_identity_status\":\"caller_declared\",\"expected_compressed_sha256\":\""<<hex(sha256(expected))<<"\",\"actual_input_sha256\":\""<<hex(sha256(input))<<"\",\"expected_decompressed_sha256\":\""<<hex(sha256(raw))<<"\",\"declared_records\":18,\"declared_compressed_bytes\":"<<expected.size()<<",\"declared_decompressed_bytes\":"<<raw.size()<<",\"trading_date\":null,\"receive_clock\":null},\"profile\":{\"name\":\"p1i-h18-bounded-v1\",\"pmr_budget_bytes\":"<<pmr_budget<<",\"book_count\":2,\"max_orders_per_book\":8,\"max_levels_per_book\":8,\"depth_per_book\":8,\"journal_cap_per_book\":16,\"source_record_cap\":32,\"receipt_budget_bytes\":65536,\"context_directories\":2,\"context_lifetime_orders\":4,\"context_matches\":3,\"context_logical_budget_bytes\":4096,\"gzip_output_buffer_bytes\":128,\"compressed_byte_cap\":1024,\"decompressed_byte_cap\":1024,\"expansion_ratio_cap\":2,\"expansion_slack_bytes\":64,\"header_byte_cap\":64,\"framer_payload_cap\":64,\"framer_buffer_bytes\":64,\"framer_record_cap\":32,\"framer_byte_cap\":1024,\"price_tick\":[1,10000],\"quantity_lot\":[1,1],\"allow_c_book_only\":false,\"pause_after_accepted\":8},\"restart_verified\":";boolean(out,restart_verified);out<<",\"pause\":"<<(pause.str().empty()?"null":pause.str())<<",\"replayed\":"<<(replay.str().empty()?"null":replay.str())<<",\"final\":"<<final.str()<<",\"resources\":{\"allocation_attempts\":"<<stats.attempts<<",\"allocations\":"<<stats.allocations<<",\"deallocations\":"<<stats.deallocations<<",\"peak_pmr_bytes\":"<<stats.peak_bytes<<",\"restart_coexistence_peak_pmr_bytes\":"<<coexist_peak<<",\"live_pmr_bytes_after_destroy\":"<<stats.live_bytes<<",\"live_pmr_blocks_after_destroy\":"<<stats.live_blocks<<",\"scope\":\"pipeline PMR plus native queries; fixed objects, fixture and output buffers excluded\"}}";
        const auto rendered=out.str();require(rendered.size()<=128U*1024U,"bounded validation output");std::cout<<rendered<<'\n';std::cout.flush();return std::cout?0:3;
    }catch(const std::exception& error){std::cerr<<"synthetic demonstration failed: "<<error.what()<<'\n';return 2;}
}
