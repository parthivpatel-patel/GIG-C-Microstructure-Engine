# Phase 2 deterministic replay contract

Status: IMPLEMENTED; no matching, analytics, execution or Python. MUST HAVE:
strict continuity, explicit initial state/recovery, atomic book/cursor/journal
commit and complete accepted-event lineage. Buffering/reordering, multi-book
routing, live feeds and exchange-specific adapters are LATER / EXPERIMENTAL.

## Initial state and declared sources

ReplayConfig requires run ID, venue book session and 1..8 StreamStart declarations.
Each declares venue, dataset identity/version, stream/session/epoch, sequence unit,
first expected sequence and unique deterministic stream rank. A stream may contain
multiple instruments. Order IDs are scoped as in PHASE_2_BOOK.md, independently
of channel sequencing. This baseline routes ONE instrument/venue book. Up to eight
additional instrument rule sets permit explicit validated filtering within that
venue. Unknown streams/instruments or unsupported controls fail, never silently
vanish. Stream IDs must be unique within a run, including across selected datasets;
channel-local raw identities need a declared adapter mapping, not guessed coercion.

Default initial state requires a complete order-level snapshot; apply/depth refuse
until recovery. Synthetic fixtures explicitly declare an empty initial book.
A nonzero first sequence alone NEVER establishes an empty historical book. Initial
snapshot boundaries may end immediately before the declared first sequence, not
arbitrarily earlier. Scope/session changes are rejected until an explicit reset or
snapshot transition. Dataset identity/version, venue, sequence unit and stream rank
cannot silently change inside a run.

## Sequence and multi-stream order

Message sequencing: first subevent index is 0; all subevents retain the same
sequence and declared message count. Advance sequence only after the last subevent.
Event sequencing: index 0/count 1 only. Detect duplicate last (sequence,index),
regressions, gaps and inconsistent message extents. Sequence UINT64_MAX can be
accepted once, then the cursor is exhausted; never wrap to zero.

Continuity is checked BEFORE instrument filtering. A filtered event is still
validated using its declared instrument rules, advances its stream cursor and is
retained in the journal, but does not change the target book. No payload is
validated against another instrument's tick/quantity rules by accident.

Two input ordering policies, with NO internal sorting:
- capture_ordinal: strictly increasing per-CANONICAL-EVENT ordinal. This is not a
  packet counter repeated across subevents; raw packet/source identity is separate.
  Gaps in this global ordinal can reflect unselected streams; selected streams
  still require strict sequence continuity. Source timestamp regression is retained.
- timestamp_rank: caller supplies already merged input ordered strictly by
  (UTC event timestamp, configured stream rank, sequence, subevent index). Every
  timestamp must reference the declared common UTC clock identity; unknown or
  unsynchronized clocks are unsupported. Equal timestamps use the declared rank,
  never inferred causality. Reject bad order, do not reorder it. Resets/recovery
  must also advance the global key; no implicit time or ordinal rebasing.

Every accepted subevent is a consistent non-crossed book boundary; transient
crossed multi-event bundles are unsupported. Independent stream subevents may
interleave when these consistency/sequence/order rules hold.

## Stop, reset and recovery

apply handles ordinary data/observations. A source continuity/order failure marks
needs_recovery and preserves the committed book, cursors, ordering high-water mark
and accepted journal. That diagnostic change is intentionally visible in canonical
output; it is not a partially applied book event. Normal replay and healthy depth
publication remain blocked until successful recovery. Invalid payload, allocation
or capacity errors do not consume an event; they can be explicitly corrected or
retried at the SAME expected position. run(span) always stops at the first error
and reports accepted prefix count and failing input index. Callers must inspect
that result; a valid committed prefix is not proof that a whole input file passed.

reset(event, RestartPlan): source reset event must be continuous under the OLD
scope and end its message; no other stream may have pending subevents. The complete
plan supplies every new stream scope/first sequence. New epoch equals the reset
payload's strictly greater next epoch; session identity may explicitly change.
Clear old orders, debit discarded quantity and switch book/cursors together.
Source identities/ranks/units remain fixed. Reset cannot bypass a detected gap;
recovery requires a real declared snapshot rather than an invented empty book.

recover(snapshot): complete order-level coverage only. Require exactly one valid
included boundary for EVERY configured stream, all in the explicitly declared new
book session/epoch. Never infer FIFO from aggregate or bounded snapshots. The
snapshot's source boundary must equal its envelope position. In the same scope,
no boundary can precede committed history, message counts cannot change for an
already observed sequence, and the source cannot duplicate its last accepted
position. Other-stream boundaries may equal their last included position. New
scope requires a greater epoch. Restore expected position strictly AFTER each
included boundary (possibly within a message), rebuild book from supplied FIFO
ranks, and clear recovery-required only after atomic commit. Payload/provenance
validation does not certify external snapshot authenticity or completeness.

Controls for filtered instruments require a future multi-book router; they are
explicitly unsupported in ordinary apply, not silently processed as target resets.

## Atomic journal and lineage

Validate source, prospective cursor, ordering, payload, reset/recovery plan and
journal limit first. Reserve journal capacity BEFORE calling book mutation. Book
stages allocations as documented separately. Once book commit succeeds, journal
append into reserved storage, fixed cursor replacement and ordering assignment
are nonthrowing (JournalEntry copy construction is statically checked). No I/O or
external callbacks enter this section. Reset/recovery update all cursors atomically.

Every accepted input is OWNED in the journal, including its full metadata,
provenance, missing reasons, payload and disposition (book/filtered/reset/recovery).
Reset entries also retain the complete restart plan. Rejected messages are not
accepted journal entries; callers can archive input/error diagnostics separately.
Book and replay have no disk transaction or crash-durability claim.

The journal retains 4096 records by default, configurable 1..100000, with geometric
bounded reservation. Resource exhaustion returns an error. A failed book stage
may leave extra reserved journal capacity, but never an extra committed record or
changed cursor/order key/book. Capacity is excluded from canonical logical state;
all allocations are released at owner destruction. Provide a byte-budget resource
when bounding physical memory; full event ownership is intentionally expensive.
No streaming spill/output retention optimization has been introduced.

Replay depth returns owned levels plus (run ID, journal prefix count, book revision).
Complete research lineage requires retaining/resolving that canonical run journal
and its surrounding manifest (code SHA, source hashes, parameters/environment).
latest_metadata alone is not lineage for a reconstructed state. Events/copies keep
synthetic vs observed, source, transformations, parents and real generator seeds.
Fixed fixture helpers use seed 0; randomized tests carry their ACTUAL stream seed.
A fixed-seed labeling issue in the first book fixture helper was corrected here;
it did not change book mutation semantics or the reference-operation sequences.

## Canonical replay outputs

Internal grammar gig.replay.v1 emits initial configuration/assumption, policies,
current diagnostic, ordering high-water mark, every cursor, every journal event
(including all provenance/missing fields and reset plans), and canonical book state.
Numbers use to_chars, independent of locale. Tokens encode byte length; then exact
bytes; then a delimiter, so printable delimiter/quote/backslash bytes are preserved.
No raw object memory, padding, addresses, floating price conversion or unordered
iteration is serialized. Book levels are best-to-worst, orders FIFO. Configuration
list order is an explicit input and retained; identical input/configuration gives
identical output. This is an internal versioned canonical representation, not a
GIG wire ABI or an implemented parser. Future schema compatibility needs review.

Complexity: 8-stream/config scans are bounded. Dispatch adds expected book mutation
cost plus validation, a bounded event copy and amortized journal reallocation;
worst journal growth copies O(H) records. Retained memory O(H*sizeof(JournalEntry))
plus book state; canonical export O(H+N+L) bytes/work plus its owned output. Snapshot
recovery has bounded K<=64 book inserts plus 8 boundary checks. No concurrent state.

## Checkpoint validation

Local GCC Debug/Release/ASan+UBSan: 47/47 CTest outcomes in each configuration,
zero failures/errors/skips and no reported sanitizer findings. Replay fault sweeps
exercise 30 reached allocation-failure positions; book sweeps remain 34. All failed
resource operations preserve committed canonical state (including cursor/order/
journal/diagnostic fields), and tracked bytes return to zero at destruction.
Continuity-stop diagnostics intentionally differ while committed fields stay fixed.
The 20000 independent reference operations additionally assert actual seed retention
(current reference assertion count 1318396). Fixed fixtures use seed 0, not a fake
common random-workload seed.

The synthetic demo's 11-record workflow (all event families, explicit reset and
recovery) produces byte-identical canonical output in Debug, Release and ASan+UBSan:
SHA-256 `bee1448c29fc918911c48e62a6f6060d09d3e53f0938a02f4e4063b49d362979`. This is current-platform/build-mode evidence, not ARM64 or
hosted CI success. No performance result is inferred from these tests.
