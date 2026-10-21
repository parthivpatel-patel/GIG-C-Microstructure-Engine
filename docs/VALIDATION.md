# Validation and acceptance gates

## Bootstrap commands

Requires CMake >=3.20, Ninja and GCC or Clang with C++20. No network downloads occur
at configure/build time. From the repository root:

```sh
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
cmake --preset release
cmake --build --preset release
ctest --preset release
cmake --preset asan-ubsan
cmake --build --preset asan-ubsan
ctest --preset asan-ubsan
```

The inherited Phase 1 checks include: 2 numeric groups (including 10624
independent Python integer/Fraction cases), 11 event-contract groups, 11 migrated
scaffold boundary cases, 1 demo, 1 benchmark correctness case and 3 negative checks.
Each negative check requires exit 1 and its intended diagnostic, rejecting crashes
and sanitizer findings. All runtime assertions remain active under NDEBUG.
Event groups test all eight variants, metadata/provenance ownership, enum rejection,
snapshot duplicates/capacity and input preservation. No zero-test run is accepted.
No event serialization/canonical wire representation is included in Phase 1.

Warnings are private to project executables. ASan/UBSan abort on findings and use
frame pointers; no suppressions. TSan has a separate configuration switch but is
not a Phase 0B acceptance target because no concurrent code exists. Sanitizer
support is gated to GCC/Clang; actual runtime/platform support still needs testing.

## Phase 2 validation

Presets now register 48 CTest outcomes: 29 inherited checks, 7 book groups,
11 replay groups and one correctness-only book benchmark smoke. All use active
runtime checks under NDEBUG. The book oracle executes 20000 deterministic operations
with seeds 1/42/1729/999 and 1318396 assertions. Actual PMR failure injection reaches
34 book and 30 replay allocation positions. Reference comparisons include exact
orders, FIFO, aggregate depth, ledger and invariants after each randomized operation.
Replay covers both ordering policies, subevents, filtering, gaps, duplicates,
regressions, exhaustion, scope/reset/recovery and accepted provenance/canonical bytes.

The benchmark runner reruns the complete Release suite before measurements, checks
its workload against the independent oracle, records raw samples/source hashes/code
SHA, and rejects source changes during the run. See PHASE_2_BENCHMARKS.md.

## Phases 3–6 additions

Presets now execute 61 CTest outcomes: the Phase 2 48 plus two book-analytics groups,
two flow groups, five synthetic-simulation groups and four execution/TCA groups.
Independent Python references: 2650 exact book cases (seed3071), 2000 exact flow
cases (4099), 1000 matching/cancel states (5/42/1729/2027), and 2600 execution/cost
cases (6011). Allocation injection additionally reaches two flow, 28 simulation,
six planner, 42 integrated-execution and one TCA output position. Every inherited
book/replay and arbitrary-precision numeric reference remains active. See phase
reports for actual results and correctness-gated benchmark scopes.

## Phase gates and final evidence

Phase 1 IMPLEMENTED: strong types, exact conversion, malformed events, checked arithmetic.
Phase 2 IMPLEMENTED: FIFO/conservation/index invariants, independent reference book,
seeded streams, canonical replay, sequence recovery and allocation fault injection.
Phase 3 IMPLEMENTED: independent exact book metrics and unavailable states.
Phase 4 IMPLEMENTED: OFI/signing assumptions, causal horizons and sampling.
Phase 5 IMPLEMENTED: separate matching, cancellation races and seeded latency.
Phase 6 IMPLEMENTED: schedule constraints, inventory/cost reconciliation, no look-ahead.
Phase 7 VERIFIED locally: common correctness baseline/profile; no justified optimization,
so before/after optimization comparison is inapplicable; concurrency remains absent.
Phase 8 VERIFIED locally: 63 Debug/Release outcomes including schema/Python checks;
64 GCC ASan/UBSan outcomes including the active-leak positive control. Late Python
finalization leaks are excluded explicitly, not suppressed.
Phase 9: fresh x86_64 GCC/Clang validation and standalone packaging/reproduction;
native ARM64 unavailable and not tested. See FINAL_REPORT.md for actual outcomes.

Every coherent checkpoint: inspect diff, test, review, commit, push designated
private development branch, compare remote SHA exactly; only then continue.
Never force-push, rewrite published history or merge main without approval.

## Correctness remediation follow-up

Current suites have65 native CTest outcomes in each GCC/Clang Debug/Release/
ASan+UBSan configuration,68 with ordinary optional Python and69 with Python ASan.
New coverage includes both-side client reports, TCA quantity limits, consistent
retained export references/digests, selected-compiler metadata and a16-case independent
fixed-width RNG fixture reference. Historical phase counts above remain historical.
See CORRECTNESS_REMEDIATION.md for actual results, intentional v2 canonical/generator
changes, raw-evidence hashes and unchanged sanitizer/platform qualifications.
