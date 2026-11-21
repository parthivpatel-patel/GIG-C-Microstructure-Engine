# Original-DTS inherited closed explicit hypercubes — V8

`ORIGINAL_DTS_INHERITED_CLOSED_EXPLICIT_V8` is a new explicit profile. It combines
multiple positive closed explicit hypercubes and supports transitive primary-item
inheritance within one preserved original has-hypercube base role. Consecutive
cube/dimension/domain relationships can cross roles using the existing V7 original-
DTS targetRole contract. It does not claim complete Dimensions, XML Schema, OIM,
accounting, statement/history completeness or independent issuer authentication.
V1–V7 schemas, defaults, original artifact identities and selection behavior remain
unchanged; no frontend allowlist, provider or application activation is added.

## Normative authority and bounded semantics

The corrected [XBRL Dimensions 1.0 Recommendation](https://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18%2Bcorrected-errata-2012-01-25-clean.html)
was independently opened through the public documentation tool. Sections 2.6 and
2.6.1 establish transitive primary inheritance and preservation of the original
has-hypercube base set, DRS, contextElement and closed semantics. Section 3.1.2
establishes conjunctive positive-cube validity within that base; 2.4 establishes
targetRole transitions; 2.7 establishes global defaults. Sections 3.1.3–3.1.4
establish each individual cube/context/member constraint. No provider data was used.

Full Dimensions also permits inherited relationships found through primary networks
in other base sets and alternative valid has-hypercube base sets. V8 deliberately
rejects these broader interpretations. All supplied all relationships must belong
to one original base role. A selected fact's primary ancestors must be reached only
through domain-member arcs that stay in that preserved role. A nonlocal incoming
primary relationship is an explicit unsupported result, not an implicit role union
or an invented AND/OR over alternative bases. The cube/dimension/domain chain itself
retains exact V7 targetRole replacement, including changes between roles.

For each original fact, the producer finds its direct and transitive ancestors,
then finds all positive closed assignments belonging to those exact concepts.
Shared ancestors in a diamond apply once. All applicable cubes must validate; a
valid direct cube cannot hide an invalid inherited cube. Each closed cube validates
against the original reported dimensions separately. The union of cube axes cannot
make an extra reported dimension valid. Different unreported default axes can be
merged only after each individual cube validates. Global defaults never add members
to a domain, and explicit defaults remain invalid. Both the assignment source and
the inherited fact itself are checked against primary-item polymorphism.

Only explicit dimensions, default-priority optional usable arcs and one shared
context container per fact are supported. Negative/open/typed/effective-precedence,
mixed-container conjunction, alternate-base OR, cross-base primary inheritance,
empty-cube and ambiguous-domain interpretations remain explicitly unsupported.
V7's strict original roleRef/roleType/schema/location rules and restricted original
linkbase contents remain. This supported subset is not full taxonomy validation.

## Source boundary and retained proof

Call `xbrl_dimensions.corroborate(parsed, dts,
profile=INHERITED_CROSS_ROLE_PROFILE, documents=original_dts_bodies,
allow_observed=False, instance_uri=None)`. Plain originals require their exact
original URI; inline sets use the retained actual schema-reference union.

The V7 original-source preflight and full canonical DTS replay are reused without
modifying V7. Exact declared observation approval and source processing-reference
digests are checked before XML; all raw original hashes, membership, graph metadata,
concept declarations, role definitions and reference roots must reconstruct.
Missing/changed/duplicate originals and rehashed false retained graphs reject. V8
replays original DTS bodies, not the filing itself; the separate original filing
or inline audit remains that original-byte authority. Hashes/grants do not establish
issuer or provider authentication.

Schemas are `gig.sec.xbrl.dimensional_instance.v8` and
`gig.sec.xbrl.dimensional_inline_set.v8`. The dimensional proof contains exactly
profile, facts, relationships, role_references, complete_drs_validation:false and
scope. Original raw relationship/role-reference receipts retain V7 shapes and
original authored node order. Conjunctive fact details use a canonical semantic
order; this does not rewrite original source semantics or source receipts.

Each fact proof contains source_fact_id, original base role, context_element,
used_defaults, primary_ancestors, assignments and status
`VALIDATED_RESTRICTED_INHERITED_CROSS_ROLE_CONTEXT`. Each assignment contains exact
primary_item, hypercube, context_element, closed:true, used_defaults, inherited,
source_uri and source_arc_node_ordinal. Original facts, values, units, contexts,
source IDs and filing receipts are unchanged. An inherited relation never creates a
new reported fact or accounting equivalence.

The selected-financials consumer validates retained URI/hash/role/ordinal fields.
Distinct relationships cannot claim the same original arc node, one extended-link
node cannot carry conflicting roles, and one original schema/roleType node or URI
cannot carry conflicting role/type identities. Reusing the same original roleType
consistently from separate linkbases remains valid. The consumer rebuilds complete ancestry, each applicable assignment, cube/domain membership,
context semantics and aggregate defaults. Re-signed missing/duplicate assignments,
false ancestors, changed direct/inherited labels and provenance mismatches reject.
Retained-proof consistency cannot recover original XML or authenticate an issuer
from hashes; the producer's original-body replay remains separate. Dimensioned or
defaulted facts stay excluded from consolidated financial metrics. FilingCollection
passes originals/permissions/URI only for V6–V8 and commits a whole batch atomically.
Legacy collection signatures and defaults are unchanged.

## Resource bounds

Existing original-DTS/XML limits remain: sixteen documents, 2 MiB per document,
8 MiB total, eight discovery levels, 32 roots, 4,096 edges, 64 definition links,
128 role declarations/references and 4,096 retained arcs. V8 permits at most 64
positive assignments globally and sixteen applicable assignments per fact. Cube
and combined fact axes stay bounded to 32. Each domain and primary ancestry has
at most 2,048 states and 32 levels. Cached traversals additionally have independent
total limits of 32,768 domain states and 32,768 primary states. Retained output is
bounded to 8 MiB. Limits raise errors; none silently truncates evidence.

## Developer evidence and remaining work

`work/cross-role-v8/focused.log`: **40 focused tests pass**, covering direct/inherited
conjunction, diamonds, failed second cubes, distinct closed axis sets, global/default
membership, multiple source facts, source preservation, per-fact/global/depth budgets,
original permission/hash/graph replay, re-signed proof corruption, two-document inline
collection and batch atomicity. Three impossible original-node bindings were
independently reproduced as accepted by the pre-repair V8 consumer, then rejected
by the strengthened receipt checks; the pre-repair receipt is retained in
`work/cross-role-v8/source_projection_before.json`. The authored-order fixture was corrected to compare
the same original assignment's node ordinal after reordering, rather than the ordinal
at the unchanged first list position; no production assertion was weakened.

`work/cross-role-v8/related.log`: **294 related V1–V7 dimensional, instance, collection,
inline, calculation and original-source audit tests pass**. Fourteen representative
V1–V7 artifacts and selected-financial outputs are independently canonical-identical
to `6e9713d6a4584569b7c4268a15a01146e4dd0162`; exact hashes and the isolated baseline
comparison helper are in `work/cross-role-v8/legacy-identities.json` and
`legacy-artifacts.py`.

These authored fixtures close a bounded engineering subcriterion only. General
cross-base inheritance/alternative-base evaluation, broader DRS/OIM/schema/calculation
conformance, source-backed complete statements/history and all actual provider,
physical-target and owner acceptance remain unqualified. SEC02 remains PARTIAL.
No application/server, live provider, deployment, trade, paid resource or owner
acceptance was used.
