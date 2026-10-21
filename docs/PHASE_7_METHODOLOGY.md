# Phase 7 common-code performance and profiling

MUST HAVE: correctness-gated sequential Release measurements across book mutations,
replay, snapshots, exact book/flow analytics, synthetic matching/scheduling and
execution planning/TCA. Reuse implemented deterministic fixtures and independent
preflight/hand references. No latency threshold, concurrency or optimizer switches.

From the repository root with CMake/Ninja activated:

```sh
cmake --preset release
cmake --build --preset release
python3 scripts/run_engine_baseline.py --output-dir build/phase7-baseline
```

Runner requires a clean code checkpoint by default, runs every Release test, checks
required independent cases executed with no failures/skips, excludes sanitizer/LTO/
profile flags and captures Git/source/executable hashes, compile commands, compiler,
CPU/affinity/OS and every raw timing/allocation/memory sample. --allow-dirty is for
development validation only; dirty=true must not be presented as clean-code evidence.
Existing evidence is never overwritten; incomplete runs cannot masquerade as complete.
Canonical generated artifacts remain in ignored run directories; durable hashes and
exact generators/seed/configuration make them reproducible. Archive selected manifest.

Every case runs as the sole child of a fresh Python measurement worker. Linux child
rusage supplies wait-accounted peak RSS (KiB converted to bytes), user/system CPU.
This avoids confusing sampled RSS or accumulated previous-child peak with the current
benchmark. Wait-accounted RSS can retain the worker image's inherited pre-exec high-water floor;
small program readings must not be described as engine-only RAM. C++ benchmarks also
report native_vm_hwm_bytes from /proc/self/status AFTER exec; this mm high-water value
separates the native benchmark from the worker's startup floor. Both figures remain
in raw evidence, with null when the native observation is unavailable. Benchmark
input/oracle/canonical/sampling/formatting/proc-read memory is INCLUDED. Book/replay/copy share one process, so its RSS
is whole-group peak, not assignable to individual mutations. Selected PMR counters
separately describe per-case engine allocation requests; they exclude upstream
allocator overhead, uninstrumented driver allocations and process/shared mappings.
Whole-child CPU includes setup/preflight/export and is not timed-operation latency.

Seven bulk repetitions and separate serial service samples; workload-specific counts
in raw outputs. Median bulk throughput, nearest-rank p50/p95/p99 and worst observed
service wrappers. Clock/error/checksum/lifecycle overhead included, no external
arrival queue/network/venue latency. Synthetic scheduler logic still executes.
Finite small fixtures and shared scheduling/frequency are not production evidence;
copy-control measurements can be timer dominated. No comparison across different
phase code/workload/flags is asserted as an optimization gain.

## Instrumented profiling, separate from ordinary timing

Where GNU gprof is available, configure a separate Release tree with -pg compiler/
link flags and BUILD_TESTING=OFF; build representative flow/simulation benchmarks.
Run each from its own ignored directory, inspect gprof's flat profile/call counts,
and archive compact profile text with exact code/flags/tool version. Never substitute
instrumented timings for ordinary Release baseline. 10 ms statistical sampling and
short synthetic workloads can make CPU percentages coarse or absent; say so.

An optimization is optional and only justified by usable profiling evidence plus a
maintainable bounded change. Preserve this baseline, change one mechanism, rerun
all correctness/Debug/Release/sanitizer gates and compare exact canonical outputs and
same workloads under comparable flags. Report regressions as well as gains. If sample
resolution or maintenance tradeoffs are insufficient, retain the correctness baseline
and explicitly defer optimization. No lock-free structures, concurrency, speculative
allocator/container rewrites or speed claims merely for appearance.

Interview rationale: distinguish cumulative engine allocation requests, live requested
bytes, process high-water memory and service-time scope; they answer different questions.
Profiling identifies a candidate, not proof of a safe optimization. Standard-container
reconstruction and full-State simulated atomicity remain the reference implementations.
