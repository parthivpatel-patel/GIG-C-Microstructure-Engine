# P1I end-to-end validation plan and engineering backlog

Planning date: **October23,2026, America/New_York**. Local inspected HEAD:
`cafcdb986afac5298c95bcf3418acb7cf3e6aafe`, branch
`feat/bootstrap-cpp20-engine`, with a clean working tree before this document.
The parent delivery checkpoint records this commit as pushed/remotely verified;
this documentation review did not perform another remote/network request. P1H
implementation/measurement checkpoint:
`e055f055a447baa6bf1f913c09f7c7dcd57a8878`.

**Preparation only. No P1I production code, new tests, data acquisition, release,
merge or deployment is implemented/authorized by this plan.** The current assignment
permits read-only/documentation preparation after P1H; future implementation packages
below require explicit scope authorization. Existing P1G/P1H evidence remains the
baseline, not an excuse to repeat successful matrices without a relevant change.

## Starting capability and evidence

The verified synthetic pipeline now exists: bounded gzip → BinaryFile framing →
typed decode → prepared context/native transaction → two independent native L3 books,
with receipts, separate integrity/completeness flags and byte0 checkpoint replay.
It is synthetic-only and is not a real-market adapter or an execution simulator.
See [P1G implementation notes](P1G_IMPLEMENTATION_NOTES.md),
[P1H validation](P1H_VALIDATION_REPORT.md), [coverage](P1H_COVERAGE.md) and
[machine-readable evidence](P1H_EVIDENCE.json). This plan extends rather than
duplicates their source/test mappings and the original
[P1G-to-release backlog](P1G_TO_RELEASE_BACKLOG.md).

At the delivery checkpoint, P1H recorded1,063 actual CTest outcomes:117/117 in
each GCC/Clang native Debug/Release/ASan+UBSan configuration,120/120 Python
Debug/Release and121/121 Python sanitizer, with zero failures/skips/disabled tests.
The direct and source-built wheels each passed7 interface plus6 export-contract
tests. Sixteen measured Release benchmark cases, actual allocator probes and a
500,001-record authored synthetic compressed source with a controlled1,024-record
accepted stop are recorded there. These are completed local results, not new P1I
executions, hosted CI success or observed-market evidence.

The P1G and P1H report headers now record the verified delivery checkpoints;
historical counts elsewhere remain tied to their original source revisions.

## Current source boundaries that P1I must preserve

Source references below describe the inspected P1H checkpoint, not a proposal:

| Current interface/source | Implemented boundary and consequence |
|---|---|
| `src/itch/reconstruction.cpp:70–76` | Factory requires authored-empty evidence at byte0/ordinal0, complete synthetic history declaration and synthetic source provenance matching fixture hash/seed. **Observed-origin initialization is not supported.** Changing a label or constructor flag is not an observed adapter. |
| `src/itch/reconstruction.cpp:77–89,169–180` | At most two preconfigured books; unknown stock locate/binding, mismatched symbol and default-disabled C book-only projection stop explicitly. An R for an unconfigured symbol can stop a full-market prelude before useful target orders. |
| `src/itch/decoder.cpp:61–104` | S,R,A,F,E,C,X,D,U,P,Q,B decoded; recognized but unimplemented types, including H/h, are unsupported. A historical file can stop before any native mutation; absence of handling is not permission to skip. |
| `include/gig/itch/context.hpp:21–32` | Context defaults64 directories,4,096 lifetime IDs and4,096 matches,4MiB logical vector budget; lifecycle/clock/units are explicit policies. The often-used8-directory/1,024-reference profile is a selected configuration, not this API's default. |
| `include/gig/itch/reconstruction.hpp` | BookBinding defaults128 orders/128 levels/depth16 and1,024 journal records per book; source records default4,096, receipt budget2MiB. Hard aggregate PMR governance is caller-supplied; count limits do not establish process RSS. |
| `src/replay/replay.cpp:45–49`; `include/gig/events/contracts.hpp:156–160` | Native journal maximum100,000; complete native snapshot capacity64 orders/8 boundaries. Snapshots neither append larger books nor seed source directories, retired references, matches and lifecycle state. |
| `src/itch/streaming.cpp:18–26,92–110` | Streaming constructs that same synthetic reconstructor. Publication requires actual EOF, gzip verification, BinaryFile termination, exact compressed/raw identities and no error/pause. It does not establish exchange completeness or a historical initial state. |
| `src/itch/streaming.cpp:122–139`; `include/gig/itch/restart.hpp` | Trusted in-memory logical descriptors and isolated replay from byte0; no signature/MAC, persistent inflater state, compressed seek, serialized complete-context loader or crash-safe hot recovery. |

Retired and match references are retained within explicit bounds, not evicted to make
a later event pass. A native journal entry remains15,944bytes on the measured ABI.
Input streaming does not remove retained-journal growth. Preserve source raw TOD,
tracking numbers, actual C price/printability, hidden/cross/correction observations
and source-to-native accounting; never invent UTC, missing orders or executions.

## A. Unblocked synthetic candidate work

The following packages are dependency-ordered. **Unblocked** means technically
independent of NASDAQ rights/network/data, not authorization to implement production
code now. S/M/L are relative engineering effort, not calendar-duration promises.
P1J owns the final independent audit/release checklist; this table specifies the
end-to-end evidence that audit should consume.

| Package / priority | Files and interfaces affected | Required future work | Independent oracle and measurable acceptance | Dependencies / blockers | Memory/performance risk | Effort |
|---|---|---|---|---|---|---|
| I01 / P0 evidence binding | Existing `docs/P1G_EVIDENCE.json`, `docs/P1H_EVIDENCE.json`, validation/progress reports; proposed offline evidence-index verifier | Bind source/config/toolchain/artifact identities to actual executed logs and clean implementation commits; reconcile historical pending headers and distinguish omitted evidence from failure | Independent hashing/JUnit parsing; every claimed outcome links to one actual result; wrong source/artifact/digest negative controls fail; zero contradictory totals or identities | Existing evidence available; any new verifier requires authorization; raw local logs are not guaranteed portable/distributed | Evidence parsing must be bounded; avoid embedding full raw traces or copied binaries | S–M |
| I02 / P0 consolidated synthetic demonstration | Existing `benchmarks/itch_streaming_benchmark.cpp`, streaming/reference drivers, `scripts/check_itch_streaming_reference.py`, `docs/REPRODUCIBILITY.md`; proposed small run manifest | Define one offline fixture/run showing valid full input, bounded interruption, verified restart and corrupt-source rejection; use current libraries/CLI rather than a new dashboard or framework | Freeze authored bytes/config/seed; literal trace plus independent Python flat-book/Fraction model; nonzero native and external counts; exact per-book FIFO/ledger/journal and disjoint source accounting; corruption cannot publish | I01; synthetic fixtures unblocked; new harness changes separately authorized | No whole-artifact accumulation; reader and fixture-generator memory measured separately | M |
| I03 / P0 end-to-end provenance/output contract | `include/gig/itch/{reconstruction,streaming,restart}.hpp`, existing canonical/reference output; proposed versioned validation-report schema and checker | Specify the minimal immutable research evidence record: origin, actual/declared hashes, rules, missing clocks, source/native mapping, completeness, observed versus deferred errors, implementation identity and output status. Implement only a justified thin exporter if current outputs cannot satisfy it | Independently built expected fields from bytes/manifest; exact C/P/Q/B distinctions; absent metadata remains absent; deliberately contradictory hashes/false full-source flags rejected; output/export failure cannot reapply native events | I01/I02; schema/compatibility review before code; no new Python reconstruction API assumed | Canonical/export allocation peaks; parent lifetimes and retained source records; no unbounded report buffer | M |
| I04 / P0 final boundary/failure review | Existing `tests/test_itch_{context_prepare,reconstruction,streaming,gzip,restart}.cpp` and independent scripts | Trace all public boundaries across prepare/native/receipt/hash/export/pause/EOF; add only independently justified gaps, preserving existing negative controls and canonical hashes | Reached allocation failures stay atomic; no leaked storage; stale/wrong-owner/single-use tokens rejected; late CRC/read-ahead and prior semantic-error outcomes remain distinct; count every required scenario as pass/fail/unrun | I02/I03; source-level independent review may reveal defects requiring scoped repair | Fault/query/export paths may hold extra capacity; diagnostics are separate from accepted semantic state | M–L |
| I05 / P1 profile qualification | Existing context/reconstruction/streaming benchmarks and independent benchmark checkers; existing PMR worker; proposed profile/evidence manifest | Qualify only intended candidate profiles, including remaining default-cap query/export/restart coexistence peaks. Reuse current16-case baseline; repeat only for changed scope/code/profile or unresolved concern | Measured PMR/RSS and released bytes; independent fixture/count/hash verification before timing; explicit cap failures; exact scope/CPU/compiler/warmups/repetitions. No invented throughput or tail-latency SLA | I04 correctness gate; current full default-cap combinations and event-service tails not exhaustively measured | Two retained journals and isolated restart can coexist; allocator/string export peaks; finite caps may fail before nominal count maxima | M |
| I06 / P1 clean reproduction and package boundary | Existing CMake presets/options, `pyproject.toml`, lock files, installed-consumer tests and examples; proposed offline reproduction manifest | Reproduce in a clean checkout/source archive using pinned available dependencies; verify optional streaming ON native and OFF ordinary-wheel contracts. Keep Python ABI/API unchanged unless separately authorized | Source archive byte inventory; direct/source-built installed-wheel interface/export tests; imported module paths; no unintended libz link to extension; identical non-timing semantic outputs; no missing/unconfigured required streaming tests in qualified native rows | I03–I05; tools/dependency cache available; unavailable platform/network evidence explicitly unrun | Stale objects and VCS source omissions; toolchain/stdlib/dynamic-zlib drift | M |
| I07 / P1 independent candidate review handoff | This plan, P1G/H evidence, proposed P1J audit/limitations/acceptance documents | Review source/evidence rather than accept report assertions; map remaining findings to scope and release decisions; retain a reproducible first-divergence case for any defect | No unresolved critical/high correctness defect in declared synthetic scope; every remaining limitation explicit; required local compiler/sanitizer/package results verified against final code; signed-off scope does not claim observed validation | I01–I06; independent reviewer availability; hosted CI access/advisories remain separately unverified until actually checked | Broadening scope late can invalidate baseline; avoid unrelated storage/API refactors | M |

Existing Linux qualification is GCC14.2.0 and Clang19.1.7 with the system GCC standard
library, CPython3.12.14 and zlib1.3.1. Hosted Actions, ARM64, other OS/stdlib/Python
combinations and current security-advisory clearance are **unverified**. Do not treat
a workflow edit or portable API as a pass. Decide the private candidate's claimed
platform scope before expanding it. Native leak checks remain enabled; the documented
Python live-LSan/late-finalization limitation remains explicit.

## B. Real-market path — not unlocked by synthetic acceptance

The [rights/access ledger](REAL_MARKET_DATA_ACCESS.md) records the user-provided Dan
Vizconde quotation supporting sample download/use. The original correspondence was
not independently authenticated here; unrestricted redistribution/publication and
an explicit retention schedule are not established by the quotation. This is not a
reason to invent a mandatory paid agreement, nor authorization to download in this
assignment. **No NASDAQ or LOBSTER market bytes were acquired.** Actual acquisition
requires separate authorization after resource verification; LOBSTER Support Case
#17931099 remains separate and is not a synthetic/NASDAQ engineering dependency.

Use [NASDAQ_REAL_DATA_PILOT_PLAN.md](NASDAQ_REAL_DATA_PILOT_PLAN.md) for exact source
URLs, prior3,524,013,057-byte compressed length, proposed staged bounds and integrity
procedures. Those prior transport facts do not establish archive contents, member
structure, actual trading date, useful L3 interval or sufficient resources. Do not
infer random seek capability from HTTP Range or whole-file integrity from a prefix.

| Package / priority | Files/interfaces affected | Required future work and independent acceptance | Dependencies / precise blocker | Resource risk | Effort |
|---|---|---|---|---|---|
| O01 / P0 permission/resource preflight | Existing access/pilot ledgers; private acquisition manifest outside Git | Record intended use/retention/output handling, exact official artifact, free disk and fixed byte/time/memory limits; explicit acquisition approval before first bytes; no purchase/redistribution | User authorization after preflight; raw/derived publication rights unresolved; no archive requested now |3.52GB compressed artifact; decompressed size/runtime unknown; full acquisition needs a different resource decision than a prefix | S plus external approval |
| O02 / P0 bounded format inventory | Proposed private byte-source/inventory harness reusing reviewed gzip/framer; no changes to current synthetic contract by default | Inspect permitted byte0 prefix; independently hash exact extents and parse framing/types/flags/timestamps/members; publish metadata only. A cap stop may be inconclusive | O01 and separate implementation/acquisition authorization; actual historical schema/member structure unknown | A small compressed prefix may expand beyond caps or never reach relevant orders; no full download assumed | M |
| O03 / P0 explicit source scope | Proposed source-scope policy/context admission/receipts and reference model; `context.hpp/cpp`, future observed adapter boundary | Design bounded whole-market-prelude versus target-symbol classification; retain global controls/locates and every considered disposition without native journaling other books. Independently prove target history and declared reference-namespace coverage; unknown target mutation stops | O02 inventory plus reviewed scope semantics; **current unknown-binding R rejection is a hard blocker**, not a filter option. Out-of-scope IDs cannot be silently forgotten while claiming full-day global uniqueness validation | Directory/lifetime/match/receipt growth can exhaust caps before useful target state; review retained versus streamed accounting without redesigning native journal incidentally | L |
| O04 / P0 dated semantics and truthful observed provenance | Proposed observed profile/adapter; current decoder/context/native projection interfaces | Pin historical revision and every encountered type/enum. Add only necessary semantic support with independently authored byte/context fixtures; preserve C execution-price distinctions, status/auction/correction limits and exact units; truthful observed origin and missing clocks | O02/O03; **current factory requires synthetic origin/authored-empty evidence**. H/h and other unsupported families cannot be bypassed or mislabeled synthetic | Unsupported administrative prelude or crossed intermediate states may invalidate book continuation; full tape semantics can remain excluded explicitly | L |
| O05 / P0 observed initialization | Proposed evidence/verifier; separate complete-context seed capability only if necessary | Establish independently supported empty boundary+complete relevant history or genuine complete identified L3/context state; reject missing queue/history. Never infer from S/O, timestamp, file boundary or aggregate depth | O02–O04 plus authoritative source evidence; current native snapshot64-order bound and missing context seed block arbitrary snapshot starts. Valid initial state may simply be unavailable | Full initialization can exceed journal/lifetime limits; multiple recoveries do not append a larger snapshot | L–XL, uncertain |
| O06 / P0 independent observed reference | Proposed private reference parser/alignment manifest/comparator; existing real-data acceptance methodology | Obtain legally usable independently supplied snapshots/order states; predeclare row timing/alignment/depth and comparison interval. Report eligible/attempted/match/mismatch/missing totals; zero unexplained eligible mismatches, exact first reproduction | O01/O02/O05; **no independent observed reference currently identified**. Two internal models agreeing is differential validation, not publisher-reference success | Reference coverage may be shallow, absent or differently timed; aggregate agreement cannot prove queue identities | L plus external availability |
| O07 / P1 separately authorized pilot | Future observed harness/adapter, private evidence outside Git | Run only the declared eligible bounded interval with independent comparisons, complete source/native/unsupported/pending accounting, actual memory/throughput and integrity identities; retain every limitation | O03–O06 and explicit run authorization; zero eligible rows or unavailable initial state cannot pass | Native100,000 ceiling and15,944-byte entries remain; allowed prefix may be too short for a useful interval | L |

**Current recommendation:** GO for the authorized synthetic candidate audit and
reproducibility preparation; CONDITIONAL GO for a later separately authorized bounded
format inventory; **NO-GO for directly replaying the EMI archive through the current
API as validated observed L3**. Rights clarification advances access readiness but
does not solve synthetic-only initialization, strict scope, unsupported messages,
retained-state capacity or missing external-reference evidence.

## End-to-end candidate acceptance and stopping conditions

The synthetic candidate handoff must demonstrate one consistent artifact chain:
source/config/seed/code → independently identified compressed/raw fixture → exact
accepted prefix → context/native/receipt state → immutable validation output →
verified reproduction. The demonstrated chain must include a true full-source success,
an explicitly incomplete bounded prefix, an identical restart from byte0 and a corrupt
source that cannot become publication-eligible. Reject a conflicting digest, changed
implementation/config, missing order, off-unit conversion or unsupported mutation;
do not repair it by rounding, silent skip or state fabrication.

Required outcomes remain actual GCC/Clang Debug/Release/ASan+UBSan, applicable Python
regressions and installed direct/source-built consumers for the **final changed code**.
Do not rerun1,063 outcomes solely for a planning document. If implementation changes,
run relevant focused gates, freeze sources, then complete the required final matrix;
preserve old P1E/P1F/P1G hashes unless a justified versioned contract change is reviewed.
Keep count of executed tests distinct from assertions, fixtures, candidates, benchmark
repetitions and unavailable evidence. No failed assertion, sanitizer warning or
required test may be disabled to meet the calendar.

Stop the declared validation claim at the first unexplained state mismatch, missing
initialization/history, target semantic ambiguity, unsupported event or resource bound.
Keep the valid prefix and exact diagnostics; do not continue into a misleading healthy
book. A failed or empty observed comparison can still yield useful inventory evidence,
but cannot count as empirical L3 validation.

## Conditional critical path to November5 / November12

There are **13 calendar days** from October23 to November5 and **20** to November12.
These are planning windows, not measured effort estimates or promises of a full
real-market/production release. P1G/P1H have cleared their local synthetic gates;
the remaining synthetic critical path is evidence binding → consolidated reproducible
demonstration/output contract → targeted gap review/profile qualification → final
candidate audit. External observed work is a separate path with no guaranteed date.

| Conditional window | Intended exit / constraint |
|---|---|
| Oct23–26 | Complete authorized P1I/P1J documentation preparation and source/evidence audit; decide any narrowly scoped implementation still needed. No new production phase begins without approval. |
| Oct27–30 | If authorized, execute I01–I04 gaps in dependency order, preserve independent oracles and resolve reproduced defects before broadening scope. O01 administrative/resource planning can proceed independently; no acquisition is implied. |
| Oct31–Nov5 | If applicable implementation gates pass, qualify intended profiles, clean reproduction/packages and independent candidate review. Target a **private synthetic research candidate**, with real-market and platform limitations explicit. |
| Nov6–12 contingency | Correct discovered issues and rerun affected/final gates. Defer optional bindings, new platforms, journal optimization and observed capabilities rather than dilute correctness or overstate readiness. |

What to defer: full-day/all-market scale claims, compact-journal redesign, hot crash
recovery, new dashboards, optional Python reconstruction API and additional platforms
unless a concrete acceptance need justifies separate scope. What not to build here:
live trading, broker connectivity, GIG Quant Terminal changes or new paid infrastructure.
Candidate acceptance is not authorization to merge, publish a release or deploy.

**Exact next decision:** review this backlog and the P1J acceptance/audit preparation,
then explicitly authorize the smallest remaining synthetic evidence/implementation
package or a separately resource-verified data-inspection pilot. No date, successful
synthetic test or sample-use statement substitutes for that authorization or for
observed initial-state/reference evidence.
