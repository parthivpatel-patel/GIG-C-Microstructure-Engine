# Phase 5 engineering report

Reviewed October23,2026 (America/New_York). UTC timestamps in raw evidence retain
the host clock. **Completed bounded synthetic engineering qualification.** Physical
ordinary-event journal records are23.28% smaller on the measured ABI, without a
canonical or research-schema change. Formal private candidate closure, observed
L3 validation and production readiness remain distinct and blocked/excluded as
specified below. No additional market data was requested.

## 1. Source, checkpoints and completed work

- Starting clean local/remote feature HEAD: `f0373aa3e662d416fe6260210a7f3158d8fecea7`.
- Baseline measurements/tests checkpoint: `90a6d7f9d4838089bb02bcd8fa60538f73f50222`.
- Validated implementation checkpoint: `6eee608ea6436a27bb0698dd6ee3f6f074353b2c`.
- Both new checkpoints were pushed and exact remote SHAs verified on
  `feat/bootstrap-cpp20-engine`.
- Main remains `165c5038336887116d69160b0d8e5a1a5ef59d16`.

Completed ownership/baseline analysis, measured journal improvement, failure-atomic
implementation, independent byte/state/differential controls, observed-readiness
refusal expansion, replay/recovery review, local platform/package qualification,
full supported regression matrix, and adversarial audit. The final documentation
SHA and clean-tree verification are reported after pushing; this document cannot
self-include its own Git hash. Local final-delivery evidence binds that SHA.

Supporting documents: [baseline](PHASE5_BASELINE.md),
[baseline evidence](PHASE5_BASELINE_EVIDENCE.json),
[storage design](PHASE5_JOURNAL_DESIGN.md),
[adversarial audit](PHASE5_ENGINEERING_AUDIT.md), and
[complete structured results](PHASE5_ENGINEERING_EVIDENCE.json).
Raw logs, JUnit, artifacts and controller outputs remain privately under
`build/phase5/evidence`. No binaries, environments or raw market data are committed.

## 2. Journal ownership, size and optimization

Framing/decoding own bounded wire values. Context owns source directory/lifecycle/
match state and prepares atomic deltas. Reconstruction owns two native replay books
and source receipts. Replay owns its book, cursors, retained journal and allocator
association. Research snapshots/canonical exports are owned copies with run/prefix
lineage. Trusted-start restart rebuilds those accepted states; it is not disk
persistence, a full ITCH seed or a crash-safe hot-recovery mechanism.

The original15,944-byte JournalEntry contains a12,208-byte MarketEvent and a3,728-byte
optional RestartPlan, plus disposition/alignment. The event contains5,576-byte
Metadata and a6,632-byte variant dominated by a6,624-byte inline Snapshot. These
are measured GCC/Clang x86_64 ABI sizes, not portable wire sizes or heap totals.

Only reset records need restart plans. The private journal now stores an owned
event/disposition and optional stable plan index, with successful reset plans in a
separate PMR vector. Ordinary record size is **12,232 bytes**, saving3,712 bytes
(**23.2815%**). The public logical JournalEntry remains15,944 bytes; diagnostics
and benchmark output explicitly distinguish logical DTO from physical storage.
ReplayEngine grows32 bytes (14,776→14,808) for the second PMR vector.

Both reserves happen before native mutation; statically nonthrowing value appends
follow native success. The unchanged1–100000 journal cap bounds each vector.
Indices remain stable across growth and moves. Canonical v1 resolves each index
back to its exact owned plan; no provenance interning, payload compression,
metadata loss, archive eviction or new persistence format is introduced.

## 3. Before/after memory and performance

The controlled journal probe uses only authored status observations and explicit
resets, isolating journal PMR growth from resting-order allocations. Lengths
128/512/1001/1024/4096 × no-reset/1-in64/all-reset populations ×3 measured processes,
with one separate warmup per case: **45 before +45 after runs**. Independent integer
accounting reconciles used/capacity bytes and zero live allocations after destruction.

| 1,024 accepted events | Before live PMR | After live PMR | Before peak PMR | After peak PMR | Before/after allocations |
|---|---:|---:|---:|---:|---:|
| No resets |16,327,072|12,525,984|24,490,400|18,788,768|12 /12|
| Reset every64 |16,327,072|12,585,504|24,490,400|18,818,528|28 /33|
| All resets |16,327,072|16,335,264|24,490,400|20,693,408|1,036 /1,047|

All-reset used pairs cost8 extra bytes/event on this ABI; archive spare capacity
and additional reserve calls are genuine tradeoffs. Thus this is not a universal
retained-memory reduction. At4,096 ordinary events, live PMR falls65,307,040→
50,102,688, peak97,960,352→75,153,824, and median process RSS67,162,112→51,949,568
bytes. Ordinary allocations remain14. At100,000 records, physical ordinary element
payload is1,223,200,000 bytes per book rather than1,594,400,000; metadata, snapshot,
vector slack, books/context/receipts and transient copies still require substantial
resources. The optimization does not make a full historical workload feasible by
itself.

Journal-probe elapsed medians include create/apply/validate/destroy, not isolated
insertion. At1,024 no-reset events:19,166,623→17,699,463ns; at4,096:67,857,079→
71,398,125ns. The latter after range61,222,392–83,124,933ns illustrates shared-host
variation; no universal speedup is claimed. The deterministic byte reduction,
bounded complexity and equivalence gates justify the repair independently of
these noisy timings.

Six additional sequential GCC/Clang Release probes ran after regression/package
jobs finished. Fixture hashes, source/native counts and receipt identities match
the existing Phase4 baselines; all tracked memory is released. Each timed batch
uses two warmups and seven repetitions; query/restart profiling has its own stated
non-timing failure sweep.

| Equivalent workload | Old peak PMR | New peak PMR, both compilers | Current GCC /Clang records/s |
|---|---:|---:|---:|
| Two-book reconstruction128 |20,822,320|16,070,960|97,851.2 /105,590|
| Gzip streaming128, fragment17 |20,865,488|16,114,128|75,696.3 /81,402.5|
| Profile128 first pipeline |42,722,343|33,219,623|Not a timing benchmark|
| Profile128 query/restart coexistence |77,281,358|60,176,462|Not a timing benchmark|

Current profile RSS:65,826,816 GCC /65,851,392 Clang bytes. Both report2,757 allocations,
45 actual query allocation-failure sites and zero tracked bytes after destruction.
Under the16MiB PMR cap, the accepted prefix changes515→516 and native512→513; this
is an intentional consequence of fitting more state, with explicit incomplete
accounting. The forced journal cap remains2,049 accepted/2,046 native. Full valid
fixture hashes remain unchanged. Do not compare peaks of different accepted
prefixes as if they were the same workload.

Raw elapsed distributions, exact commands, binary/code hashes, fixture identity,
compiler/build configuration and RSS are in the evidence. Host: Xeon Platinum8573C,
five affinity CPUs, quota equivalent to four CPUs. PMR excludes allocator headers
and fragmentation; sizeof excludes separately allocated data. RSS includes the
runtime and may include a pre-exec parent floor in small wait4 samples. No heap
fragmentation, isolated journal latency, exchange tail latency or production
throughput is inferred. Old combined timings are historical equivalent-fixture
observations, not a randomized same-session causal experiment.

## 4. L3 and recovery findings

The [observed contract](OBSERVED_L3_READINESS_CONTRACT.md) now explicitly records
the Phase5 prerequisite review. Current reconstruction still requires authored
complete synthetic-empty evidence. A native complete-order snapshot cannot seed
ITCH directory/retired-reference/match/global context or authenticate a session.
Neither byte-zero, S:O, market-open time, directory/status spins nor aggregate
snapshots prove a complete initial L3 state.

The existing machine gate remains fail-closed. Twelve unittest methods now include
120 contradictory claim combinations and2,048 seeded adversarial documents
(seed559173), with deterministic refusal and immutable input checks. All-positive
caller claims also remain BLOCKED: observed adapter, complete native/context seed
and independent observed-book oracle do not exist. These are refusal tests, not
proof of real source completeness or third-party claim authenticity.

Order identity, FIFO, partial execution/cancellation, replace retirement/priority,
external hidden/cross/broken-trade observations, source sequencing, optional clock
policy, all-stream recovery boundaries and provenance checks were preserved and
regressed. Native replay pins declared stream identity/version/scope and retains
metadata; it is not an archive authentication service. ITCH context manifest
conflicts and research-export contradictory digests remain separately checked.

New mixed replay fixtures independently check active IDs, quantities, totals,
sequence and journal count after every event. All128 canonical prefixes match a
frozen pre-change executable. Those hashes are differential evidence; the separate
map-based state model and existing independent L3 oracles supply independent checks.
New reset allocation injection reached16 sites versus11 before; existing replay
apply/recover/reset/canonical/depth injection reached32. Failures preserve complete
canonical state; successful retries apply exactly once, moves retain archive
ownership and all tracked bytes/blocks are released.

No new production correctness defect was reproduced in this audit. The measured
storage inefficiency was repaired. Existing corrupt/truncated input, source gaps,
duplicates, invalid snapshots, contradictory metadata, resource exhaustion,
interruption/publication and deterministic restart regressions all remain required.
No assertion was weakened, sanitizer suppressed or mandatory test disabled.

## 5. Executed independent validation

| Configuration | Passed CTest outcomes | Failed /skipped /disabled |
|---|---:|---:|
| GCC14.2 Debug |154|0 /0 /0|
| GCC14.2 Release |154|0 /0 /0|
| GCC14.2 ASan+UBSan |154|0 /0 /0|
| Clang19.1.7 Debug |154|0 /0 /0|
| Clang19.1.7 Release |154|0 /0 /0|
| Clang19.1.7 ASan+UBSan |154|0 /0 /0|
| Python3.12.14 Debug |157|0 /0 /0|
| Python3.12.14 Release |157|0 /0 /0|
| Python ASan+UBSan |158|0 /0 /0|
| **Total** |**1,396**|**0 /0 /0**|

The sanitizer Python row includes the live LSan control. All eight existing wire,
context, L3, streaming, demonstration, H/Y, administrative and auction canonical
hashes are unchanged in all nine rows. New journal memory/model/allocation/
pre-optimization equivalence CTests pass in every row. Current CI-summary positive,
wrong-hash and wrong-count controls pass locally (six controls); they are not hosted
GitHub execution. The frozen code manifest's13 implementation/test/build files
match commit6eee608 exactly; no final engine change followed these runs.

Both checkout-built and source-archive-built CPython3.12 Linux x86_64 wheels passed
fresh installed consumers:8 interface +6 export cases each, **28 total**, with
unchanged deterministic Python example SHA256. Three packaging contamination
regressions passed. The tested source archive contains **301** safe, intended,
byte-identical regular members and required trees; all its non-documentation
members still match delivered implementation. Source/consumer paths, hashes and
commands are retained. Builds occurred before the final code commit, so configured
Git metadata identifies the then-current baseline checkpoint; source-file hashes,
not that metadata alone, establish delivery equivalence.

Final clean-commit source-distribution reproducibility is checked separately by
two fixed-SOURCE_DATE_EPOCH sdist builds after documentation push. Their final SHA,
inventory and archive hashes are bound in local `build/phase5/evidence/final-delivery.json`;
they are not recursively embedded in their own source archive. Wheels expose the
same0.1.1 research API/schema1.0; no new ITCH Python interface or stable C++ binary
ABI is claimed. C++ consumers must rebuild the changed ReplayEngine layout.

## 6. Deployment, dependencies and readiness

| Area | Actual evidence /decision |
|---|---|
| Linux x86_64 |Executed GCC/Clang and CPython3.12 Debug/Release/sanitizers and installed-wheel checks.|
| ARM64 native |NOT RUN: no authorized native ARM executor available.|
| ARM64 cross/emulation |NOT RUN: no aarch64 compiler, qemu-aarch64 or registered binfmt handler found. Not equivalent to native qualification anyway.|
| Hosted Actions |gh API exit1, `Get https://api.github.com/.../actions/runs?...: Forbidden`. No run ID, authenticated origin status, tested head or conclusion obtained. Git push success is separate.|
| Dependencies |Existing12-version lock retained; pybind11 2.13.6, scikit-build-core0.11.6, jsonschema4.23.0; native zlib1.3.1 unchanged. Python fixture zlib/runtime identities recorded separately. No new dependency.|
| Portability/security |No manylinux, other Python ABI, Windows/macOS, independent-machine or provider advisory clearance inferred. Existing RC13/16/17 and RC18 boundaries remain.|

Current RC01–RC27 decisions remain the Phase4 overlay:18 scoped PASS,7 BLOCKED,
1 NOT RUN,1 OUT OF SCOPE. This phase strengthens memory/correctness evidence but
does not close external gates.

1. **Private synthetic evaluation:** GO within tested profiles and resource bounds.
2. **Formal private candidate closure:** BLOCKED pending independent-machine,
   hosted CI, security applicability and owner/distribution evidence.
3. **Historical ITCH compatibility:** profile-specific retained-spec synthetic
   support plus prior tiny S/R/H/Y observations, not full2019 certification.
4. **Observed-market L3 validation:** NO-GO pending valid complete initial state,
   authenticated complete capture, observed adapter and independent reference.
5. **Production execution:** out of scope; no production readiness claim.

November5 remains the private synthetic target, November12 contingency. On the
October23 client date these are13 and20 calendar days away. Local engineering
qualification is complete; external evidence turnaround controls formal closure.
No guaranteed date follows from local test success.

## 7. Changed-file inventory and next milestone

New: `benchmarks/journal_memory_probe.cpp`, `tests/test_journal_storage.cpp`,
`scripts/check_journal_storage.py`, and under docs: `PHASE5_BASELINE.md`,
`PHASE5_BASELINE_EVIDENCE.json`, `PHASE5_JOURNAL_DESIGN.md`,
`PHASE5_ENGINEERING_AUDIT.md`, this report and `PHASE5_ENGINEERING_EVIDENCE.json`.

Modified: `.github/workflows/ci.yml`, `CMakeLists.txt`, `benchmarks/CMakeLists.txt`,
`benchmarks/book_benchmark.cpp`, `benchmarks/itch_profile_probe.cpp`,
`benchmarks/itch_reconstruction_benchmark.cpp`, `benchmarks/itch_streaming_benchmark.cpp`,
`include/gig/replay/replay.hpp`, `src/replay/replay.cpp`,
`tests/test_observed_readiness.py`, `docs/OBSERVED_L3_READINESS_CONTRACT.md`,
`docs/OVERNIGHT_ENGINEERING_PROGRESS.md`, `docs/RC_OWNER_ACTIONS.md`,
`docs/REPRODUCIBILITY.md`.

No matcher, execution/TCA, event schema, ITCH decoder/normalizer, raw market data,
GIG Quant Terminal, main branch or prior audit/remediation evidence was modified.
No merge, tag, release, broker connection or paid resource was created.

Use [reproduction commands](REPRODUCIBILITY.md) to run the new bounded journal
experiment and frozen-prefix comparison. Recommended next milestone: obtain an
already-authorized independent Linux runner with accessible Actions evidence and
provider dependency applicability review. Separately design and authorize any
observed pilot only after initialization/reference/resource prerequisites are met.
Further snapshot/metadata compaction needs a new measured equivalence plan; it is
not silently started here. No background work continues after this session stops.
