# Institutional engineering gap audit — source-level review

Baseline: `ccc86d3822e4cfddd4bcd2a086dd7e779602a91d`.
Repository: `parthivpatel-patel/GIG-C-Microstructure-Engine`.
Branch: `feat/bootstrap-cpp20-engine`. Audit performed in the existing Linux x86_64
Codex environment on 2026-10-21. All line ranges below refer to baseline source,
not generated build copies. This report is the only requested repository change;
reproductions, logs and measurements are ignored artifacts under
`build/institutional-audit/`. No implementation, commit, push, merge or release was
performed for this audit. GIG Quant Terminal was not inspected or modified.

## Executive assessment

This is a substantive deterministic C++ research prototype, not merely a scaffold.
Strong units, an order-level reconstructed book, scoped replay/recovery, exact
rational calculations, a separate synthetic matcher, execution allocation, TCA and
optional Python interchange exist in source and execute. Standard containers,
single-owner mutation, explicit unavailable states, independent mathematical
references and real allocation-failure injection are defensible engineering choices.
Keeping reconstruction separate from synthetic matching is particularly important.

The evidence supports bounded synthetic correctness for tested contracts. It does
not establish exchange fidelity, empirically useful predictions, calibrated fill
probabilities, production throughput, crash recovery or operational safety. Passing
existing suites is not equivalent to complete verification: this audit reproduced
four uncovered semantic/reporting/provenance failures and identified a separate
latent benchmark metadata defect. No Critical exploit or catastrophic defect was
established; this is not a proof that none exists.

Fix maker-side client reporting, TCA field validation and export reference/digest
consistency first. Then add adversarial cross-boundary tests and address retained
history size before increasing data volume. For interview credibility, a narrow,
reviewable model with strong negative evidence is more persuasive than claiming
that all phases make it an institutional execution platform.

The comparison uses publicly defensible principles: explicit market semantics,
causal information sets, independent verification, controlled measurements,
resource accounting and recoverability appropriate to intended use. It does not
claim access to Citadel Securities, Jane Street or Hudson River Trading source,
proprietary performance targets or internal hiring criteria. No firm-specific
latency threshold or requirement is inferred.

## Method, classifications and limits

Implemented means executable source exists. Partial means some contract or necessary
boundary is incomplete. Missing means no implementation was found in the reviewed
project. Unverified means the assertion needs evidence beyond what this audit
obtained. Not applicable means deliberately outside this offline scope. Severity
reflects consequences if the component is used for its advertised research purpose;
production-only gaps are labeled conditional. A deliberate exclusion is not a
regression defect. Complexity estimates are engineering scope, not calendar promises:
Small = local contract/tests; Medium = coordinated component/interface changes;
Large = new representation, empirical work or operational subsystem.

Source review included `include/gig/`, `src/`, bindings/facade, test/oracle sources,
CMake, workflow, benchmark drivers, schemas, dependency declarations and reports.
Suspicious paths were exercised through the installed compiled Python extension;
its facade matches baseline source. Existing reference algorithms were inspected
for independence and limitations. Reports were treated as claims, not test results.
Independence here means adversarial source review and separate reference calculations,
not third-party certification. This is a targeted manual audit, not formal verification, exhaustive path coverage,
a penetration test or a complete dependency CVE audit.

### Checks actually executed in this audit

Commands used existing trees unless explicitly marked fresh:

```sh
export PATH=/workspace/gig-tools/bin:$PATH
ctest --test-dir build/phase9-clean-debug --output-on-failure
ctest --test-dir build/phase9-clean-release --output-on-failure
ctest --test-dir build/phase9-clean-asan-ubsan --output-on-failure
ctest --test-dir build/phase9-clang-debug --output-on-failure
ctest --test-dir build/phase9-clang-release --output-on-failure
ctest --test-dir build/phase9-clang-asan-ubsan --output-on-failure
ctest --test-dir build/python-debug --output-on-failure
ctest --test-dir build/python-release --output-on-failure
ctest --test-dir build/python-asan-ubsan --output-on-failure
python scripts/run_engine_baseline.py --build-dir build/phase9-clean-release \
  --output-dir build/institutional-audit/native-baseline
python scripts/benchmark_python.py --build-dir build/python-release \
  --output-dir build/institutional-audit/python-baseline
cmake -S . -B build/institutional-audit/fresh-release -G Ninja \
  -DCMAKE_CXX_COMPILER=g++ -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DGIG_WARNINGS_AS_ERRORS=ON -DGIG_BUILD_BENCHMARKS=ON -DGIG_BUILD_PYTHON=OFF
cmake --build build/institutional-audit/fresh-release --parallel 2
ctest --test-dir build/institutional-audit/fresh-release --output-on-failure
build/phase9-consumer/bin/python build/institutional-audit/reproduce.py
```

JUnit/log artifacts include the exact commands' output and counts:

| Actual audit run | Result |
|---|---|
| GCC14 native Debug, Release, ASan+UBSan existing trees | 61/61 each |
| Clang19 native Debug, Release, ASan+UBSan existing trees | 61/61 each |
| GCC optional Python Debug and Release | 63/63 each |
| GCC optional Python ASan+UBSan | 64/64 |
| Fresh out-of-source GCC Release, warnings as errors | 61/61; 43 build steps completed |
| Native/Python benchmark preflight suites | 61/61 and 63/63 |
| Native canonical workload artifacts vs Phase 9 | All identical |
| Python benchmark correctness fields vs Phase 9 | Identical input/result hashes and expected512 remaining lots |
| Targeted R1–R4 reproductions below | Uncovered failures observed despite passing suites |

Zero failed/skipped/disabled CTest outcomes in these runs. Existing sanitizer trees
were rerun, not rebuilt from scratch; only native Release received a new configure/
build tree here. Fresh wheel construction, sdist reconstruction, dependency advisory
queries and non-x86 platforms were not rerun in this audit. Earlier reports of those checks remain historical evidence.
The benchmark runners rebuild their selected trees before testing/timing.

Python sanitizer result is qualified: `scripts/run_python_sanitized.py:13–28`
checks leaks during the active interpreter, with a positive injected-leak control;
`CMakeLists.txt:188–211` configures the scoped GNU/Linux preload and disables the
late exit leak check for those Python commands. Native exit LSan stays enabled.
Late CPython-finalization leakage remains unverified, not a clean exit-leak result.

Hosted checks API probe for the exact baseline failed with curl56, proxy CONNECT403.
Hosted CI is UNVERIFIED, not failed or passed. Git access is a separate capability.
No native ARM64 machine was available; no cross-compilation was performed.

## Complete domain coverage matrix

The numbered findings following this matrix supply remediation, acceptance criteria,
complexity, dependencies and risks. Positive findings' acceptance is preservation
of their existing independent regression checks plus the new negative cases; no
rewrite is recommended merely to appear sophisticated.

| Domain | Highest associated severity | Status and source evidence | Assessment and associated findings |
|---|---|---|---|
| A. Architecture/types/lifetimes | Medium | Implemented: `include/gig/core/numeric.hpp:13–44,46–122,170–219`; `include/gig/replay/replay.hpp:49–72`; `python/bindings/module.cpp:6–28` | Distinct factory-only units, checked arithmetic, deleted replay move assignment, explicit native owner/resource order. Native PMR values are not resource-independent. F16,F22,F25. |
| B. Structures/complexity/allocations | High | Implemented: `src/book/order_book.cpp:12–20,63–110`; `src/simulation/simulator.cpp:29–44,51–56,89–96,110–123` | Map/list/hash book is a useful correctness baseline; synthetic model uses linear scans, vector insertion/removal and whole-state staging. F06,F08–F10. |
| C. L3 correctness/FIFO | High | Implemented bounded model: `src/book/order_book.cpp:144–220,269–300`; `tests/test_book.cpp:102–166` | Explicit replacement priority, quantity conservation/index/FIFO invariants. An identified execution can remove a named nonfront order: historical reconstruction, not a FIFO execution validator. Venue behavior/large recovery Partial. F07,F11,F13. |
| D. Ingestion/sequencing/provenance | High | Partial: `src/replay/replay.cpp:71–143,150–221`; `python/gig_microstructure/__init__.py:324–362` | Validated canonical events and strict cursor/order checks exist; raw feed decoding/reordering absent. Export references incomplete. F02,F03,F13,F14. |
| E. Exactness/overflow | High | Implemented: `include/gig/analytics/exact.hpp:13–54`; `include/gig/core/numeric.hpp:148–219`; `src/execution/execution.cpp:83–107` | Exact bounded rational arithmetic, no silent conversion rounding. Intermediate-capacity rejection is explicit; TCA misses a quantity-rule check. F04,F11. |
| F. Metrics/interpretation | Medium | Implemented formulas: `src/analytics/book_metrics.cpp:26–45`; `src/analytics/flow_metrics.cpp:77–140` | Spread/weighted midpoint/imbalance, OFI, signs and sampled returns exist. Weighted microprice is a proxy, not calibrated expected fair value. F09,F13,F14. |
| G. Statistics/causality | High | Partial contracts, empirical validity Unverified: `src/analytics/flow_metrics.cpp:14–20,25–56,115–140`; `src/execution/execution.cpp:44–59` | Prefix/time guards and profile availability checks help; caller-supplied timestamps/completeness are trusted. No inferential study. F12–F15. |
| H. Matching/queue/latency | High | Partial: `src/simulation/simulator.cpp:35–96,133–156` | Deterministic price/FIFO, IOC/FOK/post-only and modeled queue truth exist. Maker reporting incomplete; latency uncalibrated and full-state oracle limited. F01,F08,F12,F13. |
| I. Schedules/TCA | High | Partial: `src/execution/execution.cpp:8–60,62–107`; `scripts/check_execution_reference.py:6–25` | Exact allocation and supplied-benchmark cost algebra verified in generated cases. Open-loop schedules are not adaptive execution agents. F02,F04,F15. |
| J. Performance | Medium | Partial measurement coverage: `benchmarks/book_benchmark.cpp:21–39`; `benchmarks/research_benchmark.cpp:24–34`; `scripts/run_engine_baseline.py:11–50` | Raw bulk and serial service samples, gated by correctness, genuinely run. No queued-arrival tail/SLO or hardware-independent speed claim. F17,F18. |
| K. Memory/scalability | High | Partial evidence: `include/gig/events/contracts.hpp:156–167`; `include/gig/replay/replay.hpp:31–34,49–53`; `include/gig/memory/tracked_resource.hpp:9–40` | PMR live/peak accounting is useful, not fragmentation accounting. Large inline variants inflate every journal entry. F06–F10,F22. |
| L. Failure/adversarial testing | High | Implemented fault injection, fuzzing Missing: `tests/test_book.cpp:102–140`; `tests/test_flow_metrics.cpp:23–46`; `python/bindings/wire.hpp:140–144` | Staging and structured errors have real tests. Four uncovered cases demonstrate adversarial cross-boundary gaps. F01–F04,F11,F12. |
| M. Persistence/recovery/operations | High | Partial in-memory recovery; durable restart Missing: `src/replay/replay.cpp:182–221,233–248`; `python/gig_microstructure/__init__.py:363–450` | Canonical export is not a restore parser/WAL/checkpoint protocol. No crash-resilient service. F07,F19. Production-only controls conditional. |
| N. Python/package/API | Medium | Implemented optional interface, compatibility Partial: `python/bindings/wire.hpp:23–78,138–144`; `CMakeLists.txt:153–184`; `pyproject.toml:1–18` | Exact strings, owned documents, strict codecs and local package exist. Schema validity differs from native semantic validity; ABI not stable. F05,F21,F22. |
| O. CI/toolchains/platforms | Medium | Partial/hosted Unverified: `.github/workflows/ci.yml:8–55`; `CMakeLists.txt:153–163,188–213` | Six native workflow combinations defined; Python only GCC Release in hosted workflow. No ARM/native multi-Python evidence. F18,F20,F21. |
| P. Security/dependencies/provenance | High | Partial: `python/gig_microstructure/__init__.py:172–200,300–450`; `scripts/review_dependencies.py:20–43`; `requirements-python.lock:1–13` | Input bounds/no unsafe deserialization, safe-name checks, retained hashes are good. Advisory snapshot/metadata is limited; source consistency holes exist. F02,F03,F19,F23. |
| Q. Real-data readiness/calibration | High | Missing/Unverified: raw wire adapters absent from source inventory; `src/replay/replay.cpp:117–143`; `src/simulation/simulator.cpp:35–39` | No licensed feed conformance corpus or empirical latency/fill calibration. Deliberate scope gap, not a claim of unsupported raw decoding. F07,F13,F14. |
| R. Terminal readiness | Medium | Partial contract only: `docs/GIG_INTEGRATION.md:8–37`; `python/gig_microstructure/__init__.py:113–170` | Standalone consumer boundary exists; no actual Terminal adapter/consumer compatibility test. Terminal modifications are Not applicable to this audit. F05,F24. |
| S. Documentation/interview | Medium | Partial: `src/main.cpp:13–16`; `docs/FINAL_REPORT.md:1–18`; dense implementation `src/execution/execution.cpp:23–37` | Extensive useful limitations and evidence, but completion language and compressed code need qualification by newly uncovered cases. F25. |

## Confirmed defects and targeted reproductions

These are synthetic adversarial inputs, not authentic research runs. Temporary
manifest code hashes/configurations are deliberately supplied by the test caller;
acceptance demonstrates missing consistency enforcement, not forged authentication.
The reproduction driver uses existing `tests/python_fixtures.py` and the validated
installed extension; it changes no implementation. R1–R4 exit normally and show:

```text
R1: maker1 sells10@100, taker2 buys10@100, advance to1000.
    exchange_fills=[{maker:"1",taker:"2",quantity:"10",price:"100"}]
    client_fill_orders=["2"]
    remaining_orders=[]
R2: rules.maximum_quantity="10", input SimFill.quantity="11", target="20".
    transaction_costs accepts; filled_lots="11", unfilled_lots="9".
R3: VWAP profile="MISSING-PROFILE"; only unrelated-input bytes retained.
    export_run succeeds; verify_export returns complete=true.
R4: event.dataset.sha256=64 zeroes; retained dataset identity="python-synthetic".
    actual retained bytes SHA256=
    13d88c6c0d70bbff19ed19f9b545ed2919687882f04a10b02ba627cf0144449a
    export_run succeeds; verify_export returns complete=true.
R5 (boundary illustration, not a new defect): loads accepts schema-valid Add quantity0;
    event(document,rules) rejects it with invalid_range: quantity.
```

F18 below is also a confirmed source-level metadata defect for alternate compiler
build directories; the reproduced GCC run itself is not mislabeled. No new memory
corruption/UB finding was produced by this audit. Failure to find one is not a safety
proof. R5 is intentional schema/domain layering that requires clearer consumer use,
not evidence that `Replay.apply` accepts zero quantity.

## Top 25 prioritized findings and improvements

### F01 — Complete maker-side client execution reports

- **Severity / status:** High / Partial. Confirmed reporting defect within the general
  per-order client-report contract, not a matching-price/FIFO defect.
- **Source:** `src/simulation/simulator.cpp:46–49,67–74`; client contract
  `docs/PHASE_5_CONTRACTS.md:33–37,59–66`; tests `tests/test_python.py:95–108`.
- **Current behavior / consequence:** Accepted resting makers lose inventory in
  exchange truth but only the incoming taker gets a fill report. A client consuming
  only delivered reports cannot reconcile an accepted maker order after execution.
  There is no participant/background-order designation justifying omission.
- **Evidence:** R1: maker1 accepted10, fully consumed; no maker fill report even after
  advancing past all delays, while its exchange order disappears. Existing matcher
  oracle checks fills/ledger, not both counterparties' client reports.
- **Improvement / acceptance:** Deliver fills to each modeled client order, or define
  and enforce explicit ownership scope that distinguishes external liquidity.
  Reconcile accepted minus fills/cancels/expiry with outstanding client state for
  every owned maker and taker; cover partial/multiple makers, delayed ACK/fill and
  cancellation races. Ensure allocation failures leave all reports/fills atomic.
- **Complexity / dependencies / risks:** Medium; requires report scope decision and
  extension of independent report oracle. Extra reports affect caps, RNG consumption,
  canonical bytes and version compatibility. Do not hide the change under old hashes.

### F02 — Resolve all execution input references during export

- **Severity / status:** High / Partial. Confirmed provenance completeness defect.
- **Source:** `python/gig_microstructure/__init__.py:324–362`, especially346–349;
  `include/gig/execution/execution.hpp:13–29`.
- **Current behavior / consequence:** Export checks schedule run/oracle labels but
  not VWAP profile identity or POV volume-point source artifacts. A complete export
  can omit the stated source inputs. Inline weights can still reproduce allocation;
  it is the asserted source lineage/completeness that is false or unsupported.
- **Evidence:** R3 exported a plan referencing MISSING-PROFILE with only unrelated
  input bytes; both exporter and verifier accepted complete=true. POV lacks the
  equivalent reference traversal by source inspection.
- **Improvement / acceptance:** Define a centralized typed reference traversal shared
  by export and verification. Every profile, volume, benchmark, source and parent
  reference resolves to retained input or explicit typed external-unavailable state;
  complete=true must reject unresolved mandatory refs. Test dangling/cyclic/duplicate
  references, oracle labels and intentionally absent optional metadata.
- **Complexity / dependencies / risks:** Medium; coordinate schema/reference semantics
  with F03,F24. Identity collisions and raw-versus-derived artifact distinctions must
  be explicit; do not require duplicate raw data unnecessarily.

### F03 — Reject contradictory declared and retained digests

- **Severity / status:** High / Partial. Confirmed internal consistency defect, distinct
  from the explicitly excluded problem of cryptographic source authentication.
- **Source:** `python/gig_microstructure/__init__.py:315–320,330–339,414–449`;
  digest syntax validator `src/events/validation.cpp:22–28,76–79,101–104`.
- **Current behavior / consequence:** Retained bytes match the manifest input hash,
  but an event's known dataset/parent digest is not compared with that same retained
  identity. Mutually inconsistent lineage can pass complete verification.
- **Evidence:** R4 retains actual bytes under the declared dataset identity while
  its event declares all-zero SHA256; verification still reports complete=true.
- **Improvement / acceptance:** For references with the same defined artifact scope,
  compare all known digests with the retained content and reject disagreement before
  finalization. If dataset/file/journal digest scopes differ, represent the mapping
  explicitly rather than silently equating identities. Test dataset, parent, profile
  and nested manifest contradictions in both export and read-only verification.
- **Complexity / dependencies / risks:** Medium; depends on F02's identity/scope model.
  Hash consistency is not authentication, licensing proof or completeness proof.

### F04 — Apply quantity rules to every TCA fill

- **Severity / status:** High / Partial. Confirmed validation defect.
- **Source:** `src/execution/execution.cpp:83–105`, especially94,98;
  contrast `src/events/validation.cpp:62–67,235` and
  `src/simulation/simulator.cpp:19–23`.
- **Current behavior / consequence:** TCA checks positive fill quantity and aggregate
  target, but not `fill.quantity <= rules.maximum_quantity`. Caller-supplied fills
  can violate rules enforced by the other typed event/model boundaries.
- **Evidence:** R2 accepts11 lots under maximum10. This modifies an input record to
  test rejection; it does not claim the native simulator generated an illegal fill.
- **Improvement / acceptance:** Factor a SimFill validator with rules and causal/source
  context. Reject max+1 with deterministic field/index before producing costs; accept
  max and valid multi-fill totals. Independently test maker and taker cost sides,
  quantity0/max/u64 limits, bad seeds/identity and no mutation on failure.
- **Complexity / dependencies / risks:** Small for range fix; Medium for shared full
  validator. Confirm maximum_quantity is per-order/fill rather than aggregate target;
  avoid incorrectly capping the entire parent execution.

### F05 — Make schema validity and semantic validity unmistakable

- **Severity / status:** Medium / Partial. Boundary clarity gap, not an apply bypass.
- **Source:** `python/gig_microstructure/__init__.py:132–170,202–209,224–226`;
  native validators `src/events/validation.cpp:209–255`.
- **Current behavior / consequence:** `loads`/`validate_document` validate shape and
  string bounds, not every event/derived-result invariant. Consumers may treat an
  owned/validated document as an executable valid event. Native apply does revalidate.
- **Evidence:** R5 loads zero-quantity Add, while `event(...,rules)` rejects it.
  Arbitrary schema-valid metric values are not recomputed against source history.
- **Improvement / acceptance:** Document and name structural/domain/trusted-derived
  validation levels. Expose explicit semantic validation with required rules/context;
  no consumer path should mistake a JSON hash for a correctness proof. Add paired
  acceptance/rejection tests for each level and every event family.
- **Complexity / dependencies / risks:** Small/Medium; coordinate F02,F24. Avoid turning
  deserialization into implicit replay of an arbitrarily large external history.

### F06 — Reduce inline journal size after measuring it

- **Severity / status:** High / Implemented. Measured scalability limitation, deliberate
  owned-data baseline rather than memory corruption.
- **Source:** `include/gig/events/contracts.hpp:156–167`;
  `include/gig/replay/replay.hpp:31–34,49–53`; reserve
  `src/replay/replay.cpp:109–115,137–142`.
- **Current behavior / consequence:** Every event contains the largest bounded
  snapshot variant; every journal entry also reserves optional restart storage.
  Measured GCC x86_64 sizes: MarketEvent12,208 bytes, JournalEntry15,944,
  RestartPlan3,720, ReplayConfig4,824. At4,096 entries the journal element storage
  alone is65,306,624 bytes; at100,000 it is1,594,400,000, before vector growth peak,
  book, strings, exports or Python. Optional absence does not save inline space.
- **Evidence:** The temporary sizeof program below and reproduced PMR/RSS results.
  Reserve growth keeps old and new storage alive during transfer.
- **Improvement / acceptance:** Separate common event headers from uncommon snapshot/
  restart payload ownership; consider immutable interned source metadata only after
  defining lifetime/versioning. Preserve exact canonical events and failure atomicity.
  Publish bytes/event, peak/live allocation and output equivalence over increasing N
  before/after; agree resource budgets from intended workloads, not a made-up SLA.
- **Complexity / dependencies / risks:** Large; affects codecs, snapshots and journal
  ownership. Depends on F11 and a pre-change memory baseline. Do not replace large
  owned values with dangling string_views or borrowed buffers.

### F07 — Align recovery capacity with supported book size

- **Severity / status:** High / Partial. Deliberately bounded scope with real-data impact.
- **Source:** `include/gig/events/contracts.hpp:156–160`;
  `src/book/order_book.cpp:125–129,231–266`;
  `src/replay/replay.cpp:182–221`.
- **Current behavior / consequence:** Order books can be configured for up to1,000,000
  orders, but a complete recovery event holds only64 orders and8 stream boundaries.
  A gap on a larger book cannot be repaired through the current snapshot contract.
- **Evidence:** Fixed BoundedList64 type and sorted64 recovery staging array; existing
  recovery tests exercise the bounded mechanism, not production-sized snapshots.
- **Improvement / acceptance:** Explicitly declare a recoverable-size limit now.
  If large replay is authorized, implement bounded chunked snapshot assembly with a
  transaction boundary, completeness/order proof and all-stream barrier;64/65 and
  multi-chunk failure/retry tests must preserve state. Demonstrate recovery equals
  uninterrupted replay for an agreed larger synthetic dataset.
- **Complexity / dependencies / risks:** Large; depends on F06,F11 and feed semantics.
  Partial snapshots must never become active FIFO state or silently drop orders.

### F08 — Treat simulator cloning and vector scheduling as a baseline

- **Severity / status:** High / Implemented. Architectural scalability tradeoff.
- **Source:** `src/simulation/simulator.cpp:29–44,51–56,69–81,89–96,110–123`.
- **Current behavior / consequence:** Each submit/cancel/advance copies active orders,
  queued events, all fills/reports/issued IDs and commands. Queue insertion and front
  removal move vector elements; matching scans all orders per maker fill. A long
  bounded run can accumulate quadratic work in retained history, even with a small
  active book. Debug invariant scans add quadratic active-order checks.
- **Evidence:** Explicit copy constructor/staging and loops; reproduced benchmark
  covers32 initial makers and128 taker operations, not a growth curve.
- **Improvement / acceptance:** Measure components versus active N, queue E and retained
  history independently. Retain clone model as an oracle if moving to a staged delta
  commit or heap/index. Require identical matching/report semantics under independent
  reference, failure injection and deterministic seeds; report both peak memory and
  throughput on identical histories. No arbitrary absolute latency target.
- **Complexity / dependencies / risks:** Large; F01,F11,F12 first. Transaction rollback,
  scheduler ties, PRNG consumption and canonical versioning are major risks.

### F09 — Remove repeated linear quote searches only when warranted

- **Severity / status:** Medium / Implemented. Known algorithmic cost.
- **Source:** `src/analytics/flow_metrics.cpp:14–20,95–105,117–138`.
- **Current behavior / consequence:** `quote_at` rescans quotes for grid points and
  several queries per trade. Complexity is O(Q*(T+S)+Q+T), with Q,T,S each bounded4096;
  small fixed benchmark hides worst-case cost. Input ordering already supports cursors
  or binary searches, with care for prefix constraints and equal timestamps.
- **Evidence:** Loop nesting in source; benchmark uses two quotes and one trade.
- **Improvement / acceptance:** Profile maximum allowed/window-diverse inputs. If
  material, use monotone cursors or search indices while preserving strict prior
  prefix selection, age, zero horizon and same-time semantics. Compare every field
  against the current algorithm across randomized boundary cases and document scaling.
- **Complexity / dependencies / risks:** Medium; depends on F11,F14. A faster lookup
  that admits future equal-time quotes is a correctness regression.

### F10 — Measure fragmentation, churn and resource exhaustion separately

- **Severity / status:** Medium / Unverified. Memory evidence gap.
- **Source:** `include/gig/memory/tracked_resource.hpp:9–40`;
  `benchmarks/memory_stats.hpp:9–20`; book node allocation
  `src/book/order_book.cpp:90–100`.
- **Current behavior / consequence:** PMR records requested live/peak bytes and counts;
  VmHWM is whole-process high-water. Neither measures allocator metadata, unusable
  free space, post-churn resident retention or deterministic allocation latency.
- **Evidence:** Counter implementation and actual RSS/PMR fields; no fragmentation/
  long-lived churn measurement found in benchmark sources.
- **Improvement / acceptance:** Add repeatable add/cancel/replacement churn and burst/
  recovery cycles at several active/history sizes; report live/requested/RSS before,
  during and after teardown, allocator/tool version and hard-budget failure behavior.
  Do not infer fragmentation from a single RSS number or “zero live PMR” alone.
- **Complexity / dependencies / risks:** Medium; F06,F17 workloads first. Diagnostic
  tools perturb memory; keep instrumented results separate from timing baselines.

### F11 — Add mutation-sequence and interchange fuzzing

- **Severity / status:** High / Missing. Important research hardening gap.
- **Source:** Existing deterministic generators `tests/test_book.cpp:141–166`,
  `scripts/check_simulation_reference.py:5–33`, `scripts/check_flow_metrics.py:5–17`;
  CMake test registration `CMakeLists.txt:78–146`.
- **Current behavior / consequence:** Good seeded and hand tests do not explore the
  Cartesian product of malformed metadata, field contradictions, message fragments,
  reset/recovery, allocation failures and exports. No fuzz target/corpus/coverage
  build was found. Independent book oracle also uses unchecked small-case arithmetic
  (`tests/support/book_reference.hpp:19–59`), so it is not a max-u64 reference.
- **Evidence:** All suites passed while R1–R4 succeeded. Absence established by source/
  target inventory, not inferred from a test count.
- **Improvement / acceptance:** Seed fuzzers with existing fixtures and audit cases;
  exercise parser/schema/native transitions and differential state machines under
  ASan/UBSan. Record seed/corpus/tool/coverage and bounded execution budget; every
  finding becomes a minimized permanent regression. Add arbitrary-precision ledger
  boundary references rather than overflowing the small C++ oracle.
- **Complexity / dependencies / risks:** Medium/Large; establish explicit expected
  malformed-input behavior first. Coverage is not proof, and fuzz budgets must remain
  bounded. A fuzzer should not replay untrusted files outside a scratch directory.

### F12 — Independently verify latency/report information sets

- **Severity / status:** Medium / Partial. Matching math verified more broadly than reports.
- **Source:** `scripts/check_simulation_reference.py:5–32`;
  `src/simulation/simulator.cpp:35–49,89–96`; `tests/test_python.py:95–108`.
- **Current behavior / consequence:** Random oracle compares orders, fills and
  conservation with zero-time commands; hand cases check some races and delays.
  It does not independently model both counterparties' reports, PRNG draw mapping
  or a strategy restricted to observations. Modulo jitter is deterministic, but is
  only approximately uniform unless the PRNG range divides the chosen modulus;
  no independent distribution/calibration study was obtained.
- **Evidence:** Oracle output construction excludes client_reports. R1 escaped it.
- **Improvement / acceptance:** Build a small independent event scheduler/report oracle
  with explicit RNG mapping and owned order scope. Compare delivered information
  after each command/time advance, including report-before-ACK, equal-time ties,
  pending cancel and failure rollback. Label latency as assumed or fit it to data;
  if exact uniform sampling is promised, specify/test unbiased mapping.
- **Complexity / dependencies / risks:** Medium; depends on F01 and deterministic
  model version. More scenarios do not prove real exchange latency distributions.

### F13 — Establish real-data and empirical research validity

- **Severity / status:** High / Unverified. Intended future scope, not a fabricated capability.
- **Source:** Generic event boundary `src/events/validation.cpp:209–251`,
  `src/replay/replay.cpp:117–143`; analytics formulas
  `src/analytics/book_metrics.cpp:29–34`, `src/analytics/flow_metrics.cpp:77–140`;
  latency model `src/simulation/simulator.cpp:35–39`.
- **Current behavior / consequence:** No actual raw exchange decoder, conformance
  captures, licensed observed dataset or calibrated queue/impact model was found.
  Formula correctness does not validate predictive utility or causal market impact.
  Trade signs are estimates; weighted microprice is not an empirically established
  conditional expected price. Synthetic activity rates are not market statistics.
- **Evidence:** All current reference/benchmark inputs are synthetic generators;
  existing tests compare algebra/transition rules, not observations.
- **Improvement / acceptance:** Select one licensed/publicly redistributable source
  and explicitly chosen venue/instrument/session semantics. Independently reconcile
  message counts, gaps, order/volume/depth and known snapshot boundaries. Then use
  time-ordered train/validation/test splits, ex-ante parameter availability, declared
  horizons, uncertainty/dependence-aware estimates and documented failed hypotheses.
  Publish reproducible analysis with dataset rights/digests, not an alpha assertion.
- **Complexity / dependencies / risks:** Large; F02–F04,F07,F11,F14 and suitable data
  rights first. Survivorship, feed corrections, clock errors, corporate actions,
  currency/contract multipliers and data-snooping can invalidate conclusions.

### F14 — Make completeness and clock assumptions evidence-bearing

- **Severity / status:** High / Partial. Research contract weakness.
- **Source:** `include/gig/analytics/flow_metrics.hpp:14–17`;
  `src/analytics/flow_metrics.cpp:25–56,68–79,121–140`;
  `src/replay/replay.cpp:91–102`.
- **Current behavior / consequence:** Standalone flow defaults completeness flags to
  true and accepts caller-built parent references/timestamps. Strict common clock
  names/prefix ordering are checked, but actual complete top updates and physical
  clock synchronization cannot be derived from these assertions. A forged or sparse
  yet monotone observation set can generate apparently known OFI/intensity.
- **Evidence:** Source guards inspect bools/identities/order only; gap/false-flag hand
  tests suppress metrics correctly (`tests/test_flow_metrics.cpp:23–37`).
- **Improvement / acceptance:** Default unproven continuity to unavailable or require
  an explicit evidence token derived by a replay-aware extractor. Retain a deliberate
  trusted-input path with visible assumptions. Deleting an intermediate update or
  crossing session/gap/clock precision boundaries must yield unavailable/rejection
  unless the caller explicitly supplies a reviewed completeness assertion.
- **Complexity / dependencies / risks:** Medium; F02,F13 source semantics. Replay
  continuity alone does not prove the adapter preserved every top update.

### F15 — Distinguish execution schedules from adaptive agents

- **Severity / status:** Medium / Partial. Deliberate model boundary.
- **Source:** `src/execution/execution.cpp:23–59,62–80`.
- **Current behavior / consequence:** TWAP/VWAP produce fixed children; POV allocates
  against externally visible cumulative volume with submitted-inventory caps.
  Integration submits a prebuilt plan against seeded liquidity without feedback
  adaptation. No urgency optimization, cancel/replace agent, price discovery,
  calibrated cost control or market impact feedback is implemented. Conservative
  submitted budgeting can underexecute; that is documented, not a conservation bug.
- **Evidence:** `simulate` submits initial liquidity and each fixed child then advances;
  independent references cover allocations/cost algebra, not a policy evaluation.
- **Improvement / acceptance:** Keep current deterministic planners explicitly named
  schedules. Only if needed, add a separate causal execution controller consuming
  delivered reports after F01/F12. Verify no overshoot, no future volume/quote use,
  deadline/pending-order handling, and end-to-end cost reconciliation on adverse cases.
- **Complexity / dependencies / risks:** Large for adaptive policy, Small for clarified
  naming. Requires empirical objectives and source data before optimality claims.

### F16 — Strengthen native PMR lifetime ergonomics

- **Severity / status:** Medium / Partial. API hazard, no reproduced ownership violation.
- **Source:** `include/gig/book/order_book.hpp:23–29,34–45`;
  `include/gig/analytics/flow_metrics.hpp:27–37`;
  `include/gig/memory/tracked_resource.hpp:9–18`;
  `include/gig/replay/replay.hpp:69–72`.
- **Current behavior / consequence:** Move-only owners and custom deleters preserve
  resource selection; replay move assignment is correctly deleted. Native snapshots/
  metric vectors still borrow allocator lifetime despite owning their elements.
  Returning one beyond a stack resource lifetime is invalid caller behavior.
- **Evidence:** Explicit allocator pointers/vector constructors; existing Python
  owner ordering and copied results avoid this exposure. No claim that merely
  using PMR creates a bug; the documented precondition remains the caller's duty.
- **Improvement / acceptance:** Add conspicuous resource-lifetime examples, allocation-
  destination clone/export methods or a resource-owning session wrapper where useful.
  Test moves/destruction/returned copies across unequal resources and explicitly
  bounded spans. Avoid promising resource-independent immutable native values.
- **Complexity / dependencies / risks:** Medium; F06 ownership design and downstream
  usage. Shared ownership everywhere would add cost and obscure the single owner.

### F17 — Expand performance experiments before making system claims

- **Severity / status:** High / Unverified. Performance generalization gap.
- **Source:** `scripts/run_engine_baseline.py:11–14,34–50`;
  `benchmarks/research_benchmark.cpp:12–31`;
  `benchmarks/execution_benchmark.cpp:10–21`; Python benchmark
  `scripts/benchmark_python.py:27–54`.
- **Current behavior / consequence:** Bounded repeated bulk throughput and separate
  serial service observations are real; most research kernels repeat a tiny fixture.
  There is no offered-load queue, backpressure, mixed-session arrival stream,
  dependence-aware tail interval or capacity curve. Serial p99 does not establish
  end-to-end queued p99; short closed-loop experiments can hide coordinated omission.
- **Evidence:** Reproduced measurements below; no external arrival process in drivers.
  Shared-host outliers are retained and honestly scoped in manifests.
- **Improvement / acceptance:** Add workload composition, cardinality/history/depth,
  burst/cancel/replace/recovery and warm/cold experiments; distinguish operations,
  events and plans. For latency claims define arrival model/load and report queueing,
  drops, sample counts and confidence/uncertainty. Include CPU/time baseline and
  repeated-host trials; avoid invented institutional targets and cross-row speedups.
- **Complexity / dependencies / risks:** Medium/Large; F06–F10 and meaningful use case.
  Pinning/affinity does not remove shared-cloud scheduling or frequency uncertainty.

### F18 — Record the selected compiler, not ambient c++

- **Severity / status:** Medium / Partial. Confirmed source-level metadata defect for
  alternate build directories; not a defect in this GCC run's numeric results.
- **Source:** `scripts/run_engine_baseline.py:16–22,31,49`.
- **Current behavior / consequence:** `--build-dir` can select Clang, but manifest
  `environment.compiler` executes ambient `c++ --version`. Here ambient c++ is GCC14
  and the Clang tree uses workspace Clang19. Compile commands preserve clues, but
  the explicit compiler field would misidentify that experiment.
- **Evidence:** Source line49 and two locally installed compiler versions; no claim
  that a complete Clang benchmark was newly run. GCC baseline compiler matches.
- **Improvement / acceptance:** Read compiler executable/ID/version from the selected
  build's CMake metadata and preserve actual compile/link flags/toolchain identity.
  Run smoke experiments selecting GCC and Clang while ambient CXX/c++ differs; the
  manifest must identify the selected compiler exactly. Verify no undeclared LTO/
  sanitizer/profile instrumentation; inspect assembly where constant fixture
  optimization could matter before interpreting tiny-kernel throughput.
- **Complexity / dependencies / risks:** Small/Medium; metadata schema version and
  toolchain wrappers need explicit handling. Do not “fix” by discarding compile flags.

### F19 — Keep export integrity distinct from crash-safe recovery

- **Severity / status:** High / Missing for production durability; Not applicable to a
  claim of an always-on trading service, which the project does not make.
- **Source:** `src/replay/replay.cpp:233–248`; public API
  `include/gig/replay/replay.hpp:73–82`;
  `python/gig_microstructure/__init__.py:363–450`.
- **Current behavior / consequence:** Canonical data is exported, but no canonical
  restore parser, durable append log/checkpoint cursor transaction, checksum chain
  or restart protocol exists. Export fsyncs files and links a manifest, but not the
  containing directories; initial/incomplete markers are not a crash transaction.
  Path checks also are not a race-resistant hostile-filesystem sandbox.
- **Evidence:** Public methods have no restore operation; source finalization sequence
  lacks directory fsync. Mocked os.link failure test covers one exception, not power
  loss at every file/directory transition (`tests/test_python.py:168–173`).
- **Improvement / acceptance:** For offline scope, state precise recoverable artifact
  guarantees and test interruption stages. If durable restart becomes authorized,
  design versioned checkpoint/log ownership and atomic cursor+state recovery, perform
  process-kill/storage-fault tests, and verify resumed output equals uninterrupted
  output with no double application. Use trusted directories or fd-based safe opens
  if adversarial writers are in scope.
- **Complexity / dependencies / risks:** Large; F02,F03,F07,F11 first. Filesystem/OS
  semantics and corruption policy matter. Do not introduce a database/service merely
  to inflate this portfolio project's scope.

### F20 — Obtain retained hosted/platform CI evidence

- **Severity / status:** Medium / Partial. Hosted status Unverified, not a known CI failure.
- **Source:** `.github/workflows/ci.yml:8–55`; sanitizer support
  `CMakeLists.txt:188–211`; platform restriction
  `include/gig/analytics/exact.hpp:6–8`.
- **Current behavior / consequence:** GCC/Clang x3 native configurations defined;
  hosted Python tests only GCC Release. No artifact upload/retained JUnit step,
  native ARM job or compatibility matrix covers the declared Python range.
- **Evidence:** Local audit matrix passed; exact baseline checks API blocked CONNECT403.
  No native ARM hardware or cross-compile test was obtained. GNU128 is required;
  current MSVC exact-arithmetic path is unsupported despite generic CMake warning code.
- **Improvement / acceptance:** When authorized access exists, retain job links,
  exact commit/tool versions/JUnit/log artifacts and schema/package results. Add
  practical native ARM and supported-Python coverage with existing resources, no
  paid provisioning. A cross-compile build must remain labeled cross-compiled only.
- **Complexity / dependencies / risks:** Medium; CI access/runtime budget and F21.
  Platform coverage is evidence, not a guarantee of identical long-double strings.

### F21 — Align Python support claims, locks and wheel portability

- **Severity / status:** Medium / Unverified. Explicitly scoped lock, not a proven install bug.
- **Source:** `pyproject.toml:1–10`; `requirements-python.lock:1–13`;
  `CMakeLists.txt:158–165`; `python/bindings/module.cpp:31–32`.
- **Current behavior / consequence:** Metadata allows CPython3.9–3.12, while only3.12
  Linux was exercised. The tested lock's referencing0.37 requires>=3.10 and rpds-py
  2026.9.1>=3.11 per installed distribution metadata. The lock header correctly
  restricts its scope; it cannot validate3.9/3.10. Wheel is platform/CPython-specific,
  not stable ABI or automatically portable manylinux.
- **Evidence:** Installed metadata and lock; no3.9/3.10 run attempted. Runtime pip
  resolution without that lock might choose compatible older transitive versions,
  so incompatibility of the declared package itself is not established.
- **Improvement / acceptance:** Test every advertised interpreter or narrow metadata;
  provide per-version/platform constraints where required. Inspect wheel linked
  dependencies and minimum libc/libstdc++ requirements; install away from checkout
  in clean consumers. Do not claim abi3 or binary reproducibility without evidence.
- **Complexity / dependencies / risks:** Medium; F20 resources, upstream compatibility
  and dependency license/advisory review. Preserve the validated3.12 environment.

### F22 — Profile repeated Python serialization and native export copies

- **Severity / status:** Medium / Implemented. Unnecessary hot-path work worth measuring.
- **Source:** `python/gig_microstructure/__init__.py:67–94,132–167,224–226`;
  `python/bindings/wire.cpp:19–24`.
- **Current behavior / consequence:** Document construction serializes canonical JSON;
  each nested lookup reparses the whole document, apply validates then copies back
  to dict. A simulation snapshot includes full arrays and a second canonical history
  string. Ownership safety is strong, but repeated access/export is costly and Python
  allocations sit outside native resource_budget_bytes.
- **Evidence:** Reproduced full-interface678.5 events/s includes these layers, not
  merely C++ mutation. Native PMR does not measure parser/schema/JSON allocations.
- **Improvement / acceptance:** Profile parsing/schema/copy/native separately, and
  compare safe immutable parsed storage or explicit bulk input against current design.
  Preserve nonborrowed values and rejection semantics. Publish wall time and Python/
  native peak memory for identical document sizes/access patterns before changing API.
- **Complexity / dependencies / risks:** Medium; F05,F06,F17. Cached mutable dicts can
  violate ownership; releasing GIL without lifetime discipline is not a shortcut.

### F23 — Make dependency/security evidence reproducible and bounded

- **Severity / status:** Medium / Partial. No current vulnerability established here.
- **Source:** `requirements-python.lock:1–13`; `scripts/review_dependencies.py:20–43`;
  `python/gig_microstructure/__init__.py:43–73,172–200,407–449`;
  `THIRD_PARTY_NOTICES.md` (retained pybind notice).
- **Current behavior / consequence:** Exact versions and a previous registry-digest/
  advisory inventory exist; install lock does not itself enforce hashes. Registry
  advisory absence and license metadata are not a complete source/platform audit.
  JSON depth/byte bounds are useful, but objects/serialized output are allocated
  before some final size checks. No signing/authentication or formal threat model.
- **Evidence:** Source review only for dependency status in this audit; no fresh
  advisory query. Current limited pattern review is not proof of no secrets. The
  project has no authorized public distribution/license grant.
- **Improvement / acceptance:** Define trusted input/filesystem boundaries, retain
  approved wheel hashes and SBOM/license evidence, and verify hash-pinned offline
  installation where practical. Separate unavailable advisory data from clean checks;
  cover parser/export size limits and dependency update regression gates. Review
  distribution rights before any release, which remains unauthorized.
- **Complexity / dependencies / risks:** Medium; F02,F03,F11,F19,F21. Package index
  hash matching is not an upstream signature; do not manufacture security assurance.

### F24 — Validate the standalone consumer contract before Terminal integration

- **Severity / status:** Medium / Partial. Actual Terminal integration deliberately absent.
- **Source:** `docs/GIG_INTEGRATION.md:8–37`;
  `python/gig_microstructure/__init__.py:117–170`;
  `python/bindings/schemas.cpp:1–37`.
- **Current behavior / consequence:** Versioned exact JSON and Python consumption
  contract exist. Numeric bounds use custom x-integer annotations, which generic
  JSON Schema validators do not enforce automatically; native state invariants
  remain a separate layer. No external consumer regression proves equivalent behavior.
- **Evidence:** Python companion extends validators at119–125; this audit did not
  touch/run Terminal or a JS/Rust/etc consumer. An interface contract is not integration.
- **Improvement / acceptance:** Create a standalone consumer conformance corpus
  covering2^53+ integers/u64/i64, fractions, enums, missing reasons, unknown versions,
  semantic-invalid-but-schema-valid events and incomplete provenance. Require any
  later adapter to pass it and preserve origin/assumptions before changing Terminal.
- **Complexity / dependencies / risks:** Medium; F02–F05,F21. No new dashboard or
  Terminal dependency is justified to test a wire contract.

### F25 — Improve reviewability and qualify completion claims

- **Severity / status:** Medium / Partial. Maintainability/interview evidence gap.
- **Source:** Dense algorithms `src/execution/execution.cpp:23–37,83–107`,
  `src/simulation/simulator.cpp:110–123`, `python/bindings/wire.hpp:28–78,140–144`;
  historical demo `src/main.cpp:13–16`; completion `docs/FINAL_REPORT.md:1–18`.
- **Current behavior / consequence:** Many nontrivial transitions/formulas/errors share
  one physical line; reflection/codecs, generated schemas and long reports increase
  review surface. The console labels Phase2 while later features live in libraries.
  “Complete” refers to phase scope, not absence of the defects found here.
- **Evidence:** Direct source inspection and four passing-suite counterexamples.
  The project has useful detailed limitations; those should not be replaced with
  blanket institutional/production claims.
- **Improvement / acceptance:** Reformat bounded components without semantic change;
  name validation/commit stages and formula units; cross-reference one authoritative
  contract per behavior. Add audit regressions and a concise evidence ledger labeling
  implementation/tested/unverified. Demonstrate unchanged canonical bytes and tests
  for readability-only changes. Explain why a weighted metric is not alpha and why
  an oracle does not certify an exchange.
- **Complexity / dependencies / risks:** Small/Medium; fix F01–F04 first or separately
  to avoid obscuring behavioral diffs. Do not collapse safe boundaries simply to
  reduce file count or add fashionable template/infrastructure abstractions.

## Reproduced performance and memory findings

The following are actual new runs at the audited SHA, dirty=false, recorded before
creating this audit document. They are experiments on a shared cloud host, not
institutional targets. All five native workload artifact sets match Phase 9, and
both benchmark runners reran their regression/reference preflight. The native
runner rebuilt Release; all checks passed before timing. Runs were serial after
other builds/tests stopped. The subsequent fresh configure/build was performed
after these measurements. No performance optimization was attempted.

| Native wrapper workload | Median ops/s | p50 ns | p95 ns | p99 ns | Worst observed ns |
|---|---:|---:|---:|---:|---:|
| book_analytics | 3,255,185.0 | 300 | 301 | 471 | 1132056 |
| add | 1,387,221.8 | 341 | 771 | 1012 | 76532 |
| cancel | 3,015,845.0 | 230 | 421 | 611 | 98365 |
| depth_snapshot | 6,878,022.6 | 161 | 240 | 451 | 91455 |
| event_copy_add | 4,906,376.4 | 190 | 271 | 371 | 49342 |
| event_copy_snapshot | 8,611,265.3 | 170 | 181 | 250 | 2144 |
| execution | 1,111,528.4 | 290 | 871 | 1272 | 225963 |
| payload_copy | 425,956,738.8 | 20 | 30 | 31 | 1912 |
| replay | 56,776.6 | 7261 | 15934 | 119516 | 5037815 |
| execution_tca | 682,885.9 | 1002 | 1522 | 2064 | 1691880 |
| flow_analytics | 852,184.2 | 931 | 1433 | 2183 | 2752882 |
| simulation | 109,648.4 | 5238 | 37876 | 66047 | 111524 |

Interpretation: these are separate bulk and serial-service passes. No outside
arrival queue or exchange/network path is timed. Book-analytics repeats an immutable
depth1 snapshot; flow repeats two quotes/one trade; simulation uses32 initial makers
and128 IOC takers; execution_tca times plan+cost calculation on a validated simulated
parent, not the entire simulation. Event-copy and payload-copy rows have different
semantics. Small-case headline throughput is not evidence of real-market capacity.
Seven repetitions and finite nearest-rank percentiles do not establish tail
probability under another load. The flow/simple-return formulas are exact; that
says nothing about predictive alpha, causal impact or model fit.

Python repeat: median **678.536 events/s**; p50 **1,369,586ns**, p95 **2,687,805ns**,
p99 **4,286,449ns**, worst **77,180,132ns**,1,792 service observations. Includes
schema validation, canonical immutable document construction, conversion, native
validation and journaling. Comparing it with a bare C++ Add benchmark would be
misleading. No gain or regression is attributed to implementation changes: the
implementation did not change, and host noise/configuration differences remain.

Native post-exec VmHWM in this run: book/replay group67,428,352 bytes;
book analytics2,420,736; flow2,560,000; simulator2,310,144; execution/TCA2,248,704.
Wait-accounted RSS for small native children retained a10,223,616-byte worker floor;
it must not replace the native VmHWM values. Both include driver/setup/export work,
not solely engine storage. PMR excludes external allocator overhead and Python heaps.
RSS high-water is not post-churn resident memory or a fragmentation estimate.

The 256-order Python benchmark reports native PMR live4,109,064 bytes,
peak6,137,608,787 allocations and268 deallocations after each bulk pass. This
corroborates the large journal-entry representation; it does not establish a leak.
Native tests/fault sweeps verify teardown for their workloads. Measure larger
histories and repeated reuse before asserting scalability (F06,F08,F10).

Reproduce size evidence with an ignored file and current compiler:

```cpp
#include <iostream>
#include "gig/replay/replay.hpp"
int main() {
    std::cout << sizeof(gig::MarketEvent) << ' '
              << sizeof(gig::JournalEntry) << ' '
              << sizeof(gig::RestartPlan) << ' '
              << sizeof(gig::ReplayConfig) << '\n';
}
```

```sh
g++ -std=c++20 -Iinclude build/institutional-audit/sizes.cpp \
  -o build/institutional-audit/sizes
build/institutional-audit/sizes
# 12208 15944 3720 4824 (the audit driver prints named fields)
```

These sizes are toolchain/ABI-specific, not a serialization layout contract. A
runtime supporting100,000 journal records could require ~1.59GB just for entries;
that is a calculation, not a newly executed100,000-record memory experiment.
An actual run can hit a configured resource budget earlier and correctly reject.

## Security and operational assessment

Useful protections exist: exact builtin-type codecs, enum/range checking, duplicate
JSON key rejection, byte/depth/list caps, no eval/pickle, safe export filenames,
no-overwrite finalization, retained hashes, read-only verification, owned Python
results and native allocation budgets. API error envelopes are allocated before
mutations can commit (`python/bindings/wire.hpp:143–144`). Those are meaningful
protections; they do not replace the missing provenance consistency checks.

Operational failure behavior is explicit and conservative for an offline library:
sequence gaps poison continuity until complete recovery; allocation failures return
structured errors and preserve committed logical state. Journal bucket/capacity
changes on failure are not promised to roll back. Bounded ledger/history/priority
counters reject exhaustion; they do not support indefinite service uptime.

Missing production facilities are conditional requirements, not silently failed
promises: persistent restart/corruption policy, service health/latency observability,
operator runbooks, failover, bounded backpressure, authentication/authorization for
external services, deployment/rollback controls, time synchronization monitoring,
order/risk/credit checks, kill switches and broker/venue reconciliation. None should
be implemented merely because an offline research audit mentions them. If live
execution is ever authorized, they become a separate safety-critical project with
specific requirements, independent review and operational testing.

Data rights, dataset/version identity, raw/derived artifact mapping and out-of-sample
research traceability require real evidence. Hashes do not establish licenses,
source authenticity or complete lineage. No licensed observed dataset was consumed
by this audit. No private market connectivity, credentials, paid resources or public
artifact publication were used. No source credential values were inspected. Existing
advisory/license reports are historical snapshots, not freshly certified security.

## Unverified claims and evidence needed

| Claim | Current defensible position | Evidence needed before strengthening it |
|---|---|---|
| “The engine is correct” | Tested transitions/formulas pass; R1–R4 expose holes | Fix/regressions, expanded independent malformed/stateful corpus and bounded fuzzing |
| “Research outputs have complete provenance” | Fields/hashes exist; F02/F03 contradict full consistency | Shared reference resolver and known-digest contradiction tests |
| “Latency simulation gives a causal client state” | Delivered-time filtering exists; maker reports incomplete | F01/F12 reconciliation of every owned order under races |
| “Microprice/OFI predict returns or measure impact” | Formula implementation only | Licensed dataset, ex-ante availability, time splits, dependence-aware uncertainty and calibration |
| “It handles real market data” | Validated generic canonical event boundary | One explicit source decoder, conformance captures, corrections/session mapping and independent reconciliation |
| “It scales to large L3 histories” | Book configured large; tested workloads smaller, recovery64 and journal large | Cardinality/history/churn/recovery curves with actual RAM/time and budget outcomes |
| “p99 latency is suitable for execution” | Scoped finite serial observations only | Defined arrival/load/system boundary, queueing/drops and uncertainty; no firm-specific threshold assumed |
| “Sanitizers are clean” | Actual rerun scopes pass | Native broader paths; Python late-finalization outcome separately isolated/verified |
| “CI is green” | Workflow defined, available local matrix rerun; API blocked | Hosted job links/artifacts for exact baseline |
| “Portable Python3.9–3.12/ARM64” | Only3.12/Linux x86_64 locally exercised for bindings | Actual native interpreter/platform matrix; distinguish cross-compilation from execution |
| “Crash recovery is supported” | Explicit in-memory recovery only | Restore protocol, process/storage fault injection, restart equivalence |
| “Terminal integration is ready” | Standalone contract/package exist | External consumer corpus and later authorized adapter acceptance, without coupling builds |
| “Dependencies are secure/licensed for release” | Pinned snapshot/notice inventory; no release authorized | Updated advisory/SBOM/license and redistribution review with reproducible artifact identity |

## Dependency-aware roadmap — proposals only

No work below was implemented in this audit. Numbered findings are prioritized by
consequence, while actual scheduling must honor the following dependencies.

| Workstream | Findings | Exit evidence | Depends on / sequencing rationale |
|---|---|---|---|
| Restore trust in advertised semantics | F01,F04,F02,F03, then F05 | Maker/taker reconciliation; invalid fill rejection; missing/mismatched source references reject; four audit cases become permanent tests | Decide owned client scope and artifact identity/digest scope before changing model/schema versions |
| Strengthen the independent verification boundary | F11,F12,F14,F25 | Minimized adversarial corpus, both-side timed report oracle, explicit completeness evidence and readable contracts | Behavioral contracts above; make this protection precede representation optimization |
| Correct experiment metadata and broaden evidence | F18,F17,F10 | Actual selected compiler identity, mixed/size/churn/arrival experiments with scopes and raw samples | Can begin independently as a proposal; no speed target or optimization claim until measured |
| Improve memory/scale only where supported | F06,F07,F08,F09,F16,F22 | Canonical and semantic equivalence; allocation failure safety; bytes/event/scaling and larger snapshot recovery | Independent corpus and before-change measurements; evaluate one bounded change at a time |
| Establish distribution/consumer confidence | F20,F21,F23,F24 | Hosted evidence, supported-version installs, exact consumer conformance and dependency artifact review | Stable contracts F02–F05; use existing resources; native ARM only when available |
| Establish empirical research relevance | F13, optionally F15 | One reconciled licensed dataset; causal/out-of-sample study; honest calibration uncertainty | Input correctness/provenance/clock evidence and an explicit research question |
| Consider operational durability only if scope changes | F19 and separately specified operational controls | Defined failure model and restart/operational acceptance under faults | Explicit user authorization and intended deployment requirements; not a portfolio checklist to implement now |

Fix first: the four audit counterexamples and latent compiler metadata defect.
Defer: optimized containers, queues, zero-copy interchange, new adaptive policies
and large-feed recovery until correctness/reference tests and representative profiles
show why they are needed. Do not build: live trading, broker integrations, a dashboard,
Terminal dependencies, distributed microservices, lock-free structures, custom
allocators or ML/advanced estimators just to resemble a trading firm. Do not broaden
scope to production without requirements, data rights and explicit authorization.

## Research-grade versus production-grade expectations

| Concern | Defensible offline research standard | Additional production execution requirement, if ever authorized |
|---|---|---|
| Market model | Explicit bounded rules and known unsupported mechanics | Venue-specific conformance, full lifecycle/reconciliation/correction behavior |
| Correctness | Independent state/math references, negative cases and reproducible runs | Risk-critical acceptance, exhaustive relevant fault classes, operational monitoring and controlled change management |
| Data and causality | Retained source evidence, assumptions, unavailable states and ex-ante studies | Trusted feeds, loss/reorder/resync policies, monitored clocks and service-level correctness |
| Performance | Honest scoped experiments and size/load curves | Capacity/queue/backpressure requirements from actual service demand, predictable resource/failure behavior |
| Persistence | Verified reproducible artifacts for batch runs | Crash-consistent restore, corruption handling, failover and operator recovery |
| Security/operations | Bounded local interfaces, license/provenance review | Authn/authz, hardened service boundaries, deployment/rollback/runbooks and incident response |
| Order execution | Explicit synthetic orders and modeled costs | Independent pretrade limits, kill/reconciliation controls, approved venue/broker connectivity |

Current recommendation: describe the repository as a **bounded synthetic research
prototype with meaningful correctness infrastructure and known audit defects**.
It is not yet an empirically validated research platform for observed-market
conclusions, and it is not a production execution system. Some production
capabilities are properly excluded. This distinction does not diminish the work;
it makes its engineering claims falsifiable.

## Quant developer interview readiness

Strong demonstrations already available: defend map/list/hash complexity and
worst cases; explain logical commit versus allocator-capacity rollback; show real
fault injection rather than a mocked success path; distinguish print-only trades
from identified executions; derive integer apportionment and cost identity with
units; explain strict replay ordering and explicit recovery; show the independent
Python Fraction/reference programs and reproduce canonical bytes.

Be ready to explain limitations without borrowing a firm's name as evidence:
why an identified historical execution need not remove the current FIFO head;
why tiny serial benchmark p99 is not network/service p99; why an inline variant
costs12KB even for AddOrder; why exact arithmetic does not make a statistical claim
true; why a complete=true manifest is not sufficient while F02/F03 remain; why
maker reports matter when only the delivered channel is causal; and what caller-
owned PMR lifetime means for a returned native snapshot.

Exceptional engineering evidence would be a small, reviewable sequence of fixes
with permanent independent counterexamples; one venue/source reconciled end-to-end
from licensed raw bytes; a timed-information-set oracle; documented failed research
hypotheses and leakage controls; a measured memory/complexity improvement with
identical outputs; and reliable clean-build/consumer CI artifacts. Explain each
tradeoff and avoid unsupported institutional speed or production-readiness claims.
A grander feature list, uncalibrated impact formulas or cosmetic low-level machinery
would be weaker evidence.

Assessment: credible material for a rigorous systems/research interview, especially
if the author can reproduce and reason through the source. Not yet evidence of
institutional production readiness or of any specific firm's hiring standard.
Prior phase completion claims should be read as bounded deliverable acceptance;
this audit supersedes any implication that they establish absence of defects.

## Reproduction appendix and local evidence

Audit logs, JUnit, canonical artifacts and raw samples are in
`build/institutional-audit/`, intentionally not committed. The raw evidence path is
local workspace state, not a promise of persistence after environment replacement.
The following driver is included in this document so the defect evidence can be
recreated without depending on those ignored artifacts. Run from repository root
with the installed `build/phase9-consumer/bin/python` after following the package
reproducibility guide. It calls existing interfaces only. All exported directories
are temporary, and supplied manifests deliberately test acceptance of contradictions.

```python
import sys,json,hashlib,tempfile
from pathlib import Path
from copy import deepcopy
sys.path.insert(0,str(Path.cwd()/'tests'))
import python_fixtures as f
import gig_microstructure as g
# Maker-side visibility: accepted maker completely fills; only taker receives execution report.
s=g.Simulation(f.simulation_config());s.submit('0',f.order(1,'1',100,10));s.submit('0',f.order(2,'0',100,10,'1'));s.advance('1000');st=s.snapshot()['data']['state']
print('R1',json.dumps({'fills':st['exchange_fills'],'client_fill_orders':[r['order'] for r in st['client_reports'] if r['kind']=='5'],'remaining_orders':st['exchange_orders']}))
# An otherwise valid TCA fill exceeds the declared per-order maximum.
fill=deepcopy(st['exchange_fills'][0]);fill['quantity']='11';rules=f.rules();rules['maximum_quantity']='10'
c={'run_id':'cost-run','simulation_run_id':'python-simulation-run','rules':rules,'side':'0','target':'20','arrival':f.benchmark(100),'terminal':f.benchmark(104,1000),'as_of':'1000'}
rows=[{'fill':fill,'child':'2','decision_time':'0','decision_benchmark':f.benchmark(100),'fee_ticks_per_lot':f.ratio(0)}]
print('R2',json.dumps(g.transaction_costs(c,rows)['data']['result']['summary']))
# Build a schema-valid manifest with no inputs, then export a missing VWAP profile.
info=g.native_build_info()
def manifest(schemas):return g.run_manifest({'run_id':'python-simulation-run','code':{'commit_sha':'ccc86d3822e4cfddd4bcd2a086dd7e779602a91d','dirty':False,'source_tree_sha256':'a'*64},'build':{'compiler':info['compiler'],'flags':info['config_flags'],'architecture':'x86_64','os':'Linux','dependencies':{'pybind11':'2.13.6'}},'inputs':[{'identity':'unrelated-input','sha256':hashlib.sha256(b'x').hexdigest(),'license_reference':'synthetic','origin':'synthetic','source':'test','transformation':'generated','local_file':None}],'parents':[],'schema_versions':schemas,'instrument_rules':[f.rules()],'policies':{'ordering':'capture ordinal','sequence':'strict','recovery':'snapshot','clock':'UTC declared','precision':'ns'},'parameters':{},'seeds':[],'coverage':{'start_ns':f.known('0'),'end_ns':f.known('1000'),'records':'0'},'outputs':[],'errors':[],'complete':True})
plan=g.vwap(f.plan_config(),['1','2','1'],'MISSING-PROFILE','0')
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'vwap';g.export_run(p,manifest({'gig.execution_schedule':'1.0'}),{'plan.json':plan},input_artifacts={'unrelated-input':b'x'});v=g.verify_export(p);print('R3',json.dumps({'complete':v['data']['complete'],'inputs':v['data']['inputs'],'unresolved_profile':plan['data']['profile']}))
# Supplied known dataset hash contradicts the exact retained bytes; exporter checks only identity.
e=f.event();e['data']['metadata']['provenance']['dataset']['value']['sha256']=f.known('0'*64)
m=manifest({'gig.event':'1.0'}).to_dict();m['data']['seeds']=['0'];b=b'actual bytes';m['data']['inputs']=[{'identity':'python-synthetic','sha256':hashlib.sha256(b).hexdigest(),'license_reference':'synthetic-fixture:no-external-data','origin':'synthetic','source':'test','transformation':'generated','local_file':None}]
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'event';g.export_run(p,g.run_manifest(m['data']),{'event.json':g.event(e,f.rules())},input_artifacts={'python-synthetic':b});print('R4',json.dumps({'verification_complete':g.verify_export(p)['data']['complete'],'declared_dataset_sha256':'0'*64,'retained_bytes_sha256':hashlib.sha256(b).hexdigest()}))
# Python semantic validation vs schema-only documents.
invalid=f.event();invalid['data']['payload']['value']['quantity']='0'
print('R5',json.dumps({'schema_only_load_accepts_zero_add':g.loads(json.dumps(invalid))['data']['payload']['value']}))
try:g.event(invalid,f.rules())
except g.EngineError as e:print('R5_NATIVE_REJECT',str(e))
```

### Evidence checksums and preservation

- `build/institutional-audit/reproduce.py`: SHA256 `775c89c1a7845c235074b4d1aa31a9528ad980bdbdec275d5a5e9a4adf9893f8`.
- `build/institutional-audit/reproductions.txt`: SHA256 `b15b07a3cddbe729c0a26ca3606ff1255beed13af3d350935cae1ef426318892`.
- `build/institutional-audit/native-baseline/manifest.json`: SHA256 `436a5e1f6f617d7553aaf1156dcea986a4a481f217ee21cd61e59e96519d2d31`.
- `build/institutional-audit/python-baseline/manifest.json`: SHA256 `44f6914aa69052e98b2325d292cd8c24f27725dd166c34843ec84b82a81fcccc`.

The loaded installed facade was byte-compared with baseline Python source, and
the loaded native binary was byte-compared with the previously validated local
sdist-built wheel. The reproduction therefore exercises the audited interface,
not a newly edited implementation. All nine existing compiler/binding suites and
the fresh Release suite have zero failures/skips/disabled outcomes in saved JUnit.
Remote development HEAD was rechecked as the baseline; main remains
`165c5038336887116d69160b0d8e5a1a5ef59d16`. The audit document is left uncommitted
for review, with no source changes or history mutation. Implementation requires
new authorization; this audit stops here.

## Correctness remediation addendum — original audit preserved

The preceding audit is preserved verbatim (original SHA256
`4c3837cd33a1be9621716d7073eb8d2e32a6624c39b624cf7824a7545e819889`).
Its source ranges and defect statuses describe baseline
`ccc86d3822e4cfddd4bcd2a086dd7e779602a91d`, not the later remediation.

Targeted F01 maker reports, F04 TCA quantity boundaries, F02 retained VWAP/POV
references, F03 known event dataset/parent digest consistency and F18 compiler
selection are repaired in the subsequent remediation change. Original failures
were reproduced and failing-before regressions retained; see
CORRECTNESS_REMEDIATION.md for roots, exact tests, validation outcomes and commit
traceability. This is not closure of every recommendation in those broader audit
cards: empirical calibration, arbitrary external graph completeness, journal
scalability, fragmentation, native ARM, hosted evidence and production durability
remain separately unverified/missing as described above. No roadmap optimization
or new development phase is implied by these correctness repairs.

The resumed user instruction additionally authorizes the newly identified fixture
RNG portability repair. Generator v2 explicitly sequences quantity then price,
preserving established GCC price/quantity values while removing argument-order
dependence across compilers. New independent fixture reference coverage and full
canonical benchmark comparisons are included in CORRECTNESS_REMEDIATION.md. This
is an authorized reproducibility repair, not the start of a storage optimization
or the next roadmap phase. The original audit prefix remains unchanged.
