# Phase 5 completion report

Objective: separate deterministic offline synthetic matching/latency, never historical
feed matching. Start, clean local/remote verified:
`dee6ff3869bd8692f3e484a696d338eb7b1736da`.
End implementation: `bc9a1b57c6ce138ebefcd8d0bba98366258f5385`, tested/reviewed,
normally pushed and exact remote SHA verified. Evidence/report commit is the Git
commit containing this document; next report records that phase-boundary SHA.

Implemented: price-time maker-price matching, seeded event/arrival scheduling, FIFO
queue positions, partial/full fills, cancel races, marketable limits, GTC/IOC/FOK,
post-only GTC, independently configured arrival/cancel/ack/execution-report delays,
client reports filtered by delivery time, complete simulated command/fill lineage,
exact conservation and atomic whole-command staging. Mathematical/engineering/model
contracts, complexity, ownership, invalidity and interview rationale: PHASE_5_CONTRACTS.md.
Historical book/replay mutation behavior is unchanged; simulator accepts no feed events.

Actual results: Debug 57/57 (3.10s), Release 57/57 (0.76s), ASan+UBSan 57/57 (13.54s).
No failures/errors/skips or reported sanitizer findings. Independent Python sorted-
list matcher: 1000 states, seeds 5/42/1729/2027, compares every surviving order/FIFO
rank, fill and conservation term including cancels and TIF outcomes. Hand examples
cover maker price, priority-preserving partial fill, multi-maker FOK, IOC expiry,
post-only reject, invalid enum/ID/quantity/time, cancel-before-arrival and after-fill,
delayed acknowledgment and report visibility, same-seed deterministic output.
28 actual PMR fault positions across submit/cancel/multi-fill advancement preserve
canonical state, clock/RNG/queue/ledger and live bytes. Query failure and capacity/
near-max quantity/time failures also reject atomically; owners clean up all allocations.

Debug/Release/ASan+UBSan benchmark canonical outputs match SHA-256
`4a6d1b061ca25ef5d9123fc214d8a7282e69c4922c5935d13bfc51c393ed3f45`.
Raw clean-code Release evidence: baselines/phase5-simulation.json. Runner repeats
all 57 tests; embeds complete synthetic canonical command history/seed/hash,
exact code/build/CPU context, two warmups, seven 128-operation bulk repetitions and
896 separate serial service samples. Setup: 32 eight-lot asks, then 128 one-lot IOC
buys, zero assumed delays; one operation includes submit AND advance (two stages).
Reference-checked final state has 128 fills, ledger submitted 384/executed sides 256.
Observed median 63,485 operations/s;
p50/p95/p99/worst observed 5428/19969/148919/657066 ns.
Each bulk repetition used 2558 successful selected-PMR allocations, lifetime peak
368432 requested bytes including setup/staging, zero live bytes at owner destruction.
Driver allocations and upstream allocator overhead are excluded. Shared-cloud finite
samples; no production latency/throughput claim. Archived run executed without other
benchmarks started by this session; host scheduling/frequency remain uncontrolled.

Hosted CI UNVERIFIED due GitHub checks API proxy 403; equivalent local GCC gates
pass and mandate permits continuation. Native ARM64/local Clang remain unverified.
Risks: full-State clone and linear scans intentionally costly; bounded lifetime
history/reports can exhaust even with small live book; timestamp horizon exhaustion
requires a new run; PMR resource lifetime/view invalidation belongs to caller.
Latency distributions are assumed synthetic, not calibrated. Exchange state is model
truth, not a strategy information set: only delivered reports are causal client data.
No STP/agents/hidden liquidity/auctions/venue certification, uncapped market orders,
DAY TIF, live brokers or Terminal changes. No release or main merge/history rewrite.

Acceptance: supported implementation and contracts, independent/hand math, unit/
regression/Debug/Release/sanitizers, real fault injection/rollback, provenance,
benchmark, diff review, normal remote checkpoints PASSED. Hosted evidence unavailable
and disclosed. Phase 5 complete; automatically continue Phase 6 causal offline
execution schedules, participation/inventory limits and independently validated TCA.

Changed paths:

- `CMakeLists.txt`
- `README.md`
- `benchmarks/CMakeLists.txt`
- `benchmarks/simulation_benchmark.cpp`
- `docs/PHASE_5_CONTRACTS.md`
- `docs/PHASE_5_REPORT.md`
- `docs/baselines/phase5-simulation.json`
- `fixtures/synthetic/simulation.hpp`
- `include/gig/simulation/simulator.hpp`
- `scripts/check_simulation_reference.py`
- `scripts/run_research_benchmark.py`
- `src/simulation/simulator.cpp`
- `tests/test_simulation.cpp`
