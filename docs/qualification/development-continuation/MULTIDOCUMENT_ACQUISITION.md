# Explicit bounded inline acquisition manifest

`FilingIngestor.ingest(..., inline_manifest=...)` accepts caller acquisition intent
with exactly schema (`gig.sec.inline_acquisition_manifest.v1`), issuer_cik,
accession, primary_document and documents. Each of one to eight documents has exactly
name and lowercase SHA256. Names are local XHTML filenames; all must be advertised
regular files with exact sizes. The primary must equal current filing metadata.
The manifest is caller-supplied intent, not an official SEC document-set assertion.
All existing source permissions, 2 MiB/source, 8 MiB transaction/retention, 24 request,
30 second and rate/shared-lock limits remain. No transport or retention is activated.

Authored manifest order is preserved in its immutable identity and private plan.
Acquisition reads the primary once, then remaining members in authored order. The
existing supplied-set contract sorts original URIs for canonical storage only;
within-document text ordering and explicit continuedAt traversal are preserved.
Reordering an accepted manifest rejects replacement even when parsed values agree.
No arbitrary hyperlink grants acquisition authority. Only default-target XML/XHTML
and the existing narrow transformations/continuations are supported.

Every original has its own raw SHA, URI, receipt, filing identity and node/segment
lineage. DTS discovery uses the validated set's real reference union. Missing,
wrong-kind, cyclic or ambiguous continuations reject the candidate atomically.
A primary is not substituted as the origin of a sibling document's facts.

Version3 checkpoints contain inline_manifest, inline_manifest_sha256 and inline_keys.
Restore verifies exact version/fields, all original hashes and directory bindings,
reparses the complete set and remains PAUSED_RESTORED without transport. Existing
v1/v2 no-manifest checkpoints remain supported and are emitted as before. Unknown
versions reject. The existing private immutable writer and admission-before-publish
path are reused. Company-v2/Stock Intelligence uses existing explicit installation;
the cross-language contract includes an actual acquired multi-document collection.

Twelve adversarial integration tests cover author/canonical ordering, transformed
numbers and cross-document text, identity/schema/limits, primary/hash/directory
binding, invalid XML/IDs/chains, eight-member acceptance and byte budget, immutable
refresh, corrupt/downgraded checkpoint, cancellation/shared lock, private child-process
restore with sockets forbidden, and disk-publication failure. Existing source tests
continue to cover version1/version2 and immutable revisions. This is a bounded
acquisition package, not full HTML/inline/DRS/schema or accounting conformance.
