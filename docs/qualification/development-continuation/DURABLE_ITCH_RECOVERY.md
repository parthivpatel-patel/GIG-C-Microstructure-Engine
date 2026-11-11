# Durable ITCH recovery — November 11, 2026

This is an offline development contract for authored synthetic ITCH reconstruction. It does not establish observed exchange completeness, authenticated exchange sequencing, observed L3 initialization, actual owner deployment or hardware power-loss recovery. No application, listener, provider, account or workflow is started by these APIs.

## Version 1 artifact and trust

`include/gig/itch/durable_checkpoint.hpp`, `src/itch/hot_codec.cpp` and the explicit member inventory in `src/itch/hot_codec_fields.hpp` define the format. It is field serialization, not a memory dump or a pickle.

|Byte range|Encoding|
|---|---|
|0–7|ASCII `GIGITCH1`|
|8–15|Schema version, unsigned little-endian 64-bit, currently 1|
|16–23|Payload length, unsigned little-endian 64-bit|
|24–55|Raw 32-byte SHA-256 of payload|
|56 onward|Capture token, generation, implementation digest, complete typed hot reconstruction image|

Every scalar is an eight-byte little-endian value, including Boolean presence flags and variant indices. Signed native numbers use their exact 64-bit two's-complement representation with checked narrowing. Booleans, enums, ASCII fields, scalar minima and variant indices are validated. Tokens and canonical strings have explicit lengths. Fixed arrays have schema-defined lengths; fixed ITCH Text fields preserve their exact padded bytes. Other fixed-array elements use their element codec (including eight bytes per typed digest-byte element). Lists carry a checked count. Optional fields carry a strict presence flag. No pointers, allocator identities, prepared tokens or process handles are serialized.

The image includes complete configuration/initialization evidence, source/context policies, directories, active and inactive lifetime orders, seed-retired references, matches/broken flags, lifecycle stage and source cursors, all receipts and source provenance, sequence bases, both full native books, native journals/cursors/configuration and canonical strings. Seed recovery retains its original recovery journal event and starts continuation sequences at one. No new synthetic identities are invented during restoration.

`DurableAdmission` is supplied **outside** the untrusted artifact. It binds the artifact SHA-256, deterministic configuration digest, implementation SHA-256, capture identity and exact generation. Header, payload checksum, external identity and version checks precede materialization. Native/source cross-checks and canonical admission precede publication of the isolated owner. A checksum embedded in the same file is not authentication. Operators must retain admission evidence independently; computing a hash of an arbitrary downloaded file does not authorize it.

Version 1 accepts only its own schema and exact implementation contract. Unknown versions, unknown fields represented by trailing bytes, and different capture/generation/configuration/code identities fail closed. There is **no automatic schema or code migration**. A future migration must have a separately specified and tested profile; do not edit metadata to relabel old bytes.

## Resource envelope

- Entire artifact at most 32 MiB; individual canonical strings at most 16 MiB.
- At most 4,096 entries per dynamic list, context capacity and native journal/order/level capacity in this durable profile. The older general-purpose engine limits are not broadened or removed.
- At most 2,000,000 decoder nodes and 128 MiB total requested decoded dynamic storage; counts and remaining bytes are checked before reserve.
- The Python native owner uses an explicit PMR budget, 128 MiB by default and at most 256 MiB, across decoding and isolated native restoration. This is managed native memory, not total Python RSS or OS page cache.
- Configuration hashing streams into SHA-256 without dynamic allocation. No floating-point conversion is used.
- Failure leaves the input bytes and any pre-existing owner unchanged. Restored prepared-token ownership uses a fresh context instance guard.

A matching checksum does not excuse invalid native/context state. The regression also demonstrates rejection of an impossible next cursor on a zero-record image, even when its typed fingerprint was recomputed.

## Python and immutable files

The installed SDK exposes `gig_microstructure.itch_recovery.ItchAdmission` and `ItchRecovery.restore`. It validates exact Python types, lengths, digest syntax, capture/generation and budgets before calling the real native admission path. Status, both canonical books, explicit complete-record continuation and recapture are available. Accepted prefix events are not reapplied.

`terminal/itch_recovery.py` adds explicit `save_new` and `load` operations. These are not startup hooks or HTTP endpoints. Only native-admitted authored images are written. The existing private-directory policy and bounded, symlink-rejecting file reader are reused.

Publication writes a private temporary file completely, checks the write count, flushes and fsyncs it, atomically links a new immutable revision without overwriting rollback input, then fsyncs the directory. Before-link failure leaves no published target. After-link failure is reported as publication uncertainty and requires reopening with the trusted admission. An abrupt process exit after linking may leave an extra private hardlink; exact bytes and private ownership still determine admission. The tests cover local process failure, not hardware/filesystem guarantees beyond the tested host.

## Source, framing and gzip coordination

`include/gig/itch/source_recovery.hpp` and `src/itch/source_recovery.cpp` define `resume_hot_source` in the optional streaming library.

1. Verify the independently supplied immutable source SHA, capture, generation, container and source starting Location.
2. Restore the native/context image into an isolated candidate.
3. Frame from the configured authored starting boundary. Compare committed frames against their exact retained decoded receipts, including original provenance; **do not call the context/native transition path for those frames**.
4. Apply only new complete frames. New records use the configured source provenance; existing receipt distinctions remain unchanged.
5. Publish only after all supplied input validates. A gzip input must be one complete CRC/trailer-verified member. A bad trailer discards the isolated candidate even if its suffix has already been processed internally.

Plain input and seeded-tail gzip input are supported. Gzip decompression starts at compressed byte zero; this is bounded container/framing reprocessing, not committed-event replay or a claim of constant-time decompressor restoration. No arbitrary compressed seek, zlib pointer serialization or partial-frame admission exists. Terminal BinaryFile cursor positions are explicitly unsupported by this active-prefix profile. Gaps, missing/altered committed frames, incomplete frames/members, trailing members, stale generations, budget exhaustion and unexpected source boundaries are rejected. The result remains an active accepted bounded prefix; it is not a declaration of complete historical coverage.

## Developer reproduction

With the existing compiler/build presets and optional Python bindings enabled:

```bash
cmake --build <build> -j 3
ctest --test-dir <build> --output-on-failure -R 'itch\.(durable_checkpoint|source_hot_recovery|hot_context_checkpoint)|python\.itch_durable_recovery'
PYTHONPATH=<build>/python:. <venv>/bin/python terminal/tests/run_no_launch_suite.py
```

These commands execute offline developer tests, not the application. The CTest Python test invokes an authored fixture executable, verifies actual cross-process bytes and abrupt-exit restart, and forbids socket bind/connect. Its child process sets an explicit repository working directory; this repairs the initially reproduced CTest import failure without weakening the assertions.

Final source-bound receipts, exact counts, compiler profiles, frozen hashes, packaging and failing-before evidence are recorded in `DURABLE_ITCH_EVIDENCE.json`. The previous checkpoint's evidence is retained rather than rewritten as current results.

## Remaining limits

Full Inline-XBRL transformations/continuations, full schema/custom-type/relationship semantics, complete financial-statement assembly and financial API integration remain partial. The DTS simple-reference validation defect was separately reproduced and repaired. No source history or missing financial values were manufactured.

The Alpaca/IEX gates, execution-disabled defaults and prior lifecycle repairs are preserved. Kraken remains provisional: official current contract/rights material was not obtained and no known blocked host was retried. Actual provider, observed-L3, private Codespaces, browser/device and native ARM64 acceptance remain unverified for this implementation. None is implied by offline fixture success.
