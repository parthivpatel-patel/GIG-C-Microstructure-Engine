# Additive exact calculation-interval profile

New math APIs in xbrl_accuracy.py: `calculation_enclosure`,
`calculation_duplicates` and `calculation_consistency`. They use explicit
`rounding_mode='round-to-nearest'` or `'truncation'` under profile
EXACT_CALCULATION_INTERVALS_V2. Existing enclosure/duplicates/consistency APIs,
statement selection, displayed facts and defaults remain unchanged.

Authority reviewed for this package: XBRL International Calculations1.1,
Recommendation22February2023 with errata to14February2024, sections5.2–5.7:
https://www.xbrl.org/Specification/calculation-1.1/REC-2023-02-22%2Bcorrected-errata-2024-02-14/calculation-1.1-REC-2023-02-22%2Bcorrected-errata-2024-02-14.html
Documentation access only;no report/provider connection.

Rounded enclosures include both endpoints. Truncated positive/negative enclosures
exclude the endpoint away from zero;zero excludes both endpoints. Infinite accuracy
is a closed point. Arithmetic preserves endpoint closure under signed finite-decimal
weights, addition, subtraction and intersection using exact Fractions. Zero weights,
nondecimal grids, mode mixing, duplicate contributing concepts and malformed/budget-
exceeding intervals reject. Existing numeric/exponent and source-count bounds stay.

Each duplicate source value and identity remains visible. An intersection is a
calculation constraint, not a selected or synthesized reported financial value.
`selected_reported_value` is always null. Differing source values remain differing;
the legacy fact-conflict policy is unchanged. Disjoint duplicates and excess digits
make calculation unavailable with source error diagnostics. Noncanonical reported
accuracy is never silently rounded/truncated into a replacement fact. Nil/mixed nil,
missing accuracy and precision-attribute inputs remain explicitly unavailable in
this decimals-based profile.

Scope is interval math for already bound compatible data points. Callers must first
establish concept/entity/period/unit/dimension compatibility and supported effective
relationships. This helper does not establish OIM compatibility, select networks,
validate units/periods, promote extension concepts, or claim full Calc1.1/report
conformance. Automatic product/source calculation selection remains unchanged.

Nineteen authored tests cover both modes, boundary-only overlap, signed/fractional
weights, zero, exact point intervals, duplicate source preservation/intersections,
excess digits and missingness, malformed/mixed-profile inputs, resource identities,
low Decimal-context precision, extreme decimal grids and an independent rational
lattice witness oracle. No GAAP alias, inferred accounting equivalence, missing zero,
provider evidence or observed-value substitution is introduced.
