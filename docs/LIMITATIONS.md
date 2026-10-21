# Limitations and truth boundaries

Only a C++20 AddOrder validation scaffold exists. Its integer aliases are not
strong types; invalid Side enum values are not rejected. Instrument, venue,
timestamps, provenance and sequence continuity are not represented. These are
Phase 1 gaps, intentionally not expanded during bootstrap hardening.

No LOB, matching, replay, snapshots, market analytics, execution simulation,
Python bindings, GIG integration, market data or broker connections exist.
Bootstrap timing is not engine throughput. Native ARM64, Windows and macOS are
not validated. Shared-cloud results do not establish production performance.

IMPLEMENTED != VERIFIED; TESTED != NUMERICALLY_VERIFIED; BENCHMARKED != FAST;
SYNTHETIC != REAL; SIMULATED != OBSERVED; LOCAL_TESTED != PRODUCTION_VALIDATED.
No live trading, secrets, restricted datasets or hidden network behavior.
