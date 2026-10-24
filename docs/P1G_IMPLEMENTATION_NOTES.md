# P1G implementation contracts

This additive synthetic-only layer links `gig::itch_context` and the existing
native replay/book libraries through `gig::itch_reconstruction`. It does not
change matching, execution, TCA, Python schemas or the replay journal format.
The latest executed evidence belongs in `P1G_VALIDATION_REPORT.md`; this document
specifies behavior rather than asserting that an unrun gate passed.

## Initialization and source identity

`SyntheticReconstructor::create` requires an authored-empty initialization record,
matching source/session and byte-zero boundary, a complete-history declaration,
synthetic origin, matching seed/digest, a generator/fixture contract version and
private synthetic policy reference. Unknown, incomplete, invalid and complete-seed
starts reject. S/O and a clock value cannot authorize an empty book. Seeded native
snapshots remain insufficient to seed source retirement/match/lifecycle context.

`initialization_verified` means these **synthetic evidence consistency checks**
passed. The library does not independently know the truth of a caller's authored
empty-state assertion or authenticate a publisher. The independent fixture runner
constructs the empty start, computes the exact BinaryFile SHA256 independently,
and checks every expected state. Raw source provenance may be unavailable and
remains unavailable; the immutable manifest is distinct from per-record values.

The fixture/generator `version` is caller-declared; generated lineage preserves it.
The reconstruction operation has its own version1. Native event and receive times
remain unavailable. Raw 48-bit nanoseconds are retained externally, without an
invented date or UTC clock. Derived stream IDs/instrument IDs are declared local
configuration; source tracking numbers are never exchange sequence claims.

## Coordinated transaction

`SourceContext::prepare` owns fixed validated deltas and does not mutate accepted
state. Its move-only token binds owner address, checked lifetime nonce and accepted
record generation. Wrong owner, consumed, moved, stale and finished tokens reject.
The lifetime nonce is not semantic output and cannot alter canonical hashes.

The adapter owns its context privately. Before native mutation it checks eligibility,
routing, exact conversions, metadata, token and pre-reserved receipt capacity.
It invokes at most one fallible `ReplayEngine::apply`. After success, only the
private nofail context commit, reserved receipt copy and bounded counters run.
No export, callback, serialization or allocation is added to that commit section.
A reentrant process/finish call from an allocator is blocked. As with the existing
engine, callers must not move/destroy an object or its resource during a member call;
all operations are single-threaded and the resource must outlive all owners/outputs.

A failed native call may retain capacity or recovery-required diagnostics. Accepted
book/context/cursors/journal/receipt prefixes must remain unchanged. Resources are
not silently retried: the exact held payload, location and raw provenance are required
for an explicit retry. A changed payload cannot skip a failed source position.

## Projection and bounds

A/F add; E decrements an identified resting order; X cancels a delta; D cancels all;
U atomically retires/replaces with a new FIFO ticket. C is disabled unless explicitly
enabled as a book-only decrement at the resting price; its real execution price and
printability remain in the source receipt. P/Q/B and S/R are external observations;
no native sequence or journal is consumed, no hidden liquidity is inserted, and B
never restores liquidity. Unsupported types and unknown bindings stop explicitly.
One or two configured books have independent contiguous derived sequences and
journals. Shared source lifetime IDs prevent reuse across symbols.

Conversions cancel rational factors before multiplication, check divisibility and
representation, then apply native instrument validation. No floating point is used.
The initial binding profile requires the context integer wire-unit hints to agree
with native tick/lot rules (one hint unit equals one native unit). Rational helper
conversions also support noninteger scales; profiles that cannot express that hint
consistency reject configuration rather than silently disagree.

Counts and receipt storage are bounded at creation. The default receipt reservation
is4096 slots within2MiB; native journals retain their existing capacity policy and
100,000 hard maximum. The independent driver/benchmarks supply a128MiB hard shared
PMR resource. The general API accepts a caller-owned resource; its default resource
has **no additional aggregate byte governor** beyond explicit container/count caps.
Use a budgeted resource for bounded applications. Object/stack, fixture storage,
allocator overhead and process RSS are measured separately from tracked PMR.
No journal pruning, rotation, compact storage or hot recovery is implemented.

## Accounting and restart

For considered complete payloads:

```
considered = native_committed + external_observations + rejected + pending
context_committed = native_committed + external_observations
```

Here pending is0/1 for a resource-deferred held record. A semantic rejection is
rejected=1,pending=0; its bytes are still held to prevent source skipping. Successful
exact retry changes that record's disposition once. Repeated attempts do not increase
considered. A cap+1 offered record is explicitly unconsidered and prevents a complete
source claim. Full-file tail counts remain unknown. Physical offered position and
last context commit are distinct. Framer partial bytes are not complete records.

Version1 checkpoints bind exact config, caller-supplied implementation SHA256,
framed-prefix SHA256, context summary, source receipts and native canonical state.
Capture independently rebuilds the prefix before accepting the descriptor. Restart
rebuilds an isolated adapter from byte zero, verifies the trusted descriptor and
only then returns it. Changed source/config/code/state rejects. This is integrity
verification against trusted caller evidence, not a signature or proof of origin.
Uniform per-record provenance is supported; mixed per-record overrides explicitly
reject checkpoint capture. Finished/rejected/deferred prefixes cannot be captured.
No seeking into gzip, snapshot hot restore, durable crash recovery or filesystem
publication transaction is claimed. Canonical/query failure leaves committed state
intact; retry output, never reapply the source event to repair an output failure.
