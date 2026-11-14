# Explicit source-bound calculation report

`bind_calculation_report(parsed, dts, *, role=None,
rounding_mode='round-to-nearest')` in xbrl_calculation_report.py returns
`gig.sec.xbrl.calculation_report.v1` under SOURCE_BOUND_CALCULATIONS_V1.
The original parsed artifact and full original DTS graph are explicit inputs.
An abbreviated retained declaration proof cannot replace the graph needed to
revalidate its canonical identity. Plain originals, inline document sets and their
existing declaration-bound versions are accepted; no collection/default product
behavior or source activation changes.

The binder verifies canonical input/source/DTS/effective-relationship identities,
context/entity/period and unit semantic hashes, original source fact IDs, known
source document hashes and declaration/arc provenance. Inline set original filing
identities, aggregate set identity and each original fact segment are checked.
A previously bound artifact cannot silently switch DTS. One calculation role must
be explicit or uniquely identifiable, usable and supported. Unknown/ambiguous roles,
unsupported effective networks, unclosed dependencies and unknown source semantics
reject. The legacy NON_PRESENTATION_LINK_NOT_INTERPRETED diagnostic is allowed only
because the independently checked effective graph handles that calculation content.

Data points bind by exact expanded concept plus context and unit semantic identity.
Source aliases for equal contexts or units group without losing original references.
Different entities, periods or units never join. Numeric extensions require supplied
item declarations, compatible period, supported numeric type/facets and original
lexical-value corroboration. Their derived numeric diagnostics do not replace raw
source values, create GAAP aliases or infer accounting equivalence.

Each parent binding retains context/entity/period/unit aspects, all duplicate source
facts, exact math, missing-concept diagnostics and effective arc provenance. Every
reported value remains available; selected_reported_value is null. Missing
contributions remain INCOMPLETE, not fabricated zeros. Conflicting duplicate display
policies and existing statement outputs remain unchanged. Modes remain explicit
and consistent throughout each report.

Authority reviewed: XBRL International Calculations1.1 Recommendation22February2023
with errata to14February2024, sections3.2,4.1,5.1–5.7:
https://www.xbrl.org/Specification/calculation-1.1/REC-2023-02-22%2Bcorrected-errata-2024-02-14/calculation-1.1-REC-2023-02-22%2Bcorrected-errata-2024-02-14.html
The opt-in application of interval math to supported legacy summation-item arcs is
explicit; this report is not the legacy calculation result or full standards
conformance. Existing legacy calculation APIs remain available independently.

Supported boundary: one existing standard effective calculation role, signed-unit
weights, plain decimal numeric items, exact matched undimensioned contexts, and no
DTS definition/default networks. Dimensioned/typed/opaque/forever contexts are
explicitly excluded. Definition/default relationships and unsupported source nodes
reject rather than imply OIM alignment. General XDT/OIM compatibility, arbitrary
arcroles/weights, date-time conversion rules and complete report conformance remain
unsupported. Integrity hashes are not independent source authentication.

Limits:8MiB per input artifact,16DTS documents,64networks,4096arcs/facts,
512contexts,128units,8duplicates/data point,128terms/parent,128result bindings and
4MiB output. Existing exact-number/exponent constraints apply. Exceeding output or
input bounds rejects; no partial/truncated acceptance is published.

Twenty authored adversarial tests cover original/bound/inline lineage, exact maths,
context/unit aliases and incompatibility, duplicate conflicts/excess digits/nil,
rounding modes, dimensions/unknown semantics, source/graph/arc corruption, ambiguous
roles, definition/default refusal, unsupported extension types, output ceilings and
unchanged legacy product disclosures. No application/server/provider or paid source
was used. Product integration remains an explicit caller operation.
