# P1D — BinaryFile and ITCH 5.0 validation design

Status: **PROPOSED, NOT IMPLEMENTED OR TESTED**. Offline review, October 22, 2026
(America/New_York), against `183ac12d0a4cc5e3587820ecbba19e5cbaf2d03d` on
`feat/bootstrap-cpp20-engine`. This document specifies a future input boundary; it
adds no parser, adapter, dependency, fixture or test. No market bytes were downloaded
in P1D. Rights clarification and LOBSTER support remain external work, not reasons
to defer synthetic design.

## Relationship to existing work

[REAL_MARKET_DATA_FEASIBILITY.md](REAL_MARKET_DATA_FEASIBILITY.md) already defines
source compatibility, inventory and independent snapshot comparison. Do not duplicate
its source-acquisition plan here. [REAL_MARKET_DATA_ACCESS.md](REAL_MARKET_DATA_ACCESS.md)
and [NASDAQ_ITCH_SAMPLE_ASSESSMENT.md](NASDAQ_ITCH_SAMPLE_ASSESSMENT.md) preserve earlier
access findings; their blocked-network statements describe historical checkpoints.
Later P1C evidence in this conversation established HTTP206 for a one-byte range, not
sample decoding. These four P1D documents are the proposed offline validation contract:

- This document owns wire framing, decoding, provenance and synthetic byte fixtures.
- [L3_RECONSTRUCTION_REQUIREMENTS.md](L3_RECONSTRUCTION_REQUIREMENTS.md) owns state semantics.
- [MEMORY_STREAMING_DESIGN.md](MEMORY_STREAMING_DESIGN.md) owns resource policies.
- [REAL_DATA_REPLAY_ACCEPTANCE_MATRIX.md](REAL_DATA_REPLAY_ACCEPTANCE_MATRIX.md) owns test gates.

## Evidence catalog and claim labels

**S** denotes a retrieved official specification statement; **C** an existing code
contract; **P** a proposed project policy; **Q** an unresolved question. Proposed
limits/error names below are not existing public APIs or exchange requirements.
Specifications were read from retained local copies, without network retrieval in
this phase. SHA256 verifies those copies match the previously recorded documents:

| ID | Official document and exact-byte SHA256 | Relevant sections |
|---|---|---|
| S1 | [Nasdaq TotalView-ITCH 5.0](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf), `45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3` | Architecture p.3; Data Types/System Events pp.4–5; directory pp.5–8; status pp.8–12; orders pp.12–16; trades pp.16–18; NOII/RPII pp.18–20; direct listing p.20; revision log p.22 onward |
| S2 | [BinaryFILE 1.00](https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/binaryfile.pdf), `a1f443400728b3ce44953e9ae263e4846fe6ad68420e7a635829872aefdfff60` | §§1.1–1.2: external session identity, two-byte length, zero-length terminator; revision notes p.2 |
| S3 | [Historical access guide](https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/ITCHFTP.pdf), `77d0c9a5e86866951d99e58e5fda76b54ccf0316f19cbd7428492d459dee8177` | SFTP account access p.1; filename conventions/BinaryFile guidance pp.3–4; official support p.5 |
| C1 | `include/gig/core/numeric.hpp:13–44,117–221`; `src/events/validation.cpp:34–106,180–250` | Strong types, exact units, required/missing metadata, timestamp domains, positive priced quantities |
| C2 | `include/gig/events/contracts.hpp:56–167` | Payloads, missing metadata, source lineage, bounded snapshots |
| C3 | `src/book/order_book.cpp:51–110,144–267`; `include/gig/book/order_book.hpp:10–19` | Mutation, ownership, priorities, crossing/capacity, recovery |
| C4 | `include/gig/replay/replay.hpp:6–43`; `src/replay/replay.cpp:38–60,71–148,150–220` | Initialization, contiguous local sequencing, ordering, prefix commit, reset/recovery, journal |

The S1 revision log starts with April 28, 2023; metadata identifies a 2024-produced
PDF. A file named for 2019 is not certified against every later extension. P: select
and hash a dated schema profile explicitly. The table below describes the retrieved
S1 layout, not an independently established 2019 archive profile. Q: confirm the
historical type/enum revision and actual archive framing before real-data decoding.
No general raw market-data license follows from S2's technical “None known” restrictions.

Q: S1 contains legacy prose as well as typed field tables (for example K's IPO-price
formatting prose). Any conflict must be recorded and reviewed against the selected
historical schema; do not silently substitute ASCII price parsing for the stated
Price(4) binary field. Profiles and tests must record their resolution before use.
Gzip header/trailer/member/ISIZE details are not specified by S1/S2: the memory design
labels that dependency-level contract as pending review rather than a NASDAQ claim.

## Layered proposed architecture

Immutable external bytes -> optional bounded gzip decoder -> incremental BinaryFile
framer -> dated ITCH wire validator -> owned raw envelope -> semantic classifier ->
state eligibility gate -> existing ReplayEngine -> independent comparator/report.
All processing remains single-threaded and in source order. Every arrow has explicit
byte/record counters and a bounded resource policy. Expected snapshots never feed
normalization or book state. Decoder buffers must not outlive borrowed views; either
consume synchronously before buffer reuse or copy into a bounded owned envelope.
No reinterpret_cast to packed C++ structs or borrowed pointers in persisted events.

The raw envelope is a new proposed adapter-level contract, not a change to MarketEvent.
It retains artifact identity, decompressed frame/payload offsets, length, local source
ordinal, type, raw fields including tracking/match/print flags, source timestamp,
external date/session, schema profile and disposition. Keep wire attributes that
have no native field; a native projection is not a lossless raw exchange record.
Compressed offsets and decompressed offsets are separate. A gzip chunk does not have
a one-to-one mapping to an ITCH record; checkpoint information must say what it covers.

## BinaryFile framing state machine (S2; behavior P)

States: `need_length`, `need_payload`, `terminal`, `stopped`. Maintain at most two
prefix bytes and a bounded current payload. Accept input split at any byte; transport
chunk boundaries have no protocol meaning. Use checked 64-bit offset/count increments.

| Condition | Required proposed outcome |
|---|---|
| Two length bytes available | Decode big-endian unsigned length L; payload excludes the two-byte prefix |
| L=0 | Terminal marker, not an ITCH message; no type byte, time or instrument invented |
| L>0, payload incomplete but more input expected | `need_more`; retain partial bytes, no decoded record callback or book effect |
| Complete known-type payload | Validate exact length, fields and context before exposing a semantic record |
| Complete unknown/profile-disabled type | Structured unsupported record; strict mode stops before any engine event; never scan for a familiar type to resynchronize |
| EOF with one prefix byte | `truncated_length`, exact offset, expected2/available1 |
| EOF inside payload | `truncated_payload`, prefix/type if available, expectedL/available count |
| EOF on a frame boundary without terminal | Incomplete session under S2, even when all observed frames parse |
| Bytes after terminal | Strict one-session mode rejects `trailing_after_terminal`; do not guess a concatenated session |
| Known acquisition/output budget cutoff | `bounded_prefix`/`budget_stop`, not a fabricated source-corruption diagnosis; report residual prefix/payload separately |
| Offset/count/resource overflow | Stop with range/resource error before allocation or state commit |

S2 says no protocol maximum is defined. The two-byte unsigned field can nevertheless
encode only0..65535. P: allow at most 65535 current payload bytes under the generic
framer budget; for known types reject wrong lengths as soon as the type is available.
A larger advertised logical length is not representable in this framing. No unchecked
allocation from a size field and no concatenation across files without a new declared
external session. A complete terminal marker proves only framing termination, not
upstream feed completeness or an empty initial book.

Layer clarification for implementation: BinaryFile framing alone checks lengths,
bounds, offsets and termination. Known-type lengths, fields and context in the table
above are decoder/pipeline responsibilities; the reusable framer must not depend on
ITCH message definitions.

The strict finalization API must distinguish actual source EOF, caller-imposed cutoff
and gzip error. Treating every short read as EOF is invalid. A truncated prefix may
be inspected without replay, but must never be marked a complete session.

## Dated type/length registry (derived from S1 field endpoints)

Lengths include the message-type byte and exclude BinaryFile's two length bytes.
For the retrieved S1 layout, length = last field offset + its field width:

| Types | Payload bytes | S1 location | Raw validation versus native support |
|---|---|---|---|
| S | 12 | §1.1 pp.4–5 | System code/locate0; global observation, not a native instrument claim |
| R | 39 | §1.2.1 pp.5–8 | Directory and daily registry input, not an order |
| H / Y / L | 25 / 20 / 26 | §§1.2.2–1.2.4 pp.8–10 | Status/participant fields preserved; reduced native projection only if declared |
| V / W | 35 / 12 | §1.2.5 pp.10–11 | Global circuit-breaker metadata; V uses Price(8), not Price(4) |
| K / J / h | 28 / 35 / 21 | §§1.2.6–1.2.8 pp.11–12 | IPO/collar/venue-halt context; no fabricated liquidity |
| A / F | 36 / 40 | §1.3 pp.12–13 | Displayed add; F's attribution remains external |
| E / C | 31 / 36 | §§1.4.1–1.4.2 pp.14–15 | Execution; C's price/printability require qualified handling |
| X / D / U | 23 / 19 / 35 | §§1.4.3–1.4.5 pp.15–16 | Reduction / full delete / new-reference replacement |
| P / Q / B | 44 / 40 / 19 | §1.5 pp.16–18 | Non-displayed print / cross / break; not arbitrary book changes |
| I / N / O | 50 / 20 / 48 | §§1.6–1.8 pp.18–20 | Imbalance / retail indication / later direct-listing discovery; decoding is not an auction model |

P: reject known types with L±1 and extra suffix bytes; do not silently decode a
shorter known prefix of a changed layout. Registry revisions can explicitly add a
layout. A recognized later type under a historical profile is `unsupported_profile`,
not an invented old message. Never case-fold type bytes (`H` and `h` differ).
Profiles must enumerate allowed enum values/reserved-field policies, with a separate
unsupported-value path for valid later extensions; do not guess all reserved fields
are zero. For example, K's locate is0 while it carries a symbol: locate0 does not
universally mean a record has no instrument-specific content (S1 §1.2.6).

## Field decoding and contextual validation

S1 common prefix: type offset0/width1, locate1/2, tracking3/2, time5/6. Decode unsigned
bytes using checked-width accumulation or equivalent explicit big-endian loads; never
host-endian memcpy, unaligned struct loads or signed-char shifts. Check each field's
[offset,offset+width) against the validated payload before access. Preserve high-bit
values, including 64-bit references above INT64_MAX; native OrderId is nonzero uint64
(C1). P's documented zero reference is an observation field, not a native OrderId.

S1 Price(4) is an integer quantum of1/10000 currency unit, with stated maximum
200000.0000; use exact integer/rational arithmetic. Other fields such as V's Price(8)
have different scales and must not enter the order-price path accidentally. Shares
are source integer shares; one QuantityLots may mean one share under an explicit
rule, not a round lot of100. Positive-quantity native mutations differ from legitimate
zero-valued control/cross fields. Source validity and representability are separate.

Preserve exact eight-byte symbol text/padding in raw records. For a registry key,
remove only specified right-space padding under a documented policy; no case changes,
truncation or replacement of unrecognized characters. Bind daily locate to symbol
and external venue/session; compare redundant symbol fields on A/F/P/status records.
P: identical repeated directory data may be recorded as an idempotent observation;
conflicting intraday locate/symbol binding is a fatal context conflict until an
official revision policy is verified. Unknown locate before an order is not assigned
a synthetic symbol. A fixed-width registry key must never imply issuer continuity
across corporate actions or days.

Tracking number is S1's internal tracking number, not a transport sequence. BinaryFile
has no per-record exchange sequence/session ID in its framing (S2). Preserve record
order and derive a clearly named local ordinal; do not sort time ties/regressions or
claim local contiguity proves no upstream messages were missing. Retain source sequence
only if another verified archive envelope actually supplies it.

S1 says nanoseconds since midnight; the retrieved field wording alone does not supply
a dated timezone/UTC epoch conversion. Q: establish exact venue clock/day conventions,
DST/leap-day treatment and historical date before UTC conversion. P: retain raw48-bit
count; reject structurally unrepresentable widths, and make any [0,86400s) rule an
explicit ordinary-day context policy with an unresolved exceptional-day treatment.
A raw48-bit maximum is a wire-boundary test, not necessarily a valid time of day.

C1 only accepts UTC or `venue_utc_unsynchronized` for a supplied event time. Do not
mislabel arbitrary local-midnight counts as UTC/unsynchronized UTC. Until a justified
conversion exists, leave native event_time unavailable, preserve raw source time and
use capture-ordinal replay. Missing native timestamps are representable (C1); receive
time stays unavailable. Timestamp precision is not synchronization/accuracy evidence.

## Error, output and failure contract (P unless noted)

A wire result reports status (`record`, `need_more`, `terminal`, `error`, `budget_stop`),
input offsets/ordinal, schema profile, deterministic error code/field, expected versus
available lengths and bounded raw diagnostic identity. Error names here are proposed,
not additions to gig::ErrorCode. Malformed, unsupported, context-invalid and resource
errors remain distinct. No exception may escape a future executable/C/Python boundary;
catch only at well-defined owned-resource boundaries and map allocation/I/O failures
without continuing with corrupt state. No unbounded exception/log strings or raw data
in Git. The original input remains immutable.

Physical bytes may already have been read ahead when a record fails; report read
position separately from the last committed source/native position. No callback or
native mutation from an incomplete frame. A valid frame can still be rejected by
context/book validation. Strict replay then stops, preserves the last good state and
marks downstream comparisons invalid. Do not advance native sequence or adapter
identity/lifetime state on rejection. Existing C4 continuity faults can change the
recovery diagnostic; compare that separately from book/cursor/journal invariance.
C4's run commits prefixes, not arbitrary multi-event transactions. First scope should
emit at most one native mutation per source record; no partial compound C projection.

Unknown records can be counted/quarantined in a separately labeled inspection pass,
with raw offsets and an input hash for reproduction. They cannot be silently filtered
out of an accepted reconstruction. Proof that a known record is nonmutating can
support a documented external-only disposition; an unknown type is not such proof.

## Proposed deterministic synthetic byte fixtures

All future repository fixtures must be authored/generated synthetic bytes, labeled
synthetic, with explicit schema/date/session and known expected values. No copied
NASDAQ rows, proprietary data, real market observations or network dependency.
These are test definitions only; no fixtures/tests are added in P1D.

| Fixture | Input definition | Exact expected result |
|---|---|---|
| BF-S-O | `00 0c | 53 | 00 00 | 00 00 | 00 00 00 00 00 01 | 4f | 00 00` (`|` separates fields, not bytes) | 16 total bytes; one S payload12 at frame offset0/payload offset2, locate0/tracking0/time1ns/codeO; terminal marker at offset14; no book order or instrument invented |
| BF-empty | `00 00` | Valid terminated framing with0 ITCH records; not automatically a valid populated research run |
| BF-cut-L | One byte `00`, then actual EOF | `truncated_length` offset0, expected2/available1,0 records |
| BF-cut-S | Prefix12, only11 payload bytes, actual EOF | `truncated_payload`, expected12/available11,0 published records |
| BF-wrong-S | Prefix11 or13 with a complete S-like payload of that advertised length | Known-length mismatch,0 published S records; no resynchronization |
| BE-values | Bytes `01 02 03 04`; eight bytes `01 02 03 04 05 06 07 08`; six `ff` | Unsigned16909060;72623859790382856;281474976710655 respectively, before field/context validation |
| A-golden | Synthetic declared registry locate1->`TEST    `; A fields tracking2/time3/reference72623859790382856/B/shares10/Price(4)1000000 | Raw bytes roundtrip unchanged; projected buy10 shares at USD100 under source quantum, only after an explicitly synthetic valid initial state |
| Profile-extension | O payload48 with valid modern fields under modern versus historical2019 profiles | Modern wire parse; historical unsupported-profile outcome unless that profile is explicitly revised; no auction mutation |

One hand-authored valid payload for every enabled type must test every field offset,
not only type/length. Independent reference encoders use literal field lists and
Python integer/struct operations, not the production decoder's registry/helpers.
Numeric expected values use arbitrary-precision integer/Fraction arithmetic. For
each valid frame, test every single split point and a byte-at-a-time feed, then
multi-record chunk schedules with explicit fixed seeds1/42/1729 (draws in separate
statements). Golden results must be identical across chunk boundaries and compilers.
See the acceptance matrix for truncation/enum/context/fuzz/failure cases and counts.
