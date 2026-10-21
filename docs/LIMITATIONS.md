# Limitations and truth boundaries

Phase 1 implements strong types and self-contained event validation; no stateful
book/replay checks exist. See PHASE_1_CONTRACTS.md for exact required metadata,
128-byte ASCII token, 8-lineage/parent and 64-snapshot-entry capacity limits.
Inspect-incomplete validation is not replay readiness. Missing timestamps and
checksums are explicit; digest syntax is not content verification or authenticity.
No serialization or stable wire ABI is implemented.

No LOB, matching, replay, analytics, execution simulation, Python, GIG integration,
market-data adapter or broker connection exists. Order-ID uniqueness across events,
FIFO, fills/cancels, sequence continuity and full provenance graph validation await
later phases. Validation does not certify exchange semantics. Shared-cloud payload
benchmarks are not engine throughput and are not comparable to old scaffold timing.
Native ARM64, Clang locally, Windows and macOS are unverified.

IMPLEMENTED != VERIFIED; TESTED != NUMERICALLY_VERIFIED; BENCHMARKED != FAST;
SYNTHETIC != REAL; SIMULATED != OBSERVED; LOCAL_TESTED != PRODUCTION_VALIDATED.
No live trading, secrets, restricted datasets or hidden network behavior.
