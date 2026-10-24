# Observed L3 reconstruction readiness contract

Audit baseline:3ee54cf552c096bc8fe8f46b9237336bcd376473; current work remains
synthetic/offline except the already completed4KiB inspection. **NO-GO for observed
L3 reconstruction with current interfaces.** Wire compatibility is a separate gate.

## Actual pipeline and boundaries

| Stage /source | Implemented | Observed prerequisite /missing capability |
|---|---|---|
| `src/itch/gzip.cpp`, `include/gig/itch/gzip.hpp` |Single-member incremental gzip, bounded output/header/input/ratio, CRC/ISIZE, explicit EOF/prefix, sticky errors |Complete authorized source with full digest, trailer and member policy. Prefix identity does not verify archive. No acquisition adapter included. |
| `src/itch/binary_file.cpp` |Owned bounded payload buffer, BE length, physical byte positions/ordinals, terminal/trailing/fragment diagnostics |Capture completeness needs external source/transport evidence; payload tracking numbers are not exchange sequence numbers. Physical adjacency alone cannot prove no dropped exchange records. |
| `src/itch/decoder.cpp` |Exact typed wire values, profile-selected finite enums, owned strings, structured errors |23 known lengths; typed support is profile-specific. Remaining K/J/I/O unsupported, explicit stop. Historical2019 snapshot/profile remains unauthenticated beyond retained later spec and observed S/R/H/Y examples. |
| `src/itch/context.cpp` |Prepared one-shot atomic semantic deltas, daily directories, lifetime/retired orders, matches, lifecycle/clock policy, bounded reserves, exact units |Observed metadata may remain missing, but no fabricated session/date/history. Directory mapping must precede stock references. Retired IDs/matches are retained to detect reuse; resource caps stop, never evict silently. No complete-state seeding API. |
| `src/itch/reconstruction.cpp` |Joint prepared context/native transaction, two books, exact rational Price4/share conversion, contiguous per-book derived sequence, receipts |Factory explicitly requires authored complete synthetic empty evidence, origin synthetic and matching seed/digest. Observed initialization unsupported; changing an enum/origin is not an adapter. Native metadata generator remains intentionally synthetic. |
| `src/replay/replay.cpp` |Native validated event replay, journal, continuity/recovery-required diagnostics, complete order-level snapshot recovery |A native snapshot does not restore ITCH directory, lifetime/retired identities, matches, global status or source cursor; all-stream boundaries and complete FIFO identity required. No observed hot-recovery claim. |
| `src/itch/streaming.cpp`, `src/itch/restart.cpp` |Synthetic replay-from-authenticated-start checkpoints, hashes, per-stage accounting, bounded read-ahead |Restart rereads/replays source from its trusted start and compares logical accepted boundary; not seek-into-gzip hot recovery or crash durability. Raw consumed position may exceed committed prefix. |
| Research exports /`src/research`, Python existing API |Existing deterministic synthetic output contracts, references, dataset digest checks |No observed adapter/export lineage path, no independent observed reference book/queue, no empirical calibration or scientific inference validated by a tiny prefix. |

Source locations are repository-relative. Source/test contracts take precedence
over older planning language. No matcher/execution/TCA/journal behavior changes.

## Required initialization evidence

Accept only an independently verified complete order-level seed at a known source
boundary, or an authenticated complete capture whose exchange/profile contract
establishes an empty start and all prior order-state messages are present. Neither
is available in this assignment. S:O, market-open time, byte0, a directory spin,
H:T, quote/depth snapshot or absence of adds in a prefix does not establish this.
A seed must carry every active order ID, stock, side, exact price and quantity,
FIFO ordering/priority, global context and identity-retirement/match history needed
for subsequent validation, plus a declared completeness boundary. Seed import into
both context and native engine must be independently validated and atomic before use.
No top-N/L2 snapshot can invent L3 identities or queue positions.

## Source and transition invariants

1. Pin official artifact identity, acquired extent, full integrity status, profile,
   transformation/version, session/date/timezone evidence and source origin.
   Preserve unavailable metadata explicitly. Byte ordinal is capture order, not
   a fabricated exchange sequence or timestamp. No synthetic-to-observed relabeling.
2. Require daily locate↔exact padded symbol mappings; no inferred cross-day reuse.
   Track session-scoped order references and retired replacement chains. Unknown,
   duplicate or inconsistent references block acceptance; no fabricated adds.
3. A/F create identities; E/C decrement known positive remaining quantities; X is
   partial cancellation under explicit equal-cancel policy; D retires; U retires
   old identity and creates new identity/priority retaining side/stock/attribution.
   Enforce checked arithmetic and exact tick/lot conversion before native commit.
4. C execution price/printable flag remains distinct from resting price. Native
   book-only decrement is an explicit projection, not a fabricated trade at resting
   price. Define tape accounting to avoid double-counting later nonprintable crosses.
5. P is non-displayed print, not an add or inferred aggressor. Q is bulk cross
   observation; B is final correction, never automatic liquidity restoration.
   Current context rejects cross-break references; research correction aggregation
   requires a separate independently validated observed contract.
6. H/Y and v3 L/V/W/h/N are observations. No automatic clearing, trading-policy
   enforcement, liquidity creation or synthetic fill. Global V/W have locate0;
   per-security L/h/N require mapped symbols. h's venue Q/B/X is preserved, not
   conflated with cross-market H. No current per-security regime/enforcement table.
7. Validate source order as delivered. Optional monotonic/intraday timestamp policy
   must match authoritative feed guarantees or report explicit incompatibility.
   Tracking numbers are retained, never assumed globally unique/increasing.
8. Context preparation must be nonmutating. Reject before native commit; after native
   success, prevalidated context commit/receipt insertion cannot allocate or fail.
   Test real allocation failure, no duplicate retries and pending-source identity.
9. Stop on unknown/unsupported events, invalid provenance, lifecycle error, gaps,
   corrupt data, resource exhaustion or ambiguous initialization. Keep the last valid
   prefix and explicit unprocessed/pending tail, not a silently filtered history.
10. Independent observed oracle must compare every order identity, quantity, price,
    FIFO queue, level total and best quote after relevant events. Two implementations
    of the same decoder do not replace independent reconstructed-book evidence.

## Completeness is multidimensional

Distinguish gzip integrity, physical-source EOF, BinaryFile terminal, accepted
prefix, local context session closure, initialization validity, native continuity
and exchange capture completeness. `StreamingSummary::publication_eligible` is the
existing synthetic source-integrity contract; it does not independently certify an
exchange session or initialization. `SourceContext::finish` exposes
`session_incomplete` separately, even if caller-declared physical source completes.
This distinction is an observed-readiness limitation, not a reproduced contradiction
of the existing synthetic contract. A future observed publication gate must require
all independently necessary facts explicitly, with negative controls for each.

## Memory and restart acceptance

Current native journal cap is100000 entries (`ReplayEngine::create`), and synthetic
source cap is independently100000 records (`SyntheticReconstructor::create`).
Measured baseline journal entry size15944 bytes on this x86_64 ABI implies
1,594,400,000 bytes of element storage at100000 entries for one book, excluding
other state/capacity growth and recovery coexistence. Streaming decompression does
not bound retained journal/receipt/context growth by itself. Defaults are smaller:
4096 native journal records, context64 directories/4096 lifetime orders/4096 matches,
4MiB logical context budget; reconstruction4096 receipts/2MiB budget, two books.
These are configurable profile limits, not a feasible full-Nasdaq guarantee.

A future pilot must predeclare whole-process/PMR/record/journal/time/disk limits,
include oracle/query/restart coexistence, and report the first exhausted boundary.
No journal optimization is implemented here. Separate benchmark-gated plan: freeze
native replay outputs and recovery semantics, compare proposed compact journal
against the independent oracle including failure/capacity cases, then measure
memory and throughput on identical workloads before any migration.

## Dependency-ordered observed acceptance gates

- Rights/access and exact bounded resource authorization; no redistribution implied.
- Complete source integrity/profile and defensible initial boundary/seed evidence.
- Independent observed decoder/context compatibility and exhaustive source accounting.
- Dedicated observed provenance/initialization adapter; no synthetic factory bypass.
- Whole-context/native seed and restart contract with allocation-failure atomicity.
- Bounded single-symbol pilot with independent full order/FIFO oracle, then multi-symbol.
- Exact mismatches/first reproduction, rejected/unsupported/ambiguous counts, comparison
  coverage, memory/throughput and source hashes; no cherry-picked matching intervals.
- Scientific research controls: no look-ahead, explicit nonprintable/correction policy,
  no causal or statistical conclusion from format/decoder checks alone.

None of the observed gates is supplied by implementing administrative wire types.
Synthetic candidate readiness, historical decoding compatibility, observed L3
validation and production readiness remain four separate assessments.

## Phase4 machine-checkable refusal and observed16KiB follow-up

The16KiB prefix provides1433 observed S/R/H/Y messages and1424 directory admissions
in a bounded observed SourceContext with unknown initialization. No orders/matches,
book or reconstructor were created. It does not close any initial-state/session/
full-artifact gate. Retained-2023 auction v4 supports all23 documented layouts,
including K global locate0 routed by exact stock, but none of K/J/I/O was observed.

Machine-checkable audit:

```sh
python3 scripts/check_observed_l3_readiness.py \
  --from-second-prefix docs/NASDAQ_SECOND_PREFIX_EVIDENCE.json
# Expected exit1, assessment BLOCKED, observed_certified false.
python3 tests/test_observed_readiness.py
```

The checker uses a strict bounded64KiB JSON envelope, rejects duplicate/unknown
fields and coerced state values, distinguishes source claims from attestations,
and records unavailable observed adapter/context-native seed/oracle capabilities.
Even all-positive owner claims cannot fabricate these implementation capabilities
or certify observed L3. This is a versioned conservative capability audit, not
cryptographic verification or a generic future certification API. Updating it later
requires reviewing actual source/evidence and its independent negative controls.
Synthetic origin, unknown/incomplete initialization, prefix-only integrity and
unverified full capture stay BLOCKED. CLI invalid inputs exit2, never a success.

Replay/snapshot, journal and streaming contracts remain unchanged. New fault
fixtures independently check accepted/native/external prefix counts for CRC,
truncation, partial framing, oversized frame, invalid field, contradictory K cancel,
duplicate order, journal/source-cap exhaustion and unknown type across fragmented
input. Formal candidate, exchange session and observed L3 gates remain distinct.
