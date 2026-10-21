# Reproducible scaffold baseline

## Scope and correctness gate

Phase 0B measures ONLY the existing AddOrder field validator. It does not measure
book mutation, matching, replay, analytics, order throughput or economic outcomes.
No storage/event implementation or optimization is introduced.

Deterministic xorshift64 fixture version 1, seed 42, has eight repeating categories:
valid buy, valid sell, zero ID, zero price, negative price, zero quantity, zero
sequence, valid extreme values. The independent construction labels determine
expected answers; every event and each batch are checked outside timing. The
original validator intentionally remains unchanged, including its known enum gap.
The harness is not a claim that the event contract is complete.

The timed function lives in a separate translation unit; IPO is disabled. It
counts validation successes over preallocated input. No input generation, oracle,
I/O or manifest serialization is timed. Result counts are consumed and checked.
Current baseline: 262144 records, 64 batches/repetition, 2 warmup repetitions,
7 measured repetitions, one thread. Bound all CLI sizes to avoid overflow and
unbounded allocation; invalid CLI arguments fail. FNV-1a hashes explicit
little-endian field encodings, never padding; it is not a security hash.

## Reproduce from repository root

```sh
cmake --preset release
cmake --build --preset release
ctest --preset release
python3 scripts/run_benchmark.py --output build/baseline.json
```

The runner rebuilds and reruns all tests before measuring. It refuses non-Release,
sanitized builds and existing output paths. A run is published atomically only on complete
success (same-filesystem hard link; Linux target). It records Git SHA/dirty state, source/executable/result SHA-256 hashes,
workload version/fingerprint/seed, exact raw samples, compiler/version, standard-library version and commands,
flags, generator, CMake, CPU/architecture, OS/kernel, affinity, available CPUs,
clock, warmup, repetitions and thread count. Source and Git state must remain
unchanged during measurement. Source hashes also disambiguate dirty experiments.
The checked-in compact baseline is necessary reproducibility evidence, not a
build output. It records the earlier clean benchmark implementation commit.

Report median batch throughput and raw duration range. Batch-derived ns/event is
not an observed per-event latency distribution. No p50/p95/p99 event latency,
allocation, RSS, venue latency or speedup is claimed. CPU isolation and frequency
are uncontrolled in this shared cloud; do not compare noisy runs as proof of an
optimization. Hardware/standard-library selection is visible in compile commands
and compiler identity; portability remains separately unverified.

## Future performance gates

Before optimizing any new component, establish its own oracle-validated baseline,
including invariants, deterministic replay and relevant sanitizer checks. Reuse
identical workloads for candidates and prove semantic equivalence. Later measure
parser/end-to-end replay, LOB, snapshots, analytics and simulation separately,
record active-order/depth/event-mix distributions, allocations and peak memory.
Define event service vs queueing latency, arrival schedule and timer overhead;
report p50/p95/p99/worst observed latency with adequate samples, raw repetitions
and coordinated-omission controls. Throughput is never reciprocal latency.
No target values or production-readiness claims are assumed.
