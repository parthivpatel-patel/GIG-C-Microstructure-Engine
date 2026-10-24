#include "gig/itch/decoder.hpp"
#include <limits>

namespace gig::itch {
std::optional<std::size_t> expected_length(std::uint8_t type) noexcept {
    switch(type){
    case 'S':return 12;case 'R':return 39;case 'H':return 25;case 'Y':return 20;
    case 'L':return 26;case 'V':return 35;case 'W':return 12;case 'K':return 28;
    case 'J':return 35;case 'h':return 21;case 'A':return 36;case 'F':return 40;
    case 'E':return 31;case 'C':return 36;case 'X':return 23;case 'D':return 19;
    case 'U':return 35;case 'P':return 44;case 'Q':return 40;case 'B':return 19;
    case 'I':return 50;case 'N':return 20;case 'O':return 48;default:return std::nullopt;
    }
}
namespace {
struct Reader {
    std::span<const std::byte> bytes; Location location; Error error{};
    std::uint64_t number(std::size_t at,std::size_t width)const noexcept {
        std::uint64_t out=0;
        for(std::size_t i=0;i<width;++i) out=(out<<8U)|std::to_integer<std::uint8_t>(bytes[at+i]);
        return out;
    }
    char character(std::size_t at)const noexcept { return static_cast<char>(std::to_integer<unsigned char>(bytes[at])); }
    void bad(Code code,std::size_t at,std::string_view field,std::uint64_t expected,std::uint64_t actual) noexcept {
        if(!error) error={code,ByteOffset{location.payload_offset.value()+at},field,expected,actual};
    }
    char enumeration(std::size_t at,std::string_view choices,std::string_view field) noexcept {
        const auto c=character(at);
        if(choices.find(c)==std::string_view::npos) bad(Code::invalid_enum,at,field,0,number(at,1));
        return c;
    }
    template<std::size_t N> Text<N> text(std::size_t at,std::string_view field) noexcept {
        Text<N> out;
        for(std::size_t i=0;i<N;++i){
            const auto c=number(at+i,1);
            if(c<32||c>126) bad(Code::invalid_value,at+i,field,0,c);
            out.bytes[i]=character(at+i);
        }
        return out;
    }
    Price4 price(std::size_t at,std::string_view field) noexcept {
        auto n=number(at,4);if(n>2000000000ULL)bad(Code::invalid_value,at,field,2000000000,n);
        return Price4{static_cast<std::uint32_t>(n)};
    }
    OrderReference reference(std::size_t at,std::string_view)noexcept {return OrderReference{number(at,8)};}
    Shares shares(std::size_t at,std::string_view)noexcept{return Shares{static_cast<std::uint32_t>(number(at,4))};}
    AddOrder add()noexcept{return {reference(11,"order_reference"),static_cast<Side>(enumeration(19,"BS","side")),shares(20,"shares"),text<8>(24,"stock"),price(32,"price")};}
    OrderExecuted executed()noexcept{return {reference(11,"order_reference"),shares(19,"executed_shares"),MatchNumber{number(23,8)}};}
};
}
Result<DecodedRecord> decode(std::span<const std::byte> payload,Location location,Provenance provenance) noexcept {
    return decode(payload,location,std::move(provenance),DecodeProfile::baseline_v1);
}
Result<DecodedRecord> decode(std::span<const std::byte> payload,Location location,Provenance provenance,DecodeProfile profile) noexcept {
    constexpr auto max=std::numeric_limits<std::uint64_t>::max();
    if(location.frame_offset.value()>max-2 || location.payload_offset.value()>max-payload.size())
        return Result<DecodedRecord>::failure({Code::offset_overflow,location.frame_offset,"location",0,0});
    if(location.payload_offset.value()!=location.frame_offset.value()+2)
        return Result<DecodedRecord>::failure({Code::invalid_location,location.payload_offset,"payload_offset",location.frame_offset.value()+2,location.payload_offset.value()});
    if(static_cast<unsigned>(provenance.origin)>static_cast<unsigned>(Origin::observed))
        return Result<DecodedRecord>::failure({Code::invalid_enum,location.payload_offset,"provenance.origin",0,static_cast<unsigned>(provenance.origin)});
    if(static_cast<unsigned>(profile)>static_cast<unsigned>(DecodeProfile::retained_2023_auctions_v4))
        return Result<DecodedRecord>::failure({Code::invalid_enum,location.payload_offset,"decode.profile",0,static_cast<unsigned>(profile)});
    if(payload.empty())return Result<DecodedRecord>::failure({Code::truncated_payload,location.payload_offset,"type",1,0});
    const auto type=std::to_integer<std::uint8_t>(payload[0]);
    const auto length=expected_length(type);
    if(!length)return Result<DecodedRecord>::failure({Code::unknown_type,location.payload_offset,"type",0,type});
    if(payload.size()!=*length)return Result<DecodedRecord>::failure({Code::length_mismatch,location.payload_offset,"payload",*length,payload.size()});
    Reader r{payload,location};
    DecodedRecord out;
    out.type=type;out.location=location;out.provenance=provenance;
    out.header={StockLocate{static_cast<std::uint16_t>(r.number(1,2))},TrackingNumber{static_cast<std::uint16_t>(r.number(3,2))},TimestampNanoseconds{r.number(5,6)}};
    switch(type){
    case 'K':case 'J':case 'I':case 'O':{
        if(profile!=DecodeProfile::retained_2023_auctions_v4)
            return Result<DecodedRecord>::failure({Code::unsupported_type,location.payload_offset,"type",0,type});
        switch(type){
        case 'K':out.message=IpoQuotingUpdate{r.text<8>(11,"stock"),static_cast<std::uint32_t>(r.number(19,4)),r.enumeration(23,"AC","ipo_qualifier"),r.price(24,"ipo_price")};break;
        case 'J':out.message=LuldAuctionCollar{r.text<8>(11,"stock"),r.price(19,"collar_reference"),r.price(23,"collar_upper"),r.price(27,"collar_lower"),static_cast<std::uint32_t>(r.number(31,4))};break;
        case 'I':{NetOrderImbalance n;n.paired=r.number(11,8);n.imbalance=r.number(19,8);n.direction=r.enumeration(27,"BSNOP","imbalance_direction");n.stock=r.text<8>(28,"stock");n.far=r.price(36,"far_price");n.near=r.price(40,"near_price");n.reference=r.price(44,"reference_price");n.cross_type=r.enumeration(48,"OCHA","imbalance_cross");n.variation=r.enumeration(49,"L123456789ABC ","price_variation");out.message=n;break;}
        case 'O':out.message=DirectListingDiscovery{r.text<8>(11,"stock"),r.enumeration(19,"NY","open_eligibility"),r.price(20,"minimum_price"),r.price(24,"maximum_price"),r.price(28,"near_price"),r.number(32,8),r.price(40,"lower_collar"),r.price(44,"upper_collar")};break;
        default:break;
        }
        break;
    }
    case 'L':case 'V':case 'W':case 'h':case 'N':{
        if(profile<DecodeProfile::administrative_observations_v3)
            return Result<DecodedRecord>::failure({Code::unsupported_type,location.payload_offset,"type",0,type});
        // Exact source observations only; no book, auction or regulatory enforcement.
        switch(type){
        case 'L':out.message=MarketParticipantPosition{r.text<4>(11,"mpid"),r.text<8>(15,"stock"),
            r.enumeration(23,"YN","primary_market_maker"),r.enumeration(24,"NPSRL","market_maker_mode"),
            r.enumeration(25,"AEWSD","participant_state")};break;
        case 'V':out.message=MwcbDeclineLevels{Price8{r.number(11,8)},Price8{r.number(19,8)},Price8{r.number(27,8)}};break;
        case 'W':out.message=MwcbStatus{r.enumeration(11,"123","breached_level")};break;
        case 'h':out.message=OperationalHalt{r.text<8>(11,"stock"),r.enumeration(19,"QBX","market"),r.enumeration(20,"HT","halt_action")};break;
        case 'N':out.message=RetailPriceImprovement{r.text<8>(11,"stock"),r.enumeration(19,"BSAN","retail_interest")};break;
        default:break;
        }
        break;
    }
    case 'H':{
        if(profile==DecodeProfile::baseline_v1)return Result<DecodedRecord>::failure({Code::unsupported_type,location.payload_offset,"type",0,type});
        StockTradingAction h;h.stock=r.text<8>(11,"stock");h.trading_state=r.enumeration(19,"HPQT","trading_state");
        // The official layout specifies Alpha, but no fixed reserved value or
        // exhaustive historical reason enum. Preserve printable fields exactly.
        h.reserved=r.text<1>(20,"reserved").bytes[0];h.reason=r.text<4>(21,"reason");out.message=h;break;
    }
    case 'Y':{
        if(profile==DecodeProfile::baseline_v1)return Result<DecodedRecord>::failure({Code::unsupported_type,location.payload_offset,"type",0,type});
        out.message=RegShoRestriction{r.text<8>(11,"stock"),r.enumeration(19,"012","reg_sho_action")};break;
    }
    case 'S':out.message=SystemEvent{r.enumeration(11,"OSQMEC","event_code")};break;
    case 'R':{
        StockDirectory d;
        d.stock=r.text<8>(11,"stock");d.market_category=r.enumeration(19,"QGSNAPZV ","market_category");
        d.financial_status=r.enumeration(20,"DEQSGHJKCN ","financial_status");
        d.round_lot_size=static_cast<std::uint32_t>(r.number(21,4));d.round_lots_only=r.enumeration(25,"YN","round_lots_only");
        d.issue_classification=r.text<1>(26,"issue_classification").bytes[0];d.issue_subtype=r.text<2>(27,"issue_subtype");
        d.authenticity=r.enumeration(29,"PT","authenticity");d.short_sale_threshold=r.enumeration(30,"YN ","short_sale_threshold");
        d.ipo_flag=r.enumeration(31,"YN ","ipo_flag");d.luld_tier=r.enumeration(32,"12 ","luld_tier");
        d.etp_flag=r.enumeration(33,"YN ","etp_flag");d.etp_leverage=static_cast<std::uint32_t>(r.number(34,4));
        d.inverse=r.enumeration(38,"YN","inverse");out.message=d;break;
    }
    case 'A':out.message=r.add();break;
    case 'F':out.message=AddAttributedOrder{r.add(),r.text<4>(36,"attribution")};break;
    case 'E':out.message=r.executed();break;
    case 'C':out.message=OrderExecutedWithPrice{r.executed(),r.enumeration(31,"YN","printable"),r.price(32,"execution_price")};break;
    case 'X':out.message=OrderCancel{r.reference(11,"order_reference"),r.shares(19,"cancelled_shares")};break;
    case 'D':out.message=OrderDelete{r.reference(11,"order_reference")};break;
    case 'U':out.message=OrderReplace{r.reference(11,"original_reference"),r.reference(19,"new_reference"),r.shares(27,"shares"),r.price(31,"price")};break;
    case 'P':{
        auto& trade=out.message.emplace<Trade>();
        trade.order_reference=OrderReference{r.number(11,8)};
        trade.side=static_cast<Side>(r.enumeration(19,"BS","side"));
        trade.shares=r.shares(20,"shares");trade.stock=r.text<8>(24,"stock");
        trade.price=r.price(32,"price");trade.match_number=MatchNumber{r.number(36,8)};
        break;
    }
    case 'Q':{
        auto& cross=out.message.emplace<CrossTrade>();
        cross.shares=CrossShares{r.number(11,8)};cross.stock=r.text<8>(19,"stock");
        cross.cross_price=r.price(27,"cross_price");cross.match_number=MatchNumber{r.number(31,8)};
        cross.cross_type=r.enumeration(39,"OCH","cross_type");
        break;
    }
    case 'B':out.message=BrokenTrade{MatchNumber{r.number(11,8)}};break;
    default:return Result<DecodedRecord>::failure({Code::unsupported_type,location.payload_offset,"type",0,type});
    }
    if(r.error)return Result<DecodedRecord>::failure(r.error);
    return Result<DecodedRecord>::success(out);
}
} // namespace gig::itch
