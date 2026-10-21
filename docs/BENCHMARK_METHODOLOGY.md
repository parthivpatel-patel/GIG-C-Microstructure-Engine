# Benchmark methodology

Phase 0B scope: existing AddOrder validator only, NOT book/replay/analytics speed.
The minimal harness and manifest runner are introduced in the next checkpoint.
See ADR 0001 for the mandatory correctness-before-optimization gate.

Record CPU/architecture, OS/kernel, compiler/version, flags/build type, exact Git
SHA/dirty state, workload/hash/seed, sample count, warmup, repetitions and threads.
Time pre-generated inputs with a monotonic clock, validate against an independent
oracle outside timing, preserve checked results and report raw repetitions.
Throughput is not reciprocal per-event latency. No invented latency percentiles,
allocation counts or engine performance. Shared-cloud noise must be disclosed.
Full engine p50/p95/p99/worst latency, allocation and peak-memory measurements are
required when those components exist, using defined workloads and timer scopes.
