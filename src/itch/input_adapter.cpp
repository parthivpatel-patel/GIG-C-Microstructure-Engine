#include "gig/itch/input_adapter.hpp"
#include "gig/itch/seed.hpp"
#include <chrono>
#include <type_traits>

namespace gig::itch {
namespace {
struct Guard{bool& busy;explicit Guard(bool& b):busy(b){busy=true;}~Guard(){busy=false;}};
bool date_valid(const std::optional<Text<10>>& date) noexcept {
    if(!date)return true;
    const auto& s=date->bytes;
    if(s[4]!='-'||s[7]!='-')return false;
    unsigned y=0,m=0,d=0;
    for(std::size_t i=0;i<10;++i){if(i==4||i==7)continue;if(s[i]<'0'||s[i]>'9')return false;
        const auto digit=static_cast<unsigned>(s[i]-'0');if(i<4)y=y*10+digit;else if(i<7)m=m*10+digit;else d=d*10+digit;}
    return y>=1&&std::chrono::year_month_day{std::chrono::year{static_cast<int>(y)},std::chrono::month{m},std::chrono::day{d}}.ok();
}
}
BinarySourceAdapter::BinarySourceAdapter(InputAdapterConfig c,BinaryFileFramer f,std::optional<SourceContext> context,std::optional<SyntheticReconstructor> native) noexcept
:config_(std::move(c)),framer_(std::move(f)),context_(std::move(context)),native_(std::move(native)){
    summary_.context_only=!native_;summary_.declared_initial=config_.initial;
}
BinarySourceAdapter::BinarySourceAdapter(BinarySourceAdapter&& other) noexcept
:config_(std::move(other.config_)),framer_(std::move(other.framer_)),context_(std::move(other.context_)),native_(std::move(other.native_)),hash_(other.hash_),summary_(other.summary_),finished_(other.finished_),moved_from_(other.moved_from_){other.moved_from_=true;}
gig::Result<BinarySourceAdapter> BinarySourceAdapter::create(InputAdapterConfig c,std::pmr::memory_resource* memory) noexcept {return create_impl(std::move(c),nullptr,{},memory);}
gig::Result<BinarySourceAdapter> BinarySourceAdapter::create_seeded(InputAdapterConfig c,const SeedState& seed,Sha256Digest trusted,std::pmr::memory_resource* memory) noexcept {return create_impl(std::move(c),&seed,trusted,memory);}
gig::Result<BinarySourceAdapter> BinarySourceAdapter::create_impl(InputAdapterConfig c,const SeedState* seed,Sha256Digest trusted,std::pmr::memory_resource* memory) noexcept {
    const auto bad=[](std::string_view field){return gig::Result<BinarySourceAdapter>::failure(gig::ErrorCode::inconsistent_metadata,field);};
    if(!memory||!c.source.provenance.sha256||!c.source.provenance.source||*c.source.provenance.source!=c.source.source
        ||(c.source.provenance.origin!=Origin::synthetic&&c.source.provenance.origin!=Origin::observed)
        ||static_cast<unsigned>(c.initial)>static_cast<unsigned>(InitialClaim::authored_synthetic_seed)
        ||!date_valid(c.dataset.session_date)||c.dataset.capture_start.value()>UINT64_MAX-2
        ||c.context_policy.first_location.payload_offset.value()!=c.dataset.capture_start.value()+2
        ||c.dataset.capture_start!=c.context_policy.first_location.frame_offset
        ||(c.dataset.capture_end&&c.dataset.capture_end->value()<c.dataset.capture_start.value())
        ||c.framing.buffer_bytes>65535||c.framing.max_stream_bytes==0||c.framing.max_stream_bytes>128U*1024U*1024U
        ||c.framing.max_records==0||c.framing.max_records>100000)return bad("adapter.manifest_or_limits");
    if(c.synthetic&&(c.initial!=(seed?InitialClaim::authored_synthetic_seed:InitialClaim::authored_synthetic)||c.source.provenance.origin!=Origin::synthetic
        ||c.dataset.known_gaps||c.synthetic->source!=c.source||c.synthetic->context_policy!=c.context_policy
        ||c.framing.max_records>c.synthetic->max_source_records))return bad("adapter.synthetic_evidence");
    if(!c.synthetic&&(seed||c.initial==InitialClaim::authored_synthetic||c.initial==InitialClaim::authored_synthetic_seed))return bad("adapter.synthetic_config_missing");
    auto framing=BinaryFileFramer::create(c.framing,c.dataset.capture_start,c.context_policy.first_location.ordinal,memory);
    if(!framing)return gig::Result<BinarySourceAdapter>::failure(framing.error.code==Code::resource_exhausted?gig::ErrorCode::resource_exhausted:gig::ErrorCode::inconsistent_metadata,"adapter.framer");
    std::optional<SourceContext> context;std::optional<SyntheticReconstructor> native;
    if(c.synthetic){auto created=seed?SyntheticReconstructor::create_seeded(*c.synthetic,*seed,trusted,memory):SyntheticReconstructor::create(*c.synthetic,memory);if(!created)return gig::Result<BinarySourceAdapter>::failure(created.error.code,created.error.field);native.emplace(std::move(*created.data));if(seed)c.synthetic=native->config();}
    else {auto created=SourceContext::create(c.source,c.context_policy,memory);if(!created)return gig::Result<BinarySourceAdapter>::failure(created.error.code==Code::resource_exhausted?gig::ErrorCode::resource_exhausted:gig::ErrorCode::inconsistent_metadata,"adapter.context");context.emplace(std::move(*created.data));}
    return gig::Result<BinarySourceAdapter>::success(BinarySourceAdapter(std::move(c),std::move(*framing.data),std::move(context),std::move(native)));
}
AdapterFeed BinarySourceAdapter::feed(std::span<const std::byte> bytes) noexcept {
    AdapterFeed out;
    if(moved_from_||finished_||busy_){out.error={moved_from_?AdapterCode::moved_from:busy_?AdapterCode::reentrant:AdapterCode::finished,"adapter.state"};return out;}
    if(summary_.error){out.error=summary_.error;return out;}
    Guard guard(busy_);const auto frame=framer_.feed(bytes);out.consumed=frame.consumed;
    if(!hash_.update(bytes.first(frame.consumed))){summary_.error={AdapterCode::digest,"adapter.hash_capacity"};out.error=summary_.error;return out;}
    summary_.bytes+=frame.consumed;summary_.input_sha256=hash_.finish();
    if(frame.error){summary_.error={AdapterCode::framing,"adapter.framing",frame.error};out.error=summary_.error;return out;}
    if(!frame.frame)return out;
    out.frame=true;out.location=frame.frame->location;out.type=std::to_integer<std::uint8_t>(frame.frame->payload.front());++summary_.records;
    if(native_){out.native=native_->process(frame.frame->payload,frame.frame->location,config_.source.provenance);out.committed=out.native.committed;
        if(!out.committed)summary_.error={AdapterCode::native,"adapter.native",{}, {},out.native};
        else summary_.native_records=native_->summary().native_committed;
    }else {auto result=context_->apply(frame.frame->payload,frame.frame->location,config_.source.provenance);out.committed=result.committed();
        if(!out.committed)summary_.error={AdapterCode::context,"adapter.context",{},result.error};
        else {static_assert(std::is_nothrow_move_constructible_v<NormalizedRecord>);static_assert(std::is_nothrow_move_assignable_v<NormalizedRecord>);out.normalized=std::move(result.record);}}
    if(out.committed)++summary_.accepted;else ++summary_.rejected;
    out.error=summary_.error;return out;
}
AdapterSummary BinarySourceAdapter::finish(EndKind end) noexcept {
    if(moved_from_||busy_){auto invalid=summary_;invalid.error={moved_from_?AdapterCode::moved_from:AdapterCode::reentrant,"adapter.state"};invalid.publication_eligible=invalid.full_l3_complete=false;return invalid;}
    if(finished_)return summary_;
    Guard guard(busy_);const auto framing=framer_.finish(end);summary_.input_sha256=hash_.finish();
    if(framing.error&&!summary_.error)summary_.error={AdapterCode::framing,"adapter.framing",framing.error};
    const bool end_matches=!config_.dataset.capture_end||framer_.position()==*config_.dataset.capture_end;
    if(end==EndKind::source_eof&&!summary_.error&&(!end_matches||summary_.input_sha256!=*config_.source.provenance.sha256))summary_.error={AdapterCode::digest,"adapter.capture_identity"};
    summary_.input_complete=framing.session_complete&&!summary_.error&&end==EndKind::source_eof;
    const auto kind=summary_.input_complete?ContextEnd::declared_source_complete:ContextEnd::bounded_prefix;
    if(native_){const auto native=native_->finish(kind);const auto& context=native_->context().summary();summary_.session_complete=!context.session_incomplete;
        summary_.full_l3_complete=summary_.input_complete&&native.input_complete&&!config_.dataset.known_gaps&&!context.session_incomplete&&!native.pending&&!native.rejected;
    }else {const auto context=context_->finish(kind);summary_.session_complete=!context.session_incomplete;}
    summary_.publication_eligible=summary_.full_l3_complete;finished_=true;return summary_;
}
} // namespace gig::itch
