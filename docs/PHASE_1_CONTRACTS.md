# Phase 1 contracts

## Numeric checkpoint

IMPLEMENTED: eleven distinct types in gig::types. No raw/default constructor,
implicit conversion, floating construction or unchecked arithmetic operators.
Checked factories reject nonrepresentable values before conversion. Identifiers
are nonzero uint64; sequence numbers include zero because their origin is scoped.
Price/event/receive timestamps cover int64. Quantity includes zero for arithmetic,
but order quantities must be positive at event validation. Simulation time and
duration are nonnegative int64 nanoseconds. Zero is not a missing-value sentinel.

Only prices, quantities and durations expose same-unit checked arithmetic. Exact
division rejects zero divisors, signed-min/-1 overflow and nonzero remainders
instead of truncating.
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

The event checkpoint replaces the original raw aliases and migrates the demo,
tests and benchmark. Public contracts import the eleven gig::types into gig.

Numeric checkpoint evidence: Debug/Release/ASan+UBSan each passed 18 CTest
outcomes, including 8507 independent integer/Fraction reference cases, 27 runtime
numeric contract checks, the existing scaffold tests and benchmark checks.
No sanitizer findings were reported. This checkpoint adds numeric contracts only.

## Event checkpoint: implemented contracts

All eight payload families are IMPLEMENTED: AddOrder, CancelOrder, ReplaceOrder,
Trade (print vs identified execution), Quote, BookReset, Snapshot, SessionEvent.
UnsupportedEvent explicitly retains an unknown wire-type number and is rejected.
No parsing, serialization, book mutation, matching, execution or analytics exists.
No ABI/wire-schema compatibility is promised for the replaced pre-release scaffold.

| Contract | Required content and validation |
|---|---|
| AddOrder | Nonzero typed ID, valid side, in-range ticks, positive bounded lots |
| CancelOrder | Nonzero typed ID; tagged cancel-all or positive bounded lots |
| ReplaceOrder | Old/new typed IDs, side, price/quantity, explicit priority policy; same ID allowed |
| TradePrint | Price/quantity and explicitly known/missing aggressor; never a book decrement |
| BookExecution | Resting ID and side, price/quantity; no inference from print |
| Quote | Optional bid/ask; omitted side means absent; positive sizes; crossed rejected, locked allowed |
| BookReset | Supported reason and strictly greater next epoch when current epoch is known |
| Snapshot | Kind/coverage/depth, bounded owned entries and per-stream included boundaries |
| SessionEvent | Supported action plus reason explicitly known or missing |

Replace priority eligibility, cancel/fill availability, active-ID uniqueness,
sequence continuity and session transition legality need state and remain Phase 2.
Quantity is remaining quantity for add and desired new remaining quantity for
replace; partial cancel is a delta, not new remaining quantity. No silent coercion.

### Required versus missing metadata

Every event carries instrument, venue, StreamScope(stream/session/epoch and
message-vs-event sequencing), sequence, subevent index/count, event/receive clocks
and precision, source record, optional capture ordinal and Provenance.
Available<T> stores either an actual value with reason none, or absence with
not_reported/unavailable/not_applicable. Contradictions and unknown enums fail.
No identifier, timestamp or seed is invented as a missing-value sentinel.

Complete mode requires instrument/venue/scope/sequence/source-record, dataset
identity/version/license reference, origin/source and nonempty lineage. Synthetic
origin requires generator source, generated lineage and a seed (zero is valid).
Observed origin requires observed lineage and prohibits relabeling generated data.
Derived transformations require parent artifact references. Missing timestamps,
checksums and capture ordinal remain explicitly representable even in complete
mode: complete means required contract fields, not authenticated or exhaustive data.
Known timestamps may separately retain unknown clock/precision, and known datasets
may retain unknown version/license, for inspection without inventing placeholders.
These partial composites fail complete validation. StreamScope is an atomic known
tuple; if its session/epoch/unit is unavailable, the scope itself is missing.
Inspect-incomplete mode checks structure and any present values but permits unknown
required metadata. It cannot create ValidatedEvent. Unsupported clock domains,
versions and payloads remain errors in both modes.

Event/receive values are signed int64 nanoseconds with explicit clock identity.
Event time permits UTC or an explicitly unsynchronized venue UTC clock; receive
time permits UTC. Relative/simulation clocks are unsupported here, not silently
coerced. Precision must align with the stored value; no cross-clock event<=receive
assumption. Source timestamps are not reordered or repaired. SimulationTime is a
separate strong type and is not an observed event timestamp.

Sequence zero is allowed; first expected sequence is a later replay-policy input.
Message subevents preserve index/count; event sequencing requires index 0/count 1.
No multi-stream merger is implemented. ADR 0001 remains the ordering contract.

### Owned provenance and bounded snapshots

Tokens own <=128 printable non-whitespace ASCII bytes. Invalid/oversized tokens
fail; adapters must not truncate or silently transliterate. SHA-256 tokens, when
present, require 64 lowercase hex characters. Syntax is not authenticity proof.
Dataset metadata, generator seed, operation/version lineage and parent references
survive exact semantic equality and validated copying; no borrowed strings/spans.
Lineage and parent capacities are 8 each. Duplicate parent IDs fail. Full external
artifact existence, hash verification and provenance-graph cycles require a future
manifest registry and are NOT verified by this local contract.

Snapshots hold up to 64 orders OR 64 aggregate levels, plus up to 8 sequence
boundaries. Counts, holes, hidden suffix entries and mutually inconsistent content
fail. Order IDs and same-level priority indexes must be unique; aggregate
side/price pairs and boundary streams must be unique. Checked level sums reject
uint64 overflow. Bounded depth must be positive and cover no more than that many
distinct levels per side; complete coverage uses depth 0. Empty books are valid.
Crossed snapshots fail; locked snapshots are permitted as observations. Boundary
subevents are in range; a boundary on the snapshot's own stream cannot be ahead
of its envelope. Other-stream boundaries are explicit, not compared as if their
sequences shared a clock. Aggregate/bounded snapshots do not claim full FIFO
recovery capability. Priority indexes establish order within each price level;
the input array need not already be sorted. Capacity errors never truncate data.

### Failure safety, ownership and complexity

Validators are const/noexcept, allocation-free and return a deterministic first
Error(code, static field path, optional entry index). Scalar factories and numeric
operations are constexpr/noexcept. Result.data must be checked before dereference;
no throwing optional::value is used internally. No C/Python boundary exists yet.
make_validated validates complete metadata then returns an owned immutable event
AND the exact InstrumentRules used for validation. Editing a draft cannot alter
that copy. Copy construction is statically verified nothrow. Rejection preserves
all input fields; there is no mutable book/journal/cursor in this phase.

Fixed capacities make memory bounded and error handling allocation-free, at the
cost of larger copies and explicit limits. Snapshot duplicate/sum checks use
O(N^2) work with N<=64; parent checks O(P^2), P<=8. Simple scalar/event checks are
constant work; tokens/lineage are bounded scans. Dynamic pools, hash indexes and
allocation optimizations await measured need. An interview explanation should
emphasize exact units and auditable failure semantics before cache tuning.

### Benchmark compatibility

Workload version 2 measures ONLY AddOrder payload validation against fixed
InstrumentRules, excluding metadata/provenance. Categories: valid buy/sell,
invalid side, zero/negative price, zero quantity, price above instrument maximum,
and valid maximum quantity at maximum instrument price. Fingerprint fields and
semantics changed; the immutable Phase 0B version-1 baseline remains historical
and is NOT comparable as a speedup/regression. No optimization has been made.

## Final local validation

Debug/Release/ASan+UBSan each passed 29 CTest outcomes with zero failures/errors/
skips in the actual JUnit reports. Numeric: 10624 independent integer/Fraction
reference cases and 27 direct runtime contracts; events: 755 assertions across
11 groups, including fixture and input-preservation checks. Compile-time pairwise
separation checks cover all eleven types. No sanitizer findings were reported.
A fresh external CMake Release consumer linked with tests disabled and exercised
invalid-side rejection. The event variant occupies 12208 bytes on this GCC/x86_64
build; bounded ownership trades larger copies for predictable failure behavior.

The clean version-2 payload baseline is preserved in
baselines/phase1-add-order-payload.json. It excludes metadata/provenance validation
and cannot be compared with the historical Phase 0B version-1 numbers. No engine
optimization or Phase 2 implementation occurred.
