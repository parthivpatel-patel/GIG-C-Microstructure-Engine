# P1E synthetic BinaryFile / ITCH 5.0 engineering evidence

P1E is complete as a **synthetic-only, standalone wire foundation**. It does not
establish exchange-data ingestion, valid initial L3 state, exchange-equivalent
matching, production trading readiness, or empirical market validation. No NASDAQ
or LOBSTER sample bytes were acquired. Existing engine, Python, journal, simulation,
TCA and GIG Quant Terminal behavior were not changed.

## Baseline and durable checkpoints

Repository: `parthivpatel-patel/GIG-C-Microstructure-Engine`; branch:
`feat/bootstrap-cpp20-engine`. Initial local HEAD and remote feature HEAD were both
`183ac12d0a4cc5e3587820ecbba19e5cbaf2d03d`. Only the four P1D designs were initially
untracked; no pre-existing code changes were discarded.

The reviewed designs were preserved separately in
`d41a8e82835cf071ee5175fcdfd56ff888fa67e8`. The wire design was clarified to keep
BinaryFile framing independent of ITCH type/field/context checks. No historical
claims were upgraded into validation results.

Implementation, tests and the row-level coverage ledger are committed in
`6ff92dbed431c0c047a3c887ad48be6e48e53126`. Final evidence/reproduction documentation
is a separate subsequent commit; its exact SHA and remote verification are reported
in the delivery response. No rebase, reset, history rewrite, merge, release or
network configuration change was performed. The institutional audit and remediation
reports remain byte-identical to the starting commit.

## Official contracts and explicit interpretation

The retained official specifications were inspected locally; no new source or market
data download was needed. Their exact PDF hashes and URLs are recorded in
[the P1D source ledger](ITCH_50_VALIDATION_DESIGN.md):

- ITCH: `45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3`;
  Data Types and sections 1.1, 1.2.1, 1.3–1.5 govern enabled fields.
- BinaryFile: `a1f443400728b3ce44953e9ae263e4846fe6ad68420e7a635829872aefdfff60`;
  sections 1.1–1.2 govern framing, external session identity and terminator.

The selected layout is the retrieved ITCH 5.0 document whose revision log begins
April 2023; it is **not certification of a 2019 archive profile**. K remains
unsupported because its prose/table price interpretation needs profile resolution.
No UTC/timezone/date or exchange-sequence field is invented.

Unsigned source order references and quantities, including zero, are preserved.
The native engine's positive-ID/size rules are not evidence of an exchange wire
restriction. A final source review removed that conflation from the initial decoder;
zero-preservation regressions and an independently updated oracle verify the result.
Contextual admissibility remains future work. Price(4)'s documented maximum is
2,000,000,000 integer quanta (200,000.0000); larger encodings are rejected, with no
rounding, floating-point conversion or native tick conversion. Zero prices remain
observable raw values. Classification/subtype text is printable-ASCII validated,
not certified against every appendix enumeration.

## Interfaces, ownership and failure behavior

`gig::itch` is a separate CMake static-library alias. It is not linked into the
existing core or Python extension. New production files are limited to:

| File | Responsibility |
|---|---|
| `include/gig/itch/wire.hpp` | Distinct offsets/ordinals, structured errors/results, bounded owned source identity, optional provenance |
| `include/gig/itch/binary_file.hpp` | Configurable framer, pull results, borrowed frame view, explicit EOF/cutoff finish |
| `src/itch/binary_file.cpp` | Checked incremental framing and one bounded allocation |
| `include/gig/itch/decoder.hpp` | Distinct unsigned wire units, 12 typed variants, owned decoded record |
| `src/itch/decoder.cpp` | Exact-length, big-endian, field and enum validation |

`BinaryFileFramer::create(limits, offset, ordinal, memory_resource)` returns a
structured result and catches allocation failure. `feed(span)` emits at most one
record or terminator and returns an explicit consumed count. **Callers must feed
all remaining bytes**, including any bytes after the terminal marker. Otherwise
they have not validated the supplied source extent. No resynchronization or silent
record skipping occurs. An empty feed is incomplete input, not EOF.

A frame's borrowed bytes remain valid until the next nonempty feed or destruction.
Call `decode(frame.payload, frame.location, provenance)` before reusing the buffer;
its successful result owns all fields and provenance. The supplied PMR resource
must outlive the framer. Resource deallocation must obey the standard PMR contract.
The components are single-threaded and do not invoke callbacks or the engine.

`finish(source_eof)` seals the reader and certifies framing completeness only when
an end marker was observed and no error exists. It never certifies L3 validity.
`finish(bounded_prefix)` reports residual bytes and never certifies full-source
completeness, even if a terminal happened to be seen. Finish is idempotent. Feed
failures are sticky; feed after a finished reader returns `already_finished`.
`terminated()` reports marker observation only, separately from complete validation.

Errors identify code, absolute source byte offset, static field name, and expected/
actual values. Missing/truncated EOF, unsupported/unknown types, wrong lengths,
invalid fields, resource/stream/record bounds and counter overflow are distinct.
No incomplete frame is published. Partial reads can advance the read position;
there is no native apply/commit position because no engine integration exists.
Decoder failure returns no partial decoded record and cannot mutate previous output.
All library entry points are noexcept; wire outputs have no dynamic allocation.
Public wire-value constructors are explicit representation wrappers, not validation
factories for arbitrary user-built records: validated output is provided by decode.

## Supported and unsupported message families

| Type | Payload bytes | Owned decoded content |
|---|---:|---|
| S | 12 | System event code |
| R | 39 | Every directory field, including exact padded stock/subtype and ETP values |
| A | 36 | Reference, side, shares, stock, Price(4) |
| F | 40 | A fields plus exact attribution |
| E | 31 | Reference, executed shares, match number |
| C | 36 | E fields plus printable flag and execution Price(4) |
| X | 23 | Reference and cancelled shares |
| D | 19 | Reference |
| U | 35 | Original/new references, shares, Price(4) |
| P | 44 | Raw print fields; no fictional displayed order or aggressor inference |
| Q | 40 | 64-bit cross shares, stock, price, match and cross type |
| B | 19 | Broken match reference; no liquidity restoration |

All preserve locate, tracking number, full unsigned 48-bit nanosecond timestamp,
physical frame/payload offsets and local ordinal. Tracking number and local ordinal
are not claimed to be transport exchange sequences. Optional source identity,
origin, SHA256 and generator seed are copied exactly, not inferred or hash-verified
against an absent external artifact. Unavailable provenance remains absent.

The registry recognizes exact lengths of all 23 types. H/Y/L/V/W/K/J/h/I/N/O produce
`unsupported_type` at valid lengths; unknown bytes produce `unknown_type`. A known
wrong length fails before field reads or unsupported-type handling. Unknown field
extensions are not automatically accepted as a historical profile.

## Independent verification and adversarial evidence

The reference driver exposes canonical test-only decoded output. Independently
written Python `struct.pack`, explicit field-offset tables and `int.from_bytes`
calculations produce expected fields and diagnostics, without importing production
parsers or generated tables. Literal S/O bytes and the 16-byte BinaryFile golden
are independently counted. All accepted fields, exact padding, locations and
provenance are compared, rather than comparing only a checksum.

`itch.independent_reference` passes **10,000 exact-comparison cases** per build:
1,585 regular full-field/time fixtures, 412 framing/truncation cases, 1,024 enum-byte
sweeps, 17 numeric boundaries, 398 malformed/unsupported cases and 6,564 deterministic
adversarial payloads. The latter comprise 5,000 arbitrary payloads and 1,564
bit-mutated valid payloads; accepted mutations receive full-field comparisons and
rejections receive exact first-error comparisons. Request bytes/seeds stayed fixed
when zero-value expectations were corrected from the official field contract.

All nine builds produce canonical SHA256:
`142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e`.

A separate native property group runs **10,000** generated valid frame/chunk schedules
using a fixed LCG, checking every payload byte, position, progress and completion.
`itch.oracle_negative_control` accepts its correct baseline and detects all four
intentional wrong expected-output doubles: endianness, field offset, quantity and
row alignment. Production code is never deliberately damaged for this control.

Native framer tests also cover literal/max65535 payloads, empty/one-byte/truncated
input, intentional cutoff, duplicate/trailing terminal, cap/cap+1 record and stream
admission, offset/ordinal exhaustion, allocation failure, moves and deallocation.
No test assertion is compiled away under NDEBUG.

## Final local validation matrix

Linux x86_64, GCC 14.2.0, Clang 19.1.7 using the system GCC standard library,
CMake 3.31.6 and CPython 3.12.14. Warnings are errors. Sanitizer rows enable both
ASan and UBSan with nonrecovering diagnostics.

| Configuration | Passed | Failed | Skipped/disabled |
|---|---:|---:|---:|
| GCC Debug | 74/74 | 0 | 0 |
| GCC Release | 74/74 | 0 | 0 |
| GCC ASan + UBSan | 74/74 | 0 | 0 |
| Clang Debug | 74/74 | 0 | 0 |
| Clang Release | 74/74 | 0 | 0 |
| Clang ASan + UBSan | 74/74 | 0 | 0 |
| GCC Python Debug | 77/77 | 0 | 0 |
| GCC Python Release | 77/77 | 0 | 0 |
| GCC Python ASan + UBSan | 78/78 | 0 | 0 |

Each native row includes all **65 existing outcomes plus 9 new ITCH outcomes**.
Existing deterministic replay, book, numeric, analytics, simulation, execution,
TCA, benchmark compiler metadata and RNG fixture regressions remain active.
The Python additions are the existing interface, export and schema checks; the
sanitizer row also runs the positive live-LSan control. Its established live-
interpreter harness does not cover late CPython finalization; native sanitizer
checks retain normal leak detection. Clang Python configurations were not run.

The initial matrix found a GCC Release `maybe-uninitialized` warning in temporary
variant construction for P/Q. Direct variant emplacement and explicit assignments
fixed it without warning suppression. The final matrix above was rerun after all
code and oracle-policy changes. There were no final test failures or sanitizer
findings. Earlier development logs are retained separately, not counted as passes.

Fresh private 0.1.1 wheel: installed interface **7/7**, export contracts **6/6**,
and research example passed. A source archive was unpacked and rebuilt offline;
its installed consumer repeated those checks. Installed module paths identify the
separate consumer venv. Source archive contents match the new production-source
hashes. No package was uploaded, no Python API/schema/version was changed, and the
new decoder is deliberately not exposed through Python.

Hosted Actions status is **unverified**: the GitHub API request via `gh api` returned
`Forbidden`. Existing CI automatically builds/registers the new targets and tests,
but inspecting its workflow is not evidence of a hosted successful run. ARM64,
Windows/macOS, other Python versions and real-market validation remain untested.

## Memory, measurement and determinism

The framer object is 256 bytes on the measured GCC x86_64 ABI; Result<DecodedRecord>
is 360 bytes and FrameResult 112 bytes. The framer allocates exactly one configurable
payload buffer at creation, at most
**65,535 bytes**, independent of source length. Its fixed object contains the
2-byte prefix and counters. Feed, EOF, cutoff and error paths allocate nothing;
real PMR failure injection and allocation accounting verify this. The decoder uses
fixed owned records: **304 bytes per DecodedRecord**, 48-byte Message variant and
16-byte Header on both tested x86_64 toolchains. These sizes are not an ABI promise.
A caller retaining all outputs can still grow memory; bounded framing alone does
not bound a future transport, decompressor, output collector or native journal.

Release synthetic measurements were run sequentially from the clean implementation
commit after builds stopped. The workload creates 20,000 A records (760,002 framed
bytes including terminal), exercises 4,093-byte input windows, and performs one
correctness preflight plus seven measured passes. Allocation, framing, decoding
and checksums are inside the timed run; fixture generation is outside it. No LTO
or sanitized timing is used. A separate Python byte construction verifies fixture
fingerprint and expected sum independently. Compiler metadata comes from the
compiler that built the executable.

| Compiler | Median ns/record | Minimum ns/record | Wait-accounted child RSS bytes |
|---|---:|---:|---:|
| GCC 14.2 | 89.5984 | 84.4497 | 10,223,616 |
| Clang 19.1.7 | 66.4378 | 64.8556 | 10,223,616 |

Both produce checksum 20,402,020,000 and fixture FNV-1a64
14,735,029,317,026,867,373. Independent construction of those 760,002 bytes has
SHA256 `31c4c85b45ef83e1435b28dd5f481dd8e4c17d608fb4201d8bf4dee5d227f7c2`.
This SHA identifies independently authored fixture bytes; the executable's emitted
FNV fingerprint is compared to their fingerprint. The 1,000-record benchmark
preflight also passes in every matrix row.

These are whole-run per-record averages on a shared host, not per-event tail
latencies or an exchange/institutional target. No speedup or SLA is asserted.
The benchmark does not satisfy all of P1D P01's future CPU/RSS/raw-service protocol.
The existing measurement worker reports wait-accounted child RSS, which can include
an inherited pre-exec worker memory floor as well as fixture/runtime/allocator costs;
it is not a native-only or engine-only memory measurement. `/usr/bin/time` was
unavailable, so the existing worker was used without adding dependencies. Exact local raw results and executable hashes are
retained under `build/p1e/evidence/`; selected durable results/hashes are in
[P1E_EVIDENCE.json](P1E_EVIDENCE.json).

The existing **15,944-byte journal entry** finding and **100,000-record** limit are
unchanged. At that entry size alone the cap implies 1,594,400,000 bytes (~1.485 GiB),
excluding additional allocation/copy/export overhead. This framer's default
100,000-record admission limit is independently configurable; it does not bypass
native journal capacity or authorize incomplete replay. No journal optimization
or integration was performed.

## Coverage, remaining gates and recommended next phase

[P1E_MATRIX_COVERAGE.md](P1E_MATRIX_COVERAGE.md) enumerates all **62** synthetic rows:
9 covered, 25 partial (their remaining requirements deferred), 16 deferred and
12 existing-core-only. All **8 observed-data gates remain deferred/unverified**.
This is not a claim that all 62 proposed replay requirements pass. The row ledger
separates wire evidence from native integration and full real-data requirements.

The next separately authorized phase should remain synthetic-first: select an
explicit dated profile; build source/session/locate context and dispositions;
specify initialization and retired-reference policy; implement a minimal projection
transaction with distinct decoded/read versus native committed positions; compare
all intermediate states with an independent flat-order/FIFO model. Require zero
field/state mismatches, allocation-failure atomicity and deterministic cross-build
outputs before connecting any observed input. Gzip/decompression limits need a
reviewed dependency and separate corrupt/truncated/container tests.

Market acquisition remains blocked on applicable private-evaluation/cloud/retention/
publication permissions, historical profile evidence, initial-state completeness,
and independent observed reference availability. Support Case #17931099 is external
and does not establish these rights. No market bytes, adapter, native mutation,
broker connectivity, journal refactor or new roadmap phase was added here.

## Complete file inventory and reproduction

P1D checkpoint: the four requested design files only. P1E implementation checkpoint:
CMakeLists.txt; benchmarks/CMakeLists.txt; benchmarks/itch_benchmark.cpp;
include/gig/itch/{wire,binary_file,decoder}.hpp; src/itch/{binary_file,decoder}.cpp;
tests/{test_binary_file,test_itch_decoder,itch_reference_driver}.cpp;
scripts/{check_itch_reference,check_itch_benchmark}.py; docs/P1E_MATRIX_COVERAGE.md.
Final evidence checkpoint: this report, docs/P1E_EVIDENCE.json and the small
P1E/counts addition to docs/REPRODUCIBILITY.md. No existing tests were edited.

Follow [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the established toolchains,
Python sanitizer harness and package commands. The new targeted commands are:

```sh
cmake --preset debug -DGIG_BUILD_PYTHON=OFF
cmake --build --preset debug
ctest --preset debug -R '^itch\.'
python scripts/check_itch_reference.py build/debug/gig_itch_reference_driver
python scripts/check_itch_reference.py build/debug/gig_itch_reference_driver --negative-control
cmake --preset release -DGIG_BUILD_PYTHON=OFF
cmake --build --preset release
python scripts/check_itch_benchmark.py build/release/benchmarks/gig_itch_benchmark
build/release/benchmarks/gig_itch_benchmark 20000 7
```

Repeat the complete suite for each compiler and configuration, not only the
focused command. Sanitizer builds are correctness evidence, not performance baselines.
