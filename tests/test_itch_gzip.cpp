#include "gig/itch/gzip.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_gzip_fixture.hpp"
#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
using namespace gig::itch;
using namespace gig::itch::test;
namespace {
using Bytes=std::vector<std::byte>;
std::size_t checks{};
void require(bool value,const char* message){++checks;if(!value)throw std::runtime_error(message);}
struct Run {Bytes bytes;GzipFinish finish;};
Run collect(GzipReader& reader,std::span<const std::byte> compressed,std::size_t chunk,EndKind end=EndKind::source_eof){
    Run result;std::size_t offset=0;bool failed=false;
    while(offset<compressed.size()&&!failed){
        auto pending=compressed.subspan(offset,std::min(chunk,compressed.size()-offset));
        while(!pending.empty()){
            const auto next=reader.feed(pending);result.bytes.insert(result.bytes.end(),next.output.begin(),next.output.end());
            require(next.consumed<=pending.size(),"reader consumed bounded input");offset+=next.consumed;pending=pending.subspan(next.consumed);
            if(next.error){failed=true;break;}
            require(next.consumed!=0||!next.output.empty(),"nonempty input makes progress");
        }
    }
    if(!failed){for(;;){const auto next=reader.feed({});require(next.consumed==0,"empty feed never consumes");result.bytes.insert(result.bytes.end(),next.output.begin(),next.output.end());if(next.error||next.output.empty())break;}}
    result.finish=reader.finish(end);return result;
}
Run run(std::span<const std::byte> compressed,std::size_t chunk,GzipLimits limits={},EndKind end=EndKind::source_eof){auto created=GzipReader::create(limits);require(bool(created),"gzip create");return collect(*created.data,compressed,chunk,end);}
Bytes plain(){Bytes bytes(513);for(std::size_t i=0;i<bytes.size();++i)bytes[i]=static_cast<std::byte>(i&255U);return bytes;}
Bytes hex(std::string_view encoded){Bytes bytes;for(std::size_t i=0;i<encoded.size();i+=2)bytes.push_back(static_cast<std::byte>(std::stoul(std::string(encoded.substr(i,2)),nullptr,16)));return bytes;}
Bytes optional_header(const Bytes& base,std::size_t& header_size){Bytes out(base.begin(),base.begin()+10);out[3]=std::byte{0x1e};little(out,3,2);for(char c:std::string_view("ABCname\0comment\0",16))out.push_back(static_cast<std::byte>(c));little(out,fixture_crc32(out)&65535U,2);header_size=out.size();out.insert(out.end(),base.begin()+10,base.end());return out;}
void valid(){
    const auto original=plain();const auto compressed=stored_gzip(original);
    for(auto buffer:{std::size_t{1},std::size_t{2},std::size_t{7},std::size_t{65536}}){GzipLimits limits;limits.output_buffer_bytes=buffer;for(auto chunk:{std::size_t{1},std::size_t{2},std::size_t{3},std::size_t{17},compressed.size()}){const auto result=run(compressed,chunk,limits);require(result.bytes==original&&result.finish.complete&&result.finish.member_verified&&!result.finish.error,"all fragmentation schedules preserve data and verified member");require(result.finish.compressed_bytes==compressed.size()&&result.finish.decompressed_bytes==original.size(),"exact byte accounting");}}
    const auto empty=stored_gzip({});GzipLimits zero;zero.max_decompressed_bytes=0;const auto no_output=run(empty,empty.size(),zero);require(no_output.bytes.empty()&&no_output.finish.complete,"empty gzip with zero output budget");
    std::size_t header_size=0;const auto extended=optional_header(compressed,header_size);GzipLimits exact;exact.max_header_bytes=header_size;const auto header=run(extended,extended.size(),exact);require(header.finish.complete&&header.bytes==original,"optional FEXTRA/FNAME/FCOMMENT/FHCRC exact header bound");
    auto made=GzipReader::create();require(bool(made),"move fixture create");auto first=made.data->feed(std::span<const std::byte>(compressed).first(3));require(first.consumed==3&&!first.error,"partial move prefix");auto moved=std::move(*made.data);require(made.data->feed({}).error.code==GzipCode::moved_from,"moved-from rejected");const auto rest=collect(moved,std::span<const std::byte>(compressed).subspan(3),5);require(rest.bytes==original&&rest.finish.complete,"stable z_stream callbacks across move");require(moved.finish()==rest.finish,"finish idempotent");require(moved.feed({}).error.code==GzipCode::already_finished,"finished feed rejected");
}
void errors(){
    const auto original=plain();const auto compressed=stored_gzip(original);
    for(std::size_t byte:{std::size_t{0},std::size_t{2},std::size_t{3},compressed.size()-8,compressed.size()-4}){auto invalid=compressed;invalid[byte]^=byte==3?std::byte{0x80}:std::byte{1};std::optional<Run> baseline;for(auto chunk:{std::size_t{1},std::size_t{7},invalid.size()}){const auto result=run(invalid,chunk);require(!result.finish.complete&&result.finish.error.code==GzipCode::corrupt&&!result.finish.member_verified,"invalid magic/method/reserved flags/CRC/ISIZE rejected");if(baseline)require(result.bytes==baseline->bytes&&result.finish.error==baseline->finish.error,"corrupt prefix/error independent of caller fragments");else baseline=result;}}
    for(std::size_t cut=0;cut<compressed.size();++cut){const auto result=run(std::span<const std::byte>(compressed).first(cut),3);require(!result.finish.complete&&result.finish.error.code==GzipCode::truncated,"every true EOF cut is truncated");const auto prefix=run(std::span<const std::byte>(compressed).first(cut),5,{},EndKind::bounded_prefix);require(!prefix.finish.complete&&prefix.finish.bounded_prefix&&!prefix.finish.error,"intentional prefix cut remains incomplete, not corruption");require(prefix.bytes==result.bytes,"cut accepted bytes unaffected by finish policy");}
    for(bool concatenated:{false,true}){auto trailing=compressed;if(concatenated)trailing.insert(trailing.end(),compressed.begin(),compressed.end());else trailing.push_back(std::byte{0});for(auto chunk:{std::size_t{1},trailing.size()}){const auto result=run(trailing,chunk);require(result.bytes==original&&!result.finish.complete&&result.finish.member_verified&&result.finish.error.code==GzipCode::trailing_data,"single-member policy rejects suffix and concatenation");}}
    std::size_t header_size=0;auto extended=optional_header(compressed,header_size);extended[header_size-1]^=std::byte{1};require(run(extended,2).finish.error.code==GzipCode::corrupt,"header CRC validated");
}
void limits(){
    const auto original=plain();const auto compressed=stored_gzip(original);
    GzipLimits limits;limits.max_compressed_bytes=compressed.size();limits.max_header_bytes=10;limits.max_decompressed_bytes=original.size();require(run(compressed,compressed.size(),limits).finish.complete,"exact compressed/output caps permit trailer verification");
    {GzipLimits independent;independent.max_compressed_bytes=9;for(auto chunk:{std::size_t{1},compressed.size()}){const auto result=run(compressed,chunk,independent);require(result.finish.error.code==GzipCode::compressed_limit&&result.finish.compressed_bytes==9&&result.bytes.empty(),"compressed/header limits remain independent with compressed stop precedence");}}
    --limits.max_compressed_bytes;for(auto chunk:{std::size_t{1},std::size_t{11},compressed.size()}){const auto result=run(compressed,chunk,limits);require(result.finish.error.code==GzipCode::compressed_limit&&result.finish.compressed_bytes==limits.max_compressed_bytes&&result.bytes==original,"compressed cap stops at exact byte independent of fragments");}
    limits={};limits.max_decompressed_bytes=original.size()-1;for(auto chunk:{std::size_t{1},std::size_t{13},compressed.size()}){const auto result=run(compressed,chunk,limits);require(result.finish.error.code==GzipCode::decompressed_limit&&result.bytes.size()==original.size()-1&&result.finish.decompressed_bytes==original.size()-1,"output cap publishes exact allowed prefix only");require(std::equal(result.bytes.begin(),result.bytes.end(),original.begin()),"output cap exact byte truth");}
    std::size_t header_size=0;const auto extended=optional_header(compressed,header_size);limits={};limits.max_header_bytes=header_size-1;for(auto chunk:{std::size_t{1},extended.size()}){const auto result=run(extended,chunk,limits);require(result.finish.error.code==GzipCode::header_limit&&result.finish.compressed_bytes==limits.max_header_bytes&&result.bytes.empty(),"optional-header bound is header-only and exact");}
    // Independently generated Python gzip.compress(b'A'*4096,mtime=0) fixture.
    const auto bomb=hex("1f8b0800000000000203edc1010d000000c2a06cef5fca1e0e28000000e0dd004034a6fe00100000");limits={};limits.max_expansion_ratio=1;limits.expansion_slack_bytes=16;std::optional<Run> baseline;for(auto chunk:{std::size_t{1},std::size_t{4},bomb.size()}){const auto result=run(bomb,chunk,limits);require(result.finish.error.code==GzipCode::expansion_limit,"expansion ratio enforced before excess publication");require(result.bytes.size()<=result.finish.compressed_bytes+16,"ratio arithmetic bound");if(baseline)require(result.bytes==baseline->bytes&&result.finish.error==baseline->finish.error,"ratio failure chunk invariant");else baseline=result;}
    limits.max_expansion_ratio=UINT64_MAX;const auto no_overflow=run(bomb,3,limits);require(no_overflow.finish.complete&&no_overflow.bytes==Bytes(4096,std::byte{'A'}),"ratio maximum avoids multiplication overflow");
    for(int invalid=0;invalid<5;++invalid){limits={};if(invalid==0)limits.output_buffer_bytes=0;if(invalid==1)limits.output_buffer_bytes=65537;if(invalid==2)limits.max_expansion_ratio=0;if(invalid==3)limits.max_header_bytes=0;if(invalid==4)limits.max_decompressed_bytes=UINT64_MAX;require(!GzipReader::create(limits),"invalid limits rejected");}
}
void allocation(){
    const auto source=plain();const auto compressed=stored_gzip(source);gig::TrackedResource baseline;
    {auto reader=GzipReader::create({},&baseline);require(bool(reader),"allocation baseline create");const auto result=collect(*reader.data,compressed,7);require(result.finish.complete,"allocation baseline decode");}
    const auto sites=baseline.stats().attempts;require(sites>0&&baseline.stats().live_bytes==0,"baseline tracked allocations released");
    for(std::size_t fail=0;fail<sites;++fail){gig::TrackedResource resource;resource.fail_after(fail);{auto reader=GzipReader::create({},&resource);if(reader){const auto result=collect(*reader.data,compressed,compressed.size());require(result.finish.error.code==GzipCode::allocation_failure,"zlib callback allocation failure becomes structured error");}else require(reader.error.code==gig::ErrorCode::resource_exhausted,"factory allocation failure structured");}require(resource.stats().live_bytes==0&&resource.stats().live_blocks==0,"every allocator failure releases all bytes");}
    gig::TrackedResource tiny(std::pmr::get_default_resource(),64);require(!GzipReader::create({},&tiny)&&tiny.stats().live_bytes==0,"hard PMR budget honored");std::cout<<"gzip_reached_allocation_sites="<<sites<<'\n';
}
}
int main(int argc,char** argv){try{const std::string name=argc>1?argv[1]:"all";if(name=="all"||name=="valid")valid();if(name=="all"||name=="errors")errors();if(name=="all"||name=="limits")limits();if(name=="all"||name=="allocation")allocation();std::cout<<"gzip "<<name<<" checks="<<checks<<" passed\n";return 0;}catch(const std::exception& error){std::cerr<<"gzip failure: "<<error.what()<<'\n';return 1;}}
