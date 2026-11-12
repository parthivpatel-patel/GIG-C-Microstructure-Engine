# Authored full-source continuation through SDK and product — November 12, 2026

The existing tested C++ `resume_hot_source` coordinator now has an optional
Python binding and an explicit private product-file operation. This closes an
SDK/product integration gap;it does not extend a provider's protocol guarantees.

## Build and admission

`GIG_BUILD_ITCH_STREAMING=ON` builds the zlib-backed coordinator into the native
extension. Default OFF builds preserve the previous dependency contract and
reject SDK source continuation with `itch_source_sdk_streaming_disabled`.
No Python decompression/parser fallback bypasses native admission. This build
flag grants no provider,observed-storage,execution or startup permission.

`ItchRecovery.resume_source(image,admission,source,source_admission)` accepts exact
bytes,an independently retained image admission and a separate `ItchSourceAdmission`:
source_sha256,capture,generation,container,first_frame,first_ordinal. It verifies
Python types,budgets,digests and capture/generation scope before native allocation.
The C++ coordinator validates the configured first boundary and committed receipts
without applying the prefix,then applies only new complete frames in isolation.
Failure cannot mutate the original accepted owner. The returned admission pins
the newly encoded image;it is not left pointing at the input image hash.

Containers:plain BinaryFile and one complete CRC-verified gzip member. Limits:
source input32MiB,PMRbudget<=256MiB,decompressed/framer32MiB,4096framed records;
the existing default gzip compressed limit is additionally1MiB. No arbitrary
compressed seek,partial/terminal frame boundary,extra gzip member,source gap or
generation promotion is supported. Existing native allocation-failure tests
remain mandatory. Unknown artifact schema and wrong source bytes fail closed.

## Product revision2

Old product revision1 remains readable/writable for its existing contract.
The new `continue_source` operation creates revision2 only when a verified source
continuation adds source-recovery lineage. The native typed artifact remains
version1;this does not reinterpret a native artifact schema.

Revision2 adds a bounded four-record source_history with original bundle/image
hashes,source hash/container,capture/generation,configured first boundary and
from/to source-record counts. Captures and explicit code migrations preserve
that lineage;invalid types,scope,counts,versions and over-budget history reject.
A verified repeated identical source with no new events returns the same bundle
bytes rather than consuming history or duplicating transitions. The operator
must retain the independent bundle/source admissions;self-contained hashes are
integrity evidence,not authentication or proof of complete exchange capture.

The input product must have no unresolved authored continuation. Otherwise the
operation rejects instead of silently replacing the pending records. The result
is a new immutable private revision,starts paused on restoration,retains both
books and exposes source-recovery hash/count provenance in the ordinary state.
It never creates a historical UTC timestamp or changes authored origin to live.

## Offline operator command

```bash
<venv>/bin/python scripts/manage_itch_session.py continue-source --input <trusted-private-bundle> --expected-sha256 <independently-retained-bundle-hash> --source <private-authored-source> --source-sha256 <independently-retained-source-hash> --container binary_file --first-frame <configured-first-frame> --first-ordinal <configured-first-ordinal> --output <new-immutable-private-revision>
```

`single_gzip` selects the complete-member container. All boundary/hash arguments
are explicit;no value is learned from an arbitrary source to confer authority.
Files require existing private-parent/owner/0600 protections and bounded readers.
No launcher,provider,application factory or listener is called. Summary stdout
contains bounded source/output hashes/status,not raw frames or credentials.
Existing inspect/migrate actions remain compatible and reject stray source flags.

Tests use independently authored source fixtures from the same native test
harness:plain/gzip equivalence,only-suffix accounting,idempotent restart,changed
committed prefix,CRC,truncation,extra members,partial/terminal frames,wrong
scope/boundary,resource refusal,optional SDK disabled mode,revision1/2 compatibility,
malformed lineage,explicit migration,immutable CLI publication and separate-process
restoration. The original9durability and18product cases are retained unchanged.
Native mathematical algorithms and all eight frozen identities remain mandatory.
