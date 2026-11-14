# Bounded opt-in Registry3 numeric transformations

`parse_document_set(..., transformation_profile='REGISTRY_2015_NUMERIC_V2')`
and `FilingCollection.ingest_inline_set_batch(..., transformation_profile=...)`
add an explicit numeric registry profile. The default supplied-set parser, plain
inline parser, collection defaults and automatic acquisition profile stay unchanged.
Explicit manifest-backed acquisition can select it via transformation_profile; see
SEC_TRANSFORMATION_PROFILE.md. Automatic/default acquisition stays unchanged.

Authority reviewed November 13, 2026 (America/New_York): XBRL International,
Transformation Rules Registry3, Recommendation26 February2015, input datatype and
numeric transformation definitions:
https://www.xbrl.org/Specification/inlineXBRL-transformationRegistry/REC-2015-02-26/inlineXBRL-transformationRegistry-REC-2015-02-26.html

The opt-in profile accepts decimal-dot and decimal-comma numeric grouping using
ordinary/no-break spaces and XML whitespace collapse, Indian decimal-dot grouping,
and a documented set of single-dash zero representations. Formatting remains
namespace-exact. It rejects signs/exponents in transformed input, invalid grouping,
unsupported dash characters/functions/namespaces, and malformed profile selectors.

Supported dash codepoints: U+002D, U+058A, U+05BE, U+2010–U+2015,
U+FE58, U+FE63 and U+FF0D. A zero exists only from an explicit supported zerodash
format applied to a reported valid character. Nil stays unavailable; empty/missing
text is never silently zero. This is a bounded Registry3 subset, not complete
transformation-registry or Inline XBRL conformance.

Transformation output then receives existing exact integer scale and sign handling,
without Decimal-context rounding. Original extracted text, expanded format QName,
raw document/segment identities and transformed lexical value remain in provenance;
explicit new profile metadata appears only when requested. Existing source, set,
node, text, numeric precision/scale, trace and output limits stay enforced.

Twelve authored regressions include valid/invalid grouping, XML and no-break-space
normalization, exact low-precision arithmetic, registered dash subset and rejection,
legacy refusal, source provenance, nil, unsupported namespaces/profiles, resource
limits, unchanged supported numeric values, collection propagation and atomic batch
failure. No provider or application was contacted/launched; no accounting alias or
source coverage is inferred.
