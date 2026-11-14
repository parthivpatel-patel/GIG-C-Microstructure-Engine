# Explicit bounded numeric restriction-definition checks

`NUMERIC_RESTRICTION_CONSTRAINTS_V5` adds declaration checks to the existing
numeric enumeration/whitespace/simple-content profiles. It supports explicit
fixed flags on totalDigits/fractionDigits only;old profiles reject those flags.
Original lexical values,booleans,restriction ancestry and source declarations
remain in proof. No default parser,acquisition profile or financial value changes.

Authority:W3C XML Schema Part2:Datatypes Second Edition,Recommendation2004-10-28,
sections4.3.7–4.3.12 (range/digit restriction constraints):
https://www.w3.org/TR/xmlschema-2/ (reviewedNovember14,2026,America/New_York).

The bounded profile checks inherited digit limits never widen,fixed digit limits
remain numerically equal,and fractionDigits does not exceed effective totalDigits.
Known integer bases retain fixed fractionDigits=0. Local inclusive/exclusive bound
pairs cannot both be declared for one side;reversed local bounds reject. Bound
lexicals must be valid for the known numeric base even when the reported fact is
nil. Equal closed endpoints are supported;equal endpoints involving an exclusive
bound are explicitly unsupported in this subset. Fixed range facets remain
unsupported rather than being partially applied. Decimal comparisons are exact.

These checks run on resolved selected-type declarations before fact/nil admission.
They do not validate all schema restrictions,inheritance range relationships,
complex content,attributes,substitution,DRS or accounting equivalence. Unknown or
empty-interval/general cases are not a full-schema-invalidity claim. No name,
presentation adjacency or approximate number creates a GAAP alias.

Twelve adversarial tests cover fixed equality/changes,legacy refusal,nonfixed
narrowing/widening,inherited total/fraction constraints,integer defaults,nil with
contradictory bounds,closed singleton/unsupported empty interval,bound base ranges,
strict boolean/unsupported fixed facets,low Decimal precision and atomic batches.
