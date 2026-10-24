# Phase 4 completion report

Objective: defensible causal trade/quote/flow research metrics, no invented data.
Start (verified clean local/remote): `0620b4c2e48d8aae317143dfecf9ed3185bc3c58`.
End implementation: `a1d0644dff8a3446ac5417f2442234edb566ab99`, normal push and
exact remote SHA verified. The subsequent evidence/report commit is this document's
containing Git commit; Phase 5 report records the exact phase-boundary SHA.

Implemented: top-update OFI, quote/midpoint/tick trade signing with explicit Lee–Ready-
style lag, event intensities, effective/realized spreads, horizon impact, exact simple
window/grid returns and realized variance, approximate finite sqrt volatility. Owned
immutable-access results retain configuration/as-of time and all input context parent
refs. Contracts/formulas/units/clock/lag/age/sampling/capacity/complexity/alternatives:
PHASE_4_CONTRACTS.md. Unsupported Kyle lambda/VPIN remain experimental and unimplemented
because valid calibration/population assumptions are absent.

Actual final local results: Debug 52/52 (3.86s), Release 52/52 (1.03s), ASan+UBSan
52/52 (12.91s), zero failures/errors/skips and no reported sanitizer findings.
Python Fraction independently checked 2000 randomized cases, seed 4099, for OFI,
signing, spread decomposition, returns and variance. Hand tests include quote lag,
equal-time future-prefix exclusion, tick repeats, horizon pending, staleness, clocks,
combined revision/time order, missing sides, gap/reset boundaries, zero midpoint and
sampling divisibility. Both reached PMR allocation positions fail safely with no
input mutation, partial result or leaked bytes. All previous regression tests pass.
Debug/Release/sanitizer flow benchmark smoke runs also passed (timings not evidence).

Clean-code Release baseline reran all 52 tests. Archived raw evidence:
`baselines/phase4-flow-metrics.json`; embeds actual five-record synthetic replay
canonical input/hash, code/compiler/build/CPU, two warmups, seven 5000-window bulk
passes and 35000 separate service samples. Fixed workload has three top states and
one print: OFI 30 lots, effective/realized spread 2/0 ticks. Observed median 722,320 windows/s;
p50/p95/p99/worst observed 932/961/1892/200065 ns.
PMR counters cover all 80000 calls, including warmups and service passes: 160000 successful
allocations, peak 2048 requested bytes, zero live bytes after calls. These are selected
PMR allocations, not process RAM or allocator overhead. Shared-cloud fixed workload,
wrapper/clock/output allocation costs included, no production or latency promise.

Hosted Actions UNVERIFIED due restricted GitHub API access (proxy CONNECT 403).
Equivalent GCC local checks passed; mandate explicitly permits continuation. No
local Clang/native ARM evidence yet. Common UTC synchronization and full top-update/
sequence completeness are declared input assumptions, not authenticated facts.
Input times cannot regress or exceed as-of; reset scopes must be partitioned.
Linear bounded searches intentionally favor correctness over optimization. Exact
128-bit intermediate capacity and approximate sqrt portability remain limitations.
No synthetic matching, execution scheduling, bindings, live trading or Terminal
changes in this phase. Main/history preserved; no release publication.

Acceptance: implementation, mathematical/engineering contracts, independent math,
unit/regression tests, Debug/Release/sanitizers, provenance, benchmark, diff review,
normal pushes and exact remote verification PASSED. Hosted CI unavailable/disclosed.
Phase 4 complete; automatically continue Phase 5 separate offline synthetic matching,
seeded scheduling, queue positions, latencies and cancel races. Never feed simulated
fills back as observed historical executions.

Changed files:

- `CMakeLists.txt`
- `README.md`
- `benchmarks/CMakeLists.txt`
- `benchmarks/flow_benchmark.cpp`
- `docs/MICROSTRUCTURE_METRICS.md`
- `docs/PHASE_4_CONTRACTS.md`
- `docs/PHASE_4_REPORT.md`
- `docs/baselines/phase4-flow-metrics.json`
- `include/gig/analytics/book_metrics.hpp`
- `include/gig/analytics/flow_metrics.hpp`
- `scripts/check_flow_metrics.py`
- `scripts/run_research_benchmark.py`
- `src/analytics/flow_metrics.cpp`
- `tests/test_flow_metrics.cpp`
