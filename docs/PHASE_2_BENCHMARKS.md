# Phase 2 correctness-gated baseline methodology

Purpose: measure the standard-container reconstruction/replay baseline before any
storage optimization. All inputs are synthetic; no external dataset is required.
This is shared-cloud evidence, not a production or ultra-low-latency claim.
The earlier payload-only benchmark remains a separate historical measurement.

## Reproduce

From a clean checkout of the code commit recorded in the manifest, activate CMake
and Ninja as documented in README.md, then run:

```sh
cmake --preset release
cmake --build --preset release
python3 scripts/run_phase2_benchmark.py --orders 512 --repetitions 7 --warmup 2 --seed 1729 --output-dir build/phase2-baseline
python3 scripts/run_phase2_benchmark.py --orders 512 --repetitions 2 --warmup 1 --seed 1729 --verify-against build/phase2-baseline/manifest.json --output-dir build/phase2-reproduce
```

Output directories must be new and ignored or outside the checkout. The runner
reconfigures/builds, runs every CTest outcome, validates the required executed tests,
then invokes the independent-reference-gated benchmark. Debug, sanitized or LTO
builds are rejected as timing evidence. A dirty tree is explicitly recorded; the
published baseline must identify a clean code commit. Git/source hashes are checked
again after measurements. Exceptions leave an incomplete marker, not a valid manifest.
Existing evidence is never overwritten. CI runs only a small correctness/evidence
smoke without timing thresholds. Reproduction compares canonical hashes, not timings.

## Workload and correctness gate

phase2_workload.hpp uses an explicit xorshift64 seed and bounded integer generation.
Default 512 orders alternate buy prices 100..115 and sell prices 200..215, quantities
10..100 lots. Add-only, full-cancel and one-lot identified-execution workloads are
separate; cancel/execution setup seeds the complete book outside the timed interval.
Depth requests the best eight levels of both sides repeatedly without mutating.
Replay merges two explicit streams by capture ordinal: all adds, then full cancels
for even-index orders and one-lot identified executions for odd-index orders (1024
events). Each scenario has its own dataset identity/version, source-record identities,
actual seed and transformation lineage. A complete synthetic snapshot is used only
for the copy diagnostic. There is no matching, analytics or observed exchange data.

Before timing, every mutation and replay input is compared to the independent flat-
vector oracle: orders, quantities, priority, level depth, ledger and invariants.
Copy equality/probe values and snapshot validation are also checked. Timed runs check
success and final conservation/invariants outside their intervals. These gates reject
incorrect benchmark runs; they do not certify every possible exchange workload.

## Measurement scopes

Eight cases: add, full cancel, identified execution, depth snapshot, full validated
replay/journaling, by-value AddOrder-event copy, by-value snapshot-event copy and a
payload-only AddOrder by-value control. Each receives two full untimed warmup runs,
then seven bulk passes and seven separate serial per-operation timing passes on
fresh state. No sampling vector growth occurs inside the per-operation interval.

Bulk throughput includes loop/error/checksum work and per-operation temporary
lifecycle; excludes state construction, fixture generation, preflight, canonical
export, setup and final verification. Service-time samples include paired steady-
clock calls and operation-wrapper error/checksum/destructor work. They measure no
arrival queue, network or venue latency. Percentiles use nearest rank across all
raw samples; worst means worst observed, not a bound. A raw 10000-pair timer
calibration is retained without subtraction. Small copy-control measurements may
be dominated by these overheads. Case order is fixed; CPU/frequency/scheduling are
uncontrolled. No unwarranted speed or architecture comparison follows.

The copy probes compile in a separate translation unit with IPO disabled. They
force the compiler's by-value ABI path and consume selected metadata/payload fields;
they do NOT prove that every sizeof byte was physically copied. Full events and
the smaller payload control differ semantically; the latter is no replacement API.
Object sizes, actual allocated fixture-vector capacity bytes and nominal payload-
only storage arithmetic expose representation cost. The payload storage control
is hypothetical, not a measured allocated compact input container. Inspect retained
journal PMR memory alongside copy timings when assessing the large representation.

Allocation/deallocation counts are successful selected-PMR calls in the BULK timed
interval, excluding setup. Live bytes are captured before/after; lifetime peak
includes setup and staging. Node/bucket requests exclude upstream allocator overhead.
A 128 MiB live-byte resource budget bounds the measured book/replay state. Driver,
input/oracle/canonical/timing-array allocations are outside PMR counters. Linux peak
RSS is process-wide and includes those allocations and preflight, not engine-only RAM.

## Evidence and provenance

manifest.json retains exact code SHA/dirty status, source SHA-256 map, executable
hash, compiler/version/flags/compile commands, OS/kernel/CPU/affinity, workload/seed,
test counts/XML hash, all raw bulk and service samples, timer calibration, allocation
and memory scopes, summaries and canonical artifact hashes/sizes. The raw result
hash is SHA-256 of sorted compact JSON of the retained raw object. The canonical
workload includes full events/metadata and the replay artifact includes configuration,
accepted journal and final book, allowing end-to-end reconstruction lineage.

The compact manifest is archived under docs/baselines. Generated canonical files,
JUnit and logs stay in ignored build output; regenerate them from the exact recorded
code/parameters and compare hashes/sizes. Timing values, executable hashes and JUnit
hashes depend on the environment and are not deterministic cross-machine claims.
No optimization or benchmark speed threshold is introduced in Phase 2.
