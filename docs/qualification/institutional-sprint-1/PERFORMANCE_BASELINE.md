# Reproducible performance baseline

Measured from clean implementation `11f1e9cfe6898970461855829650220a9e57bb5d`; tracked_dirty=false. All inputs are independently authored synthetic fixtures. No provider/network, exchange latency, trading alpha or production performance claim follows.

## Environment and method

Architecture `x86_64`, CPU `INTEL(R) XEON(R) PLATINUM 8573C`, Python `3.12.14`, compiler `GNU 14.2.0`, selected native build `Release`. Affinity: `[0, 1, 2, 3, 4]`. Native binary and selected compiler-metadata SHA256 are retained in EVIDENCE.json. Existing unchanged-source Release binaries were used; no fresh native compile is claimed.

Native book workloads: 64 orders, seed 1729, one warmup, three repetitions; eight correctness-gated cases. Reconstruction: 64 orders per symbol, two warmups and three repetitions, checked against separately authored BinaryFile bytes/conservation/source mapping. Python replay: 64 validated events, one warmup/three repetitions; expected visible quantity is 128 lots (2 per event), verified independently before recording each output hash. Provider fixture: 512 observations across 4 symbols, same warmup/repetitions; independent reconstruction verifies every bounded client window.

Native service samples are a separate timed serial pass. Python serial service timings include wrapper/oracle/timer overhead and share the throughput pass. Percentiles use nearest rank over finite observed samples; native 192/384 and Python 192 samples are too few to characterize rare production tails. Reconstruction reports bulk average/median, not invented event percentiles. Copy controls are not semantically equivalent to full event processing; comparing their rates is not a speedup claim. No arrival queue, network, owner edge or external source is in these timers. Shared scheduling and frequency are uncontrolled.

| Workload | Median operations/events per second | p50 ns | p95 ns | p99 ns | Samples |
|---|---:|---:|---:|---:|---:|
|Native add|3976884.4|283|376|596|192|
|Native cancel|5852231.2|198|252|270|192|
|Native depth_snapshot|7587433.3|146|150|249|192|
|Native event_copy_add|7213706.0|182|187|190|192|
|Native event_copy_snapshot|10938301.1|118|124|126|192|
|Native execution|7207207.2|167|194|253|192|
|Native payload_copy|429530201.3|26|29|32|192|
|Native replay|130221.8|4310|5835|219483|384|
|Python/native replay|926.5|1088821|1439959|1855502|192|
|IEX fixture+metrics+projection+oracle|336.1|3266325|4192819|5016359|1536|

Two-symbol reconstruction: **515 records**, **114,985 records/s**, median **8696.79 ns/record** as a bulk average, peak PMR **8,036,560 bytes**, live bytes after destruction **0**. Initialization is authored complete empty; container/session completeness remains false.

## Memory, CPU and bounded growth

| Replay events | Live PMR bytes | Peak PMR bytes | Allocations | Journal records |
|---|---:|---:|---:|---:|
|16|198200|295192|63|16|
|64|790536|1178488|211|64|
|128|1580344|2356232|405|128|

Physical journal record: **12,232 bytes**. The 100,000-record configured ceiling would imply about 1.2232 GB of physical record storage alone; that is arithmetic extrapolation, not an executed workload or feasible RAM promise. Owner memory budgets and actual vector/copy/retained state matter. No journal optimization was attempted.

Provider retention checkpoints every 128 events: `[128, 256, 256, 256]`; final retained 256 / evicted 256, maximum encoded projected snapshot **21,917 bytes**. Separate traced pass: current **73,054**, peak **1,432,845 bytes**. Whole parent-process Linux peak RSS **43,320 KiB**, includes Python/driver/native setup; not engine-only RAM.

Parent CPU time **16.624 s**, wall **16.693 s**; native child CPU excluded. This is CPU consumption, not sampled per-core utilization. Total allocation counts outside native PMR, fragmentation, one-hour/day stability and real slow-consumer behavior were not instrumented.

## Candidate budgets, not universal institutional targets

- Preserve actual structural limits: 4 source symbols, 256 retained events, 8 browser clients, no per-client event queue, 1 MiB SSE frame ceiling and 2 s send deadline. The benchmark's per-event full metrics/oracle path is deliberately heavier than production's 250 ms coalesced browser emission; its measured rate is not a supported market-arrival quota.
- For this exact 128-event synthetic replay profile, a **4 MiB peak PMR diagnostic budget** would contain the observed 2.36 MB peak; for this exact 64-order/two-symbol reconstruction, **12 MiB** would contain the observed 8.04 MB. These are proposed regression diagnostics for the same workload/toolchain, not newly configured engine defaults or production-memory promises.
- Compare distributions only on equivalent source/build/input/hardware. Establish repeated target-machine distributions before choosing latency regression limits; no noisy percentage threshold was imposed.
- Current frontend remains byte-identical to the verified 22-asset redesign. 118 tests/build and GIG/native/recorded browser workflows passed; this sprint did not conduct a new GPU timing/physical-device benchmark. Prior frontend timings remain historical, not fresh speedup evidence.
- Real source-to-browser latency/p99, clock error, production loss and full-session replay are **unmeasured**. Qualification requires the actual permitted account/environment.

## Reproduce

Use a provider-disabled development instance with the selected existing Release native module. Do not benchmark under ASan or while rebuilding assets/source. With the project's dependencies installed:

```bash
PYTHONPATH=terminal/tests/offline_guard:build/python-release/python:. .venv/bin/python scripts/qualify_production_performance.py --native-build-dir build/python-release --output build/production-performance-new
```

Output must not already exist. `--orders (16–256)`, `--observations (512–4096)`, `--repetitions (3–9)`, `--warmup (1–3)` are bounded. Match the native module to the selected build tree; adapt its path to the actual native installation. The manifest stores source/binary/compiler/input/output/artifact hashes, raw native samples, exact contracts and limitations. The initial exploratory measurements are retained separately; only the clean-checkpoint run supplies this baseline.
