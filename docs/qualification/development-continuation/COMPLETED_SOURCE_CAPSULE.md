# Completed-source replay capsule v1

This separate native/SDK format persists the originals needed to reconstruct a
finished supplied source. It does not change the active durable-v1 image, encode
opaque finished C++ objects, infer unknown migrations or seek inside compressed
streams. Existing restore/resume/complete APIs and defaults remain unchanged.

## Exact format and independent trust

Bytes are `GIGSCAP1` (eight ASCII bytes), original image length as u64 little-endian,
original source length as u64 little-endian, then exactly those two original blobs.
No padding, additional members or trailing bytes are accepted. Total size is bounded
to32MiB, including the24-byte header. Lengths are checked before slicing/allocating;
unsupported magic/version refuses interpretation.

`CompletionCapsuleAdmission` is retained independently: capsule SHA-256, the original
`DurableAdmission`, and the original `SourceRecoveryAdmission`. Nothing inside an
untrusted capsule supplies its own trust. The native decoder authenticates the whole
capsule before allocations, then verifies original checkpoint contract/code/capture/
generation and the complete source identity through the existing coordinator. Its
committed prefix is checked without reapplying it. Only the suffix is applied.
Plain input requires terminator at exact EOF; single-gzip requires its verified sole
member CRC/trailer and the same decompressed terminal boundary. Seed and source
positions remain independently admitted. Source replay starts at byte zero.

Encoding first completes an isolated native reconstruction, destroys that temporary
owner, then allocates the capsule output. Resource failures return no artifact.
Restore returns a finished owner; further process/hot-checkpoint operations reject.
The original image, source and prior active owner stay unchanged. Identical admitted
originals produce identical capsule bytes and reconstructed canonical books.

This is a replay capsule, not arbitrary terminal-image schema migration. It provides
bounded durable completed-source handling using the already supported active image
and original source contracts. Supplied-container completion remains distinct from
observed source authenticity, exchange/session completeness and hardware durability.

## APIs and SDK capability

Native APIs in `completion_capsule.hpp` are `encode_completion_capsule` and
`restore_completion_capsule`. All memory comes through the supplied PMR resource;
existing source/gzip/record limits remain in force. No file or transport is opened.

The optional streaming SDK adds:

- `ItchRecovery.create_completion_capsule(image, admission, source, source_admission)`
  returning bytes and frozen `ItchCompletionAdmission`;
- `ItchRecovery.restore_completion_capsule(bytes, admission)` returning the existing
  read-only `ItchSourceCompletion` view.

The typed capsule admission retains the original checkpoint/source admissions and
scope equality. Exact types, lowercase SHA-256, u64 positions, generation, byte and
resource budgets fail closed. Default SDKs without streaming reject explicitly;
there is no Python replay fallback. The existing active-v1 decoder refuses a capsule,
and a finished owner cannot be relabeled as an active-v1 checkpoint.

## Demonstrated offline acceptance

The new native target reports535 assertions, including all actual encode/restore PMR
failure positions: plain restore57/encode58, gzip restore61/encode62. It covers exact
header/original bytes, deterministic replay, stale metadata, corrupted/rehash-forged
bodies, length overflow, trailing data, missing terminal/trailer, null resources,
immutable prior state and allocation cleanup. The target was freshly compiled and
passed in GCC Debug/Release, Clang Debug/Release and native ASan+UBSan.

Eleven SDK tests cover both containers, wire layout, immutable originals, exact type/
budget/admission refusal, unavailable SDK capability, finished-write rejection and
an actual fresh-process capsule restore. Combined with the existing completion and
source-product tests,33 pass. The complete Release CTest cohort passes153 targets;
all eight freshly relinked reference identities match the prior checkpoint exactly.
Logs: `work/nov21-native/`. Final source-bound receipts record publication/build scope.

REL02 remains PARTIAL for partial-frame checkpoint contracts, unsupported image/schema
interpretations, arbitrary compressed offsets and actual observed/hardware evidence.
No application/server/provider, deployment, trading, spending or owner acceptance
was performed for this package.
