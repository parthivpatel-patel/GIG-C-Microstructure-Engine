#include "gig/lobster/adapter.hpp"
#include <charconv>
#include <limits>
namespace gig::lobster {
namespace {
std::string_view trim_end(std::string_view s) noexcept {if(!s.empty()&&s.back()=='\n')s.remove_suffix(1);if(!s.empty()&&s.back()=='\r')s.remove_suffix(1);return s;}
template<std::size_t N> bool columns(std::string_view line,std::array<std::string_view,N>& fields) noexcept {
    line=trim_end(line);if(line.empty()||line.size()>4096)return false;
    for(std::size_t i=0;i<N;++i){const auto at=line.find(',');if(i+1==N){if(at!=std::string_view::npos||line.empty())return false;fields[i]=line;return true;}
        if(at==std::string_view::npos||at==0){return false;}fields[i]=line.substr(0,at);line.remove_prefix(at+1);}
    return false;
}
template<class T> bool integer(std::string_view s,T& value) noexcept {if(s.empty()||s.front()=='+')return false;const auto result=std::from_chars(s.data(),s.data()+s.size(),value);return result.ec==std::errc{}&&result.ptr==s.data()+s.size();}
bool timestamp(std::string_view s,std::uint64_t& out) noexcept {
    const auto dot=s.find('.');const auto seconds=s.substr(0,dot);std::uint64_t sec{};
    if(seconds.size()>5||!integer(seconds,sec)||sec>=86400)return false;
    out=sec*1000000000ULL;
    if(dot!=std::string_view::npos){const auto fraction=s.substr(dot+1);if(fraction.empty()||fraction.size()>9)return false;
        std::uint64_t n{};for(char c:fraction){if(c<'0'||c>'9')return false;n=n*10+static_cast<unsigned>(c-'0');}
        for(std::size_t i=fraction.size();i<9;++i){n*=10;}out+=n;}
    return true;
}
}
gig::Result<Message> parse_message(std::string_view line) noexcept {
    std::array<std::string_view,6> f{};if(!columns(line,f))return gig::Result<Message>::failure(gig::ErrorCode::malformed,"lobster.message.columns");
    Message m{};if(!timestamp(f[0],m.time.value))return gig::Result<Message>::failure(gig::ErrorCode::invalid_range,"lobster.message.time");
    if(!integer(f[1],m.code)||!integer(f[2],m.order)||!integer(f[3],m.quantity.value)||!integer(f[4],m.price.value)||!integer(f[5],m.direction))return gig::Result<Message>::failure(gig::ErrorCode::malformed,"lobster.message.integer");
    m.kind=Kind::unsupported;
    switch(m.code){case 1:m.kind=Kind::add;break;case 2:m.kind=Kind::cancel;break;case 3:m.kind=Kind::erase;break;case 4:m.kind=Kind::visible_execution;break;case 5:m.kind=Kind::hidden_execution;break;case 7:m.kind=Kind::halt;break;default:break;}
    if(m.kind==Kind::halt){if(m.order||m.quantity.value||m.direction!=-1||m.price.value< -1||m.price.value>1)return gig::Result<Message>::failure(gig::ErrorCode::invalid_range,"lobster.halt.fields");}
    else if(m.kind!=Kind::unsupported){
        if((m.direction!=1&&m.direction!=-1)||m.quantity.value==0||m.price.value<=0||(m.kind!=Kind::hidden_execution&&m.order==0))return gig::Result<Message>::failure(gig::ErrorCode::invalid_range,"lobster.message.semantic_fields");}
    return gig::Result<Message>::success(m);
}
gig::Result<Reference> parse_reference(std::string_view line) noexcept {
    std::array<std::string_view,20> f{};if(!columns(line,f))return gig::Result<Reference>::failure(gig::ErrorCode::malformed,"lobster.reference.columns");
    Reference out{};
    for(std::size_t i=0;i<5;++i){for(std::size_t side=0;side<2;++side){const auto offset=4*i+2*side;Level level{};
        if(!integer(f[offset],level.price.value)||!integer(f[offset+1],level.quantity.value))return gig::Result<Reference>::failure(gig::ErrorCode::malformed,"lobster.reference.integer");
        const auto sentinel=side==0?9999999999LL:-9999999999LL;level.missing=level.price.value==sentinel;
        if((level.missing&&level.quantity.value!=0)||(!level.missing&&(level.price.value<=0||level.price.value==9999999999LL)))return gig::Result<Reference>::failure(gig::ErrorCode::invalid_range,"lobster.reference.sentinel_price");
        auto& levels=side==0?out.asks:out.bids;
        if(i&&((levels[i-1].missing&&!level.missing)||(!level.missing&&(side==0?level.price.value<=levels[i-1].price.value:level.price.value>=levels[i-1].price.value))))return gig::Result<Reference>::failure(gig::ErrorCode::ordering_error,"lobster.reference.level_order");
        out.missing_levels+=level.missing?1U:0U;out.zero_volume=out.zero_volume||(!level.missing&&level.quantity.value==0);levels[i]=level;
    }}
    if(!out.asks[0].missing&&!out.bids[0].missing){out.locked=out.bids[0].price==out.asks[0].price;out.crossed=out.bids[0].price.value>out.asks[0].price.value;}
    return gig::Result<Reference>::success(out);
}
PairedValidator::PairedValidator(Limits limits) noexcept:limits_(limits),start_(std::chrono::steady_clock::now()){}
gig::Result<PairedValidator> PairedValidator::create(Limits l) noexcept {
    if(l.max_bytes==0||l.max_bytes>1024ULL*1024ULL*1024ULL||l.max_records==0||l.max_records>10000000||l.max_line_bytes==0||l.max_line_bytes>4096||l.max_milliseconds==0||l.max_milliseconds>3600000||l.max_errors!=1)return gig::Result<PairedValidator>::failure(gig::ErrorCode::invalid_range,"lobster.limits");
    return gig::Result<PairedValidator>::success(PairedValidator(l));
}
gig::Result<Pair> PairedValidator::accept(std::string_view message,std::string_view reference) noexcept {
    const auto fail=[&](gig::ErrorCode code,std::string_view field){++summary_.rejected;summary_.stopped=true;return gig::Result<Pair>::failure(code,field);};
    if(summary_.stopped||summary_.input_complete)return gig::Result<Pair>::failure(gig::ErrorCode::inconsistent_state,"lobster.stopped");
    if(message.size()>limits_.max_line_bytes||reference.size()>limits_.max_line_bytes||summary_.accepted==limits_.max_records)return fail(gig::ErrorCode::capacity,"lobster.row_budget");
    const auto bytes=message.size()+reference.size();if(bytes>limits_.max_bytes-summary_.bytes)return fail(gig::ErrorCode::capacity,"lobster.byte_budget");
    if(std::chrono::steady_clock::now()-start_>std::chrono::milliseconds(limits_.max_milliseconds))return fail(gig::ErrorCode::capacity,"lobster.deadline");
    const auto m=parse_message(message);if(!m)return fail(m.error.code,m.error.field);const auto r=parse_reference(reference);if(!r)return fail(r.error.code,r.error.field);
    if(summary_.last&&m.data->time.value<summary_.last->value)return fail(gig::ErrorCode::ordering_error,"lobster.time_regression");
    if(!summary_.first){summary_.first=m.data->time;}summary_.last=m.data->time;++summary_.accepted;summary_.bytes+=bytes;
    ++summary_.codes[m.data->code<8?m.data->code:0];summary_.unsupported+=m.data->kind==Kind::unsupported?1U:0U;
    summary_.locked+=r.data->locked?1U:0U;summary_.crossed+=r.data->crossed?1U:0U;summary_.zero_volume+=r.data->zero_volume?1U:0U;summary_.missing_levels+=r.data->missing_levels;
    return gig::Result<Pair>::success({*m.data,*r.data});
}
gig::Error PairedValidator::finish(bool a,bool b) noexcept {if(summary_.stopped)return {gig::ErrorCode::inconsistent_state,"lobster.stopped"};if(!a||!b){summary_.stopped=true;return {gig::ErrorCode::inconsistent_metadata,"lobster.row_alignment"};}summary_.input_complete=true;return {};}
} // namespace gig::lobster
