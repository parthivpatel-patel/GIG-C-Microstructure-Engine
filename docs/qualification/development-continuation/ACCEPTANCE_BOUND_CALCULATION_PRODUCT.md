# Acceptance-selected calculation exports and supplied amendment ancestry

`filing_lineage(collection, accession, as_of)` follows only explicit amendment
links in one immutable supplied collection. Every visited parsed/source identity,
issuer,form/order and exact acceptance cutoff is validated. Unknown/missing/future
parents stay unresolved without disclosing future source metadata. A resolved
supplied chain is not complete history,independent source authentication or a claim
that an amendment is additive. No date-neighbor predecessor is inferred.

`company_calculation_contract(workspace,symbol,as_of,dts_graphs,role=...,
form='10-K',rounding_mode=...,expected_collection_sha256=...)` uses the existing
latest-filing selector and exact collection identity. Competing latest filings,
missing original DTS and unresolved supplied ancestry remain unavailable. The
explicit accession-to-full-DTS mapping is never replaced by an older filing or
abbreviated retained proof. A matching graph is passed to the source-bound binder;
its original source/fact/context/unit/network provenance remains in the signed
export. This adds a separate API;existing Company-v1/v2 defaults remain unchanged.

Schema `gig.backend.company_calculations.v1` is an offline export capped256KiB.
Stock Intelligence's supplied-XBRL panel now contains a separate named file control
and exact-diagnostic table. Client admission verifies envelope/child/lineage hashes,
issuer/cutoff/collection/source links,point identities and exact signed interval
arithmetic with endpoint closure. Unavailable and missing inputs remain visible.
The UI never selects a financial fact or fills a statement row. No HTTP mutation,
provider fetch,server,automatic configuration or source-retention activation exists.
Unknown identity disables the control;stale symbol/load completions cannot replace
newer state. Current schema/math restrictions remain explicit and conservative.

Six lineage plus seven product tests cover originals/amendments,missing/future/
unknown ancestry,same-time ambiguity,stale collection and output bounds,wrong/missing
DTS,no older-source substitution,exact cutoff instants and deterministic identity.
Actual Python-to-TypeScript checks cover4exports and9adversarial rejections,including
re-signed interval/provenance tampering and stripped amendment ancestry. Two actual
leaf SSR tests exercise naming,read-only disclosure and unknown-issuer disablement;
no application/server/browser is started. These checks do not establish full OIM,
Calc1.1,accounting equivalence,complete statements or physical-device acceptance.
