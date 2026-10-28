# Final independent engineering verification campaign

Date: October28,2026 (America/New_York). Frozen development source:
`f314b36cb1d088fe6dad83c705ef371bc387834e`.
Repair candidate: `6e76d405f53679ef8dade4f342dc111bcbf7ff12`.
Branch: `feat/atlas-final-release`. No main/history rewrite,release,provider activation,
workflow dispatch,paid infrastructure or restricted dataset access.

## Scope and interpretation

This campaign independently re-executed tests and measurements instead of promoting
historical reports to acceptance. It is a separate verification pass by the same
assistant in the same local cloud environment,not an independent organization,
independent machine,owner acceptance or external penetration test.

The earlier eighteen-area traceability has144 source/test references;all exist and
all stored hashes matched. The implementation was inspected alongside completion,
readiness,security,deployment and source policy reports. Assertions in documentation
were treated as claims. The new matrix decomposes directive workstreams3–16 into
207 individual checks and explicit external gates:195 PASS,0 FAIL,8 BLOCKED,
3 NOT TESTED,1 NOT APPLICABLE. These counts include measurement metadata and are
not a percentage of product functionality or proof of no defects.

The three untested gates are full Python/system dependency-advisory review,quantitative
contrast/readability audit,and the exact pinned Codespaces image/zlib qualification.
None is silently promoted to PASS. See FINAL_ACCEPTANCE_MATRIX.json for exact candidate,
environment,method,evidence,status,blocker and follow-up on every row.

## Confirmed defect and repair

**Medium:clean installation omitted authored native diagnostics.** In a fresh detached
checkout with a fresh runtime venv and installed rebuilt wheel,272/274 terminal tests
passed;`terminal.test_historical.AuthoredNativeDiagnostics.test_itch_restart` and
`test_lobster_unknown_state` errored with `native_diagnostic_not_built`.
The whitelisted diagnostic API requires `gig_itch_validation_demo` and
`gig_lobster_validate`. Standard setup built the wheel/frontend but neither executable.
Thus two existing Research/Historical actions were unavailable after clean setup.

`scripts/setup_terminal_native.sh` now builds exactly these existing targets with
ITCH streaming enabled. `setup_terminal.sh` invokes it before declaring completion.
The devcontainer explicitly requests zlib development headers. There is no new input
adapter,network acquisition,semantics change or relaxed assertion. Existing CMake
zlib>=1.3.1 requirements remain strict. The helper does not disable existing tests or
Python/benchmark cache options. Native diagnostics still accept only authored profiles.

The clean-checkout helper and full274 terminal tests then passed,as did164 stock tests.
The final helper revision was rerun and the six existing historical regression cases
passed again. No new test duplicates installer source logic:the same real executable
integration tests that failed before now pass after setup. Failing-before and repaired
logs are retained. This repair changes only setup/Docker configuration,not native,
Python application or frontend calculations. Six-configuration source testing below
was executed on the frozen source and applies to unchanged components;the repaired
setup path was independently exercised in the clean checkout. No claim of an actual
Codespaces image build is made.

**Remaining setup risk:**installing a distro package named zlib1g-dev does not prove
its version meets1.3.1 on the pinned Ubuntu image. This host has1.3.1;the actual
container image remains NOT TESTED. Setup must fail rather than say complete if its
required native build cannot be made. No source download/version bypass was introduced.

## Test results actually executed

| Cohort | Passed | Failed / skipped |
|---|---:|---:|
| GCC Release CTest |155|0 /0|
| GCC Debug CTest,Python enabled |158|0 /0|
| GCC ASan+UBSan CTest,Python enabled |159|0 /0|
| Clang Debug CTest |155|0 /0|
| Clang Release CTest |155|0 /0|
| Clang ASan+UBSan CTest |155|0 /0|
| Terminal Debug/Release/ASan+UBSan bindings |274 each|0 /0|
| Stock Debug/Release/ASan+UBSan bindings |164 each|0 /0|
| Frontend unit tests |31|0 /0|
| Seven fixed-asset browser journeys |91|0 /0|
| Ratio/statement browser |14|0 /0|
| Multi-stock stream fixtures browser |21|0 /0|
| SEC/discovery browser |3 each|0 /0|
| Native/L1 graphics-context recovery |5 +4|0 /0|
| HTTP proof/origin/host and stream diagnostics |33 +20|0 /0|
| Verified local rewritten HTTPS/WSS checks |8|0 /0|
| Fresh installed-wheel interface/export |14|0 /0|
| Packaging-pattern regressions |3|0 /0|
| Fresh local checkout terminal/stocks after native setup |274 +164|0 /0|
| Final setup helper,historical regressions |6|0 /0|

Selected final test/check outcomes:2,945 PASS,0 final FAIL,0 SKIP. Nested CTest cases,
repeated configurations and installed consumers count separately;this is not unique
coverage. No CTest expectation,canonical hash or assertion was changed. Both Python
sanitizer runs reported LIVE_LSAN_CHECK=0;this is a live-interpreter checkpoint,not
full CPython shutdown-leak qualification. All eight primary frozen canonical outputs
matched across all six executed configurations,including independent models and their
negative controls. See `build/acceptance/canonical-comparison.json` and receipt manifest.

The main browser driver builds first and checks immutable asset hashes around every
journey. AAPL/APLD/CRWV actual browser discovery passes without giving unknown CIKs
values or granting feed entitlements. Source identity/financial availability remain
separate. Held responses,invalid financial fields and period changes fail locally.
The native extension is real;providers/source records in these journeys are authored.

### Preserved unsuccessful attempts

- Isolated wheel build initially failed because inherited CXX was `clang++ -pthread`;
  explicit `/usr/bin/gcc` and `/usr/bin/g++` produced a fresh successful wheel.
- A combined wheel/build-test invocation initially errored importing scikit_build_core
  in the runtime-only venv. Runtime consumer14 and packaging3 were separately run
  in their appropriate environments and passed. Build dependencies were not smuggled
  into the runtime package.
- Fresh npm installation initially failed at its unavailable default home cache;
  explicit writable `/tmp/gig-atlas-acceptance-npm` cache allowed locked installation.
- Clean terminal suite exposed the genuine two-diagnostic setup defect above.
- An exploratory diagnostic build omitted GIG_BUILD_ITCH_STREAMING and had no demo
  target;the repaired helper declares the required option explicitly.

These failures are retained,not erased by final zero-failure totals. The native build
minimums and test assertions remain unchanged.

## Environment and reproducibility

Linux x86_64,Intel Xeon Platinum8573C,Python3.12.14,Node24.19.0;
GCC14.2.0 and Clang19.1.7;headless Chromium154.0.8037.57/SwiftShader.
Existing six native build directories were rebuilt and all CTests rerun. A separate
local detached checkout from f314,new venv,isolated wheel build,pinned Python dependency
installation,npm ci,production frontend build and diagnostic source build provide fresh
local reproduction. This is not a second machine. No Docker image or ARM64 runner
was executed. Strict free/owner-gated workflow rules were preserved.

The frozen source archive had774 safe intended byte-identical members. The repaired
implementation archive had775;both passed traversal/type/inventory/content checks.
The archive snapshot precedes final acceptance documentation,not the setup repair.
No private configuration,datasets,build outputs or market observations were added.

Reproduction commands (from an authorized private checkout):

```bash
# Existing prerequisites:Python3.12,GCC/Clang,CMake,Node24,zlib>=1.3.1.
# Setup builds real native diagnostics;no providers or datasets are enabled.
bash scripts/setup_terminal.sh
python terminal/tests/run_native_suite.py --expected-tests 274
python terminal/tests/run_live_market_suite.py
npm --prefix terminal/web test
# Start authored fixtures only on loopback;see DEPLOYMENT.md.
python terminal/tests/run_atlas_browser_suite.py
node terminal/tests/ratio-history-validation.mjs
# Packaging requires the pinned build-tool environment,not runtime-only venv.
CC=/usr/bin/gcc CXX=/usr/bin/g++ python -m build --sdist --wheel
```

Use the configured native binding for each Debug/Release/sanitizer suite;exact commands,
source classifications,toolchain metadata and artifact hashes are in
FINAL_ACCEPTANCE_EVIDENCE.json. Native six-config execution and browser fixture orchestration
scripts are also preserved locally under build/acceptance. Build artifacts are ignored.

## Fresh performance observations

All inputs below are authored;all values measured in this campaign. Shared-host
builds and tests ran concurrently,so do not infer a regression against historical
numbers or an isolated capacity limit. No institutional target was invented.

| Workload | Observation | Limit |
|---|---|---|
|50,000 identity rows;100 searches|parse0.267s;mean search9.05ms;peak process RSS57,652KiB|One local scan-based search workload,not current official universe|
|5,888 selected facts;144 ratio points|five repetitions,one warmup;median118.46ms;228,811-byte response;RSS20,608KiB|Local exact calculation,not SEC request latency|
|1,000 source events with full view+tracemalloc|24.46events/s;retained256;peak traced927,386bytes|Intentionally instrumented analytics+serialization,not ingestion-only|
|Three ingestion-only authored10,000-event runs|median26,262events/s|Excludes generation,analytics,network,browser;not exchange performance|
|Steady256-row projected history|178,421→5,247 JSON bytes;median encode508→74µs,100repetitions/5warmups|Authored padded unchanged rows,not live bandwidth|
|100 full snapshot serializations|representative mean12.24ms;344,808bytes|Workload-specific full history,not wire projection size|
|1,000 durable synthetic ledger events|append53.47ms;verified recovery67.95ms;2,121,728-byteDB|Single local SQLite batch test,not hot recovery|
|50,000-event memory soak|history/dedup256 throughout;1,758-byte traced growth from10k→50k;RSS36,908KiB|Not indefinite stability or native/GPU allocation accounting|
|120 quiet native3D frame intervals|mean16.665ms;zero additional bufferData calls after12 initial uploads|rAF cadence is not GPU draw completion or live/multipanel FPS|
|Browser cold-context load and route|one warmup/three repetitions;raw timings and CDP heap recorded|Loopback,software GPU,includes network-idle wait|

Initial JS remains232,995bytes,lazy Stock Intelligence and Three chunks remain deferred;
>500KB optional chunk warning is retained. Browser performance raw results and rendered
synthetic screenshot hashes are in the artifact receipts. No physical Android or
hardware-GPU performance claim. History projection semantic equivalence and gap rejection
were executed in frontend/backend suites. The fresh projection microbenchmark above
uses explicitly padded unchanged authored rows;earlier percentage savings are not
repeated as fresh measurements.

## Security and operational review

Source inspection and executable negative controls cover exact Origin/TrustedHost,
endpoint-bound one-use proofs,forged forwarding,replay/reuse rejection,private-config
loading,provider/retention/no-cost gates,rate/body/frame/client budgets,cancellation,
stale-response isolation and safe errors. Rewritten localhost Origin is not globally
allowed. Local HTTPS/WSS tests verify certificate trust;they do not authenticate as an
owner through the real Codespaces proxy. Keep8787 PRIVATE.

Fresh npm advisory query reports zero known vulnerabilities for the locked frontend
dependency tree. Narrow frontend-bundle checks found no private-key/AWS/GitHub-token
patterns;no actual provider credentials are present. Neither result proves absence of
all secrets/vulnerabilities. Full current Python/system advisory/SBOM coverage is
NOT TESTED;no penetration-testing certification. Starlette testclient deprecation and
optional bundle warnings were retained. No telemetry or broker-order path added.

Observed storage stays disabled;synthetic ledger crash/corruption/expiry/transaction
and concurrent publication tests pass. Hash-chain consistency is not authenticated
exchange completeness;historical recovery is not restoration of hot live/native state.
Offline physical deletion and infrastructure backup policy remain operational gates.

SEC identifying configuration is unavailable and remains disabled. Current official
CIK/financial reconciliation is BLOCKED. Restated financial history remains explicitly
not point-in-time information availability. Source currentness,complete XBRL statements,
complete corrected tapes,live L2/L3 and forecasting efficacy are not inferred from tests.

## Release decisions

1. **Engineering acceptance:CONDITIONAL.** Executed bounded automated checks pass and
   the reproduced setup defect is repaired. Three untested verification gates and
   external gates remain;unrestricted acceptance is not fully closed.
2. **Controlled research use:CONDITIONAL GO**,private authored/synthetic or already
   legitimately permitted inputs only,with declared missingness/limitations and
   required dependencies. No public release or data-retention authorization implied.
3. **Authorized live-market qualification:BLOCKED in this executor.** Implementation
   is ready for a bounded qualification campaign once actual feed/account/cloud/display
   permissions,credentials,current identity reconciliation and private-host checks are
   supplied. Read-only does not waive terms. Observed retention requires separate rights.
4. **Production readiness:NO-GO.** No claim of real-market/ARM64/device/full security/
   accessibility acceptance,operational HA or production trading readiness.

**Ready for final owner acceptance of the bounded research candidate:conditionally yes.**
Live-market research is not yet qualified. Exact prerequisites are in
EXTERNAL_QUALIFICATION_REGISTER.md. No owner testing or routine command execution was
requested during this autonomous campaign. The remaining gates are openly recorded;
there is no blanket195-green-cells production claim.
