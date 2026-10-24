#pragma once
// Development-only independent flat-vector oracle. No production mutation helpers.
#include <algorithm>
#include <cstdint>
#include <vector>
#include "gig/book/order_book.hpp"
namespace gig::test {
struct RefOrder { std::uint64_t id; Side side; std::int64_t price; std::uint64_t quantity,priority; };
class ReferenceBook {
public:
    std::vector<RefOrder> orders;
    QuantityLedger ledger{};
    std::uint64_t next_priority{};
    bool apply(const EventPayload& payload) {
        auto candidate=*this;
        const bool ok=std::visit([&](const auto& p)->bool {
            using T=std::decay_t<decltype(p)>;
            const auto find=[&](std::uint64_t id) { return std::find_if(candidate.orders.begin(),candidate.orders.end(),[&](auto& x){return x.id==id;}); };
            if constexpr (std::same_as<T,AddOrder>) {
                if (find(p.order_id.value())!=candidate.orders.end() || p.quantity.value()==0) return false;
                candidate.orders.push_back({p.order_id.value(),p.side,p.price_ticks.value(),p.quantity.value(),candidate.next_priority++});
                candidate.ledger.added+=p.quantity.value();candidate.ledger.total_in+=p.quantity.value();
            } else if constexpr (std::same_as<T,CancelOrder> || std::same_as<T,Trade>) {
                std::uint64_t id{},amount{};bool execution=false;
                if constexpr (std::same_as<T,CancelOrder>) id=p.order_id.value();
                else {
                    const auto* fill=std::get_if<BookExecution>(&p.details);if (!fill) return true;
                    id=fill->resting_order_id.value();amount=fill->quantity.value();execution=true;
                }
                auto old=find(id);if (old==candidate.orders.end()) return false;
                if constexpr (std::same_as<T,CancelOrder>) {
                    const auto* q=std::get_if<QuantityLots>(&p.amount);amount=q?q->value():old->quantity;
                } else {
                    const auto& fill=std::get<BookExecution>(p.details);
                    if (fill.resting_side!=old->side || fill.price_ticks.value()!=old->price) return false;
                }
                if (amount==0 || amount>old->quantity) return false;
                if (execution) candidate.ledger.executed+=amount;else candidate.ledger.cancelled+=amount;
                candidate.ledger.total_out+=amount;
                old->quantity-=amount;if (old->quantity==0) candidate.orders.erase(old);
            } else if constexpr (std::same_as<T,ReplaceOrder>) {
                auto old=find(p.old_order_id.value());if (old==candidate.orders.end()) return false;
                if (p.new_order_id!=p.old_order_id && find(p.new_order_id.value())!=candidate.orders.end()) return false;
                if (p.priority==ReplacePriority::retain_only_same_price_reduction) {
                    if (old->side!=p.side || old->price!=p.price_ticks.value() || p.quantity.value()>old->quantity) return false;
                    candidate.ledger.replacement_out+=old->quantity-p.quantity.value();candidate.ledger.total_out+=old->quantity-p.quantity.value();
                } else {
                    candidate.ledger.replacement_out+=old->quantity;candidate.ledger.total_out+=old->quantity;
                    candidate.ledger.replacement_in+=p.quantity.value();candidate.ledger.total_in+=p.quantity.value();
                    old->priority=candidate.next_priority++;
                }
                old->id=p.new_order_id.value();old->side=p.side;old->price=p.price_ticks.value();old->quantity=p.quantity.value();
            } else return false;
            return true;
        },payload);
        if (ok) *this=std::move(candidate);
        return ok;
    }
    std::uint64_t remaining() const { std::uint64_t sum=0;for (const auto& x:orders) sum+=x.quantity;return sum; }
    std::vector<RefOrder> sorted() const {
        auto result=orders;
        std::sort(result.begin(),result.end(),[](const auto& a,const auto& b) {
            if (a.side!=b.side) return a.side<b.side;
            if (a.price!=b.price) return a.side==Side::buy?a.price>b.price:a.price<b.price;
            return a.priority<b.priority;
        });return result;
    }
};
} // namespace gig::test
