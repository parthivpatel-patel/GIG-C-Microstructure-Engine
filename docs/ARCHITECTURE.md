# Approved architecture — Phase 0B

Status: architecture approved; bootstrap partially implemented. The event model,
LOB, replay, analytics, simulation and integration implementations are NOT IMPLEMENTED.
The existing numeric aliases and AddOrder are a temporary scaffold, not strong contracts.

## Priorities and boundaries

MUST HAVE: C++20, checked strong integer units, validated events, deterministic
single-owner replay, order-level reconstruction, immutable snapshots, correctness
checks, reproducible benchmarks and versioned provenance. SHOULD HAVE: flow
analytics, offline execution research, Python bindings. LATER / EXPERIMENTAL:
calibrated queue inference, impact estimators, optimized storage and concurrency.
No live trading, broker connectivity or terminal build dependency.

Inputs -> validated canonical journal -> replay -> reconstructed book -> snapshots
and analytics. Queue/latency and execution simulation consume explicit inputs and
produce separately labeled simulated results. Historical feed reconstruction does
not automatically match orders. A separate synthetic matching model prevents
counting feed executions twice. Quote-only data cannot establish order FIFO.

## Ownership and baseline storage

One owner mutates a book. Ordered price maps, FIFO lists and a scoped ID index form
the proposed correctness baseline: O(log L) level lookup, expected O(1) ID lookup
(linear worst case), O(D) aggregated depth snapshot, O(N+L) memory with node and
allocator overhead. Partial fills retain priority; same-price quantity reduction
retains priority; increases and price/side changes lose it in the initial model.
Intrusive pools, dense ladders and flat containers remain measured alternatives.
No storage implementation exists yet.

## Decisions and evidence

See decisions/0001-approved-contracts.md for mandatory atomic mutation,
multi-stream ordering, provenance and baseline gates. See MARKET_MODEL.md for
units and exclusions, VALIDATION.md for test gates, BENCHMARK_METHODOLOGY.md for
measurement, and GIG_INTEGRATION.md for the future consumer boundary.

All major components must document purpose, assumptions, complexity, memory,
alternatives, failures and tests. Interview rationale: simple deterministic
ownership makes transitions auditable; performance claims require measurements.
