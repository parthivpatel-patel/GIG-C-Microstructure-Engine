# P1H bounded synthetic gzip streaming validation

Status: **P1H local acceptance complete; final evidence push/remote verification
pending**. Starting local/remote feature HEAD:
`c3c3d8caef8f5b60aa4ce29f0f0875dc3bdd91c4`; main remains
`165c5038336887116d69160b0d8e5a1a5ef59d16`. Interrupted untracked work was inspected
and preserved; completed P1G validation was not rerun before resuming development.

This is synthetic-only engineering. No NASDAQ/LOBSTER archive bytes were acquired,
no real-market snapshot comparison occurred, and no production/live/release claim
is made. Matcher, execution, TCA and journal behavior were not modified.

## Interfaces and dependency

The optional `gig::itch_streaming` library links the existing reconstruction layer
and system zlib. `GIG_BUILD_ITCH_STREAMING` defaults OFF; native validation presets
and all nine qualified build trees enable it explicitly. Ordinary wheels leave it
OFF; the installed Python extension has no libz linkage or new API/schema/version.
The existing CI workflow installs the native development dependency before enabling
those presets. Workflow changes are not evidence of hosted success.

- `GzipReader`: stable PMR-owned inflater/buffer, gzip-only single-member policy,
  checked independent input/output/header/ratio/slack limits, explicit consumed
  bytes, provisional output and sticky errors, EOF versus bounded finish.
- `StreamingReconstructor`: incremental gzip→BinaryFile→typed decode/context→L3,
  exact full compressed/raw identity checks, per-stage accounting and publication
  gate, logical pause with bounded owned read-ahead, checkpoint/verify/resume.
- `BinaryFileFramer::residual_bytes`: additive read-only diagnostic; previous framing
  semantics and P1E canonical outputs remain unchanged.

The [compression review](P1H_COMPRESSION_DEPENDENCY_REVIEW.md) records installed
header/runtime zlib1.3.1, actual package/library hashes, API contracts, license and
security/portability limits. Python's independent reference uses zlib1.3.2. No
new source dependency was downloaded or vendored. No current vulnerability-advisory
clearance is inferred from version pinning or synthetic tests.

Inflater input/output advances in fixed one-byte microsteps, aggregating into a
bounded output buffer (maximum64KiB). This conservative v1 policy makes byte-limit,
ratio and corrupt-prefix behavior independent of caller fragmentation. It is a
correctness baseline, not a throughput optimization. Concatenated members/trailing
bytes reject. Empty feeds drain cached output. CRC/ISIZE/header validation uses the
reviewed inflate API; ISIZE is not an allocation size or full uncompressed-size proof.

## Integrity, interruption and atomicity

Decoded events are provisional until explicit EOF, valid gzip member/trailer,
BinaryFile terminator with no trailing input, exact compressed SHA256 and exact raw
manifest SHA256 all agree. `source_complete` and `publication_eligible` remain false
at intentional cutoff, pause, any resource/error stop or identity mismatch. Context
session completeness and authored initialization are separate facts; no UTC clock,
exchange sequence, empty historical state or hidden liquidity is inferred.

The source receipt/context/native transaction is the validated P1G architecture.
Hashing accepted frame bytes adds only fixed nonallocating operations within proven
length bounds; no journal optimization or additional fallible post-native commit
was introduced. Physical source progress, framer progress, accepted frame bytes,
partial framing and buffered decoded output are reported separately. Framed source
records include rejected records; accepted records and native/external dispositions
remain explicit. Unread tails are not fabricated full-source totals.

Checkpoint descriptors bind config, caller-supplied implementation identity, exact
accepted-frame prefix SHA256, context summary and native canonical state. Restart
uses a fresh pipeline from compressed byte0, pauses at the exact committed record
count, verifies the trusted descriptor, then resumes owned read-ahead before new
input. No gzip seek, state deserialization, hot crash recovery or durable publication
transaction is claimed. Full artifact identity remains provisional until EOF.

Independent review reproduced one pipeline defect: CRC corruption beyond a logical
pause was visible earlier with a larger physical read. The repaired pipeline exposes
`observed_gzip_error` immediately, while deferring the logical failure until resumed
processing reaches its bounded decoded-tail boundary. Both chunk schedules now yield
the same provisional checkpoint and fatal final CRC result, with publication blocked.
Known physical corruption is never cleared or certified. A prior semantic/framing
stop finalizes the unread reader as a bounded prefix, avoiding a fabricated origin
truncation; genuine EOF without a trailer still reports truncation.

## Independent and adversarial evidence

See [P1H_COVERAGE.md](P1H_COVERAGE.md) for all17 required domains and their assertions.

- Gzip native tests:178,091 assertions across valid/error/limit/allocation groups;
  four reached real allocator-failure sites and exact cleanup.
- Pipeline native tests:2,119 fragmentation/cut schedules;10 factory and23 feed
  allocation-failure sites; literal ID/FIFO/quantity/ledger/context/receipt checks
  after every failure, owned-buffer moves, caps and reentrancy.
- Independent streaming oracle:475 fixtures,3,993 framed/3,989 accepted source
  records across fixtures, four semantic rejections,205 true-EOF cuts and205 bounded
  cuts,21 valid restart boundaries and two corrupt-CRC pause/restart schedules.
  Six intentionally incorrect expected models are detected.
- Streaming semantic SHA256:
  `be5d6f5a15fa1dc77560e0a815b8397a605eab369fa66f44df12e5ed9b04a4d5`.
- Independent review separately executed324 synthetic gzip cases across input and
  output-buffer sizes, preserving exact corrupt-prefix hash/count/error offsets.
- Independent stored-block fixture uses a handwritten wrapper/stored-block writer
  and bitwise CRC, not production inflate output as expected truth. Python independently
  checks the fixture bytes/CRC/SHA and flat L3/Fraction state. The measured Python
  oracle high-water is15,335,424 bytes (<128MiB default-profile proposal).

## Final supported matrix and package results

Linux x86_64, GCC14.2.0, Clang19.1.7 using the system GCC standard library,
CMake3.31.6, CPython3.12.14; warnings are errors, ASan/UBSan nonrecovering checks.

| Configuration, streaming enabled | Passed | Failed / skipped / disabled |
|---|---:|---:|
| GCC Debug |117/117|0 /0 /0|
| GCC Release |117/117|0 /0 /0|
| GCC ASan/UBSan |117/117|0 /0 /0|
| Clang Debug |117/117|0 /0 /0|
| Clang Release |117/117|0 /0 /0|
| Clang ASan/UBSan |117/117|0 /0 /0|
| GCC Python Debug |120/120|0 /0 /0|
| GCC Python Release |120/120|0 /0 /0|
| GCC Python ASan/UBSan |121/121|0 /0 /0|

**1,063 final CTest outcomes**, no failures, skips, disabled tests or observed sanitizer
findings. Each final JUnit preserves exact P1E/P1F/P1G hashes and the streaming hash.
No assertions, mandatory tests, warnings or sanitizer settings were weakened.

The final source archive contains49 frozen validation files byte-for-byte. Both the
direct wheel and an offline source-built wheel pass7 interface and6 export-contract
unittest cases each. Module paths identify the installed consumer environment;
its native extension has no libz dependency. Both research examples match the P1G
output byte-for-byte (SHA256
`c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9`).
Implementation/measurement checkpoint: `e055f055a447baa6bf1f913c09f7c7dcd57a8878`.
No artifact was published. Build/test/measurement raw evidence is retained under
`build/p1h/evidence/`; selected hashes/results are in [P1H_EVIDENCE.json](P1H_EVIDENCE.json).

## Reproducible memory and performance evidence

All measurements ran sequentially from the clean verified implementation commit
above, after the nine-row matrix/package gates. Intel Xeon Platinum8573C, five
exposed logical CPUs, shared virtualized Linux host; unsanitized Release. Two warmups
and seven actual measured repetitions per case. Fixture generation is outside timing;
create, incremental gzip/framing/context/native journal/receipts, EOF integrity checks,
validation and destruction are inside. These are batch averages, not event-service or
tail-latency distributions. The fixture uses explicitly labeled manual DEFLATE stored
blocks; compressed/dynamic-Huffman correctness is separately exercised by the oracle.
These rates are not measured NASDAQ archive throughput or production exchange SLAs.

Benchmark profile:1KiB inflater output,64-byte frame buffer, exact fixture byte caps,
ratio2 with64-byte slack, source count8n+8, per-book live capn/journal4n, context
lifetime4n/matches2n,2MiB receipt cap and128MiB hard shared PMR. Each profile is explicit;
n256 is a scale case above the initial128-live-order-per-symbol proposal.

| n per symbol | Source records | Gzip bytes | GCC17-byte chunks ns/record | GCC64KiB chunks | Clang17-byte chunks | Clang64KiB chunks | Peak PMR bytes |
|---:|---:|---:|---:|---:|---:|---:|---:|
|8|72|2319|11306.1|10865.5|10434.6|10553.7|1346672|
|32|264|8703|15715.8|14643.0|13839.4|13512.1|5250448|
|128|1032|34239|14800.1|14911.9|13128.0|12700.2|20865488|
|256|2056|68292|14719.0|15549.5|15189.2|14022.6|41685328|

All16 raw runs pass independent byte packing/decompression/CRC/SHA/mapping/count
checks; all actual samples are positive and all tracked bytes are released. Maximum
measured native high-water is58,093,568 bytes, below the proposed256MiB ceiling.
Wait-accounted RSS includes allocator/process memory and possible pre-exec worker
floors; it is not engine-only or aggregate concurrent process-tree memory.

P1G n128 without gzip/framing/full-source checks measured12155.6 GCC and11169.1
Clang ns/record; the new17-byte-chunk scope measures14800.1/13128.0. Scope and control
record counts differ, so this is context rather than a paired causal overhead or
speedup estimate. No journal optimization or performance acceptance threshold was
introduced. Full raw repetitions, executable/compiler/CPU/fixture identities, user/
system time and RSS are in the evidence JSON.

A separate real allocator probe measured the default-buffer profile:

| Category / selected profile | Actual bytes |
|---|---:|
| Gzip PMR at creation,64KiB output |73112|
| Gzip after inflation, including lazy window |105896|
| Generic framer payload buffer |65535|
| Context8 directories/1024 lifetime/1024 matches |74048|
| Empty two-book reconstruction,4096 receipts, same context |1483904|
| Decoder owned record / source lifetime order / match / directory |304 /56 /16 /40|
| Receipt element / native journal element |344 /15944|
| Native book PMR empty / one order / after erase |416 /616 /432|
| Streaming object / logical checkpoint (fixed object storage) |101808 /2712|

The source order ledger retains retired references at56bytes each; the match ledger
retains corrections at16bytes each. Native bucket capacity may remain after an erase;
destruction releases it. Default4096 receipt slots occupy1,409,024 element bytes.
Decoder/objects/stack and fixture allocations are distinct from selected PMR. All probe
resources return to zero. At n256, native journal elements alone retain32,653,312
bytes; vector growth can coexist at40,816,640 journal bytes before other state. Actual
pipeline PMR peak41,685,328 bytes confirms why bounded input does not solve retained
history. The existing journal remains15,944bytes/entry and100,000 maximum records;
no storage redesign occurred. Further optimization requires separate equivalence,
failure-atomicity, migration and benchmark gates.

### Large compressed synthetic source: controlled stop

An independently generated source contains500,001 authored control records,
20,500,016 decompressed bytes, compressed to59,723 bytes with actual deflate compression.
The selected probe profile caps accepted source records at1024. It stops at complete
frame1025 with `source.limit`, accepts exactly1024 external observations and zero native
mutations/journal entries, and blocks completion/publication. This is an expected
budget stop, not a pass over all500,001 records or a full-artifact integrity claim.

Only255 compressed bytes and65,536 decoded bytes are read/generated. Framing reaches
41,998 bytes;23,538 decoded bytes remain buffered. The accepted frame prefix is41,957
bytes with independently verified SHA256
`5d5be56e33cd25588be128086a356400e37ff2d0d26d8bee4a40436932c5764f`.
Peak selected PMR is598,567 bytes,11 allocations, zero retained bytes after destruction;
wait-accounted process high-water is10,223,616 bytes. The full-source count/tail here
comes from the authored generator inventory, not fabricated reader knowledge.
No20.5MiB decompressed archive is retained by the pipeline. Fixture creation itself
uses bounded test-only storage outside Git and is outside the pipeline/RSS timing.

### Offline reproduction

Use the existing pinned compiler/Python setup. Native presets enable streaming and
require system zlib development headers/runtime>=1.3.1 (qualified here at1.3.1).

```sh
CXX=g++ cmake --preset release
cmake --build --preset release -j2
ctest --preset release --output-on-failure
python3 scripts/check_itch_streaming_reference.py build/release/gig_itch_streaming_reference_driver
python3 scripts/check_itch_streaming_benchmark.py build/release/benchmarks/gig_itch_streaming_benchmark
build/release/benchmarks/gig_itch_streaming_benchmark 128 7 17
build/release/benchmarks/gig_itch_streaming_benchmark --fixture 128 > /tmp/gig-authored-synthetic.gz
```

The last command creates only an authored synthetic fixture. No network access or real
archive is required. The validated host reused `build/phase9-clean-release` and
`build/phase9-clang-release`; its commands/logs/raw measurements are retained under
`build/p1h/evidence/`. Large/probe identities and hashes are in the durable evidence;
temporary probe source was `/tmp/gig-p1h-memory.cpp`, separately hashed, not a new
engine API. Full default-cap checkpoint/RSS combinations and service tail latency are
not exhaustively measured; resource stops are explicit rather than promises all caps
fit simultaneously.

## Remaining limits

The pipeline accepts caller-supplied byte chunks; it is not a network/archive acquisition
adapter. General APIs require a caller-owned budgeted PMR for an aggregate byte cap;
validation supplies128MiB. Count/buffer caps remain finite but process RSS, input
fixture storage and allocator overhead are separate. Context/retired/match histories,
receipts and large native journal entries remain retained and bounded by explicit caps.
Streaming input does not imply constant-memory or whole-day reconstruction.

Only authored-empty synthetic initialization and two configured symbols qualify.
Historical profile/unsupported messages/other-scope classification, real initial state,
independent observed references and empirical calibration remain unverified. A trusted
checkpoint is not a signature or proof of publisher origin. Header/library-version
qualification is Linux x86_64 only; hosted CI, ARM64, other OS/stdlib/Python combinations
and current advisory clearance are unverified. Existing Python live-LSan late-finalization
limits remain explicit; native leak checks were not disabled. P1I/P1J production work,
real-data acquisition, main merge and release publication require further authorization.
