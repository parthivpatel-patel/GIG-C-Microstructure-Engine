# P1D — bounded memory and streaming replay design

Status: **PROPOSED, NOT IMPLEMENTED/MEASURED IN P1D**. Offline review against
`183ac12d0a4cc5e3587820ecbba19e5cbaf2d03d`, October 22, 2026 (America/New_York).
No storage refactor, decoder, decompressor, adapter, benchmark or source acquisition
is added. Official S1–S3 and source C1–C4 references are cataloged in
[ITCH_50_VALIDATION_DESIGN.md](ITCH_50_VALIDATION_DESIGN.md).

## Reuse and engineering objective

[PHASE_7_METHODOLOGY.md](PHASE_7_METHODOLOGY.md) already defines correctness-gated
Release measurement, PMR versus process memory, raw distributions and shared-host
limitations. [CORRECTNESS_REMEDIATION.md](CORRECTNESS_REMEDIATION.md) records the
15,944-byte JournalEntry finding and a separate benchmark-gated optimization proposal.
This document supplies a bounded *future input harness* design without changing
those engine contracts. [REAL_MARKET_DATA_FEASIBILITY.md](REAL_MARKET_DATA_FEASIBILITY.md)
and [NASDAQ_ITCH_SAMPLE_ASSESSMENT.md](NASDAQ_ITCH_SAMPLE_ASSESSMENT.md) retain source
feasibility history; prior sample-header/range observations are not a P1D market run.

The objective is a declared, reproducible prefix that stops safely before resource
exhaustion, not an arbitrary full-day promise. Streamed input, a retained replay
journal and a retained book have different growth. A streaming reader alone does
not make ReplayEngine constant-memory.

## Existing allocation and capacity facts

| Item | Existing source/evidence | Implication |
|---|---|---|
| Journal default4,096, hard configured maximum100,000 | `include/gig/replay/replay.hpp:14–20`; `src/replay/replay.cpp:45–49,109–115` | Every accepted native event, including observations and native-filtered instruments, remains in a PMR vector |
| Vector doubles capacity up to configured maximum | `src/replay/replay.cpp:109–115` | Allocated capacity may exceed size; reallocation temporarily holds old/new arrays |
| One target book,8 optional additional-instrument rule sets and8 streams | ReplayConfig/C4 | Not a whole-market multi-book router; native filtering is not free storage or arbitrary-symbol routing |
| Book defaults100,000 orders/10,000 levels/10,000 max query depth; hard order cap1,000,000 | `include/gig/book/order_book.hpp:10–13`; `src/book/order_book.cpp:125–129` | Live book/index/buckets also grow; a journal cap is not a live-order bound |
| Nodes/maps/hash indexes use selected PMR and local staged mutation | `src/book/order_book.cpp:12–20,35–110` | Ordinary mutation does not clone the full book, but nodes/buckets/rehash/staging consume memory; average hash lookup is not hard constant time |
| Reset/recovery builds another state before swap | `src/book/order_book.cpp:216–230,233–267` | Peak can include old/new books; real complete initial snapshot max64 orders remains a separate limitation |
| Canonical export allocates an output string; depth export allocates vectors | `src/replay/replay.cpp:228–248`; `src/book/order_book.cpp:302–335` | Query/export peak is additional, not free or already streaming |
| Caller-owned PMR must outlive objects/outputs | `include/gig/memory/tracked_resource.hpp:8–42`; `src/book/order_book.cpp:114–121`; PHASE_2_BOOK.md | Do not return borrowed output backed by a destroyed budget resource |
| Prior measured x86_64 ABI sizes | CORRECTNESS_REMEDIATION.md; prior evidence | JournalEntry15,944 bytes, MarketEvent12,208 bytes; not portable sizeof guarantees or heap-inclusive figures |

Element-size arithmetic, before all other costs:

| Entries/capacity | Journal element bytes | MiB |
|---|---:|---:|
| 4,096 | 65,306,624 | 62.28125 |
| 10,000 | 159,440,000 | 152.05383 |
| 65,536 | 1,044,905,984 | 996.5 |
| 100,000 | 1,594,400,000 | 1,520.53833 |

Growth2,048->4,096 can coexist at97,959,936 element bytes (93.421875MiB).
Growth65,536->100,000 can coexist at2,639,305,984 bytes (about2.458GiB). Memory
allocator overhead/retention and RSS may add more. These are arithmetic estimates
from the prior ABI measurement and current growth code, not fresh measurements.
Measure actual selected build sizeof/capacities before future real-run budgeting.

## Proposed pipeline and ownership

Use one bounded byte source, one incremental decompressor if required, one framer,
one owned decoded/raw record, one normalization decision and at most one pending
native mutation. No vector of all MarketEvents, unbounded pending queue, background
reader, speculative symbol cache or asynchronous callbacks. File/network buffers are
not engine state. The framework must separately account for:

1. Input bytes acquired/read, compressed representation identity and exact ranges.
2. Decompressed bytes and the current BinaryFile prefix/payload.
3. Daily locate/symbol and selected-order lifetime/context registries.
4. Current native journal size/capacity and book/PMR state.
5. Comparator state and output, with bounded diagnostics/fingerprints.

Raw attributes lacking native fields are copied into bounded owned diagnostic/source
envelopes or resolved by immutable source offset; no dangling span into a recycled
buffer. Only synthetic bytes may be fixtures in Git. Permitted observed bytes and
row-bearing diagnostics stay in a private external root with applicable retention.
No new storage service or persistent recovery infrastructure is required for the pilot.

## Proposed initial safety profile — reviewable project choices

**These numbers are proposed local harness limits, not exchange constraints, observed
market requirements, promises of useful coverage or existing API defaults except where
explicitly noted.** They are intended to make the first future run bounded. Change
only by an explicit versioned configuration, never automatically after an overrun.
All counters use checked arithmetic; limits apply before allocations/read expansion.

| Resource | Proposed pilot bound and acceptance rule |
|---|---|
| First format-only acquisition after rights gate | Start4KiB compressed bytes; do not infer that it contains orders; staged expansion only, maximum1MiB compressed in the pilot |
| Compressed read chunk / decompressed work chunk | At most64KiB each; reserve fixed bounded buffers, not an allocation proportional to archive size |
| Decompressed output processed | At most32MiB total per pilot attempt, inclusive of prelude/directory/control bytes |
| One BinaryFile payload | At most65,535 bytes generically; exact known-type length checked early; current S1 longest listed enabled type I is50 bytes |
| Current raw/native work records | One of each; no multi-record normalized batch; raw attributes bounded by validated payload/context |
| Decoded frame budget | At most100,000 complete source frames; prelude and other symbols count too; terminal counted separately |
| Native journal | At most4,096 accepted records in initial pilot (existing default); no exceeding core100,000 ceiling in any profile |
| Native live-order/level proposal for pilot | At most4,096 orders/4,096 levels/query depth<=10; configure explicit BookLimits, not the much larger defaults. Reaching a bound means a recorded stop, not partial state or deletion |
| Generic daily locate keys | At most65,535 nonzero 16-bit keys; scope reset only on valid external session transition; representation also subject to adapter memory bound |
| Target lifetime ledger | At most4,096 admitted references in pilot, including retired IDs; fail before adding beyond bound rather than forgetting uniqueness history |
| Decoder/adapter heap, including registry/diagnostics | At most8MiB tracked owned allocations plus fixed buffers/stack reported separately; slot bounds never override byte budget |
| Engine selected PMR live budget |128MiB; all book/journal/query/staging allocations subject to it; failure is deterministic and atomic. This may stop before an entry-count bound; it is not a guarantee all valid workloads fit |
| Whole unsanitized native-process high-water | At most256MiB for the declared pilot; report build/host and external peak measurement. This limit is independently checked, not inferred from PMR |
| Separate independent oracle | At most128MiB process high-water; if concurrent, report aggregate process-tree peak as well as per-process values, not only native PMR |
| Bounded inspection wall time |30seconds, monotonic, checked between bounded reads/decompression/frame steps; stop_reason=time_budget, not source-malformed. A blocking byte-source read also needs a finite timeout |
| Diagnostic samples | First error plus at most16 bounded subsequent diagnostics in inspection-only mode; no full raw rows in public logs, no unbounded error-string accumulation |

Decompression/registry work can exhaust a budget without a single native event.
Resource-bound fixtures must deliberately hit each byte/count/time boundary. Expected
budget stops are not parser crashes or successful full-file validation. P1D has not
verified that these limits suffice on any real sample; authorize/revise the profile
after synthetic measurements if necessary. Process RSS is an observed high-water
acceptance metric, not a precise per-allocation governor. PMR/adapter budgets are the
inner deterministic governors; an independent process limit may terminate the worker
without graceful report finalization. Such termination cannot count as acceptance.

## Decompression and compressed-range constraints

S3 describes gzip-compressed historical files; S2 defines framing only *after*
decompression. **Q: the detailed gzip container/library contract below requires a
separate RFC1952 and selected-library review before implementation.** S1–S3 do not
specify CRC, ISIZE or member-validation rules. Those statements are proposed engineering
requirements/assumptions to verify, not independently reviewed NASDAQ archive facts.
No decompression library is part of the current engine; this is an unresolved dependency. P: require recognized gzip header/method and checksum/trailer validation
for every fully consumed member, using a vetted bounded incremental library in a
future implementation. Its version/dependency policy must be reviewed then; no library
is installed by this design. Validate header optional fields incrementally with caps;
do not buffer unlimited filename/comment/extra data. Bound total output absolutely:
compression ratio alone is not a safe or scientifically meaningful validity rule.

Handle corrupt header/deflate stream, CRC mismatch, missing trailer, member count and
trailing bytes explicitly. For the initial profile, accept one gzip member; a further
member is unsupported-container-policy until an intentional concatenation policy is
approved. This is a project restriction, not a claim NASDAQ always emits one member.
Do not silently ignore extra members or process them as new empty sessions.

A caller-bounded prefix may stop inside a valid gzip member or BinaryFile frame.
Report compressed/uncompressed positions, residual frame bytes and that CRC/full-gzip
integrity are **not verified**. Do not turn the deliberate stop into a source EOF
error. Actual source EOF with missing trailer or frame bytes is an integrity failure.
Under the gzip contract to be independently confirmed, ISIZE is modulo2^32;
a trailer alone must not be used to establish a full archive's uncompressed size/integrity. A local compressed-prefix hash is not the publisher's whole-file hash.

HTTP Range success does not make an ordinary deflate stream randomly seekable by
message or time. A future acquisition must use byte0 and maintain sequential decoder
state or separately validated checkpoints; arbitrary middle bytes do not restore gzip
or book state. Bind ranges to an immutable representation (validated Content-Range,
consistent entity validator/length, and actual content hashes where available).
ETag is not a cryptographic dataset digest. This is design-only; P1D performs no HEAD,
Range request, new sample download or network configuration change.

## Bounded replay versus retained history

An admissible interval is a predeclared prefix from a proven empty boundary or complete
identified snapshot within current recovery capacity. Initialization/warmup and all
accepted observations consume native journal. Do not count only the scored period.
Choose source/native byte/frame budgets before reading comparison outcomes. Stop at
the last complete accepted message for replay; keep any physical read-ahead/residual
bytes in diagnostics and do not claim they were committed.

Filter raw other-symbol records only through a declared source classification and
normalized stream mapping. Preserve directory/global controls externally and count
all source frames; C4 native filtering still retains journal entries and requires
known instrument rules. No source-aware multi-book router or source-cursor-only native
event exists. Unknown target mutation invalidates continuation. No implicit resequencing
to hide loss or duplicate payload dropping based on equal content/time.

No journal rotation/pruning/checkpointed disk archive exists. Do not call OrderBook
directly to avoid ReplayEngine storage while claiming complete replay provenance.
Do not reset/recover from an aggregate row at chunk boundaries or create a new empty
replay per chunk. If required initial history exceeds the pilot or core capacity,
report resource-blocked feasibility. A separately authorized compact journal or
complete-state streaming bootstrap may later address it with the remediation plan's
benchmark/atomicity/lineage gates; it is not part of this design phase.

A prefix can be valid for its declared scope without completing a session. It may
also contain no eligible book state; zero eligible comparison rows cannot pass a
reconstruction gate. Streamed external record hashes/counts can describe consumed
history without retaining every raw record in memory, but that is not a durable
crash-recovery store and does not remove the current native journal.

## Completeness and failure reporting

Report independent fields, not one overloaded success bit:

- stop_reason: terminal/actual_eof/acquisition_limit/decompressed_limit/frame_limit/
  journal_limit/memory_limit/time_limit/unsupported/error; expected versus observed.
- source_extent: total compressed size if verified, acquired/read ranges, decoded
  source prefix, native committed mapping, unprocessed tail (count may be unknown).
- integrity: gzip_members_verified, container_terminal_observed, terminal followed
  by clean source EOF, full_artifact_hash_verified, publisher_digest_verified.
- validity: framing, identity/units, initial_state, displayed_book, tape, session,
  reference_comparison; unknown is distinct from false and true.
- memory: journal size/capacity/element sizeof, live orders/levels, decoder and context
  bytes, selected PMR live/peak/allocation counts, process high-water and oracle peak.

A budget_stop can leave a valid committed bounded prefix but must set session_complete
false. A terminal marker observed before unverified compressed tail cannot establish
a complete archive. A later CRC contradiction prevents full verified-input claims.
Allocation failure preserves book/cursor/journal/logical context at the last commit;
raw read position may be later. Export/write failure does not roll back a committed
engine event; mark artifact/report incomplete and do not retry by reapplying it.
No crash-durable guarantees are implied by an in-memory atomic mutation (ADR0001).

## Proposed measurable memory/performance acceptance

Correctness and finite resource behavior precede timing. For the pilot, zero budget
overshoot in acquired/decoded/retained counts, zero dangling references, zero unexplained
allocator leaks after owner destruction, and exact failure-atomic state/sequence/context
comparisons are required. Selected PMR/adapter tracked usage must stay within their
configured caps. Unsanitized native/oracle peaks must satisfy the declared pilot
profile or the profile fails and is reviewed; do not silently raise limits. Include
query/canonical peaks, decoder preload, and recovery coexistence in the measurement.

Sanitizer runs use a separately recorded profile: virtual shadow-memory reservation
is not an RSS regression or a reason to disable ASan. Report sanitizer RSS independently;
no timing comparisons to Release. Fault injection must cover real allocation paths
and release ownership safely. A deliberately forced tiny budget is an expected rejection,
not a passed ordinary replay.

For the first correct Release baseline, use a fixed synthetic workload/hash and
identical profile:2 warmups, at least3 complete measured repetitions, positive actual
record/native/comparison counts, identical canonical/counter outputs, zero hidden
failures/skips, and raw wall/CPU/memory samples. Any planned performance canary may
have a60-second per-run local timeout, with an incomplete result on timeout. This is
a bounded-test policy, not a throughput SLA. Record source, compiler flags/version,
CPU/affinity, clocks, output/checksum costs and cache/I/O policy. Separate decoder,
normalizer, native mutation, comparison and end-to-end records/s or bytes/s with the
correct denominators. Nearest-rank p50/p95/p99 and worst-observed wrapper time describe
finite service observations, not exchange/network latency or an arrival process.

**No minimum records/s is defensible before a correct measured ingestion baseline.**
Do not invent an institutional target or claim the synthetic engine baseline predicts
ITCH throughput. Before later optimization, freeze an approved regression budget from
that baseline and host variance; it is an open decision, not a claimed P1D result.
Every performance acceptance also requires exact semantic/oracle equivalence and
resource-cap compliance. No journal optimization is authorized here.
