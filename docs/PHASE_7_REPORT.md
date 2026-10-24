# Phase 7 completion report

Objective: reproducible common-code baselines, allocation/copy/native memory scopes
and profiling, optimizing only with adequate evidence. Verified clean start:
`a63a7d5d11e04244a8e1c89861bb860858949e64`.
End implementation/harness: `5707417ba2ae705fff45f0cc53a280dd33de9473`, normally
pushed and exact remote SHA verified. Evidence/report checkpoint is this document's
containing Git commit; next phase report records the exact boundary hash.

Implemented: sequential correctness-gated common-code runner across all current
components; fresh worker per benchmark; wait-accounted CPU/RSS plus native post-exec
/proc VmHWM; complete raw sample/PMR counters, executable/source/canonical hashes,
compiler/flags/CPU/affinity/environment and clear error/overwrite/dirty-run behavior.
Mathematical/engineering scopes and reproduction: PHASE_7_METHODOLOGY.md. No core
book/analytics/simulator/execution semantics changed; no optimization gain claimed.

Actual local Debug 61/61 (4.21s), ASan+UBSan 61/61 (13.63s), common clean-code Release
61/61, zero failures/errors/skips and no reported sanitizer findings. Every prior
independent numeric/reference/fault-injection case remains enabled. Development
runner exercises all five benchmark programs; required suites/checksums/sample counts
checked, child failures propagated, dirty default/overwrite evidence rejected.
Clean baseline source hashes were independently compared with recorded Git objects.
Ordinary measurements ran serially without another benchmark launched by this session.

Raw evidence: baselines/phase7-engine.json, code SHA above, clean, GCC14.2 x86_64
AMD EPYC9V74, Release -O3 -DNDEBUG, one engine thread, shared CPU scheduling/frequency.
Seven repetitions, two warmups and case-specific counts. Throughput is median BULK
wrapper operations/s; latency columns separate serial p50/p95/p99/worst observed ns:

| Case | Median operations/s | p50/p95/p99/worst ns |
|---|---:|---:|
| book_analytics | 2,119,265 | 300/411/611/362064 |
| add | 2,932,971 | 320/431/681/31546 |
| cancel | 4,492,489 | 221/340/531/17836 |
| depth_snapshot | 7,998,250 | 130/141/250/77524 |
| event_copy_add | 3,334,050 | 181/260/360/53659 |
| event_copy_snapshot | 8,570,759 | 131/141/200/94319 |
| execution | 4,108,688 | 211/370/551/101670 |
| payload_copy | 367,816,092 | 30/30/40/390 |
| replay | 57,080 | 7021/13329/117413/5192513 |
| execution_tca | 692,166 | 1022/1643/3876/810014 |
| flow_analytics | 751,886 | 931/1082/2193/319511 |
| simulation | 122,312 | 5258/20320/88991/419949 |

Case scope differs: simulation operation is submit+advance, execution_tca is plan+
TCA, replay includes validation/journal. Do not compare unlike operations as speedups.
Full-event copy probes and payload controls differ semantically and are partly timer
limited. Book snapshot output lifecycle included; setup/oracle/export excluded from
timers. Raw PMR counts/live/peaks retain their individual scopes, including simulation
full-State staging. All raw samples remain available, not only selected best timings.

Native process VmHWM: book/replay/copy whole group 67461120 bytes; book analytics
2412544, flow analytics2555904, simulation2310144, execution/TCA2244608 bytes.
These include fixture/oracle/driver/export/proc-read, NOT just engine state. Linux
wait-accounted child RSS retained a 10223616-byte pre-exec worker-image floor in
small cases; this was discovered during measurement validation and is separately
retained/labeled rather than presented as native C++ memory. Book group exceeds that
floor, so its two observations agree. PMR requests exclude allocator overhead and
non-PMR driver memory; no cross-metric memory equivalence is asserted.

Profiling: baselines/phase7-gprof.json, same clean code, separate Release tree with
-pg compile/link, GNU gprof2.44. Representative flow/simulation checksums passed.
Flow profile has only 0.03s accumulated statistical samples; simulation0.01s at10ms
resolution. Simulator profile attributes its sole sample to full State copying and
records5120 staged commands; allocation/copy counters identify this as a candidate
cost. Flow helper symbol/inlining attribution is not precise enough for per-helper
accounting. These short shared-cloud instrumented samples do NOT support reliable
percent speed claims or a transaction/history ownership rewrite. Instrumented timings
are excluded from baseline. No optimization chosen; standard-container/full-State
reference retained. Conditional before/after optimization gates are N/A, not skipped
or represented as achieved gains. No concurrency/lock-free/custom allocator rewrite.

Reproduce profiling after the ordinary baseline (do not contend with timing runs):

```sh
cmake -S . -B build/phase7-profile -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF -DGIG_BUILD_BENCHMARKS=ON -DGIG_WARNINGS_AS_ERRORS=ON -DCMAKE_CXX_FLAGS=-pg -DCMAKE_EXE_LINKER_FLAGS=-pg
cmake --build build/phase7-profile --target gig_flow_benchmark gig_simulation_benchmark --parallel 2
```

Run each executable from its own ignored directory to create gmon.out, then
`gprof -b <absolute executable> <absolute gmon.out>`. Generated binary/gmon artifacts
stay ignored; archived compact profiles include executable hash/flags/tool context.

Hosted Actions UNVERIFIED because GitHub checks API is blocked (proxy CONNECT403).
Native Git pushes/exact SHA checks work; equivalent local gates pass. No local
Clang/native ARM evidence yet. Remaining risks: finite small synthetic workloads,
uncontrolled host noise, timer-dominated control, explicit numerical/model/resource
limits inherited from earlier phases, coarse profiling insufficient for safe broad
optimization. No production or ultra-low-latency claim. No main/history rewrite,
Terminal change, external release/publication or live/broker integration.

Acceptance: complete current-component baselines, appropriate reference/regression/
Debug/Release/sanitizer gates, sample/workload/code/environment/provenance, raw timing/
allocations/peak memory/copy evidence, profiling with limitations, review and normal
remote durability PASSED. No optimization required by usable evidence. Phase 7
complete; automatically continue Phase 8 pinned Python bindings/versioned schemas,
ownership/errors/provenance and independent consumer package tests.

Changed paths:

- `README.md`
- `benchmarks/book_benchmark.cpp`
- `benchmarks/execution_benchmark.cpp`
- `benchmarks/flow_benchmark.cpp`
- `benchmarks/memory_stats.hpp`
- `benchmarks/research_benchmark.cpp`
- `benchmarks/simulation_benchmark.cpp`
- `docs/ARCHITECTURE.md`
- `docs/LIMITATIONS.md`
- `docs/PHASE_7_METHODOLOGY.md`
- `docs/PHASE_7_REPORT.md`
- `docs/VALIDATION.md`
- `docs/baselines/phase7-engine.json`
- `docs/baselines/phase7-gprof.json`
- `scripts/measure_benchmark_child.py`
- `scripts/run_engine_baseline.py`
