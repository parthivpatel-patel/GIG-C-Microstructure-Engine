# P1H compression dependency and container-policy review

Reviewed October23,2026 UTC against remotely verified P1G
`c3c3d8caef8f5b60aa4ce29f0f0875dc3bdd91c4`. This is a dependency decision and
source-contract review. It is not the P1H test report, a security certification,
or evidence of NASDAQ archive validation. No market-data bytes, external RFCs,
advisories or packages were downloaded for this review.

## Decision and dependency boundary

Use the installed **zlib1.3.1** through its documented incremental `inflate` C API,
with the gzip-only wrapper request `inflateInit2(...,15+16)`. Do not add another
compression framework or implement Deflate ourselves. The C++ wrapper must own
its input/output bounds, PMR allocations and exact state/failure reporting; selecting
a mature decoder does not supply those application guarantees automatically.

Introduce a separate optional `GIG_BUILD_ITCH_STREAMING` build feature, default
**OFF**, finding zlib **minimum1.3.1** when enabled and linking the imported
`ZLIB::ZLIB` target through the new streaming target. Native Debug/Release/sanitizer
presets and the actual P1H validation configurations must explicitly turn it **ON**;
Python regression build trees can enable the standalone streaming tests without
adding an ITCH/P1H Python API or linking that feature into the existing Python
module. Ordinary wheel defaults remain **OFF** and require no new compression
dependency. Do not weaken existing tests or treat an OFF configuration as a passed
streaming qualification. Final implemented CMake/settings and executed counts belong
in the P1H evidence report; this paragraph states the selected policy.

System zlib is already present, so no installation, network/package-manager change,
vendored source, paid service or new market-data entitlement is required. Preserve
the existing engine, simulator, matcher, execution, TCA and journal contracts.

## Independently observed installation

Executed local metadata/hash checks and a tiny C++ gzip-initialization probe; no
synthetic stream performance or production adapter test follows from these checks.

| Observation | Actual result |
|---|---|
| `pkg-config --modversion zlib` | `1.3.1` |
| `pkg-config --cflags --libs zlib` | `-lz` (default system includes) |
| `pkg-config --variable=libdir zlib` | `/usr/lib/x86_64-linux-gnu` |
| `dpkg-query` package versions | `zlib1g` and `zlib1g-dev`: `1:1.3.dfsg+really1.3.1-1+b1`, `amd64` |
| Shared-library aliases | `libz.so` and `libz.so.1` point to `libz.so.1.3.1` in that directory |
| Header/runtime probe | `ZLIB_VERSION=1.3.1`, `zlibVersion()=1.3.1`, `zlibCompileFlags()=169` |
| Probe ABI sizes | `sizeof(uInt)=4`, `sizeof(uLong)=8`, `sizeof(z_stream)=112` bytes on this host |
| Probe initialization/cleanup | `inflateInit2(...,31)=Z_OK(0)`, `inflateEnd=Z_OK(0)` |

Probe source: `/tmp/gig-p1h-zlib-probe.cpp`, executable:
`/tmp/gig-p1h-zlib-probe`; these are temporary local evidence, not distributable
project artifacts. Compile command:

```sh
/usr/bin/g++ -std=c++20 -Wall -Wextra -Werror \
  /tmp/gig-p1h-zlib-probe.cpp -lz -o /tmp/gig-p1h-zlib-probe
/tmp/gig-p1h-zlib-probe
```

Exact-byte identities for this installation, not portable dependency lock hashes:

| Local file | SHA256 |
|---|---|
| `/usr/include/zlib.h` | `8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c` |
| `/usr/include/zconf.h` | `44e543ff4514c7a9a01d648019c2c9a81d1105cbfa3c77f1faf6cd86eafa8abd` |
| `/usr/lib/x86_64-linux-gnu/libz.so.1.3.1` | `85590dd58edf5445e18bc7193e5ebc01ac5841f1ae187e97705a662e90c6421e` |
| `/usr/lib/x86_64-linux-gnu/libz.a` | `f81da8056ea0ee821570a6289f2f77b65de24756df2ad68730295ad818266579` |
| `/usr/lib/x86_64-linux-gnu/pkgconfig/zlib.pc` | `4bd54096d6c5f7f370956ab5df18b250f226d0ee6200bbeb86087e15887f8fb7` |
| `/usr/share/doc/zlib1g-dev/copyright` | `9e5b96d63773a5d177ba264254390f792be07e41748ebd94730981c6cac31cc6` |

## Specification and API evidence

The local `/usr/include/zlib.h`1.3.1 was read directly. Relevant documented contracts:

| Header location | Contract and application consequence |
|---|---|
| Lines1–28,115–149 | License restrictions and bounded caller-provided gzip header buffers; do not buffer unlimited optional names/comments |
| Lines221–229;1792–1823 | Header/runtime compatibility and init macros carry version/structure size; inspect actual init return, record runtime version separately |
| Lines465–515 | Incremental output can precede final validation; gzip CRC32 and output length modulo2^32 checked at stream end; `Z_BUF_ERROR` is not automatically corrupt input |
| Lines835–890 | `windowBits=31` selects gzip only; `inflate` returns `Z_STREAM_END` at one member, does not automatically process concatenated members |
| Lines1035–1073 | Header checked including optional FHCRC even without retaining header fields; truncated optional-field copies do not themselves limit total header length |
| Lines1326–1341,1398–1415 | `gzread` supports concatenated members and can pass through non-gzip input; unsuitable for this explicit strict single-member policy |
| Lines94–112 | Custom `zalloc/zfree` and `uInt` input/output counters; application must bridge checked sizes and prevent C++ exceptions escaping C callbacks |

Canonical gzip format reference: **RFC1952**, https://www.rfc-editor.org/rfc/rfc1952 .
The installed header itself identifies RFCs1950–1952 as format references. The local
Debian copyright metadata lists `doc/rfc1950.txt`, `doc/rfc1951.txt` and
`doc/rfc1952.txt` among excluded files; no such copies were found under
`/usr/share/doc` during this review. **No RFC text was fetched or independently
re-read here.** Specific behavior above is supported by the inspected API header,
not a claim to newly inspected RFC wording. Existing P1D design's pending gzip
dependency review is addressed by this installation/API evidence plus actual P1H
tests; official NASDAQ BinaryFile/ITCH specifications do not define gzip behavior.

## Required strict-container policy

The authorized implementation selects **one gzip member only**, rejecting further
members and any trailing bytes explicitly. This is an intentional supported-input
restriction, not a claim that concatenation is invalid gzip or that the NASDAQ file
contains only one member. A future observed profile must inventory actual members
and separately review support before changing this restriction.

- Require gzip framing, never raw Deflate/zlib auto-detection or plain-file fallback.
- Use incremental bounded input/output chunks and checked application-owned64-bit
  cumulative counters. zlib's `uLong total_in/total_out` width varies by platform;
  do not base large-stream budgets on this host's8-byte width.
- Enforce absolute compressed-input and decompressed-output caps plus the configured
  ratio/slack cap. Record exact limits and whether ratio uses consumed input or
  another declared denominator; cap checks must not depend on arbitrary read size.
  Optional-header processing consumes the compressed budget even when no output
  appears. A large header must not trigger proportional field-storage allocation.
- The inspected initial `src/itch/gzip.cpp` uses fixed **at-most-one-input-byte /
  one-output-byte** inflate steps, checking each output byte against the absolute
  and ratio/slack limits using actually consumed compressed bytes. Publication
  groups may differ with caller fragments, but admitted byte order and deterministic
  limit/error prefixes must not. A feed can return preceding provisional output
  **together with an error**; callers must process/account for that output without
  labeling it source-integrity-verified. An unpublished one-byte overflow probe
  detects output beyond an exact cap. This conservative correctness baseline is
  intentionally not a throughput optimization or performance SLA; benchmark its
  actual overhead before considering any equivalent batched implementation.
- Validate headers, optional-header CRC when present, Deflate errors, trailer CRC32
  and ISIZE before declaring member integrity. ISIZE is modulo2^32, not a complete
  decompressed-size measurement. CRC32 detects corruption; it is not authentication.
- Distinguish `Z_OK`, `Z_BUF_ERROR`, `Z_STREAM_END`, allocation failure and corrupt
  input. A no-progress condition may require more input/output; an infinite retry
  loop, ignored error or automatic `inflateSync` recovery is prohibited.
- Distinguish declared bounded interruption from actual EOF/truncation. A cutoff
  inside a member cannot verify its final CRC/trailer. Retain exact accepted prefix
  identity and physical read-ahead; do not label it a full verified archive.
- On late CRC/trailer failure, already committed semantic prefix events cannot
  simply be undone or relabeled container-verified. Preserve the prefix diagnostics,
  mark integrity/source completeness false and block a full-source success claim.
  Conversely, CRC success does not prove upstream exchange delivery completeness.

The streaming adapter may feed decoded bytes to reconstruction before the trailer
arrives. This is conditional accepted-prefix processing: per-event context/native
atomicity is distinct from final source-integrity certification. Neither a BinaryFile
terminal observed early nor a complete local lifecycle permits reporting source
complete before clean gzip end and caller-declared actual EOF with no trailing data.

The pipeline additionally requires the actually consumed compressed SHA256 and
decoded artifact SHA256 to match the authored fixture manifest before publication
eligibility. Those full-artifact identities, container integrity, BinaryFile
termination, context lifecycle completeness and upstream exchange completeness are
different facts. None is inferred from another.

### Logical pauses versus physical read-ahead

The inspected streaming implementation keeps a bounded owned decoded tail when
pausing after an accepted record. A CRC error already observed while producing that
tail is exposed as `observed_gzip_error`; it is not erased. Its logical stop is
deferred until resume consumes the preceding tail or otherwise stops. This lets
the same accepted-frame prefix produce the same provisional checkpoint regardless
of how far the compressed reader happened to advance. The checkpoint excludes
physical read-ahead and carries no source-integrity/publication certification.
Restart begins at compressed byte0 and independently replays to the trusted logical
descriptor; it does not seek into Deflate or restore a hot process snapshot.

A focused independent review reproduced an early implementation defect: with a
corrupt CRC suffix, pause-after4 succeeded for one-byte compressed fragments but
checkpoint capture failed for a single whole-artifact fragment. The bounded
deferred-error repair preserves the physical diagnostic while making both checkpoints
available; resuming both reaches the same explicit corruption and cannot publish.
Development reproduction/verification evidence is retained locally under
`build/p1h/evidence/pause-corrupt-{before,after}-fix.json`; final frozen-source tests
and sanitizer matrices remain separate mandatory evidence.

Finalizing an intentionally paused stream seals a bounded prefix, including its
context, even if the caller also declares physical EOF; that sealed instance cannot
hot-resume. A pre-existing framing/semantic failure similarly stops the gzip reader
as a bounded prefix instead of inventing a new gzip-truncation diagnosis for an
unconsumed offered tail. A genuine actual EOF with no preceding pipeline stop still
requires a validated member end; missing header/body/trailer bytes are truncation.
Known gzip corruption is always retained independently of the first primary pipeline
error. No bounded/pending/errored outcome is full-source publication-eligible.

## Memory, lifetime and failure requirements

The decoder wrapper must use RAII cleanup on every init/feed/error/end/destruction
path. Custom allocation callbacks need checked `items*size` arithmetic, valid
alignment, selected PMR/budget accounting and a no-throw C ABI boundary. Memory
resource ownership must outlive decoder and all outputs; moving an object must not
leave callback opaque pointers referring to a destroyed/moved owner. Test actual
zlib allocations, including lazily allocated window state, rather than injecting
only wrapper allocations. No all-output accumulation or whole compressed archive
buffer is justified by the dependency choice.

Separate framer, decoder work buffers, context/order/reference ledgers, receipts,
native journal, PMR peaks and process RSS. Streaming alone cannot bound the retained
native journal. Preserve the15,944-byte-per-entry baseline finding and the separate
optimization/equivalence proposal; do not redesign journal storage incidentally.
The shared PMR governor cannot account for external runtime/library mappings or
process-stack memory, so independent peak RSS and sanitizer results remain necessary.

## Security, portability and reproducibility limits

The minimum1.3.1 is the tested integration floor, **not a claim that1.3.1 or every
newer build is vulnerability-free**. No advisory database, vendor support policy,
full upstream source audit or dependency supply-chain attestation was performed.
Installed distro patch identity is recorded; a later build must record its own
actual header/runtime/package identities. Review relevant advisories before any
release decision, without claiming unavailable evidence as clean.

System zlib avoids vendored maintenance but means builds on another OS/distribution
need not resolve identical bytes. Discover with CMake's imported target rather than
hard-coded Linux library paths. Validate header/runtime compatibility and relevant
ABI sizes, fixed-width counters and cleanup on every supported platform. ARM64,
Windows, macOS, other C libraries and other zlib versions are not qualified merely
because the API is portable. Header/version compatibility checks are not a runtime
security-version-floor check; record actual loaded version and fail/review an
unexpected dependency identity according to the declared run profile.

Deterministic semantic results must not depend on compressed chunk scheduling or
the exact compressor's byte encoding. Preserve both compressed artifact SHA256 and
decoded/source-prefix SHA256; equivalent gzip byte streams can differ in timestamp,
header fields or compressor decisions. Fixture generation must fix those inputs or
record them. Cross-compiler output equality and external Python/gzip reference checks
are required independently of selecting zlib. Do not compare sanitizer throughput
with Release, or infer real NASDAQ throughput from synthetic compression.

## License and distribution handling

The installed header attributes zlib to **Jean-loup Gailly and Mark Adler** and
permits any use, including commercial applications, with origin not misrepresented,
altered sources clearly marked and the notice preserved in source distributions.
The distro copyright record includes the same Zlib license, packaging notices and
an upstream source URL. This review introduces no modified/vendored zlib source.
If later distributing dependency source/binaries, retain applicable notices and
review the actual redistribution packaging; do not claim this document alone settles
every release obligation. The default Python wheel does not acquire a new zlib
link/API from the optional feature. Market-data licensing is entirely separate from
the compression library's license.

## Acceptance handoff

P1H completion still requires actual independent valid/corrupt/truncated/header/
CRC/member/ratio/fragmentation/resource/restart fixtures, real allocator failpoints,
full supported compiler/sanitizer/Python/package gates, deterministic hashes and
measured memory/throughput evidence. This review authorizes no archive acquisition,
source licensing inference, release publication or live integration. Record final
results in the P1H validation/progress evidence rather than treating this policy
review as executed pipeline acceptance.
