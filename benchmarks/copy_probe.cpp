#include "copy_probe.hpp"
std::uint64_t probe_event_copy(gig::MarketEvent event) noexcept {
    return event.metadata.sequence.data->value() ^ *event.metadata.provenance.generator_seed.data ^
        static_cast<std::uint64_t>(event.payload.index()) ^ static_cast<std::uint64_t>(event.metadata.source_record.data->view().size());
}
std::uint64_t probe_payload_copy(gig::AddOrder order) noexcept {
    return order.order_id.value() ^ static_cast<std::uint64_t>(order.price_ticks.value()) ^ order.quantity.value();
}
