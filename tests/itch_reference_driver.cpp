#include "gig/itch/decoder.hpp"
#include "gig/itch/binary_file.hpp"
#include <algorithm>
#include <array>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <type_traits>
using namespace gig::itch;
namespace {
std::string hex(std::string_view s){ constexpr char digits[]="0123456789abcdef"; std::string out; for(char c:s){auto b=static_cast<unsigned char>(c);out+=digits[b>>4];out+=digits[b&15];}return out; }
std::string hex(std::span<const std::byte> s){return hex({reinterpret_cast<const char*>(s.data()),s.size()});}
void error(const Error&e){std::cout<<"ERR,"<<static_cast<unsigned>(e.code)<<','<<e.offset.value()<<','<<e.field<<','<<e.expected<<','<<e.actual;}
template<class T> void number(T n){std::cout<<','<<n.value();}
void add(const AddOrder&a){number(a.order_reference);std::cout<<','<<static_cast<unsigned>(a.side);number(a.shares);std::cout<<','<<hex(a.stock.view());number(a.price);}
void execution(const OrderExecuted&a){number(a.order_reference);number(a.executed_shares);number(a.match_number);}
void decoded(const DecodedRecord&r){std::cout<<"OK,"<<static_cast<unsigned>(r.type);number(r.header.stock_locate);number(r.header.tracking_number);number(r.header.timestamp);
std::visit([](const auto&v){using T=std::decay_t<decltype(v)>;
if constexpr(std::is_same_v<T,SystemEvent>)std::cout<<','<<static_cast<unsigned>(v.event_code);
else if constexpr(std::is_same_v<T,StockDirectory>){std::cout<<','<<hex(v.stock.view())<<','<<static_cast<unsigned>(v.market_category)<<','<<static_cast<unsigned>(v.financial_status)<<','<<v.round_lot_size<<','<<static_cast<unsigned>(v.round_lots_only)<<','<<static_cast<unsigned>(v.issue_classification)<<','<<hex(v.issue_subtype.view())<<','<<static_cast<unsigned>(v.authenticity)<<','<<static_cast<unsigned>(v.short_sale_threshold)<<','<<static_cast<unsigned>(v.ipo_flag)<<','<<static_cast<unsigned>(v.luld_tier)<<','<<static_cast<unsigned>(v.etp_flag)<<','<<v.etp_leverage<<','<<static_cast<unsigned>(v.inverse);}
else if constexpr(std::is_same_v<T,AddOrder>)add(v);
else if constexpr(std::is_same_v<T,AddAttributedOrder>){add(v.order);std::cout<<','<<hex(v.attribution.view());}
else if constexpr(std::is_same_v<T,OrderExecuted>)execution(v);
else if constexpr(std::is_same_v<T,OrderExecutedWithPrice>){execution(v.execution);std::cout<<','<<static_cast<unsigned>(v.printable);number(v.execution_price);}
else if constexpr(std::is_same_v<T,OrderCancel>){number(v.order_reference);number(v.cancelled_shares);}
else if constexpr(std::is_same_v<T,OrderDelete>)number(v.order_reference);
else if constexpr(std::is_same_v<T,OrderReplace>){number(v.original_reference);number(v.new_reference);number(v.shares);number(v.price);}
else if constexpr(std::is_same_v<T,Trade>){number(v.order_reference);std::cout<<','<<static_cast<unsigned>(v.side);number(v.shares);std::cout<<','<<hex(v.stock.view());number(v.price);number(v.match_number);}
else if constexpr(std::is_same_v<T,CrossTrade>){number(v.shares);std::cout<<','<<hex(v.stock.view());number(v.cross_price);number(v.match_number);std::cout<<','<<static_cast<unsigned>(v.cross_type);}
else if constexpr(std::is_same_v<T,BrokenTrade>)number(v.match_number);
},r.message);std::cout<<",LOC,"<<r.location.frame_offset.value()<<','<<r.location.payload_offset.value()<<','<<r.location.ordinal.value()<<",PROV,"<<static_cast<unsigned>(r.provenance.origin)<<','<<(r.provenance.source?hex(r.provenance.source->view()):"-")<<','<<(r.provenance.generator_seed?std::to_string(*r.provenance.generator_seed):"-")<<','<<(r.provenance.sha256?hex(std::span<const std::byte>(*r.provenance.sha256)):"-");}
}
int main(){std::string line;while(std::getline(std::cin,line)){std::istringstream in(line);char mode{};std::string encoded;std::size_t chunk=1;in>>mode;if(mode=='F')in>>chunk;in>>encoded;std::vector<std::byte> data;if(encoded!="-"){if(encoded.size()%2){std::cout<<"DRIVER_ERROR\n";continue;}for(std::size_t i=0;i<encoded.size();i+=2)data.push_back(static_cast<std::byte>(std::stoul(encoded.substr(i,2),nullptr,16)));}
if(mode=='D'){Provenance p;p.origin=Origin::synthetic;p.source=SourceIdentity::make("synthetic-reference").data;p.generator_seed=1729;std::array<std::byte,32> digest{};for(std::size_t i=0;i<digest.size();++i)digest[i]=static_cast<std::byte>(i);p.sha256=digest;auto r=decode(data,{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}},p);if(r)decoded(*r.data);else error(r.error);}
else if(mode=='F'&&chunk>0){auto f=BinaryFileFramer::create();if(!f){error(f.error);}else{bool failed=false;std::size_t pos=0;while(pos<data.size()&&!failed){const auto end=std::min(data.size(),pos+chunk);while(pos<end){auto r=f.data->feed(std::span<const std::byte>(data).subspan(pos,end-pos));pos+=r.consumed;if(r.frame){const auto&v=*r.frame;std::cout<<"R,"<<v.location.frame_offset.value()<<','<<v.location.payload_offset.value()<<','<<v.location.ordinal.value()<<','<<hex(v.payload)<<';';}if(r.error){error(r.error);failed=true;break;}if(r.consumed==0){std::cout<<"NO_PROGRESS";failed=true;break;}}}if(!failed){auto r=f.data->finish();if(r.error)error(r.error);else std::cout<<"END,"<<r.session_complete<<','<<r.bounded_prefix<<','<<r.residual_bytes;}}}else {std::cout<<"DRIVER_ERROR";}
std::cout<<'\n';}}
