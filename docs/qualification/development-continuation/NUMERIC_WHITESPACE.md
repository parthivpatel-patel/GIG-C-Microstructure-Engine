# Explicit numeric whitespace schema profile

`NUMERIC_WHITESPACE_V3` extends the existing numeric simple-content profile with
explicit `xs:whiteSpace value="collapse"` restrictions. Only the four XML boolean
spellings for fixed are admitted. The original facet and source declaration path
are retained. Resolution must still end at an existing supported numeric base;
string types cannot become numeric. Inherited range/digit checks are unchanged.
Legacy numeric profiles explicitly reject declarations using the new facet.

Authority reviewed: W3C XML Schema Part 2: Datatypes Second Edition, Recommendation
28 October 2004, section 4.3.6 and its representation/restriction subsections:
https://www.w3.org/TR/xmlschema-2/#rf-whiteSpace (accessed November 13, 2026,
America/New_York through documentation retrieval, not a provider).

The supported normalization removes surrounding XML whitespace. Internal whitespace
remains invalid for the supported numeric lexical grammar; it is never deleted to
join separated digits. Only collapse is supported; preserve/replace, malformed
fixed, duplicate facets, foreign facet structure and nonnumeric bases reject.
Both the finite declaration-depth and numeric output budgets remain in force.
This is value corroboration for a narrow declaration family, not full schema
validity, schema-derivation validation, DRS, accounting equivalence or full XBRL
conformance. No GAAP aliases or replacement values are created. No default source
permission/profile is changed. Existing offline inspection/batch APIs discover the
new opt-in profile through their shared profile registry.

Six regressions cover exact values/source facet proof, legacy rejection, internal
whitespace, unsupported variants, inherited bounds and nonnumeric refusal.
