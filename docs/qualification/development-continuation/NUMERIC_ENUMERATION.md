# Explicit numeric enumeration schema profile

`NUMERIC_ENUMERATION_V4` adds bounded numeric `xs:enumeration` restrictions to the
existing selected-numeric corroboration path. Opt-in batch/inspection callers use
the shared numeric-profile registry. Source acquisition defaults and legacy profile
selection do not change. The previous V1/V2/V3 profiles explicitly refuse a selected
type whose derivation includes enumeration; no unknown type becomes numeric.

Authoritative basis reviewed November 13, 2026 (America/New_York): W3C XML Schema
Part2: Datatypes Second Edition, Recommendation 28 October 2004, section4.3.5 and
subsections4.3.5.3–4.3.5.5: https://www.w3.org/TR/xmlschema-2/#rf-enumeration .
Enumeration describes membership in a type's value space. Multiple members at one
derivation step form one set, and every listed member must be valid for its base.

The supported subset resolves only existing decimal/integer/XBRL numeric bases and
numeric simple-content derivations. Decimal equality is exact and independent of
the current Decimal arithmetic precision; lexical alternatives such as `1`, `1.00`
and `+001` may designate the same value. Every original enumeration lexical and
source declaration path remains in proof. No value is substituted for a reported
fact. Each ancestor's membership/range/digit constraints are enforced. Every listed
member is checked against its supported immediate base, including unused members
and declarations whose selected fact is nil. Nil remains unavailable. Conflicting
reported members remain conflicts even if each separately satisfies enumeration.

Enumeration shares the sixteen-facet ceiling per declaration, eight-level type
resolution limit, sixty-four-character numeric lexical ceiling and existing
source/type/fact/output bounds. Repeated enumeration members are legal set entries;
other repeated singleton facets retain their rejection. Nonnumeric bases, invalid
lexicals, unsupported facet structure/attributes, cycles and unknown types reject.
This narrow profile omits annotation children on enumeration elements and arbitrary
XML Schema derivations, lists, unions, patterns and general string enumeration.
It is not full schema validity, DRS conformance, accounting equivalence or proof of
statement completeness. The existing broad schema-validation flag remains false.

Fourteen authored regressions cover value-space membership, source lexicals,
same-step alternatives, inherited constraints and invalid derived members, base
lexical/range rejection, scalar facets, legacy refusal, low arithmetic precision,
nil, malformed/budgeted declarations, atomic collection admission and contradictory
reported facts. Related binding, collection, tool, statement and ingestion tests
were exercised separately. No provider, application or network source was used by
the tests.
