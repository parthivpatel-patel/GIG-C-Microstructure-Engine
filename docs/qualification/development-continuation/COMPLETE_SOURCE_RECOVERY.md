# Explicit verified-container source completion

The additive native `resume_complete_source` API restores an independently admitted
active version-1 durable image into an isolated owner, verifies the supplied source
SHA-256 before allocations, reparses its committed prefix without applying it, and
applies only a compatible suffix. It then requires the BinaryFile `00 00` terminator
at exact source EOF. Single-gzip input also requires complete sole-member CRC/size/
trailer verification. Source reading starts at byte zero; no compressed offsets,
inflate pointers or partial-frame positions are guessed.

This is a bounded extension of the existing native source contract. The original
`resume_hot_source` API, durable v1 wire format, configured seed/capture/generation,
source boundaries and defaults remain unchanged. Original v1 still refuses terminal
positions. The new API accepts a terminal supplied container, not a serialized
finished v1 image. A successful candidate is finished and rejects further process or
hot-checkpoint calls. Unsupported v1 terminal serialization and schema migration are
not bypassed by relabeling the image. Source/container completion does not prove a
complete exchange session, source authenticity, observed initialization or hardware
durability. The context's separate session-incomplete flag remains visible.

## SDK integration

The optional streaming SDK adds `ItchRecovery.complete_source(image, admission,
source, source_admission, resource_budget_bytes=...)`. All trusted metadata, hashes,
exact Python types, resource budgets and first-position checks remain explicit.
It returns `ItchSourceCompletion`, a read-only owner exposing status, description,
canonical books and depth. Original checkpoint admission and source admission stay
separate. There is no checkpoint/process method on that public completed-owner API.
The native finished owner also rejects those operations if called internally.
Default SDKs without streaming support reject explicitly; no Python replay fallback
or provider/application activation exists.

Native `completion()` reads the existing summaries without attempting the active-
context checkpoint operation, which intentionally refuses finished contexts. Status
keeps exact decimal-string counters and separate finished/input-complete/session-
incomplete booleans. Existing active-owner status shape and APIs are untouched.

## Bounds and failure behavior

Existing limits remain 32MiB source/decompressed/framing budgets, 4,096 frames and
a single complete gzip member. The isolated candidate is never returned on errors.
Missing/truncated terminators, trailing data, additional gzip members, CRC/trailer
corruption, changed committed frames even after source rehash, missing prefixes,
invalid continuations, stale capture/generation, resource failure and wrong seed
boundary reject. Original checkpoint bytes and prior owners stay unchanged.
No recovery semantics for arbitrary compressed seeking, partial frames, unknown
schemas, finished durable images or hot observed-source continuity are added.

## Current offline verification

`tests/test_itch_source_recovery.cpp` compares plain/gzip completion with an
uninterrupted native finish, including seeded nonzero-boundary tails. It checks
legacy terminal refusal, no duplicate prefix effects, no terminal serialization,
immutable inputs, rejected writes, exact trailer/EOF failure and every actual PMR
allocation failure. The complete-source sweep exercises 66 allocation positions;
legacy source restore retains its 67-position sweep. The target reports331 checks.

The actual new source coordinator was rebuilt and tested under GCC Debug/Release,
Clang Debug/Release and native ASan+UBSan. All eight freshly relinked native reference
hashes match the protected delivery baseline. `terminal/test_itch_source_completion.py`
adds11 SDK tests including an actual new-process restore/finish; the existing11
source-product tests remain passing. Missing/partial/bad-gzip/admission/budget cases
and explicitly disabled SDK capability all fail closed. Logs are in
`work/completion-recovery/`; final source-bound receipts record exact commits.

REL02 remains PARTIAL: this closes verified-container terminal continuation and its
SDK read-only boundary, not all partial/terminal image, migration, compressed-position
or hardware/observed continuity criteria. No application/server/provider, deployment,
trading or paid resource was used.
