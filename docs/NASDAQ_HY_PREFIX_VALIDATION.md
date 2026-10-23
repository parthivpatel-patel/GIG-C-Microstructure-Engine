# Real NASDAQ H/Y prefix compatibility validation

**2026-10-23T23:07:38Z. PASS for the complete messages in this one authorized
4 KiB prefix; INCONCLUSIVE for full historical-feed/session compatibility.**
No real-market L3 reconstruction or initial-state inference was attempted.

## Baseline and authorization

Repository `parthivpatel-patel/GIG-C-Microstructure-Engine`, branch
`feat/bootstrap-cpp20-engine`; entry local/remote HEAD
`20e07ec89987368c121eae657e21060aea7dc0b9`, clean. Main remote remains
`165c5038336887116d69160b0d8e5a1a5ef59d16`.
Reviewed [preflight](NASDAQ_PILOT_PREFLIGHT.md),
[first inspection](NASDAQ_FIRST_PREFIX_INSPECTION.md),
[H/Y contracts](HY_HISTORICAL_COMPATIBILITY.md) and
[prior validation evidence](HY_VALIDATION_EVIDENCE.json).
Cloud runtime/network guidance followed; inherited proxy, certificate validation
and TLS hostname checks preserved. No HEAD, directory listing, LOBSTER request,
checksum request, retry, redirect or automatic range expansion occurred.

The existing default `DecodeProfile::baseline_v1` and explicitly selected
`DecodeProfile::status_observations_v2` were invoked on each complete frame.
All validated source hashes still match the H/Y checkpoint. No C++/Python engine,
test, CMake, package, journal or canonical expectation was modified.

## Exactly one transport request

Official URL:
<https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/12302019.NASDAQ_ITCH50.gz>.

Request: GET, `Range: bytes=0-4095`, `Accept-Encoding: identity`,
`If-Match: "64b3281599bfd51:0"`, connection close.
A private exclusive one-shot marker prevents re-executing this request budget.
The reader validates metadata before any application response-body read, then
uses `read1(min(1024, remaining4096))`. It never probes a4097th byte, drains the
connection or follows an inadmissible response. It rejects non206, wrong/duplicate/
missing lengths or validators, Content-Encoding transformations, Transfer-Encoding
and Location. Request/inspection used a30s external watchdog and supervisor deadline,
with a15s worker alarm and5s blocking timeout.

| Observation | Actual result |
|---|---|
| Official GET attempts |**1** |
| HTTP status |**206 Partial Content** |
| Content-Range |**`bytes 0-4095/3524013057`** |
| Content-Length / bytes delivered to reader |**4096 /4096** |
| ETag |`"64b3281599bfd51:0"`, matching frozen preflight |
| Last-Modified |`Tue, 31 Dec 2019 05:13:48 GMT` |
| MIME / Accept-Ranges |`application/x-gzip` /`bytes` |
| Header bytes counted, including proxy/response status |401 |

Compressed-prefix SHA256 exactly matches both the authorized identity and the
previous inspection:

`133d94175e46e156baf6c7284f1fdad7e00f0fd4700bd09ed87a5afc98a700c2`

Worker and supervisor independently hashed the bounded extent. This is a local
prefix identity, not a publisher-authenticated archive checksum. The entity-body
cap excludes HTTP/TLS overhead and unsolicited kernel/TLS buffering; no exact
wire-byte ceiling or full-source integrity claim is made.

## Gzip and frame accounting

Python zlib and the existing native `GzipReader` independently produced
**14,267 decompressed bytes**, SHA256:

`97e045b089ab2037d05c1746aa82766c2826b205cf5141487605995b29a077d4`

Gzip header:10 bytes, magic/method valid, Deflate8, flags0, MTIME0, XFL0, OS octet0;
no optional fields indicated. MTIME0 supplies no calendar time. Both inflaters
report an unfinished member, zero observed gzip errors and **no trailer/CRC/ISIZE
verification**. That is an expected prefix limitation, not evidence of corruption.

Independent Python byte walking and native BinaryFile framing agree:
**350 complete frames**,14,257 complete-frame bytes,10 buffered residual bytes,
no terminal marker, no unknown type or expected-length mismatch.
The corrected comparison is:

`native consumed14267 = complete-frame boundary14257 + residual10`.

The earlier supervisor counter defect is not rewritten: its original evidence
remains preserved. A local authored partial-frame control verified this exact
counter distinction before the new GET. The new supervisor's comparison passes.

| Type | Complete frames | Payload bytes | Default v1 | Opt-in v2 |
|---|---:|---:|---|---|
| S |1 |12 |Decoded |Decoded |
| R |345 |39 |Decoded |Decoded |
| H |2 |25 |Explicit unsupported |Decoded |
| Y |2 |20 |Explicit unsupported |Decoded |
| **Total** |**350** | |**346 decoded,4 unsupported,0 rejected** |**350 decoded,0 unsupported,0 rejected** |

All counts, decompressed size/digest and residual bytes also match the previous
inspection's retained aggregate evidence. Source capture ordering is preserved;
raw wire timestamps range11072057543747–11354339842618 ns since source midnight,
with zero timestamp regressions in this extent. No date, UTC offset, receive clock,
exchange sequence or tracking-number uniqueness is invented.

## Independent field and association validation

A separate Python `struct`/byte parser was authored from documented field layouts,
without importing production decoder code or expected results. It independently
checks lengths/enums/Alpha policy and reconstructs each typed S/R/H/Y payload.
The native bridge separately re-encodes every field from production decoded
structs, including common locate/tracking/48-bit timestamp, all directory fields,
exact padded stock bytes and all H/Y fields. Ordered comparison entries contain
big-endian uint64 ordinal, uint64 physical frame offset, uint16 payload length,
and re-encoded payload. Both implementations hash their own ordered entries.
This checks field values and ordering without retaining or publishing symbol rows.

| Ordered field digest | Independent and native SHA256 |
|---|---|
| Default successful records |`55b38913085e76591784a5d1ef1896f4f7ecb05249c8ae6b02b594908761e7c0` |
| All v2 successful records |`5bd16117bcfcacc6aef11384a9fa8e151a17f421863075f5f6fb43867b3a22ac` |
| H/Y records only |`275ccae33e6e684d3deb1761dd6be06245deb71a0bc7eac9dbb052e9ab72fdfe` |

Observed H states: **T2**. Reserved octet: **ASCII space32, twice**.
Reasons: **four spaces in both H messages**. Observed Y action: **ASCII0, twice**.
These are aggregate field observations, not a claim that all enum/reason values
occurred or that every security was trading/unrestricted. No per-symbol rows,
identifiers or source payloads are committed.

Both parsers independently build a temporary locate-to-eight-byte-symbol map in
capture order. All **four H/Y associations match already observed directories**;
345 directory locates, zero duplicate locates, zero association failures.
Native decoded provenance/location checks also report zero mismatches: origin
remains observed, official source identity and prefix digest are retained, and no
synthetic generator seed is assigned. Typed roundtrip mismatches:zero.

For each profile, `decoded + unsupported + rejected =350`. This is wire-source
accounting. **SourceContext was not admitted or committed; no context cursor,
reconstruction receipt, native journal or native sequence claim follows.**
Temporary directory lookups do not establish full context/session validity.

## L3 isolation and publication restrictions

The observed native bridge invokes only bounded gzip, framing, stateless decode
and hashing; it instantiates **no SourceContext, order book or reconstructor**.
Consequently no observed message mutates any native L3 state. It never invokes the
synthetic initialization factory or labels observed bytes synthetic.

Separately, all **9 applicable synthetic H/Y CTest outcomes** passed before the
GET. These cover two-book/journal/FIFO/sequence isolation, unknown-initialization
rejection, incomplete-prefix publication rejection, provenance, restart-profile
identity, allocation failures and independent-oracle negative controls.
That is synthetic regression evidence, not an observed L3 state-transition test.
Source hashes and prior canonical evidence remain unchanged; the completed1,189-
outcome matrix was not rerun or presented as a new result.

## Safety and resource evidence

Before any GET, **35 local safety controls passed**, zero failures. They cover
pre-body status/metadata rejection, exact read boundary, short/duplicate/oversized
headers, gzip CRC/corruption/truncation/concatenation/expansion controls, memory and
time limits, independent authored S/R/H/Y fixtures, wrong expected-field hash,
wrong symbol association, TLS/no-redirect policy and partial-frame accounting.
An initial preparation command lacked ctest on PATH; the explicit pinned tool
path resolved it and all9 focused tests passed before the request.

| Resource | Enforced bound | Actual observation |
|---|---|---|
| Compressed entity body |4096 bytes |4096 |
| Decompressed output |589824 bytes (576 KiB), plus128×consumed+65536 guard |14267 |
| Managed memory |64MiB supervisor soft address-space cap plus one192MiB hard-capped child; RSS watchdog at256MiB |Peak sampled combined RSS29,298,688 bytes |
| Worker measured peak RSS |Within child cap |18,087,936 bytes |
| Supervisor measured peak RSS |Within supervisor cap |11,010,048 bytes |
| Wait-accounted child peak RSS |Separate measurement |18,219,008 bytes |
| Acquisition and both inspections |30s wall deadline |0.537s (worker0.439s) |
| Retained private output |8MiB, individual output-file cap1MiB, core dumps disabled |148,717 bytes after result writing |
| Raw market-data retention |At most7 days |**Zero retained after run** |

RSS polling is not an exact simultaneous peak. Virtual-address limits enforce an
independent process bound; kernel/TLS buffers and host page cache are not included
in a whole-host guarantee. Compilation/local controls precede the30s acquisition
window; subsequent reporting uses only sanitized aggregates and source code.
Raw compressed bytes existed only in a parent-owned anonymous memfd; decompressed
bytes existed only in worker/native memory. The descriptor was closed and children
exited before this report. No raw cleanup job or seven-day future execution is needed.
Private metadata/tools remain outside Git at
`/workspace/nasdaq-hy-inspection-20261023/`.

## Defects, limits and next step

**No actual decoder defect was reproduced in the350 complete observed messages.**
Default H/Y unsupported results are intentional profile behavior. The earlier
counter-comparison defect is fixed in the temporary supervisor and independently
regression-tested; no engine repair is necessary. No protected code changed.

This prefix does not test observed H:H/P/Q, nonblank reasons, non-space reserved
values or Y:1/2. Synthetic tests remain the evidence for those supported branches.
Nine other known ITCH families remain unsupported. No order messages occur in this
extent; no conclusion about their presence elsewhere or historical compatibility
follows. Full archive integrity, gzip completion, remaining format/type coverage,
authenticated trading date, complete session, valid initial L3 state and empirical
reconstruction/reference-book correctness are all unverified.

Recommended next experiment: first complete a **separate resource preflight** for
one modestly larger byte-zero prefix (for example16KiB), followed by explicit
owner approval of its exact range and new limits. Keep it format/type inventory
only, stop on unsupported semantics, retain no rows and make no L3 claim. A larger
prefix is not guaranteed to expose new message families. This4KiB authorization
is consumed; no further request, range growth or implementation begins here.

Detailed aggregate observations, exact tool/source hashes and commands:
[NASDAQ_HY_PREFIX_VALIDATION_EVIDENCE.json](NASDAQ_HY_PREFIX_VALIDATION_EVIDENCE.json).
