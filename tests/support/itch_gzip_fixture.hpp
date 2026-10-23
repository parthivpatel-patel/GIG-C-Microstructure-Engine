#pragma once
#include "itch_reconstruction_fixture.hpp"
#include <cstdint>
#include <vector>
namespace gig::itch::test {
// Independent RFC1952 fixture writer: fixed header + RFC1951 stored blocks.
// It does not call the production inflater or a compression library.
inline std::uint32_t fixture_crc32(std::span<const std::byte> bytes){
    std::uint32_t crc=0xffffffffU;
    for(const auto byte:bytes){crc^=std::to_integer<std::uint32_t>(byte);for(unsigned bit=0;bit<8;++bit)crc=(crc>>1U)^((crc&1U)!=0?0xedb88320U:0U);}
    return crc^0xffffffffU;
}
inline void little(std::vector<std::byte>& bytes,std::uint32_t value,unsigned width){for(unsigned i=0;i<width;++i){bytes.push_back(static_cast<std::byte>(value&255U));value>>=8U;}}
inline std::vector<std::byte> stored_gzip(std::span<const std::byte> source){
    std::vector<std::byte> bytes{std::byte{0x1f},std::byte{0x8b},std::byte{8},std::byte{0},std::byte{0},std::byte{0},std::byte{0},std::byte{0},std::byte{0},std::byte{255}};
    std::size_t offset=0;
    do{const auto count=std::min<std::size_t>(65535,source.size()-offset);const bool last=offset+count==source.size();bytes.push_back(last?std::byte{1}:std::byte{0});little(bytes,static_cast<std::uint32_t>(count),2);little(bytes,static_cast<std::uint32_t>(count)^0xffffU,2);bytes.insert(bytes.end(),source.begin()+static_cast<std::ptrdiff_t>(offset),source.begin()+static_cast<std::ptrdiff_t>(offset+count));offset+=count;}while(offset<source.size());
    little(bytes,fixture_crc32(source),4);little(bytes,static_cast<std::uint32_t>(source.size()&0xffffffffU),4);return bytes;
}
inline void fixture_frame(std::vector<std::byte>& bytes,std::span<const std::byte> payload){check(payload.size()<=65535,"gzip fixture frame bound");bytes.push_back(static_cast<std::byte>((payload.size()>>8U)&255U));bytes.push_back(static_cast<std::byte>(payload.size()&255U));bytes.insert(bytes.end(),payload.begin(),payload.end());}
inline std::vector<std::vector<std::byte>> streaming_records(){return {system(),directory(),directory(2,"TWO     "),add(101,10),add(201,20,200,2,'S'),add(102,20),reduce('E',102,4,1),reduce('X',101,3),reduce('D',101),replace(102,103,15),trade(2),cross(3),broken(2),system('S'),system('Q'),system('M'),system('E'),system('C')};}
inline std::vector<std::byte> framed_records(const std::vector<std::vector<std::byte>>& records,bool terminal=true){std::vector<std::byte> bytes;for(const auto& record:records)fixture_frame(bytes,record);if(terminal){bytes.push_back(std::byte{0});bytes.push_back(std::byte{0});}return bytes;}
} // namespace gig::itch::test
