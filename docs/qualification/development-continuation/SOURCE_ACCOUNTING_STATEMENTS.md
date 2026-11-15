# Original-source accounting statement reconstruction V1

`company_accounting_statements(workspace,symbol,as_of,source_inputs,role_bindings,
*,form='10-K',expected_collection_sha256=None)` returns
`gig.backend.company_accounting_statements.v1`. `company_accounting_history` accepts
up to8strictly increasing explicit cutoffs and returns independent source vintages.
These are additive offline APIs;no HTTProute,provider activation or legacy/default
change. Whole latest filing selection and explicit supplied amendment ancestry are
reused. An absent current recipe is never replaced by an older filing's values.

Each source recipe supplies original plain instance bytes,manifest,explicit concept
profile,URI and original taxonomy documents. Their original parsed facts/contexts/
units/source must match the admitted immutable collection. The full graph is rebuilt
and compared with admitted graph identity when present. The new accounting extractor
then independently audits the originals and every definition relationship. Unsupported
custom/dimensional definition scope rejects rather than being stripped or relabelled.
This statement profile currently supports external linkbases/plain originals only;
the separate accounting extractor has its own explicit embedded profile.

The normative basis is XBRL2.1 corrected2013 sections3.5.3.9.7.4,4.7,4.8,5.2.5 and
5.2.6.2.2/5.2.6.2.4, linked in SOURCE_ACCOUNTING_RELATIONSHIPS.md. The role bindings
explicitly designate separate balance-sheet,income-statement and cash-flow presentation
roles plus an optional accounting relationship role per source/kind. Repeated nonnull
presentation roles reject. Designations are caller labels,not inferred GAAP roles.

Every original source presentation row retains expanded concept,type,periodType,
balance and declaration URI/SHA. A direct source essence-alias arc can additionally
classify an alias by its explicit essence concept,with full arc provenance and
checks. No relationship chain,name similarity,display adjacency,numeric resemblance
or calendar-quarter assumption creates a classification. `accounting_metric` remains
null. Multiple source essence candidates are unsupported,not arbitrarily selected.
Requires-element checks preserve global occurrence semantics;missing required rows
remain missing. No target value is inferred from an alias or another filing.

Rows are SUPPORTED,CONFLICTING,MISSING or UNSUPPORTED. Nil,zero,missing,contradictory
duplicates,units,dimensioned/opaque contexts and unsupported numeric types stay
separate. Original facts/lexical strings remain;derived numeric records bind their
source IDs. A conflicting source equivalence removes the row's projected value while
retaining both source quantities. A missing counterpart does not erase a valid
reported alias fact or manufacture the missing essence. Original/source-audited vs
admitted/declaration-bound hashes are explicitly separate fields.

`SOURCE_RELATIONSHIP_REPORTED_EQUAL` records exact reported-value agreement under an
explicit source relation. It is distinct from `SOURCE_EQUIVALENCE_VERIFIED`,which
requires the extractor's supported equality predicates,including INF accuracy for
numeric values. Full rounding-based XBRL V-Equality is not implemented. Differing
reported numbers remain conservative conflicts,even when separate rounding intervals
could overlap. Root review found that abstract/period-invalid facts could otherwise
assert equality;new regressions and fail-closed checks reject those invalid sources.
The old context-mismatch fixture now uses a valid different instant,retaining its
original missing-counterpart assertions;invalid declared periods have separate tests.

Exact calculation intervals use only supported signed-unit relationships in the
explicit presentation role. Entity identifier lexical spelling,context semantic
identity,exact period,unit and original undimensioned aspects must bind. Missing or
unsupported terms remain INCOMPLETE. Every duplicate is retained;no reported value is
selected by calculation math. Diagnostics are not accounting validity or invented
balancing values. Types/numerics use the existing bounded simple-content profile.

Limits:32source entries,2MiBinstance/8MiBtotal originals,16DTSdocuments;128concepts,
12periods,8sourcefacts per row,128terms/checks;1MiBpacket;8historycutoffs/2MiBhistory.
No period/output truncation is accepted. Returned values are detached from inputs;
all original source receipt and existing V1/V2/vintage defaults remain unchanged.
Complete statements/history and independent issuer authentication remain false.

18product tests and19relationship tests cover three roles,exact source classification,
allfour row states,required occurrence,exact/finite equality,missing/conflicting/nil
facts,incompatible contexts/units/dimensions,source corruption,whole amendments,
cutoffs/history/ambiguity,role/source/budget rejection and immutability. Seven actual
exports pass the existing strict TypeScript JSON consumer plus224source/row assertions
and7hash-tamper rejections. This is a test consumer,not a new public browser import
mode. The authored issuer/taxonomy corpus is synthetic engineering evidence,not an
observed GAAP mapping or independent issuer qualification. General accounting
reconstruction and full financial-statement completeness remain open.
