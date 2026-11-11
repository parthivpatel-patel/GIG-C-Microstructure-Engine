#include "hot_identity.hpp"
#include <algorithm>
namespace gig::itch {
namespace {
bool bounded(const ContextStateImage&i)noexcept{return i.version==1&&i.directories.size()<=i.policy.max_directories&&i.directories.size()<=4096&&i.orders.size()<=4096&&i.matches.size()<=4096&&i.seed_retired.size()<=4096&&i.orders.size()<=i.policy.max_lifetime_orders&&i.seed_retired.size()<=i.policy.max_lifetime_orders-i.orders.size()&&i.matches.size()<=i.policy.max_matches;}
}
Result<Sha256Digest> context_image_identity(const ContextStateImage&i)noexcept {
 if(!bounded(i))return Result<Sha256Digest>::failure({Code::invalid_config,ByteOffset{0},"hot.context_limits",0,0});
 hot_detail::Writer w;w.put(std::string_view("gig.itch.context_hot.v1"));w.put(i);
 if(!w.valid())return Result<Sha256Digest>::failure({Code::stream_limit,ByteOffset{0},"hot.context_digest",0,0});
 return Result<Sha256Digest>::success(w.finish());
}
Result<ContextStateImage> SourceContext::checkpoint(std::pmr::memory_resource*r)const noexcept {
 if(!r||moved_from_||summary_.finished)return Result<ContextStateImage>::failure({Code::invalid_config,ByteOffset{0},"hot.context_boundary",0,0});
 if(directories_.size()>4096||orders_.size()>4096||matches_.size()>4096||seed_retired_.size()>4096)
  return Result<ContextStateImage>::failure({Code::record_limit,ByteOffset{0},"hot.context_limits",4096,0});
 try {
  ContextStateImage i(manifest_,policy_,r);i.summary=summary_;i.lifecycle_stage=lifecycle_stage_;i.next_location=next_location_;i.cursor_exhausted=cursor_exhausted_;
  i.directories.assign(directories_.begin(),directories_.end());i.orders.assign(orders_.begin(),orders_.end());i.matches.assign(matches_.begin(),matches_.end());i.seed_retired.assign(seed_retired_.begin(),seed_retired_.end());
  if(!bounded(i))return Result<ContextStateImage>::failure({Code::record_limit,ByteOffset{0},"hot.context_limits",0,0});
  return Result<ContextStateImage>::success(std::move(i));
 }catch(const std::bad_alloc&){return Result<ContextStateImage>::failure({Code::resource_exhausted,ByteOffset{0},"hot.context_capture",0,0});}
}
Result<SourceContext> SourceContext::restore(const ContextStateImage&i,SourceManifest manifest,ContextPolicy policy,Sha256Digest trusted,std::pmr::memory_resource*r)noexcept {
 const auto bad=[](std::string_view field){return Result<SourceContext>::failure({Code::invalid_config,ByteOffset{0},field,0,0});};
 if(!r||i.manifest!=manifest||i.policy!=policy)return bad("hot.context_contract");
 const auto hash=context_image_identity(i);if(!hash||*hash.data!=trusted)return bad("hot.context_identity");
 const auto&s=i.summary;
 if(s.finished||s.source_complete||s.bounded_prefix||s.finish_error!=ContextCode::none||i.lifecycle_stage>6||
    s.directories!=i.directories.size()||s.lifetime_orders!=i.orders.size()+i.seed_retired.size()||s.matches!=i.matches.size()||
    s.active_orders!=static_cast<std::size_t>(std::count_if(i.orders.begin(),i.orders.end(),[](const auto&o){return o.active;}))||
    (s.accepted_records!=0&&(!s.last_location||!s.last_timestamp)))return bad("hot.context_summary");
 if(s.last_location){const auto last=*s.last_location;
  if(last.frame_offset.value()>UINT64_MAX-2||last.payload_offset.value()!=last.frame_offset.value()+2)return bad("hot.context_location");
  if(!i.cursor_exhausted&&(last.ordinal.value()==UINT64_MAX||i.next_location.ordinal.value()!=last.ordinal.value()+1||i.next_location.frame_offset.value()<last.payload_offset.value()||i.next_location.frame_offset.value()>UINT64_MAX-2||i.next_location.payload_offset.value()!=i.next_location.frame_offset.value()+2))return bad("hot.context_cursor");
 }
 for(std::size_t n=0;n<i.directories.size();++n){const auto&d=i.directories[n];
  if(d.locate.value()==0)return bad("hot.context_directory");
  for(std::size_t j=0;j<n;++j)if(i.directories[j].locate==d.locate||i.directories[j].directory.stock==d.directory.stock)return bad("hot.context_directory_duplicate");
 }
 const auto directory=[&](StockLocate locate){return std::find_if(i.directories.begin(),i.directories.end(),[&](const auto&d){return d.locate==locate;});};
 for(std::size_t n=0;n<i.orders.size();++n){const auto&o=i.orders[n];auto d=directory(o.locate);
  if(o.reference.value()==0||d==i.directories.end()||d->directory.stock!=o.stock||(o.side!=Side::buy&&o.side!=Side::sell)||o.active!=(o.remaining.value()!=0))return bad("hot.context_order");
  for(std::size_t j=0;j<n;++j)if(i.orders[j].reference==o.reference)return bad("hot.context_order_duplicate");
  if(std::find(i.seed_retired.begin(),i.seed_retired.end(),o.reference)!=i.seed_retired.end())return bad("hot.context_retired_conflict");
 }
 for(std::size_t n=0;n<i.seed_retired.size();++n){if(i.seed_retired[n].value()==0||std::find(i.seed_retired.begin(),i.seed_retired.begin()+static_cast<std::ptrdiff_t>(n),i.seed_retired[n])!=i.seed_retired.begin()+static_cast<std::ptrdiff_t>(n))return bad("hot.context_retired_duplicate");}
 for(std::size_t n=0;n<i.matches.size();++n){const auto&m=i.matches[n];if(directory(m.locate)==i.directories.end()||static_cast<unsigned>(m.kind)>static_cast<unsigned>(MatchKind::cross))return bad("hot.context_match");for(std::size_t j=0;j<n;++j)if(i.matches[j].number==m.number)return bad("hot.context_match_duplicate");}
 auto made=create(std::move(manifest),policy,r);if(!made)return made;
 auto&out=*made.data;
 try {
  out.seed_retired_.assign(i.seed_retired.begin(),i.seed_retired.end());
  if(out.seed_retired_.capacity()>(policy.memory_budget_bytes-out.summary_.reserved_bytes)/sizeof(OrderReference))return bad("hot.context_memory_budget");
  const auto reserved=out.summary_.reserved_bytes+out.seed_retired_.capacity()*sizeof(OrderReference);
  if(reserved!=s.reserved_bytes)return bad("hot.context_capacity_contract");
  out.directories_.assign(i.directories.begin(),i.directories.end());out.orders_.assign(i.orders.begin(),i.orders.end());out.matches_.assign(i.matches.begin(),i.matches.end());
  out.summary_=s;out.lifecycle_stage_=i.lifecycle_stage;out.next_location_=i.next_location;out.cursor_exhausted_=i.cursor_exhausted;
  // create allocated a new instance guard. No old PreparedContext becomes valid.
  return made;
 }catch(const std::bad_alloc&){return Result<SourceContext>::failure({Code::resource_exhausted,ByteOffset{0},"hot.context_restore",0,0});}
}
}
