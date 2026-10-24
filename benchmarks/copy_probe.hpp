#pragma once
#include "gig/events/contracts.hpp"
// Separate translation unit + disabled IPO prevents caller from eliding ABI copies.
std::uint64_t probe_event_copy(gig::MarketEvent event) noexcept;
std::uint64_t probe_payload_copy(gig::AddOrder order) noexcept;
