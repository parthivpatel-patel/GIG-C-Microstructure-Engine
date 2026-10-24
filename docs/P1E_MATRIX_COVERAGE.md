# P1E coverage of the P1D proposed acceptance matrix

This is a source-level coverage ledger for the synthetic-only standalone BinaryFile
framer and ITCH decoder. It supplements, and does not rewrite, the historical
[62-case plus 8-gate P1D matrix](REAL_DATA_REPLAY_ACCEPTANCE_MATRIX.md).
A covered component is not an accepted real-data ingestion system. Execution counts,
compiler/configuration results and artifact hashes belong in the P1E validation
report; the presence of a test alone is not evidence it passed.

**Covered** means the row's standalone wire requirement has direct assertions.
**Partial** means some assertions exist but the full original row remains open.
**Core only** means existing engine regression coverage, without ITCH integration.
**Deferred** means no corresponding P1E implementation or validation. No observed-data
gate is passed. These labels deliberately avoid counting mixed rows as completed.

## Evidence routes

- **FR**: [test_binary_file.cpp](../tests/test_binary_file.cpp), CTest
  `itch.framer_basic`, `itch.framer_errors`, `itch.framer_limits`,
  `itch.framer_allocation`, `itch.framer_properties`;
  [binary_file.cpp](../src/itch/binary_file.cpp).
- **DC**: [test_itch_decoder.cpp](../tests/test_itch_decoder.cpp),
  `itch.decoder_contracts`; [decoder.cpp](../src/itch/decoder.cpp),
  [decoder.hpp](../include/gig/itch/decoder.hpp) and
  [wire.hpp](../include/gig/itch/wire.hpp).
- **OR**: [check_itch_reference.py](../scripts/check_itch_reference.py) and
  [itch_reference_driver.cpp](../tests/itch_reference_driver.cpp),
  `itch.independent_reference` and `itch.oracle_negative_control`. Separately authored Python packing/field tables,
  integer decoding and literal framing expectations compare complete canonical
  outputs or exact structured errors. The suite has 10,000 cases: valid/boundary,
  enum sweeps, truncations and 6,564 adversarial arbitrary-byte/mutation cases.
  FR separately has 10,000 positive grammar/chunking cases using an explicit LCG.
- **BK**: [test_book.cpp](../tests/test_book.cpp), existing `book.*` tests.
- **RP**: [test_replay.cpp](../tests/test_replay.cpp), existing `replay.*` tests.
- **EV**: [test_events.cpp](../tests/test_events.cpp), existing `event.*` tests;
  [test_numeric.cpp](../tests/test_numeric.cpp), existing `numeric.*` tests.
- **BM**: [itch_benchmark.cpp](../benchmarks/itch_benchmark.cpp),
  [check_itch_benchmark.py](../scripts/check_itch_benchmark.py),
  `itch.benchmark_correctness`. Independent packed bytes, checksum and fingerprint
  preflight a synthetic A-message framing/decoding workload. This is not book replay.

The registry recognizes 23 retrieved-layout type lengths. Twelve types are decoded:
S/R/A/F/E/C/X/D/U/P/Q/B. H/Y/L/V/W/K/J/h/I/N/O return explicit unsupported-type
errors at their valid lengths. Unknown types and wrong known lengths have distinct
errors. Raw unsigned references and quantities preserve zero: this does not certify
contextual validity or native representability. Existing native positivity requirements
remain unchanged. This is not a certified historical-2019 schema profile.

## BinaryFile and container rows (17)

| ID | Coverage | Evidence and remaining requirement |
|---|---|---|
| F01 | Covered | FR asserts the exact literal16-byte BF-S-O offsets/payload/time1/terminal; OR independently decodes its S/O payload. Framing completeness does not imply valid L3 initialization. |
| F02 | Covered | OR terminal-only case asserts zero records and complete framing; no native state is generated. |
| F03 | Covered | FR empty EOF and one-byte prefix; OR exhaustively cuts its multi-record stream and checks literal errors. |
| F04 | Covered | OR every proper prefix of its 12-type stream checks exact frame/truncation offsets and counts; FR checks partial payload without publication. |
| F05 | Partial | DC/OR reject wrong known lengths, including supported-type shorter/longer payloads; no dedicated 0x0100 known-type frame assertion. |
| F06 | Partial | Bytewise and seeded chunks in FR/OR match canonical results. Exhaustive every interior two-part split for every golden frame and native mapping are not implemented. |
| F07 | Covered | FR admits a full65535-byte opaque payload under its fixed buffer and rejects a stricter configured cap; OR distinguishes unknown-type decoder rejection. No type interpretation belongs to the framer. |
| F08 | Covered | FR duplicate terminal and OR trailing byte assert strict trailing error; no automatic session transition. |
| F09 | Covered | OR cuts exactly after complete frames without terminal and asserts missing-terminal error while retaining parsed-prefix records. |
| F10 | Partial | FR bounded-prefix finish preserves residual bytes, never certifies complete source, and differs from actual EOF. No pipeline budget-stop/source-commit integration exists. |
| F11 | Partial | DC/OR distinguish unknown and known unsupported O at exact offsets. Historical profile selection and reconstruction disposition are deferred. |
| F12 | Partial | FR injects near-maximum byte offset and ordinal with checked failure; no logical native commit or injected reader-count overflow integration. |
| Z01 | Deferred | No gzip implementation/dependency or container roundtrip test. |
| Z02 | Deferred | No gzip header/optional-field validation. |
| Z03 | Deferred | No deflate/CRC/trailer integrity validation. |
| Z04 | Deferred | No decompression-expansion cap implementation. |
| Z05 | Deferred | No gzip member/trailing-container policy implementation. |

## Fields and context rows (12)

| ID | Coverage | Evidence and remaining requirement |
|---|---|---|
| D01 | Partial | DC/OR independently assert all fields/padding of 12 supported types; other 11 have length recognition and explicit rejection, not decoding. |
| D02 | Covered | DC/OR high-bit unsigned64 references, full48-bit timestamps, explicit big-endian packing/decoding and integer boundaries. |
| D03 | Partial | Exhaustive S/A/C/Q enum-byte sweeps, R finite enum cases, printable text validation and case-sensitive registry. Unsupported-type enums and full R appendix classification remain outside scope. |
| D04 | Partial | Exact raw Price(4), declared maximum/max+1 boundaries; no Price(8), native tick conversion, Fraction integration or sum normalization. |
| D05 | Partial | DC/OR preserve raw unsigned zero/max quantities and zero references rather than importing native positivity into wire validity. EV/BK retain native positive-size/nonzero-ID requirements. Whether a decoded zero is contextually admissible, and full-cancel policy, await the projection layer. |
| D06 | Partial | DC/OR preserve 0/1/full48-bit time exactly. No day/date/timezone validation or contextual timestamp policy; source order is not sorted. |
| D07 | Deferred | R fields decode, but no date-scoped directory map, conflict/repeat policy or locate-to-native routing. |
| D08 | Deferred | No session/day lifetime registry or cross-day reuse validation. |
| D09 | Partial | Raw locate and S fields are preserved. No complete S/V/W/K global/symbol context policy; V/W/K unsupported and semantic locate validation is not a context map. |
| D10 | Partial | DC/OR preserve P zero reference, C printable flag, Q zero shares and B match. No native book/tape projection, correction accounting or double-count prevention integration. |
| D11 | Partial | Owned wire provenance and invalid-origin validation; EV preserves existing native metadata regressions. No external manifest bridge, native lineage/token normalization or license/version invention. |
| D12 | Deferred | One pinned retrieved-layout registry; no selectable/certified historical2019-versus-modern profile. |

## State, sequencing and initialization rows (19)

P1E does not call native book/replay APIs. Existing core tests must stay green, but
cannot demonstrate that a future ITCH projection obeys those APIs.

| ID | Coverage | Evidence and remaining requirement |
|---|---|---|
| I01 | Deferred | No initialization manifest or native publication gate for an arbitrary source prefix. |
| I02 | Deferred | Synthetic wire fixtures exist, but no synthetic empty-book initialization/replay integration. |
| I03 | Core only | BK/RP recovery regressions; no observed aggregate-snapshot classifier. |
| I04 | Core only | BK recovery/boundary regressions; no ITCH snapshot adapter fixture. |
| I05 | Core only | RP recovery/multistream and BK recovery validation; no source-boundary recovery bridge. |
| S01 | Deferred | No ITCH lifecycle projection or independent flat-book ledger fixture. |
| S02 | Core only | BK duplicate/unknown order checks; daily retired-ID registry deferred. |
| S03 | Core only | BK cancel/execute/boundary correctness; no wire-to-native reduction transaction. |
| S04 | Core only | BK replacement priority/atomicity regressions; NASDAQ projection policy deferred. |
| S05 | Core only | BK identified execution behavior; no decoded E/C book application. |
| S06 | Core only | BK crossed-book invariants; no real-source intermediate-state handling. |
| S07 | Deferred | Raw P/Q/B fields only; no hidden/cross/break/halt validity-domain integration. |
| Q01 | Core only | RP continuity/gaps tests; wire record ordinal is explicitly not exchange sequence. |
| Q02 | Partial | FR/OR preserve physical frame order independently of timestamp values; contextual native capture policy remains deferred. |
| Q03 | Deferred | No raw-source-to-native projection/disposition map or derived sequence allocation. |
| Q04 | Core only | RP filtering/config tests; no ITCH registry routing or external-scope classifier. |
| Q05 | Core only | RP subevent/batch regressions; no compound source normalization. |
| Q06 | Core only | RP reset/recovery/atomicity regressions; no session transition adapter. |
| Q07 | Deferred | S code decoding does not implement daily lifecycle classification or post-close semantic acceptance. |

## Failure safety, determinism and resources rows (14)

| ID | Coverage | Evidence and remaining requirement |
|---|---|---|
| A01 | Partial | FR real PMR allocation failure at its sole allocation; BK/RP existing allocation regressions remain. No new adapter registry staging/native transaction sites exist. |
| A02 | Partial | Decoder returns owned results without mutating prior results; framer has explicit read state/sticky failure. No native apply/commit-offset/retry bridge. |
| A03 | Deferred | No ingestion report writer or post-native-commit I/O failure/retry test. |
| A04 | Partial | New library boundaries are noexcept structured-result APIs, including framer resource failure. No future ingestion driver exception-injection boundary. |
| R01 | Partial | FR input-byte, payload/buffer, record, offset and ordinal limits. Decompression/journal/live-order/directory joint admission limits deferred. |
| R02 | Partial | FR proves one fixed65535-byte PMR buffer and no incremental feed allocation; decoded records own fixed fields. No full pilot/RSS/oracle/query/export/recovery budget run. |
| R03 | Deferred | No injectable deadline/read timeout or controlled fake-clock budget stop; benchmark timing alone cannot satisfy it. |
| R04 | Partial | FR allocator accounting covers move, release and create failure; sanitizer gates cover new code. Full pipeline recreation/RSS-growth experiment remains deferred. |
| T01 | Partial | FR/OR chunk-independent payloads/offsets/canonical outputs, seeded reproducibility. No semantic source disposition/native-state hash. |
| T02 | Partial | New tests are registered for required toolchain gates; actual final execution/cross-build hashes must be read from the P1E report. No hosted CI/ARM64 claim follows. |
| T03 | Partial | Independent Python wire/framing oracle implemented; no new flat-book or Fraction-based ITCH normalization oracle. |
| T04 | Partial | OR10,000 total explicit expected-output cases include6,564 adversarial payloads; FR10,000 positive grammar cases. This is not the proposed minimum10,000 mutation cases with all P1D seeds/native replay scope. |
| T05 | Covered | OR `--negative-control` accepts the correct baseline and rejects four deliberately wrong expectations: endian, field offset, quantity and row alignment, without changing production code. |
| P01 | Partial | BM independently validates fixture/checksum and positive counts; wall-time repetitions/minimum/median exist. Two warmups, CPU/RSS/raw service samples and complete original protocol are not all implemented. |

## Observed-data gates (8)

| Gate | Coverage | Reason |
|---|---|---|
| O01 Rights/source identity | Deferred | No new permission determination or market acquisition in P1E; prior access/rights reports retain their unresolved qualifications. |
| O02 Artifact/container | Deferred | No acquired market-data artifact, complete archive hash or gzip verification. Synthetic fixture identities do not satisfy this gate. |
| O03 Dated schema/context | Deferred | Actual archive types/enums/date profile remain uninspected; modern registry recognition is insufficient. |
| O04 Initialization | Deferred | No observed empty boundary or complete initial L3 state established. |
| O05 Replay/order oracle | Deferred | No observed ingestion/native projection or observed lifecycle validation. |
| O06 Snapshot reference | Deferred | No independent observed reference snapshots or nonzero eligible comparisons. |
| O07 Accounting/resource | Deferred | No actual permitted bounded run or full source-disposition/resource accounting. |
| O08 Repeatability | Deferred | Synthetic cross-build evidence cannot establish observed-input repeatability. |

## Scope conclusion

All62 synthetic IDs and8 observed gates are enumerated above. The synthetic rows
comprise9 Covered,25 Partial,16 Deferred and12 Core only; all8 observed gates remain
Deferred. These are coverage classifications, not test-result counts. P1E delivers a bounded
wire foundation and independent synthetic checks; it does not complete the broader
P1D replay acceptance program. The next separately authorized work should settle
historical/context profiles, lifecycle initialization, source/native commit accounting
and independent state projection before claiming an observed-market validation pass.
