# Phase 2 book semantics and atomicity

Status: book IMPLEMENTED; replay/benchmark checkpoints follow. No matching engine,
analytics, execution simulation, broker or terminal changes. MUST HAVE baseline:
standard ordered maps, FIFO lists, hash index, checked quantities and safe staging.
SHOULD HAVE: profiling evidence. LATER / EXPERIMENTAL: alternative allocators/indexes.

## Ownership and scope

One owner mutates each instrument/venue book. OrderBook is move-only; its allocated
State stays at a stable address, so moving the owner cannot invalidate index list
iterators. Order identity is (instrument, venue, session identity, epoch, order ID).
Stream IDs scope feed sequences, NOT order identity. Events on several channels in
the same declared venue session can reference the same order. Adapters must certify
that namespace mapping; feeds whose IDs are channel-local need an explicit future
adapter policy, not silent remapping. Wrong sessions/epochs or instrument/venue
identities are rejected. Reset removes old IDs before reuse in a new scope.

The std::pmr resource is caller-owned and must outlive the book, its snapshots and
canonical strings. It must throw bad_alloc on allocation failure and never throw
from deallocation. TrackedResource supplies deterministic failure injection,
allocation/live/peak-byte counts and an optional live-byte budget. No threads or
global allocation hooks. All production book container/state/output allocations
use the selected PMR resource; ordinary fixture/test allocations are separate.

## Mutation semantics

- Add: append at the price-level FIFO tail; duplicate active ID rejected.
- Partial cancellation: subtract a positive delta, retaining priority.
- Cancel-all/full execution: remove the node/index and any now-empty level.
- Identified execution: stored side/price must match and amount <= remaining.
  It can identify a non-head order: reconstruction records that observation rather
  than inferring an aggressor/matching rule. Surviving FIFO positions do not change.
- Replacement with retain_only_same_price_reduction: same side/price and nonincreasing
  positive remaining quantity required. A unique new ID may replace the old ID
  without moving the queue node. Invalid retain requests fail, not silently upgrade.
- Replacement with lose: remove old quantity, append a fresh-priority node, even
  for a same-price increase. Price/side changes use this policy. New-ID collisions
  fail. Replacement quantity means desired NEW remaining quantity.
- Reset: clear orders explicitly, debit discarded quantity, change epoch (and an
  explicitly supplied session identity), retain lifetime ledger and revision.
- Recovery: explicit API only; complete order-level snapshots only, never aggregate
  or bounded-depth input. Replace rather than merge. Sort provided FIFO ranks within
  side/price; reject capacity, duplicate IDs/ranks, overflow and invalid boundaries.
- Quote, print-only Trade and SessionEvent: observations only; no depth mutation.
  They update accepted revision/latest metadata but do not invent order state.

No incoming add triggers matching. Each accepted canonical event is a consistent
book boundary: bid > ask is rejected without mutation. Locked books are permitted
as observations. Transient crossed states requiring later feed messages are NOT
supported; such data needs a separately approved atomic-bundle policy. This is not
an exchange-certified matching engine and does not model auctions/hidden priority.

## Strong failure guarantee

Validate immutable event/rules/scope first. Compute quantity/category/priority/
revision/capacity/crossing effects in local checked values. Add and priority-losing
replace allocate a temporary map node (if needed), list node and index node using
the SAME allocator as their live destinations. Live index rehash is the final
potential allocation. Then only equal-allocator node transfers, list splice,
nonthrowing key comparisons/hash, erasure and scalar/metadata assignment remain.
No callbacks or external publication occurs during commit. Retained replacements,
cancels and executions require no allocation. Reset and recovery build replacement
state independently and commit with a nonthrowing owner swap.

Bad input, bad_alloc, resource capacity or integer overflow leaves orders, FIFO,
index, quantities, priority clock, revision, ledger and latest metadata unchanged.
Hash-bucket capacity is an implementation detail, excluded from canonical state.
Canonical/depth output allocation failures also leave input state unchanged.
Failure injection sweeps every reached PMR allocation position, including live
rehash, recovery, reset and query allocations; it is not an arbitrary simulated
failure flag bypassing real container allocation.

Debug builds assert all invariants after successful commits. Release tests and
benchmark correctness preflight explicitly call the invariant scanner too; no
correctness evidence relies on Debug-only assertions. The scanner checks every
node/index/level, strictly increasing local FIFO ranks, positive quantities,
empty-level removal, counts, limits, crossed prices and ledger reconciliation.

## Quantity, counts and resource bounds

Checked level and global remaining quantities use uint64. Counts are bounded by
configured limits and checked on insertion. Lifetime counters distinguish added,
recovered, replacement-in, cancelled, executed, discarded and replacement-out:

    total_in = added + recovered + replacement_in
    total_out = cancelled + executed + discarded + replacement_out
    remaining = total_in - total_out

Every component and total must fit uint64; even a net-flat operation is rejected
if lifetime counters would overflow. Resets/recovery explicitly debit discarded
old state rather than erasing its conservation history. Revision/priority clocks
never wrap; UINT64_MAX is not assigned as a new FIFO rank. Recovered ranks remain
explicit and determine the next available rank.

Defaults: 100000 orders, 10000 levels and max depth 10000. Hard order limit 1000000;
levels <= order limit and max depth <= level limit. Zero/invalid limits fail.
Recovery retains Phase 1's maximum 64 snapshot orders and 8 boundaries; no truncation.
Depth queries independently return configured requested depth, owned level vectors,
truncation flags, exact rules/session/revision and explicit empty/one-sided states.
A low-level depth result is NOT a complete research artifact: full lineage requires
the replay run/journal prefix introduced in the next checkpoint. latest_metadata()
only identifies the latest input; it is not a substitute for complete history.

## Complexity and interview rationale

For N orders, L levels and D requested depth: add/priority-changing replace has
O(log L) level work and expected O(1) hash lookup, with amortized O(N) index rehash
and O(N) adversarial hash worst cases. Cancel/identified fill is expected O(1), plus
O(log L) lookup/removal of its level. Best prices O(1), owned depth O(min(D,L)).
Invariant scan O(N+L) expected; recovery bounded sorting O(K log K) plus inserts.
Canonical book output O(N+L). Debug invariant assertions add a scan per mutation;
Release timing must identify that distinction. Memory O(N+L) plus bucket and node
overhead, temporary staged nodes and output vectors. No full-book copy per mutation.

Interview rationale: standard node handles and same-allocator splice retain stable
ownership while making the throwing/nonthrowing boundary explicit. Independent
flat-vector comparisons and actual allocator failures challenge both semantics
and rollback; later optimization must beat a measured, correctness-gated baseline.

## Checkpoint validation

Debug, Release and ASan+UBSan each passed 36 CTest outcomes, zero failures/errors/
skips and no reported sanitizer findings. Book groups include 20000 independent
flat-vector reference operations (seeds 1/42/1729/999), 1298396 associated assertions,
and 34 reached allocation-failure positions across staged insertion, index growth,
replacement, reset, recovery and output queries. Zero-allocation cancellation,
execution and retained-ID replacement also succeed with the next PMR allocation
armed to fail. Every fault retry checked canonical state, latest metadata,
invariants and live-byte cleanup; resources returned to zero after destruction.
These are local GCC/libstdc++ observations, not hosted CI or exchange validation.
