# Historical ITCH engineering report

**Complete within the bounded offline scope.** Five documented administrative
families added under an explicit v3 profile; default v1 and H/Y v2 preserved.
All local validation gates passed. **Observed L3 and public/production release
remain blocked.** No additional Nasdaq/LOBSTER request or market byte acquisition.

Starting clean feature HEAD: `3ee54cf552c096bc8fe8f46b9237336bcd376473`.
Implementation committed, pushed and remotely verified:
`45e8d7e58e952d5f3a262c58c84167b31746bcb7`.
Branch: `feat/bootstrap-cpp20-engine`. Main preserved at
`165c5038336887116d69160b0d8e5a1a5ef59d16`.
Final documentation delivery SHA is reported with the Git push/remote verification;
a document cannot self-reference the hash of its own containing commit.

## Completed phases and source evidence

1. Read the retained official specification in full relevant message/data-type/
   revision sections, rechecked SHA256 and audited all23 documented families:
   [ITCH50_COMPATIBILITY_MATRIX.md](ITCH50_COMPATIBILITY_MATRIX.md).
2. Implemented only clear, bounded administrative observation semantics for L,V,W,h,N.
   Selection reflects documented certainty and source-accounting value, not an
   unsupported claim about unseen historical message frequencies.
3. Audited actual gzip→framer→decoder→context→native/replay→research boundaries:
   [OBSERVED_L3_READINESS_CONTRACT.md](OBSERVED_L3_READINESS_CONTRACT.md).
4. Reviewed truncation, CRC, fragmentation, resource/record/journal limits, allocation
   failure, read-ahead, source accounting and restart. Existing comprehensive
   controls rerun; no production streaming defect reproduced or speculative repair.
5. Completed9-row compiler/Python/sanitizer matrix, independent oracles, installed
   wheels, source inventory and fresh resource measurements, documented below.
6. Prepared [16KiB next-prefix proposal](NASDAQ_NEXT_PREFIX_PREFLIGHT_PROPOSAL.md)
   offline. No network experiment executed; explicit separate owner approval required.
7. Adversarial review, suspected-boundary dispositions and retained preliminary
   failures: [HISTORICAL_ITCH_STREAMING_REVIEW.md](HISTORICAL_ITCH_STREAMING_REVIEW.md).
   Independent algorithms/negative controls do not imply an external reviewer or
   independent-machine certification.

Official retained PDF:1200722 bytes, SHA256
`45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3`.
It includes2023 revisions, not a separately authenticated frozen2019 document.
All new families remain synthetic-tested, not newly observed-market validated.
The existing350-message S/R/H/Y prefix evidence remains unchanged.

## Exact new interfaces and semantics

`DecodeProfile::administrative_observations_v3` is opt-in and includes v2 H/Y.
Normalized records retain profile/config and `normalization_version=3`.
Existing enum/variant alternatives remain in their previous order; new alternatives
are appended. No package, Python API or research schema version changed.

| Type /typed alternative | Bytes /official contract | Context and integration |
|---|---|---|
| L /`MarketParticipantPosition` |26; MPID4, stock8, primary Y/N, mode N/P/S/R/L, state A/E/W/S/D; §1.2.4 p9–10 |Require exact known stock/locate; preserve MPID/status fields; observation only. Participant state D never deletes an order. |
| V /`MwcbDeclineLevels` |35; three BE uint64 Price(8) fields, scale100000000; §1.2.5.1 p10 |Global locate0 observation; distinct `Price8`, no Price4 cap, float conversion, native ticks or invented cross-level constraint. |
| W /`MwcbStatus` |12; ASCII breached level1/2/3; §1.2.5.2 p10–11 |Global locate0 observation, no fabricated book binding, halt/reset or native sequence. |
| h /`OperationalHalt` |21; stock8, market Q/B/X, action H/T; §1.2.8 p12 |Require mapped stock; preserve venue-specific status, distinct from cross-market H; no book clearing or matching policy. |
| N /`RetailPriceImprovement` |20; stock8, interest B/S/A/N; §1.7 p19–20 |Require mapped stock; observation only, no displayed quantity/order inferred. |

Exact common locate/tracking/48-bit time, owned Alpha bytes, source location and
provenance are preserved. Lengths, enums and printable Alpha are checked before
semantic admission. Unknown/reserved/unimplemented semantics are explicit errors
or preserved documented fields, never a silent omission. Global-locate validity
is contextual; stateless wire decoding retains the raw header.

`SemanticKind` appends participant_position, mwcb_levels, mwcb_status,
operational_halt and retail_interest. No latest-status table, regulatory execution
policy or new order/match history is added. Accepted context preparation/commit
uses reserved storage and allocates zero times. Native mutation classification is
unchanged; observations produce exact source receipts without advancing either
book's journal, revision, FIFO or derived sequence. Global V/W have no native book
index. Configuration equality/restart identity includes the explicit profile.

Current typed support:12 families v1,14 v2,19 v3; all23 lengths recognized.
**K,J,I,O remain unsupported** and stop explicitly. J is a lower-priority clear
collar extension; I needs revision-specific NOII semantics; K has global-symbol
routing and inconsistent price prose/cancellation details; O is a2023 addition,
not an asserted2019 requirement. Separate bounded extensions need their own
independent tests; this assignment does not invent them to maximize feature count.

## Independent validation and failure evidence

The new Python reference imports no production decoder/context and derives expected
results before execution. It uses explicit byte/struct/integer layouts and a
separate lifecycle/directory/clock model:

- **25,233 wire cases**, including all256 values at every post-header byte,
  malformed lengths, old-profile unsupported checks and10000 independent full-width
  uint64 numeric tuples; seed731991. Price8 is never narrowed or rounded.
- **16,960 context candidates across320 sessions**, seed817321. Compare commit
  classification, accepted count, directory/order/match counts, accepted source
  byte offset and normalization version. Exercise unknown/conflicting stocks,
  global locate errors, interleaving, session stages, timestamp policies and
  rejected-event nonadvancement. This is a bounded candidate model, not lossless
  filtering of a real source stream.
- Negative controls deliberately corrupt encoded-wire expectations and accepted
  context counts. Both must disagree with actual results; positive comparisons
  still run independently.
- Native contracts additionally compare typed provenance, no native unit candidates,
  source receipt/accounting, two-book isolation, restart profile identity and
  unknown-initialization rejection.
- Synthetic gzip fixture **23 source records =7 native +16 external**, fragmentation
  sizes1/3/17/65536, pause/replay with changed fragmentation, incomplete-prefix
  publication rejection and exact accepted-prefix hash agreement.
- **3 reached context creation allocation sites**, **0 accepted-observation
  incremental allocations**, **33 reached streaming failure sites**, zero tracked
  live bytes/blocks after owners are destroyed. Counts describe reached fixture
  paths, not proof of every allocation in arbitrary possible inputs.

Preliminary test-only failures were retained: explicit sign conversion rejected
under Werror, then a canonical query executed while an injected allocator was
still armed (first focused run7pass/1fail). Fixed test harness sequencing without
weakening checks: first assert zero observation allocations, then disarm and query
canonical state. Final focused run8/8. No production decoder/streaming defect was
reproduced, no sanitizer finding suppressed and no old assertion disabled.

## Executed compiler/Python matrix

GCC14.2.0, Clang19.1.7, CPython3.12.14; Linux x86_64 managed environment.
Each row configured, built and executed, with exact commands/JUnit/log hashes in
[HISTORICAL_ITCH_ENGINEERING_EVIDENCE.json](HISTORICAL_ITCH_ENGINEERING_EVIDENCE.json).

| Configuration | Passed /total | Failed /skipped /disabled |
|---|---:|---:|
| GCC Debug |139 /139 |0 /0 /0 |
| GCC Release |139 /139 |0 /0 /0 |
| GCC ASan+UBSan |139 /139 |0 /0 /0 |
| Clang Debug |139 /139 |0 /0 /0 |
| Clang Release |139 /139 |0 /0 /0 |
| Clang ASan+UBSan |139 /139 |0 /0 /0 |
| Python Debug |142 /142 |0 /0 /0 |
| Python Release |142 /142 |0 /0 /0 |
| Python ASan+UBSan |143 /143 |0 /0 /0 |

**1,261 final CTest outcomes**, including existing C++/P1E–P1J regressions,
independent replay oracles and Python interfaces; Python sanitizer includes the
existing live leak-control outcome. No hosted CI or independent-machine pass is
inferred. Local CI-summary native/Python positives and wrong-new-hash negatives
also pass; workflow now requires139 native/142 GCC Python Release and seven hashes.

All **six previous canonical identities are unchanged in every row**: P1E wire,
P1F context, P1G L3, P1H streaming, P1I demonstration and H/Y v2. Full hex identities
are pinned per row in the evidence. The new independently versioned v3 hash is:

`87556148fdc43cb7d3c073aa5a5fa9a0b9a6368c15a5182edb72bced17957d03`

## Packaging and artifacts

Three pinned-backend packaging regression cases pass. Complete source archive
inventory passed **278 safe, intended, byte-identical members**, with required
source/header/CMake/Python/schema trees complete, no cache/build files or links.
Compressed archive1203504 bytes, SHA256:

`480b3f39993cba5394204eefd83524998d39b95bf474e0420b772ad0fa102466`

Fresh direct and source-built installed wheels each pass8 interface+6 export cases,
**28 installed unit cases total**, zero failures/skips; module paths are inside
independent consumer environments. Research examples match the existing
`c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9` digest.
Wheels preserve the existing Python research API, not a new ITCH administration API.

Artifacts were built from the verified precommit implementation patch and
then-current documentation, not a claimed pristine final-delivery source archive.
All non-documentation implementation members match commit45e8d7e by file hash;
subsequent reports/progress updates are not retroactively inside those artifacts.
Exact wheel hashes/commands and source member manifest hash are recorded. Private
binaries, wheels, source archives and logs remain ignored under build/historical-itch;
no raw market bytes or public package publication occurred.

## Fresh resource measurements and journal limits

Existing Release measurement tools were executed after the regression/package
runners completed; actual commands, CPU/quota, binary hashes and raw repetitions
are pinned. These are equivalent **baseline_v1 synthetic workloads**, not v3
administration throughput, exchange latency or a performance optimization claim.
The absent `/usr/bin/time` utility prevented an initial measurement command from
launching; standard Python os.wait4/rusage plus monotonic clock then executed both
programs successfully. No utility was downloaded or environment configuration changed.

| Measurement | Actual result |
|---|---|
| New Message /DecodedRecord sizes |48 /304 bytes, matching H/Y checkpoint ABI sizes |
| Profile128, two books |2056 source records,2048 native; remaining127104 per book |
| Profile first-pipeline PMR peak |42,722,343 bytes |
| Query/restart coexistence PMR peak |77,281,358 bytes; zero tracked bytes after destruction |
| Profile wait-accounted peak RSS |76,062,720 bytes; includes process measurement scope |
| Query allocation-failure sites |45 reached |
| Forced16MiB PMR profile |Stops at515 accepted/512 native,12,109,863-byte tracked peak |
| Forced1023 journal slots/book |Stops at2049 accepted/2046 native; next framed record2050, field journal.records |
| Streaming benchmark |264 source records,256 native;2 warmups,5 measured repetitions,17-byte input chunks |
| Streaming PMR /wait-accounted peak RSS |5,250,448 /11,010,048 bytes |
| Streaming finite-sample median throughput |59,914 source records/s; raw median independently recomputed |
| Native journal entry /2048 element bytes |15,944 /32,653,312 bytes |

At100000 journal entries, element storage alone is1,594,400,000 bytes **per book**,
plus context, native orders/levels, receipt vectors, allocator/capacity and query/
recovery coexistence. Source-record and journal caps are independent. Bounded
inflation does not make retained history constant-memory. No journal redesign here.
Separate optimization requires frozen semantic/migration equivalence, independent
failure/recovery oracles, then identical-workload memory and throughput measurement.

The equivalent older P1H GCC32-order/17-byte workload has identical fixture/output
hashes, source/native counts, receipt checksum, PMR peak and journal element size.
Its earlier recorded throughput63630.3 versus current59914 is about5.8% lower in
this finite sample; different shared-host runs and7versus5 repetitions do not
isolate attribution or statistical significance. No improvement/regression SLA,
event-level tails, real gzip-compression throughput or production rate is asserted.

## Observed blockers, next preflight and candidate status

The current reconstructor still requires authored complete synthetic empty history,
matching origin/seed/digest and explicit two-book bindings. Native snapshots do not
restore ITCH directory/retired IDs/matches/cursor state. No observed initialization,
seed importer, observed provenance adapter, complete capture/session proof or
independent observed FIFO/book reference is available. Never infer an empty book
from file start, S:O, early timestamps, directory/status spins, L2 depth or absence
of adds in a prefix. Decode compatibility does not close these gaps.

The next proposal is **one bytes0–16383 GET**,16384 compressed bytes,2162688
maximum decompressed bytes with stricter dynamic128×consumed+65536 guard,
256MiB managed memory,8MiB private output,30s wall time, zero retries/expansion.
Require206, exact range/total16384 length, frozen validator consistency and matching
first4096 digest, then independent format/accounting checks. Test the revised
inspector locally first. Additional message coverage is not guaranteed. This is
**unexecuted and requires separate owner approval**; no additional request is pending.

- Private synthetic evaluation: locally qualified expanded scope.
- Historical decoding: retained-spec synthetic v3; actual observed evidence remains
  only the earlier350-message S/R/H/Y prefix, not these five new families.
- Observed L3: NO-GO pending initialization/provenance/completeness/oracle gates.
- Formal release candidate: RC13 independent-machine, RC16 provider security
  applicability and RC17 hosted CI evidence remain unresolved. No ARM64/other ABI,
  advisory clearance, merge, tag, production readiness or public release claim.

Owner decisions: separately approve any next acquisition envelope; supply/authorize
independent hosted/machine evidence and provider applicability review; authorize a
future observed adapter only after its source-state/oracle prerequisites exist.
No deadline overrides these gates, and no background acquisition continues here.

## Complete changed-file inventory

Implementation milestone: `.github/workflows/ci.yml`, `CMakeLists.txt`,
`include/gig/itch/{decoder,context}.hpp`,
`src/itch/{decoder,context,reconstruction}.cpp`,
`scripts/check_itch_admin_reference.py`, `tests/test_itch_admin.cpp`,
`tests/test_itch_admin_streaming.cpp`.

Documents (under docs/): `ITCH50_COMPATIBILITY_MATRIX.md`,
`OBSERVED_L3_READINESS_CONTRACT.md`, `HISTORICAL_ITCH_STREAMING_REVIEW.md`,
`NASDAQ_NEXT_PREFIX_PREFLIGHT_PROPOSAL.md`, this report,
`HISTORICAL_ITCH_ENGINEERING_EVIDENCE.json`, `OVERNIGHT_ENGINEERING_PROGRESS.md`,
`REPRODUCIBILITY.md`, `RC_OWNER_ACTIONS.md`,
`ITCH_HISTORICAL_COMPATIBILITY_MATRIX.md`.

Institutional audit, remediation history, original observed-prefix evidence,
existing canonical reports, matcher/execution/TCA/journal code, main and GIG Quant
Terminal are preserved. Exact final push/clean-tree verification is in delivery.
