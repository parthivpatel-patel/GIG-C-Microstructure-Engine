# P1I transaction, streaming and restart boundary review

Review baseline: `f3869b2e3c5b0ad4003f974499b78e265d5f820e`,
`feat/bootstrap-cpp20-engine`. This is the I04 source-level review and additional
adversarial investigation, not the later P1J candidate audit. It was performed in a
separate review-agent pass against actual source and executed probes. Agents share
the same environment and repository; this is algorithmic/review-pass separation,
not organizational independence or a clean-machine certification.

No confirmed critical/high correctness defect was reproduced in the paths below.
No production source, existing test or assertion was changed by this review. That
result is scoped to the inspected contracts and executed tests, not exhaustive proof.

## Source-level accepted-state trace

| Boundary / source at baseline | Actual behavior | Why failure does not partly accept an event / limitation |
|---|---|---|
| `src/itch/decoder.cpp:51–68`; `src/itch/context.cpp:74–88,220–235` | Wire payload/location/enum/provenance and cursor/timestamp checks precede preparation. Location addition is protected by decoder overflow checks; rejected input does not advance context. | Decoder uses exact big-endian fields and preserves wire metadata. A prepared token contains proposed state; it has not updated directories, orders, matches or accepted cursors. |
| `src/itch/context.cpp:42–67,237–272`; `include/gig/itch/context.hpp:135–140` | Required vector storage is checked and reserved at construction. Tokens carry owner address, lifetime instance, accepted-generation and validity. Commit validates public tokens; private validated commit is adapter-only. | Moving a token invalidates its source. Wrong-owner, stale-generation and consumed tokens reject before commit. Accepted-generation changes make independently prepared sibling tokens stale. Vector elements have nothrow copy/assignment assertions at lines9–14. |
| `src/itch/reconstruction.cpp:142–182` | Reentrancy/lifetime checks precede held-source identity, configured source cap, context prepare, binding/C-policy admission and token validation. Receipt capacity is pre-reserved and rechecked. | Failed native admission leaves the held source explicitly rejected/pending/unconsidered as appropriate; these diagnostics are separate from accepted semantic state. No skip/missing-order synthesis path exists. |
| `src/itch/reconstruction.cpp:183–199` | Projection and derived-sequence checks precede one native apply. Only after native success are the validated context token, receipt, counts and accepted position committed. | No callback, allocation or input-dependent validation remains after native success. `SourceReceipt` has a nothrow-copy assertion; reserved receipt capacity and private context ownership make the final updates nonfallible in the supported single-threaded contract. |
| `src/replay/replay.cpp:109–143`; `src/book/order_book.cpp:63–114,147–234` | Replay validates identity/order/sequence/event then reserves journal before native mutation. Native add/replace stage level/list/index nodes and reserve real index buckets before transfer; ledger arithmetic is local until success. | Native rejection cannot append a journal record or advance accepted cursors. Continuity errors intentionally set recovery diagnostics. P1G's repaired first-insert bucket admission remains present. Allocator/resource must outlive objects; native resource allocation failures are the standard `bad_alloc`/container-capacity contract. |
| `src/itch/gzip.cpp:23–47,57–123` | PMR zlib callbacks catch allocation exceptions at the C ABI. Gzip-only input, independent header/input/output/ratio caps, fixed one-byte admission, CRC/trailer checks and sticky errors are explicit. | Output accompanying an error is provisional. One overflow-probe byte is not counted/published. Reader output spans remain borrowed until the next feed/destruction; owning-state moves preserve the allocation address. This is not a thread-safe/reentrant standalone inflater contract. |
| `src/itch/binary_file.cpp:17–64` | Exact two-byte BE framing, bounded payload, byte/ordinal/record overflow checks, terminal/trailing detection and explicit EOF versus bounded finish. | At most one complete owned frame is returned at a time. Partial frame bytes remain accounted, not silently treated as a valid record. |
| `src/itch/streaming.cpp:28–77,92–120` | Decompressed read-ahead is bounded owned state. Frame processing uses prepared/native transactions; accepted-frame SHA updates are fixed-storage and bounded by the100,000-frame hard cap. | Late physical CRC failure beyond a requested logical pause is retained as an observed diagnostic/deferred fatal error. It cannot certify publication. A source becomes complete only after declared EOF, verified gzip, terminal framing, exact compressed/raw identities and no error/pause. |
| `src/itch/streaming.cpp:121–151`; `src/itch/restart.cpp:17–109` | Streaming descriptors capture logical accepted prefix/config/code/native state; raw-prefix restart separately rebuilds and compares full source-context/receipts/native descriptors. | Export/canonical allocation can fail explicitly without changing accepted events. Streaming restart is fresh replay from byte0, not gzip seeking or a full-context snapshot loader. Trusted descriptors are integrity checks, not a MAC, signature or publisher authentication. |

## Independently executed adversarial probes

### Logical pauses with late CRC corruption

`python /tmp/gig-p1i-boundary-probe.py` passed **72 scenarios**:

- Independently authored17-record, two-symbol BinaryFile source, raw SHA256
  `4a5635e7fd1d345188da5d346298a15a34ef951e6d5681918debbf585afb8369`.
- Python `struct`/integer framing plus raw-DEFLATE/RFC1952 construction; no market data.
  Record byte builders come from the existing independent Python fixture layer;
  expected native quantities, priorities, ledger and accepted-frame hash are literal
  calculations in the probe, not copied from production output.
- Valid and deliberately CRC-corrupt source, each of18 logical pause boundaries
  (zero through17 committed records), input chunks1 and whole-source, inflater
  output bound65,536 bytes.
- All72 checkpoint/replay comparisons passed. Every valid source published only on
  complete verified EOF. Every corrupt source remained nonpublication-eligible with
  explicit gzip corruption, including pauses before and after native activity.
- Independently expected book1 remaining25, book2 remaining30; book1 active IDs101
  (quantity8, priority0) and103 (quantity17, priority2). Book1 ledger
  `[30,3,2,0,0,17,17,47,22]` in the documented ledger field order.

Probe source SHA256:
`0d5dbc89f0d444f05f1827da1ae4d45d9d6bc1b07a814844f283113b45c6033a`.
The exercised Release driver's SHA256 was
`f93b77dfd0c9668840924d4eaeddee24f1fab921d6dabcd658ee2c7e851a1321`.
The temporary report is `/tmp/gig-p1i-boundary-probe.json`. Initial draft assertions
used an incorrect numeric enum constant; the probe was corrected against the public
`GzipCode::corrupt` declaration before these results. No production defect or repair
was inferred from that test-author error.

### Checkpoint/depth export allocation failures

The C++ probe `/tmp/gig-p1i-query-probe.cpp` links the qualified Release libraries,
uses the independent stored-block fixture, pauses after10 accepted records, captures
literal baseline accepted/native state and injects failure at **every reached query
allocation**:

- **22 checkpoint/canonical allocation sites** and **2 depth-query sites** reached.
- Every injected operation returned `resource_exhausted`; no unexpected exception,
  event reapplication, accepted-position change or source/native divergence occurred.
- The source summary, native canonical state and accepted-frame prefix hash remained
  unchanged after each failure. After disabling the fault, exact checkpoint verification
  succeeded at every site.
- Selected shared-PMR peak **477,631 bytes**; after destruction **zero live bytes
  and zero live blocks**. This narrow two-book prefix is not the maximum candidate
  profile and excludes fixture/test-process allocations outside the PMR.

Compilation/execution used GCC C++20/O2 with `-Wall -Wextra -Wpedantic -Werror`,
`-Iinclude -Itests`, the existing Release `libgig_itch_streaming.a`,
`libgig_itch_reconstruction.a`, `libgig_itch_context.a`, `libgig_itch.a`,
`libgig_microstructure.a`, and `-lz`. No library was rebuilt by this probe.
Source SHA256:
`23965be72ae5f64472b36b1eeee2beab09552a05abfb0f58a5200d7090c773a4`.
Result is `/tmp/gig-p1i-query-probe.json`. Temporary probes are local investigation
artifacts; the final P1I evidence manifest should retain their identities/results or
promote justified scenarios to maintained acceptance checks.

## Remaining profile and output gates

These are limitations/gaps to qualify, not reproduced source defects:

1. **Query/restart coexistence memory:** canonical/depth output, retained original and
   fresh restart state can coexist. Qualify their combined peak against a declared
   shared hard PMR budget; do not extrapolate from base ingestion or enlarge the cap
   silently. The default count maxima do not jointly promise to fit128MiB.
2. **Output allocation:** caller-owned JSON/strings, fixture generation, fixed objects
   and process overhead can be outside the engine PMR. Record the boundary and process
   RSS; a PMR figure alone does not bound the complete research application.
3. **Final P1I exporter:** this review covered existing canonical/checkpoint queries.
   The new versioned exporter needs its own frozen-source identity/schema/negative
   controls and write-failure behavior. Writing stdout is not durable atomic file
   publication; a failed output must not be reused as a valid complete artifact.
4. **Future observed input:** current initialization remains synthetic authored-empty
   only; unsupported message/binding/lifetime/match/journal limits stop explicitly.
   No timestamps, aggregate depth, system-open message or arbitrary archive boundary
   establishes complete initial L3 state. No real-source claim is made here.
5. **Scope of proof:** existing reached-fault/native/sanitizer suites and this source
   review provide bounded evidence. They do not establish all allocation schedules,
   every platform, crash-safe persistence, thread safety, adversarial allocator
   correctness or empirical exchange equivalence. P1J must audit the final candidate
   after P1I's mandatory gates and verified push.
