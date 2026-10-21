# Phase 3 book-state analytics

IMPLEMENTED, MUST HAVE: pure single-owner snapshot calculations, exact values,
explicit missingness and a source reference. No flow metrics in this phase.

For best bid B, ask A, respective displayed quantities b,a and requested D levels:
spread=A-B (ticks); midpoint=(A+B)/2 (ticks, half ticks retained);
microprice=(A*b+B*a)/(b+a) (ticks); top imbalance=(b-a)/(b+a) (dimensionless).
Aggregated bid/ask depth sums existing first D levels (lots). Depth imbalance uses
(sum_bid-sum_ask)/(sum_bid+sum_ask) and is unavailable unless BOTH sides supply D
levels. Asking beyond snapshot requested_depth rejects. Fewer real levels do not
invent zero levels for the strict imbalance; aggregate quantities still describe
available displayed liquidity. No time-weighting or hidden-depth interpretation.

Empty/one-sided books explicitly lack two-sided metrics. Empty aggregate depth is
exact zero. Locked books have zero spread and valid midpoint/microprice. Crossed,
zero-quantity, duplicate/unsorted-price, zero-count, oversized, out-of-rule and
inconsistent-truncation snapshots reject. No partial analytics object on malformed
input. Book-produced snapshots cannot have combined quantity beyond uint64; manually
constructed snapshots are checked too. Thus even signed-64 extreme prices and
uint64 total quantity have exact signed-128 weighted numerators.

Numerics use reduced exact fractions with positive denominators. GCC/Clang 128-bit
integer support is required and checked at compile time (no binary floating prices,
Boost dependency or silent narrowing). General rational intermediate arithmetic has
a symmetric +/-((2^127)-1) bound, uses checked builtins and cross cancellation; it
may reject a calculation whose final mathematical value would fit but whose checked
intermediate would not. Such failure returns structured arithmetic-capacity error.
Zero denominators reject, never infinity/NaN. These are engineering capacity bounds,
not restrictions on the financial definition. Canonical decimal fraction strings
preserve exactness and need no host-memory serialization.

BookMetrics exposes const getters only, owns values and copies rules/session plus
run ID/journal prefix/revision. Retain/resolve that reference against the canonical
accepted journal and immutable run manifest for complete input hashes, versions,
ordering, synthetic/observed origin and code/build lineage. A supplied identity is
not authentication; manually created snapshots carry caller-provided references.
Metrics never mutate the input book/snapshot. Invalid enum metric lookup throws
out_of_range at the explicit accessor (integration adapters must validate selectors).
Public calculate returns structured errors; exact helper arithmetic throws only its
explicit internal ArithmeticFailure, translated at operational boundaries.

Time O(number of supplied levels + D), space O(1), no dynamic allocation during
calculation; output is a small owned value. Exact decimal export may allocate.
Alternative floating results simplify plotting but would lose half-tick and extreme
integer precision; a future approximate view must be labeled separately. Interview
rationale: immutable inputs and exact fractions isolate financial definitions from
feed mutation and make Python Fraction a truly independent numeric oracle.

Validation: hand-worked 100/101 with 30/10 lots gives midpoint 201/2, microprice
403/4 and imbalance 1/2; Python integer/Fraction checks randomized/extreme/empty/
one-sided/locked/crossed inputs. Unit checks cover insufficient depth, malformed
snapshots, conservation capacity, source preservation and unchanged book canonical
bytes. The release-only research benchmark validates a fixed fixture first, retains
all repeated bulk and serial service samples, code SHA/build/CPU context and declared
clock/loop scopes. Its no-PMR-allocation claim covers pure calculation, not formatting,
fixture construction, driver vectors or process RSS. Shared-cloud timing is noisy.
