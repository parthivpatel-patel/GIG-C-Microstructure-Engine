#pragma once
#include <algorithm>
#include <cstdint>
#include <string>
#include "gig/core/result.hpp"
#if !defined(__SIZEOF_INT128__)
#error "Exact research arithmetic requires compiler signed/unsigned 128-bit integer support"
#endif
namespace gig::exact {
__extension__ using Wide = __int128;
__extension__ using Unsigned = unsigned __int128;
struct ArithmeticFailure { ErrorCode code; };
inline constexpr Wide maximum=static_cast<Wide>((Unsigned{1}<<127U)-1);
inline Wide checked_add(Wide a,Wide b) {
    Wide r{};if (__builtin_add_overflow(a,b,&r) || r == -maximum-1) throw ArithmeticFailure{ErrorCode::overflow};return r;
}
inline Wide checked_mul(Wide a,Wide b) {
    // Check magnitudes before multiplication. Clang's signed 128-bit overflow
    // builtin can require __muloti4, absent from AArch64's default libgcc.
    // Unsigned negation also handles the signed minimum without undefined behavior.
    if (a==0 || b==0) return 0;
    const auto ua=a<0?Unsigned{0}-static_cast<Unsigned>(a):static_cast<Unsigned>(a);
    const auto ub=b<0?Unsigned{0}-static_cast<Unsigned>(b):static_cast<Unsigned>(b);
    if (ua>static_cast<Unsigned>(maximum)/ub) throw ArithmeticFailure{ErrorCode::overflow};
    const auto product=static_cast<Wide>(ua*ub); // proved within symmetric range
    return (a<0)!=(b<0)?-product:product;
}
inline Wide magnitude(Wide n) {if (n == -maximum-1) throw ArithmeticFailure{ErrorCode::overflow};return n<0?-n:n;}
inline Wide gcd(Wide a,Wide b) {a=magnitude(a);b=magnitude(b);while (b) {auto t=a%b;a=b;b=t;}return a;}
inline std::string decimal(Wide n) {
    const bool negative=n<0;auto u=static_cast<Unsigned>(negative?-(n+1):n)+(negative?1U:0U);
    std::string s;do {s.push_back(static_cast<char>('0'+u%10));u/=10;} while (u);
    if (negative) {s.push_back('-');}
    std::reverse(s.begin(),s.end());return s;
}
// Reduced, positive denominator; symmetric signed-127-magnitude capacity.
class Fraction {
    Wide n_{},d_{1};
    Fraction(Wide n,Wide d):n_(n),d_(d) {}
public:
    Fraction()=default;
    explicit Fraction(std::int64_t n):n_(n) {}
    static Fraction ratio(Wide n,Wide d) {
        if (d<=0) throw ArithmeticFailure{ErrorCode::invalid_range};
        const auto g=gcd(n,d);return Fraction(n/g,d/g);
    }
    static Fraction whole(Wide n) {return ratio(n,1);}
    Wide numerator() const noexcept {return n_;}
    Wide denominator() const noexcept {return d_;}
    std::string str() const {return decimal(n_)+"/"+decimal(d_);}
    bool operator==(const Fraction&) const = default;
    friend Fraction operator-(Fraction a) {return Fraction(-a.n_,a.d_);}
    friend Fraction operator+(Fraction a,Fraction b) {
        auto g=gcd(a.d_,b.d_);return ratio(checked_add(checked_mul(a.n_,b.d_/g),checked_mul(b.n_,a.d_/g)),checked_mul(a.d_,b.d_/g));
    }
    friend Fraction operator-(Fraction a,Fraction b) {return a+(-b);}
    friend Fraction operator*(Fraction a,Fraction b) {
        auto g=gcd(a.n_,b.d_),h=gcd(b.n_,a.d_);return ratio(checked_mul(a.n_/g,b.n_/h),checked_mul(a.d_/h,b.d_/g));
    }
    friend Fraction operator/(Fraction a,Fraction b) {
        if (b.n_==0) throw ArithmeticFailure{ErrorCode::invalid_range};
        return a*ratio(b.n_<0?-b.d_:b.d_,magnitude(b.n_));
    }
};
} // namespace gig::exact
