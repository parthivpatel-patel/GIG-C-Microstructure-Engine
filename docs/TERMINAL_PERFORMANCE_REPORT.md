# Local terminal performance evidence

Authored-only,single-owner,shared-cloud measurements;no public endpoint load test.
Intel Xeon Platinum8573C,x86_64,CPython3.12.14,GCC14.2 Release native binding.
One warmup/three measured repetitions,240 remaining authored events/run after20
initial records. Measured834–860 accepted events/sec through Python schema validation
and native replay.100 state+exact JSON serializations/repetition averaged about
0.158–0.192ms each. Native replay PMR peak9,398,456bytes,including retained source
journal;process RSS peak35,072KiB includes interpreter/imports,not just native state.
Raw timings/source hashes/fixture seed0 are in the final evidence manifest.

Chromium headless/SwiftShader local navigation measured 1.114s in the qualified
browser run;ten state HTTP round trips included one30.35ms first sample and roughly
2.15–2.80ms remaining samples. Use exact final run values from evidence rather than
extrapolating a latency percentile. Single-sample cloud/browser startup is noisy.
No tail-latency,physical GPU/Android,Internet feed latency or exchange-speed claim.

The rendering pipeline is event/interaction-driven,not an always-running animation.
Source progression and10Hz view publication are separate;view frames can coalesce.
No measured3D FPS qualification or sustained multiclient capacity claim is made.
The bounded geometry/history/PMR/WS limits are engineering caps,not empirical SLAs.
Native L2 currently stages two reserved vectors/transaction and uses bounded linear
search/duplicate scans/sorting. Preserve correctness baseline before optimization;
no journal redesign or speculative micro-optimization was introduced.
