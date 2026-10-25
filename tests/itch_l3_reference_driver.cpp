#include "gig/itch/reconstruction.hpp"
#include "gig/itch/input_adapter.hpp"
#include "gig/itch/seed.hpp"
#include <chrono>
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
bool seed_case(std::istringstream& input,ReconstructionConfig config,gig::TrackedResource& resource,std::size_t chunk){
    std::uint64_t offset{},ordinal{},timestamp{};unsigned stage{};std::size_t count{};
    if(!(input>>offset>>ordinal>>stage>>timestamp>>count)||count>128||stage>5||offset>UINT64_MAX-2)return false;
    std::vector<SeedOrder> orders;orders.reserve(count);
    for(std::size_t i=0;i<count;++i){std::uint64_t ref{},quantity{},price{},priority{},arrival{};unsigned locate{},side{};
        if(!(input>>ref>>locate>>side>>quantity>>price>>priority>>arrival)||locate<1||locate>2||quantity>UINT32_MAX||price>UINT32_MAX||side>255)return false;
        orders.push_back({{OrderReference{ref},StockLocate{static_cast<std::uint16_t>(locate)},stock(locate==1?"TEST    ":"TWO     "),static_cast<Side>(side),Shares{static_cast<std::uint32_t>(quantity)},Price4{static_cast<std::uint32_t>(price)},{},RecordOrdinal{arrival},true},priority});
    }
    if(!(input>>count)||count>4096){return false;}std::vector<OrderReference> retired;retired.reserve(count);
    for(std::size_t i=0;i<count;++i){std::uint64_t ref{};if(!(input>>ref))return false;retired.push_back(OrderReference{ref});}
    if(!(input>>count)||count>4096){return false;}std::vector<MatchState> matches;matches.reserve(count);
    for(std::size_t i=0;i<count;++i){std::uint64_t match{};unsigned locate{},kind{},broken{};if(!(input>>match>>locate>>kind>>broken)||locate>65535||kind>2||broken>1)return false;matches.push_back({MatchNumber{match},StockLocate{static_cast<std::uint16_t>(locate)},static_cast<MatchKind>(kind),broken!=0});}
    std::array<SeedDirectory,2> directories;std::string encoded;
    for(auto& directory:directories){if(!(input>>encoded)||encoded.size()!=78)return false;for(std::size_t i=0;i<39;++i)directory.payload[i]=static_cast<std::byte>(std::stoul(encoded.substr(i*2,2),nullptr,16));}
    std::string expected;if(!(input>>expected)||expected.size()!=64)return false;Sha256Digest trusted{};
    for(std::size_t i=0;i<32;++i)trusted[i]=static_cast<std::byte>(std::stoul(expected.substr(i*2,2),nullptr,16));
    SeedState seed{{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},static_cast<std::uint8_t>(stage),TimestampNanoseconds{timestamp},directories,orders,retired,matches};
    config.initialization.kind=InitialStateKind::complete_seed;config.initialization.boundary=seed.boundary;config.context_policy.first_location=seed.boundary;
    const auto start=std::chrono::steady_clock::now();auto created=SyntheticReconstructor::create_seeded(config,seed,trusted,&resource);
    const auto initialized=std::chrono::steady_clock::now();if(!created){std::cerr<<"seed create "<<created.error.field<<'\n';return false;}
    auto& r=*created.data;std::cout<<"{\"seed_sha256\":\""<<expected<<"\",\"initial\":";ReconstructionStep initial;initial.committed=true;initial.disposition=SourceDisposition::external_observation;outcome(initial,r);
    Bytes bytes;while(input>>encoded){if(encoded.empty()||encoded.size()%2||encoded.size()>131070)return false;raw(bytes,encoded.size()/2,2);for(std::size_t i=0;i<encoded.size();i+=2)bytes.push_back(static_cast<std::byte>(std::stoul(encoded.substr(i,2),nullptr,16)));if(bytes.size()>2U*1024U*1024U)return false;}
    bytes.push_back(std::byte{});bytes.push_back(std::byte{});FramerLimits limits;limits.max_stream_bytes=2U*1024U*1024U;limits.max_records=config.max_source_records;
    auto reader=BinaryFileFramer::create(limits,seed.boundary.frame_offset,seed.boundary.ordinal,&resource);if(!reader)return false;
    std::cout<<",\"events\":[";bool comma=false;std::size_t consumed=0;
    const auto replay_start=std::chrono::steady_clock::now();
    while(consumed<bytes.size()){const auto frame=reader.data->feed(std::span<const std::byte>(bytes).subspan(consumed,std::min(chunk,bytes.size()-consumed)));if(frame.error||!frame.consumed)return false;consumed+=frame.consumed;
        if(frame.frame){const auto step=r.process(frame.frame->payload,frame.frame->location,config.source.provenance);if(comma)std::cout<<',';comma=true;outcome(step,r);if(!step.committed)break;}}
    const auto replay_end=std::chrono::steady_clock::now();
    std::cout<<"],\"journal_sha256\":[";for(std::size_t i=0;i<2;++i){const auto canonical=r.engine(i)->canonical();if(!canonical)return false;const auto digest=hex_digest(sha256(std::as_bytes(std::span(canonical.data->data(),canonical.data->size()))));if(i)std::cout<<',';std::cout<<'\"'<<std::string_view(digest.data(),digest.size())<<'\"';}
    const auto memory=resource.stats();std::cout<<"],\"measurements\":{\"initialization_ns\":"<<std::chrono::duration_cast<std::chrono::nanoseconds>(initialized-start).count()<<",\"replay_ns\":"<<std::chrono::duration_cast<std::chrono::nanoseconds>(replay_end-replay_start).count()<<",\"pmr_peak_bytes\":"<<memory.peak_bytes<<",\"pmr_allocations\":"<<memory.allocations<<",\"journal_record_bytes\":"<<gig::ReplayEngine::journal_record_bytes()<<",\"seed_records\":2,\"observed_qualified\":false}}\n";return true;
}
bool adapter_case(std::istringstream& input,ReconstructionConfig config,gig::TrackedResource& resource,std::size_t chunk,std::string_view dataset_id){
    Bytes bytes;std::string encoded;
    while(input>>encoded){
        if(encoded.size()%2||encoded.size()>131070){std::cerr<<"adapter fixture hex bound\n";return false;}
        const auto size=encoded.size()/2;bytes.push_back(static_cast<std::byte>(size>>8U));bytes.push_back(static_cast<std::byte>(size&255U));
        for(std::size_t i=0;i<encoded.size();i+=2)bytes.push_back(static_cast<std::byte>(std::stoul(encoded.substr(i,2),nullptr,16)));
        if(bytes.size()>2U*1024U*1024U){std::cerr<<"adapter fixture byte bound\n";return false;}
    }
    bytes.push_back(std::byte{});bytes.push_back(std::byte{});
    DatasetContract dataset{source_identity("independent-authored"),source_identity(dataset_id),source_identity("literal-generator"),source_identity("synthetic-test-permitted"),source_identity("no-market-data"),source_identity("authored-empty-evidence"),{},ByteOffset{0},ByteOffset{bytes.size()},false};
    FramerLimits limits;limits.max_records=config.max_source_records;limits.max_stream_bytes=8U*1024U*1024U;
    InputAdapterConfig input_config{dataset,config.source,config.context_policy,limits,InitialClaim::authored_synthetic,config};
    auto created=BinarySourceAdapter::create(input_config,&resource);if(!created){std::cerr<<"adapter create "<<created.error.field<<'\n';return false;}
    auto& adapter=*created.data;std::size_t offset=0;bool comma=false;std::cout<<"{\"events\":[";
    while(offset<bytes.size()){
        const auto count=std::min(chunk,bytes.size()-offset);const auto step=adapter.feed(std::span<const std::byte>(bytes).subspan(offset,count));offset+=step.consumed;
        if(step.frame){if(comma)std::cout<<',';comma=true;outcome(step.native,*adapter.reconstruction());}
        if(step.error)break;
        if(!step.consumed){std::cerr<<"adapter stalled\n";return false;}
    }
    const auto summary=adapter.finish();const auto digest=hex_digest(summary.input_sha256);
    std::cout<<"],\"summary\":{\"records\":"<<summary.records<<",\"accepted\":"<<summary.accepted<<",\"native\":"<<summary.native_records
             <<",\"dataset_hex\":\""<<hex(dataset_id)<<"\",\"rejected\":"<<summary.rejected<<",\"bytes\":"<<summary.bytes<<",\"error\":"<<static_cast<unsigned>(summary.error.code)
             <<",\"input_complete\":"<<(summary.input_complete?"true":"false")<<",\"l3_complete\":"<<(summary.full_l3_complete?"true":"false")
             <<",\"publication_eligible\":"<<(summary.publication_eligible?"true":"false")<<",\"input_sha256\":\""<<std::string_view(digest.data(),digest.size())<<"\"}}\n";
    return true;
}

}
int main(int argc,char** argv){
    const bool use_seed=argc>1&&std::string_view(argv[1])=="--seed";
    const bool use_adapter=argc>1&&std::string_view(argv[1])=="--adapter";
    if(argc>4||(argc>1&&!use_adapter&&!use_seed))return 5;
    const auto dataset=SourceIdentity::make(argc==4?argv[3]:"adapter-differential-v1");if(!dataset)return 5;
    const auto chunk=argc>=3?static_cast<std::size_t>(std::stoul(argv[2])):std::size_t{7};
    if(chunk==0||chunk>65536)return 5;
    bool oversized=false;std::string line;
    const auto next=[&](){
        if(!use_adapter&&!use_seed)return static_cast<bool>(std::getline(std::cin,line));
        line.clear();char value{};
        while(std::cin.get(value)){if(value=='\n')return true;if(line.size()==2U*1024U*1024U){oversized=true;std::cerr<<"adapter fixture line limit\n";return false;}line.push_back(value);}
        return !line.empty();
    };
    while(next()){gig::TrackedResource resource(std::pmr::get_default_resource(),128*1024*1024);{std::istringstream input(line);unsigned flags{};gig::types::UnitScale tick{},lots{};input>>flags>>tick.numerator>>tick.denominator>>lots.numerator>>lots.denominator;std::string digest_text;input>>digest_text;
    if((use_adapter||use_seed)&&(!input||flags>7||digest_text.size()!=64||!std::all_of(digest_text.begin(),digest_text.end(),[](char c){return (c>='0'&&c<='9')||(c>='a'&&c<='f');})
        ||!tick.numerator||!tick.denominator||!lots.numerator||!lots.denominator||tick.numerator>1000000||tick.denominator>1000000||lots.numerator>1000000||lots.denominator>1000000)){std::cerr<<"adapter fixture metadata\n";return 5;}
    auto config=configuration(flags,tick,lots,digest_text);if(use_seed){if(!seed_case(input,config,resource,chunk))return 2;}else if(use_adapter){if(!adapter_case(input,config,resource,chunk,dataset.data->view()))return 2;}else{auto reconstruction=SyntheticReconstructor::create(config,&resource);if(!reconstruction){std::cerr<<"create: "<<static_cast<unsigned>(reconstruction.error.code)<<' '<<reconstruction.error.field<<'\n';return 2;}
    std::cout<<'[';std::string encoded;std::uint64_t offset=0,ordinal=0;bool comma=false;while(input>>encoded){Bytes payload;for(std::size_t i=0;i<encoded.size();i+=2)payload.push_back(static_cast<std::byte>(std::stoul(encoded.substr(i,2),nullptr,16)));const auto step=reconstruction.data->process(payload,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},config.source.provenance);if(comma)std::cout<<',';comma=true;outcome(step,*reconstruction.data);if(step.committed){offset+=payload.size()+2;++ordinal;}else break;}
    std::cout<<"]\n";
}}if(resource.stats().live_bytes!=0){std::cerr<<"driver PMR leak\n";return 4;}}return oversized?5:0;}
