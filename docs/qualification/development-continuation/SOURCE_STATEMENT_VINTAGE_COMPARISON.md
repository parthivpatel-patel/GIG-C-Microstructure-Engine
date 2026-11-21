# Original-source adjacent financial-statement vintage comparison

`terminal.stocks.xbrl_statement_comparison.company_statement_vintage_comparison` is
an additive private callable export using profile
`ORIGINAL_SOURCE_ADJACENT_VINTAGES_V1` and schema
`gig.backend.statement_vintage_comparison.v1`. It independently reconstructs each
supplied acceptance cutoff through the existing original-byte source-accounting API,
then analyzes adjacent views. No HTTP route, automatic provider activation, default
switch or existing packet/schema change is introduced.

The function takes workspace, symbol, one to eight strictly increasing exact cutoff
strings, the existing original-source recipe mapping and explicit issuer role
bindings, plus optional form family and expected collection digest. The first
accepted collection digest is frozen across the cohort; a later source collection
change fails instead of publishing mixed history. Each underlying original instance,
DTS and accounting report still passes the existing source receipt, permission,
acceptance selection, explicit amendment ancestry and original-byte reconstruction
contracts. Tampered original bytes, rehashed replacements, changed taxonomy closure
and stale identities do not become admissible comparison evidence.

## Exact supported comparison

Rows are compared within the same caller-designated statement kind, exact expanded
concept QName and exact period start/end. Presentation and accounting role bindings
must remain identical. A concept-name resemblance, display position, approximate
value or relationship in another filing never maps two different concepts. A row
absent from one presentation is reported as absent from that view; it is not called
a missing issuer fact or filled from another source. Comparisons sort their own row
keys deterministically without changing the authored source envelopes or source
presentation/document order.

Both numeric rows must already be independently supported. Their original contexts
must contain exactly one equivalent aspect signature, including exact CIK, original
entity identifier lexical spelling, period, dimensions and opaque content. Different
lexical identifiers and multiple context aspect signatures do not cross-join merely
because normalized CIKs agree. Units must have identical original unit semantics.
The source concept declaration and resolved numeric type/restriction declaration
path must agree; a matching named type with changed original facets does not gain
historical equivalence. Revisions to unrelated declaration documents alone do not
invent a type change; every original source document hash stays in the full envelope.

Selected direct accounting relationship endpoints/roles and declaration constraints
must remain compatible. Changed source relationships, conflicting or unsupported
accounting aspects and unsatisfied requires-element checks remain explicit. No
cross-concept accounting alias is applied to produce a comparison value. Explicit
amendment ancestry distinguishes a supplied amendment chain from independently
selected filings; an accession/date/value change never infers an amendment edge.

For each directly participating selected presentation-role calculation network,
original source-aspect-bound interval diagnostics and relationship provenance are
retained. A definitely inconsistent supplied calculation blocks a compatible-number
comparison claim. Missing or unsupported calculations stay visible; no absent term
becomes zero and no equality is inferred from an unavailable interval. Diagnostic
coverage is the directly selected concept/network scope, not all possible issuer
accounting relationships or general OIM conformance.

Once those conditions pass, exact rational arithmetic classifies original reported
numeric values as unchanged or changed. Signed zero and distinct legitimate decimal
lexicals remain preserved while equal reported numeric values compare equally.
This says nothing about unknown underlying values, XBRL rounding-based V-Equality,
restatement acceptance or full financial-statement consistency. Every row explicitly
sets `underlying_value_equality_established:false` and
`restatement_established:false`; the original value, lexical spelling, nil, accuracy,
unit/context IDs, source fact IDs and source/parse/DTS identities stay available.

## Missing, conflicting and unavailable evidence

Conflicting and unsupported source rows are never selected. Nil/no-fact rows remain
missing, with distinct previous/current/both-missing states. Unsupported dimensions,
incompatible units/contexts/declarations and changed role/relationship authority
remain noncomparable. Existing row status/reason and original reported facts are
retained on both sides. No difference, average, estimated missing value or financial
metric is generated.

Only adjacent entries are compared. If an intermediate original or view is
unavailable, the next entry is compared against that unavailable adjacent entry;
the algorithm never skips back to the last available filing. Missing latest
originals/role bindings, unresolved ancestry and same-time selection ambiguity remain
unavailable rather than substituting an earlier source. Full source envelopes retain
all three independently designated views, their calculation diagnostics and explicit
amendment lineage. No source is merged into another.

The top-level result is `ANALYZED_BOUNDED_SUPPLIED_VINTAGES`, not a claim that history
or statements are complete. `complete_history`, `complete_statements`,
`restatements_inferred`, `values_filled`, `gaap_aliases_inferred` and
`provider_requested` are all false; `selected_reported_value` is null. The packet is
read-only. Source hashes establish supplied-byte consistency, not independent issuer
or provider authentication. Authored fixtures are not real financial observations.

## Bounds and compatibility

At most eight cutoffs, 4,096 total compared rows and 4 MiB canonical output are
allowed. Individual original-source envelopes retain their existing 256 KiB cap and
underlying XML/DTS/resource limits. The comparison counts serialized row bytes
incrementally and indexes selected source calculation membership instead of repeatedly
walking every taxonomy arc for every row. Resource excess yields no result. All
inputs/collection state remain unchanged; returned nested data is detached.

This new export is not implicitly admitted by existing 256 KiB source-accounting UI
controls. A future UI/import integration requires its own strict schema, byte and
semantic admission. Existing Company-v1/v2/vintage/history and Financial Intelligence
packet defaults and legacy artifact identities remain untouched. This package adds
historical consistency diagnostics; it does not close SEC02's complete observed
history, full conformance or corpus-backed statement-completeness criterion.

## Offline evidence

`terminal/stocks/test_xbrl_statement_comparison.py` uses actual authored original XML,
taxonomy/linkbase bytes, existing FilingCollection and source-accounting envelope
producers. It covers original/amendment and independent vintages; exact lexical,
unit/entity/period/type/restriction changes; absent concepts; missing/nil/conflicting/
unsupported rows; source relationships and required-element failures; inconsistent
and incomplete calculations; unavailable intermediate/latest sources; original/graph
corruption; source permissions; collection changes; output/row limits; eight-cutoff
ordering; deterministic results and input/return ownership. A custom-type fixture's
initial duplicate namespace declaration was corrected to a distinct authored prefix;
production assertions and source validation were not weakened.

From repository root, without application/server/provider access:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python -m unittest terminal.stocks.test_xbrl_statement_comparison -v
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python -m unittest terminal.stocks.test_xbrl_statement_comparison terminal.stocks.test_xbrl_accounting_statements terminal.stocks.test_financial_intelligence_product terminal.stocks.test_xbrl_statement_set terminal.stocks.test_xbrl_lineage -v
```

Exact logs are retained in `work/nov21-statement-comparison/`. Final integrated source,
cohort and publication SHA belong to the enclosing engineering evidence. No browser,
provider, deployment, trading, paid service or owner acceptance occurred.
