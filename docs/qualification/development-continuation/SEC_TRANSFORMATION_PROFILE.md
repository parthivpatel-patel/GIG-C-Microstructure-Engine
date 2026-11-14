# Explicit acquired numeric transformation profile

`FilingIngestor.ingest(..., inline_manifest=...,
transformation_profile='REGISTRY_2015_NUMERIC_V2')` now propagates the selected
bounded numeric transformation contract through complete-set discovery, strict
collection ingestion, immutable source interpretation and offline recovery. The
selector is optional. Unknown/non-string selectors reject before transport. A
nondefault profile requires an explicit hash-bound inline acquisition manifest;
automatic primary discovery cannot silently widen interpretation.

Both successful admission and restoration use the same original-document manifest,
source hashes, receipts, schema-reference union, exact transformed values and raw
segment provenance. Source/transaction/request/time/set/node limits are unchanged.
No permission, config default, startup hook, transport or source retention is enabled.
No independent official-source authentication is inferred from a supplied manifest.

Collections containing a selected profile emit explicit checkpoint version4. The
profile is retained per filing plan and restored only with its known selector and
manifest. Exact version/plan consistency and parsed collection identity are checked.
Missing/unknown/null interpretation metadata, version downgrade, stripping a profile
from otherwise compatible sources, and corrupt manifest bindings reject atomically.
Version1/version2/version3 no-profile formats remain supported and are emitted as
before. A refreshed accepted filing cannot gain, drop or change interpretation
profile; it rejects before new transport reads and preserves accepted state.

Thirteen authored regressions exercise acquired Indian numerics and explicit zero
dash, source/transform lineage, legacy refusal, strict pre-I/O admission, immutable
profile addition/removal, version4 paused restore without transport, existing
version3/default emission, corrupted metadata/version/manifest, interpretation
stripping, private child-process restore with sockets forbidden, cache/receipt
idempotency and one/eight-document acceptance without duplicate reads. Existing
source/private-store fixtures retain failure/cancellation/lock and version1/version2
coverage. This is bounded numeric interpretation, not full inline/schema/accounting
conformance, observed financial coverage or provider acceptance.
