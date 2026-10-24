# Phase 6 completion report

Objective: causal offline execution planning, participation/inventory limits and exact
transaction-cost research. Verified clean start:
`1f747482b664f6437a5ce10cedc4809d30cf3683`.
End implementation: `a5340f99dbac1dca6cc187086e374d3827fee04c`, normally pushed
and exact remote SHA verified. Evidence/report commit is this document's containing
Git commit; next report records the full phase-boundary SHA.

Implemented: largest-remainder exact-lot TWAP/VWAP, explicit forecast availability
and hindsight-oracle labeling, causal prefix-stable POV, configurable limit/TIF/
max-child/time grid, directional inventory/target/participation caps, validated
owned simulation integration, and exact execution VWAP/notional/delay/spread/fee/
slippage/opportunity/implementation-shortfall/currency reports with full parents.
See PHASE_6_CONTRACTS.md for equations, units, assumptions, precision, invalidity,
complexity, memory, alternatives and interview rationale. Simulated execution stays
distinct from historical reconstruction; Terminal unchanged, no broker/live orders.

Actual local final results: Debug 61/61 (4.05s), Release 61/61 (1.12s), ASan+UBSan
61/61 (14.67s), zero failures/errors/skips and no reported sanitizer findings.
Independent Python Fraction: 2600 apportionment/POV/buy-sell cost cases, seed6011.
Hand checks include full uint64 weighted products, ties/grid/splits, future-profile
rejection/oracle labels, POV prefix invariance, ID/capacity/inventory boundaries,
empty fills, maker/taker attribution, causal quotes/reports, duplicate fills,
sell/rebate signs, forged-plan rejection and actual simulation integration.
Real PMR fault sweeps reached six planner and 42 integrated-run positions; every
failure returns no partial run and zero leaked selected-resource bytes. TCA output
allocation failure is separately checked. All inherited regressions remain enabled.

Raw clean-code Release benchmark: baselines/phase6-execution-tca.json, complete
actual parent simulation canonical/hash plus declared plan/fee/midpoint assumptions,
code/build/CPU/seed and every repeated raw sample. Runner reran all 61 Release tests.
Timed operation is TWAP planning + one-fill TCA, not simulator setup/matching/export.
Two warmups, seven 5000-operation bulk passes and 35000 service samples. Hand result:
buy20/fill10 at103, arrival100/decision102/terminal104, fee1/10 -> shortfall71 tick-lots,
71/100 currency. Observed median 675,767 operations/s;
p50/p95/p99/worst observed 1002/1562/3976/455170 ns.
Selected PMR counts across all 80000 warmup/bulk/service calls: 560000 successful
allocations, 560 peak requested bytes, zero live bytes after owners. Excludes upstream
overhead and driver allocations. Fixed shared-cloud fixture, no production speed claim.

Hosted Actions remains UNVERIFIED (GitHub API proxy CONNECT403); equivalent local
GCC checks pass and mandate permits continuation. Local Clang/native ARM still
unverified. Modeling risks: forecasts need authenticated availability outside this
library; labels cannot certify them. POV caps submitted volume conservatively and
can underexecute after IOC misses; no resubmission/optimization/portfolio margin.
Latency may leave in-flight orders/reports beyond finish; completion is not an
inventory fill guarantee. Fees/benchmarks are supplied synthetic assumptions, not
calibrated exchange economics. No hidden liquidity/adverse-selection/impact fitting.
Exact intermediate capacity and caller PMR lifetime remain explicit limits.

Acceptance: implementation/contracts, independent/hand references, unit/regression
checks, Debug/Release/sanitizers, real allocation rollback, provenance, relevant
baseline, diff review and normal remote durability PASSED. Hosted evidence unavailable
and disclosed. Phase 6 complete; automatically continue Phase 7 common-code baseline,
allocation/peak memory/event-copy measurement and profiling. No optimization will be
claimed without a justified comparable before/after result.

Changed files:

- `CMakeLists.txt`
- `README.md`
- `benchmarks/CMakeLists.txt`
- `benchmarks/execution_benchmark.cpp`
- `docs/PHASE_6_CONTRACTS.md`
- `docs/PHASE_6_REPORT.md`
- `docs/baselines/phase6-execution-tca.json`
- `fixtures/synthetic/execution.hpp`
- `include/gig/execution/execution.hpp`
- `scripts/check_execution_reference.py`
- `scripts/run_research_benchmark.py`
- `src/execution/execution.cpp`
- `tests/test_execution.cpp`
