# First authorized NASDAQ prefix inspection

**October 23, 2026, America/New_York. Overall: INCONCLUSIVE for complete
historical-profile compatibility. The single authorized transport and bounded
format inspection succeeded. No second request, larger range or L3 replay occurred.**

## Verified starting state and procedure

Repository `parthivpatel-patel/GIG-C-Microstructure-Engine`, branch
`feat/bootstrap-cpp20-engine`. Entry local/remote HEAD both
`e1211cc9c996ae43d736e97a72aa5a5fc41c2d43`; working tree clean. Main remote
`165c5038336887116d69160b0d8e5a1a5ef59d16` unchanged. Followed
[NASDAQ_PILOT_PREFLIGHT.md](NASDAQ_PILOT_PREFLIGHT.md) and the user's explicit
one-request authorization. Runtime skill/network guidance checked; normal configured
proxy, CA trust and TLS hostname verification retained. Configured EMI allowlist
and current running observations did not substitute for actual response validation.
No additional HEAD, LOBSTER, checksum-file or directory request was made.

Before the GET,27 local synthetic controls passed: non206 rejection before body
reads, redirects, wrong/duplicate/absent lengths, changed validators, content coding,
chunked transport, exact4096 read boundary, short response, header budget, gzip
CRC/corruption/concatenation/expansion, partial trailers, native synthetic decoding,
allocation cap and slow-work watchdog. TLS/no-redirect and supervisor-to-worker
resource-limit transitions were checked separately. A temporary draft referenced
an unavailable private HTTPSHandler attribute; it was removed and the controls
rerun before any official request. These are temporary inspection tools outside
Git, not additions to the validated engine or its test suite.

The worker's opener has no redirect/retry/auth-retry handler. It uses one GET,
`Range: bytes=0-4095`, `Accept-Encoding: identity`, `If-Match` against the preflight
ETag and connection close. Response metadata must pass before application body
reads:206,one exact Content-Range/Length/ETag,identity/no Content-Encoding,no
Transfer-Encoding or Location. Body calls are at most `min(1024, remaining4096)`;
there is no cap-plus-one read, connection drain or automatic expansion.
The parent owns an anonymous memory-backed descriptor, not a named prefix file.
A one-shot marker prevents rerunning the request tool.

## Actual transport and byte identity

Official URL:
<https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/12302019.NASDAQ_ITCH50.gz>.
Request/inspection started **17:43:26 EDT** (`2026-10-23T21:43:26Z`).

| Property | Actual observation |
|---|---|
| Official GET attempts | **1**, no retries/redirects/follow-up requests |
| HTTP status | **206 Partial Content** |
| Content-Range | **`bytes 0-4095/3524013057`** |
| Content-Length | **4096** |
| Body bytes delivered to bounded reader | **4096** |
| Content-Type | `application/x-gzip` |
| ETag | `"64b3281599bfd51:0"`, matching preflight |
| Last-Modified | `Tue, 31 Dec 2019 05:13:48 GMT`, matching preflight |
| Accept-Ranges | `bytes` |
| Prefix SHA256 | `133d94175e46e156baf6c7284f1fdad7e00f0fd4700bd09ed87a5afc98a700c2` |

Worker and parent independently hash the same bounded extent and agree on count
and digest. This establishes a local prefix identity, not a publisher-authenticated
whole-archive checksum. The approved expected artifact length remains a response
metadata assertion. The preflight's HEAD+Range416 anomaly did not recur for this GET.
HTTP/TLS/header overhead and possible TLS/kernel buffering are outside the
application entity-body counter, as explicitly scoped in the approved preflight;
no claim of an exact encrypted-wire-byte cap is made.

## Gzip and BinaryFile observations

Gzip fixed header is complete,10 bytes: method8 (Deflate),flags0,MTIME0,XFL0,
OS octet0. No optional extra/name/comment/header-CRC fields are indicated.
MTIME0 supplies no compression timestamp; OS0 is a wire field, not proof of the
producer's operating system. No calendar trading date is inferred.

Python's incremental inflater and the unchanged native P1H GzipReader independently
produce **14,267 decompressed bytes** from4096 compressed bytes, SHA256:

`97e045b089ab2037d05c1746aa82766c2826b205cf5141487605995b29a077d4`

Both report an incomplete member, with no observed gzip error. No member trailer,
CRC or ISIZE completion is verified. That is expected at an intentional compressed
prefix cutoff, not evidence that the full archive is corrupt. No unbounded flush
or decompressed-output allocation was used.

Independent byte walking and native P1E framing identify:

- **350 complete frames**, using big-endian two-byte payload lengths.
- **14,257 bytes** occupied by complete frames, followed by **10 residual bytes**
  of an unfinished frame; no terminal marker observed.
- Zero unknown types,zero expected-length mismatches in complete frames.
- All extracted common timestamps are within a nominal24-hour nanosecond day.
  Range11072057543747–11354339842618 nanoseconds since source midnight,
  approximately03:04:32.057543747–03:09:14.339842618. No date,UTC offset,receive
  clock,tracking-number sequence or capture-loss guarantee is inferred.

| ITCH type | Complete frames | Payload length | Actual native stateless outcome |
|---|---:|---:|---|
| S — system event |1 |12 |Decoded |
| R — stock directory |345 |39 |Decoded |
| H — stock trading action |2 |25 |Known length; explicit unsupported-type outcome |
| Y — Reg SHO short-sale price-test indicator |2 |20 |Known length; explicit unsupported-type outcome |
| **Total** |**350** | |**346 decoded,4 explicitly unsupported,0 rejected supported frames** |

No A/F/E/C/X/D/U/P/Q/B records were observed in this prefix. That is an inventory
of this extent, not absence from the archive. Actual S action values,individual
symbols/locates and directory rows are not published in this report.

## Independent accounting check and temporary harness defect

The original one-shot supervisor recorded **BLOCKED** at its final comparison,
`independent.native_mismatch`. That original report is preserved in the evidence;
it is not silently rewritten into a successful execution record.

Its comparison conflated two valid counters: the Python walker reports the end
of complete frames (14257); the native framer consumes all supplied bytes,including
its buffered partial frame (14267). Both independently report10 residual bytes.
No discrepancy exists in decompressed size/hash,complete frame count,type histogram
or residual bytes. Correct relation:

`native consumed14267 = complete-frame bytes14257 + residual bytes10`.

After the descriptor was closed, a **local authored synthetic**12-byte S payload
plus a10-byte partial-frame prefix reproduced exactly this counter distinction:
Python complete boundary14,native consumed24,residual10. Source confirmation is
`src/itch/binary_file.cpp:31–42,56`:feed advances consumption for partial input;
finish separately reports buffered residual bytes. An offline review of already
recorded aggregates passes all eight explicit size/hash/type/count/residual/gzip
checks. No market bytes were fetched again,reparsed or recovered.

This is an inspection-harness comparison defect,not a reproduced native-framer
or archive defect. A future run must use the corrected equation and include the
partial-frame synthetic regression before consuming any new request budget.
Original execution status remains distinct from the reviewed evidence assessment.

## Compatibility with existing interfaces

| Interface | Evidence / limitation |
|---|---|
| P1E BinaryFileFramer |Actual complete-frame counts and residual behavior match independent byte walking. `finish(EndKind::bounded_prefix)` reports residual bytes without inventing a terminal/session boundary. |
| P1E typed decoder |All346 S/R frames pass current typed validation,with `Origin::observed` and explicit official source identity in the temporary native bridge. This does not certify all historical enum/subtype values. |
| P1E H/Y support |`expected_length` recognizes25/20 bytes (`src/itch/decoder.cpp:7–13`); typed variant/switch omits H/Y (`include/gig/itch/decoder.hpp:52`,src/itch/decoder.cpp:104). Four outcomes are Code14,`unsupported_type`,not malformed or silently skipped. Their actual state/reason/action fields have not been semantically validated. |
| P1F context/normalization |Not invoked. No locate map,session completeness,order references or order-lifecycle acceptance claim. H/Y semantic/state handling needs separately reviewed historical contracts. |
| P1G L3 reconstruction |Not invoked. Source/control messages,early timestamps and a byte0 file boundary do not establish a valid empty L3 state. |
| P1H standalone gzip |Native reader agrees with separate Python inflater on exact size/digest and incomplete-member classification under the approved caps. |
| P1H streaming reconstructor |Not invoked; its authored synthetic initialization contract was not bypassed or relabeled observed. |

The actual byte layout is **consistent with ITCH5.0 BinaryFile framing** for the
observed records. MIME/filename/one prefix do not certify the entire2019 historical
profile. The retained specification includes later revisions; unobserved families,
all enum meanings,session/date metadata and source completeness remain unresolved.
Unsupported H/Y support is a deliberate existing scope boundary exposed by real
inventory,not authorization to add or weaken semantics in this assignment.

## Resource enforcement and measurements

| Resource | Approved/enforced bound | Actual observation |
|---|---|---|
| Application compressed body |4096 bytes |4096; close without extra read |
| Decompressed absolute / stricter ratio |32 MiB / at most576 KiB;128×consumed+64 KiB |14267 bytes; neither approached |
| Response-header budget |64 KiB aggregate parser budget |401 bytes including proxy/response status+headers |
| Process memory |Supervisor64 MiB soft address space;one worker192 MiB hard;sum256 MiB |Peak sampled combined RSS29,155,328 bytes |
| External wait-accounted child peak RSS |Measured separately,includes possible pre-exec floor |18,087,936 bytes;supervisor peak10,878,976 bytes |
| Retained private directory output |8 MiB total;file sizes capped;core dumps disabled |104,649 bytes after aggregate review,including temporary tools/native executable and metadata;zero named/raw market files |
| Acquisition+both inspections |30s supervisor deadline;worker15s alarm,5s blocking timeout |0.502s total;Python network+inspection0.416s |
| Raw data retention |At most7 days |Anonymous descriptor closed and processes exited;**zero raw bytes retained after run** |

The sampled RSS is not an exact simultaneous whole-process peak;hard virtual
address-space caps supplied the independent bound. Kernel/TLS buffers and page
cache are not whole-host RAM promises. Preparation,compilation and local synthetic
controls occurred before this30s experiment;postrun accounting review used only
metadata and authored synthetic input. No full synthetic matrix or performance
benchmark was rerun or claimed. Python zlib runtime1.3.2 and native system zlib1.3.1
remain distinct implementation instances; agreement is not a whole-source CRC.

Market bytes never had a named disk path:the worker reads/hashes the compressed
prefix into a parent-owned anonymous descriptor;native inspection reuses that
same memory extent. Decompressed bytes exist only in worker/native process memory.
The descriptor was closed in the supervisor's finally block;no seven-day cleanup
service is promised or required for a retained prefix. Metadata/tools reside
privately outside Git at `/workspace/nasdaq-first-inspection-20261023/`.

## Outcome and recommended next experiment

**Transport PASS;bounded gzip/framing identification PASS;typed decoder coverage
PARTIAL;overall historical/engine compatibility INCONCLUSIVE.** No initial-state,
FIFO,order-lifecycle,real-L3,matching,execution/TCA,empirical correctness or source-
completeness claim follows. Whole-archive hash,CRC and session coverage remain unknown.
No engine implementation,tests,journal or previously validated canonical artifacts
changed. Original synthetic canonical identities remain historical qualified evidence,
not newly rerun test results.

Recommended next approval:an **offline H/Y historical-profile compatibility study**
using the retained official specification and independently authored synthetic
fixtures,including a regression for the temporary counter comparison. Define
explicit typed support/unsupported outcomes and initialization implications before
any observed-market integration. No further market request is necessary to expose
this already confirmed coverage gap. Production implementation or another/larger
prefix requires its own explicit authorization;neither starts here.

Full sanitized aggregate evidence and exact tool/library hashes:
[NASDAQ_FIRST_PREFIX_EVIDENCE.json](NASDAQ_FIRST_PREFIX_EVIDENCE.json).
Only documentation/aggregate metadata is committed. No raw prefix,decompressed
bytes,rows,order identities or source-derived payload fixtures enter Git. Main,
validated P1E–P1J behavior,Terminal and all Git history remain preserved.
