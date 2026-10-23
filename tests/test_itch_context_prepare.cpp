#include "gig/itch/context.hpp"
#include "gig/memory/tracked_resource.hpp"
#include <array>
#include <iostream>
#include <new>
#include <stdexcept>
#include <type_traits>
using namespace gig::itch;
namespace {
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
SourceManifest manifest(){return {*SourceIdentity::make("synthetic-preparation").data,*SourceIdentity::make("session").data,{},Initialization::synthetic_history_declared};}
SourceContext context(std::pmr::memory_resource* resource=std::pmr::get_default_resource()){
    ContextPolicy policy;policy.max_directories=2;policy.max_lifetime_orders=4;policy.max_matches=4;
    auto created=SourceContext::create(manifest(),policy,resource);require(bool(created),"create");return std::move(*created.data);
}
std::array<std::byte,12> system(char code='O'){
    std::array<std::byte,12> bytes{};bytes[0]=std::byte{'S'};bytes[11]=static_cast<std::byte>(code);return bytes;
}
constexpr Location first{ByteOffset{0},ByteOffset{2},RecordOrdinal{0}};
constexpr Location second{ByteOffset{14},ByteOffset{16},RecordOrdinal{1}};
void guards(){
    auto original=context();auto other=context();
    const auto before=original.summary();auto prepared=original.prepare(system(),first);
    require(bool(prepared)&&prepared.prepared->record().source.type=='S',"owned preparation");
    require(original.summary()==before&&original.directories().empty()&&original.orders().empty()&&original.matches().empty(),"prepare is read-only");
    require(other.validate_prepared(*prepared.prepared).code==ContextCode::invalid_prepared,"wrong owner guard");
    require(!other.commit(std::move(*prepared.prepared)).committed(),"wrong owner cannot commit");
    require(original.validate_prepared(*prepared.prepared).code==ContextCode::none,"wrong-owner rejection preserves rightful token");
    PreparedContext moved{std::move(*prepared.prepared)};
    require(original.validate_prepared(*prepared.prepared).code==ContextCode::invalid_prepared,"moved donor invalid");
    require(original.commit(std::move(moved)).committed(),"moved token commits once");
    const auto after=original.summary();require(after.accepted_records==1,"single commit count");
    require(!original.commit(std::move(moved)).committed()&&original.summary()==after,"consumed token reuse rejected");
    auto stale=original.prepare(system('S'),second);require(bool(stale),"stale candidate");
    require(original.apply(system('S'),second).committed(),"competing accepted step");
    const auto advanced=original.summary();require(original.validate_prepared(*stale.prepared).code==ContextCode::stale_prepared,"generation stale guard");
    require(!original.commit(std::move(*stale.prepared)).committed()&&original.summary()==advanced,"stale rejection atomic");
}
void lifetime(){
    auto original=context();auto prepared=original.prepare(system(),first);require(bool(prepared),"move context preparation");
    auto relocated=std::move(original);
    require(original.validate_prepared(*prepared.prepared).code==ContextCode::invalid_prepared,"moved-from owner invalid");
    require(relocated.validate_prepared(*prepared.prepared).code==ContextCode::invalid_prepared,"context move invalidates outstanding token");
    require(relocated.apply(system(),first).committed(),"relocated context remains usable");
    auto ending=context();auto ending_token=ending.prepare(system(),first);ending.finish(ContextEnd::bounded_prefix);
    require(ending.validate_prepared(*ending_token.prepared).code==ContextCode::stale_prepared,"finish invalidates pending preparation");
    alignas(SourceContext) std::byte storage[sizeof(SourceContext)];
    auto* first_owner=new(storage)SourceContext(context());auto old_token=first_owner->prepare(system(),first);
    first_owner->~SourceContext();
    auto* next_owner=new(storage)SourceContext(context());
    require(next_owner->validate_prepared(*old_token.prepared).code==ContextCode::invalid_prepared,"same-address new lifetime cannot accept old token");
    require(next_owner->summary().accepted_records==0,"ABA rejection no change");next_owner->~SourceContext();
}
void ownership_and_allocations(){
    gig::TrackedResource resource;
    {
        auto owner=context(&resource);const auto before=resource.stats();resource.fail_after(0);
        auto bytes=system();auto prepared=owner.prepare(bytes,first);require(bool(prepared),"allocation-armed preparation");
        bytes[11]=std::byte{'C'};
        require(std::get<SystemEvent>(prepared.prepared->record().source.message).event_code=='O',"prepared source is owned");
        require(owner.summary().accepted_records==0,"prepared uncommitted");
        require(owner.commit(std::move(*prepared.prepared)).committed(),"allocation-armed commit");
        require(resource.stats()==before,"prepare and commit make no allocation requests");
        const auto accepted=owner.summary();
        {auto discarded=owner.prepare(system('S'),second);require(bool(discarded),"discardable candidate");}
        require(owner.summary()==accepted,"discard is rollback");
        auto malformed=system('S');malformed[0]=std::byte{255};
        require(!owner.prepare(malformed,second)&&owner.summary()==accepted,"source-invalid prepare atomic");
        require(resource.stats()==before,"failed prepare has no allocator requests");
    }
    require(resource.stats().live_bytes==0,"all reserved storage released");
}
static_assert(!std::is_copy_constructible_v<PreparedContext>);
static_assert(!std::is_move_assignable_v<PreparedContext>);
static_assert(std::is_nothrow_move_constructible_v<PreparedContext>);
static_assert(std::is_nothrow_move_constructible_v<ContextPreparation>);
static_assert(noexcept(std::declval<SourceContext&>().commit(std::declval<PreparedContext&&>())));
}
int main(){try{guards();lifetime();ownership_and_allocations();std::cout<<"prepared context guards/ownership/allocation tests passed; token_bytes="<<sizeof(PreparedContext)<<'\n';return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
