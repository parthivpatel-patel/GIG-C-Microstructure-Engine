#include "gig/itch/sha256.hpp"
#include <algorithm>
#include <bit>
#include <cassert>
#include <cstring>

namespace gig::itch {
namespace {
constexpr std::array<std::uint32_t,64> constants{
0x428a2f98U,0x71374491U,0xb5c0fbcfU,0xe9b5dba5U,0x3956c25bU,0x59f111f1U,0x923f82a4U,0xab1c5ed5U,
0xd807aa98U,0x12835b01U,0x243185beU,0x550c7dc3U,0x72be5d74U,0x80deb1feU,0x9bdc06a7U,0xc19bf174U,
0xe49b69c1U,0xefbe4786U,0x0fc19dc6U,0x240ca1ccU,0x2de92c6fU,0x4a7484aaU,0x5cb0a9dcU,0x76f988daU,
0x983e5152U,0xa831c66dU,0xb00327c8U,0xbf597fc7U,0xc6e00bf3U,0xd5a79147U,0x06ca6351U,0x14292967U,
0x27b70a85U,0x2e1b2138U,0x4d2c6dfcU,0x53380d13U,0x650a7354U,0x766a0abbU,0x81c2c92eU,0x92722c85U,
0xa2bfe8a1U,0xa81a664bU,0xc24b8b70U,0xc76c51a3U,0xd192e819U,0xd6990624U,0xf40e3585U,0x106aa070U,
0x19a4c116U,0x1e376c08U,0x2748774cU,0x34b0bcb5U,0x391c0cb3U,0x4ed8aa4aU,0x5b9cca4fU,0x682e6ff3U,
0x748f82eeU,0x78a5636fU,0x84c87814U,0x8cc70208U,0x90befffaU,0xa4506cebU,0xbef9a3f7U,0xc67178f2U};
}
void Sha256::block(const std::byte* data) noexcept {
    std::array<std::uint32_t,64> words{};
    for(std::size_t i=0;i<16;++i)for(std::size_t j=0;j<4;++j)words[i]=(words[i]<<8U)|std::to_integer<std::uint32_t>(data[i*4+j]);
    for(std::size_t i=16;i<64;++i){
        const auto x=words[i-15],y=words[i-2];
        words[i]=words[i-16]+(std::rotr(x,7)^std::rotr(x,18)^(x>>3U))+words[i-7]+(std::rotr(y,17)^std::rotr(y,19)^(y>>10U));
    }
    auto a=state_[0],b=state_[1],c=state_[2],d=state_[3],e=state_[4],f=state_[5],g=state_[6],h=state_[7];
    for(std::size_t i=0;i<64;++i){
        const auto t1=h+(std::rotr(e,6)^std::rotr(e,11)^std::rotr(e,25))+((e&f)^((~e)&g))+constants[i]+words[i];
        const auto t2=(std::rotr(a,2)^std::rotr(a,13)^std::rotr(a,22))+((a&b)^(a&c)^(b&c));
        h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;
    }
    state_[0]+=a;state_[1]+=b;state_[2]+=c;state_[3]+=d;state_[4]+=e;state_[5]+=f;state_[6]+=g;state_[7]+=h;
}
bool Sha256::update(std::span<const std::byte> data) noexcept {
    constexpr auto max_bytes=UINT64_MAX/8U;
    if(data.size()>max_bytes-bytes_)return false;
    bytes_+=data.size();
    while(!data.empty()){
        if(used_==0&&data.size()>=64){block(data.data());data=data.subspan(64);continue;}
        const auto n=std::min(data.size(),pending_.size()-used_);
        std::memcpy(pending_.data()+used_,data.data(),n);used_+=n;data=data.subspan(n);
        if(used_==64){block(pending_.data());used_=0;}
    }
    return true;
}
Sha256Digest Sha256::finish()const noexcept {
    auto copy=*this;const auto bits=copy.bytes_*8U;
    copy.pending_[copy.used_++]=std::byte{0x80};
    if(copy.used_>56){std::fill(copy.pending_.begin()+static_cast<std::ptrdiff_t>(copy.used_),copy.pending_.end(),std::byte{0});copy.block(copy.pending_.data());copy.used_=0;}
    std::fill(copy.pending_.begin()+static_cast<std::ptrdiff_t>(copy.used_),copy.pending_.begin()+56,std::byte{0});
    for(std::size_t i=0;i<8;++i)copy.pending_[63-i]=static_cast<std::byte>((bits>>(i*8U))&0xffU);
    copy.block(copy.pending_.data());Sha256Digest digest{};
    for(std::size_t i=0;i<8;++i)for(std::size_t j=0;j<4;++j)digest[i*4+j]=static_cast<std::byte>((copy.state_[i]>>((3-j)*8U))&0xffU);
    return digest;
}
Sha256Digest sha256(std::span<const std::byte> data) noexcept {
    Sha256 hash;const bool accepted=hash.update(data);assert(accepted);(void)accepted;return hash.finish();
}
std::array<char,64> hex_digest(Sha256Digest digest) noexcept {
    constexpr char digits[]="0123456789abcdef";std::array<char,64> out{};
    for(std::size_t i=0;i<digest.size();++i){const auto n=std::to_integer<unsigned>(digest[i]);out[i*2]=digits[n>>4U];out[i*2+1]=digits[n&15U];}return out;
}
} // namespace gig::itch
