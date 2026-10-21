# Phase 2 completion report

Phase 2 ONLY: deterministic order-level reconstruction and strict replay are
implemented and locally validated. No Phase 3 analytics, synthetic matching,
execution simulation, Python bindings, live/broker integration or Terminal changes.
Stop for explicit approval before Phase 3.

## A. Repository and commits

Repository: parthivpatel-patel/GIG-C-Microstructure-Engine. Development branch:
`feat/bootstrap-cpp20-engine`. Starting local and remote commit, verified clean:
`4417d21d9e7bdc691cd312b972dddc3951c6cf2e`.

Each bounded implementation checkpoint was tested, diff-reviewed, committed,
pushed normally and verified against the exact remote branch SHA before proceeding:

- Book: `790245248f028eb39b734c4c411489b7068553ba` (36/36 in all three modes).
- Replay: `f2273f872f5cf3b3e6f42a61296da47d3eed9a96` (47/47 in all three modes).
- Final code/benchmark: `23c98d119dbd5e7fe05e2caf6a1c71d47ade9a8b`
  (48/48 in all three modes; clean commit used for archived measurements).

The ending evidence/report commit contains this document and the archived manifest;
its exact ending SHA is supplied in the final response and remote verification.
A file cannot contain its own Git commit hash. No history was rewritten. Remote
main remains `165c5038336887116d69160b0d8e5a1a5ef59d16`; no merge or force push.

## B. Complete changed-file list

Relative to the verified Phase 1 starting commit (33 final paths):

- `.github/workflows/ci.yml`
- `CMakeLists.txt`
- `README.md`
- `benchmarks/CMakeLists.txt`
- `benchmarks/book_benchmark.cpp`
- `benchmarks/copy_probe.cpp`
- `benchmarks/copy_probe.hpp`
- `docs/ARCHITECTURE.md`
- `docs/LIMITATIONS.md`
- `docs/MARKET_MODEL.md`
- `docs/PHASE_2_BENCHMARKS.md`
- `docs/PHASE_2_BOOK.md`
- `docs/PHASE_2_REPLAY.md`
- `docs/PHASE_2_REPORT.md`
- `docs/VALIDATION.md`
- `docs/baselines/phase2-book-replay.json`
- `fixtures/synthetic/book_events.hpp`
- `fixtures/synthetic/phase2_workload.hpp`
- `fixtures/synthetic/replay_events.hpp`
- `include/gig/book/order_book.hpp`
- `include/gig/core/result.hpp`
- `include/gig/detail/canonical.hpp`
- `include/gig/memory/tracked_resource.hpp`
- `include/gig/replay/replay.hpp`
- `scripts/check_book_benchmark.py`
- `scripts/run_phase2_benchmark.py`
- `src/book/order_book.cpp`
- `src/main.cpp`
- `src/replay/canonical.cpp`
- `src/replay/replay.cpp`
- `tests/support/book_reference.hpp`
- `tests/test_book.cpp`
- `tests/test_replay.cpp`

## C. Architecture and complexity

Single owner; separate ordered bid/ask PMR maps, FIFO PMR lists and scoped hash
index pointing to stable list iterators. Order namespace is instrument, venue,
session, epoch and ID; streams scope sequencing, not orders. Stable allocated State
survives owner moves. No full-book clone per normal mutation or alternate optimized
storage. Caller-owned allocator must outlive all dependent objects/outputs.

N orders, L levels, D depth, H journal records: add/priority-changing replace has
O(log L) map work, expected O(1) hash work and amortized O(N) rehash (adversarial
hash lookup O(N)); cancel/fill expected O(1) plus O(log L) level work. Best prices
O(1); aggregated depth O(min(D,L)); state memory O(N+L) plus nodes/buckets/staging.
Invariant scan O(N+L) expected. Bounded recovery K<=64 sorts O(K log K) and inserts.
Replay adds bounded eight-stream scans, full event ownership and amortized journal
growth copying O(H) records. Journal memory O(H*sizeof(JournalEntry)); canonical
export O(H+N+L) records/work plus output bytes. Debug scans invariants per commit;
Release timing excludes those automatic scans. See PHASE_2_BOOK.md for details.

## D. Supported mutations

Adds append FIFO; partial cancel/quantity reduction/partial execution retain queue
priority; full cancellation/execution remove the ID and empty levels. Identified
executions require matching stored side/price and sufficient remaining quantity;
explicit non-head execution is permitted as a feed observation without matching.
Retain-policy replace requires same side/price and nonincreasing positive quantity;
it may rekey to a unique ID without queue movement. Lose-policy replace appends
fresh priority, including same-price increases and side/price changes. New quantity
means NEW remaining quantity. Duplicate active IDs, missing IDs, overdraw, crossing,
invalid scope, overflow and configured capacity failures reject atomically.

Reset clears old orders and debits discarded quantities while retaining lifetime
conservation history. Complete order-level snapshot recovery replaces state using
explicit FIFO ranks; never merges or infers priority from aggregate depth. Replay
requires explicit reset/recover APIs and boundaries. Quote, print-only Trade and
SessionEvent are accepted observations: journal/latest metadata/revision may advance,
but order quantities do not change. Every event is a consistent boundary: bid>ask
rejects, locked observations allowed. No incoming event automatically matches.

## E. Replay continuity and dispatch

Declared streams, dataset versions, session/epoch, first sequence and rank are
mandatory. Default initial state requires a complete snapshot; synthetic empty
state is explicitly declared. Per-event or message/subevent sequences are strict:
detect duplicates, regressions, gaps, extent changes and UINT64_MAX exhaustion.
Continuity is checked before validated instrument filtering; filtered inputs remain
journaled and advance cursors. Unknown instruments are unsupported.

No sorting: capture policy requires globally increasing canonical-event ordinals;
timestamp-rank policy requires an already merged strict tuple (common known UTC
time, declared stream rank, sequence, subevent). Capture policy preserves source
time regressions. Sequence/order failure blocks healthy replay/depth until explicit
recovery, preserving committed book/cursors/order key/journal; diagnostic state
changes intentionally. Semantic/resource failure consumes nothing and may be retried
at the same position. Batch run stops at first error and reports committed prefix.

Reset requires continuous old scope, no pending messages and a complete restart
plan for every stream. Recovery requires exact included boundaries for all streams,
no committed rewind, unchanged observed message extent and a source boundary equal
to the snapshot envelope. A new session needs a greater epoch. Accepted journal,
book and all cursors commit atomically. See PHASE_2_REPLAY.md for edge conditions.

## F. Invariants and failure atomicity

Scanner checks unique indexed active IDs, every list/index association, positive
quantities, strictly increasing FIFO ranks, level counts/aggregates, no empty levels,
configured limits, prices and conservation:

    total_in = added + recovered + replacement_in
    total_out = cancelled + executed + discarded + replacement_out
    remaining = total_in - total_out

All components, totals, revision and priority are checked before commit. A lifetime
counter may exhaust even when net remaining would fit; rejection is intentional.
Adds/losing replacements stage same-allocator map/list/index nodes; live rehash is
the final allocation, followed by nonthrowing transfers. Cancel/fill/retained-ID
replacement allocate nothing. Reset/recovery build independent state then swap.
Replay reserves journal space before book mutation; remaining commit operations
are statically checked nonthrowing. Public operational boundaries return errors for
bad_alloc/capacity, not partial book mutation. No callbacks or disk writes in commit.

Actual PMR fail-at-allocation sweeps reached 34 book and 30 replay positions,
including live rehash, journal growth, reset/recovery and query allocation. Failures
check canonical state/metadata/cursors/ledger/invariants and destruction cleanup.
Tracked bytes return to zero. Capacity/reserved buckets may differ without changing
canonical logical state. Replay continuity-stop diagnostics are an explicit exception
to byte-identical diagnostics, never an exception to book/cursor/journal atomicity.

## G. Independent reference evidence

A separate flat-vector oracle scans raw integer IDs/prices/quantities and maintains
its own FIFO priorities and ledger. It does not call production mutation helpers.
20000 deterministic operations, seeds 1/42/1729/999, compare every accepted state,
full order set/priority, best/depth aggregates, totals and invariants; 1318396 active
assertions, zero failures in each final mode. Input quantities remain deliberately
small so the oracle's arithmetic is independently safe; explicit boundary tests
cover production uint64 overflow/underflow and lifetime limits. Phase 1's 10624
Python arbitrary-precision integer/Fraction cases still pass.

A first-checkpoint fixture helper mislabeled all synthetic seeds as 1729. The replay
checkpoint corrected fixed fixtures to seed 0 and randomized fixtures to their
actual seed; tests assert seed preservation. Mutation sequences/semantics were
unchanged. This correction is disclosed rather than retaining misleading lineage.

## H. Local build and sanitizer evidence

GCC 14.2.0, libstdc++ 20250315, Linux x86_64, CMake 3.31.6, Ninja 1.11.1.
Warnings treated as errors; tests retain runtime assertions in Release.

| Configuration | Executed | Failed/errors/skipped | Findings |
|---|---:|---:|---|
| Debug | 48/48 | 0/0/0 | Passed |
| Release | 48/48 | 0/0/0 | Passed |
| Debug ASan+UBSan | 48/48 | 0/0/0 | No reported sanitizer findings |

Latest full Debug time 4.99s; combined ASan+UBSan time 24.72s. The clean baseline
runner and reproduction each reran all 48 Release tests successfully (raw manifest
contains the baseline JUnit hash). Performance values come solely from Release.
Correctness-only CLI smoke checks eight workloads, sample counts, artifacts and
invalid argument exit/diagnostic. Runner rejects Debug timing and evidence overwrite;
a second smoke and full workload run reproduced canonical hashes.

The demo's full 11-record all-family workflow produces identical canonical bytes
across all three modes: SHA-256
`bee1448c29fc918911c48e62a6f6060d09d3e53f0938a02f4e4063b49d362979`.
Canonical encoding is internal/versioned, length-delimited, locale independent and
excludes padding/addresses/hash iteration. Full metadata and missing reasons survive.
No cross-architecture or stable wire-format claim follows.

## I. Reproducible performance baseline

Raw evidence: [phase2-book-replay.json](baselines/phase2-book-replay.json).
Methodology/commands/scopes: [PHASE_2_BENCHMARKS.md](PHASE_2_BENCHMARKS.md).
Clean exact code SHA `23c98d119dbd5e7fe05e2caf6a1c71d47ade9a8b`;
AMD EPYC 9V74 80-Core Processor, shared cloud, one thread, uncontrolled scheduling
and frequency. 512 synthetic orders, 32 possible price levels, seed 1729, seven
repetitions and two full warmups; replay has 1024 events over two streams.
Every benchmark input is reference/invariant validated before timing.

Throughput is median bulk-wrapper operations/s. Latency columns are separate serial
service-wrapper p50/p95/p99/worst-observed nanoseconds, with timer/error/checksum/
temporary-lifecycle overhead. Allocations are median successful PMR calls per bulk
repetition, excluding setup; PMR peak includes setup. No queue/network/venue latency.

| Case | Median operations/s | p50 / p95 / p99 / worst ns | PMR allocs/repetition | PMR peak bytes |
|---|---:|---:|---:|---:|
| add | 2,409,038 | 331 / 651 / 1342 / 90994 | 1574 | 56,816 |
| cancel | 2,760,212 | 240 / 531 / 862 / 113286 | 0 | 56,816 |
| depth_snapshot | 6,716,340 | 140 / 230 / 361 / 315565 | 1024 | 57,096 |
| event_copy_add | 5,716,710 | 181 / 271 / 431 / 172034 | 0 | 0 |
| event_copy_snapshot | 2,237,596 | 130 / 200 / 310 / 333881 | 0 | 0 |
| execution | 2,917,745 | 220 / 430 / 651 / 88530 | 0 | 56,816 |
| payload_copy | 418,985,270 | 20 / 30 / 31 / 2383 | 0 | 0 |
| replay | 46,543 | 7091 / 32378 / 242227 / 6092719 | 1585 | 24,546,696 |

Each non-replay case has 3584 service samples; replay has 7168. Raw repeated bulk,
allocation/deallocation/live/peak counts and the 10000-pair timer calibration are
archived, without subtraction. Observed timer-pair range 20..26018 ns demonstrates
measurement/scheduling noise. Worst observed service times are not guarantees.

Representation sizes: MarketEvent 12208 bytes, Metadata 5576, AddOrder 32,
JournalEntry 15944, OrderBook owner 5704, ReplayEngine owner 14776. Fixture vector
capacity storage totals 31252480 bytes. Nominal 512-payload-only storage is 16384
bytes, a hypothetical control with no metadata, NOT an allocated equivalent engine.
By-value probes are separately compiled without IPO and consume selected fields;
timings establish this ABI path, not that every sizeof byte is physically copied.
Copy controls are diagnostic, not an optimization or semantically equivalent API.

Replay PMR live-after is 16357384 bytes, lifetime peak 24546696 bytes including
geometric journal staging. Add PMR live-after 56712 bytes; cancel retains 4744
bytes of empty State/buckets; destruction frees those. Process peak RSS 67436544
bytes includes fixtures/oracle/driver/timing arrays/canonical work, not engine-only
memory. PMR excludes allocator overhead and non-PMR driver allocations. No storage
optimization was introduced; these costs are the baseline for future review.

Canonical workload: 825629 bytes,
SHA-256 `7d16448f3e9f3ac61652ce3a1ffcd4b747695a4075b0cb2aa0ecbc7d7b1850bc`.
Canonical replay: 337924 bytes,
SHA-256 `09dfc1573ad73a18e2b29dd64bdf281fa6b0e1ed14e225ac2f18cc79ae5c1b45`.
A separate 512-order run with two repetitions/one warmup reproduced both exactly.
The archived manifest's source hashes were independently checked against Git objects
at its recorded code commit; its raw-result hash was recomputed successfully.

Generated canonical files/JUnit/logs remain in ignored build directories and can
be regenerated from exact code/seed/parameters and checked against durable hashes.
The manifest durably retains all timing samples, source/executable/configuration
hashes, compiler flags, environment, provenance and summaries. Research depth outputs
reference the accepted journal by run/prefix/revision; latest metadata alone never
stands for full state lineage. External dataset authenticity remains unverified.

## J. Hosted CI status

Workflow retains GCC/Clang x Debug/Release/ASan+UBSan and adds the small correctness-
gated Phase 2 evidence runner for Release. No performance gate. Local commands pass;
hosted success is UNVERIFIED. Starting checks access returned Forbidden; final-code
GitHub checks API attempt failed at proxy CONNECT with HTTP 403 (curl exit 56), so
no hosted run/conclusion was available. Native Git push/read and SHA checks worked.
This access limitation does not establish CI success or failure. No credentials or
network policy were changed to bypass it. Clang is configured in CI, not locally
verified in this environment.

## K. Risks and unsupported mechanics

See LIMITATIONS.md for the full boundary. Main remaining risks: finite synthetic
coverage; exchange-specific stream/ID mapping and event-bundle rules unvalidated;
strict per-event crossing policy cannot replay transient crossed bundles; no real-
feed adapter/certification. Complete snapshot recovery limited to 64 orders/eight
streams. Declared-empty initialization is a caller assumption. Accepted in-memory
journal is bounded and expensive, with no crash durability/spill/parser support.
PMR resource lifetime is a caller responsibility. Lifetime conservation counters
can exhaust. Timestamp-ranked mode requires a declared synchronized UTC clock;
ranking is deterministic tie-breaking, not inferred cross-stream causality.
No hidden/iceberg/auction/pro-rata/pegged/STP/routing model. No production or ultra-
low-latency claim; shared CPU noise, no local Clang/native ARM/Windows/macOS evidence,
and hosted CI access remains restricted.

## L. Acceptance checklist

- [x] Starting clean branch, repository and remote SHA verified; main preserved.
- [x] Standard-container single-owner scoped FIFO book, exact counts/quantities/depth.
- [x] All authorized mutations, no matching; observation-only prints/quotes/session.
- [x] Strict continuity, both explicit merge policies, reset and bounded recovery.
- [x] Checked conservation/index/FIFO/crossing invariants and failure staging.
- [x] Actual allocation injection, rollback and cleanup evidence.
- [x] Independent randomized oracle and boundary/adversarial tests.
- [x] Debug/Release/ASan+UBSan: 48 executed, zero failures/skips in each.
- [x] Provenance-owned canonical replay and byte reproducibility.
- [x] Clean-code correctness-gated raw benchmark, copy/memory/allocation evidence.
- [x] Bounded checkpoints committed/pushed and exact remote SHAs verified.
- [ ] Hosted Actions success verified: blocked by API proxy access; explicitly unknown.
- [x] No Phase 3 analytics/matching/simulation/Python/live/Terminal implementation.

Phase 2 local acceptance is satisfied; hosted-CI evidence remains unavailable.
User review is required to authorize the next phase; no next-phase work began.

## M. Proposed Phase 3 plan (not implemented)

After explicit approval, inspect final remote state and hosted checks again. Define
basic snapshot metric contracts (spread, midpoint, microprice and depth imbalance),
units/exact rational calculation, empty/one-sided/zero-denominator states, depth and
clock assumptions before implementation. Compute only from immutable healthy replay
snapshots; preserve run/journal-prefix/revision and full transformation lineage.
Use independent Python integer/Fraction references and adversarial boundary cases,
then Debug/Release/ASan+UBSan checks and normal durable checkpoints. Keep OFI,
classification, causal-horizon studies, synthetic matching, execution simulation,
bindings and live integrations outside that phase unless separately authorized.
