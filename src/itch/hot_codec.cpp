#include "gig/itch/durable_checkpoint.hpp"
#include "hot_codec_fields.hpp"
#include <algorithm>
#include <bit>
#include <limits>
namespace gig::itch {
namespace codec_detail {
struct Failure {gig::ErrorCode code;std::string_view field;};
[[noreturn]] void fail(gig::ErrorCode c,std::string_view f){throw Failure{c,f};}
template<class T> T take(gig::Result<T> x){if(!x)fail(x.error.code,x.error.field);return std::move(*x.data);}
struct Output {
 std::pmr::vector<std::byte> data;Sha256* hash{};std::size_t bytes{};
 explicit Output(std::pmr::memory_resource*r):data(r){}
 explicit Output(Sha256&h):data(std::pmr::null_memory_resource()),hash(&h){}
 void raw(std::span<const std::byte>b){if(b.size()>durable_max_bytes-bytes)fail(gig::ErrorCode::capacity,"durable.byte_budget");bytes+=b.size();if(hash){if(!hash->update(b))fail(gig::ErrorCode::capacity,"durable.hash");}else data.insert(data.end(),b.begin(),b.end());}
 void number(std::uint64_t n){std::array<std::byte,8>b{};for(auto&x:b){x=static_cast<std::byte>(n&255);n>>=8;}raw(b);}
};
struct Input {
 std::span<const std::byte> data;std::pmr::memory_resource* resource;std::size_t allocated{},nodes{};
 std::span<const std::byte> raw(std::size_t n){if(n>data.size())fail(gig::ErrorCode::malformed,"durable.truncated");auto out=data.first(n);data=data.subspan(n);return out;}
 std::uint64_t number(){auto b=raw(8);std::uint64_t n=0;for(std::size_t i=0;i<8;++i)n|=static_cast<std::uint64_t>(b[i])<<(i*8);return n;}
 void allocation(std::size_t n){constexpr std::size_t max=128U*1024U*1024U;if(n>max-allocated)fail(gig::ErrorCode::capacity,"durable.allocation_budget");allocated+=n;}
 void node(){if(++nodes>2000000)fail(gig::ErrorCode::capacity,"durable.node_budget");}
};
template<class T,class=void>struct Codec;
template<class T>void put(Output&o,const T&v){Codec<T>::put(o,v);}
template<class T>T get(Input&i){i.node();return Codec<T>::get(i);}
template<class T>struct Codec<T,std::enable_if_t<std::is_integral_v<T>>>{
 static void put(Output&o,T v){o.number(static_cast<std::uint64_t>(v));}
 static T get(Input&i){auto n=i.number();
  if constexpr(std::is_same_v<T,bool>){if(n>1)fail(gig::ErrorCode::malformed,"durable.boolean");return n!=0;}
  else if constexpr(std::is_signed_v<T>){const auto s=std::bit_cast<std::int64_t>(n);if(!std::in_range<T>(s))fail(gig::ErrorCode::invalid_range,"durable.signed");return static_cast<T>(s);}
  else {if(!std::in_range<T>(n))fail(gig::ErrorCode::invalid_range,"durable.unsigned");return static_cast<T>(n);}
 }
};
template<>struct Codec<char>{static void put(Output&o,char v){o.number(static_cast<unsigned char>(v));}static char get(Input&i){auto n=i.number();if(n>127)fail(gig::ErrorCode::malformed,"durable.ascii");return static_cast<char>(n);}};
template<>struct Codec<std::byte>{static void put(Output&o,std::byte v){gig::itch::codec_detail::put(o,static_cast<std::uint8_t>(v));}static std::byte get(Input&i){return static_cast<std::byte>(gig::itch::codec_detail::get<std::uint8_t>(i));}};
template<class T>struct EnumLimit;
#define E(T,N) template<>struct EnumLimit<T>{static constexpr unsigned max=N;};
E(gig::MissingReason,3) E(gig::Side,1) E(gig::ClockDomain,3) E(gig::SequenceUnit,1)
E(gig::Origin,1) E(gig::Source,4) E(gig::TransformationKind,4) E(gig::types::TimestampUnit,3)
E(gig::ReplacePriority,1) E(gig::ResetReason,3) E(gig::SnapshotKind,1) E(gig::SnapshotCoverage,1) E(gig::SessionAction,3)
E(gig::JournalDisposition,3) E(gig::OrderingPolicy,1) E(gig::InitialBookState,1)
E(Origin,2) E(Initialization,1) E(ContextCode,static_cast<unsigned>(ContextCode::invalid_observation)) E(DecodeProfile,3) E(MatchKind,2)
E(InitialStateKind,4) E(ReconstructionEligibility,3) E(SourceDisposition,7)
#undef E
template<class T>struct Codec<T,std::enable_if_t<std::is_enum_v<T>>>{
 static void put(Output&o,T v){o.number(static_cast<std::uint64_t>(v));}
 static T get(Input&i){auto n=i.number();if constexpr(std::is_same_v<T,Side>){if(n!='B'&&n!='S')fail(gig::ErrorCode::invalid_enum,"durable.side");}
  else if(n>EnumLimit<T>::max){fail(gig::ErrorCode::invalid_enum,"durable.enum");}
  return static_cast<T>(n);}
};
template<class Tag,std::integral R,R Min,bool A>struct Codec<gig::types::Scalar<Tag,R,Min,A>>{
 using T=gig::types::Scalar<Tag,R,Min,A>;static void put(Output&o,T v){codec_detail::put(o,v.value());}static T get(Input&i){return take(T::make(codec_detail::get<R>(i)));}
};
template<class Tag,class R>struct Codec<WireNumber<Tag,R>>{using T=WireNumber<Tag,R>;static void put(Output&o,T v){codec_detail::put(o,v.value());}static T get(Input&i){return T{codec_detail::get<R>(i)};}};
template<class Tag>struct Codec<Position<Tag>>{using T=Position<Tag>;static void put(Output&o,T v){o.number(v.value());}static T get(Input&i){return T{i.number()};}};
template<class T>struct TokenCodec{
 static void put(Output&o,const T&v){const auto s=v.view();o.number(s.size());o.raw(std::as_bytes(std::span{s.data(),s.size()}));}
 static T get(Input&i){auto n=i.number();if(n>128)fail(gig::ErrorCode::capacity,"durable.token");auto b=i.raw(static_cast<std::size_t>(n));auto v=T::make({reinterpret_cast<const char*>(b.data()),b.size()});if(!v)fail(gig::ErrorCode::malformed,"durable.token");return *v.data;}
};
template<std::size_t N>struct Codec<gig::Token<N>>:TokenCodec<gig::Token<N>>{};
template<>struct Codec<SourceIdentity>:TokenCodec<SourceIdentity>{};
template<class T,std::size_t N>struct Codec<std::array<T,N>>{
 static void put(Output&o,const std::array<T,N>&v){for(const auto&x:v)codec_detail::put(o,x);}
 template<std::size_t...J>static std::array<T,N> read(Input&i,std::index_sequence<J...>){return {((void)J,codec_detail::get<T>(i))...};}
 static std::array<T,N> get(Input&i){return read(i,std::make_index_sequence<N>{});}
};
template<std::size_t N>struct Codec<Text<N>>{static void put(Output&o,const Text<N>&v){o.raw(std::as_bytes(std::span{v.bytes}));}static Text<N> get(Input&i){Text<N>v;auto b=i.raw(N);std::copy(b.begin(),b.end(),reinterpret_cast<std::byte*>(v.bytes.data()));return v;}};
template<class T>struct Codec<std::optional<T>>{
 static void put(Output&o,const std::optional<T>&v){codec_detail::put(o,v.has_value());if(v)codec_detail::put(o,*v);}
 static std::optional<T> get(Input&i){if(!codec_detail::get<bool>(i))return {};return codec_detail::get<T>(i);}
};
template<class T>struct Codec<gig::Available<T>>{
 static void put(Output&o,const gig::Available<T>&v){codec_detail::put(o,v.reason);codec_detail::put(o,v.data);}
 static gig::Available<T> get(Input&i){auto why=codec_detail::get<gig::MissingReason>(i);auto v=codec_detail::get<std::optional<T>>(i);if(v.has_value()!=(why==gig::MissingReason::none))fail(gig::ErrorCode::inconsistent_metadata,"durable.available");return {std::move(v),why};}
};
template<class T,std::size_t N>struct Codec<gig::BoundedList<T,N>>{
 static void put(Output&o,const gig::BoundedList<T,N>&v){if(v.count>N)fail(gig::ErrorCode::capacity,"durable.bounded_list");o.number(v.count);for(std::size_t n=0;n<N;++n){if(v.items[n].has_value()!=(n<v.count))fail(gig::ErrorCode::inconsistent_state,"durable.bounded_list");if(n<v.count)codec_detail::put(o,*v.items[n]);}}
 static gig::BoundedList<T,N> get(Input&i){auto n=i.number();if(n>N)fail(gig::ErrorCode::capacity,"durable.bounded_list");gig::BoundedList<T,N>v;for(std::uint64_t j=0;j<n;++j){auto e=v.append(codec_detail::get<T>(i));if(e)fail(e.code,"durable.bounded_list");}return v;}
};
template<class T>struct Codec<std::pmr::vector<T>>{
 static void put(Output&o,const std::pmr::vector<T>&v){if(v.size()>4096)fail(gig::ErrorCode::capacity,"durable.records");o.number(v.size());for(const auto&x:v)codec_detail::put(o,x);}
 static std::pmr::vector<T> get(Input&i){auto n=i.number();if(n>4096||n>i.data.size())fail(gig::ErrorCode::capacity,"durable.records");i.allocation(static_cast<std::size_t>(n)*sizeof(T));std::pmr::vector<T>v(i.resource);v.reserve(static_cast<std::size_t>(n));for(std::uint64_t j=0;j<n;++j)v.push_back(codec_detail::get<T>(i));return v;}
};
template<>struct Codec<std::pmr::string>{
 static void put(Output&o,const std::pmr::string&v){o.number(v.size());o.raw(std::as_bytes(std::span{v.data(),v.size()}));}
 static std::pmr::string get(Input&i){auto n=i.number();if(n>16U*1024U*1024U)fail(gig::ErrorCode::capacity,"durable.string");auto b=i.raw(static_cast<std::size_t>(n));i.allocation(b.size()+1);return {reinterpret_cast<const char*>(b.data()),b.size(),i.resource};}
};
template<class...T>struct Codec<std::variant<T...>>{
 using V=std::variant<T...>;
 static void put(Output&o,const V&v){o.number(v.index());std::visit([&](const auto&x){codec_detail::put(o,x);},v);}
 template<std::size_t J=0>static V at(Input&i,std::uint64_t n){if constexpr(J<sizeof...(T)){if(n==J)return V{std::in_place_index<J>,codec_detail::get<std::variant_alternative_t<J,V>>(i)};return at<J+1>(i,n);}else fail(gig::ErrorCode::unsupported,"durable.variant");}
 static V get(Input&i){auto n=i.number();return at(i,n);}
};
template<class T>struct Codec<T,std::void_t<decltype(Record<T>::fields())>>{
 static void put(Output&o,const T&v){std::apply([&](auto...m){(codec_detail::put(o,v.*m),...);},Record<T>::fields());}
 static T get(Input&i){return std::apply([&](auto...m){return T{codec_detail::get<std::remove_cvref_t<decltype(std::declval<T>().*m)>>(i)...};},Record<T>::fields());}
};
template<>struct Codec<ContextStateImage>{
 static void put(Output&o,const ContextStateImage&v){std::apply([&](auto...m){(codec_detail::put(o,v.*m),...);},Record<ContextStateImage>::fields());}
 static ContextStateImage get(Input&i){auto version=codec_detail::get<std::uint32_t>(i);if(version!=1)fail(gig::ErrorCode::unsupported,"durable.context_version");auto manifest=codec_detail::get<SourceManifest>(i);auto policy=codec_detail::get<ContextPolicy>(i);ContextStateImage v(manifest,policy,i.resource);v.version=version;v.summary=codec_detail::get<ContextSummary>(i);v.lifecycle_stage=codec_detail::get<std::uint8_t>(i);v.next_location=codec_detail::get<Location>(i);v.cursor_exhausted=codec_detail::get<bool>(i);v.directories=codec_detail::get<decltype(v.directories)>(i);v.orders=codec_detail::get<decltype(v.orders)>(i);v.matches=codec_detail::get<decltype(v.matches)>(i);v.seed_retired=codec_detail::get<decltype(v.seed_retired)>(i);return v;}
};
template<>struct Codec<HotReconstructionState>{
 static void put(Output&o,const HotReconstructionState&v){codec_detail::put(o,v.version);codec_detail::put(o,v.config);codec_detail::put(o,v.context);codec_detail::put(o,v.summary);codec_detail::put(o,v.sequence_base);codec_detail::put(o,v.receipts);codec_detail::put(o,v.engines);codec_detail::put(o,v.canonical);}
 static HotReconstructionState get(Input&i){auto version=codec_detail::get<std::uint32_t>(i);if(version!=1)fail(gig::ErrorCode::unsupported,"durable.hot_version");auto config=codec_detail::get<ReconstructionConfig>(i);auto context=codec_detail::get<ContextStateImage>(i);HotReconstructionState v(config,std::move(context),i.resource);v.summary=codec_detail::get<ReconstructionSummary>(i);v.sequence_base=codec_detail::get<decltype(v.sequence_base)>(i);v.receipts=codec_detail::get<decltype(v.receipts)>(i);v.engines=codec_detail::get<decltype(v.engines)>(i);v.canonical=codec_detail::get<decltype(v.canonical)>(i);return v;}
};
bool bounded_contract(const ReconstructionConfig&c)noexcept {
 if(c.book_count<1||c.book_count>2||c.max_source_records>4096||c.context_policy.max_directories>4096||c.context_policy.max_lifetime_orders>4096||c.context_policy.max_matches>4096||c.context_policy.memory_budget_bytes>64U*1024U*1024U||c.receipt_budget_bytes>64U*1024U*1024U)return false;
 for(const auto&b:c.bindings)if(b&&(b->limits.max_orders>4096||b->limits.max_levels>4096||b->limits.max_snapshot_depth>4096||b->max_journal_records>4096))return false;
 return true;
}
constexpr std::array<std::byte,8> magic{std::byte{'G'},std::byte{'I'},std::byte{'G'},std::byte{'I'},std::byte{'T'},std::byte{'C'},std::byte{'H'},std::byte{'1'}};
}
Sha256Digest hot_contract_sha256(const ReconstructionConfig&c)noexcept {
 try{Sha256 hash;codec_detail::Output o(hash);codec_detail::put(o,c);return hash.finish();}catch(...){return {};}
}
gig::Result<std::pmr::vector<std::byte>> encode_hot_checkpoint(const HotReconstructionState&v,SourceIdentity capture,std::uint64_t generation,gig::Digest code,std::pmr::memory_resource*r)noexcept {
 using R=gig::Result<std::pmr::vector<std::byte>>;using namespace codec_detail;
 if(!r)return R::failure(gig::ErrorCode::invalid_range,"durable.resource");
 try{
  if(!bounded_contract(v.config))fail(gig::ErrorCode::capacity,"durable.contract_limits");
  auto identity=take(hot_identity(v,code));auto validate=take(SyntheticReconstructor::restore_hot(v,identity,v.config,code,r));(void)validate;
  Output body(r);put(body,capture);put(body,generation);put(body,code);put(body,v);auto hash=sha256(body.data);
  Output out(r);out.raw(magic);out.number(1);out.number(body.data.size());out.raw(hash);out.raw(body.data);return R::success(std::move(out.data));
 }catch(const Failure&e){return R::failure(e.code,e.field);}catch(const std::bad_alloc&){return R::failure(gig::ErrorCode::resource_exhausted,"durable.memory");}
}
gig::Result<SyntheticReconstructor> restore_durable_checkpoint(std::span<const std::byte>b,const DurableAdmission&trusted,std::pmr::memory_resource*r)noexcept {
 using R=gig::Result<SyntheticReconstructor>;using namespace codec_detail;
 if(!r||b.size()>durable_max_bytes)return R::failure(gig::ErrorCode::capacity,"durable.byte_budget");
 if(sha256(b)!=trusted.artifact_sha256)return R::failure(gig::ErrorCode::identity_mismatch,"durable.artifact_digest");
 try{
  Input i{b,r};auto m=i.raw(8);if(!std::equal(m.begin(),m.end(),magic.begin()))fail(gig::ErrorCode::malformed,"durable.magic");if(i.number()!=1)fail(gig::ErrorCode::unsupported,"durable.schema_version");auto length=i.number();auto expected=i.raw(32);if(length!=i.data.size())fail(gig::ErrorCode::malformed,"durable.length");const auto hash=sha256(i.data);if(!std::equal(hash.begin(),hash.end(),expected.begin()))fail(gig::ErrorCode::identity_mismatch,"durable.payload_digest");
  const auto capture=get<SourceIdentity>(i);const auto generation=get<std::uint64_t>(i);const auto code=get<gig::Digest>(i);
  if(capture!=trusted.capture||generation!=trusted.generation||code!=trusted.implementation_sha256)fail(gig::ErrorCode::identity_mismatch,"durable.capture_generation_code");
  auto state=get<HotReconstructionState>(i);if(!bounded_contract(state.config))fail(gig::ErrorCode::capacity,"durable.contract_limits");if(!i.data.empty())fail(gig::ErrorCode::malformed,"durable.trailing_bytes");if(hot_contract_sha256(state.config)!=trusted.contract_sha256)fail(gig::ErrorCode::identity_mismatch,"durable.contract_digest");
  auto identity=take(hot_identity(state,code));return SyntheticReconstructor::restore_hot(state,identity,state.config,code,r);
 }catch(const Failure&e){return R::failure(e.code,e.field);}catch(const std::bad_alloc&){return R::failure(gig::ErrorCode::resource_exhausted,"durable.memory");}
}
}
