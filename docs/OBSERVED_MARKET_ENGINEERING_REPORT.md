# Observed-market engineering program report

## Executive assessment and delivery

Entry7fca902bac36e30befd657d2bb4e35fa92ec5a5f; exclusive feature branch
feat/bootstrap-cpp20-engine. Protected main remains
12f3a53943dc245e36f2cbbc35b9910fb21c0718. Preserved previous code, source audit,
raw local evidence and history. No new workflows, data acquisition, paid resources,
live orders/brokers, Terminal modification, releases, tags, merges or force pushes.
Every commit uses [skip ci]. Completed all feasible offline engineering; externally
unavailable archival and empirical evidence remains explicitly PARTIAL/BLOCKED.

Implemented bounded initialization manifests, atomic **authored synthetic** seed
import, seeded-prefix restart, independent seeded comparison and bounded source
comparison/refusal/reproduction tools. **No observed-market L3 correctness,
production readiness, security certification or new native ARM qualification.**
Observed seeding and publisher completeness attestation remain unimplemented.

| Phase | Exact pushed closure commit |
|---|---|
|1 ARM64 evidence|`c04ea88840c4ee9b34e4c0c6d08a51402d789f39`|
|2 Initialization contracts|`097dc19aadb131c020bb45136c6a141840ef94c4`|
|3 Seeded reconstruction|`3a5714511cfb87c97606bb2bce7b11d24070b4e3`|
|4 Comparison/evidence closure|`8a80ffcf6f8fc962265bdba6937d2500b7591f9b`|

Phase4 implementation checkpoint:
`b06a41775600fab25531ce12768143b64d1a31e9`.
Evidence follow-up8a80ffc preserves that pushed history: local JUnit output truncation
required additional full seeded-reference receipts before archival closure. There
are five phase checkpoints (Phase4 has implementation + evidence), followed by this
separate report-only commit. No amend/rebase or hidden history rewrite.

Last verified remote feature HEAD before this report commit:
8a80ffcf6f8fc962265bdba6937d2500b7591f9b. Delivery response/private verification
receipt records the subsequent report commit and final remote HEAD. Its own SHA
cannot be embedded literally in itself; resolve with
`git log -1 --format=%H -- docs/OBSERVED_MARKET_ENGINEERING_REPORT.md`.

## Native ARM64 run4: qualified source and evidence limits

Run40135471630 at7fca902; official URL:
https://github.com/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/runs/40135471630

Owner confirms six GCC/Clang Debug/Release/ASan+UBSan jobs passed. Independently
retrieved official public summary confirms exact SHA/feature/Success/six completed
jobs/successful matrix badge/manual trigger/7m52s. Tested workflow declares native
ubuntu-24.04-arm and asserts ARM64/aarch64. No emulation or new run was used here.
Detailed archival PARTIAL: summary lacks individual IDs; job-groups fragment400,
matrix expansion404; raw logs require sign-in and no authorized identity exists.
Job IDs/raw per-job test summaries, compiler/CMake versions, JUnit and packaging
outputs were not independently exported. No repeated denied API/proxy workaround.
Configured workflow requirements are distinguished from retrieved raw outputs.

See [run4 evidence](ARM64_RUN4_EVIDENCE.md) and
[manifest](evidence/arm64_run4_manifest.json). Historical qualifications are retained.
**Run4 qualifies7fca902 only. Subsequent implementation remains pending a separately
owner-authorized hosted run.** Manual/free-usage/feature guards and existing six-job
workflow are unchanged. Main's registration is unchanged.

## Initialization and provenance

[Contract](MARKET_INITIALIZATION_CONTRACT.md),
[provenance](DATASET_PROVENANCE_REQUIREMENTS.md),
[11-method/13-mutation evidence](evidence/initialization_validation.json).
Bounded1MiB JSON validator refuses duplicate keys, invalid identifiers/enums,
negative/zero/overflow quantities, price/priority/boundary/date/digest contradictions,
instrument ambiguity and resource caps. It is pure: invalid manifests cannot mutate
accepted state. Capture ordinal is explicit; missing exchange sequence stays absent.

Complete/seeded eligibility requires complete/no-gap authored input and separately
supplied trusted fixture digests. Unknown/incomplete/corrupt inputs are context-only
or refused. Self-declared completeness is never publisher proof. Observed-origin
claims never obtain a native book. Provider/dataset, rights/retention references,
source/snapshot digests, instruments/date/capture boundaries, initial-state source,
verification method, status, clock/lifecycle and gaps remain explicit.

ModeA observed complete-start and ModeB observed snapshot validation remain blocked
on independent evidence and an observed evidence-verifier/projection implementation.
Authored versions are exercised. ModeC unknown state and ModeD invalid input fail
closed. No empty state is inferred from O/open/time/top quote/file boundary.

## Seeded-state implementation and restrictions

[Implementation](SEEDED_STATE_RECONSTRUCTION.md),
[independent validation](SEEDED_STATE_REFERENCE_VALIDATION.md),
[results](evidence/seeded_reconstruction_results.json).
Factory constructs context and native recovery books privately, exposes a result
only after validation succeeds, and cleans up every failing allocation. Existing
prepared context/native transaction applies subsequent source events. Seed carries
active order identities/side/Price4/remaining/arrival/FIFO rank, exact directory
layout, retired references, match history and continuation boundary. No borrowed
seed storage escapes. Retired IDs have no fabricated side/price/stock history.

At most2 books/64 active orders each; further context/journal/PMR caps apply.
Identity-sorted canonical seed SHA256 is independently encoded in Python; manifest
JSON snapshot hash and raw-source hash are separate. Native provenance adds exact
seed parent/lineage. One derived recovery journal record per book uses sequence0;
subsequent source-native sequences start1, with seed counts separate from source
counts. Historical snapshot liquidity is recovered, not fabricated prior adds/fills.
FIFO ranks preserved; future native priorities use max active rank+1, not an asserted
historical exchange absolute priority counter. Historical execution analytics and
retired absolute priority high-water behavior are not inferred.

Actual PMR failure sweep covers24 failing factory allocation positions before full
success; zero live blocks/bytes after every return. Additional seeded-adapter sweep,
65th-order cap, lifetime/match/identity/unit/clock/boundary checks and journal-cap
rejection preserve context/native agreement. Prefix restart re-creates from trusted
seed + complete framed-prefix hash and rejects corruption/truncation. Canonical
journals reproduce; existing canonical format unchanged. No serialized-journal state
parser, hot snapshot recovery, filesystem durability or crash-safe operations added.
Old empty-start checkpoint API remains scoped; no silent format migration.
Public C++ context/config layouts were extended: rebuild native consumers fully;
no stable binary ABI or safe mixing with old object files is claimed. Python public
API remains unchanged and fresh installed consumers were tested.

Independent flat-book oracle:152 schedules/330 prefixes,seed1397048644,2 fragmentation
schedules and128-order extreme-quantity seed; three intentional quantity/FIFO/
accounting errors are detected. Supplemental digest:
4618d9b3c94d34535001c8f9e6a2a54cfd5708ac72b58116425b0cf0c996d4b1.
Same-session architectural independence is not external certification.

## Bounded comparison readiness and demonstration

[Comparison plan](OBSERVED_MARKET_COMPARISON_PLAN.md),
[real-data gates](REAL_DATA_ACCEPTANCE_CRITERIA.md),
[full evidence](evidence/bounded_comparison_results.json).
Working seeded BinarySourceAdapter path preserves exact input hash/order/receipts,
with deterministic first refusal. CLI bounds bytes/records/events, candidate PMR,
reference state cells, child output/deadline, instruments and stop-first error count.
PMR is not a whole-process RSS/ASan-virtual-memory cap; all other storage is separately
count/size bounded. Fixture-only provider/two-symbol mapping explicit. Unsupported
missing seed clock/stage is refused by the driver protocol rather than invented.

11 demo commands produce expected outcomes: complete/seeded agreement, unknown
initialization blocked, corrupt seed and missing event refused, duplicate/unknown
order and unsupported message refused with accepted-prefix accounting, memory cap,
intentional divergence and its reproduction. First divergence event0/typeE/quantity
field retains a verified one-record authored prefix, full initialization manifest,
original parent/input hashes, expected/actual state and absolute reproduction argv.
It is not globally delta-minimal. Exclusive report writes; observed payload export
and observed replay are refused. Source counts/reasons/unprocessed tail/unsupported/
order/quantity/depth/best metrics are scoped; unknown upstream sequence is null.
Independent algorithm agreement is not independent observed evidence.

Reproduce offline (new output directory):

```sh
python3 scripts/demo_bounded_comparison.py build/phase9-clean-release/gig_itch_l3_reference_driver /tmp/gig-authored-comparison-new
python3 tests/test_market_initialization.py
python3 tests/test_bounded_comparison.py build/phase9-clean-release/gig_itch_l3_reference_driver
```

No market observations, new datasets, archive decompression or network calls occur.

## Exact executed validation

Local x86_64, GCC14.2.0-19,Clang19.1.7,CMake3.31.6,Python3.12.14. Phase3 and final
Phase4 each completed the comprehensive9-configuration matrix; counts are repeated
configuration outcomes, not distinct new test cases. Final Phase4:

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

Total1396/1396;0 failed/skipped/disabled. GCC/Clang and Python ASan+UBSan actually
ran, strict warnings/assertions preserved; no findings suppressed. Allocation,
replay/journal, deterministic and old independent suites retained.

Additional final12-method diagnostic checks across9 current candidates:108/108,
including final missing-clock guard and actual recorded reproduction command.
New seeded reference re-executed in all9 candidates with full receipts: each152/
330 and same supplemental digest. Local JUnit's1024-byte passed-output truncation
is disclosed; direct receipts replace missing output, not failed tests. Existing
hosted workflow larger-output policy remains unchanged.

Fresh checkout/source-archive wheels:28 installed interface/export checks,4 failure
controls,2 identical deterministic research-example outputs;14 build/install/check
steps exit0.379 safe intended archive members (378 source + generated PKG-INFO).
All378 source members additionally compared byte-for-byte with immutable
b06a41775600fab25531ce12768143b64d1a31e9. Final evidence/report documentation follows
that code package; wheel Git metadata can name the precommit baseline/dirty build.
Source-content binding is explicit; no false final-HEAD/bit-identical wheel claim.
Archive SHA256:b17450e942fc7a4d4f4561363d6f9c252ff40c95201e11ab4f42c1c24f6c34ef.
Three packaging-pattern and10 security receipt controls pass. Raw logs/artifacts
remain private under ignored build/observed-program; digests are committed.

Development failures retained, not suppressed: initial seed directory Location /
Error-append convention and indentation warnings repaired before gates. Pre-existing
GCC Debug benchmark object had Ninja deps0 after public type change; preserved stale
object/failure, rebuilt it and scanned all9 directories, final matrix passes. New
reproducer's relative cwd assumption caused3 initial Debug CTest failures; absolute
recorded argv fixed and final matrices/focused checks pass. Evidence exporter first
refused truncated new digest output; full direct receipts collected, evidence added
in a follow-up commit without rewriting pushed code. No unresolved reproduced engine
defect or sanitizer finding remains from these tests. Finite tests are not proof of
arbitrary-input or historical-market correctness.

## Eight preserved canonical SHA256 identities

| Oracle | SHA256 |
|---|---|
|itch.independent_reference|`142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e`|
|itch.context_reference|`58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e`|
|itch.l3_reference|`bb16d4ba9e400ee8f2bc40707de5aa89d0b0955819b4f1f45ca2cdf82cac7991`|
|itch.streaming_reference|`be5d6f5a15fa1dc77560e0a815b8397a605eab369fa66f44df12e5ed9b04a4d5`|
|itch.validation_demo_reference|`4ebdd734b5f11e368be1525f95a93070893ec14e9caafb161583807c88d23520`|
|itch.hy_reference|`ad982777da3595d8fb608755a4986e68a19c3ab2721ec1e1e084f1945f0412af`|
|itch.admin_reference|`87556148fdc43cb7d3c073aa5a5fa9a0b9a6368c15a5182edb72bced17957d03`|
|itch.auction_reference|`76ad62693c22631e4be0842f44029d779211451a395e8538d70450ae7015ebc6`|

All eight match every final configuration; no golden fixture regenerated. New
supplemental digest is separate. Existing earlier context/streaming/admin/HY/auction
coverage remains intact.

## Resource findings

Phase3 Clang Release exploratory factory median225907ns,max683544ns; zero warmups,
shared host and mixed correctness fixtures, not an exchange-latency benchmark.
Factory/state source binding is3a57145. Current seeded adapter correctness run152
processes/330 prefixes: peak tracked PMR615415bytes,max allocations470,child peak
RSS12928KiB (maximum across separate candidates, not aggregate/parent),wall0.550725s.
Timing includes JSON state output. Journal record12232bytes unchanged; two seed
records precede source records. Maximum authored active seed128, not full-market
scalability qualification. Seed/journal/resource caps stop explicitly rather than
silently truncate. No further journal optimization was attempted.

## Remaining blockers, owner actions and next milestone

- Obtain signed-in run4 job/log/JUnit/toolchain/package exports for full archival.
  Current public evidence plus owner confirmation is not fabricated raw evidence.
- Separately authorize a current-source six-job nativeARM run after reviewing local
  receipts and verifying eligible free runner. None launched here;7fca902 remains
  the last native-qualified source.
- Supply authenticated complete observed start/seed and an independently aligned
  observed reference; implement/review the observed evidence verifier/projection.
  Another reconstruction algorithm or aggregate depth alone is insufficient.
- Separately authorize a small private pilot with actual usage/retention/share terms
  and exact byte/decompression/disk/RAM/time/instrument/error limits. Do not request
  the3.5GB archive. Existing Nasdaq sample-use confirmation does not independently
  grant unrestricted redistribution/publication. No data acquired here.
- Provider security remains partial: existing register17 unresolved/2 mitigated/1
  specific non-applicable path; OpenSSL/CPython/Expat/vendor applicability/backport
  evidence remains missing. No residual risk accepted on owner's behalf.
- No operational crash durability/HA, live execution, full-day scalability,
  production trading readiness or institutional certification is established.

Highest-value next engineering milestone: independently verified **observed**
initialization/source-evidence contract and aligned reference, then a separately
approved bounded comparison. Synthetic seed/FIFO/context/native transactions and
refusal paths are now implemented/tested. ARM qualification/security evidence can
advance independently through owner/provider actions. Further unrelated engine
features, large downloads or production deployment are not justified by this report.

## Complete changed-file inventory

Entry7fca902 through code/evidence closure plus report-only readiness overlays:

- `CMakeLists.txt`
- `docs/ARM64_RUN4_EVIDENCE.md`
- `docs/CURRENT_HEAD_ARM64_READINESS.md`
- `docs/DATASET_PROVENANCE_REQUIREMENTS.md`
- `docs/ENGINEERING_READINESS_MATRIX.md`
- `docs/MARKET_INITIALIZATION_CONTRACT.md`
- `docs/NATIVE_ARM64_QUALIFICATION.md`
- `docs/OBSERVED_DATA_ADAPTER.md`
- `docs/OBSERVED_MARKET_COMPARISON_PLAN.md`
- `docs/OBSERVED_MARKET_ENGINEERING_REPORT.md`
- `docs/OVERNIGHT_ENGINEERING_PROGRESS.md`
- `docs/REAL_DATA_ACCEPTANCE_CRITERIA.md`
- `docs/SEEDED_STATE_RECONSTRUCTION.md`
- `docs/SEEDED_STATE_REFERENCE_VALIDATION.md`
- `docs/evidence/arm64_run4_manifest.json`
- `docs/evidence/bounded_comparison_results.json`
- `docs/evidence/initialization_validation.json`
- `docs/evidence/observed_program_source_binding.json`
- `docs/evidence/seeded_reconstruction_results.json`
- `include/gig/itch/context.hpp`
- `include/gig/itch/input_adapter.hpp`
- `include/gig/itch/reconstruction.hpp`
- `include/gig/itch/seed.hpp`
- `scripts/check_adapter_differential.py`
- `scripts/check_initialization_manifest.py`
- `scripts/check_itch_l3_reference.py`
- `scripts/check_seeded_reference.py`
- `scripts/demo_bounded_comparison.py`
- `scripts/run_bounded_comparison.py`
- `src/itch/context.cpp`
- `src/itch/input_adapter.cpp`
- `src/itch/reconstruction.cpp`
- `src/itch/seed.cpp`
- `tests/fixtures/market_seed_manifest.json`
- `tests/itch_l3_reference_driver.cpp`
- `tests/support/itch_seed_checks.hpp`
- `tests/test_bounded_comparison.py`
- `tests/test_itch_reconstruction.cpp`
- `tests/test_market_initialization.py`
