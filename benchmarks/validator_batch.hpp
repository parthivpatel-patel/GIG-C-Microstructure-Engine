#pragma once
#include <cstdint>
#include <span>
#include "gig/market_event.hpp"
std::uint64_t count_valid(std::span<const gig::AddOrder> events, const gig::InstrumentRules& rules) noexcept;
