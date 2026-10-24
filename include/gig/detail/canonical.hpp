#pragma once
#include <charconv>
#include <memory_resource>
#include <string>
#include "gig/events/contracts.hpp"
namespace gig::detail {
// Internal canonical grammar: semicolon-delimited numbers; tokens are length;bytes;.
// No locale, pointer values, object padding, floats, hash iteration or implicit defaults.
class CanonicalWriter {
    std::pmr::string& out_;
public:
    explicit CanonicalWriter(std::pmr::string& out):out_(out) {}
    void raw(std::string_view s) { out_.append(s); }
    template<std::integral T> void number(T value) {
        char buffer[32];const auto result=std::to_chars(buffer,buffer+32,value);out_.append(buffer,result.ptr);out_.push_back(';');
    }
    template<class E> requires std::is_enum_v<E> void enumeration(E e) { number(static_cast<std::underlying_type_t<E>>(e)); }
    void token(std::string_view value) { number(value.size());raw(value);raw(";"); }
    template<std::size_t N> void token(const Token<N>& value) { token(value.view()); }
    template<class T,class F> void available(const Available<T>& value,F emit) {
        enumeration(value.reason);number(static_cast<unsigned>(value.data.has_value()));if (value.data) emit(*value.data);
    }
    template<class T,std::size_t N,class F> void list(const BoundedList<T,N>& values,F emit) {
        number(values.count);for (std::size_t i=0;i<values.count;++i) emit(*values.items[i]);
    }
};
void canonical_scope(CanonicalWriter&,const StreamScope&);
void canonical_rules(CanonicalWriter&,const InstrumentRules&);
void canonical_event(CanonicalWriter&,const MarketEvent&);
} // namespace gig::detail
