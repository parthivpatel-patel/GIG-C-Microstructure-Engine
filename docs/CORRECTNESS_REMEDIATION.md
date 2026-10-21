# Correctness remediation — audited issues and deterministic fixture follow-up

Scope: the four reproduced defects and selected-compiler metadata flaw authorized
following INSTITUTIONAL_ENGINEERING_AUDIT.md, plus the explicitly authorized RNG
evaluation-order repair when this session resumed. No journal optimization, new development
phase, live/broker integration, Terminal change, main merge or release publication.
Starting branch: `feat/bootstrap-cpp20-engine`; local and remote starting SHA:
`ccc86d3822e4cfddd4bcd2a086dd7e779602a91d`. Main remains
`165c5038336887116d69160b0d8e5a1a5ef59d16`.

The original uncommitted audit was copied before edits and is preserved byte-for-byte
as the prefix of its now-annotated file. Original SHA256:
`4c3837cd33a1be9621716d7073eb8d2e32a6624c39b624cf7824a7545e819889`.
All target reproductions and cited source paths were reviewed; all five findings
reproduced. No reported target defect had to be dismissed as unreproducible.
Audit source ranges retain baseline meaning; its addendum identifies targeted repairs
without rewriting historical findings or claiming all25 recommendations are closed.

## Root causes, repairs and before/after evidence

### 1. Missing maker reports — audit F01

Root: `src/simulation/simulator.cpp`, State::arrive/report, previously scheduled a
fill ClientReport only for incoming.id. Resting makers' quantities changed in exchange
truth without a delivered client fill. All submitted orders were modeled clients;
there was no external/background ownership flag legitimizing the omission.

Repair: schedule a maker report alongside the original taker report, sharing the
fill index, quantity and one `reported_at`/execution-latency draw. Taker-first stable
tie order is preserved. No new RNG draw changes subsequent arrival/report latency.
All scheduling/delivery remains inside the existing staged State clone and owner
swap, including the second report's queue/report capacity and allocation failures.
No storage redesign or new participant infrastructure was introduced.

| Case | Before | After |
|---|---|---|
| Maker1 sells10@100, taker2 buys10 | Only order2 gets a10-lot fill report | Order2 and order1 each receive10 lots, same fill/time |
| Maker1 fully consumed, maker2 partially consumed by15-lot taker | Client channel misses both maker updates | Maker fills10/5 and taker fills15 reconcile |
| Execution latency5ns, ACK7ns | Taker report precedes ACK | Both side reports arrive at5; ACKs at7; no early fills |
| Maker cancellation after partial fill | Exchange residual correct, report information incomplete | Delivered acceptance/fill/cancel deltas reconcile each order to zero |
| Insufficient queue/report capacity | Previously fewer report slots needed | Whole command rejects atomically rather than dropping maker reports |

Failing-before regression: new `simulation.reports` failed1/1 against original source.
After repair it passed; all six simulation CTest outcomes, including the expanded
1,000-state independent matching/cancel/client-report oracle, passed. The oracle now
compares report IDs, kinds, reasons, quantities and fill indices after each command,
not only orders/fills/ledger. Existing latency/FOK/IOC/post-only/fault tests remain.
Real allocation failure positions reached29 in simulation (previous28), with96
checks in the direct faults run. Queue max_events2 and delivered max_reports3
reproductions prove second-report failure rolls back canonical state and invariants.

Four-seed jitter comparison (5/42/1729/2027) against the preserved0.1.0 installed
extension produced identical exchange orders/fills, times, conservation and original
taker/other client reports after removing only new maker fill reports. Both outputs
SHA256: `318fbfb3dba45089ea263871cb48eac89d93186ac0e01a74599e157a49efc592`.

Intentional compatibility change: canonical simulation identifier is
`gig.simulated.v2;`; package/CMake/binding patch version0.1.1. Wire schema1.0 fields
and enum codes are unchanged. There are now two side reports per economic fill;
filter by order before summing. Exchange fills still represent one trade, and
executed_sides still counts2*q. Existing tight report/queue budgets can now reject
runs sooner; this is preferable to silent missing reports. Maker and taker latency
is a shared synthetic assumption, not independently calibrated participant latency.

### 2. TCA fill maximum — audit F04

Root: `src/execution/execution.cpp`, transaction_costs row validation, checked positive
quantity and aggregate target, but omitted the per-fill rules.maximum_quantity bound.

Repair: include that bound in the existing `cost.fill` invalid_range guard before
cost output allocation. Do not cap the parent target or sum of valid fills by this
per-fill limit. No financial formulas or accepted valid values changed.

Before: an11-lot supplied fill under maximum10 and target20 produced a report with
filled11/unfilled9. After: invalid_range, field `cost.fill`, row index0. Native
`execution.cost_limits` failed1/1 before the guard and passes afterward. It covers
buy/sell and maker/taker cost perspectives, quantity0/max/max+1/u64 maximum,
two valid10-lot fills against target20, unmodified input records, and zero PMR
allocation attempts for invalid input even when the allocator is armed to fail.
Existing output allocation-failure and independent2,600-case execution/math checks
pass. Integrated execution fault sweep now reaches44 allocation positions, planner6;
existing single TCA output allocation failure remains covered.

### 3. Missing retained VWAP profile — audit F02 targeted scope

Root: `python/gig_microstructure/__init__.py`, export_run, checked execution run/oracle
labels but not the profile input identity. verify_export verified file hashes/schema,
without running export's reference checks.

Repair: one `_validate_export_references` function is used before export creates a
directory and after verifier input-byte integrity checks, while output documents are
streamed through read-only verification. VWAP (forecast and hindsight/oracle) requires
a known retained profile identity; POV volume-point source identities also resolve.
TWAP has no invented profile dependency. Existing seed/run/schema/benchmark checks
are shared by writer and verifier rather than diverging.

Before: a plan naming MISSING-PROFILE plus only unrelated bytes exported and verified
complete=true. After: `export.profile_artifact_not_retained`, before directory creation;
POV equivalent returns `export.volume_artifact_not_retained`. Three new profile/POV
regression methods all failed before repair and pass after it. Tests include valid
forecast/oracle exports, oracle labeling, valid/absent POV sources, TWAP absence,
and read-only verification of a profile reference changed while manifest/file hashes
are recomputed self-consistently. Retained profile bytes are evidence of identity,
not proof that they generated inline weights or that the forecast was genuinely ex ante.

### 4. Contradictory retained dataset digest — audit F03 targeted scope

Root: exporter validated bytes against manifest input hashes and checked an event's
source identity existed, but never compared known dataset/parent digests with the
manifest's hash for that same retained identity. Verifier lacked the cross-check too.

Repair: shared reference validation compares known dataset and parent digests with
the corresponding retained input hash, already checked against bytes. A retained
artifact identity names those exact bytes. A different normalized/aggregated scope
requires another identity and explicit parent mapping. Unknown hashes stay unknown;
no value is invented, silently substituted or used as an authentication assertion.

Before: declared SHA256 of64 zeroes and actual bytes with a different digest passed
complete export/verification. After: `export.dataset_digest_mismatch` or
`export.parent_digest_mismatch`. Three new digest methods had four failing subtests
before repair (dataset/parent in writer/verifier); matching/unavailable hashes already
passed and continue to pass. All six export-contract methods now pass. Invalid
writer inputs create no output directory. Verifier tests recompute file/manifest
hashes before supplying contradictions, and compare all directory file bytes before/
after rejection to prove no writes. Existing corrupt/incomplete/no-overwrite and
intentional os.link failure tests remain active.

### 5. Selected-compiler metadata — audit F18

Root: `scripts/run_engine_baseline.py` accepted --build-dir but populated the compiler
field using ambient `c++ --version` rather than the selected build's compiler.

Original full Clang smoke run reported `c++ (Debian14.2.0-19)14.2.0` while its
compile command used `/workspace/gig-clang/bin/clang++`. The actual-run manifest
regression rejected that original output with exit1 before repair.

Repair: `compiler_metadata` locates the selected CMake version directory from cache
MAJOR/MINOR/PATCH, reads generated compiler executable/optional first arguments,
ID and version, records metadata SHA256 and queries that exact executable. Missing
selected metadata is an error, never a fallback to PATH's c++. Compile commands,
flags, binary hashes and CPU/OS fields remain recorded. The legacy
run_research_benchmark.py now reuses the same selected-build helper; the older
payload/Phase2 runners already queried their configured CMake compiler. Benchmark metadata has
additive compiler identity fields; research wire schemas are unchanged.

Tests cover GNU/Clang metadata fixtures, executable paths with spaces and missing
metadata rejection. Actual GCC and Clang runner manifests now report the selected
/usr/bin/g++14.2.0 / GNU and workspace clang++19.1.7 / Clang respectively despite
ambient c++ being GCC. One development CLI checker initially required the literal
word GNU in the GCC banner; it was corrected to accept GNU/GCC/g++ aliases while
still requiring the configured compiler ID. Both actual-run checks then passed,
and the full nine-configuration suite was rerun after that checker correction.

### 6. Compiler-dependent fixture RNG — authorized resume follow-up

Root: `fixtures/synthetic/phase2_workload.hpp` called random() twice in one add(...)
argument list. The language does not define which argument is evaluated first.
The calls are indeterminately sequenced in C++20, not undefined behavior, but assign
successive random draws to different fields under the tested GCC and Clang builds.
For seed1, count1 the new Clang regression originally observed quantity65 instead
of37 from the fixed-order reference. Existing compiler-specific baseline input
hashes were genuinely different, not a defect in replaying identical input.

Repair: draw quantity then price in separate full statements. This chooses and
specifies one portable order while preserving established GCC field values and
the side/ID/price-range/quantity-range/count/seed semantics. Fixture lineage now
names `phase2-benchmark-generator-v2`, version2. Dataset/stream versions, the raw
workload_version field and the internal gig.phase2.workload.v2 container advance
consistently; the Phase2 benchmark manifest records generator-v2/dataset2. This intentionally changes canonical
fixture metadata and hashes even where GCC prices/quantities remain unchanged.
Historical v1 baseline files are preserved, not relabeled as v2 measurements.

A new `benchmark.fixture_reference` regression compiles the same source with each
toolchain and compares16 cases (four seeds, including UINT64_MAX; counts1/16/512/2048)
against a separately implemented Python fixed-width xorshift64 and explicit draw
order. It verifies IDs, sides, prices, quantities, generator identity/version, and
that add/cancel/execution/replay payload identities remain coherent. It failed1/1
under original Clang and passes after the repair. Final compiler matrix and full
canonical workload comparisons are recorded below. The existing benchmark smoke
and independent book oracle remain active; no journal representation changed.

## Validation matrix and independent evidence

Linux x86_64, GCC14.2.0, Clang19.1.7, CMake3.31.6, CPython3.12.14. Every selected
binary tree was rebuilt after source changes with warnings as errors. The original
five-repair matrix passed64/64 native,67/67 Python and68/68 Python sanitizer; a new
full matrix includes the additional RNG fixture regression after the resume repair. Counts below are CTest
outcomes; methods/subtests inside Python groups are not represented as extra CTests.

| Configuration | Passed | Failed | Errors | Skipped | Disabled |
|---|---:|---:|---:|---:|---:|
| GCC Debug | 65 | 0 | 0 | 0 | 0 |
| GCC Release | 65 | 0 | 0 | 0 | 0 |
| GCC ASan+UBSan | 65 | 0 | 0 | 0 | 0 |
| Clang Debug | 65 | 0 | 0 | 0 | 0 |
| Clang Release | 65 | 0 | 0 | 0 | 0 |
| Clang ASan+UBSan | 65 | 0 | 0 | 0 | 0 |
| Optional Python Debug | 68 | 0 | 0 | 0 | 0 |
| Optional Python Release | 68 | 0 | 0 | 0 | 0 |
| Optional Python ASan+UBSan | 69 | 0 | 0 | 0 | 0 |

Python ASan retains the prior qualified scope: ASan/UBSan and active-interpreter
LSan checks plus a positive intentional-leak control. Late CPython-finalization
leak coverage remains unverified. Native tests retain normal exit-time LSan;
no new suppressions or disabled checks were introduced.

Independent checks remain enabled: strong numeric conversions/boundaries,20,000
book operations,2,650 Fraction book cases,2,000 Fraction flow cases,1,000 matching/
cancel/client-report states,2,600 allocation/participation/cost cases and300 Python
Fraction roundtrips. Replay ordering, reset/recovery, canonical output and real PMR
failure injection are preserved. The report does not infer exhaustive correctness
from fixed seeds. Targeted Python-only export isolation initially used the patched
facade with the preserved baseline extension; final matrix/package tests use the
rebuilt0.1.1 native extension.

Native application canonical replay SHA256 remains identical across all six native
builds: `bee1448c29fc918911c48e62a6f6060d09d3e53f0938a02f4e4063b49d362979`.
Private0.1.1 wheel and sdist are local artifacts only, never published. Installed
consumer checks use their own venv and confirm installed import/native paths.
Seven interface tests and six export-contract tests pass against the new wheel;
the self-contained Python example also runs and checks both counterparties.
The final source archive was unpacked and rebuilt offline into a wheel, then
installed in the separate consumer venv:7/7 interface and6/6 export-contract tests
passed, with0 failures/skips. All14 schema files retain their original bytes and
third-party notices are present. The example and four-seed jitter comparison passed.
Final runtime/fixture/test sources in that archive match the implementation commit;
subsequent changes are documentation/evidence only. No release portability or binary
reproducibility claim follows from a local wheel build.

## Benchmark reproducibility and an isolated additional limitation

Corrected GCC and Clang development smoke runs (dirty=true, due preserved audit and
remediation work) reran64/64 native tests and validated all benchmark checksums.
Their timing samples are development checks, not performance evidence: package
build activity overlapped part of these smokes. Final clean-checkpoint experiments
run sequentially after builds stop and are identified separately in the evidence.

Before the RNG follow-up, each compiler reproduced its own book/replay fixture.
The v2 fixture intentionally changes that group’s metadata and input/replay hashes.
Book-analytics and flow canonical artifacts retain their prior hashes. Simulator and execution-parent canonical artifacts
change intentionally to v2 with the additional maker reports; their mathematical
checksums remain132096 and6480000. Book analytics/flow expected checksums remain
40000000/2400000. Cross-compiler simulator/execution/book-metric/flow fixed-fixture
artifacts agree.

The initial cross-compiler book comparison failed because of the v1 generator
argument-order issue. This was first isolated with compiler-specific pre/post
hashes; the resumed user instruction then authorized its repair. Generator v2 now
specifies draw order and records revised provenance. Final full-run cross-compiler
hash comparisons, including book input and replay, passed and are archived in the
completion evidence. Old GCC hashes7d16448f…/09dfc157… and old Clang
fb99c0d1…/7486fe5e… remain historical v1 evidence, not v2 expectations.
No cross-version/cross-workload speedup is claimed.

## Journal memory finding and separate proposed plan

Measured JournalEntry size remains15,944 bytes on the existing GCC x86_64 ABI;
no journal/container/allocator optimization was made. The4,096-entry element
storage calculation remains65,306,624 bytes before growth/driver/book/export costs.

Separate benchmark-gated proposal, requiring later authorization:

1. Record retained and peak bytes, allocation counts, VmHWM and throughput/service
   distributions over identical bounded histories and churn patterns at several N.
2. Profile common event headers versus rare inline snapshot/restart payload cost.
3. Evaluate one ownership-preserving representation change, such as separately owned
   uncommon payloads; retain the current implementation/reference as an oracle.
4. Require canonical/semantic equivalence, malformed-input and allocation-failure
   coverage, no borrowed dangling data, and measured before/after memory/performance
   evidence. Set budgets from an agreed research workload, not an invented firm SLA.

No such optimization or additional roadmap implementation starts here.

## Remaining risks and acceptance boundaries

All five targeted repairs have original failure evidence and passing regressions.
Broader audit findings remain: native PMR lifetime obligations, large journal/state
clones,64-order recovery snapshots, trusted completeness/clock/availability assertions,
uncalibrated queue/latency/impact models, finite synthetic tests, no raw real-market
adapter or empirical calibration, no crash-safe persistent restart, no production
risk/operational system, and no actual Terminal adapter. Export consistency is not
proof of arbitrary parent-graph completeness, profile derivation, authenticity or
licensing. The additional compiler-dependent fixture is repaired as documented above; its
portable v2 ordering now has an independent reference and explicit provenance.

Native ARM64/cross-compilation and observed-market validation were not performed.
Hosted Actions requires separate evidence; local passes are not hosted CI success.
Other CPython versions/platforms and late interpreter-finalization leaks remain
unverified. No new dependency, live connection, deployment, release or paid resource
was introduced. Stop after this correctness remediation.

## Commit traceability, file inventory and durable evidence

Verified implementation checkpoint: `26514722c878d9011d36258fd80a95ab794d8246`,
committed and normally pushed to the existing development branch. Git ls-remote
returned that exact SHA; main remained unchanged. The final evidence/report commit
is a descendant containing documentation and evidence only; its exact SHA is reported
in the completion response. A document cannot embed its own commit SHA. Historical
baselines and reports have not been rewritten.

Durable evidence: [remediation-validation.json](baselines/remediation-validation.json).
It records the nine final JUnit/log hashes and counts, six original-red regression
logs, targeted greens, installed-wheel/source-archive hashes, compiler identities,
canonical artifacts, unchanged application hashes, audit preservation and limits.
Raw evidence remains in ignored `build/remediation/`; recorded hashes are identifiers,
not a claim that ignored files are available from a fresh clone. Regenerate with the
commands below. Original red evidence remains locally available and its hashes are
retained; the historical baseline can also be inspected without changing this branch.

### Final clean-checkpoint experiments

All runners completed at source commit26514722c878d9011d36258fd80a95ab794d8246
with dirty=false, serially on the shared host. GCC and Clang runners each reran65/65
CTest outcomes; Python reran68/68; the legacy book runner and Phase2 runner each
reran65/65. All had zero failed/errors/skipped/disabled. Correctness checks and
expected checksums passed. Full manifests include raw service samples, build commands,
executable hashes and qualified memory measurements; durable evidence retains their
hashes, summaries and canonical artifact identities. No timing threshold or speedup
claim is inferred from these shared-host observations.

```sh
export PATH=/workspace/gig-tools/bin:$PATH
python scripts/run_engine_baseline.py --build-dir build/phase9-clean-release --output-dir build/remediation/verified-gcc
python scripts/run_engine_baseline.py --build-dir build/phase9-clang-release --output-dir build/remediation/verified-clang
python scripts/benchmark_python.py --build-dir build/python-release --output-dir build/remediation/verified-python
python scripts/run_research_benchmark.py --component book --output build/remediation/verified-legacy-book.json
python scripts/run_phase2_benchmark.py --build-dir build/phase9-clean-release --output-dir build/remediation/verified-phase2 --orders 32 --repetitions 2 --warmup 1
python tests/test_benchmark_metadata.py --manifest build/remediation/verified-gcc/manifest.json GNU
python tests/test_benchmark_metadata.py --manifest build/remediation/verified-clang/manifest.json Clang
```

Use new output paths to rerun: runners intentionally refuse to overwrite evidence.
Their next code_sha will identify the current clean documentation descendant.
Build each matrix tree with its existing compiler/sanitizer configuration, then use
`ctest --test-dir <tree> --output-on-failure --no-tests=error --output-junit <new.xml>`.
The exact selected source files are unchanged after the tested implementation commit.
For package reproduction use the source-build/consumer commands in REPRODUCIBILITY.md
and also run `tests/test_export_contracts.py` with the installed consumer interpreter.
No package upload or release was performed.

All five GCC/Clang artifact sets are equal. Book metrics and flow hashes are unchanged
from the historical baseline. Simulation and execution-parent hashes intentionally
change for maker reports/v2; book/replay hashes intentionally change for generator,
dataset and container v2 provenance. Representative final SHA256 values:

| Artifact | SHA256 |
|---|---|
| Book workload | `5acd23e7b7ae0f5e3baed41b77cdfeb39c75ace3f7bba8ebd43751345cb57911` |
| Replay | `d83d57a15e35fb499429bcacb3967ffb12a7b782b6f9f6d071aaa87b014f8979` |
| Simulation | `7877560d4add7189bbca57b42f71207f0424ae762fe190dcbd3ab7c37123fbd0` |
| Execution parent | `4f7bc286df9da64295f086dcd16269e7c3ac5757d0e574c2cc4dac59019e8c95` |

A final512-order, seed1729 dump agrees byte-for-byte between compilers; prices,
quantities, IDs and sides equal the original GCC dump when excluding the explicitly
versioned header. The separate16-case arbitrary-precision fixture reference passed
in every matrix tree. A manual evidence invocation initially swapped count/seed;
correcting that invocation produced the documented512/1729 comparison without any
implementation change or suppressed regression.

Hosted Actions status is **UNVERIFIED**. The exact-commit GitHub API request failed
with curl56, CONNECT tunnel proxy403 (HTTP000). This is unavailable evidence, not a
failed Actions result or a successful run. Native ARM64, real-market calibration,
other Python platforms and late CPython-finalization leak coverage remain unverified.

### Remediation acceptance

- [x] Preserve baseline history, development branch and the original audit verbatim.
- [x] Reproduce all five original issues, add red/green regressions and minimal repairs.
- [x] Repair the additionally authorized RNG fixture sequencing with explicit v2 provenance.
- [x] Pass six native and three optional Python configurations; no failures/skips.
- [x] Preserve replay determinism, independent numerical references and atomicity checks.
- [x] Validate installed0.1.1 source-rebuilt consumer, example, schemas and export contracts.
- [x] Verify clean-checkpoint canonical artifacts across GCC/Clang and selected compilers.
- [x] Record journal memory and a separate benchmark-gated plan; do not optimize it.
- [x] Push implementation normally and verify exact remote SHA; final report commit follows.
- [ ] Hosted CI success: unavailable, not claimed.
- [ ] ARM64/observed-market/production qualification: outside this local evidence.

### Complete changed-file inventory versus baseline

- `.github/workflows/ci.yml`
- `CMakeLists.txt`
- `README.md`
- `benchmarks/book_benchmark.cpp`
- `docs/BENCHMARK_METHODOLOGY.md`
- `docs/CORRECTNESS_REMEDIATION.md`
- `docs/INSTITUTIONAL_ENGINEERING_AUDIT.md`
- `docs/LIMITATIONS.md`
- `docs/PHASE_2_BENCHMARKS.md`
- `docs/PHASE_5_CONTRACTS.md`
- `docs/PHASE_6_CONTRACTS.md`
- `docs/PHASE_8_INTERFACE.md`
- `docs/REPRODUCIBILITY.md`
- `docs/VALIDATION.md`
- `docs/baselines/remediation-validation.json`
- `examples/python_research.py`
- `fixtures/synthetic/phase2_workload.hpp`
- `include/gig/simulation/simulator.hpp`
- `pyproject.toml`
- `python/bindings/module.cpp`
- `python/gig_microstructure/__init__.py`
- `scripts/check_book_benchmark.py`
- `scripts/check_simulation_reference.py`
- `scripts/check_workload_reference.py`
- `scripts/run_engine_baseline.py`
- `scripts/run_phase2_benchmark.py`
- `scripts/run_research_benchmark.py`
- `src/execution/execution.cpp`
- `src/simulation/simulator.cpp`
- `tests/test_benchmark_metadata.py`
- `tests/test_execution.cpp`
- `tests/test_export_contracts.py`
- `tests/test_python.py`
- `tests/test_simulation.cpp`
- `tests/test_workload.cpp`
