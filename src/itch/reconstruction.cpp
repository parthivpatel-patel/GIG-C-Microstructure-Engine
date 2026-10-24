#include "gig/itch/reconstruction.hpp"
#include <algorithm>
#include <charconv>
#include <numeric>
#include <type_traits>

namespace gig::itch {
namespace {
gig::Result<std::uint64_t> ratio(std::uint64_t a,std::uint64_t b,std::uint64_t c,std::uint64_t d) noexcept {
    if(c==0||d==0)return gig::Result<std::uint64_t>::failure(gig::ErrorCode::invalid_range,"units");
    const auto cancel=[](auto& x,auto& y){const auto g=std::gcd(x,y);x/=g;y/=g;};
    cancel(a,c);cancel(a,d);cancel(b,c);cancel(b,d);
    if(c!=1||d!=1)return gig::Result<std::uint64_t>::failure(gig::ErrorCode::off_unit,"units");
    if(b!=0&&a>UINT64_MAX/b)return gig::Result<std::uint64_t>::failure(gig::ErrorCode::overflow,"units");
    return gig::Result<std::uint64_t>::success(a*b);
}
std::optional<std::array<std::byte,32>> digest_bytes(gig::Digest digest) noexcept {
    const auto s=digest.view();if(s.size()!=64)return std::nullopt;
    std::array<std::byte,32> out{};
    const auto nibble=[](char c)->int {return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;};
    for(std::size_t i=0;i<32;++i){const int a=nibble(s[i*2]),b=nibble(s[i*2+1]);if(a<0||b<0)return std::nullopt;out[i]=static_cast<std::byte>(a*16+b);}
    return out;
}
gig::StreamScope scope(const ReconstructionConfig& c,const BookBinding& b) noexcept {
    return {b.derived_stream,*gig::Identity::make(c.source.session.view()).data,0,gig::SequenceUnit::event};
}
gig::Metadata metadata(const ReconstructionConfig& c,const BookBinding& b,std::uint64_t sequence,std::uint64_t ordinal) noexcept {
    gig::Metadata m;
    m.instrument=gig::Available<gig::InstrumentId>::known(b.rules.instrument);
    m.venue=gig::Available<gig::VenueId>::known(b.rules.venue);
    m.scope=gig::Available<gig::StreamScope>::known(scope(c,b));
    m.sequence=gig::Available<gig::SequenceNumber>::known(*gig::SequenceNumber::make(sequence).data);
    m.capture_ordinal=gig::Available<std::uint64_t>::known(ordinal);
    m.event_time=gig::Available<gig::Timestamp<gig::EventTimestamp>>::missing(gig::MissingReason::unavailable);
    m.receive_time=gig::Available<gig::Timestamp<gig::ReceiveTimestamp>>::missing(gig::MissingReason::unavailable);
    const auto& e=c.initialization;
    m.provenance.dataset=gig::Available<gig::DatasetIdentity>::known({e.fixture,gig::Available<gig::Identity>::known(e.version),gig::Available<gig::Identity>::known(e.policy_reference),gig::Available<gig::Digest>::known(e.fixture_sha256)});
    m.provenance.origin=gig::Available<gig::Origin>::known(gig::Origin::synthetic);
    m.provenance.source=gig::Available<gig::Source>::known(gig::Source::generator);
    m.provenance.generator_seed=gig::Available<std::uint64_t>::known(e.seed);
    const auto v=*gig::Identity::make("1").data;
    const auto generator=*gig::Identity::make(e.generator.view()).data;
    (void)m.provenance.lineage.append({gig::TransformationKind::generated,generator,e.version});
    (void)m.provenance.lineage.append({gig::TransformationKind::reconstructed,*gig::Identity::make("itch-synthetic-l3").data,v});
    (void)m.provenance.parents.append({e.fixture,gig::Available<gig::Digest>::known(e.fixture_sha256)});
    return m;
}
}
gig::Result<gig::PriceTicks> price4_to_ticks(Price4 price,gig::types::UnitScale scale) noexcept {
    if(!scale.valid())return gig::Result<gig::PriceTicks>::failure(gig::ErrorCode::invalid_range,"tick_scale");
    const auto r=ratio(price.value(),scale.denominator,10000,scale.numerator);
    if(!r)return gig::Result<gig::PriceTicks>::failure(r.error.code,r.error.field);
    return gig::PriceTicks::make(*r.data);
}
gig::Result<gig::QuantityLots> shares_to_lots(std::uint64_t shares,gig::types::UnitScale scale) noexcept {
    if(!scale.valid())return gig::Result<gig::QuantityLots>::failure(gig::ErrorCode::invalid_range,"lot_scale");
    const auto r=ratio(shares,scale.denominator,scale.numerator,1);
    if(!r)return gig::Result<gig::QuantityLots>::failure(r.error.code,r.error.field);
    return gig::QuantityLots::make(*r.data);
}
SyntheticReconstructor::SyntheticReconstructor(ReconstructionConfig c,SourceContext context,std::pmr::memory_resource* resource) noexcept
:config_(std::move(c)),context_(std::move(context)),receipts_(resource) {}
SyntheticReconstructor::SyntheticReconstructor(SyntheticReconstructor&& other) noexcept
:config_(std::move(other.config_)),context_(std::move(other.context_)),engines_(std::move(other.engines_)),receipts_(std::move(other.receipts_)),summary_(other.summary_),pending_(other.pending_),pending_size_(other.pending_size_),pending_location_(other.pending_location_),pending_provenance_(other.pending_provenance_),moved_from_(other.moved_from_),held_(other.held_) {other.moved_from_=true;}
gig::Result<SyntheticReconstructor> SyntheticReconstructor::create(ReconstructionConfig c,std::pmr::memory_resource* resource) noexcept {
    const auto bad=[](std::string_view field){return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::inconsistent_metadata,field);};
    const auto& e=c.initialization;
    if(!resource||c.book_count==0||c.book_count>2||c.max_source_records==0||c.max_source_records>100000)return bad("reconstruction.limits");
    if(c.max_source_records>c.receipt_budget_bytes/sizeof(SourceReceipt))return bad("receipt_budget");
    if(e.kind!=InitialStateKind::authored_empty||!e.complete_history||e.boundary!=c.context_policy.first_location
        ||e.boundary!=Location{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}}
        ||e.source!=c.source.source||e.session!=c.source.session
        ||c.source.initialization!=Initialization::synthetic_history_declared)return bad("initialization.evidence");
    const auto digest=digest_bytes(e.fixture_sha256);
    if(!digest||c.source.provenance.origin!=Origin::synthetic||c.source.provenance.source!=c.source.source
        ||c.source.provenance.sha256!=digest||c.source.provenance.generator_seed!=e.seed)return bad("initialization.provenance");
    for(std::size_t i=0;i<2;++i){
        if(c.bindings[i].has_value()!=(i<c.book_count))return bad("bindings.layout");
        if(i>=c.book_count)continue;
        const auto& b=*c.bindings[i];
        if(b.locate.value()==0||std::all_of(b.stock.bytes.begin(),b.stock.bytes.end(),[](char x){return x==' ';})
            ||std::any_of(b.stock.bytes.begin(),b.stock.bytes.end(),[](char x){const auto c=static_cast<unsigned char>(x);return c<32||c>126;}))return bad("binding.identity");
        if(const auto error=gig::validate(b.rules))return gig::Result<SyntheticReconstructor>::failure(error.code,error.field);
        for(std::size_t j=0;j<i;++j){const auto& p=*c.bindings[j];if(p.stock==b.stock||p.locate==b.locate||p.rules.instrument==b.rules.instrument||p.derived_stream==b.derived_stream)return bad("bindings.duplicate");}
        const auto ticks=price4_to_ticks(Price4{c.context_policy.price_quantum},b.rules.tick_size);
        const auto lots=shares_to_lots(c.context_policy.lot_size,b.rules.lot_size);
        if(!ticks||ticks.data->value()!=1||!lots||lots.data->value()!=1)return bad("context_unit_consistency");
        auto m=metadata(c,b,0,0);m.source_record=gig::Available<gig::Identity>::known(e.fixture);
        if(const auto error=gig::validate(m))return gig::Result<SyntheticReconstructor>::failure(error.code,error.field);
    }
    auto context=SourceContext::create(c.source,c.context_policy,resource);
    if(!context)return gig::Result<SyntheticReconstructor>::failure(context.error.code==Code::resource_exhausted?gig::ErrorCode::resource_exhausted:gig::ErrorCode::inconsistent_metadata,context.error.field);
    try {
        SyntheticReconstructor out(c,std::move(*context.data),resource);
        out.receipts_.reserve(c.max_source_records);
        if(out.receipts_.capacity()>c.receipt_budget_bytes/sizeof(SourceReceipt))return bad("receipt_actual_budget");
        for(std::size_t i=0;i<c.book_count;++i){
            const auto& b=*c.bindings[i];gig::RestartPlan starts;
            (void)starts.append({b.rules.venue,scope(c,b),e.fixture,e.version,*gig::SequenceNumber::make(0).data,0});
            gig::ReplayConfig replay{c.run_id,{*gig::Identity::make(c.source.session.view()).data,0},starts};
            replay.max_journal_records=b.max_journal_records;replay.initial_state=gig::InitialBookState::declared_empty;
            auto engine=gig::ReplayEngine::create(b.rules,replay,b.limits,resource);
            if(!engine)return gig::Result<SyntheticReconstructor>::failure(engine.error.code,engine.error.field);
            out.engines_[i].emplace(std::move(*engine.data));
        }
        return gig::Result<SyntheticReconstructor>::success(std::move(out));
    }catch(...){return gig::Result<SyntheticReconstructor>::failure(gig::ErrorCode::resource_exhausted,"reconstruction.storage");}
}
gig::Result<gig::MarketEvent> SyntheticReconstructor::project(const NormalizedRecord& n,std::size_t index) const noexcept {
    const auto& b=*config_.bindings[index];const auto& raw=n.source;
    auto m=metadata(config_,b,summary_.native_counts[index],raw.location.ordinal.value());
    std::array<char,160> token{};const auto id=config_.initialization.fixture.view();std::copy(id.begin(),id.end(),token.begin());token[id.size()]=':';
    const auto converted=std::to_chars(token.data()+id.size()+1,token.data()+token.size(),raw.location.ordinal.value());
    if(converted.ec!=std::errc{})return gig::Result<gig::MarketEvent>::failure(gig::ErrorCode::capacity,"source_record");
    const auto source=gig::Identity::make({token.data(),static_cast<std::size_t>(converted.ptr-token.data())});
    if(!source)return gig::Result<gig::MarketEvent>::failure(source.error.code,"source_record");
    m.source_record=gig::Available<gig::Identity>::known(*source.data);
    const auto& state=(raw.type=='A'||raw.type=='F'||raw.type=='U')?*n.after:*n.before;
    const auto price=price4_to_ticks(state.resting_price,b.rules.tick_size);
    std::uint64_t shares=state.remaining.value();
    if(raw.type=='E')shares=std::get<OrderExecuted>(raw.message).executed_shares.value();
    if(raw.type=='C')shares=std::get<OrderExecutedWithPrice>(raw.message).execution.executed_shares.value();
    if(raw.type=='X')shares=std::get<OrderCancel>(raw.message).cancelled_shares.value();
    const auto quantity=shares_to_lots(shares,b.rules.lot_size);
    if(!price||!quantity)return gig::Result<gig::MarketEvent>::failure(!price?price.error.code:quantity.error.code,"conversion");
    const auto id_value=gig::OrderId::make(state.reference.value());
    if(!id_value)return gig::Result<gig::MarketEvent>::failure(id_value.error.code,"order_id");
    const auto side=state.side==Side::buy?gig::Side::buy:gig::Side::sell;
    gig::EventPayload payload=gig::AddOrder{*id_value.data,side,*price.data,*quantity.data};
    switch(raw.type){
    case 'A':case 'F':break;
    case 'E':case 'C':payload=gig::Trade{gig::BookExecution{*id_value.data,side,*price.data,*quantity.data}};break;
    case 'X':payload=gig::CancelOrder{*id_value.data,*quantity.data};break;
    case 'D':payload=gig::CancelOrder{*id_value.data,gig::CancelAll{}};break;
    case 'U':payload=gig::ReplaceOrder{*gig::OrderId::make(n.before->reference.value()).data,*id_value.data,side,*price.data,*quantity.data,gig::ReplacePriority::lose};break;
    default:return gig::Result<gig::MarketEvent>::failure(gig::ErrorCode::unsupported,"projection");
    }
    gig::MarketEvent event{m,payload};
    if(const auto error=gig::validate(event,b.rules))return gig::Result<gig::MarketEvent>::failure(error.code,error.field);
    return gig::Result<gig::MarketEvent>::success(event);
}
ReconstructionStep SyntheticReconstructor::process(std::span<const std::byte> payload,Location location,Provenance provenance) noexcept {
    ReconstructionStep step;
    if(busy_){step.native_error={gig::ErrorCode::inconsistent_state,"reentrant.process"};return step;}
    struct Guard {bool& flag; explicit Guard(bool& f) noexcept:flag(f){flag=true;} ~Guard(){flag=false;}} guard(busy_);
    if(moved_from_||summary_.finished){step.disposition=SourceDisposition::finished;step.native_error={gig::ErrorCode::inconsistent_state,"finished_or_moved"};return step;}
    if(held_){
        if(payload.size()!=pending_size_||location!=pending_location_||provenance!=pending_provenance_||!std::equal(payload.begin(),payload.end(),pending_.begin())){
            step.disposition=SourceDisposition::pending_identity_mismatch;step.native_error={gig::ErrorCode::identity_mismatch,"pending.source"};return step;
        }
    }else {
        if(summary_.considered>=config_.max_source_records||payload.size()>pending_.size()){
            step.disposition=SourceDisposition::resource_rejected;step.native_error={gig::ErrorCode::capacity,"source.limit"};summary_.eligibility=ReconstructionEligibility::stopped_at_valid_prefix;summary_.unconsidered_record=true;summary_.physical_position=location;return step;
        }
        ++summary_.considered;summary_.pending=true;held_=true;summary_.physical_position=location;
        std::copy(payload.begin(),payload.end(),pending_.begin());pending_size_=payload.size();pending_location_=location;pending_provenance_=provenance;
    }
    const auto reject=[&](ReconstructionStep s){summary_.pending=s.disposition==SourceDisposition::resource_rejected;summary_.rejected=summary_.pending?0:1;summary_.eligibility=ReconstructionEligibility::stopped_at_valid_prefix;return s;};
    auto prepared=context_.prepare(payload,location,provenance);
    if(!prepared){
        step.context_error=prepared.error;
        step.disposition=prepared.status==ContextStatus::source_invalid||prepared.status==ContextStatus::unsupported?SourceDisposition::source_rejected:
            prepared.status==ContextStatus::resource_limit?SourceDisposition::resource_rejected:SourceDisposition::context_rejected;
        return reject(step);
    }
    auto& token=*prepared.prepared;const auto& n=token.record();
    const bool mutation=n.kind==SemanticKind::add||n.kind==SemanticKind::execution||n.kind==SemanticKind::cancel||n.kind==SemanticKind::erase||n.kind==SemanticKind::replace;
    std::optional<std::size_t> index;
    if(n.source.type!='S'&&n.source.type!='V'&&n.source.type!='W'){
        for(std::size_t i=0;i<config_.book_count;++i)if(n.source.type=='K'?config_.bindings[i]->stock==std::get<IpoQuotingUpdate>(n.source.message).stock:config_.bindings[i]->locate==n.source.header.stock_locate){index=i;break;}
        if(!index){step.native_error={gig::ErrorCode::identity_mismatch,"unknown_binding"};return reject(step);}
        const auto& b=*config_.bindings[*index];
        const Text<8>* stock=nullptr;
        if(n.after)stock=&n.after->stock;
        if(n.kind==SemanticKind::directory)stock=&std::get<StockDirectory>(n.source.message).stock;
        if(n.kind==SemanticKind::trading_action)stock=&std::get<StockTradingAction>(n.source.message).stock;
        if(n.kind==SemanticKind::reg_sho_restriction)stock=&std::get<RegShoRestriction>(n.source.message).stock;
        if(n.source.type=='K')stock=&std::get<IpoQuotingUpdate>(n.source.message).stock;
        if(n.source.type=='J')stock=&std::get<LuldAuctionCollar>(n.source.message).stock;
        if(n.source.type=='I')stock=&std::get<NetOrderImbalance>(n.source.message).stock;
        if(n.source.type=='O')stock=&std::get<DirectListingDiscovery>(n.source.message).stock;
        if(n.source.type=='L')stock=&std::get<MarketParticipantPosition>(n.source.message).stock;
        if(n.source.type=='h')stock=&std::get<OperationalHalt>(n.source.message).stock;
        if(n.source.type=='N')stock=&std::get<RetailPriceImprovement>(n.source.message).stock;
        if(n.source.type=='P')stock=&std::get<Trade>(n.source.message).stock;
        if(n.source.type=='Q')stock=&std::get<CrossTrade>(n.source.message).stock;
        if(stock&&*stock!=b.stock){step.native_error={gig::ErrorCode::identity_mismatch,"binding.stock"};return reject(step);}
    }
    if(n.source.type=='C'&&!config_.allow_c_book_only){step.native_error={gig::ErrorCode::unsupported,"C.book_only_disabled"};return reject(step);}
    if(auto error=context_.validate_prepared(token);error.code!=ContextCode::none){step.context_error=error;step.disposition=SourceDisposition::context_rejected;return reject(step);}
    if(receipts_.size()==receipts_.capacity()){step.disposition=SourceDisposition::resource_rejected;step.native_error={gig::ErrorCode::capacity,"receipts"};return reject(step);}
    SourceReceipt receipt{n.source,SourceDisposition::external_observation,index,std::nullopt};
    if(mutation){
        if(summary_.native_counts[*index]==UINT64_MAX){step.native_error={gig::ErrorCode::overflow,"derived_sequence"};return reject(step);}
        const auto event=project(n,*index);if(!event){step.native_error=event.error;return reject(step);}
        step.native_error=engines_[*index]->apply(*event.data);
        if(step.native_error){step.disposition=step.native_error.code==gig::ErrorCode::resource_exhausted||step.native_error.code==gig::ErrorCode::capacity?SourceDisposition::resource_rejected:SourceDisposition::integration_rejected;return reject(step);}
        receipt.disposition=SourceDisposition::native_committed;receipt.native_sequence=summary_.native_counts[*index];
    }
    // Private context ownership and the guard above make this commit nonfallible.
    // All vector slots were reserved at creation; no callouts or allocation follow native success.
    static_assert(std::is_nothrow_copy_constructible_v<SourceReceipt>);
    (void)context_.commit_validated(std::move(token));
    receipts_.push_back(receipt);
    ++summary_.context_committed;
    if(mutation){++summary_.native_committed;++summary_.native_counts[*index];}else ++summary_.external_observations;
    summary_.committed_position=location;summary_.pending=false;held_=false;summary_.rejected=0;summary_.eligibility=ReconstructionEligibility::eligible_synthetic_empty;
    step.disposition=receipt.disposition;step.book_index=receipt.book_index;step.native_sequence=receipt.native_sequence;step.committed=true;return step;
}
ReconstructionSummary SyntheticReconstructor::finish(ContextEnd end) noexcept {
    if(busy_||moved_from_||summary_.finished)return summary_;
    if(end!=ContextEnd::bounded_prefix&&end!=ContextEnd::declared_source_complete&&end!=ContextEnd::unexpected_eof)return summary_;
    const auto context=context_.finish((held_||summary_.unconsidered_record)?ContextEnd::bounded_prefix:end);
    summary_.finished=true;summary_.input_complete=!held_&&!summary_.unconsidered_record&&context.source_complete;
    if(!summary_.input_complete)summary_.eligibility=ReconstructionEligibility::stopped_at_valid_prefix;
    return summary_;
}
} // namespace gig::itch
