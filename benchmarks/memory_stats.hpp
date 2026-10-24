#pragma once
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>
namespace gig::benchmark_memory {
// Native post-exec mm high-water RSS. Linux rusage may retain a pre-exec image floor.
inline void emit_native_peak_rss() {
    std::cout<<",\"native_vm_hwm_bytes\":";
#if defined(__linux__)
    std::ifstream status("/proc/self/status");std::string line;
    while(std::getline(status,line))if(line.starts_with("VmHWM:")){
        auto first=line.data()+6;const auto last=line.data()+line.size();while(first!=last && (*first==' ' || *first=='\t'))++first;
        std::uint64_t kib{};auto r=std::from_chars(first,last,kib);
        if(r.ec==std::errc{} && kib<=std::numeric_limits<std::uint64_t>::max()/1024){std::cout<<kib*1024;return;}
    }
#endif
    std::cout<<"null";
}
}
