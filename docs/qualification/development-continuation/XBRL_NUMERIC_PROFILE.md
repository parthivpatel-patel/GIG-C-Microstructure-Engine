# Supplied-taxonomy numeric value profile — November 12, 2026

`NUMERIC_VALUE_FACETS_V1` is an explicit, offline selected-fact corroboration
profile. `FilingCollection.ingest_dts_batch(entries,numeric_profile=...)` requests
it. The default remains declaration-only ingestion; no existing caller silently
acquires a full-schema claim. No URI is fetched or source permission activated.

The supplied DTS graph now retains named simple restriction declarations and
source-document identities. The profile resolves at most8named restrictions,
rejects cycles, and validates selected values against supported XML Schema
integer/decimal or standard XBRL decimal,monetary,shares,pure and selected integer
item types. Decimal parsing and comparisons do not depend on Decimal precision.
XML whitespace,integer lexical/range boundaries and known standard unit forms
are checked. Monetary units require an ISO4217 QName with a three-letter code;
this does not validate an authoritative currency registry or perform conversion.

Supported restriction facets:minInclusive,maxInclusive,minExclusive,maxExclusive,
totalDigits,fractionDigits. Every inherited supported facet is applied. Digit
counts describe decimal values,not redundant lexical leading/trailing zeros.
Unknown/custom complex types,patterns,lists/unions,fixed facets,unsupported
attributes and substitution-group chains reject when selected by this profile.
They remain explicit unvalidated metadata under declaration-only ingestion.
Nil retains missingness and existing nillable admission,not a numeric zero.

This checks numeric values against the retained supported restrictions. It does
not establish complete schema construction/derivation validity,all attribute
constraints,DRS/hypercube validity,accounting semantics or complete statements.
`schema_type_validation` and `complete_statements` remain false. The existing
explicit concept/period/unit profile still controls financial selection.
Unverified concepts remain unselected. Contradictions in any entry reject the
whole candidate collection. Inputs,source-byte SHA,acceptance/receipt timestamps,
amendment lineage and exact numeric lexical values remain unchanged.

Limits:128named types per DTS,8restriction levels,16facets per restriction,
64-character numeric/facet lexical values,existing16documents/8MiBbatch/4096facts
bounds. Numeric evidence has an8MiBoutput bound checked before accumulating each
record and again after final metadata assembly. Duplicate/conflicting type
identities,unsupported selected types and corrupt hashed inputs fail closed.

## Offline command-line use

The existing `scripts/inspect_xbrl_instances.py` also accepts a new explicit batch:

```json
{
  "schema": "gig.sec.xbrl.input_dts_batch.v1",
  "issuer_cik": "0000320193",
  "origin": "HISTORICAL_SYNTHETIC",
  "numeric_profile": "NUMERIC_VALUE_FACETS_V1",
  "entries": [{
    "path": "instance.xml",
    "manifest": "SUPPLY_THE_EXISTING_COMPLETE_SOURCE_MANIFEST_OBJECT",
    "gaap_namespace": "http://fasb.org/us-gaap/2024",
    "instance_uri": "https://authored.invalid/instance.xml",
    "documents": [{"path":"taxonomy.xsd","uri":"https://authored.invalid/authored.xsd","sha256":"SUPPLY_INDEPENDENT_DOCUMENT_SHA256"}]
  }]
}
```

The manifest/hash placeholders above are explanatory,not executable source
admission. Use an authored fixture or a separately authorized supplied copy.
`numeric_profile:null` explicitly selects declaration-only corroboration.
All paths are relative to the batch directory;traversal,symlinks,unknown keys,
changed source digests and oversize batches reject. The original input_batch.v1
contract remains accepted. Existing permission gates apply before processing
observed XML;this command grants no dataset rights.

```bash
<venv>/bin/python scripts/inspect_xbrl_instances.py --batch <private-batch.json> --as-of <exact-cutoff> --output <new-private-result.json>
```

Results retain document/fact/type provenance in existing acceptance-time export
coverage. Summary stdout contains counts/classification,not raw facts or private
configuration. Failed validation does not create the output. Existing exclusive
0600 output-file semantics remain unchanged. No application/server is started.

## Specification and evidence boundary

The bounded rules refer to W3C XML Schema Part2 datatype/facet definitions:
https://www.w3.org/TR/xmlschema-2/#decimal ,
https://www.w3.org/TR/xmlschema-2/#integer ,
https://www.w3.org/TR/xmlschema-2/#rf-totalDigits and
https://www.w3.org/TR/xmlschema-2/#rf-fractionDigits . XBRL2.1 numeric item/unit
rules are a separate specification layer;custom schema/DRS validation is not
inferred from these value checks. These references identify the profile's rules;
no fresh official-specification download or provider qualification is claimed.
Tests are independently authored XML/value expectations,including original
failing-before UTC/context defects,integer limits,facets,cycles,identity,
permission,atomicity,budgets,CLI paths and original API compatibility.
