# GIG durable ITCH recovery development — November 11, 2026

The clean starting branch and remote both matched `d2120bb6812d38f30c5fc529b5ddf1b179c08147`. The new runtime is `1f07e43c71e8db7377a1e16c6b88c049a6591b4f` on `development/gig-ui-redesign`. Both implementation checkpoints below were pushed and checked against the remote. The final documentation-only commit is identified by Git, not self-embedded here.

|Published commit|Implementation|
|---|---|
|`b997b85d7640045ceb0a42029dafc5b95a4c94b3`|Versioned full typed ITCH artifact, Python/native admission and immutable files, seeded hot restoration and coordinated plain/gzip source continuation; impossible empty-cursor repair.|
|`1f07e43c71e8db7377a1e16c6b88c049a6591b4f`|Strict DTS simple-XLink reference repair and expanded guarded offline regression cohort.|

## Completed engineering

The durable version-1 format preserves both order-level native books, journal/cursor state, full ITCH context, directories, active/inactive and seed-retired references, matches and broken flags, lifecycle, source cursors, receipts, initialization evidence, configuration and provenance. Field encoding is deterministic and bounded; decoding rejects corruption, invalid lengths/types/tags/versions and inconsistent native/context state. Independently retained artifact/configuration/code/capture/generation evidence is required. Embedded hashes are not authentication. No automatic artifact/schema/code migration is allowed.

Authored-empty and complete authored-seed hot images restore directly, without applying committed events again. Seed priority, retired references, match state and the seed recovery journal boundary survive restoration. An impossible zero-record source cursor was reproduced against the published starting implementation and now fails admission even with a recomputed typed fingerprint.

The installed Python SDK exposes a native recovery owner with status, both canonical books, recapture and explicit complete-record continuation. Private-file operations validate before writing, fsync complete bytes, atomically publish new immutable revisions without overwriting rollback inputs, and fsync the directory. Disk-full and abrupt cross-process exit tests distinguish no publication from uncertain publication. The latter requires reopening with trusted admission; no RPO/RTO or hardware power-loss guarantee is inferred.

Plain BinaryFile and complete single-member gzip coordination start at the independently specified source boundary, compare committed frames to retained receipts without applying them, then apply only the suffix. Seeded tails work. CRC/trailer failure discards the isolated candidate. Source mismatches, altered/missing committed frames, stale generations, gaps, partial frames, incomplete gzip, trailing members and resource exhaustion fail closed. Active-prefix version 1 explicitly rejects terminal cursors and arbitrary compressed seeks. Gzip framing/decompression is repeated from container byte zero; committed native/source transitions are not replayed.

DTS discovery previously accepted missing/empty/extended XLink types on a linkbaseRef and could report a usable graph. Three independently authored invalid shapes reproduced that failure. The parser now requires a simple reference. Full XBRL type/transform/relationship/accounting validation remains partial; no financial values, source receipts or historical coverage were invented.

See [format, trust and recovery contract](DURABLE_ITCH_RECOVERY.md). The explicit member inventory, tests and source hashes are in [current evidence](DURABLE_ITCH_EVIDENCE.json).

## Actual developer validation

|Configuration|CTest passed|
|---|---:|
|GCC 14.2 Debug|152/152|
|GCC 14.2 Release|152/152|
|GCC 14.2 ASan+UBSan|153/153|
|Clang 19.1.7 Debug|152/152|
|Clang 19.1.7 Release|152/152|
|Clang 19.1.7 native ASan+UBSan|148/148|

Each configuration executed 363 durable checks and 163 source-recovery checks, including measured sweeps over **57 decode/restore, 63 encode and 67 source/gzip restoration allocation points**, with cleanup assertions. Existing 221 typed hot-context checks and all eight frozen native identities were also executed and matched in every profile. These are overlapping cohorts, not a single invented assertion total.

The guarded Python cohort passed **273/273** in each of five supported binding configurations: GCC Debug/Release/ASan+UBSan and Clang Debug/Release. Zero final failures, errors or skips. It includes nine new real-native durable/file/cross-process cases and 49 XML cases. Binding objects are real; provider fixtures are authored. Socket bind/connect and application factories are forbidden in this cohort. Clang Python ASan remains unsupported by the existing harness; Clang native sanitizers and GCC Python sanitizers passed. Existing live-interpreter LSan coverage is not whole-CPython exit-leak clearance.

The clean `1f07e43` source archive contains **1,246 members**; all18 changed runtime/test entries match committed bytes. The wheel was built from that extracted archive,contains22 members,and its new recovery module matches source. Installed tests run from the extracted source passed **8 SDK consumer checks and37 native/aggregate/session/ITCH recovery cases**. No-index/no-dependency installation and private/cache/build payload exclusions passed. All six compiler/configuration fixture encodings are also byte-identical (12,834 bytes for nine authored source records). Exact receipts are recorded in `PACKAGE_CURRENT.json` and the durable evidence. No artifact was published as a release. Frontend source and dependencies were unchanged; prior frontend/build evidence remains source-bound historical evidence and was not rerun. Browser, WebGL, owner HTTPS/WSS and physical-device tests were not launched. No new production latency, throughput, recovery SLA or hardware durability claim is made.

## Failures retained and repaired

- New-code compilation initially caught a misleading-indentation diagnostic, a nonportable char range check and an incorrect CMake target name. All were repaired; strict warnings remain enabled.
- An initial allocation test left failure injection armed while requesting a new canonical allocation. It now measures the exact restoration allocation count and sweeps those points without an unrelated diagnostic allocation.
- An initial corruption fixture accidentally repaired the header bytes it intended to corrupt. It now preserves those corruptions while independently updating only the external expected artifact digest.
- CTest exposed a child-process import failure from its build-directory working directory. The child now selects the repository working directory explicitly; all nine cases and all final profiles pass.
- Published empty-cursor and DTS-reference defects have actual failing-before receipts. Intermediate failed logs are retained and are not counted as passing results.

## Remaining scope and effort

The matrix retains **50 entries: 49 reviewed areas plus the historical A18/A19 decision**. Counts remain **34 COMPLETE / 8 PARTIAL / 7 BLOCKED / 1 NOT APPLICABLE**. The bounded durable/seed/source requirements are now implemented; this does not silently close the stronger product/source/hardware requirement.

Remaining engineering includes explicit opt-in full-ITCH product/startup session selection alongside the existing authored-native NativeSession recovery, full Inline-XBRL transformations/continuations, full schema/custom-type and cross-link relationship semantics, complete financial-statement assembly and v2/UI integration. Automatic startup was not enabled. Additional schema/container profiles require explicit tested contracts; current partial/terminal-position rejections are intentional supported-profile boundaries.

Conditional planning ranges are 1–3 engineer-days for narrowly scoped product-session selection/integration and its failure matrix, and several engineer-weeks for scoped full XBRL semantics and statement integration. These are estimates, not a committed completion date. Some remaining work is engineering, not merely external access.

External evidence remains required for actual observed L3 initialization/reference, lossless observed trade/backfill authority, current authoritative listing coverage, original A18/A19 requirements, current native ARM64, private Codespaces/browser/device/security target and hardware durability. IEX permissions/execution/retention gates were unchanged. No real IEX qualification is claimed. Kraken remains provisional: official current protocol/rights material was not obtained, known blocked documentation probes were not retried, and no wire-contract authority was invented.

No application/factory/server/listener, provider/account connection, deployment/workflow, trading or paid infrastructure was started. Restricted historical data was not accessed. Protected branches and GIG-only frontend branding were preserved. **Full development and production qualification are not complete.**

Next engineering action: use the completed SDK/file layer to implement a narrowly scoped, explicitly selected full-ITCH product-session recovery policy. Do not reimplement the codec or repeat unchanged matrices. Keep provider/owner acceptance separate and preserve version-1 rejection rules.
