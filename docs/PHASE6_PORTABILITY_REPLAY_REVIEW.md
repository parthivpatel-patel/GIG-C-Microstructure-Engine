# Phase 6 portability and replay review — October 24, 2026

No production defect reproduced; no warning suppression or speculative optimization.
The GCC13 Release fixture repair remains intact. The prior seven-configuration
1081-outcome repair qualification is preserved, not relabeled as new execution.

Source reviewed: core numeric/contracts, replay reserve/reset/recover/canonical,
ITCH framer/decoder/context/reconstruction/restart/gzip/streaming and prior Python
boundary audits. Strong types/exact arithmetic remain unchanged. PMR objects must
outlive consumers; default engine move retains owned vectors and stable indices.
Bounds checks precede frame copies, integer byte decoding avoids unaligned typed
loads, and gzip's max_align_t allocation header preserves zlib allocation alignment.
Gzip byte-pointer adaptation is the existing C API boundary, not a new typed alias.
Journal growth arithmetic remains bounded by100000 records. No new pointer or
iterator is retained across growth. Complete source/native context initialization
and crash durability remain unsupported rather than inferred from native snapshots.
These are source-review conclusions and bounded tests, not proof of absence of UB.

New journal regressions strengthen failure atomicity: accepted record and restart
plan counts must remain unchanged after injected allocation failures, while reserved
capacity may grow. Exactly one plan follows successful retry. A separate32-cycle
fixture alternates complete native snapshot recovery and resets, moves the engine,
checks independent quantities/sequence/source counts, and destroys all state after
each cycle.4128 accepted events;4727264 peak PMR bytes;35552 successful allocations
and35552 deallocations, zero live blocks/bytes after every cycle in focused Debug.
This is allocator churn/release evidence, not a measurement of libc fragmentation.

Controlled scaling uses unchanged production binaries from the qualified core:
GCC14.2 andClang19 Release, lengths4097/8191/8192, no resets/reset every64/all resets,
one separate warmup and3 measured processes/case:54 measured runs. The byte ledger
independently reconciles both vector capacities and every process releases all PMR
storage. Physical ordinary records remain12232, reset plans3720, logical DTO15944.
Raw command/binary identity, RSS, used/reserved bytes, allocations and elapsed samples
are in build/phase6/evidence/journal-{gcc,clang}-scaling.json. Shared-host timings
and pre-exec RSS floors are not causal performance or fragmentation evidence.
No additional journal compaction is justified by this review; inline metadata and
snapshot alternatives still dominate remaining costs, with a separate equivalence
and migration plan required before any replacement.

Final compiler/sanitizer execution is recorded separately in the Phase6 report.
New tests use bounded value construction and indices; no compiler-specific pragma,
packed layout, alias trick or API/schema change is introduced.
