#pragma once
#include "gig/itch/input_adapter.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "itch_reconstruction_fixture.hpp"
#include <string>

namespace gig::itch::test {
inline std::vector<std::byte> adapter_frames(const std::vector<std::vector<std::byte>>& records){
    std::vector<std::byte> bytes;
    for(const auto& p:records){check(p.size()<=65535,"adapter fixture frame size");bytes.push_back(static_cast<std::byte>(p.size()>>8U));bytes.push_back(static_cast<std::byte>(p.size()&255U));bytes.insert(bytes.end(),p.begin(),p.end());}
    bytes.push_back(std::byte{});bytes.push_back(std::byte{});return bytes;
}
inline InputAdapterConfig adapter_config(std::span<const std::byte> bytes,bool native=true){
    auto c=config();const auto digest=sha256(bytes);const auto hex=hex_digest(digest);
    c.source.provenance.sha256=digest;c.initialization.fixture_sha256=number<gig::Digest>(std::string_view(hex.data(),hex.size()));
    DatasetContract data{source_id("authored-provider"),source_id("authored-dataset-v1"),source_id("locally-authored"),source_id("synthetic-fixture-permitted"),source_id("no-observed-data"),source_id("literal-authored-empty"),{},ByteOffset{0},ByteOffset{bytes.size()},false};
    FramerLimits limits;limits.max_stream_bytes=8U*1024U*1024U;limits.max_records=c.max_source_records;
    return {data,c.source,c.context_policy,limits,native?InitialClaim::authored_synthetic:InitialClaim::unknown,native?std::optional<ReconstructionConfig>(c):std::nullopt};
}
inline AdapterSummary adapter_run(BinarySourceAdapter& adapter,std::span<const std::byte> bytes,std::size_t chunk){
    std::size_t offset=0;
    while(offset<bytes.size()){
        const auto count=std::min(chunk,bytes.size()-offset);const auto feed=adapter.feed(bytes.subspan(offset,count));offset+=feed.consumed;
        if(feed.error)break;
        check(feed.consumed>0,"adapter forward progress");
        if(feed.normalized)check(feed.normalized->source.provenance==adapter.config().source.provenance,"adapter exact source provenance");
    }
    return adapter.finish();
}
inline std::vector<std::byte> adapter_session(){
    std::vector<std::vector<std::byte>> records{system(),directory(),directory(2,"TWO     "),add(11),reduce('E',11,2,71),replace(11,12,8,101),reduce('X',12,1),reduce('D',12)};
    for(char code:std::string_view("SQMEC")){records.push_back(system(code));}
    return adapter_frames(records);
}
inline void input_adapter_checks(){
    const auto bytes=adapter_session();
    for(const auto chunk:{std::size_t{1},std::size_t{7},std::size_t{4096}}){
        auto result=BinarySourceAdapter::create(adapter_config(bytes));check(bool(result),"native input adapter create");
        const auto summary=adapter_run(*result.data,bytes,chunk);
        check(!summary.error&&summary.records==13&&summary.accepted==13&&summary.native_records==5&&summary.full_l3_complete&&summary.publication_eligible,"native full adapter accounting");
        check(result.data->reconstruction()->engine(0)->book().order_count()==0,"native adapter final book");
    }
    for(const auto claim:{InitialClaim::unknown,InitialClaim::session_start_evidence,InitialClaim::snapshot_evidence,InitialClaim::incomplete}){
        auto c=adapter_config(bytes,false);c.initial=claim;
        // Authored mock declaration exercises provenance preservation, not an observed dataset.
        c.source.provenance.origin=Origin::observed;c.source.provenance.generator_seed.reset();
        auto result=BinarySourceAdapter::create(c);check(bool(result),"context-only caller evidence accepted as unverified");
        const auto summary=adapter_run(*result.data,bytes,3);
        check(summary.input_complete&&summary.session_complete&&summary.context_only&&!summary.full_l3_complete&&!summary.publication_eligible&&!result.data->reconstruction(),"observed claims never certify native L3");
    }
    auto c=adapter_config(bytes);c.source.provenance.origin=Origin::observed;
    check(!BinarySourceAdapter::create(c),"observed to synthetic bridge forbidden");
    c=adapter_config(bytes);c.dataset.known_gaps=true;check(!BinarySourceAdapter::create(c),"gapped native initialization forbidden");
    c=adapter_config(bytes);c.initial=static_cast<InitialClaim>(255);check(!BinarySourceAdapter::create(c),"adapter invalid init enum");
    c=adapter_config(bytes);Text<10> bad;const std::string date="2026-02-30";std::copy(date.begin(),date.end(),bad.bytes.begin());c.dataset.session_date=bad;check(!BinarySourceAdapter::create(c),"invalid explicit calendar date");
    c=adapter_config(bytes,false);(*c.source.provenance.sha256)[0]^=std::byte{1};auto wrong=BinarySourceAdapter::create(c);check(bool(wrong),"digest is checked on stream completion");
    check(adapter_run(*wrong.data,bytes,5).error.code==AdapterCode::digest,"input SHA mismatch blocks completion");
    for(const auto cut:{std::size_t{1},std::size_t{3},bytes.size()-1}){
        const auto partial=std::span<const std::byte>(bytes).first(cut);auto result=BinarySourceAdapter::create(adapter_config(partial));
        check(bool(result),"truncated source adapter create");const auto summary=adapter_run(*result.data,partial,3);
        check(bool(summary.error)&&!summary.input_complete&&!summary.publication_eligible,"truncated source never complete");
    }
    for(const auto kind:{'E','A','?'}){
        auto raw=kind=='E'?adapter_frames({system(),directory(),reduce('E',999,1,1)}):kind=='A'?adapter_frames({system(),directory(),add(11),add(11)}):adapter_frames({system(),directory(),{std::byte{'?'}}});
        auto result=BinarySourceAdapter::create(adapter_config(raw));check(bool(result),"invalid fixture adapter creation");const auto summary=adapter_run(*result.data,raw,2);check(bool(summary.error)&&summary.rejected==1&&!summary.publication_eligible,"invalid source/lifecycle explicitly stops");
    }
    {auto result=BinarySourceAdapter::create(adapter_config(bytes));check(bool(result),"interrupted adapter");const auto step=result.data->feed(std::span<const std::byte>(bytes).first(1));check(!step.error,"fragment input");const auto summary=result.data->finish(EndKind::bounded_prefix);check(!summary.input_complete&&!summary.publication_eligible,"interruption not complete");}
    {auto c2=adapter_config(bytes);c2.framing.max_records=3;auto result=BinarySourceAdapter::create(c2);check(bool(result),"capped adapter");const auto summary=adapter_run(*result.data,bytes,4096);check(bool(summary.error)&&summary.accepted==3&&!summary.publication_eligible,"record budget preserves accepted prefix");}
    {auto result=BinarySourceAdapter::create(adapter_config(bytes));check(bool(result),"move adapter");auto moved=std::move(*result.data);check(result.data->feed(bytes).error.code==AdapterCode::moved_from&&!result.data->reconstruction(),"moved donor refused");check(adapter_run(moved,bytes,9).publication_eligible,"moved owner valid");check(moved.feed(bytes).error.code==AdapterCode::finished,"finished input rejected");}
    bool completed=false;
    for(std::size_t fail=0;fail<128&&!completed;++fail){
        gig::TrackedResource memory;memory.fail_after(fail);
        {auto result=BinarySourceAdapter::create(adapter_config(bytes),&memory);
            if(result){const auto summary=adapter_run(*result.data,bytes,7);completed=!summary.error;
                const auto* native=result.data->reconstruction();check(native&&native->summary().context_committed==summary.accepted&&native->summary().native_committed==summary.native_records,"adapter/native accepted-prefix atomicity");
                if(summary.error)check(!summary.publication_eligible,"allocation failure no complete publication");}
            else check(result.error.code==gig::ErrorCode::resource_exhausted,"adapter allocation failure classification");}
        check(memory.stats().live_bytes==0&&memory.stats().live_blocks==0,"adapter failure cleanup");
    }
    check(completed,"adapter allocation sweep reached success");
}
} // namespace gig::itch::test
