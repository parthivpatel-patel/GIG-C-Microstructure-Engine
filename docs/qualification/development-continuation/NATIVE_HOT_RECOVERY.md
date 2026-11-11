# Native L2/L3 hot recovery — offline developer evidence

The initial L3 implementation was already committed and remotely verified as `47e9b1697b1e528091c3e254458d6d365cd52d7f`. This continuation preserves it, adds restart-reader publication preflight and a full 260-event authored-prefix recovery regression, and adds isolated aggregate L2 state images and bindings. Exact source and executed-log hashes are in `NATIVE_HOT_RECOVERY_EVIDENCE.json`.

## Implemented contract

`OrderBook::checkpoint/restore` preserve full identities, side, price, quantity, level FIFO, ledgers, session, revision, priority and metadata. `ReplayEngine::checkpoint/restore` additionally preserve cursors, deterministic ordering state and logical journal/restart plans. Restoration creates an isolated owner, validates expected rules/configuration/limits and independently trusted canonical bytes, then publishes the owner. Old book events are not reapplied. A healthy image cannot be exported from a recovery-required engine.

`Replay.checkpoint/restore_checkpoint` expose that contract to Python. `NativeSourceRecovery` atomically persists a complete image together with authored source identity, capture session/generation/index, prefix hash and a 32-identity duplicate window. It binds the actual native binary SHA and caller-declared implementation SHA. Gaps, conflicting duplicates and native rejection persist RECOVERY_REQUIRED against the last healthy image. Explicit complete order-level snapshots can resynchronize a newer generation. Unknown initialization and observed origins are rejected.

SQLite publication precedes owner replacement. Actual process exits before/after commit, allocation/storage failure, uncertain acknowledgment, stale writers, corruption and retry idempotency are tested. The JSON restart reader's node/depth budget is now also checked **before** durable publication. A 260-event positive test proves a meaningful authored prefix can reopen;it did not reproduce a prior structural-budget failure. Limits:8 MiB payload,20,000 JSON nodes/depth24,16 MiB database plus up to16 MiB rollback journal,32 duplicate identities. Native replay image limit:4,096 journal records;resource budgets can reject earlier. This is bounded recovery infrastructure,not a long-session archive redesign.

`AggregateDepth::checkpoint/restore` and `_native.restore_aggregate` retain full aggregate levels,initialized state,sequence and revision in a separate image. They reject unsorted/duplicate/zero levels,invalid boundaries,contract mismatch and resource failure. L2 levels contain no order identities or FIFO. Provider lexical checksum caches,raw framing and source-generation authority are **not** recreated from native ticks.

## Executed checks

| Compiler | Debug CTest | Release CTest | ASan/UBSan CTest |
|---|---:|---:|---:|
| GCC14.2 |148/148|148/148|149/149|
| Clang19.1.7 |148/148|148/148|145/145|

Zero final failures. Every configuration ran the98-assertion native hot-checkpoint test,real PMR allocation-failure sweeps,aggregate-depth contracts and all eight frozen-reference programs. Every expected frozen hash matched. CTest totals include independent Python reference programs and applicable SDK tests;they are not C++ assertion totals. Clang sanitizer excludes Python bindings because the repository's existing Python ASan harness explicitly supports GNU/Linux only. This unsupported configuration was recorded,then the supported Clang native sanitizer profile was executed;the guard was preserved.

The18 real-native Python recovery tests passed separately with GCC Debug,Release and ASan/UBSan bindings:15 L3/source/persistence cases and3 aggregate-image cases. The sanitizer cohort took93.194 seconds under concurrent local compiler/test load;this is not a replay throughput or recovery-time SLA. A new test initially named the SDK exception incorrectly (`GigError`);it was corrected to the existing `EngineError`,and all3 L2 tests then passed without changing production behavior. The original error log is retained locally and is not presented as a product defect.

## Reproduction without launching GIG

Configure normal CMake developer builds with `BUILD_TESTING=ON`,warnings-as-errors and the desired compiler/build/sanitizer flags. Enable Python for supported configurations. Build,then:

```bash
ctest --test-dir <native-build> --output-on-failure -j 4
PYTHONPATH=<native-build>/python:. <venv>/bin/python -m unittest terminal.test_native_recovery terminal.test_aggregate_recovery
```

GCC Python ASan uses the existing CMake live-LSan/preload profile (`LD_PRELOAD` matching compiler libasan and libstdc++;`PYTHONMALLOC=malloc`,halt-on-error). Do not import a sanitizer extension into an uninstrumented interpreter without that profile. See CMake's `python_test_environment` and the source-bound receipts. No app/server/browser/provider/deployment test was run.

## Remaining boundaries

This is an authored typed-native recovery profile. It is **not** a full hot image of ITCH decoder/framer/context/receipt state. Existing ITCH restart reconstructs from its authenticated synthetic boundary;that separate behavior remains unchanged. Complete observed initialization,an authoritative observed source contract and independent observed order-level evidence are still required for empirical L3 claims. IEX Level1 does not supply that evidence. Local integrity hashes are not source authentication;SQLite synchronous-FULL tests do not establish arbitrary filesystem/power-loss guarantees. No current native ARM64 run,owner Codespaces qualification or production acceptance is claimed.

## Final continuation regression

A real JSON-node-budget fault injection was also run against the original `47e9b16` coordinator loaded from Git:it committed an image with20,001 injected metadata nodes instead of raising before publication. Exactly one regression failed as expected. The current prepublication reader check rejects that image while preserving both in-memory and reopened accepted prefixes. This additional case raises the current standalone recovery cohort to19 cases (16 L3/source and3 L2),and the guarded broader cohort to175. All175 passed with GCC Debug/Release/ASan+UBSan and Clang Debug/Release. The earlier18-case receipts remain historical executed results,not relabeled counts. The same new case also passed using the installed source-built wheel,completing19 distinct installed recovery cases alongside8 SDK-consumer cases. No further C++ runtime changes occurred after the six compiler/reference runs.
