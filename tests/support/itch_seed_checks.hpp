#pragma once
#include "gig/itch/seed.hpp"
#include "itch_input_adapter_checks.hpp"
#include <iostream>
#include "itch_reconstruction_fixture.hpp"
#include "gig/memory/tracked_resource.hpp"
namespace gig::itch::test {
struct SeedFixture {
    std::array<SeedDirectory,2> directories;
    std::vector<SeedOrder> orders;
    std::vector<OrderReference> retired{OrderReference{9}};
    std::vector<MatchState> matches{{MatchNumber{70},StockLocate{1},MatchKind::displayed_execution,false}};
    Location boundary{ByteOffset{4096},ByteOffset{4098},RecordOrdinal{100}};
    std::uint8_t stage{4};std::optional<TimestampNanoseconds> timestamp{TimestampNanoseconds{1}};
    SeedFixture(){
        const auto a=directory(),b=directory(2,"TWO     ");std::copy(a.begin(),a.end(),directories[0].payload.begin());std::copy(b.begin(),b.end(),directories[1].payload.begin());
        orders={{{OrderReference{11},StockLocate{1},stock("TEST    "),Side::buy,Shares{10},Price4{100},{},RecordOrdinal{10},true},4},
                {{OrderReference{12},StockLocate{1},stock("TEST    "),Side::buy,Shares{7},Price4{100},{},RecordOrdinal{12},true},8},
                {{OrderReference{21},StockLocate{2},stock("TWO     "),Side::sell,Shares{6},Price4{201},{},RecordOrdinal{11},true},2}};
    }
    SeedState view()const{return {boundary,stage,timestamp,directories,orders,retired,matches};}
    ReconstructionConfig configuration()const{auto c=config();c.initialization.kind=InitialStateKind::complete_seed;c.initialization.boundary=boundary;c.context_policy.first_location=boundary;return c;}
    Sha256Digest digest()const{const auto c=configuration();auto d=seed_sha256(view(),c.source.source,c.source.session);check(bool(d),"seed hash");return *d.data;}
    gig::Result<SyntheticReconstructor> create(std::pmr::memory_resource* memory=std::pmr::get_default_resource())const{return SyntheticReconstructor::create_seeded(configuration(),view(),digest(),memory);}
};
inline void seed_checks(){
    SeedFixture f;auto initial=f.create();if(!initial)throw std::runtime_error(std::string(initial.error.field));auto& r=*initial.data;
    check(r.engine(0)->book().order_count()==2&&r.engine(0)->book().remaining()==17&&r.engine(1)->book().remaining()==6,"seed independent totals");
    check(r.engine(0)->book().ledger().recovered==17&&r.engine(0)->journal_size()==1&&r.summary().native_committed==0,"seed recovery not source event");
    check(r.context().summary().accepted_records==0&&r.context().summary().lifetime_orders==4&&!r.context().summary().initialization_incomplete,"seed context and provenance");
    check(r.context().seed_retired_references().size()==1,"retired IDs without fabricated attributes");
    check(r.config().seed_sha256.has_value()&&r.engine(0)->book().last_metadata()->provenance.parents.count==2,"seed hash native provenance");
    auto reversed=f;std::reverse(reversed.orders.begin(),reversed.orders.end());std::reverse(reversed.directories.begin(),reversed.directories.end());
    check(reversed.digest()==f.digest(),"seed canonical permutation hash");auto same=reversed.create();check(bool(same)&&state(*same.data)==state(r),"seed deterministic permutation state");
    std::uint64_t offset=4096,ordinal=100;
    const auto apply=[&](const std::vector<std::byte>& p){const auto result=r.process(p,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},r.config().source.provenance);check(result.committed,"seed continuation accepted");offset+=p.size()+2;++ordinal;return result;};
    const auto first=apply(reduce('E',11,2,71));check(first.native_sequence==1,"first continuation after seed journal boundary");
    apply(replace(12,13,9,101));apply(reduce('X',11,1));apply(reduce('D',13));apply(add(14,5));
    const auto a=r.engine(0)->book().find(number<gig::OrderId>(11)),b=r.engine(0)->book().find(number<gig::OrderId>(14));
    check(a&&a->order.quantity.value()==7&&a->priority==4&&b&&b->order.quantity.value()==5&&b->priority==10,"seed partial/FIFO/replace semantics");
    check(r.engine(0)->book().remaining()==12&&r.engine(0)->journal_size()==6&&r.summary().native_committed==5,"seed source accounting");
    const auto before=state(r);apply(broken(70));check(state(r)==before,"seed broken trade observation no liquidity restoration");
    const auto refused=r.process(add(9),{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},r.config().source.provenance);
    check(!refused.committed&&refused.context_error.code==ContextCode::duplicate_reference&&state(r)==before,"seed retired identity collision atomic");
    for(unsigned variant=0;variant<16;++variant){auto bad=f;
        switch(variant){case 0:bad.orders[0].state.remaining=Shares{0};break;case 1:bad.orders[0].state.side=static_cast<Side>('?');break;
        case 2:bad.orders[0].state.resting_price=Price4{0};break;case 3:bad.orders[0].state.locate=StockLocate{99};break;
        case 4:bad.orders[1].state.reference=OrderReference{11};break;case 5:bad.orders[1].priority=4;break;
        case 6:bad.orders[0].priority=UINT64_MAX;break;case 7:bad.orders[0].state.arrival=RecordOrdinal{100};break;
        case 8:bad.retired.push_back(OrderReference{11});break;case 9:bad.matches.push_back(bad.matches[0]);break;
        case 10:bad.directories[0].payload[19]=std::byte{'?'};break;case 11:bad.stage=6;break;
        case 12:bad.boundary.payload_offset=ByteOffset{4097};break;case 13:bad.retired.push_back(OrderReference{9});break;
        case 14:bad.orders[0].priority=9;break;case 15:bad.orders[0].state.active=false;break;}
        check(!bad.create(),"invalid typed seed refused even with matching hash");
    }
    auto cfg=f.configuration();cfg.source.provenance.origin=Origin::observed;
    check(!SyntheticReconstructor::create_seeded(cfg,f.view(),f.digest()),"observed seed not synthetic relabelled");
    auto wrong=f.digest();wrong[0]^=std::byte{1};check(!SyntheticReconstructor::create_seeded(f.configuration(),f.view(),wrong),"seed integrity failure");
    cfg=f.configuration();cfg.context_policy.max_directories=1;check(!SyntheticReconstructor::create_seeded(cfg,f.view(),f.digest()),"seed directory capacity");
    cfg=f.configuration();cfg.context_policy.max_lifetime_orders=3;check(!SyntheticReconstructor::create_seeded(cfg,f.view(),f.digest()),"seed retired capacity included");
    cfg=f.configuration();cfg.context_policy.require_monotonic_timestamps=true;auto no_time=f;no_time.timestamp.reset();check(!SyntheticReconstructor::create_seeded(cfg,no_time.view(),no_time.digest()),"seed unknown clock boundary refused under monotonic policy");
    std::vector<std::byte> prefix;for(const auto& wire:{reduce('E',11,2,71),replace(12,13,9,101)}){prefix.push_back(static_cast<std::byte>(wire.size()>>8U));prefix.push_back(static_cast<std::byte>(wire.size()&255U));prefix.insert(prefix.end(),wire.begin(),wire.end());}
    auto restarted=restart_seeded_prefix(f.configuration(),f.view(),f.digest(),prefix,sha256(prefix));
    check(bool(restarted)&&restarted.data->engine(0)->book().remaining()==17,"seed authenticated prefix replay");
    auto repeated=restart_seeded_prefix(f.configuration(),f.view(),f.digest(),prefix,sha256(prefix));
    check(bool(repeated)&&*restarted.data->engine(0)->canonical().data==*repeated.data->engine(0)->canonical().data,"seed canonical journal replay identical");
    auto corrupt=prefix;corrupt[3]^=std::byte{1};check(!restart_seeded_prefix(f.configuration(),f.view(),f.digest(),corrupt,sha256(prefix)),"seed corrupt replay archive refused");
    auto truncated=prefix;truncated.pop_back();check(!restart_seeded_prefix(f.configuration(),f.view(),f.digest(),truncated,sha256(truncated)),"seed partial frame restart refused");
    auto crowded=f;crowded.orders.clear();
    for(std::uint64_t i=0;i<65;++i)crowded.orders.push_back({{OrderReference{1000+i},StockLocate{1},stock("TEST    "),Side::buy,Shares{1},Price4{100},{},RecordOrdinal{i},true},i+1});
    check(!crowded.create(),"seed64 per-book snapshot boundary enforced");
    cfg=f.configuration();cfg.bindings[0]->max_journal_records=1;
    auto full=SyntheticReconstructor::create_seeded(cfg,f.view(),f.digest());check(bool(full),"seed consumes journal limit explicitly");
    const auto full_before=state(*full.data);auto blocked=full.data->process(reduce('E',11,1,71),f.boundary,cfg.source.provenance);
    check(!blocked.committed&&full.data->context().summary().accepted_records==0&&state(*full.data)==full_before,"seed journal exhaustion preserves context/book");
    const auto tail=adapter_frames({reduce('E',11,2,71),system('E'),system('C')});
    auto adapter_cfg=adapter_config(tail);auto seed_cfg=f.configuration();seed_cfg.source.provenance.sha256=sha256(tail);
    const auto tail_hex=hex_digest(sha256(tail));seed_cfg.initialization.fixture_sha256=number<gig::Digest>(std::string_view(tail_hex.data(),tail_hex.size()));
    adapter_cfg.source=seed_cfg.source;adapter_cfg.context_policy=seed_cfg.context_policy;adapter_cfg.synthetic=seed_cfg;
    adapter_cfg.initial=InitialClaim::authored_synthetic_seed;adapter_cfg.dataset.capture_start=f.boundary.frame_offset;adapter_cfg.dataset.capture_end=ByteOffset{4096+tail.size()};
    check(!BinarySourceAdapter::create(adapter_cfg),"seed claim needs seed API");
    for(auto chunk:{std::size_t{1},std::size_t{7},std::size_t{4096}}){auto adapter=BinarySourceAdapter::create_seeded(adapter_cfg,f.view(),f.digest());check(bool(adapter),"seed adapter creates");
        const auto summary=adapter_run(*adapter.data,tail,chunk);check(summary.input_complete&&summary.full_l3_complete&&summary.publication_eligible&&summary.accepted==3&&summary.native_records==1,"bounded seeded adapter complete authored tail");
        check(adapter.data->reconstruction()->engine(0)->book().remaining()==15,"adapter seeded execution exact");}
    bool adapter_success=false;std::size_t adapter_failures=0;
    for(std::size_t i=0;i<128;++i){gig::TrackedResource memory;memory.fail_after(i);{auto attempt=BinarySourceAdapter::create_seeded(adapter_cfg,f.view(),f.digest(),&memory);adapter_success=bool(attempt);if(!attempt)++adapter_failures;}check(memory.stats().live_bytes==0,"seed adapter allocation cleanup");if(adapter_success)break;}
    check(adapter_success&&adapter_failures>0,"seed adapter allocation sweep");
    bool success=false;std::size_t failures=0;
    for(std::size_t fail=0;fail<256;++fail){gig::TrackedResource memory(std::pmr::get_default_resource(),16U*1024U*1024U);memory.fail_after(fail);{auto attempt=f.create(&memory);if(attempt){success=true;check(attempt.data->engine(0)->book().remaining()==17,"allocation success coherent");}else ++failures;}check(memory.stats().live_bytes==0&&memory.stats().live_blocks==0,"seed factory failure atomic cleanup");if(success)break;}
    check(success&&failures>0,"real seed allocation failures through full success");
    std::cout<<"seed_factory allocation_failure_positions="<<failures<<" cleanup_live_bytes=0\n";
}
} // namespace gig::itch::test
