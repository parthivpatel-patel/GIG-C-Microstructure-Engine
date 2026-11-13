# Closed reported-accuracy enclosures V1

`CLOSED_REPORTED_ACCURACY_V1` uses exact decimal/rational arithmetic. For supported
canonical reported values v and finite decimals d, q=10^(-d) and the conservative
closed enclosure is [v-q/2,v+q/2]. INF is the exact point [v,v]. For nonzero values
with finite precision p, d=p-1-floor(log10(abs(v))); this is computed from the exact
decimal exponent, never a binary logarithm. Positive/negative weights reverse
interval endpoints correctly. A calculation is definitely inconsistent within this
profile only when parent and weighted-sum enclosures are disjoint. Touching closed
endpoints are conservatively compatible. Compatibility does not prove an exact
underlying accounting value or full XBRL/Calculations conformance.

The implementation deliberately does not resolve ambiguous rounding/tie conventions.
Reported values with digits outside the declared quantum are unsupported rather
than implicitly rounded to a different number. Finite precision at zero is explicit
unsupported behavior;zero with decimals or INF is supported. Missing accuracy,nil,
missing terms and unknown/conflicting duplicate values never become exact zeros.
Equal numeric duplicates intersect supported enclosures and preserve every fact ID;
unknown accuracy on one duplicate is not silently supplied from another duplicate.
Differing duplicate values remain conflicting even if their enclosures overlap.

Both accuracy attributes together,invalid lexical declarations,invalid nil/value
pairs and malformed numbers reject. Legitimate declarations beyond the bounded
exponent profile are unavailable,not guessed. Exponents are bounded to +/-128,
numeric strings to80characters,duplicates to8 and calculation terms to128.
Signed-unit weights are supported;others reject. Rational inputs/outputs preserve
numerators and denominators as strings. No Decimal context or float rounding can
change the endpoints.

Reference: XBRL2.1 section4.6.3 numeric facts/accuracy and section5.2.4 calculation
relationships in the published recommendation linked in XBRL_EFFECTIVE_RELATIONSHIPS.md.
This is a restricted conservative interval profile,not an implementation of every
XBRL2.1/Calculations1.1 duplicate/rounding rule or fresh online specification review.
No provider,source corpus,browser or empirical accounting validation is implied.

Initial16authored primitive tests passed in accuracy-primitive-first.log. They
include exact endpoints,negative weights,boundary contact,large/small values,
precision derivation,unsupported declarations,nil,missingness,duplicates and
independence from Decimal's current precision. Later integrated evidence is in
the current REPORT.md and evidence manifest.
