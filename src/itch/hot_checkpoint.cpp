#include "hot_identity.hpp"
#include <algorithm>
namespace gig::itch {
namespace {
bool active(const ReconstructionSummary&s)noexcept{return s.initialization_verified&&!s.finished&&!s.input_complete&&!s.pending&&!s.rejected&&!s.unconsidered_record&&(s.eligibility==ReconstructionEligibility::eligible_synthetic_empty||s.eligibility==ReconstructionEligibility::eligible_synthetic_seed);}
bool code_valid(gig::Digest value)noexcept{auto v=value.view();return v.size()==64&&std::all_of(v.begin(),v.end(),[](char c){return(c>='0'&&c<='9')||(c>='a'&&c<='f');});}
Sha256Digest text_hash(std::string_view s)noexcept{return sha256(std::as_bytes(std::span{s.data(),s.size()}));}
gig::Error context_error(const Error&e)noexcept{return{e.code==Code::resource_exhausted?gig::ErrorCode::resource_exhausted:gig::ErrorCode::inconsistent_state,e.field};}
}
gig::Result<HotReconstructionIdentity> hot_identity(const HotReconstructionState&i,gig::Digest implementation)noexcept {
 using R=gig::Result<HotReconstructionIdentity>;
 if(!code_valid(implementation)||i.version!=1||!active(i.summary)||i.config.book_count==0||i.config.book_count>2||i.receipts.size()>i.config.max_source_records||i.receipts.size()>100000||i.canonical[0].size()>16*1024*1024||i.canonical[1].size()>16*1024*1024)return R::failure(gig::ErrorCode::inconsistent_state,"hot.identity_boundary");
 auto context=context_image_identity(i.context);if(!context){auto e=context_error(context.error);return R::failure(e.code,e.field);}
 HotReconstructionIdentity out{1,i.config,implementation,i.summary,*context.data,{},i.sequence_base,{}};
 hot_detail::Writer w;w.put(std::string_view("gig.itch.receipts_hot.v1"));w.put(i.receipts);if(!w.valid())return R::failure(gig::ErrorCode::capacity,"hot.receipts_digest");out.receipts_sha256=w.finish();
 for(std::size_t n=0;n<2;++n){if(i.engines[n].has_value()!=(n<i.config.book_count))return R::failure(gig::ErrorCode::inconsistent_state,"hot.engine_layout");if(n<i.config.book_count)out.native_sha256[n]=text_hash(i.canonical[n]);else if(!i.canonical[n].empty())return R::failure(gig::ErrorCode::inconsistent_state,"hot.unbound_engine");}
 return R::success(std::move(out));
}
gig::Result<HotReconstructionState> SyntheticReconstructor::hot_checkpoint(std::pmr::memory_resource*r)const noexcept {
 using R=gig::Result<HotReconstructionState>;
 if(!r||busy_||held_||moved_from_||!active(summary_)||(config_.initialization.kind!=InitialStateKind::authored_empty&&config_.initialization.kind!=InitialStateKind::complete_seed))return R::failure(gig::ErrorCode::recovery_required,"hot.accepted_boundary");
 auto context=context_.checkpoint(r);if(!context){auto e=context_error(context.error);return R::failure(e.code,e.field);}
 try {
  HotReconstructionState i(config_,std::move(*context.data),r);i.summary=summary_;i.sequence_base=sequence_base_;i.receipts.assign(receipts_.begin(),receipts_.end());
  for(std::size_t n=0;n<config_.book_count;++n){auto image=engines_[n]->checkpoint(r);if(!image)return R::failure(image.error.code,image.error.field);auto canonical=engines_[n]->canonical();if(!canonical)return R::failure(canonical.error.code,canonical.error.field);i.engines[n].emplace(std::move(*image.data));i.canonical[n].assign(canonical.data->begin(),canonical.data->end());}
  return R::success(std::move(i));
 }catch(const std::bad_alloc&){return R::failure(gig::ErrorCode::resource_exhausted,"hot.capture_memory");}
}
gig::Result<SyntheticReconstructor> SyntheticReconstructor::restore_hot(const HotReconstructionState&i,const HotReconstructionIdentity&trusted,const ReconstructionConfig&expected,gig::Digest implementation,std::pmr::memory_resource*r)noexcept {
 using R=gig::Result<SyntheticReconstructor>;const auto bad=[](std::string_view f){return R::failure(gig::ErrorCode::inconsistent_state,f);};
 if(!r||trusted.version!=1||trusted.config!=expected||i.config!=expected||trusted.implementation_sha256!=implementation||!code_valid(implementation))return R::failure(gig::ErrorCode::identity_mismatch,"hot.expected_contract");
 auto identity=hot_identity(i,implementation);if(!identity)return R::failure(identity.error.code,identity.error.field);
 if(identity.data->summary!=trusted.summary||identity.data->context_sha256!=trusted.context_sha256||identity.data->receipts_sha256!=trusted.receipts_sha256||identity.data->native_sha256!=trusted.native_sha256||identity.data->sequence_base!=trusted.sequence_base)return R::failure(gig::ErrorCode::identity_mismatch,"hot.trusted_identity");
 const bool seeded=expected.initialization.kind==InitialStateKind::complete_seed;
 const auto base=seeded?std::uint64_t{1}:std::uint64_t{0};
 if((!seeded&&expected.initialization.kind!=InitialStateKind::authored_empty)||
    i.summary.eligibility!=(seeded?ReconstructionEligibility::eligible_synthetic_seed:ReconstructionEligibility::eligible_synthetic_empty)||
    (seeded&&(!expected.seed_sha256||!code_valid(*expected.seed_sha256)||expected.initialization.boundary!=expected.context_policy.first_location||expected.initialization.boundary.ordinal.value()==0||i.context.summary.initialization_incomplete||i.context.lifecycle_stage==0)))return R::failure(gig::ErrorCode::unsupported,"hot.initialization_profile");
 for(std::size_t n=0;n<2;++n)if(i.sequence_base[n]!=(n<expected.book_count?base:0))return bad("hot.sequence_base");
 auto context=SourceContext::restore(i.context,expected.source,expected.context_policy,trusted.context_sha256,r);if(!context){auto e=context_error(context.error);return R::failure(e.code,e.field);}
 const auto&s=i.summary;
 if(s.context_committed!=i.receipts.size()||s.considered!=i.receipts.size()||i.context.summary.accepted_records!=i.receipts.size()||s.native_committed+s.external_observations!=s.context_committed)return bad("hot.accounting");
 std::array<std::uint64_t,2>counts{};std::uint64_t external=0;auto next=expected.context_policy.first_location;
 for(const auto&receipt:i.receipts){
  const auto length=expected_length(receipt.source.type);if(!length||receipt.source.location!=next||next.payload_offset.value()>UINT64_MAX-*length||next.ordinal.value()==UINT64_MAX)return bad("hot.receipt_location");
  const auto end=next.payload_offset.value()+*length;if(end>UINT64_MAX-2)return bad("hot.cursor_exhausted_profile");next={ByteOffset{end},ByteOffset{end+2},RecordOrdinal{next.ordinal.value()+1}};
  if(receipt.book_index&&*receipt.book_index>=expected.book_count)return bad("hot.receipt_book");
  if(receipt.disposition==SourceDisposition::native_committed){if(!receipt.book_index||receipt.native_sequence!=std::optional<std::uint64_t>{base+counts[*receipt.book_index]++})return bad("hot.derived_sequence");}
  else if(receipt.disposition==SourceDisposition::external_observation&&!receipt.native_sequence)++external;
  else return bad("hot.receipt_disposition");
 }
 if(counts!=s.native_counts||external!=s.external_observations)return bad("hot.derived_accounting");
 if(i.receipts.empty()){if(s.committed_position||s.physical_position||i.context.summary.last_location||i.context.next_location!=expected.context_policy.first_location||i.context.cursor_exhausted||(!seeded&&(!i.context.directories.empty()||!i.context.orders.empty()||!i.context.matches.empty()||!i.context.seed_retired.empty())))return bad("hot.empty_boundary");}
 else {const auto&last=i.receipts.back().source;if(s.committed_position!=last.location||s.physical_position!=last.location||i.context.summary.last_location!=last.location||i.context.summary.last_timestamp!=last.header.timestamp||i.context.cursor_exhausted||i.context.next_location!=next)return bad("hot.source_cursor");}
 auto factory=expected;
 if(seeded){factory.seed_sha256.reset();factory.initialization.kind=InitialStateKind::authored_empty;factory.initialization.boundary={ByteOffset{0},ByteOffset{2},RecordOrdinal{0}};factory.context_policy.first_location=factory.initialization.boundary;}
 auto made=create(factory,r);if(!made)return made;auto&out=*made.data;
 try {
  for(std::size_t n=0;n<expected.book_count;++n){
   const auto&b=*expected.bindings[n];const auto&image=*i.engines[n];
   if(image.journal.size()!=counts[n]+base||image.book.revision!=counts[n]+base)return bad("hot.native_accounting");
   if(seeded&&(image.journal.empty()||image.journal[0].disposition!=gig::JournalDisposition::recovery||!std::holds_alternative<gig::Snapshot>(image.journal[0].event.payload)))return bad("hot.seed_native_boundary");
   const auto config=out.engines_[n]->config();auto native=gig::ReplayEngine::restore(image,b.rules,config,b.limits,std::string_view(i.canonical[n]),r);if(!native)return R::failure(native.error.code,native.error.field);
   std::size_t orders=0;
   for(const auto&source:i.context.orders)if(source.active&&source.locate==b.locate){++orders;const auto order=std::find_if(image.book.orders.begin(),image.book.orders.end(),[&](const auto&o){return o.order.order_id.value()==source.reference.value();});const auto price=price4_to_ticks(source.resting_price,b.rules.tick_size);const auto quantity=shares_to_lots(source.remaining.value(),b.rules.lot_size);
    if(source.stock!=b.stock||order==image.book.orders.end()||!price||!quantity||order->order.price_ticks!=*price.data||order->order.quantity!=*quantity.data||order->order.side!=(source.side==Side::buy?gig::Side::buy:gig::Side::sell))return bad("hot.native_context_order");
   }
   if(orders!=image.book.orders.size())return bad("hot.native_context_count");
   out.engines_[n].emplace(std::move(*native.data));
  }
  for(const auto&source:i.context.orders)if(source.active&&std::none_of(expected.bindings.begin(),expected.bindings.begin()+static_cast<std::ptrdiff_t>(expected.book_count),[&](const auto&b){return b->locate==source.locate;}))return bad("hot.unrouted_active_order");
  // SourceContext is not move-assignable:construct the final owner around its
  // fresh instance guard,then move all already validated isolated native owners.
  SyntheticReconstructor restored(expected,std::move(*context.data),r);restored.receipts_.reserve(expected.max_source_records);restored.receipts_.assign(i.receipts.begin(),i.receipts.end());
  for(std::size_t n=0;n<expected.book_count;++n)restored.engines_[n].emplace(std::move(*out.engines_[n]));
  restored.summary_=s;restored.sequence_base_=i.sequence_base;return R::success(std::move(restored));
 }catch(const std::bad_alloc&){return R::failure(gig::ErrorCode::resource_exhausted,"hot.restore_memory");}
}
}
