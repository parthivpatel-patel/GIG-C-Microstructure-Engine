#pragma once
#include <memory>
#include <memory_resource>
#include <span>
#include <string>
#include <vector>
#include "gig/market_event.hpp"
namespace gig::simulation {
enum class TimeInForce : std::uint8_t { gtc, ioc, fok };
struct SimOrder {
    OrderId id;Side side;PriceTicks limit;QuantityLots quantity;TimeInForce tif{TimeInForce::gtc};bool post_only{};
    bool operator==(const SimOrder&) const = default;
};
struct Latency {Duration base,jitter;bool operator==(const Latency&)const=default;};
struct SimConfig {
    Identity run_id;InstrumentRules rules;std::uint64_t seed;
    Latency arrival,cancel,acknowledgment,execution;
    std::size_t max_orders{1024},max_events{16384},max_fills{16384},max_commands{16384},max_reports{32768};
};
struct Resting {SimOrder order;std::uint64_t priority;std::size_t source_command;bool operator==(const Resting&)const=default;};
struct SimFill {
    Identity run_id;std::uint64_t seed;OrderId maker,taker;Side taker_side;PriceTicks price;QuantityLots quantity;
    SimulationTime matched_at,reported_at;std::size_t maker_command,taker_command;
    // All fills in this subsystem are SYNTHETIC / SIMULATED, never observed executions.
    bool operator==(const SimFill&)const=default;
};
enum class ReportKind : std::uint8_t { accepted,rejected,cancelled,cancel_rejected,expired,fill };
enum class RejectReason : std::uint8_t { none,not_active,post_only_would_take,fok_insufficient };
struct ClientReport {
    Identity run_id;ReportKind kind;RejectReason reason;OrderId order;SimulationTime delivered_at;QuantityLots quantity;
    std::optional<std::size_t> fill_index;
    bool operator==(const ClientReport&)const=default;
};
struct Conservation {
    std::uint64_t submitted{},executed_sides{},cancelled{},expired{},rejected{};
    bool operator==(const Conservation&)const=default;
};
struct QueuePosition {std::uint64_t orders_ahead,quantity_ahead;bool operator==(const QueuePosition&)const=default;};
class Simulator {
    struct State;
    struct Deleter {std::pmr::memory_resource* resource;void operator()(State*)const noexcept;};
    using StatePtr=std::unique_ptr<State,Deleter>;
    SimConfig config_;std::pmr::memory_resource* resource_;StatePtr state_;
    Simulator(SimConfig,std::pmr::memory_resource*,StatePtr) noexcept;
    Error command(SimulationTime,std::optional<SimOrder>,std::optional<OrderId>) noexcept;
public:
    static Result<Simulator> create(SimConfig,std::pmr::memory_resource* resource=std::pmr::get_default_resource()) noexcept;
    ~Simulator();Simulator(Simulator&&) noexcept;Simulator& operator=(Simulator&&) noexcept;
    Simulator(const Simulator&)=delete;Simulator& operator=(const Simulator&)=delete;
    Error submit_at(SimulationTime,const SimOrder&) noexcept;
    Error cancel_at(SimulationTime,OrderId) noexcept;
    Error advance_to(SimulationTime) noexcept;
    SimulationTime now()const noexcept;
    const SimConfig& config()const noexcept{return config_;}
    Conservation conservation()const noexcept;
    std::span<const Resting> exchange_orders()const noexcept;
    std::span<const SimFill> exchange_fills()const noexcept;
    std::span<const ClientReport> client_reports()const noexcept;
    std::optional<QueuePosition> exchange_queue_position(OrderId)const noexcept;
    Error check_invariants()const noexcept;
    Result<std::pmr::string> canonical()const noexcept;
};
} // namespace gig::simulation
