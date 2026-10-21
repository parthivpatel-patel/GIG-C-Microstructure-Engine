# Reproducible versioned payload baseline

## Phase 1 workload revision

Current workload version 2 measures AddOrder payload validation ONLY, including
side, price/quantity bounds and instrument-rule checks; it excludes metadata and
provenance. Required types and fixture categories changed. See PHASE_1_CONTRACTS.md.
Version-1 Phase 0B evidence below remains historical and unchanged. Do not compare
these workloads as a speedup or regression. The runner hashes current headers,
validation implementation and fixture source as well as benchmark code.

## Historical Phase 0B scope and correctness gate

Phase 0B measures ONLY the existing AddOrder field validator. It does not measure
book mutation, matching, replay, analytics, order throughput or economic outcomes.
No storage/event implementation or optimization is introduced.

Deterministic xorshift64 fixture version 1, seed 42, has eight repeating categories:
valid buy, valid sell, zero ID, zero price, negative price, zero quantity, zero
sequence, valid extreme values. The independent construction labels determine
expected answers; every event and each batch are checked outside timing. The
original validator was unchanged, including its known enum gap; Phase 1 replaces it.
The harness is not a claim that the event contract is complete.

The timed function lives in a separate translation unit; IPO is disabled. It
counts validation successes over preallocated input. No input generation, oracle,
I/O or manifest serialization is timed. Result counts are consumed and checked.
Current baseline: 262144 records, 64 batches/repetition, 2 warmup repetitions,
7 measured repetitions, one thread. Bound all CLI sizes to avoid overflow and
unbounded allocation; invalid CLI arguments fail. FNV-1a hashes explicit
little-endian field encodings, never padding; it is not a security hash.

## Reproduce current workload from repository root

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

## Correctness remediation: compiler provenance

The common engine runner obtains compiler executable, optional first arguments,
ID and version from the selected build's CMake-generated compiler metadata, using
the cache's exact CMake version directory. It records that metadata's SHA256 and
runs that compiler's --version command. Missing selected metadata is an error;
ambient c++ is never a fallback. Compile commands/flags and executable hashes
remain recorded. Existing manifests are historical and are not rewritten. GCC and
Clang selection regressions and actual-run checks are in CORRECTNESS_REMEDIATION.md.

Generator v2 additionally removes compiler-dependent argument evaluation from the
book workload. Quantity and price draws are explicitly sequenced and tested against
an independent fixed-width reference. Compare only identical generator/model
versions and input hashes; historical v1 runs are not silently treated as v2.
The legacy research runner also uses the shared selected-build compiler helper.
