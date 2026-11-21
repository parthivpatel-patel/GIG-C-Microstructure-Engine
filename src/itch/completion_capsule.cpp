#include "gig/itch/completion_capsule.hpp"
#include <algorithm>
#include <array>
namespace gig::itch {
namespace {
constexpr std::size_t header=24;
constexpr std::array magic{std::byte{'G'},std::byte{'I'},std::byte{'G'},std::byte{'S'},std::byte{'C'},std::byte{'A'},std::byte{'P'},std::byte{'1'}};
std::uint64_t length(std::span<const std::byte> bytes,std::size_t offset)noexcept {
 std::uint64_t out=0;for(std::size_t n=0;n<8;++n)out|=std::uint64_t(std::to_integer<unsigned>(bytes[offset+n]))<<(n*8U);return out;
}
}
gig::Result<std::pmr::vector<std::byte>> encode_completion_capsule(std::span<const std::byte> image,const DurableAdmission&trusted,std::span<const std::byte> source,const SourceRecoveryAdmission&a,std::pmr::memory_resource*r)noexcept {
 using R=gig::Result<std::pmr::vector<std::byte>>;
 if(!r||image.size()>completion_capsule_max_bytes-header||source.size()>completion_capsule_max_bytes-header-image.size())return R::failure(gig::ErrorCode::capacity,"completion_capsule.budget");
 // Verify the whole interpretation before allocating any published capsule bytes.
 {auto completed=resume_complete_source(image,trusted,source,a,r);if(!completed)return R::failure(completed.error.code,completed.error.field);}
 try {
  std::pmr::vector<std::byte> out(r);out.reserve(header+image.size()+source.size());out.insert(out.end(),magic.begin(),magic.end());
  for(const auto size:{image.size(),source.size()})for(std::size_t n=0;n<8;++n)out.push_back(static_cast<std::byte>((static_cast<std::uint64_t>(size)>>(n*8U))&255U));
  out.insert(out.end(),image.begin(),image.end());out.insert(out.end(),source.begin(),source.end());return R::success(std::move(out));
 }catch(const std::bad_alloc&){return R::failure(gig::ErrorCode::resource_exhausted,"completion_capsule.output");}
}
gig::Result<SyntheticReconstructor> restore_completion_capsule(std::span<const std::byte> bytes,const CompletionCapsuleAdmission&a,std::pmr::memory_resource*r)noexcept {
 using R=gig::Result<SyntheticReconstructor>;
 if(!r||bytes.size()>completion_capsule_max_bytes)return R::failure(gig::ErrorCode::capacity,"completion_capsule.budget");
 if(sha256(bytes)!=a.capsule_sha256)return R::failure(gig::ErrorCode::identity_mismatch,"completion_capsule.digest");
 if(bytes.size()<header||!std::equal(magic.begin(),magic.end(),bytes.begin()))return R::failure(gig::ErrorCode::unsupported,"completion_capsule.version");
 const auto image=length(bytes,8),source=length(bytes,16),remaining=bytes.size()-header;
 if(image<56||image>remaining||source!=remaining-image||source<2)return R::failure(gig::ErrorCode::malformed,"completion_capsule.lengths");
 return resume_complete_source(bytes.subspan(header,static_cast<std::size_t>(image)),a.checkpoint,bytes.subspan(header+static_cast<std::size_t>(image),static_cast<std::size_t>(source)),a.source,r);
}
}
