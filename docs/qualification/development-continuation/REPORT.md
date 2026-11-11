# GIG remaining-engineering continuation — November11,2026

Runtime source:`72e175e2f94981647e1921be97b875a452b7f3c5`,branch `development/gig-ui-redesign`. Overall continuation baseline:`3e17e7052a6b20478bd02d62a46c679660eeaac1`;initial recovered native milestone:`47e9b1697b1e528091c3e254458d6d365cd52d7f`. The closing documentation-only commit is intentionally not self-embedded;use the final Git remote receipt. All implementation milestones below were committed,pushed and independently checked against the remote branch.

## Implemented and published

| Commit | Working implementation |
|---|---|
|`47e9b1697b1e528091c3e254458d6d365cd52d7f`|Full healthy native L3 book/replay images,direct isolated import,Python binding and atomic authored native/source SQLite coordinator.|
|`fb6adf24a9898bb4c2a6737ac7208837bac0654d`|Six-compiler-profile qualification,full260-event prefix reopen,prepublication restart-reader budget check,and isolated aggregate L2 images/bindings.|
|`5a90f57c991b4ba661664894011aa0682e1723e0`|Reproduced concurrent-start worker race fixed;retired sockets fenced;safe phase/provider-code diagnostics validated and displayed.|
|`2395277e945462fe8e1c4f3a1686efe9e6327184`|Bounded XBRL XML/context/dimension/unit/exact-fact reader,atomic filing batches,conservative acceptance-time selection and offline private export tool.|
|`72e175e2f94981647e1921be97b875a452b7f3c5`|Failing-before JSON-reader publication regression and deterministic offline recovery/XBRL measurement tool.|

The native checkpoint restores identities,FIFO,ledgers,revision,cursors and journal/restart state without reapplying historical book events. Authored source position/session/generation,prefix hash,dedup window and native state publish atomically;gaps/conflicts remain recovery-required across restart. L2 images preserve levels,sequence and revision without inventing order IDs. These are explicit opt-in SDK/coordinator contracts,not an automatically enabled app startup path,observed initialization authority or full hot ITCH context image.

The XBRL path preserves source lexical values,expanded namespaces,dimensions,units,nil/precision,original missing receipts,amendment references and conflicts. Selection uses exact nanosecond acceptance cutoffs and never imputes missing periods or receipts. It uses existing exact financial calculations. No inline-XBRL/DTS/presentation completeness or current-v2 UI integration is claimed. See `XBRL_INSTANCE_PROFILE.md` for the executable input/export contract.

Existing C++ calculations,private-origin policies,provider gates,execution-disabled configuration,GIG branding,12 workspaces and15 visualization modes remain intact. Frontend changes are limited to bounded provider diagnostics;there was no redesign or live activation.

## Executed developer validation

| Configuration/cohort | Actual outcome |
|---|---|
|GCC14.2 Debug CTest|148/148|
|GCC14.2 Release CTest|148/148|
|GCC14.2 ASan+UBSan CTest|149/149|
|Clang19.1.7 Debug CTest|148/148|
|Clang19.1.7 Release CTest|148/148|
|Clang19.1.7 ASan+UBSan native CTest|145/145|
|Guarded Python,each GCC Debug/Release/ASan+UBSan and Clang Debug/Release binding environment|175/175 in **each** of5 environments|
|Frontend unit/contract tests|154passed,0failed,0skipped|
|TypeScript + production build|PASS;initial JS254.45kB,gzip79.06kB;optional deferred OrbitControls/Three.js517.06kB|
|Actual Python→TypeScript market/SEC admission|8+5 assertions passed|
|Packaging-pattern regressions|3/3|
|Installed source-built wheel SDK consumer|8/8|
|Installed wheel recovery cases|19distinct cases passed(18-case run plus new preflight case)|
|Current source archive|1,212members;selected current runtime/test bytes compared exactly;no build/cache/private DB/ZIP/native-binary payload|

Every native configuration executed98 hot-checkpoint assertions,real PMR allocation-failure checks and all eight frozen-reference programs. **All eight identities were actually rerun and matched in all six native profiles.** See `NATIVE_HOT_RECOVERY_EVIDENCE.json` for exact hashes and source/log receipts. Counts above are separate,overlapping cohorts;they are not a fabricated single assertion total.

The175-case developer cohort forbids socket bind/connect and app factories. It includes16 L3/source recovery cases,3 L2 cases and32 XBRL cases alongside existing SEC,history,tape,persistence and stream regressions. Actual process-exit/SQLite restart,stale CAS,uncertain publication,real JSON-node-budget rejection,corruption,storage/resource,subscription and retry scenarios executed. No full app/API/browser cohort was launched.

Clang Python ASan configuration was rejected by the repository's existing GNU/Linux-only Python sanitizer harness. That guard was preserved;Clang native sanitizer and GCC Python sanitizer profiles passed. The GCC harness provides its existing live-LSan coverage,not whole-CPython exit-leak clearance.

## Reproduced failures and corrected validation issues

- Concurrent subscription commands originally produced2 active replacement workers;the independent test required1. Serialized ownership fixes it without dropping coverage.
- Original `47e9b16` publication admitted a fault-injected20,001-node image that restart could not read. A real decoder-budget regression failed before and passes with the prepublication reader check. Durable and in-memory accepted prefixes stay unchanged on rejection.
- A new aggregate test initially referenced nonexistent `GigError`;it was corrected to the SDK's existing `EngineError`. An early new source test expected an exception instead of the specified explicit RECOVERY_REQUIRED result;it now asserts the returned blocked state,unchanged prefix and persisted diagnostics. Neither involved weakening an established mathematical assertion.
- First source-wheel build inherited tooling Python's unavailable `clang++ -pthread` default. Explicit installed `CXX=/usr/bin/g++ CC=/usr/bin/gcc` produced a successful source-built wheel. No production warning or security guard was disabled.

Final failures/errors/skips are zero in the executed cohorts. Existing Starlette/httpx deprecation and the optional JavaScript chunk-size warning remain visible.

## Measured local resource/performance envelope

`terminal/tests/measure_hot_recovery.py` ran at exact source72e175e with GCC Release bindings on x86_64 Intel Xeon Platinum8573C,Python3.12.14. It performs2 warmups and10 measured repetitions with canonical-equality checks. Tracemalloc was enabled and affects timings. Raw samples,fixture/binary hashes,native PMR counters and environment metadata are in `HOT_RECOVERY_BENCHMARK.json`.

| Authored accepted prefix | Checkpoint JSON bytes | Median SDK hot-import + validation |
|---|---:|---:|
|25events|31,148|3.740ms|
|100events|114,152|5.910ms|
|260events|291,702|30.041ms|

Two tiny authored XBRL filings plus cutoff selection:median26.358ms. Process peak RSS57,144KiB;Python tracemalloc peak9,992,822bytes. The260-event prefix builder reported native PMR live6,267,064bytes and peak10,413,304bytes;these counters are for that native owner,not all process allocations. The default coordinator has separately bounded8MiB payload/20,000nodes/depth24 and16MiB DB(+up to16MiB rollback journal). The native journal layout was not redesigned.

An earlier local benchmark invocation measured15.454ms for the260-event import,showing shared-host/instrumentation variability. No performance improvement,SLA,RPO/RTO,exchange latency,observed-market throughput or full-session recovery claim follows from these small fixtures. Timed native import excludes source SQLite commit.

## Completion matrix and exact remaining work

49entries =48reviewed implementation/qualification areas plus1historical A18/A19 decision. **34COMPLETE /7PARTIAL /7BLOCKED /1NOT APPLICABLE**. The counts remain unchanged because stronger approved requirements remain open;the new bounded profiles are not substituted for them. Every row retains code evidence,tests,missing components and a completion condition in `COMPLETION_MATRIX.md/JSON`.

Actionable engineering remains:

1. REL02:full hot ITCH framer/decoder/context/receipt image coordinated with native state;optional product-session wiring and explicit migration/restart semantics. Aggregate images alone do not restore provider lexical checksum/source caches.
2. SEC02:full DTS/schema/type and inline-XBRL transformation,presentation/calculation relationships,extension-taxonomy semantics,complete statement assembly and product integration. Missing original receipts/history cannot be recreated by code.
3. MD06:authoritative observed cancellation/error action profile and complete/lossless sequence/backfill authority. The current IEX source does not establish those guarantees;do not invent them.

Other PARTIAL rows still require current security/target artifacts,full WCAG/device qualification,complete current securities-source coverage or the missing original A18/A19 contract. Seven BLOCKED rows require actual observed L3/reference evidence,current SEC/IEX source qualification,empirical research data,owner-private Codespaces/browser/GPU and current genuine ARM64 results. They are not fixture passes.

Planning only:roughly3–7engineer-days for a tightly scoped remaining full-source/product recovery profile;several engineer-weeks for a specified full XBRL/DTS/inline/presentation profile and independent validation. These ranges depend on source/migration/fidelity decisions and exclude external/hardware qualification. No defensible whole-project completion date or readiness percentage is established.

## Reproduction and continuation

Developer checks only;do not launch or deploy GIG:

```bash
ctest --test-dir <native-build> --output-on-failure -j 4
PYTHONPATH=<native-build>/python:. <venv>/bin/python terminal/tests/run_no_launch_suite.py
PYTHONPATH=<native-build>/python:. <venv>/bin/python terminal/tests/check_trade_contract.py
PYTHONPATH=<release-native-build>/python:. <venv>/bin/python terminal/tests/measure_hot_recovery.py
npm --prefix terminal/web test
npm --prefix terminal/web run build
```

Use the supported sanitizer preload/CMake harness described in `NATIVE_HOT_RECOVERY.md`. The current source is offline verified for the stated bounded contracts. Live-provider,owner Codespaces,physical browser/GPU,native ARM64 and production acceptance remain **not verified**. No credential,gating,trading,provider,paid-resource,workflow,server or deployment action was performed. Continue from the final verified development-branch HEAD;do not restart completed packages or begin owner acceptance under the current no-launch instruction.
