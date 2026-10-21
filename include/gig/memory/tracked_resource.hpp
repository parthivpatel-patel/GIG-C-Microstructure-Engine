#pragma once
#include <algorithm>
#include <cstddef>
#include <limits>
#include <memory_resource>
#include <optional>

namespace gig {
// Single-threaded diagnostics. Resource must outlive all containers using it.
class TrackedResource final : public std::pmr::memory_resource {
public:
    struct Stats {
        std::size_t attempts{}, allocations{}, deallocations{}, live_blocks{}, live_bytes{}, peak_bytes{};
        bool operator==(const Stats&) const = default;
    };
    explicit TrackedResource(std::pmr::memory_resource* upstream=std::pmr::get_default_resource(),
                             std::size_t budget=std::numeric_limits<std::size_t>::max()) noexcept
        : upstream_(upstream),budget_(budget) {}
    void fail_after(std::size_t successful_requests) noexcept { fail_=successful_requests; since_arm_=0; }
    void disable_failure() noexcept { fail_.reset(); }
    Stats stats() const noexcept { return stats_; }
private:
    std::pmr::memory_resource* upstream_;
    std::size_t budget_,since_arm_{};
    std::optional<std::size_t> fail_;
    Stats stats_;
    void* do_allocate(std::size_t bytes,std::size_t alignment) override {
        if (stats_.attempts==std::numeric_limits<std::size_t>::max()) throw std::bad_alloc{};
        ++stats_.attempts;
        if (fail_ && since_arm_++==*fail_) throw std::bad_alloc{};
        if (bytes>budget_-stats_.live_bytes || stats_.allocations==std::numeric_limits<std::size_t>::max()) throw std::bad_alloc{};
        void* result=upstream_->allocate(bytes,alignment);
        ++stats_.allocations;++stats_.live_blocks;stats_.live_bytes+=bytes;
        stats_.peak_bytes=std::max(stats_.peak_bytes,stats_.live_bytes);return result;
    }
    void do_deallocate(void* ptr,std::size_t bytes,std::size_t alignment) override {
        upstream_->deallocate(ptr,bytes,alignment);
        ++stats_.deallocations;--stats_.live_blocks;stats_.live_bytes-=bytes;
    }
    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override { return this==&other; }
};
} // namespace gig
