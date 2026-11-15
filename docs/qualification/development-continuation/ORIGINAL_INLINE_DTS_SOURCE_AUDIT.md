# Original-byte inline set and DTS reconstruction audit

New explicit API in xbrl_dts_source_audit.py:

```
audit_inline_dts_sources(parsed, dts, inline_documents, taxonomy_documents,
    concepts=concepts, acquisition_manifest=None,
    expected_acquisition_manifest_sha256=None, transformation_profile=None,
    allow_observed=False, embedded_profile=None)
```

This separate profile is ORIGINAL_INLINE_SET_DTS_SOURCE_AUDIT_V1, receipt schema
`gig.sec.xbrl.inline_dts_source_audit.v1`. Existing plain audit, legacy binders,
source/collection/product defaults and all original identities remain unchanged.
The caller supplies every original XHTML byte stream with its original URI and
complete existing source manifest, explicit concept/transform/embedded choices,
and every original taxonomy/linkbase body with URI/SHA. No source is fetched.

Every original's processing permission, raw hash, filing identity, URI and receipt
is checked before any XML parse, including taxonomy parsing. All original descriptors
must exactly match the retained document-set metadata. Changing an approval reference,
receipt, acceptance instant, URI or raw digest cannot silently reparse under an old
artifact. Observed original permission references are matched in the parser's
canonical URI order and are represented only by hashes in receipts. Plaintext
processing references and original document text are never exported.

The audit reparses the full original inline set using the explicit existing parser.
Supported passive text interleaving, cross-document continuation chains, numeric
transformations, nil, original node/segment/source hashes, contexts and units must
reconstruct the exact canonical original artifact. Bound/derived artifacts are not
substitutes. Selected transformation profiles must exactly match immutable retained
profile metadata, including absence under the legacy default. The actual reference
union then reconstructs the full original DTS with exact source-body coverage.
Unresolved, missing, extra, duplicate, overlapping-role or changed taxonomy originals
reject. Rehashed facts, traces, contexts, units, declarations, types, source references
and supported/unsupported graph diagnostics must still match original reconstruction.

Acquisition intent is distinct from a canonical parsed set. Parsed sets retain
URI-sorted original metadata, not the authored acquisition-list order. Therefore
optional acquisition_manifest requires its independently retained accepted
expected_acquisition_manifest_sha256, such as the existing immutable checkpoint
plan digest. Document membership/order/primary/prefix/body hashes must agree with
that intent. An altered manifest cannot establish its old identity merely by
self-hashing. Pure set reconstruction may omit both acquisition arguments; its
receipt distinguishes supplied_document_order from parsed_document_order and makes
no claim that supplied order was originally accepted acquisition intent.

The API returns only source/parse/graph/profile/manifest identities, per-original
receipt metadata, source fact/context/unit hashes, exact taxonomy body hashes and
explicit limitations. It does not activate permissions/storage, authenticate an
issuer, create observed coverage, prove accounting equivalence or claim full
inline/schema/DRS/calculation conformance. Existing semantic diagnostics are preserved,
not silently waived. This is reconstruction under existing supported contracts:
INLINE_DOCUMENT_SETS.md, MULTIDOCUMENT_ACQUISITION.md,
INLINE_REGISTRY_NUMERIC_V2.md and SEC_TRANSFORMATION_PROFILE.md. Their authoritative
specification references and explicitly bounded semantics remain applicable.

Limits:1–8originals,2MiB/original,1–16taxonomy documents,8MiB combined original bodies,
8MiB parsed artifact,16MiB graph and1MiB receipt, plus unchanged parser/node/text/
continuation/transform/dependency-depth limits. Bounds reject without partial output.
No new source-format or registry support is implied by a successful audit.

Twenty-two new adversarial tests cover complete original reconstruction, approved
observed permissions/privacy, per-original receipts, manifest/order/primary binding,
legacy/selected transformations, one/eight originals, continuation/ID/XML/entity
failures, exact taxonomy closure, source/body/artifact corruption, canonical-rehashed
metadata forgery, concept choices, bound/derived refusal, embedded-profile parity,
limits and forbidden sockets. Forty-five focused inline/plain audit tests pass.
The only initial test failure was a fixture attempting augmented assignment through
a tuple slot while building a count-limit input; it now extends that contained list
without weakening the count assertion or changing production behavior.
