#include "gig/book/order_book.hpp"
#include <algorithm>
#include <cassert>
#include <charconv>
#include <list>
#include <map>
#include <stdexcept>
#include <unordered_map>

namespace gig {
namespace {
struct IdHash { std::size_t operator()(OrderId id) const noexcept { return std::hash<std::uint64_t>{}(id.value()); } };
struct Level {
    std::pmr::list<RestingOrder> fifo;
    std::uint64_t quantity{},count{};
    explicit Level(std::pmr::memory_resource* r):fifo(r) {}
};
struct Location { Side side; PriceTicks price; std::pmr::list<RestingOrder>::iterator node; };
using Prices=std::pmr::map<PriceTicks,Level>;
using Index=std::pmr::unordered_map<OrderId,Location,IdHash>;
Error increase(std::uint64_t& total,std::uint64_t amount) noexcept {
    auto sum=types::detail::add(total,amount);if (!sum) return {ErrorCode::overflow,"quantity_ledger"};total=*sum.data;return {};
}
Error credit(QuantityLedger& ledger,std::uint64_t& category,std::uint64_t amount) noexcept {
    if (const auto e=increase(category,amount)) return e;
    return increase(ledger.total_in,amount);
}
Error debit(QuantityLedger& ledger,std::uint64_t& category,std::uint64_t amount) noexcept {
    if (const auto e=increase(category,amount)) return e;
    return increase(ledger.total_out,amount);
}
QuantityLots lots(std::uint64_t value) noexcept { return *QuantityLots::make(value).data; }
DepthLevel depth_level(const Prices::value_type& p) noexcept { return {p.first,lots(p.second.quantity),p.second.count}; }
} // namespace
struct OrderBook::State {
    BookSession session;
    Prices bids,asks;
    Index index;
    QuantityLedger ledger{};
    std::uint64_t remaining{},next_priority{},revision{};
    State(BookSession s,std::pmr::memory_resource* r):session(s),bids(r),asks(r),index(r) { index.max_load_factor(1.0F); }
    Prices& prices(Side s) noexcept { return s==Side::buy?bids:asks; }
    const Prices& prices(Side s) const noexcept { return s==Side::buy?bids:asks; }
    void erase(Index::iterator found,bool keep_level=false) noexcept {
        const auto loc=found->second;
        auto& levels=prices(loc.side);auto level=levels.find(loc.price);
        level->second.quantity-=loc.node->order.quantity.value();--level->second.count;
        level->second.fifo.erase(loc.node);index.erase(found);
        if (level->second.count==0 && !keep_level) levels.erase(level);
    }
    bool would_cross(const AddOrder& pending,std::optional<OrderId> removed) const noexcept {
        std::optional<PriceTicks> bid,ask;
        const auto visible=[&](const Prices::value_type& level) {
            if (!removed || level.second.count!=1) return true;
            return level.second.fifo.front().order.order_id!=*removed;
        };
        for (auto i=bids.rbegin();i!=bids.rend();++i) if (visible(*i)) { bid=i->first;break; }
        for (const auto& level:asks) if (visible(level)) { ask=level.first;break; }
        if (pending.side==Side::buy && (!bid || pending.price_ticks>*bid)) bid=pending.price_ticks;
        if (pending.side==Side::sell && (!ask || pending.price_ticks<*ask)) ask=pending.price_ticks;
        return bid && ask && *bid>*ask;
    }
    // All allocations occur before the final transfer/erase section.
    Error insert_staged(AddOrder order,std::uint64_t priority,const BookLimits& limits,
                        std::pmr::memory_resource* resource,std::optional<OrderId> removed={}) {
        auto collision=index.find(order.order_id);
        if (collision!=index.end() && (!removed || order.order_id!=*removed)) return {ErrorCode::duplicate,"order_id"};
        const std::size_t after_count=index.size()+(removed?0U:1U);
        if (after_count>limits.max_orders) return {ErrorCode::capacity,"book.orders"};
        auto& levels=prices(order.side);auto target=levels.find(order.price_ticks);
        const bool new_level=target==levels.end();
        std::uint64_t base_quantity=new_level?0:target->second.quantity;
        std::uint64_t base_count=new_level?0:target->second.count;
        bool removed_level=false;
        if (removed) {
            const auto old=index.find(*removed);
            if (old==index.end()) return {ErrorCode::not_found,"order_id"};
            const auto& old_level=prices(old->second.side).find(old->second.price)->second;
            const bool same=old->second.side==order.side && old->second.price==order.price_ticks;
            if (same) { base_quantity-=old->second.node->order.quantity.value();--base_count; }
            removed_level=old_level.count==1 && !same;
        }
        const auto count_sum=types::detail::add(base_count,std::uint64_t{1});
        if (!count_sum) return {ErrorCode::overflow,"level.count"};
        const auto level_sum=types::detail::add(base_quantity,order.quantity.value());
        if (!level_sum) return {ErrorCode::overflow,"level.quantity"};
        const auto level_count=bids.size()+asks.size()+(new_level?1U:0U)-(removed_level?1U:0U);
        if (level_count>limits.max_levels) return {ErrorCode::capacity,"book.levels"};
        if (would_cross(order,removed)) return {ErrorCode::crossed_quote,"book"};
        Prices staged_levels(resource);
        if (new_level) staged_levels.try_emplace(order.price_ticks,resource);
        std::pmr::list<RestingOrder> staged_fifo(resource);
        staged_fifo.push_back({order,priority});
        Index staged_index(resource);
        staged_index.emplace(order.order_id,Location{order.side,order.price_ticks,staged_fifo.begin()});
        auto index_node=staged_index.extract(order.order_id);
        // Rehash is the LAST potentially throwing operation. Bucket capacity is not canonical state.
        // An empty unordered_map may report one sentinel bucket while its first
        // insertion still allocates real buckets. Establish insertion capacity
        // before transferring any level/list node, including that first insert.
        if (index.empty() || after_count>index.bucket_count()) {
            const auto desired=std::max(after_count,std::min(limits.max_orders,index.bucket_count()*2U));
            index.reserve(desired);
        }
        if (removed) {
            auto old=index.find(*removed);
            const bool keep=old->second.side==order.side && old->second.price==order.price_ticks;
            erase(old,keep);
        }
        if (new_level) target=levels.insert(staged_levels.extract(order.price_ticks)).position;
        target->second.fifo.splice(target->second.fifo.end(),staged_fifo);
        target->second.quantity=*level_sum.data;target->second.count=*count_sum.data;
        index.insert(std::move(index_node));
        return {};
    }
};
void OrderBook::Deleter::operator()(State* p) const noexcept {
    if (p) { std::pmr::polymorphic_allocator<State> allocator(resource);allocator.delete_object(p); }
}
OrderBook::StatePtr OrderBook::allocate_state(BookSession s,std::pmr::memory_resource* r) {
    std::pmr::polymorphic_allocator<State> allocator(r);return StatePtr(allocator.new_object<State>(s,r),Deleter{r});
}
OrderBook::OrderBook(InstrumentRules r,BookLimits l,std::pmr::memory_resource* resource,StatePtr state) noexcept
    :rules_(r),limits_(l),resource_(resource),state_(std::move(state)) {}
OrderBook::~OrderBook()=default;
OrderBook::OrderBook(OrderBook&&) noexcept=default;
OrderBook& OrderBook::operator=(OrderBook&&) noexcept=default;
Result<OrderBook> OrderBook::create(InstrumentRules rules,BookSession session,BookLimits limits,std::pmr::memory_resource* resource) noexcept {
    if (const auto e=validate(rules)) return Result<OrderBook>::failure(e.code,e.field);
    if (!resource || limits.max_orders==0 || limits.max_orders>1000000 || limits.max_levels==0 ||
        limits.max_levels>limits.max_orders || limits.max_snapshot_depth==0 || limits.max_snapshot_depth>limits.max_levels)
        return Result<OrderBook>::failure(ErrorCode::capacity,"book.limits");
    try { return Result<OrderBook>::success(OrderBook(rules,limits,resource,allocate_state(session,resource))); }
    catch (const std::bad_alloc&) { return Result<OrderBook>::failure(ErrorCode::resource_exhausted,"book.create"); }
}
const BookSession& OrderBook::session() const noexcept { return state_->session; }
std::uint64_t OrderBook::revision() const noexcept { return state_->revision; }
std::uint64_t OrderBook::remaining() const noexcept { return state_->remaining; }
std::size_t OrderBook::order_count() const noexcept { return state_->index.size(); }
QuantityLedger OrderBook::ledger() const noexcept { return state_->ledger; }
std::optional<RestingOrder> OrderBook::find(OrderId id) const noexcept {
    const auto found=state_->index.find(id);return found==state_->index.end()?std::nullopt:std::optional<RestingOrder>(*found->second.node);
}
std::optional<DepthLevel> OrderBook::best_bid() const noexcept { return state_->bids.empty()?std::nullopt:std::optional<DepthLevel>(depth_level(*state_->bids.rbegin())); }
std::optional<DepthLevel> OrderBook::best_ask() const noexcept { return state_->asks.empty()?std::nullopt:std::optional<DepthLevel>(depth_level(*state_->asks.begin())); }

Error OrderBook::apply(const MarketEvent& event,std::optional<BookSession> reset_session) noexcept {
    if (const auto e=validate(event,rules_)) return e;
    if (reset_session && !std::holds_alternative<BookReset>(event.payload)) return {ErrorCode::unsupported,"reset_session.without_reset"};
    const auto& scope=*event.metadata.scope.data;
    if (scope.session!=state_->session.session || scope.epoch!=state_->session.epoch) return {ErrorCode::session_boundary,"book.session"};
    if (state_->revision==UINT64_MAX) return {ErrorCode::overflow,"book.revision"};
    auto ledger=state_->ledger;
    auto remaining=state_->remaining;
    try {
        const auto error=std::visit([&](const auto& payload)->Error {
            using T=std::decay_t<decltype(payload)>;
            if constexpr (std::same_as<T,AddOrder>) {
                if (state_->next_priority==UINT64_MAX) return {ErrorCode::overflow,"book.priority"};
                const auto total=types::detail::add(remaining,payload.quantity.value());
                if (!total) return {ErrorCode::overflow,"book.remaining"};
                if (const auto e=credit(ledger,ledger.added,payload.quantity.value())) return e;
                if (const auto e=state_->insert_staged(payload,state_->next_priority,limits_,resource_)) return e;
                remaining=*total.data;++state_->next_priority;
            } else if constexpr (std::same_as<T,CancelOrder> || std::same_as<T,Trade>) {
                std::optional<OrderId> id;
                std::uint64_t amount=0;bool execution=false;
                if constexpr (std::same_as<T,CancelOrder>) id=payload.order_id;
                else {
                    const auto* fill=std::get_if<BookExecution>(&payload.details);
                    if (!fill) return {}; // A print is an observation, never a mutation.
                    id=fill->resting_order_id;amount=fill->quantity.value();execution=true;
                }
                auto found=state_->index.find(*id);
                if (found==state_->index.end()) return {ErrorCode::not_found,"order_id"};
                const auto old=found->second.node->order;
                if constexpr (std::same_as<T,CancelOrder>) {
                    const auto* partial=std::get_if<QuantityLots>(&payload.amount);
                    amount=partial?partial->value():old.quantity.value();
                } else {
                    const auto& fill=std::get<BookExecution>(payload.details);
                    if (fill.resting_side!=old.side || fill.price_ticks!=old.price_ticks) return {ErrorCode::identity_mismatch,"execution.order"};
                }
                if (amount>old.quantity.value()) return {ErrorCode::underflow,"order.remaining"};
                if (const auto e=debit(ledger,execution?ledger.executed:ledger.cancelled,amount)) return e;
                remaining-=amount;
                if (amount==old.quantity.value()) state_->erase(found);
                else {
                    auto& level=state_->prices(old.side).find(old.price_ticks)->second;
                    level.quantity-=amount;found->second.node->order.quantity=lots(old.quantity.value()-amount);
                }
            } else if constexpr (std::same_as<T,ReplaceOrder>) {
                auto old=state_->index.find(payload.old_order_id);
                if (old==state_->index.end()) return {ErrorCode::not_found,"replace.old_id"};
                if (payload.new_order_id!=payload.old_order_id && state_->index.contains(payload.new_order_id)) return {ErrorCode::duplicate,"replace.new_id"};
                const auto previous=old->second.node->order;
                const bool retain=payload.priority==ReplacePriority::retain_only_same_price_reduction;
                if (retain && (previous.side!=payload.side || previous.price_ticks!=payload.price_ticks || payload.quantity>previous.quantity))
                    return {ErrorCode::priority_violation,"replace.priority"};
                if (retain) {
                    const auto reduction=previous.quantity.value()-payload.quantity.value();
                    if (const auto e=debit(ledger,ledger.replacement_out,reduction)) return e;
                    auto& level=state_->prices(previous.side).find(previous.price_ticks)->second;
                    level.quantity-=reduction;remaining-=reduction;
                    old->second.node->order={payload.new_order_id,payload.side,payload.price_ticks,payload.quantity};
                    if (payload.new_order_id!=payload.old_order_id) {
                        auto node=state_->index.extract(old);node.key()=payload.new_order_id;state_->index.insert(std::move(node));
                    }
                } else {
                    if (state_->next_priority==UINT64_MAX) return {ErrorCode::overflow,"book.priority"};
                    remaining-=previous.quantity.value();
                    const auto total=types::detail::add(remaining,payload.quantity.value());
                    if (!total) return {ErrorCode::overflow,"book.remaining"};
                    if (const auto e=debit(ledger,ledger.replacement_out,previous.quantity.value())) return e;
                    if (const auto e=credit(ledger,ledger.replacement_in,payload.quantity.value())) return e;
                    if (const auto e=state_->insert_staged({payload.new_order_id,payload.side,payload.price_ticks,payload.quantity},state_->next_priority,limits_,resource_,payload.old_order_id)) return e;
                    remaining=*total.data;++state_->next_priority;
                }
            } else if constexpr (std::same_as<T,BookReset>) {
                auto next=reset_session.value_or(BookSession{state_->session.session,payload.next_epoch});
                if (next.epoch!=payload.next_epoch) return {ErrorCode::session_boundary,"reset.epoch"};
                if (const auto e=debit(ledger,ledger.discarded,remaining)) return e;
                auto staged=allocate_state(next,resource_);staged->next_priority=state_->next_priority;
                staged->revision=state_->revision;state_.swap(staged);remaining=0;
            } else if constexpr (std::same_as<T,Snapshot>) return {ErrorCode::unsupported,"snapshot.requires_explicit_recovery"};
            // Quotes and session events are journal observations, not order updates.
            return {};
        },event.payload);
        if (error) return error;
        state_->ledger=ledger;state_->remaining=remaining;++state_->revision;last_metadata_=event.metadata;
        assert(!check_invariants());
        return {};
    } catch (const std::bad_alloc&) { return {ErrorCode::resource_exhausted,"book.mutation"}; }
      catch (const std::length_error&) { return {ErrorCode::capacity,"book.mutation"}; }
}
Error OrderBook::recover(const MarketEvent& event,BookSession next) noexcept {
    if (const auto e=validate(event,rules_)) return e;
    const auto* snapshot=std::get_if<Snapshot>(&event.payload);
    if (!snapshot || snapshot->kind!=SnapshotKind::order_level || snapshot->coverage!=SnapshotCoverage::complete)
        return {ErrorCode::unsupported,"recovery.requires_complete_order_snapshot"};
    if (event.metadata.scope.data->session!=next.session || event.metadata.scope.data->epoch!=next.epoch)
        return {ErrorCode::session_boundary,"recovery.session"};
    if (state_->revision==UINT64_MAX) return {ErrorCode::overflow,"book.revision"};
    for (std::size_t i=0;i<snapshot->boundaries.count;++i)
        if (snapshot->boundaries.items[i]->scope.session!=next.session || snapshot->boundaries.items[i]->scope.epoch!=next.epoch)
            return {ErrorCode::session_boundary,"recovery.boundary",i};
    try {
        auto staged=allocate_state(next,resource_);
        std::array<std::size_t,64> sorted{};
        for (std::size_t i=0;i<snapshot->orders.count;++i) sorted[i]=i;
        std::sort(sorted.begin(),sorted.begin()+static_cast<std::ptrdiff_t>(snapshot->orders.count),[&](auto a,auto b) {
            const auto& x=*snapshot->orders.items[a];const auto& y=*snapshot->orders.items[b];
            if (x.order.side!=y.order.side) return x.order.side<y.order.side;
            if (x.order.price_ticks!=y.order.price_ticks) return x.order.price_ticks<y.order.price_ticks;
            return x.priority_index<y.priority_index;
        });
        for (std::size_t k=0;k<snapshot->orders.count;++k) {
            const auto& item=*snapshot->orders.items[sorted[k]];
            if (item.priority_index==UINT64_MAX) return {ErrorCode::overflow,"recovery.priority"};
            if (const auto e=staged->insert_staged(item.order,item.priority_index,limits_,resource_)) return e;
            if (const auto e=increase(staged->remaining,item.order.quantity.value())) return e;
            staged->next_priority=std::max(staged->next_priority,item.priority_index+1);
        }
        auto ledger=state_->ledger;
        if (const auto e=debit(ledger,ledger.discarded,state_->remaining)) return e;
        if (const auto e=credit(ledger,ledger.recovered,staged->remaining)) return e;
        staged->ledger=ledger;staged->revision=state_->revision+1;
        state_.swap(staged);last_metadata_=event.metadata;assert(!check_invariants());return {};
    } catch (const std::bad_alloc&) { return {ErrorCode::resource_exhausted,"book.recovery"}; }
      catch (const std::length_error&) { return {ErrorCode::capacity,"book.recovery"}; }
}
Error OrderBook::check_invariants() const noexcept {
    std::uint64_t count=0,total=0;
    for (const auto side:{Side::buy,Side::sell}) for (const auto& [price,level]:state_->prices(side)) {
        if (level.count==0 || level.fifo.empty()) return {ErrorCode::inconsistent_state,"empty_level"};
        std::uint64_t quantity=0,orders=0;std::optional<std::uint64_t> priority;
        for (auto i=level.fifo.begin();i!=level.fifo.end();++i) {
            const auto& node=*i;
            if (node.order.side!=side || node.order.price_ticks!=price || node.order.quantity.value()==0 ||
                (priority && node.priority<=*priority) || node.priority>=state_->next_priority)
                return {ErrorCode::inconsistent_state,"fifo"};
            priority=node.priority;
            auto found=state_->index.find(node.order.order_id);
            if (found==state_->index.end() || found->second.side!=side || found->second.price!=price || found->second.node!=i)
                return {ErrorCode::inconsistent_state,"index"};
            if (const auto e=increase(quantity,node.order.quantity.value())) return e;
            ++orders;
        }
        if (quantity!=level.quantity || orders!=level.count) return {ErrorCode::inconsistent_state,"level_totals"};
        if (const auto e=increase(total,quantity)) return e;
        if (const auto e=increase(count,orders)) return e;
    }
    if (count!=state_->index.size() || count>limits_.max_orders || total!=state_->remaining ||
        state_->bids.size()+state_->asks.size()>limits_.max_levels) return {ErrorCode::inconsistent_state,"book_totals"};
    const auto& l=state_->ledger;
    std::uint64_t credits=0,debits=0;
    for (const auto value:{l.added,l.recovered,l.replacement_in}) if (const auto e=increase(credits,value)) return e;
    for (const auto value:{l.cancelled,l.executed,l.discarded,l.replacement_out}) if (const auto e=increase(debits,value)) return e;
    if (credits!=l.total_in || debits!=l.total_out) return {ErrorCode::inconsistent_state,"ledger_categories"};
    if (l.total_in<l.total_out || l.total_in-l.total_out!=total) return {ErrorCode::inconsistent_state,"quantity_conservation"};
    const auto bid=best_bid(),ask=best_ask();
    if (bid && ask && bid->price_ticks>ask->price_ticks) return {ErrorCode::crossed_quote,"book"};
    return {};
}
Result<DepthSnapshot> OrderBook::depth(std::size_t requested) const noexcept {
    if (requested==0 || requested>limits_.max_snapshot_depth) return Result<DepthSnapshot>::failure(ErrorCode::capacity,"snapshot.depth");
    try {
        DepthSnapshot out(rules_,state_->session,state_->revision,requested,resource_);
        out.bids.reserve(std::min(requested,state_->bids.size()));out.asks.reserve(std::min(requested,state_->asks.size()));
        for (auto i=state_->bids.rbegin();i!=state_->bids.rend() && out.bids.size()<requested;++i) out.bids.push_back(depth_level(*i));
        for (const auto& level:state_->asks) { if (out.asks.size()==requested) break;out.asks.push_back(depth_level(level)); }
        out.bid_truncated=out.bids.size()<state_->bids.size();out.ask_truncated=out.asks.size()<state_->asks.size();
        return Result<DepthSnapshot>::success(std::move(out));
    } catch (const std::bad_alloc&) { return Result<DepthSnapshot>::failure(ErrorCode::resource_exhausted,"snapshot"); }
}
Result<std::pmr::string> OrderBook::canonical() const noexcept {
    try {
        std::pmr::string out(resource_);
        const auto text=[&](std::string_view s) { out.append(s); };
        const auto number=[&](auto n) { char b[32];const auto r=std::to_chars(b,b+32,n);out.append(b,r.ptr);out.push_back(';'); };
        const auto token=[&](const Identity& t) { number(t.view().size());text(t.view());text(";"); };
        text("gig.book.v1;");number(rules_.instrument.value());number(rules_.venue.value());
        number(rules_.minimum_price.value());number(rules_.maximum_price.value());number(rules_.maximum_quantity.value());
        number(rules_.tick_size.numerator);number(rules_.tick_size.denominator);number(rules_.lot_size.numerator);number(rules_.lot_size.denominator);
        token(state_->session.session);number(state_->session.epoch);number(state_->revision);number(state_->next_priority);number(state_->remaining);
        number(limits_.max_orders);number(limits_.max_levels);number(limits_.max_snapshot_depth);
        const auto l=state_->ledger;
        for (const auto n:{l.added,l.cancelled,l.executed,l.discarded,l.recovered,l.replacement_in,l.replacement_out,l.total_in,l.total_out}) number(n);
        for (const auto side:{Side::buy,Side::sell}) {
            number(static_cast<unsigned>(side));number(state_->prices(side).size());
            const auto emit=[&](const auto& level) {
                number(level.first.value());number(level.second.quantity);number(level.second.count);
                for (const auto& node:level.second.fifo) { number(node.order.order_id.value());number(node.order.quantity.value());number(node.priority); }
            };
            if (side==Side::buy) for (auto i=state_->bids.rbegin();i!=state_->bids.rend();++i) emit(*i);
            else for (const auto& level:state_->asks) emit(level);
        }
        return Result<std::pmr::string>::success(std::move(out));
    } catch (const std::bad_alloc&) { return Result<std::pmr::string>::failure(ErrorCode::resource_exhausted,"book.canonical"); }
}
} // namespace gig
