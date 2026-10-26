# Executed validation and delivery evidence

Date:2026-10-26. Baseline `6af0bdef51007d6058f4f3119ecf5bac21c61ceb`.
Backend implementation checkpoint:`56de91c9b95e6a08e1cd4a7dd3fa43ed8ef8b04b`.
All results below are local x86_64 synthetic/fixture results. No provider credentials,
SEC identifying contact,observed market data,paid resources,or workflow dispatch used.

| Cohort / command | Passed | Failed | Skipped | Scope |
|---|---:|---:|---:|---|
| `python terminal/tests/run_native_suite.py --expected-tests 274` Release |274|0|0|Existing installed native binding |
| Same with `PYTHONPATH=build/python-debug/python:.` |274|0|0|Existing Debug native binding |
| Same through `scripts/run_python_sanitized.py`,ASan/UBSan binding |274|0|0|Live-interpreter LSan checkpoint0 |
| `python terminal/tests/run_live_market_suite.py` Release |104|0|0|86 existing stock/SEC/research +18 new |
| Same,Debug binding |104|0|0|Final container-staging implementation |
| Same,sanitized binding/live LSan wrapper |104|0|0|No sanitizer finding,LSan checkpoint0 |
| Request/stream proof,Codespaces origin,browser-access unittest modules |46|0|0|Part of150-test combined cohort |
| `npm --prefix terminal/web test` |17|0|0|Financial/format/state/shared capture-axis/generation protections |
| `python terminal/tests/check_rewritten_http_tls.py` |8|0|0|Verified local HTTPS/WSS proxy,not external Codespaces authentication |
| Eight existing CTest independent reference tests |8|0|0|Exact canonical hash comparison |
| `python tests/test_python.py` |8|0|0|Installed0.1.1 wheel interface |
| `python tests/test_export_contracts.py` |6|0|0|Installed wheel export contracts |
| Tools Python `tests/test_sdist_patterns.py` |3|0|0|Packaging/privacy patterns |
| Seven existing stable-build browser suites |91|0|0|Includes90 workspace/theme/viewport combinations |
| `node terminal/tests/live-market-validation.mjs` |14|0|0|Authored multi-stock/3D journey,five widths |

These are1335 selected final outcomes,not1332 new tests and not the full native compiler
matrix. The104-test suite fails on changed discovery counts or skips. Native C++ sources,
headers,CMake,Python bindings,SEC implementation and permission/security implementation
were not edited. Reused native build artifacts were exercised;no new six-compiler build
matrix or ARM64 qualification was performed. Third-party Python codecs are not claimed
ASan-instrumented. Native shutdown uses the previously documented live-interpreter LSan
checkpoint methodology,not a claim that all CPython shutdown allocations are absent.

Final logs and SHA256 inventories are in `EVIDENCE.json`;ignored originals under
`build/live-market` and `build/atlas2/resume`. Browser runner completes the frontend build
before navigation and hashes assets before/after each suite. No source-data acquisition
is performed by the fixtures. Chromium154/SwiftShader is viewport/software-rendering
evidence,not physical Android/hardware GPU qualification or an independent-machine result.
Screenshots are labelled synthetic;their paths/hashes are recorded,not raw provider data.

## Eight canonical hashes

| Oracle | SHA256 |
|---|---|
| ITCH |142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e|
| Context |58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e|
| L3 |bb16d4ba9e400ee8f2bc40707de5aa89d0b0955819b4f1f45ca2cdf82cac7991|
| Streaming |be5d6f5a15fa1dc77560e0a815b8397a605eab369fa66f44df12e5ed9b04a4d5|
| End-to-end demo |4ebdd734b5f11e368be1525f95a93070893ec14e9caafb161583807c88d23520|
| Auction |76ad62693c22631e4be0842f44029d779211451a395e8538d70450ae7015ebc6|
| Administration |87556148fdc43cb7d3c073aa5a5fa9a0b9a6368c15a5182edb72bced17957d03|
| H/Y |ad982777da3595d8fb608755a4986e68a19c3ab2721ec1e1e084f1945f0412af|

## Preserved failures and limitations

* Resumed focused log:31 tests,two errors from new bar/cancel handling;fixed.
  Earlier staging tuple and empty-history errors remain in initial logs as well.
* A diagnostic command named nonexistent `terminal.stocks.test_sec`;129 outcomes included
  one import error. Correct module is `test_sec_integration`;final150 combined tests passed.
* First browser attempt timed out waiting for SIMULATED because the synthetic float
  exposed the12-decimal rejection;fixed and regression-tested,without rounding.
* Palette check ran against a prior bundle and timed out. Rebuilt before final journeys;
  prior failure retained. This was asset/test version mismatch,not provider failure.
* Browser read race saw a subscription before its first accepted quote;the test now
  explicitly waits for current-generation accepted observations/metrics. No assertion removed.
* Build still warns about deferred508.73kB Three/OrbitControls chunk. No warning suppressed.
* Starlette emits its existing `httpx` TestClient deprecation warning. No suppression or
  unrelated dependency migration introduced.
* CDP performance snapshot records JS heap/node counts. Layout/script counters enabled at
  the end are not execution-time measurements;zero counters do not imply zero work.
* Sustained reconnect/slow-client/GPU leak testing against real provider data is unverified.
* Independent cameras,stock browser-push,in-place subscription deltas,current calendar,
  corrected tape reconstruction and full optional bar fields remain explicit gaps.

Read `IMPLEMENTATION_REPORT.md` for per-requirement COMPLETE/PARTIAL/BLOCKED/NOT IMPLEMENTED
classification and `SETUP_AND_QUALIFICATION.md` for private owner update steps. No final
FAILED VALIDATION is hidden by the remaining external blockers. Do not label new commits
ARM64-qualified or production-ready from prior runs.

Implementation delivery commits:

* `56de91c9b95e6a08e1cd4a7dd3fa43ed8ef8b04b`:bounded history/order diagnostics/analytics.
* UI/liveness checkpoint SHA is recorded in `EVIDENCE.json` (subsequent documentation
  closure does not alter implementation). Both are pushed only to the authorized feature
  branch with `[skip ci]`;no workflow was dispatched or qualification inferred.

Changed-file inventory,log/screenshot/source hashes,actual fixture results,host metadata,
performance measurements and source-archive checks are recorded in `EVIDENCE.json`.
