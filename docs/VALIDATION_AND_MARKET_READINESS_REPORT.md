# Validation, security and market-readiness program

## Executive assessment

Four independently validated engineering checkpoints are committed/pushed on
`feat/bootstrap-cpp20-engine`; this consolidated report is a separate documentation
commit. Entry:1548afb61ef857b2312488df630ee6a9defbe4da. Protected main remains
12f3a53943dc245e36f2cbbc35b9910fb21c0718. Each push used `[skip ci]`: no workflow
was dispatched or intentionally triggered. No market-data acquisition, paid resource,
live execution, Terminal change, release or history rewrite occurred.

**Current status: qualified local synthetic behavior; partial security/provider
closure and partial observed-data readiness. No production or observed-market L3
qualification. Current source is ready for an owner-authorized ARM64 run, not already
native-qualified.** Externally unavailable evidence is explicitly left open.

## Durable checkpoints

| Phase | Exact pushed commit | Scope/status |
|---|---|---|
|1 Security|`c9df510a7f4c926715a8b0a8d0c1350cca33d85a`|Focused verifier repair/classifications complete; provider closure PARTIAL|
|2 Evidence/readiness|`fe45cadb03e21e285268b0c2f6aeb096e5eeec5d`|Public metadata/local gates complete; signed-in raw hosted archive PARTIAL|
|3 Adapter|`8ea9f62cf3c811633cd9b7344df1c9df23f6d576`|Bounded ingress/context/native synthetic bridge complete; observed native-L3 BLOCKED|
|4 Differential validation|`75246ea7c4cd86ecfc11d254e2cec285352055b8`|Synthetic byte-adapter differential/diagnostics complete; observed comparisons BLOCKED|

The final report commit is identified by Git history and the delivery response;
its own SHA cannot be embedded in its own content. All four checkpoints were
verified at remote feature HEAD after their push, and remain ancestors of delivery.

## Phase1: security and provider closure

See [residual risks](SECURITY_RESIDUAL_RISKS.md),
[qualification](SECURITY_QUALIFICATION.md) and
[machine-readable closure](evidence/security_closure.json).20 classified entries:
17 unresolved due to insufficient evidence,2 mitigated,1 confirmed non-applicable
specific executable path. No residual risk accepted on the owner's behalf.

Confirmed tool resource-policy gap: per-artifact limits lacked aggregate/count
bounds. Verifier now preflights <=256 artifacts/128MiB aggregate before hashing,
keeps64MiB/file and enforces actual read budgets. Two authored regressions failed
before repair; final10 receipt controls pass. The authentic prior157-case archive
still verifies. Concurrent hostile filesystem mutation is not certified.

CVE-2026-22184's contrib/untgz path is not deployed, not blanket zlib clearance.
Expat UTF16-specific path is mitigated by strict UTF8/NUL/DTD/entity rejection;
other provider applicability remains unresolved. Managed OpenSSL3.5.8 versus13
named3.5.9 advisories, CPython3.12.14 versus3.12.15, Expat/vendor/kernel/toolchain
patch identities and actual reachable functionality need provider evidence. No
absence-of-findings security claim or unsupported affected-range inference.

Official checkout v6.1.0 immutable SHA
`d23441a48e516b6c34aea4fa41551a30e30af803` was rechecked against upstream Git tag;
Node24/read-only permissions/persist-credentials:false retained. This program did
not alter workflows. Full bundled action SBOM/advisory mapping and current hosted
execution remain unverified. No managed runtime or network policy was changed.

## Phase2: native ARM64 evidence

[Archive](ARM64_EVIDENCE_ARCHIVE.md),
[manifest](evidence/arm64_evidence_manifest.json),
[owner procedure](CURRENT_HEAD_ARM64_READINESS.md).
Historical run40126420107 atf02363e0e09b9767b4dc6748737206254e5e4c6a:
all six GCC/Clang Debug/Release/ASan+UBSan jobs succeeded on the native ARM64
workflow; overall7m22s. Available official public metadata/job IDs/step results and
original collection receipts were rearchived with checksums. This is not a new run.
Raw authenticated logs/JUnit/compiler/CMake outputs remain unavailable; official
links and availability fields preserve that limitation. No repeated Forbidden API
retry or substitute local evidence described as hosted output.

**Previous native ARM64 qualification applies only to its tested commit. Current
HEAD remains pending a new hosted qualification run.** Standard ubuntu-24.04-arm,
manual-only workflow_dispatch, default-false free_usage_verified, feature guard,
existing60-minute job ceiling and strict test/hash policy are preserved. Owner must
reconfirm public/free eligibility and explicitly authorize dispatch. No artifact
upload/retention service or cost was introduced.

## Phase3: adapter and initialization

[Adapter](OBSERVED_DATA_ADAPTER.md),
[initial-state contract](LEVEL3_INITIALIZATION_CONTRACT.md),
[validation evidence](evidence/market_data_adapter_validation.json).
New C++20 `gig::itch_input_adapter` / `BinarySourceAdapter` incrementally pulls raw
BinaryFile frames, checks exact consumed-byte digest/boundaries, preserves source
provenance, reports physical records/errors and returns owned normalized context
or synthetic native transaction receipts. No network/filesystem/gzip acquisition.
Explicit <=128MiB input/100000 records/65535-byte framer buffer plus existing context
limits; caller-governed PMR required for a hard total allocation budget.

Dataset contract includes provider/dataset/acquisition/permission/redistribution/
initial-state references, optional validated Gregorian date, capture boundaries,
known gaps and existing source digest/origin/session identity. Symbols/instruments
remain bound through source context/native synthetic rules. References are caller
assertions, not legal or exchange authentication. No missing date/sequence invented.

Unknown, session-start, snapshot or incomplete observed claims are context-only:
no native book, no full-L3/publication eligibility. Native route requires authenticated
authored synthetic factory evidence and matching policy/source. No lossy observed
origin conversion. Current initialization categories are represented but **verified
observed start/snapshot eligibility is not implemented or supplied**. Unknown orders,
corrupt/truncated input and gaps fail closed; restart is replay from authenticated
boundary, not hot snapshot recovery.

Tests cover chunks1/7/4096, lifecycle/unknown/duplicate/unsupported records, claims,
invalid provenance/date, digest contradictions, EOF truncation, record caps,
interruption/move/finished state and real PMR allocation-failure sweeping to success
with zero leaked live bytes and consistent accepted native/context positions.
Observed-origin policy tests are authored mocks, not observed datasets.

## Phase4: independent validation and divergences

[Independent model](INDEPENDENT_BOOK_RECONSTRUCTION.md),
[reproduction commands](ORDER_BOOK_DIFFERENTIAL_VALIDATION.md),
[complete results](evidence/order_book_validation_results.json).
Simple independent Python flat-order/source-state model computes expected state
from authored source bytes and rational rules. It does not import C++ transitions.
The real adapter/native candidate is compared after every source event: order/FIFO,
price/depth/best, lifecycle, ledger, receipts/provenance/derived sequences, journal
counts, refusals and completeness; independent input digest/accounting checks too.
Same-session authorship is disclosed: architectural independence is not third-party
certification or proof against common semantic misunderstandings.

Supplement:164 fragment schedules,2228 event-prefix comparisons,seed5255495;
fragments1/257, bounded books up to128 active orders/32 price levels, extreme
quantities, repeated cancellation and fixed-seed grammar/byte mutation cases.
Original10032 sessions/65186 source candidates and prior67-session/476-prefix
supplement remain intact. New supplement expected-state digest:
`d33e05d6a6143aec86a2b04ab6d6629ee071ee7164f93dd7a1adc9e7c26d0807`.

An intentionally corrupted expected quantity is detected at event3/typeA/field
`.books[0].orders[0][3]`. Re-executed four-record first-diverging prefix reproduces;
both negative-control commands deliberately exit1. This is not an engine defect.
Report includes dataset/digest/seed/type/index/states/field/fixture/replay command.
Global delta-minimality is not claimed. Candidate crash/timeout retains an unknown
index/type and original bounded fixture rather than inventing source evidence.
Eight report/budget/type/refusal controls pass. Input/report2MiB, combined child
output32MiB,120-second child deadline, explicit termination/reap; PMR128MiB in
candidate driver, not a whole-process RSS guarantee. Observed replay is refused.

## Final executed local validation

Local x86_64 only: Debian GCC14.2.0-19, Clang19.1.7,CMake3.31.6,Python3.12.14.
Each row includes configure/build/CTest, with all eight canonical identities checked.
Final test-source hashes/JUnit/log digests bind precommit working code to Phase4;
final report-only edits do not change tested source. No emulated/nativeARM test of
this new adapter is claimed. No source changes followed final successful matrix.

| Configuration | Passed | Failed | Skipped | Disabled |
|---|---:|---:|---:|---:|
|phase9-clean-debug|154|0|0|0|
|phase9-clean-release|154|0|0|0|
|phase9-clean-asan-ubsan|154|0|0|0|
|phase9-clang-debug|154|0|0|0|
|phase9-clang-release|154|0|0|0|
|phase9-clang-asan-ubsan|154|0|0|0|
|python-debug|157|0|0|0|
|python-release|157|0|0|0|
|python-asan-ubsan|158|0|0|0|

**1396/1396 final CTest outcomes;0 failures/skips/disabled.** All native/Python
ASan+UBSan configurations actually executed; no finding suppressed. Existing
allocation-failure, replay/journal, independent reference and determinism cases
remain in these suites. Separate Phase2 and Phase3 matrices each also passed1396;
these are repeated configuration outcomes, not distinct new test cases.

Fresh checkout wheel and wheel rebuilt from source archive:28 installed interface/
export checks total,4 export-failure controls,2 deterministic research examples with
identical semantic output.14 build/install/check steps exit0. Source archive358
safe intended byte-identical members; all new adapter/harness source included.
Three packaging-pattern controls,10 security receipt controls and8 harness controls
pass (the latter also executes inside the oracle CTest). No failed/skipped checks in
these final gates. Wheel archives have different hashes; bit-identical wheel builds
are not claimed. Exact artifact sizes/digests are in Phase4 evidence. No public upload.

Development attempts included a -Werror indentation warning in a fixture and a
candidate-printer edit referring to an undeclared identifier. Both were corrected
before acceptance; original printer restored byte-for-byte, assertions/-Werror
preserved. Intentional failing-before security tests and negative controls remain
clearly separated from final passing suites. No new production-engine mismatch was
established by the independent model. No journal optimization was introduced.

## Preserved canonical SHA256 identities

| CTest oracle | SHA256 |
|---|---|
|itch.independent_reference|`142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e`|
|itch.context_reference|`58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e`|
|itch.l3_reference|`bb16d4ba9e400ee8f2bc40707de5aa89d0b0955819b4f1f45ca2cdf82cac7991`|
|itch.streaming_reference|`be5d6f5a15fa1dc77560e0a815b8397a605eab369fa66f44df12e5ed9b04a4d5`|
|itch.validation_demo_reference|`4ebdd734b5f11e368be1525f95a93070893ec14e9caafb161583807c88d23520`|
|itch.hy_reference|`ad982777da3595d8fb608755a4986e68a19c3ab2721ec1e1e084f1945f0412af`|
|itch.admin_reference|`87556148fdc43cb7d3c073aa5a5fa9a0b9a6368c15a5182edb72bced17957d03`|
|itch.auction_reference|`76ad62693c22631e4be0842f44029d779211451a395e8538d70450ae7015ebc6`|

All eight match across all final nine configurations; no golden fixture regenerated.
Supplementary digests are separate and do not replace frozen identities.

## Remaining gaps and next milestone

1. Obtain dated provider patch/backport/reachability evidence or a supported qualified
   runtime update; owner alone may explicitly accept residual security risks.
2. Owner-authorized six-job native ARM64 qualification of the new feature HEAD.
   Export signed-in logs/JUnit/compiler/CMake evidence for archival; current local
   passes cannot transfer the historical native qualification.
3. Implement an independently validated observed source/evidence verifier and complete
   context/native/FIFO seed/projection path. No session message, arbitrary file start,
   aggregate snapshot or caller declaration is sufficient initialization evidence.
4. Separately authorize a resource-bounded private acquisition/validation pilot after
   rights, storage and initial-state gates. No acquisition was performed here.
5. Align an independent observed reference and establish per-event comparison coverage,
   unsupported semantics and gap detection. The current differential loader is
   synthetic-only and explicitly refuses observed input; this work is planned.
6. Retain existing production exclusions: finite journal/context capacities, no
   certified crash-safe recovery/operations, no external institutional certification,
   no live-market execution guarantees. Existing audit/history remains preserved.

Highest-value engineering milestone: **validated observed-initialization evidence and
projection contract with an independent seeded-state oracle**, followed by a separately
authorized bounded observed comparison. In parallel, owner may authorize the current
native ARM qualification and obtain provider evidence. No full archive download,
release, merge, live execution or risk acceptance is authorized by this report.

## Complete changed-file inventory for this program

Files below compare entry1548afb to final source checkpoint, plus the report-only
readiness overlays. No raw market-data bytes, credentials, binaries or build outputs
are tracked. Historical institutional audit and main are unchanged.

- `CMakeLists.txt`
- `docs/ARM64_EVIDENCE_ARCHIVE.md`
- `docs/CURRENT_HEAD_ARM64_READINESS.md`
- `docs/ENGINEERING_READINESS_MATRIX.md`
- `docs/INDEPENDENT_BOOK_RECONSTRUCTION.md`
- `docs/LEVEL3_INITIALIZATION_CONTRACT.md`
- `docs/OBSERVED_DATA_ADAPTER.md`
- `docs/ORDER_BOOK_DIFFERENTIAL_VALIDATION.md`
- `docs/SECURITY_QUALIFICATION.md`
- `docs/SECURITY_RESIDUAL_RISKS.md`
- `docs/VALIDATION_AND_MARKET_READINESS_REPORT.md`
- `docs/evidence/arm64_evidence_manifest.json`
- `docs/evidence/market_data_adapter_validation.json`
- `docs/evidence/order_book_validation_results.json`
- `docs/evidence/security_closure.json`
- `include/gig/itch/input_adapter.hpp`
- `scripts/check_adapter_differential.py`
- `scripts/check_itch_l3_reference.py`
- `scripts/verify_reproduction.py`
- `src/itch/input_adapter.cpp`
- `tests/itch_l3_reference_driver.cpp`
- `tests/support/itch_input_adapter_checks.hpp`
- `tests/test_adapter_differential.py`
- `tests/test_itch_reconstruction.cpp`
- `tests/test_reproduction_verifier.py`
