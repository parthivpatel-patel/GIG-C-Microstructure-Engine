# LOBSTER validation program — consolidated engineering report

## Assessment and permission boundary

All feasible synthetic engineering packages are complete. Actual historical CSV
processing and empirical reconstruction remain **BLOCKED**, following the owner's
explicit clarification that third-party cloud processing permission is not established.
The completed software is preparation for an authorized private pilot, not evidence
of historical accuracy or production trading readiness.

Before that clarification, bounded ZIP structural/CRC verification, full included
README inspection and private extraction occurred. Those actions are recorded in
LOBSTER_DATASET_ACCEPTANCE.md; no historical CSV row analysis occurred. No attached
ZIP/extracted CSV access occurred after the restriction. Earlier private copies remain
untouched outside Git pending applicable retention/disposition instructions.

Source supplied by owner: official LOBSTER samples at
https://php.lobsterdata.com/info/DataSamples.php . Relevant terms supplied by owner:
https://data.lobsterdata.com/imprint.php and
https://php.lobsterdata.com/termsAndConditions.php . Public availability and an
unlicensed README do not establish cloud processing or redistribution permission.
No restricted raw rows, observations, ZIP, CSV, credentials or tokens are delivered.

Historical archive metadata (recorded before restriction):4,791,006 bytes,
SHA256 `46419dd0d6106be5fcf43600ccd08b2baa5d4cfb76284f1c58773537a3adac50`.
CRC/path/type/count/size/expansion checks passed at that time. This does not validate
CSV semantics, observed initialization, completeness, or permissible cloud use.

## Durable checkpoints

Entry: `3461a5ee571aa7639ac7939f5c91d6d8708ded02`.
Protected main: `12f3a53943dc245e36f2cbbc35b9910fb21c0718`.

| Phase | Commit | Delivered scope |
|---|---|---|
|1|`c90f753c9552adbc11a8bb2f844e61957c57ac9f`|Historical archive inspection record, usage gate, private-data exclusions|
|2|`3522808b7080d21eb20c04e6f3ea8e00fdc0bf21`|Bounded exact CSV parsing and independent authored oracle|
|3|`2a6d4602fad1eaae35170d894b466a2fc409db15`|Unknown-initial-state native subset and conditional comparisons|
|4|`3b3c9936255cecba1616101c6626b454255919be`|Adversarial, compiler, sanitizer, package and reproducibility evidence|

This separate consolidation changes documentation/evidence only. Its exact commit
is resolved with `git log -1 --format=%H -- docs/REAL_MARKET_VALIDATION_REPORT.md`
and recorded in the delivery response; a document cannot embed its own commit SHA.

## Implemented interfaces and comparison semantics

`gig::lobster` parses six message columns and twenty reference columns exactly:
nanosecond decimal seconds, integer Price(4), shares, IDs and resting side. Types1–5
and7 follow the supplied README;6/unknown remain explicit unsupported events.
Hidden executions and halt observations do not become displayed-book orders.
Sentinel tail levels are distinct from real zero-volume, locked and crossed states.
These anomalies are counted, not silently repaired. Paired EOF/time/order/column /
numeric/overflow failures stop deterministically with safe row diagnostics.

`gig_lobster_validate` supports bounded paired streaming, same-read raw-file SHA256
verification, provenance, conditional reference effects and an existing-native-book
known-order subset. Unknown initial state stays unknown. No aggregate depth becomes
invented order IDs/FIFO. Unknown references, retired-ID reuse, contradictions,
unsupported native semantics and insufficient depth coverage are explicit. Native
prefix application stops rather than guessing. Existing matching/execution/TCA /
journal/recovery implementations are unchanged.

Modes are separate: reference observation; legitimately known event-driven subset;
constrained lower-bound/equality checks; independent conditional reference-transition
checks. Quantity, best-price and full-depth comparisons each have their own eligibility
denominator. First row, hidden deeper liquidity, sixth-level revelation, incomplete
history and anomalies restrict eligibility. No overall L3 accuracy statistic exists.

Limits include4096-byte lines, explicit byte/record/time caps, bounded lifetime-ID
tracking and PMR budget. Current lifetime scans are linear and capped100k; this is
not a whole-day scalability qualification. PMR budget is not whole-process RSS.
The private runner requires operator permission attestation before opening input;
it is not an automated legal verifier. Archive tooling has immutable bounded copies,
central-directory preflight, CRC, traversal/special-file/ratio checks and atomic
rollback; it was tested only on independently authored archives after restriction.

## Actual empirical results

| Historical metric | Result |
|---|---|
|Message/reference rows, timestamps, frequencies, anomalies|null — not processed|
|Eligible/ineligible comparisons|null — blocked|
|Exact matches/mismatches/accuracy| null — not measured|
|Unknown historical references/first divergence| null — not measured|
|Historical parsing/replay throughput| null — not measured|

Evidence Level1 authored correctness and Level2 independent algorithmic agreement
are demonstrated within tested scope. Level3 observed structural validation and
Level4 partial observed book agreement are blocked. Level5 complete empirical L3
is not established: five aggregated levels cannot prove complete initial IDs/FIFO
or hidden/deeper history even if all visible comparisons eventually agree.

## Independent tests, failures and repairs

Independent Decimal/regex parsing and dictionary/level-map reference effects do
not import native book transitions. Final cohorts in each of nine candidates:
82 parser cases,12 reconstruction scenarios/32 authored rows and13 adversarial
workflow methods. Controls cover missing/duplicate records, changed price/size/type /
time/reference alignment, unknown IDs, false completeness, checksums, limits,
permission-before-open, determinism, allocation failure and malicious authored ZIPs.
Unobservable omissions or arbitrary monotonic time changes require authenticated
input evidence; they cannot be detected from aggregate observations alone.

GCC14 optimized Release rejected the generic std::sort internal threshold path
for at most six candidate levels under -Werror=array-bounds. Replaced it with
explicit bounded insertion sorting after proving five prior slots plus one insertion.
No warning suppression, changed expectation, padded state or weakened assertion.
Before-repair logs are retained locally. No actual-market engine defect is claimed.

## Full local validation

Toolchains:GCC14.2.0-19,Clang19.1.7,CMake3.31.6,Python3.12.14 on x86_64.

| Configuration | Passed | Failed / skipped / disabled |
|---|---:|---|
|phase9-clean-debug|154|0 / 0 / 0|
|phase9-clean-release|154|0 / 0 / 0|
|phase9-clean-asan-ubsan|154|0 / 0 / 0|
|phase9-clang-debug|154|0 / 0 / 0|
|phase9-clang-release|154|0 / 0 / 0|
|phase9-clang-asan-ubsan|154|0 / 0 / 0|
|python-debug|157|0 / 0 / 0|
|python-release|157|0 / 0 / 0|
|python-asan-ubsan|158|0 / 0 / 0|

Total **1396/1396** CTest outcomes. Existing seeded reconstruction, independent
models, allocation failure, journal/recovery and deterministic replay remain covered.
Additional final direct module checks passed in all nine candidates. All eight frozen
identities are unchanged (full values below and in machine-readable evidence).
Fresh checkout and source-built wheels passed28 installed interface/export checks,
4 export-failure checks and2 identical research examples;14 packaging steps passed.
Additional receipt-verifier10 tests and3 source-pattern controls passed. Source
archive407 inventory members include406 Git source files matching immutable Phase4
bytes/SHA256; generated PKG-INFO is excluded from Git comparison. No bit-identical
wheel claim. Final documentation additions follow the tested source snapshot.

- `itch.independent_reference`: `142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e`
- `itch.context_reference`: `58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e`
- `itch.l3_reference`: `bb16d4ba9e400ee8f2bc40707de5aa89d0b0955819b4f1f45ca2cdf82cac7991`
- `itch.streaming_reference`: `be5d6f5a15fa1dc77560e0a815b8397a605eab369fa66f44df12e5ed9b04a4d5`
- `itch.validation_demo_reference`: `4ebdd734b5f11e368be1525f95a93070893ec14e9caafb161583807c88d23520`
- `itch.hy_reference`: `ad982777da3595d8fb608755a4986e68a19c3ab2721ec1e1e084f1945f0412af`
- `itch.admin_reference`: `87556148fdc43cb7d3c073aa5a5fa9a0b9a6368c15a5182edb72bced17957d03`
- `itch.auction_reference`: `76ad62693c22631e4be0842f44029d779211451a395e8538d70450ae7015ebc6`

Detailed commands, counts, JUnit/log hashes, source hashes, oracle digests, package
receipts and limitations: [machine-readable evidence](evidence/lobster_independent_validation.json).
Immutable source binding: [source comparison](evidence/lobster_source_binding.json).
Raw full logs remain in ignored build/lobster-program/phase4; their hashes make
later retrieval checkable but do not substitute for an independent-machine rerun.

## Authored performance measurements

Clang Release x86_64,one warmup/three repetitions,20k parser pairs and2k full pipeline
rows per repetition. Approximately2.67–3.07 million parser pairs/sec and250–268k
pipeline rows/sec. Pipeline includes file I/O, hashing, reference and native-subset
processing. PMR peak2,961,744 bytes; child peak RSS12,672KiB;4018 tracked allocations
per measured pipeline run. Invalid-input subprocess timing2.29–2.48ms includes
startup. Source hashes/workload/timers are bound in the evidence. These are small
authored workload measurements, not historical throughput, latency or exchange claims.

## ARM64, readiness and remaining risks

Official public run40151444307:
https://github.com/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/runs/40151444307
identifies3461a5ee571aa7639ac7939f5c91d6d8708ded02,feature branch,Success,six
completed jobs and8m22s duration. Owner confirms qualification5 passed. Signed-in
raw job logs/artifacts were unavailable; no invented compiler/JUnit details.
**New implementation commits are not native-ARM64-qualified.** No workflow dispatched.

Unknown initialization, unsupported type6, legitimate crossed-state native policy,
linear lifetime tracking and lack of observed/independent full-order references are
explicit limitations. Existing provider/security/formal release gates remain open;
this work does not accept those risks or claim production readiness. Public evidence
publication still requires derivative-disclosure review after any authorized pilot.

## Reproduction and exact next actions

Follow [LOBSTER_REPRODUCIBILITY_GUIDE.md](LOBSTER_REPRODUCIBILITY_GUIDE.md) for
allowed authored commands, exact manifest fields, checksums, failure interpretation
and future private-only commands. Do not execute the private path yet.

1. Obtain reviewed permission covering this third-party cloud's processing/storage,
   retention and permitted derivative reporting; clarify disposition of earlier
   quarantined copies. Do not infer permission from download availability.
2. Once authorized, use an authorized private copy and new private manifest/output;
   verify checksums/profile/paired alignment, then review per-metric eligibility.
   Report only approved safe derivatives. No acquisition is needed for this code work.
3. Owner may separately dispatch manual qualification of the new exact implementation
   SHA and preserve signed-in artifacts. Prior ARM runs cannot qualify new code.
4. For full empirical L3, obtain independently authenticated complete initial
   order identities/FIFO and comprehensive order-level evidence, beyond five levels.

Next milestone:permission-gated bounded private structural/conditional-reference
pilot, followed by discrepancy review. No live/broker/paid/data-download/release /
main/workflow change is implied. All feasible offline phases are closed; empirical
work remains blocked. No process continues after this session ends.

## Complete changed-file inventory

Relative to entry3461a5e, including this documentation closure:

- `.gitignore`
- `CMakeLists.txt`
- `docs/LOBSTER_ADAPTER_DESIGN.md`
- `docs/LOBSTER_DATASET_ACCEPTANCE.md`
- `docs/LOBSTER_DATA_USAGE_RESTRICTIONS.md`
- `docs/LOBSTER_DIVERGENCE_ANALYSIS.md`
- `docs/LOBSTER_EMPIRICAL_RECONSTRUCTION.md`
- `docs/LOBSTER_INDEPENDENT_VALIDATION.md`
- `docs/LOBSTER_REFERENCE_VALIDATION.md`
- `docs/LOBSTER_REPRODUCIBILITY_GUIDE.md`
- `docs/evidence/lobster_dataset_acceptance.json`
- `docs/evidence/lobster_empirical_results.json`
- `docs/evidence/lobster_independent_validation.json`
- `docs/evidence/lobster_parser_validation.json`
- `examples/lobster_validate.cpp`
- `include/gig/lobster/adapter.hpp`
- `include/gig/lobster/reconstruction.hpp`
- `scripts/benchmark_lobster_synthetic.py`
- `scripts/check_lobster_reconstruction.py`
- `scripts/check_lobster_reference.py`
- `scripts/lobster_archive.py`
- `scripts/lobster_synthetic.py`
- `scripts/run_lobster_validation.py`
- `src/lobster/adapter.cpp`
- `src/lobster/reconstruction.cpp`
- `tests/support/lobster_checks.hpp`
- `tests/test_lobster.cpp`
- `tests/test_lobster_workflow.py`
- `tests/test_observed_readiness.py`
- `docs/REAL_MARKET_VALIDATION_REPORT.md`
- `docs/evidence/lobster_source_binding.json`
- `docs/OVERNIGHT_ENGINEERING_PROGRESS.md`
