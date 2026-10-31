# Sprint 3 current execution report

Every application execution targeted exact SHA
`5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`. Audit branch changes are documentation
only. Full test provenance,commands/durations and toolchains are in evidence.
Prior green reports are not substituted for the executions below.

## Environment and source binding

Linux x86_64,Intel Xeon Platinum8573C;CPython3.12.14,GCC14.2.0,Clang19.1.7,
Node24.19.0,npm11.9.0,CMake3.31.6,Chromium154/SwiftShader/Three r180. Tests use
existing exact-source native builds,not fresh compilation or current ARM64 hardware.
All native/binding/CMake/native-test source bytes are unchanged from those builds'
qualified source baseline. Compiler names/versions do not imply every existing
binary was recompiled in this session. See toolchains/native matrix receipts.

Provider flags were0 for test processes;owner private files were not read/modified.
Dedicated fixture workspaces use authored environment/permission objects and injected
fetch/socket implementations,never actual credentials or permission activation.
Python tests/child servers inherited an audit-only non-loopback socket-connect
guard. Local HTTP/TLS/WSS traffic was restricted to owned fixture processes;these
are not owner Codespaces authentication tests. No additional packages/downloads.

Stable production assets were built before browser testing;hashes matched after all
browser cohorts. Source fingerprint checks confirm no application/test edits.
All62 Sprint2 evidence receipts were independently rehashed before relying on them
as historical context. Their results are not added to current counts.

## Exact current outcomes

| Native CTest configuration | Pass | Fail/skip/disabled | Frozen identities |
|---|---:|---|---|
| GCC Python Debug |158|0/0/0|8/8 unchanged|
| GCC Python Release |158|0/0/0|8/8 unchanged|
| GCC Python ASan/UBSan |159|0/0/0|8/8 unchanged|
| Clang Debug |155|0/0/0|8/8 unchanged|
| Clang Release |155|0/0/0|8/8 unchanged|
| Clang ASan/UBSan |155|0/0/0|8/8 unchanged|

**940 actual CTest outcomes,48 hash comparisons.** Source hashes and exact commands
are retained;no hosted workflow was dispatched. All eight expected canonical values
are in evidence/native-matrix.json. Native allocation failure,transaction atomicity,
FIFO,flow,numeric,export,ITCH/LOBSTER/recovery cases are included.

| Python cohort | Debug pass | Release pass | ASan/UBSan pass |
|---|---:|---:|---:|
| Sprint2 independent/binding/deployment/recovery |30|30|30|
| Sprint1 options/HHI/resources |25|25|25|
| Source/SEC/backend/operations |142|142|142|
| Stock/provider/history/models |207|207|207|
| Native-backed terminal |274|274|274|

**2,034 outcomes**,zero failures/errors/skips in these cohorts. Precisely **five**
instrumented cohort invocations report `LIVE_LSAN_CHECK=0`;the other ten are
Debug/Release.
Live-interpreter leak checking does not certify CPython shutdown or target lifetime.
Original sanitizer warnings/assertions were not suppressed to obtain passes.

| Additional current execution | Pass | Failed requirement / skip |
|---|---:|---|
| Existing frontend unit/contracts |81|0/0|
| New independent geometry/mapping Node tests |14|0/0 after correcting invalid audit fixture|
| New independent math/Python boundary tests |9|0/0|
| Security/policy unittest cohort |55|0/0|
| Verified local TLS forwarding/proof cohorts |6+8+6=20|0/0|
| Workspace/theme/viewport browser |120|0/0|
| Advanced3D ordinary-click browser |23|0/0|
| Additional legacy-scene input-change browser |2|0/0|
| Existing installed native wheel |8+6=14|0/0;not a new wheel build|
| Packaging pattern regressions |3|0/0|
| Committed stock-intelligence browser program |4 earlier checks reached|**program FAIL** at fifth check;remaining steps NOT_RUN|
| Controlled chunked response budget requirement |reproduction succeeds|**budget requirement FAIL**;3MiB fully consumed against2MiB claim|
| Owned native server/receipt + startup |MATCH and measured|Not external target authentication|
| Bounded resource/journal/search/projection qualifiers |All complete|Not market latency or long-session validation|

The passing counted cohorts above total3,315 outcomes (native940+Python2034+
frontend81+new14+new9+security55+TLS20+browser145+wheel14+packaging3). This sum
is not unique test cases or a coverage percentage;grouped tests contain many
assertions. Four partial browser checks are **not** included in that total.
The response-budget probe exits0 because it successfully reproduces a defect;
the audited requirement is still FAIL. No overall all-tests-PASS declaration.

## Failures and diagnostic corrections preserved

1. **S3-TEST:** unchanged committed browser assertion at
   `terminal/tests/stock-intelligence-validation.mjs:15` expects `/7\.96556746/`,
   sees `THEORETICAL_SCENARIO · Price ≈7.966 · IV not requested`. Raw independent
   backend reference passes;this is stale display-contract evidence. No test repair.
2. **S3-BUDGET:** production generic API reader consumes all chunked `r.text()`
   before checking2MiB. Browser resource and original-text instrumentation agree
   on3,145,728 bytes/characters. Safe error exists,but optional catalog caller
   discards it. No application repair.
3. Initial independent dome audit fixture supplied decimal text to an integer-tick
   QuoteSample field:13/14 pass,1 error. Correcting only the temporary authored
   fixture to valid integer ratios gives14/14. Original log retained.
4. Initial budget observation probe waited for an alert;source showed optional
   catalog errors were swallowed. It timed out. Direct text/resource instrumentation
   then reproduced the actual budget invariant. Both logs retained;this is not a
   production repair or a disappeared failure.

Warnings retained:Starlette/httpx deprecation,the existing large optional JS chunk,
npm update notice and pip cache warning. No warnings were disabled. Broad repeated
native/session performance numbers are not presented as latency improvements.

## Reproducible commands and provenance

From the exact candidate with existing free dependencies/native builds:

```bash
PYTHONPATH=build/python-release/python:. GIG_TERMINAL_NATIVE_BUILD=build/python-release .venv/bin/python terminal/tests/run_native_suite.py --expected-tests 274
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_source_qualification_suite.py
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_live_market_suite.py
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_remediation_sprint1.py
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_remediation_sprint2.py
npm --offline --prefix terminal/web test
npm --offline --prefix terminal/web run build
```

Debug/sanitizer use matching existing native build directories. Exact interpreter,
ASan/libstdc++ preload,ASAN_OPTIONS,PYTHONMALLOC and temporary network guard are
recorded in evidence/harness documentation;do not run fixtures against an owner
server with providers enabled. The current audit harnesses and their unchanged
application imports are preserved as code blocks in
`evidence/REPRODUCTION_HARNESSES.md`. They create bounded local authored fixtures,
not production functionality. Source AST inventories cover every static declared
interaction;their existence alone is not runtime coverage.

Native command form:
`ctest --test-dir <existing-build> --output-on-failure -j2 --output-junit <receipt>`.
Per-configuration command,counts,duration and expected hashes are in
native-matrix.json;Python equivalents in python-matrix.json. Node and unittest logs
retain their durations. Browser-matrix records11.384s workspace,3.616s failed stock
program,23.119s advanced cohort;legacy/other durations without a monotonic receipt
remain null/not measured rather than invented.

## Explicit NOT_RUN / blocked evidence

- Any actual SEC/Alpaca/crypto data fetch or original observed response comparison:
  NOT_RUN,prohibited here;permissions and exact historical artifact still pending.
- Broker paper execution mocks/account/position/order risk-state transition tests:
  NOT_RUN,production subsystem absent. Only two negative read-only boundary tests ran.
- Paper/live orders,cancel-all and observed trading P&L:NOT_RUN,prohibited.
- Native ARM64/current candidate hosted CI:NOT_RUN,not available/authorized;old
  qualified commits do not transfer. Existing manual release-only guard preserved.
- Actual private Codespace authentication/physical Android/independent machine/
  penetration test:NOT_RUN;owner reports are separately attributed.
- Full observedL3 initialization,session recovery,corporate actions,survivorship,
  empirical signal/forecast or alpha validation:NOT_RUN,required source evidence absent.
- Long-running multiday endurance,global quotas and sustained physical-GPU FPS:
  NOT_RUN;only bounded stated envelopes and software-renderer samples measured.
