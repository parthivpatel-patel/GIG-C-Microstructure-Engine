# P1G — synthetic L3 integration architecture (proposed, not implemented)

Planning baseline: remotely verified P1F `d0b45b4003d0edbb0477de165e5db7e8cdb648c0`,
branch `feat/bootstrap-cpp20-engine`. P1F was pushed and the tree was clean before
this review began. This document authorizes no implementation, market acquisition,
release or change to existing execution behavior. The next step requires explicit
P1G implementation authorization.

## Readiness assessment and inspected evidence

Synthetic integration is technically feasible with the existing L3 book. It is not
safe to connect the present APIs by merely calling `context.apply` followed by
`replay.apply`: the former has already committed when the latter can fail.
Initialization, metadata and native semantic gaps also require explicit decisions.
The following source references are at the P1F baseline; documentation claims were
not substituted for implementation inspection.

| Inspected source | Verified capability and integration consequence |
|---|---|
| `include/gig/itch/binary_file.hpp:8–51`; `src/itch/binary_file.cpp:17–66` | Bounded pull framing, borrowed payload lifetime, explicit finish; consume trailing input and distinguish cutoff from EOF |
| `include/gig/itch/decoder.hpp:15–66`; `src/itch/decoder.cpp:51–109` | Owned raw types, 12 enabled families, full 48 timestamps, explicit unsupported registry; no historical/context certification |
| `include/gig/itch/context.hpp:14–105`; `src/itch/context.cpp:59–237` | Owned version/policy provenance, bounded lifetime/match ledgers, context-local atomic commit; initialization always incomplete |
| `src/book/order_book.cpp:35–111,144–230` | PMR levels/FIFO/index; staged add/replace; identified execution; no matching; crossing rejection; state/ledger atomicity |
| `include/gig/book/order_book.hpp:10–31,44–67`; `src/book/order_book.cpp:269–310` | Book limits, typed quantities, find/priority/depth/invariants; query/export allocates |
| `src/replay/replay.cpp:38–62,71–115,124–221` | Explicit initial state, derived stream sequencing, prefix run semantics, journaling, reset and complete recovery; one target book per engine |
| `include/gig/events/contracts.hpp:70–110,123–167`; `src/events/validation.cpp:34–106,190–250` | Required complete metadata/provenance; missing timestamps allowed; provided clocks constrained; native C/Q/B/session gaps |
| `include/gig/core/numeric.hpp:117–219` | Checked count/time conversion and exact rational tick/lot conversion; no floating-point adapter arithmetic needed |
| `src/book/order_book.cpp:233–267`; `include/gig/events/contracts.hpp:156–160` | Recovery replaces whole book; at most64 snapshot orders and8 boundaries; aggregate/bounded-depth recovery rejected |
| `src/simulation/simulator.cpp:55–86,115–132` | Separate synthetic price/time matching and staged command state; not a source reconstruction engine |
| `tests/support/book_reference.hpp:8–67`; `tests/test_book.cpp:15–33,90–101,108–166`; `tests/test_replay.cpp` | Existing flat C++ reference, recovery/FIFO/fault/core regression evidence; not an independent ITCH-to-L3 oracle |
| `scripts/check_itch_reference.py`; `scripts/check_itch_context_reference.py`; `scripts/check_simulation_reference.py` | Existing independent wire/context/simulation checks; extend with a separately authored source-to-book model |

The existing 775-outcome P1F validation remains the baseline; no additional engine
suite was rerun merely to write these plans. See [P1F_VALIDATION_REPORT.md](P1F_VALIDATION_REPORT.md)
for actually executed results and [P1G_VALIDATION_DESIGN.md](P1G_VALIDATION_DESIGN.md)
for proposed tests.

## Minimal scope and explicit initialization

P1G should deliver a synthetic-only bounded reconstruction driver and adapter target,
not a new book or matching engine. Initial acceptance uses authored complete history
from a demonstrably empty synthetic start. An `InitializationEvidence` proposal must
contain fixture/generator identity and hash, source/session scope, declared boundary
and complete-history coverage, configured symbol set, unit/rule manifest and version.
A naked boolean, S/O, 09:30 timestamp, top-of-book quote or later matching snapshot
cannot establish eligibility.

Proposed states: `inspection_only`, `eligible_synthetic_empty`,
`eligible_complete_seed` (deferred until seeded-context support), `blocked`,
`stopped_at_valid_prefix`. Keep eligibility, input/container completeness, context
session policy, native continuity and output completeness independent. Preserve
P1F `initialization_incomplete=true` as that component's statement of what it has
not established; a separate P1G eligibility result owns new evidence. Never rewrite
the P1F flag or oracle output to imply it validated a book.

For unknown/aggregate/incomplete initial state, allow inventory but do not construct
an externally published healthy reconstructed book. Native `requires_snapshot`
remains a guard; use `declared_empty` only after the adapter's synthetic evidence
has passed. Observed-data eligibility is excluded from this phase.

A complete initial L3 snapshot requires actual IDs, sides, sizes, prices, FIFO ranks
and all source boundaries. It also does not seed P1F retired-reference, match,
directory or lifecycle state today. Thus direct snapshot start is blocked until an
explicit, independently validated context-seed contract exists. At first implement
negative/rejection tests and deterministic restart from the authored start, not a
pretend hot restore. A 65-order snapshot cannot be split across 64-order recoveries:
each native recovery replaces the entire book.

## Proposed additive interfaces and ownership

All names below are proposals, not current APIs:

- `include/gig/itch/reconstruction.hpp`, `src/itch/reconstruction.cpp`:
  `ReconstructionConfig`, `InitializationEvidence`, `ReconstructionEligibility`,
  bounded `BookBinding`, `SourceDisposition`, `ReconstructionStep`, `ReconstructionSummary`
  and `SyntheticReconstructor`.
- Add a fixed-size, move-only `PreparedContextStep` to context.hpp/cpp, with
  `prepare(payload, location, provenance)` and an adapter-only nofail commit hook.
  Refactor P1F `apply` to use that same validated preparation/commit path while
  preserving every existing result and canonical hash.
- New standalone CMake target `gig::itch_reconstruction` links `gig::itch_context`
  and `gig::microstructure`; existing engine, simulator and Python targets keep
  their current dependency/behavior contracts.
- Proposed `process(FrameView, provenance)` handles one raw record, produces at most
  one native mutation and one bounded source receipt. Queries are read-only and
  eligibility checked. No callbacks, concurrency, external effects or deferred
  compound native events are allowed in a commit.

The adapter owns one stable context and a fixed maximum of two configured native
book engines initially. Bindings include exact padded source symbol/locate expectation,
explicit application-assigned InstrumentId/VenueId, InstrumentRules and derived native
stream ID. These assignments are declared normalization configuration, never claimed
exchange identifiers. An unknown binding stops; it is not guessed or silently dropped.

One raw event routes to at most one book. S/R/P/Q/B remain external/context observations
in v1 and consume no native book sequence or journal record. A known non-target symbol
can be explicitly classified by configured scope, with its source disposition retained;
never exclude deeper target orders or unsupported target mutations. Do not use
ReplayConfig.additional_instruments as a substitute for multiple books: it filters
and journals other instruments, it does not reconstruct them.

## Exact transition and integration contracts

| Source | Native projection in proposed v1 | Required source/external evidence |
|---|---|---|
| A/F | `AddOrder` with checked source ID, side, display price and quantity | Context before absent, after active; F attribution retained externally; append per-book local priority |
| E | `Trade{BookExecution}` for identified resting ID, side and **resting price**; exact execution delta | Raw E has no observed execution-price field; preserve match and source identity; non-head execution allowed |
| C | Optional explicitly enabled **book-only** `BookExecution` at resting price; otherwise block mutation | Preserve actual execution price and printable Y/N; no invented TradePrint or complete tape/TCA claim; never place actual execution price into a mismatching native resting-price field |
| X | `CancelOrder` positive delta under selected equal-X policy | Partial preserves surviving priority; equality allowed only by explicit profile; underflow rejects |
| D | `CancelOrder{CancelAll}` for known active order | Retire source reference; decrement native full remainder once |
| U | Atomic `ReplaceOrder`, old/new source IDs, inherited side, new total price/quantity, `ReplacePriority::lose` | Retire old and create unused new reference in same commit; retain F attribution externally; no opportunistic retain-only reduction |
| P | No native mutation/journal in v1 | Explicit non-displayed print receipt, raw side/reference not aggressor/order identity |
| Q | No native mutation/journal | Cross including zero quantity; no resting insertion, clearing, matching or inferred allocation |
| B | No native mutation/journal | Correction observation; no liquidity restoration; unresolved/Q-origin reference stops under current policy |
| S/R | No fake per-instrument SessionEvent/Quote/BookReset | Preserve distinct lifecycle/directory observations globally; never reset on S/O, E or C |
| H/h/others | Explicit unsupported stop unless a separately reviewed decoder/profile is added | No inferred halt/resume or future extension silently skipped |

`exact_candidate` is a hint, not eligibility or a validated native event. Do not
blindly copy optional uint64 unit hints into domain types. For source Price(4) p and
native tick a/b currency units, exact ticks are `(p*b)/(10000*a)`; source quantity q
and lot c/d shares give exact lots `(q*d)/c`. Cancel common factors before multiplying,
check representability/rules, and reject a nonintegral result. Existing checked
`to_ticks`/`to_lots` can be reused through bounded exact decimal formatting; verify
independently with Fraction. Construct actual PriceTicks/QuantityLots/OrderId through
their factories and validate the resulting MarketEvent. Initial profiles must make
P1F integer hints and full InstrumentRules consistent; zero/off-unit prices cannot
be repaired into valid target prices.

FIFO is source reconstruction, not matching. Partial reductions preserve core ranks;
full reduction erases an order/empty level; U loses priority and appends at the target
level. Compare per-book local tickets/relative within-level order, not numeric equality
with global source capture ordinal. Locked bid=ask is supported by the core; crossed
bid>ask rejects before commit. Do not reorder a source interval, auto-match it or
change crossing policy to make a fixture fit. Historical crossed-intermediate
compatibility remains an explicit blocker for observed ingestion.

The simulator's best-price/FIFO matching, latency, maker/taker fills and execution
schedules remain untouched and separate. Replaying an observed E/C must never submit
a simulated aggressive order or invent executions for an incoming crossed A.

## Native metadata, ordering and provenance bridge

Complete native validation requires instrument, venue, scope, sequence, source-record
identity, dataset/version/license-reference, origin/source and lineage. Synthetic
origin additionally requires a generator seed; normalization lineage requires a
parent artifact. P1F metadata can be unavailable, so an admissible context record may
still be ineligible here. The synthetic run manifest must explicitly supply truthful
fixture identity/hash/version, generator seed, internal private-fixture policy reference
and normalization/reconstruction lineage; do not invent a NASDAQ license reference.
Absent required data blocks integration rather than weakening complete validation.

Keep source time-of-day nanoseconds in the source envelope. Native timestamps may
remain `Available::missing(unavailable)`; timestamp absence is allowed by complete
validation. A supplied timestamp requires a supported clock and precision: raw ITCH
time-of-day must not be mislabeled UTC or venue-unsynchronized UTC. Use native
`OrderingPolicy::capture_ordinal`, not timestamp rank. A separate, explicitly authored
synthetic UTC clock fixture may test conversions; no observed UTC/date is inferred.
Receive time remains unavailable.

Each book has its own derived contiguous native event sequence (index0/count1).
Use source capture ordinal as increasing native capture ordinal, allowing gaps caused
by external observations or other books. Preserve a complete source-to-native map;
tracking number is not the derived sequence. No source message is converted to two
native events. Global S controls do not receive an invented observed InstrumentId.
Native source-record tokens must fit their bounded Identity; otherwise reject, never
truncate. External source/session/policy/fixture hashes remain available through the
run manifest and per-record mapping even when not duplicated into every native field.

## Joint failure atomicity: required before integration

A production implementation must preserve accepted semantic state, not promise that
allocator bucket capacity, diagnostics or physical reader position never change.
Proposed single-threaded transaction:

1. Retain the current bounded frame and verify input/context identity, eligibility,
   mapping capacity and all required metadata/conversions before native mutation.
2. `context.prepare` validates into owned fixed deltas without changing context.
   A move-only receipt binds context identity, generation, expected source cursor and
   normalization policy. Validate ownership/generation before invoking native apply.
3. Pre-reserve one source receipt/outbox slot and per-book sequence update. Reject a
   stale, duplicate or wrong-owner prepared token before any engine call. Prevent
   context move/mutation/reentrancy while the adapter owns a pending token.
4. For external observations, commit prepared context plus receipt with no engine call.
   For a projection, invoke existing ReplayEngine.apply once. It is the only fallible
   mutation step after preparation. Native rejection discards preparation; context,
   derived sequence and source receipt remain uncommitted.
5. On native success, perform only mechanically proven noalloc/noexcept operations:
   adapter-private context commit, fixed receipt append and counter updates. No second
   validation failure, serialization, vector growth, callback or I/O is allowed here.
   The private hook must not expose a public unsafe token-bypass API.

Replay apply may set continuity diagnostics/needs_recovery on some failures and may
reserve journal/bucket capacity before a book rejection. Its book, accepted journal
prefix and cursors remain the acceptance boundary. Preserve and report diagnostic
changes rather than resetting them or asserting byte-identical allocator state.
Allocation-failure tests must establish these distinctions.

The adapter retains one pending frame until the transaction commits or stops. Framer
read/decode progress can therefore be ahead of logical source/native commits; do not
call feed again and invalidate borrowed bytes without an owned bounded pending copy.
No automatic source skip, gap repair, empty reset or blind native retry is permitted.
A transient resource retry must use the same authenticated logical record without
reapplying committed events. Full run batches inherit prefix semantics, not all-batch
atomicity. Output/export failure after commit marks artifacts incomplete and retries
export only; it does not roll back/reapply the event.

## Source accounting, checkpoint and recovery contracts

For considered complete frames use disjoint outcomes:
`native_committed + external_observation + explicit_other_scope + rejected_or_unsupported
+ pending`. Maintain each book's native count separately. Framing failures and partial
payload bytes are not fabricated complete records. All count sums and positions are
checked. If acquisition stops early, full source totals/tail counts remain unavailable
unless a separate inventory exists; do not label prefix counts full-file totals.

A proposed checkpoint descriptor records fixture/config/code hashes, initialization
proof ID, last source-context commit, each book's native sequence/journal prefix/revision,
receipt prefix and independent state digests. It is not a native serialized-state loader.
V1 restart rebuilds fresh context/books from the authenticated authored start and
replays the complete committed source prefix, then compares all descriptors. It does
not seek into gzip, start mid-day or reconstruct retired/match history from live orders.

A later complete-seed recovery would need directory, active and retired lifetime
state, match/correction ledger, lifecycle/time/cursor state, units, per-book FIFO and
all native boundaries. Existing native snapshots alone cannot supply that context.
Multi-book recovery is not globally atomic by sequentially calling recover on each
engine; recreate and validate an entire isolated adapter before publishing it, or
specify a separate reviewed recovery transaction. Durable crash recovery and atomic
filesystem publication are later operational work, not implied by in-memory checkpoints.

## Initial bounded profile and implementation order

Proposed project choices, not measured market requirements: two configured symbols,
4,096 considered source frames, 1,024 lifetime references and 1,024 matches, eight
directories; per book 128 live orders/128 levels/query depth16 and 1,024 journal entries.
Use a 128MiB shared hard PMR budget, an additional explicit adapter/receipt budget of
2MiB, one generic framer buffer at most65,535 bytes and one bounded pending payload.
Declare ownership so nested resources do not accidentally double-charge or bypass caps;
measure fixed object/receipt allocations and complete process-tree RSS separately.

At the prior measured JournalEntry size 15,944, two 1,024-entry journals contain
32,653,312 element bytes; one journal growing from 512 to 1,024 while the other is at its 1,024 cap
can hold 40,816,640 element bytes while old/new storage coexist. These are arithmetic estimates, not a tested P1G budget pass. Default context
size/bounds and P1F timing show bounded linear scans, not whole-market scalability.
Re-measure the new prepared receipt and peak memory under normal/query/export/failure
paths. Cap stops must be explicit and comparison coverage must remain honest.
No journal optimization is part of P1G.

Implementation order: initialization/contracts and independent oracle first; additive
context prepare/commit preserving P1F hashes; checked metadata/unit bridge; one-book
projection then two-symbol isolation; fault/restart/cap accounting; final matrix and
correctness-first measurements. See [P1G_VALIDATION_DESIGN.md](P1G_VALIDATION_DESIGN.md)
and [P1G_TO_RELEASE_BACKLOG.md](P1G_TO_RELEASE_BACKLOG.md) for executable acceptance
requirements and the dependency-aware delivery path. No P1G production code exists
as a result of this planning commit.
