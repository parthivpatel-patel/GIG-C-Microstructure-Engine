# Remediation Sprint1 test evidence

Implementation source:`3f4c1984603c03f35d92d32a5aaaa5d0b874f0d3`. Baseline:`10eaee30d598807a23e42a8b60abe3d5a5dc2514`. All final rows below were
executed in this sprint; previous audit/overnight receipts are not substituted for
reruns. Full matrices used the same production bytes later committed as above;
the source-to-test manifest verifies those bytes. The25 new regressions and bounded
resource qualifier were also executed after the implementation commit. Reports are
a subsequent documentation-only checkpoint; its exact remote SHA is verified at delivery.

| Native configuration | Actual CTest pass | Failure/skip/disabled | Frozen hashes |
|---|---:|---|---|
| gcc-python-debug | 158 |0/0/0|8/8unchanged|
| gcc-python-release | 158 |0/0/0|8/8unchanged|
| gcc-python-asan-ubsan | 159 |0/0/0|8/8unchanged|
| clang-debug | 155 |0/0/0|8/8unchanged|
| clang-release | 155 |0/0/0|8/8unchanged|
| clang-asan-ubsan | 155 |0/0/0|8/8unchanged|


Native source, bindings, CMake and native tests were unchanged. These are actual CTest
reruns against existing exact-source GCC/Clang Debug/Release/ASan+UBSan builds,
**not fresh C++ compilation, hosted CI or ARM64 execution**.940 native outcomes and48
hash comparisons passed. Allocation-failure, journal atomicity, recovery and independent
oracles remain included. Explicit comparisons:[native-canonical-comparisons.json](evidence/native-canonical-comparisons.json).

| Affected Python cohort | Debug | Release | ASan+UBSan |
|---|---:|---:|---:|
| Source/SEC/operational/backend |142|142|142|
| Stock/provider/SEC |207|207|207|
| Native-backed terminal compatibility |274|274|274|
| New remediation cohort |25|25|25|

All1944Python outcomes pass, zero failures/errors/skips. Each of the four sanitizer
cohorts reports LIVE_LSAN_CHECK=0 using the existing live-interpreter checkpoint;
this does not certify CPython shutdown leak cleanliness. Strict expected counts
and original assertions were preserved. No sanitizer diagnostic was suppressed.

| Additional gate | Actual result |
|---|---|
| Frontend unit/contracts |81/81 pass; 4 new formatter methods; production TypeScript/Vite build PASS |
| Exact Origin/Host/proof/security/policy |52/52 pass |
| Local verified HTTPS/WSS proxy cohorts |6+6+8=20 pass; synthetic proxies, not current Codespace authentication |
| New boundary/concentration browser |6/6 pass |
| Existing research/history/portfolio browser |6/6 pass; exact3/500risk reference retained alongside0.6%presentation |
| Existing global selection/Stock Intelligence browser |21/21 pass; NVDA→AAPL regression preserved |
| All12 workspaces×5widths×2themes |120/120 pass; 360, 390, 768, 1280, 1920; ordinary clicks, no page overflow |
| Existing installed native0.1.1 wheel |8interface+6export checks pass; not a newly rebuilt remediation wheel |
| Source distribution pattern regressions |3/3 pass |
| Two clean implementation source archives |879 safe byte-verified members; byte-identical; no binary/private data |
| Proposed concentration independent oracle |256Decimal cases plushand values, partial/empty/zero/extreme/bounds/provenance/API isolation |
| Bounded reliability |Quiet heartbeat, real2s send timeout, cancellation, shutdown, 5000event burst, reconnect, generation and resource exhaustion |

Counts are per-cohort outcomes, not unique tests orcoverage percentages.153browser
checks span four cohorts. Browser uses Chromium154/SwiftShader and emulated viewports,
not physical Android/GPU/WCAG certification. Assets were built before browser runs;
no concurrent asset rebuild was scheduled. The existing Threechunk warning and
Starlette/httpx deprecation remain visible in logs.

## Failure-before and setup evidence

- [options-before.log](evidence/options-before.log):7 methods ran; 1failure and7subtest
  errors exposed the boundary/huge-integer/coverage conditions before repair.
  [options-after.log](evidence/options-after.log):same7 methods pass.
- Initial274Release terminal run had2errors:`native_diagnostic_not_built`, because
  the isolated worktree had no default diagnostic build. Its log is preserved.
  Command-scoped GIG_TERMINAL_NATIVE_BUILD selected existing qualified binaries;
  the complete274suite then passed in all three configurations. No test was skipped.
- Initial teardown could not inspect /proc/PID/cwd; only the three fixture PIDs created
  by this sprint were then signaled using their owned exec/log records. Owner servers
  were not contacted orchanged. No privileged configuration alteration was needed.

## Reproducible commands

Use the committed implementation orfinal evidence checkpoint, an existing native
build and test virtual environment. Provider flags below affect only the test process;
existing private configuration is not edited. Do not enable a live source to run fixtures.

```bash
PYTHONPATH=build/python-release/python:. GIG_TERMINAL_NATIVE_BUILD=build/python-release .venv/bin/python terminal/tests/run_source_qualification_suite.py
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_live_market_suite.py
PYTHONPATH=build/python-release/python:. GIG_TERMINAL_NATIVE_BUILD=build/python-release .venv/bin/python terminal/tests/run_native_suite.py --expected-tests 274
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_remediation_sprint1.py
npm --prefix terminal/web test
npm --prefix terminal/web run build
PYTHONPATH=build/python-release/python:. .venv/bin/python scripts/qualify_remediation_envelope.py --native-build build/python-release --output build/private-envelope-new
```

Native/configuration command records and exact interpreter paths are in
[python-matrix.json](evidence/python-matrix.json) and[native-matrix.json](evidence/native-matrix.json).
For sanitizer runs use existing run_python_sanitized.py and the toolchain-matched
ASan/libstdc++preload recorded in the matrix, not a weakened instrumentation profile.
The three fixture browser servers were loopback-only and have been stopped.

## Resource and security limits

The clean-commit fixture qualifier ran with512MiB virtual-address, 20/22 s CPU,
32 MiB/file and30s Python-child wall bounds; native probe children have10s watchdogs.
Actual measurements:[envelope.json](evidence/envelope.json),[journal-scaling.json](evidence/journal-scaling.json).
These are a bounded qualification profile, not new service/global limits orspeedup claims.
Runtime inventory includes actual test interpreter dependencies plusavailable-tool
inventory; unused installed packages are not automatically deployed dependencies.
Current npm registry audit reported0 advisories across the resolved frontend graph;
that does not clear managed CPython/OpenSSL/Expat orbundled Action/vendor questions.
No runtime ordependency was blindly upgraded. A10target closure remains partial.

## Visual evidence

[visual-evidence.json](evidence/visual-evidence.json) records hashes of fourauthored
screenshots:mobile/desktop concentration, theoretical options, and formatted portfolio.
Two were visually inspected here. No observed-market screenshot or private target URL
is claimed. Fullprecision/exact backend values remain available in expandable detail.

## October 31 continuation verification

Verified all 26 implementation-file fingerprints and all 73 initial evidence receipts
against the recovered checkpoint. The actual test interpreter and all 19 installed
test distributions match the recorded environment. Re-ran only the 25-case Release
remediation cohort:25 passed,zero failures/errors/skips. The earlier 940 native and
1944 Python outcomes are recovered same-sprint executions,not new October 31 matrix
runs. No application source changed during continuation. See
[resume-verification.json](evidence/resume-verification.json) and
[remediation-resume.log](evidence/remediation-resume.log).

One published frontend-build log line had trailing ASCII whitespace removed for Git
diff hygiene. Its warning text is unchanged;the exact original log SHA256 and
removed whitespace are recorded in
[evidence-normalization.json](evidence/evidence-normalization.json). The original
raw log remains preserved in ignored build evidence. No warning was suppressed.
