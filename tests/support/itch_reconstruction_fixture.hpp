#pragma once
#include "gig/itch/reconstruction.hpp"
#include <algorithm>
#include <stdexcept>
#include <string>
#include <vector>
namespace gig::itch::test {
inline void check(bool value,const char* message){if(!value)throw std::runtime_error(message);}
template<class T,class I> T number(I n){auto x=T::make(n);check(bool(x),"fixture number");return *x.data;}
inline gig::Identity identity(std::string_view s){auto x=gig::Identity::make(s);check(bool(x),"fixture identity");return *x.data;}
inline SourceIdentity source_id(std::string_view s){auto x=SourceIdentity::make(s);check(bool(x),"fixture source identity");return *x.data;}
inline Text<8> stock(std::string_view s){check(s.size()==8,"stock padding");Text<8> out;std::copy(s.begin(),s.end(),out.bytes.begin());return out;}
inline ReconstructionConfig config(){
    const auto source=source_id("p1g-native-synthetic");const auto session=source_id("p1g-session");
    Provenance provenance;provenance.origin=Origin::synthetic;provenance.source=source;provenance.sha256=std::array<std::byte,32>{};provenance.generator_seed=7707;
    SourceManifest manifest{source,session,provenance,Initialization::synthetic_history_declared};
    ContextPolicy policy;policy.max_directories=8;policy.max_lifetime_orders=128;policy.max_matches=128;
    InitializationEvidence evidence{InitialStateKind::authored_empty,source,session,source_id("literal-native-fixture"),identity("p1g-native-trace"),identity("1"),identity("private-synthetic-test-fixture"),*gig::Digest::make(std::string(64,'0')).data,7707,policy.first_location,true};
    const auto rules=[](std::uint64_t instrument){return gig::InstrumentRules{number<gig::InstrumentId>(instrument),number<gig::VenueId>(1),number<gig::PriceTicks>(1),number<gig::PriceTicks>(2000000000),number<gig::QuantityLots>(UINT64_MAX),{1,10000},{1,1}};};
    BookBinding a{stock("TEST    "),StockLocate{1},rules(1),number<gig::StreamId>(1),{128,128,16},128};
    BookBinding b{stock("TWO     "),StockLocate{2},rules(2),number<gig::StreamId>(2),{128,128,16},128};
    ReconstructionConfig out{manifest,policy,evidence,identity("p1g-native-run"),{a,b}};out.max_source_records=256;return out;
}
inline void put(std::vector<std::byte>& bytes,std::size_t at,std::uint64_t n,std::size_t width){for(std::size_t i=0;i<width;++i){bytes[at+width-i-1]=static_cast<std::byte>(n&255);n>>=8;}}
inline void text(std::vector<std::byte>& bytes,std::size_t at,std::string_view s){for(char c:s)bytes[at++]=static_cast<std::byte>(c);}
inline std::vector<std::byte> payload(char type,std::uint16_t locate=1,std::uint64_t timestamp=1){auto length=expected_length(static_cast<std::uint8_t>(type));check(length.has_value(),"fixture message type");std::vector<std::byte> bytes(*length,std::byte{});bytes[0]=static_cast<std::byte>(type);put(bytes,1,locate,2);put(bytes,5,timestamp,6);return bytes;}
inline std::vector<std::byte> system(char code='O'){auto bytes=payload('S',0);bytes[11]=static_cast<std::byte>(code);return bytes;}
inline std::vector<std::byte> directory(std::uint16_t locate=1,std::string_view symbol="TEST    "){auto bytes=payload('R',locate);text(bytes,11,symbol);bytes[19]=std::byte{'Q'};bytes[20]=std::byte{'N'};put(bytes,21,100,4);text(bytes,25,"NC  P N1N");bytes[38]=std::byte{'N'};return bytes;}
inline std::vector<std::byte> add(std::uint64_t id=101,std::uint32_t quantity=10,std::uint32_t price=100,std::uint16_t locate=1,char side='B',bool attributed=false){auto bytes=payload(attributed?'F':'A',locate);put(bytes,11,id,8);bytes[19]=static_cast<std::byte>(side);put(bytes,20,quantity,4);text(bytes,24,locate==1?"TEST    ":"TWO     ");put(bytes,32,price,4);if(attributed)text(bytes,36,"MPID");return bytes;}
inline std::vector<std::byte> reduce(char type,std::uint64_t id,std::uint32_t quantity=1,std::uint64_t match=1,std::uint16_t locate=1,std::uint32_t execution_price=101,char printable='Y'){auto bytes=payload(type,locate);put(bytes,11,id,8);if(type!='D')put(bytes,19,quantity,4);if(type=='E'||type=='C')put(bytes,23,match,8);if(type=='C'){bytes[31]=static_cast<std::byte>(printable);put(bytes,32,execution_price,4);}return bytes;}
inline std::vector<std::byte> replace(std::uint64_t old,std::uint64_t next,std::uint32_t quantity,std::uint32_t price=101,std::uint16_t locate=1){auto bytes=payload('U',locate);put(bytes,11,old,8);put(bytes,19,next,8);put(bytes,27,quantity,4);put(bytes,31,price,4);return bytes;}
inline std::vector<std::byte> trade(std::uint64_t match=50,std::uint16_t locate=1){auto bytes=payload('P',locate);bytes[19]=std::byte{'B'};put(bytes,20,3,4);text(bytes,24,locate==1?"TEST    ":"TWO     ");put(bytes,32,100,4);put(bytes,36,match,8);return bytes;}
inline std::vector<std::byte> cross(std::uint64_t match=51,std::uint16_t locate=1){auto bytes=payload('Q',locate);text(bytes,19,locate==1?"TEST    ":"TWO     ");put(bytes,27,100,4);put(bytes,31,match,8);bytes[39]=std::byte{'O'};return bytes;}
inline std::vector<std::byte> broken(std::uint64_t match=50,std::uint16_t locate=1){auto bytes=payload('B',locate);put(bytes,11,match,8);return bytes;}
inline SyntheticReconstructor reconstructor(ReconstructionConfig c=config(),std::pmr::memory_resource* resource=std::pmr::get_default_resource()){auto created=SyntheticReconstructor::create(std::move(c),resource);check(bool(created),"fixture reconstructor creation");return std::move(*created.data);}
struct Harness {
    SyntheticReconstructor reconstruction;std::uint64_t offset{},ordinal{};
    explicit Harness(ReconstructionConfig c=config(),std::pmr::memory_resource* resource=std::pmr::get_default_resource()):reconstruction(reconstructor(std::move(c),resource)){}
    Location location()const{return {ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}};}
    ReconstructionStep process(const std::vector<std::byte>& bytes,Provenance provenance={}){auto result=reconstruction.process(bytes,location(),std::move(provenance));if(result.committed){offset+=bytes.size()+2;++ordinal;}return result;}
    void accept(const std::vector<std::byte>& bytes){check(process(bytes).committed,"fixture accepted record");}
    void setup(){accept(system());accept(directory());accept(directory(2,"TWO     "));}
    const gig::OrderBook& book(std::size_t i=0)const{return reconstruction.engine(i)->book();}
};
inline std::string state(const SyntheticReconstructor& r){std::string out;for(std::size_t i=0;i<r.config().book_count;++i){auto canonical=r.engine(i)->book().canonical();check(bool(canonical),"book canonical query");out.append(canonical.data->begin(),canonical.data->end());out+='|';out+=std::to_string(r.engine(i)->journal_size());out+='|';}return out;}
} // namespace gig::itch::test
