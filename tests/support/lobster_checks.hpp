#pragma once
#include "gig/lobster/reconstruction.hpp"
#include "gig/memory/tracked_resource.hpp"
namespace gig::lobster::test {
inline gig::Identity id(std::string_view s){return *gig::Identity::make(s).data;}
inline SourceBinding source(){const auto hash=*gig::Digest::make(std::string(64,'0')).data;return {id("authored-lobster"),id("authored-session"),id("authored-permission"),hash,hash,hash,gig::Origin::synthetic,0};}
inline std::string ref(std::uint64_t bid){return "110,10,100,"+std::to_string(bid)+",120,11,90,21,130,12,80,22,140,13,70,23,150,14,60,24";}
inline void reconstruction_checks(){
    const auto require=[](bool value){if(!value)throw std::runtime_error("authored lobster reconstruction invariant");};
    require(!KnownSubset::create(source(),{},32,std::pmr::get_default_resource(),true));
    auto created=KnownSubset::create(source(),{},32);require(bool(created));auto& state=*created.data;
    auto first=state.process("1,1,11,10,100,1",ref(30));require(first&&first.data->disposition==Disposition::native);require(state.book().remaining()==10);
    auto second=state.process("2,2,11,3,100,1",ref(27));require(second&&second.data->effect.quantity_match&&state.book().remaining()==7);
    const auto before=*state.book().canonical().data;
    auto hidden=state.process("2,5,0,2,100,1",ref(27));require(hidden&&hidden.data->disposition==Disposition::external&&*state.book().canonical().data==before);
    auto missing=state.process("3,4,99,1,90,1",ref(27));require(missing&&missing.data->disposition==Disposition::unknown_order&&state.book().remaining()==7);
    auto erase=state.process("4,3,11,7,100,1",ref(20));require(erase&&state.book().remaining()==0);
    auto reused=state.process("5,1,99,1,90,1",ref(20));require(reused&&reused.data->disposition==Disposition::inconsistent_history&&state.summary().prefix_blocked);
    require(state.summary().initial_state_unknown&&!state.summary().full_l3_complete&&!state.book().check_invariants());
    const auto original=ref(20);const auto parsed=parse_reference(original);require(bool(parsed));
    auto add=parse_message("1,1,12,5,100,1");auto after=parse_reference(ref(25));auto effect=reference_effect(*parsed.data,*add.data,*after.data);require(effect.quantity_eligible&&effect.quantity_match&&effect.depth_match);
    auto wrong=parse_reference(ref(26));require(!reference_effect(*parsed.data,*add.data,*wrong.data).quantity_match);
    std::size_t failed=0;bool success=false;
    for(std::size_t i=0;i<128;++i){gig::TrackedResource memory;memory.fail_after(i);{auto attempt=KnownSubset::create(source(),{},32,&memory);success=bool(attempt);failed+=success?0U:1U;}require(memory.stats().live_bytes==0);if(success)break;}require(success&&failed>0);
    bool mutation_success=false;
    for(std::size_t i=0;i<32;++i){gig::TrackedResource memory;{auto attempt=KnownSubset::create(source(),{},32,&memory);require(bool(attempt));const auto clean=*attempt.data->book().canonical().data;memory.fail_after(i);auto result=attempt.data->process("1,1,11,10,100,1",ref(30));memory.disable_failure();require(bool(result));
        if(result.data->disposition==Disposition::native){mutation_success=true;require(attempt.data->book().remaining()==10);}else require(*attempt.data->book().canonical().data==clean);
        require(!attempt.data->book().check_invariants());}require(memory.stats().live_bytes==0);if(mutation_success)break;}require(mutation_success);
    std::cout<<"lobster unknown-initialization/native subset/reference effect/allocation controls passed\n";
}
} // namespace gig::lobster::test
