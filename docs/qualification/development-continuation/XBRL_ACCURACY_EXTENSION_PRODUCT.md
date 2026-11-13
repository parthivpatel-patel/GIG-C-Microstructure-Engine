# Opt-in accuracy and source-scoped extension statement profile

`accuracy-extension-v2` returns `gig.sec.xbrl.statement_view.v2` inside
`gig.backend.company_xbrl.v2`. The original v1 schemas and default behavior remain
unchanged. New consumers must explicitly request this profile. Old consumers
reject its schema rather than silently ignoring new interpretation policy.

The v2 view reuses exact filing/form/role/cutoff selection from v1. All filing,
amendment,source receipts,original document/set hashes and relationship provenance
remain. It exposes exact source contexts/units,including dimensioned contexts that
remain excluded from consolidated statements. No missing data or initial source
state is synthesized. Output is bounded by the same final256KiB ceiling.

Company extensions are mapped to their actual supplied presentation role,root and
incoming relationship indices. Declaration source documents and exact QNames remain.
The mapping is deliberately structural,not accounting equivalence. `accounting_metric`
is null,even for an extension named Assets or Revenue. No name similarity,role name
or adjacency can create a companyfacts metric,ratio input or standard taxonomy alias.
Full hierarchy,order,preferred-label role and arc provenance remain in relationships.

Numeric promotion requires an exact supplied declaration,known numeric base or
supported named derivation/facets,ordinary item substitution,matching period,
validated unit and non-opaque/non-dimensional context. Unknown types/substitution
or DRS scope are explicit unavailable states. Malformed numeric values,invalid
facets or illegal nil declaration reject the opt-in request atomically. Standard
selected-fact/default exclusions are never overridden. Extension DRS consolidation
is unsupported if definition relationships are present or the declaration proof
predates the explicit definition-scope flag.

Original unverified extension fact objects keep value=null and their original
IDs. Separate `numeric_facts` records bind the derived exact lexical interpretation
to the original ID,concept,filing accession,parsed instance hash and resolved type.
Only those explicit derived records authorize REPORTED_EXTENSION display. Source
facts are not relabeled or overwritten. Missing,nil,conflicting and multiple-unit
facts remain unavailable. Current companyfacts and numerical ratios are unchanged.

Row accuracy uses CLOSED_REPORTED_ACCURACY_V1 (see XBRL_ACCURACY_V1.md). Calculation
status is ROUNDING_COMPATIBLE,DEFINITELY_INCONSISTENT,INCOMPLETE,UNSUPPORTED_ACCURACY
or UNSUPPORTED. Exact-value residuals are separate diagnostics. Every interval and
term retains original fact IDs;negative weights swap endpoints. Boundary contact
is conservatively compatible,not proof of full XBRL validity or observed accuracy.
Missing/unknown accuracy is never replaced by infinite precision. The finite
base-ten interval grid and all exponent/term/duplicate limits are explicit.

API: existing read-only `/api/v2/companies/{symbol}/xbrl-statements` with query
`at=...&role=...&form=10-K&profile=accuracy-extension-v2`. No query acquires a source.
No new upload,provider or execution permission exists. Invalid/duplicate queries
continue to reject. Private offline export adds `--statement-profile accuracy-extension-v2`
to the existing inspect command alongside --company-symbol and --statement-role.
Source permission/hash/path/new-only0600 export safeguards are unchanged.

Full accounting mappings,complete statements,arbitrary DRS,full XML Schema and
source coverage are NOT established by this profile. It is an implemented
source-scoped research view,not automatic authorized filing/DTS acquisition.
