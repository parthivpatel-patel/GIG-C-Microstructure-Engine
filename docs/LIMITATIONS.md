# Limitations and truth boundaries

Implemented through Phase 9: single-owner reconstructed book/replay, exact book-state
and causal flow analytics, separate offline synthetic matching/latency, exact-lot
TWAP/VWAP/POV and TCA. See each PHASE_n_CONTRACTS.md and reports for evidence.
Historical replay NEVER matches. Simulator fills are always synthetic/simulated.
Optional Python bindings and versioned GIG consumer schemas are implemented.
Real-feed adapters remain future work.
No live/broker/Terminal integration or released production interface.

No exchange certification: auctions, hidden/iceberg/pro-rata/pegged priority, routing,
STP, atomic transient-crossed reconstruction bundles and exchange-specific corrections are
unsupported. Channel-local order IDs need an explicitly reviewed adapter mapping.

Replay defaults to requiring a complete order snapshot; declaring empty is an explicit
input assumption. Recovery retains Phase 1's 64-order/8-boundary capacity. Aggregate
or bounded-depth snapshots cannot establish FIFO. Dataset/stream identities cannot
silently change. Missing clocks cannot support timestamp-ranked ordering. Strict
ordering rejects errors; there is no buffering, reordering or message fabrication.

The accepted-event journal is owned in memory and bounded by record/resource limits.
Full event records are large; allocation/retention/copy costs are measured, not optimized.
Journal capacity may grow on an otherwise failed operation; committed logical state
remains unchanged. No disk transaction, restart log or crash-durability guarantee.
Canonical output is an internal versioned representation, not a stable wire ABI/parser.
Low-level book depth/latest metadata alone are not full research lineage; retain the
replay journal and run manifest. Metadata validation does not certify external data
completeness, content digests, licensing, authenticity or the provenance graph.

Debug scans invariants after every mutation; Release tests and benchmark preflight
scan explicitly. PMR counts exclude allocator overhead and driver allocations. Peak
RSS includes fixtures, oracle, timing arrays and driver. Shared-cloud synthetic
measurements do not establish production, real-feed or ultra-low-latency performance.
Native ARM64, Windows and macOS remain unverified. Local x86_64 GCC14 and
Clang19 are tested; no native ARM or cross-compilation claim. Hosted CI evidence
must be reported separately from local tests; inaccessible checks are not successes.

IMPLEMENTED != VERIFIED; BENCHMARKED != FAST; SYNTHETIC != OBSERVED;
LOCAL_TESTED != PRODUCTION_VALIDATED.

Flow analytics need declared common UTC clocks and complete sequences/top updates;
quote/tick signs are estimates, not observed aggression. No Kyle/VPIN calibration.
General exact fractions require GCC/Clang 128-bit support and bounded intermediates;
volatility sqrt is approximate long double. Simulation uses assumed discrete-uniform
latencies and full bounded State clones; exchange truth is not the delayed client
information set. Execution schedules cap submitted inventory and may underexecute;
VWAP forecasts need ex-ante availability, hindsight profiles remain oracle-labeled.
TCA fees/midpoints/opportunity conventions are supplied assumptions, not calibrated
adverse selection/impact/hidden liquidity. See PHASE_4/5/6_CONTRACTS.md.

Linux wait-accounted RSS may include an inherited pre-exec worker floor. Phase 7
also records native /proc VmHWM after exec; neither includes only engine data.
No optimization is inferred from different-phase/flag/workload/noisy timing results.

Python sanitizer coverage uses active-interpreter leak checks plus a positive
leak-detection control; late interpreter-finalization leaks remain unverified.
See PHASE_8_REPORT.md for the isolated CPython shutdown issue and exact settings.
Only CPython3.12/Linux was exercised; other declared compatible Python versions
are not locally validated. Local wheels are private artifacts, not published releases.
