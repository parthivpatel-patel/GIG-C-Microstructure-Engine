#include "gig/itch/restart.hpp"
#include "gig/memory/tracked_resource.hpp"
#include "support/itch_reconstruction_fixture.hpp"
#include <array>
#include <iostream>
#include <string>

using namespace gig::itch;
namespace {
using namespace gig::itch::test;
std::string hex(Sha256Digest value){const auto chars=hex_digest(value);return {chars.begin(),chars.end()};}
Sha256Digest text_hash(std::string_view value){return sha256(std::as_bytes(std::span{value.data(),value.size()}));}
gig::Digest code_hash(){return *gig::Digest::make(hex(text_hash("literal-checkpoint-test-implementation-v1"))).data;}
void hash_tests(){
    check(hex(sha256({}))=="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","SHA empty official vector");
    check(hex(text_hash("abc"))=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","SHA abc official vector");
    check(hex(text_hash("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"))=="248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1","SHA multi-block official vector");
    Sha256 million;const auto kilo=std::string(1000,'a');const auto bytes=std::as_bytes(std::span{kilo.data(),kilo.size()});
    for(std::size_t i=0;i<1000;++i)check(million.update(bytes),"million update");
    check(hex(million.finish())=="cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0","SHA million-a official vector");
    // Padding-boundary references independently calculated with Python hashlib.
    const std::array<std::pair<std::size_t,std::string_view>,5> padding{{
        {55,"9f4390f8d30c2dd92ec9f095b65e2b9ae9b0a925a5258e241c9f1e910f734318"},
        {56,"b35439a4ac6f0948b6d6f9e3c6af0f5f590ce20f1bde7090ef7970686ec6738a"},
        {63,"7d3e74a05d7db15bce4ad9ec0658ea98e3f06eeecf16b4c6fff2da457ddc2f34"},
        {64,"ffe054fe7ae0cb6dc65c3af9b61d5209f439851db43d0ba5997337df154668eb"},
        {65,"635361c48bb9eab14198e76ea8ab7f1a41685d6ad62aa9146d301d4f17eb0ae0"}}};
    for(const auto& [n,expected]:padding){const auto input=std::string(n,'a');check(hex(text_hash(input))==expected,"SHA padding boundary");}
    Sha256 incremental;const std::array<std::byte,1> a{std::byte{'a'}},b{std::byte{'b'}},c{std::byte{'c'}};
    check(incremental.update(a)&&incremental.update(b),"SHA incremental update");const auto prefix=incremental.finish();
    check(prefix==incremental.finish(),"SHA non-destructive repeated finish");check(incremental.update(c),"SHA update after finish");
    check(incremental.finish()==text_hash("abc"),"SHA resumed update");
    gig::TrackedResource resource;resource.fail_after(0);Sha256 armed;check(armed.update(a),"fixed SHA update");check(armed.finish()==text_hash("a"),"fixed SHA finalize");check(resource.stats().attempts==0,"SHA makes no PMR allocations");
}
void frame(std::vector<std::byte>& out,const std::vector<std::byte>& record){
    check(record.size()<=65535,"fixture length");out.push_back(static_cast<std::byte>((record.size()>>8U)&255U));out.push_back(static_cast<std::byte>(record.size()&255U));out.insert(out.end(),record.begin(),record.end());
}
struct Input {
    std::vector<std::vector<std::byte>> records{system(),directory(),directory(2,"TWO     "),add(),add(201,7,200,2),reduce('X',101,3),replace(101,102,8)};
    std::vector<std::byte> complete;
    ReconstructionConfig configuration=config();
    Input(){for(const auto& record:records)frame(complete,record);const auto hash=sha256(complete);configuration.initialization.fixture_sha256=*gig::Digest::make(hex(hash)).data;configuration.source.provenance.sha256=hash;}
};
void run_prefix(Harness& h,const Input& input,std::vector<std::byte>& bytes,std::size_t count,Provenance provenance={}){
    for(std::size_t i=0;i<count;++i){check(h.process(input.records[i],provenance).committed,"checkpoint fixture accept");frame(bytes,input.records[i]);}
}
void checkpoint_tests(bool explicit_provenance){
    Input input;const auto provenance=explicit_provenance?input.configuration.source.provenance:Provenance{};
    Harness original(input.configuration);std::vector<std::byte> prefix;run_prefix(original,input,prefix,4,provenance);
    auto checkpoint=capture_checkpoint(original.reconstruction,prefix,code_hash());check(bool(checkpoint),"capture authenticated active prefix");
    check(checkpoint.data->prefix_sha256==sha256(prefix)&&checkpoint.data->prefix_bytes==prefix.size(),"exact prefix identity");
    check(checkpoint.data->record_provenance==provenance,"raw provenance preserved");
    auto restarted=restart_from_checkpoint(*checkpoint.data,input.configuration,prefix,code_hash());check(bool(restarted),"restart accepted prefix");
    check(state(*restarted.data)==state(original.reconstruction)&&restarted.data->summary()==original.reconstruction.summary(),"restart exact native and source state");
    std::uint64_t offset=prefix.size(),ordinal=4;
    for(std::size_t i=4;i<input.records.size();++i){
        const auto& record=input.records[i];check(original.process(record,provenance).committed,"original suffix");
        check(restarted.data->process(record,{ByteOffset{offset},ByteOffset{offset+2},RecordOrdinal{ordinal}},provenance).committed,"restarted suffix");
        offset+=record.size()+2;++ordinal;check(state(*restarted.data)==state(original.reconstruction),"no duplicate/missing suffix event");
    }
    check(restarted.data->summary()==original.reconstruction.summary(),"final counters equal");
    auto modified=prefix;modified.back()^=std::byte{1};check(!restart_from_checkpoint(*checkpoint.data,input.configuration,modified,code_hash()),"changed source rejected");
    auto changed=input.configuration;changed.run_id=identity("different-run");check(!restart_from_checkpoint(*checkpoint.data,changed,prefix,code_hash()),"changed config rejected");
    const auto different=*gig::Digest::make(std::string(64,'a')).data;check(!restart_from_checkpoint(*checkpoint.data,input.configuration,prefix,different),"changed implementation rejected");
    for(std::size_t field=0;field<5;++field){
        auto corrupted=*checkpoint.data;
        if(field==0)++corrupted.books[0]->ledger.added;
        if(field==1)++corrupted.context.lifetime_orders;
        if(field==2)++corrupted.summary.context_committed;
        if(field==3)++corrupted.books[0]->journal_records;
        if(field==4)corrupted.books[0]->canonical_sha256[0]^=std::byte{1};
        check(!restart_from_checkpoint(corrupted,input.configuration,prefix,code_hash()),"corrupted descriptor rejected");
    }
    auto partial=prefix;partial.pop_back();check(!capture_checkpoint(original.reconstruction,partial,code_hash()),"partial frame capture rejected");
    auto corrupt=prefix;corrupt[0]=std::byte{255};check(!capture_checkpoint(original.reconstruction,corrupt,code_hash()),"corrupt framing rejected");
    check(!capture_checkpoint(original.reconstruction,prefix,code_hash()),"unrelated prefix cannot capture later state");
}
void provenance_and_terminal(){
    Input input;Harness mixed(input.configuration);std::vector<std::byte> bytes;
    check(mixed.process(input.records[0]).committed,"mixed first");frame(bytes,input.records[0]);
    check(mixed.process(input.records[1],input.configuration.source.provenance).committed,"mixed second");frame(bytes,input.records[1]);
    const auto unsupported=capture_checkpoint(mixed.reconstruction,bytes,code_hash());check(!unsupported&&unsupported.error.code==gig::ErrorCode::unsupported,"nonuniform provenance explicitly unsupported");
    Harness original(input.configuration);std::vector<std::byte> prefix;run_prefix(original,input,prefix,4);
    prefix.push_back(std::byte{0});prefix.push_back(std::byte{0});
    auto terminal=capture_checkpoint(original.reconstruction,prefix,code_hash());check(bool(terminal)&&terminal.data->terminal_observed,"terminal boundary captured separately");
    check(!terminal.data->summary.input_complete,"terminal does not invent context/source completion");
    prefix.push_back(std::byte{0});check(!capture_checkpoint(original.reconstruction,prefix,code_hash()),"trailing terminal bytes rejected");
    check(original.process(reduce('E',999,1,9)).committed==false,"pending invalid fixture");
    check(!capture_checkpoint(original.reconstruction,bytes,code_hash()),"rejected prefix not restart eligible");
    Harness finished(input.configuration);finished.reconstruction.finish(ContextEnd::bounded_prefix);
    check(!capture_checkpoint(finished.reconstruction,{},code_hash()),"finished checkpoint rejected");
}
void allocation_tests(){
    Input input;Harness original(input.configuration);std::vector<std::byte> prefix;run_prefix(original,input,prefix,4);
    auto checkpoint=capture_checkpoint(original.reconstruction,prefix,code_hash());check(bool(checkpoint),"fault checkpoint");
    gig::TrackedResource baseline;{
        auto rebuilt=restart_from_checkpoint(*checkpoint.data,input.configuration,prefix,code_hash(),&baseline);check(bool(rebuilt),"fault baseline restart");
    }
    const auto allocations=baseline.stats().attempts;check(allocations>0&&baseline.stats().live_bytes==0,"restart allocations observable");
    const auto original_state=state(original.reconstruction);
    for(std::size_t fail=0;fail<allocations;++fail){
        gig::TrackedResource resource;resource.fail_after(fail);
        {const auto result=restart_from_checkpoint(*checkpoint.data,input.configuration,prefix,code_hash(),&resource);check(!result,"every restart allocation failure rejects isolated rebuild");}
        check(resource.stats().live_bytes==0,"failed rebuild releases storage");check(state(original.reconstruction)==original_state,"failed restart cannot change original");
    }
    gig::TrackedResource tiny(std::pmr::get_default_resource(),1);
    check(!restart_from_checkpoint(*checkpoint.data,input.configuration,prefix,code_hash(),&tiny),"restart hard PMR cap");
    check(tiny.stats().live_bytes==0,"budget rejection no leaks");
    std::cout<<"restart_allocation_failpoints="<<allocations<<'\n';
}
int sha_driver(){
    std::array<char,131073> line{};
    while(std::cin.getline(line.data(),static_cast<std::streamsize>(line.size()))){
        const auto input=std::string_view(line.data());if(input.size()%2!=0)return 2;
        std::vector<std::byte> bytes;bytes.reserve(input.size()/2);
        const auto nibble=[](char c)->int{return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;};
        for(std::size_t i=0;i<input.size();i+=2){const auto a=nibble(input[i]),b=nibble(input[i+1]);if(a<0||b<0)return 2;bytes.push_back(static_cast<std::byte>(a*16+b));}
        Sha256 incremental;std::size_t used=0;
        while(used<bytes.size()){const auto n=std::min<std::size_t>(bytes.size()-used,1+used%127);check(incremental.update(std::span<const std::byte>(bytes).subspan(used,n)),"driver update");used+=n;}
        check(incremental.finish()==sha256(bytes),"chunk reference");std::cout<<hex(incremental.finish())<<'\n';
    }
    return std::cin.eof()?0:2;
}
}
int main(int argc,char** argv){try{
    if(argc==2&&std::string_view(argv[1])=="sha256")return sha_driver();
    hash_tests();checkpoint_tests(false);checkpoint_tests(true);provenance_and_terminal();allocation_tests();
    std::cout<<"SHA256 known vectors/padding and authenticated prefix restart tests passed\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
