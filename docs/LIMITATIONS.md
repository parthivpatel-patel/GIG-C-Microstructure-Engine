# Limitations and truth boundaries

Phase 2 implements a single-owner, single-instrument/venue reconstructed book and
strict multi-stream replay. See PHASE_2_BOOK.md and PHASE_2_REPLAY.md for exact scope,
mutation, sequence and recovery rules. It never matches incoming orders.

No analytics, synthetic matching, execution simulation, Python bindings, GIG Terminal
integration, real-feed adapter, broker connection or live trading is implemented.
No exchange certification: auctions, hidden/iceberg/pro-rata/pegged priority, routing,
STP, atomic transient-crossed message bundles and exchange-specific corrections are
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
Native ARM64, local Clang, Windows and macOS remain unverified. Hosted CI evidence
must be reported separately from local tests; inaccessible checks are not successes.

IMPLEMENTED != VERIFIED; BENCHMARKED != FAST; SYNTHETIC != OBSERVED;
LOCAL_TESTED != PRODUCTION_VALIDATED.
