# P1D — proposed real-data replay validation and acceptance matrix

Status: **TEST DESIGN ONLY; NO NEW TESTS EXECUTED OR ADDED**. Baseline
`183ac12d0a4cc5e3587820ecbba19e5cbaf2d03d`, October 22, 2026 (America/New_York).
All rows are future gates, not pass claims. No sample download, adapter, CI change,
C++/Python/test edit, commit or push is authorized by this document.

## Contract ownership and evidence

The source/specification catalog and proposed wire outcomes are in
[ITCH_50_VALIDATION_DESIGN.md](ITCH_50_VALIDATION_DESIGN.md). State/mutation/oracle
requirements are in [L3_RECONSTRUCTION_REQUIREMENTS.md](L3_RECONSTRUCTION_REQUIREMENTS.md).
Resource profiles and performance methodology are in
[MEMORY_STREAMING_DESIGN.md](MEMORY_STREAMING_DESIGN.md). Those documents distinguish
S (official specification), C (existing source), P (proposed policy) and Q (unresolved).
This matrix references their contracts rather than repeating the acquisition/licensing
research in [REAL_MARKET_DATA_FEASIBILITY.md](REAL_MARKET_DATA_FEASIBILITY.md).

Current regression evidence stays historical in
[CORRECTNESS_REMEDIATION.md](CORRECTNESS_REMEDIATION.md) and its
[validation record](baselines/remediation-validation.json). Existing65 native CTest
outcomes per GCC/Clang configuration and68/69 optional Python outcomes are not new
P1D runs or ingestion tests. New proposed groups will change future counts; never
announce a future count as already passed. No hosted CI/ARM64/observed-market pass
is inferred from existing local evidence.

## Required future test/report format

Each case identifies requirement ID, fixture ID/hash and schema/context profile;
expected source/frame offsets, decoded fields and error/stop reason; eligible native
pre/post state; independent oracle identity; actual disposition/counters; and pass,
fail, expected-error, skipped, disabled or unrun outcome. Expected error counts as a
passed negative *test* only when its exact error/invariance assertions execute;
it remains a rejected source record, not an accepted event. Zero-test and zero-eligible
runs cannot satisfy a positive gate. Unresolved profiles must appear blocked/unrun,
not be hidden as passes.

Four distinct positions must be available: physical acquired/read extent, last decoded
complete frame, last committed source/native mapping and last eligible comparison.
Record source offsets and bounded diagnostics, not data-bearing public log dumps.
Unexpected exceptions, crashes, sanitizer findings and time/memory-limit kills fail
the relevant test; a deliberate budget-stop fixture must assert the exact reason.

## A. BinaryFile framing and container cases

| ID | Proposed fixture / trigger | Required expected result and measurable criterion | Independent oracle |
|---|---|---|---|
| F01 | Hand-authored16-byte BF-S-O in wire design | One S at offset0/payload2, time1, terminal offset14; exact counts/fields; framing complete, not automatic L3/session-semantic validity | Hand-counted bytes and literal expected fields |
| F02 | Two-byte terminal only |0 messages, terminal observed; no synthetic instrument/time/order; no populated-replay acceptance | Literal length interpretation |
| F03 | Empty source actual EOF / prefix byte only | Missing terminal at empty boundary / truncated_length expected2 available1; no mutation | Literal byte counts |
| F04 | Valid frame prefix with every payload truncation | At actual EOF, exact expected/available lengths and first offset;0 publication for incomplete record | Exhaustive prefix enumeration independent of decoder |
| F05 | Known type with length L-1,L+1,0x0100 | Deterministic known-length mismatch;0 decoded accepted record; no resync or suffix ignored | S1 endpoint-derived length table |
| F06 | Fragmented input | Every interior split of each golden frame, byte-at-a-time and multi-frame seeded chunk schedules produce identical fields/errors/native mapping | One-shot literal/reference decoder, not production feed function |
| F07 | Length65535 and unknown type | Bounded unsupported outcome; no oversized allocation or loop; resource status distinct if stricter profile cap | Unsigned prefix and declared memory profile |
| F08 | Terminal plus arbitrary bytes or another session | Strict trailing_after_terminal; no automatic new session/empty book | Explicit S2 single-session profile |
| F09 | Valid frames without terminal at actual EOF | Parsed prefix counted; session incomplete; full-session gate fails | S2 terminal requirement |
| F10 | Intentional cutoff mid-prefix/payload / on boundary | budget_stop with residual bytes, not falsely reported source truncation; committed prefix exact | Predeclared acquired extent |
| F11 | Unknown type 0xff / profile-disabled O | Unsupported type/profile at exact offset; strict reconstruction stops; inspection disposition explicit | Independent registry/profile |
| F12 | Counter/offset near UINT64_MAX using injected reader state | Checked overflow before read/allocation/publication, unchanged logical commit | Arbitrary-precision offset addition |
| Z01 | Synthetic valid gzip around golden frames | Full roundtrip and matching terminal/CRC/counts under all selected chunk splits | Independent gzip tool/library plus literal frames |
| Z02 | Invalid header/method/reserved bits; bounded optional fields | Correct container error or local header-budget outcome; no unbounded buffering | Gzip format/library contract selected in future dependency review |
| Z03 | Corrupt deflate, CRC or trailer; actual short EOF | Integrity failure; no complete verified-input claim; prior committed prefix disclosed | Independently produced synthetic corruptions/known plaintext |
| Z04 | High-expansion synthetic member | Exact decompressed cap stop before excess output allocation; no ratio-only validity claim | Known plaintext size and measured allocated bytes |
| Z05 | Concatenated members/trailing bytes | One-member pilot rejects extra member/padding under declared policy; does not silently accept full archive | Container policy and independent byte map |

Z cases depend on selecting/reviewing a vetted decompression dependency in the later
implementation phase. P1D defines expected behavior without claiming a particular
library is installed or implemented. No network fixture or real NASDAQ row is used.

## B. ITCH field and context cases

For every enabled type in the wire design's23-type retrieved-layout registry, require
at least one independently authored valid exact-length payload and per-field boundary
cases. Historical profiles can intentionally exclude later layouts/enum values, with
explicit unsupported-profile results. “Type decoded” must not imply all record semantics
are projected into the engine.

| ID | Fixture / trigger | Required expected result | Independent oracle |
|---|---|---|---|
| D01 | All enabled exact type lengths and payload offsets | Exact raw field values, width and original padding; no extra bytes ignored | Literal field lists, S1 table endpoints, separate Python decoder |
| D02 | BE-values from wire design, high-bit refs >INT64_MAX |16909060 /72623859790382856 /281474976710655 before context rules; unsigned64 IDs preserved | Python int.from_bytes / arbitrary precision |
| D03 | B/S valid, invalid side byte, H versus h, unknown enum/reserved policy | No enum coercion, case folding or assumed reserved-zero rule; structured field/profile error | Explicit spec enum tables and policy |
| D04 | Price(4), Price(8), sub-cent value, source max/max+1, uint64 sums | Exact rational value; wrong scale cannot enter order ticks; off-unit/overflow rejects | Fraction with independent constants |
| D05 | Shares0/max; negative native attempt; full-cancel reduction | Native positive-size mutations reject0; raw zero-share Q remains legitimate observation; X equal remainder follows declared anomaly policy | S1 field semantics versus C1/C3 independently |
| D06 | Timestamp0,1,48-bit max, ties/regressions and day-policy boundary | Raw exact values retained; contextual out-of-day outcome separate; no source sorting or made-up UTC/receive time | Integer calculations and declared day policy |
| D07 | Directory before A; unknown locate; conflicting repeat; symbol mismatch | Correct date-scoped map; unknown/conflict rejects; explicitly identical repeat observation handled by policy | Independent map/literal records |
| D08 | New session/day reuses locate/reference | No state leakage; reuse allowed only after valid declared transition; stale cross-day update rejected | External session manifest and lifecycle model |
| D09 | S/V/W locate0; K locate0 with symbol | No universal non-instrumental assumption from zero; preserve proper global/symbol context; no invented exchange instrument | S1 per-type rules |
| D10 | P reference0/constantB, C printableN/Y, Q shares0, B match reference | Exact external fields; no fake OrderId/aggressor, double-counted tape, zero-sized native print or liquidity restoration | S1 §§1.4–1.5 hand cases |
| D11 | Native missing metadata / long symbols/tokens / parent lists | Honest unavailable values or complete-validation error; no invented license/version, truncation or dropped lineage | C1/C2 plus external manifest |
| D12 | Later enum/layout under2019 versus modern profile | Explicit blocked/profile mismatch; no silent assumption archive uses2023 feature set | Pinned dated registry and spec revision evidence |

## C. State, sequencing and initialization cases

| ID | Fixture / trigger | Required expected result | Independent oracle |
|---|---|---|---|
| I01 | No initial state; first source record is Add or09:30 | Parser may inspect; native replay remains requires_snapshot/unavailable;0 eligible comparisons | Initialization manifest, not inferred depth |
| I02 | Explicit synthetic empty start with complete authored history | Healthy declared prefix; fixture origin synthetic and seed/context exact | Hand-authored state definition |
| I03 | Real initial aggregate-only/bounded snapshot | Current recover unsupported, state/cursors/journal unchanged; no generated IDs/priorities | Existing C3/C4 negative recovery plus independent membership |
| I04 | Complete synthetic snapshot64 orders /65 attempted |64 valid under configured limits/boundaries;65 is capacity error, no truncation/chunked append | Literal IDs/ranks and bounds |
| I05 | Missing/duplicate/regressing snapshot stream boundary or FIFO rank | Exact recovery rejection; no prefix of snapshot installed | C4 boundary rules and separate cursor model |
| S01 | Golden A101,A102,E102,X101,D101,U102->103 | Exact final ID103 qty15@101, FIFO rank2, ledger45in/30out; compare every intermediate state | Lifecycle oracle in L3 requirements |
| S02 | Duplicate live ID, reuse retired same-day ID, unknown cancel/execute | Live collision/core error or future adapter lifetime rejection; no state invention or cursor consumption | Independent daily lifetime set/order list |
| S03 | Partial/full quantities, underflow, price/side mismatch | Positive reductions preserve surviving ranks; full delete removes level; invalid input leaves native state unchanged | Arbitrary-precision orders/aggregates |
| S04 | Lose/retain replacements, old/new collision, increase/decrease, side/price change | Exact core priority eligibility and atomic mutation; NASDAQ projection policy explicit, no opportunistic retain | Core contract plus flat priority list |
| S05 | Non-head identified fill | Actual source order decremented, not FIFO head; surviving queue unchanged | Ordered reference list |
| S06 | Locked/crossed add or replace; conflicting source intermediate | Locked permitted; crossed rejects with invariant preservation; no reordering/matching repair | Independent best-price calculation |
| S07 | Hidden print,cross,break,halt/quote-only/resume | Declared book nonmutation/status validity; unsupported tape/auction semantics not marked complete | S1 semantic examples and separate validity flags |
| Q01 | Native local sequence gap/regression/duplicate/MAX exhaustion | Exact stop before commit; needs_recovery diagnostic can change; book/cursor/journal prefix preserved | Independent integer cursor model |
| Q02 | Equal timestamps/regression with strictly increasing capture ordinal | Source order preserved; capture policy accepts context-valid data without time sorting | Literal record order |
| Q03 | Derived sequence with raw other-symbol/global records between target events | Explicit complete source disposition map, native sequence contiguous, no false raw exchange continuity claim | Full source ordinal->projection map |
| Q04 | Core-filtered known instrument / unconfigured instrument / unknown target type | Known filtering validates/retains/counts; unknown configuration/type fails; no hidden target mutation skip | C4 plus declared registry |
| Q05 | Message subevents count mismatch or rejection after first subevent | C4 prefix semantics reported; no claim entire compound record atomic; first adapter scope disallows compound mutation | Independent (sequence,index,count) model |
| Q06 | Explicit old/new session reset/recovery with pending subevents/gap | Invalid reset fails; valid declared transition switches coherently; gap cannot be cleared by fake empty reset | RestartPlan/cursor model |
| Q07 | End system/market hours followed by deletes/breaks, then end messages | Records after earlier close marker retained/classified; no premature EOF/full-session claim | S1 daily code sequence |

## D. Failure safety, determinism and resource cases

| ID | Fixture / trigger | Required expected result | Independent oracle |
|---|---|---|---|
| A01 | Fail each reached allocation site in add/replace/recovery/journal and new adapter registry staging | Book/cursor/last logical source commit/adapter state preserved; diagnostic differences explained; no leaked owned bytes | Real allocation injection, pre/post canonical plus independent fields |
| A02 | Failure after decode but before native apply; native apply rejection | Decoded/read offsets may advance, committed offsets do not; zero duplicate application on exact-position retry | Explicit stage/commit trace |
| A03 | Report/output I/O failure after engine commit | Run artifact incomplete; engine not rolled back/reapplied to “retry export” | Committed revision/journal and controlled I/O error |
| A04 | Driver/native boundary exception | Structured bounded failure, nonzero failure exit where appropriate; no unexpected exception escapes future integration boundary | Injected exceptions/status capture |
| R01 | Input/decompressed/frame/journal/live-order/registry limits at cap and cap+1 | No count/byte overshoot; exact stop reason at first prohibited admission; no silent context eviction | Declared profile with boundary assertions |
| R02 | Pilot128MiB PMR,8MiB adapter,256MiB native RSS and128MiB oracle profile | Within caps on chosen passing workload; controlled rejection on forced small budget; query/export/recovery peaks included | Tracked allocations and independent process high-water |
| R03 |30s inspection deadline / source read timeout /60s benchmark canary | Finite deterministic status for synthetic fake-clock tests; wall-time termination never a normal-pass claim | Injectable monotonic clock and external watchdog |
| R04 | Repeated same prefix with destruction/recreation | Selected live allocations return to expected baseline; no growing owned state across destroyed runs; PMR lifetime correct | Allocator accounting, sanitizers, process observations |
| T01 | Chunking/seed changes only | Exact decoded/source-disposition/native canonical hashes and counters independent of chunk boundaries | Golden canonical reference |
| T02 | GCC/Clang Debug/Release/ASan+UBSan | Same semantic outputs under each compiler/build;0 failures/errors/disabled/skipped in required groups; no sanitizer findings | Cross-build artifact comparison and JUnit |
| T03 | Independent reference decoder + flat book + Fraction math |0 field/order/FIFO/ledger/depth mismatches on every eligible synthetic step | Independently implemented oracle chain |
| T04 | Seeded grammar and mutation campaign (minimum10,000 bounded cases) | No crash/OOB/unbounded work; expected rejection classes/offsets, deterministic replay of first failure | Fixed seeds1/42/1729, separately specified mutations |
| T05 | Deliberately inject wrong endian/offset/quantity/row alignment into expected-path experiment | Oracle detects the intended mismatch; a trivial always-equal comparator cannot pass | Known counterexample with exact first divergence |
| P01 | Correct Release baseline,2 warmups/3 measured runs | Positive actual counts; identical semantic hashes; raw wall/CPU/memory/service samples; no unverified speedup/minimum throughput claim | Fixed workload, independent preflight and measurement driver |

The negative mutation experiment T05 must use a controlled test double, not modify
protected production source as a “verification step.” Existing allocator-failure sweeps
must remain active; don't substitute a single artificial error flag for new real
allocation paths. ASan/UBSan builds need correct actual toolchain/runtime execution;
ARM64, hosted CI and optional Python gates remain separate evidence when applicable.
No test is added/run by writing this matrix.

## E. Future observed-data acceptance (all currently blocked/unrun)

| Gate | Measurable acceptance criterion | Reason currently outstanding |
|---|---|---|
| O01 Rights/source identity | Applicable private-use/storage/retention terms and exact official source documented; no unauthorized raw distribution | NASDAQ clarification pending; no new bytes in P1D |
| O02 Artifact/container | Exact acquired extent/hash; correct representation; any whole-file/publisher integrity claim actually verified; bounded prefix explicitly incomplete | Actual sample contents beyond prior technical one-byte probe unverified |
| O03 Dated schema/context | All observed types/lengths/enum profiles classified; no unknown state-affecting record in accepted interval; exact units/identity/date policies | Historical profile and archive content not inspected |
| O04 Initialization | Proven empty+complete history or genuine complete L3 snapshot within supported capacity;0 fabricated IDs/queues | Initial state unknown; aggregate references cannot satisfy this |
| O05 Replay/order oracle |0 independent field/state/canonical mismatches on every eligible decoded native step; every failure has exact source reproduction | Adapter/reference decoder and actual permitted run not implemented |
| O06 Snapshot reference | Independently sourced/parsed reference, frozen alignment,100% eligible attempts,0 comparison failures/mismatches at supported available depth; nonzero eligible rows | No independent reference artifact established; internal model agreement is not a source-reference pass |
| O07 Accounting/resource | Exact conservation of dispositions, all exclusions and tail explicit; memory/profile caps satisfied; no hidden truncation or scope reduction | Future harness and permitted bounded run required |
| O08 Repeatability | Identical source/config yields same non-timing outputs in GCC/Clang required builds; exact commands/hashes retained | No actual new ingestion configurations/runs |

Failure of any required scope gate prevents its acceptance. Rights do not block an
authorized synthetic-only implementation phase; they do block acquisition/use claims.
If O06 reference data do not exist, explicitly report differential/model validation
only and leave source-snapshot validation unverified. Never fabricate expected source
snapshots or call zero-reference coverage100%.

## Accounting and completeness contract

For complete decoded frames considered by the semantic classifier, use disjoint
terminal dispositions:

```text
complete_frames_considered = native_committed + external_observation
                          + filtered_other_scope + unsupported
                          + semantic_rejected + deferred_state
```

A rejected native event is semantic_rejected, not also native_committed. A valid raw
observation not projected into native state is external_observation, not silently
accepted as a fully represented native record. Framing-error attempts and incomplete
payload bytes are separate counters, not guessed complete records. Terminal marker
is not an ITCH frame. Count emitted native events separately from raw frames; if later
one-to-many normalization exists, preserve its source mapping and compound status.

At a stop, unprocessed tail can be unknown; total_source_records must then be null/
unavailable unless a distinct inventory pass established it. Prefix counts must not
be mislabeled full-file totals. Any parsed-but-not-classified complete frame belongs
to an explicit deferred count/range, not a hole in the equation. Native filtering
counts and external other-scope counts are distinct.

For an inventoried reference set:

```text
reference_rows = eligible_rows + ineligible_rows
eligible_rows = compared_rows + comparison_failures
compared_rows = exact_rows + mismatch_rows
```

Also publish full-reference coverage, eligible coverage, side/rank/field counts,
first divergence and excluded/tainted ranges with reasons. Unknown/deeper reference
state is not zero. A later diagnostic pass after a failure can collect tainted rows
but cannot include them as eligible matches. Dataset comparison success is exact
integer equality, not float epsilon or a high averaged match rate.

Proposed final run summary includes code/dirty state, spec/profile/config/registry
hashes, synthetic seed or actual-source availability, artifact/parent identities,
rights reference, source extents/positions, all counts/error states, validity domains,
resource profile/actual peaks, first-error reproduction and exit status. Non-data
summaries can be shared only under applicable terms. Raw/mismatch bytes stay external.
No current run-manifest schema is silently extended by this design document.

## Review and implementation order

First authorize a synthetic-only decoder/framer/independent-oracle implementation
checkpoint; implement these groups and preserve all existing core regressions. Next
review state/lifetime/projection semantics and synthetic native integration. Measure
the bounded resource baseline before proposing journal optimization. Only after rights,
source integrity/schema and initialization are established should an observed prefix
be used for validation. Compound execution/tape semantics, larger complete snapshots,
crash recovery, whole-market routing and production operations require separate scope.
P1D stops at these documents; no test edits, CI edits, downloads, commits or pushes.
