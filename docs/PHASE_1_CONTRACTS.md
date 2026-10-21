# Phase 1 contracts

## Numeric checkpoint

IMPLEMENTED: eleven distinct types in gig::types. No raw/default constructor,
implicit conversion, floating construction or unchecked arithmetic operators.
Checked factories reject nonrepresentable values before conversion. Identifiers
are nonzero uint64; sequence numbers include zero because their origin is scoped.
Price/event/receive timestamps cover int64. Quantity includes zero for arithmetic,
but order quantities must be positive at event validation. Simulation time and
duration are nonnegative int64 nanoseconds. Zero is not a missing-value sentinel.

Only prices, quantities and durations expose same-unit checked arithmetic.
Timestamp advance requires Duration; elapsed rejects negative or nonrepresentable
results. Sequence increment rejects wrap. Explicit checked_cast verifies range.
Identifier arithmetic is intentionally absent. Error paths return structured
Result/Error without allocation; callers inspect success before dereferencing data.

UnitScale is a positive rational physical-unit size. Exact decimal grammar is
[-]digits[.digits], ASCII only, <=64 characters and <=18 fractional digits;
no whitespace, exponent, plus, nonfinite values or rounding. Mantissa fits uint64.
Cross-cancellation before checked multiplication avoids unnecessary intermediate
overflow. Off-unit amounts fail. Signed minimum is handled without negating it.
Negative lot amounts, including -0, are rejected. Reverse conversion returns a
reduced signed-magnitude rational, not floating point, and rejects unrepresentable
uint64 numerator. No external big-integer runtime dependency.

Validation: compile-time pairwise separation checks; runtime boundaries; Python
arbitrary-precision integers and Fraction as independent arithmetic/divisibility
references (fixed seed 1729). Numeric operations are constant work except bounded
decimal parsing and gcd. No book mutation or integration ABI is provided.

The original scaffold remains temporarily unchanged until the event checkpoint;
new public event contracts will use these types directly, removing old aliases.

Numeric checkpoint evidence: Debug/Release/ASan+UBSan each passed 18 CTest
outcomes, including 8507 independent integer/Fraction reference cases, 27 runtime
numeric contract checks, the existing scaffold tests and benchmark checks.
No sanitizer findings were reported. This checkpoint adds numeric contracts only.
