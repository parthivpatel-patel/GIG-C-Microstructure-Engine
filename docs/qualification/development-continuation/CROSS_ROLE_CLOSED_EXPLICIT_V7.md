# Original-DTS cross-role closed explicit cubes — V7

`ORIGINAL_DTS_CROSS_ROLE_CLOSED_EXPLICIT_V7` is an additive, explicitly selected
profile. It supports one direct positive closed hypercube with explicit dimensions
and a bounded consecutive relationship set crossing extended-link roles. It is not
complete XBRL Dimensions/schema/OIM conformance, financial-statement completeness
or independent issuer authentication. Existing V1–V6 defaults, original artifact
identities and selection policies remain unchanged.

## Authority and exact scope

The corrected normative [XBRL Dimensions 1.0 Recommendation](https://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18%2Bcorrected-errata-2012-01-25-clean.html)
was independently opened through the documentation tool. Sections 2.1.1 and
2.4–2.4.3 establish consecutive relationships and target-role partitioning; 2.7
establishes dimension-wide defaults; 3.1.3–3.1.4 establish closed-cube/context/member
constraints. [Corrected XBRL 2.1](https://www.xbrl.org/specification/xbrl-2.1/rec-2003-12-31/xbrl-2.1-rec-2003-12-31%2Bcorrected-errata-2013-02-20.html)
section 5.1.3 establishes original roleType location, role identity and usedOn rules.
Public specification review did not access any filing/market provider.

For each consecutive arc, targetRole replaces the source role for finding the next
arc kind; absent targetRole keeps the source role. It does not union both roles.
The implemented chain is `all → hypercube-dimension → dimension-domain → domain-member`.
A domain-member can itself change the role for subsequent domain members. Domain
membership uses exact expanded concept identities, and each dimension's selected
domain must be unambiguous. Directed member cycles are rejected even across roles.
Converging domain paths remain legal.

Every nonstandard target role must resolve through a roleRef in the same original
linkbase to an actual roleType within an original DTS schema. The same binding is
required for custom definitionLink source roles. The standard extended role
`http://www.xbrl.org/2003/role/link` needs no roleRef. Referenced roleTypes require a
bare resolvable ID, exact roleURI and usedOn permitting definitionLink. RoleTypes
must be direct children of appinfo within a top-level schema annotation; misplaced
lookalikes do not gain authority. RoleType declaration structure/ordering, unique
schema IDs and per-DTS unique roleURI declarations are checked. Equal duplicate
roleType declarations across schemas, though potentially legal under full XBRL
S-equality rules, are deliberately unsupported rather than guessed.

Only default-priority, optional, usable arcs are admitted. Duplicate relationship
keys reject instead of resolving precedence. Global dimension-default arcs can
appear in another role; conflicting targets reject, and a used default must be in
the selected dimension domain. An explicitly reported default value rejects.
Dimensions, original contexts and facts are never synthesized or normalized.

Unsupported scope fails explicitly: negative/open/inherited/multiple assignments,
typed dimensions, arc precedence/prohibition/unusable relationships, custom arcroles,
embedded linkbases and role declaration ambiguity. Linkbase documents for this
profile contain roleRef/definitionLink content only. Broader mixed-content DTS,
multiple dimension-domain roots and general taxonomy validation remain unsupported.
Unselected networks are retained, not claimed fully validated.

## Original-source boundary and API

Call `xbrl_dimensions.corroborate(parsed, dts, profile=CROSS_ROLE_PROFILE,
documents=original_dts_bodies, allow_observed=False, instance_uri=None)`.
Plain instances require the exact original instance URI. Inline sets use their
retained actual schema-reference union. Only original plain or inline-set schemas
are admitted, not already-derived dimensional artifacts.

Permission approval and per-source reference digests bind observed-origin inputs
before any original XML read. Every supplied schema/linkbase body is size/hash
checked and the complete discovered graph is reconstructed using retained real
roots. The canonical rebuilt graph must match all retained DTS metadata, concepts,
relationships and diagnostics. Original retained declaration/document bindings must
also match. Extra/missing/duplicate originals, changed bytes and rehashed forged
retained graphs reject. The original filing itself is not reparsed by V7: the
separate original-instance/inline source audit remains the full filing-byte audit.
Hashes and explicit processing grants do not establish issuer/provider authenticity.

FilingCollection forwards original documents, exact plain URI and observation
approval only to V6/V7 profiles; legacy call signatures remain unchanged. Failed
later batch members leave the entire collection unpublished. No provider, HTTP
route, SDK default, frontend profile allowlist or application flow is activated.

## Retained proof and consumer

Schemas are `gig.sec.xbrl.dimensional_instance.v7` and
`gig.sec.xbrl.dimensional_inline_set.v7`. `dimensional_validation` has exactly:
`profile`, `facts`, `relationships`, `role_references`,
`complete_drs_validation:false`, and `scope`.

Each fact proof retains source_fact_id, original assignment role, hypercube,
context_element, used_defaults and status `VALIDATED_RESTRICTED_CROSS_ROLE_CONTEXT`.
Relationship records retain kind, exact endpoints, source/target role, context/closed
semantics and original linkbase URI/hash/link-node/arc-node ordinals. Authored node
order is preserved within each original document; deterministic source-URI ordering
is only a receipt presentation policy. Role-reference records bind the original
linkbase digest and original target schema/roleType URI/hash/node ordinal.

`selected_financials` independently validates retained proof fields/types/source
receipts, role links, declarations, complete fact-proof membership, context semantic
identity, axis membership, selected-role domains, cycles and global defaults. It
rebuilds the expected fact proof instead of trusting a re-signed reported status.
This is retained-artifact consistency; it cannot independently recover raw XML
semantics or issuer authenticity from hashes alone. Source audit authority remains
separate. Dimensioned/defaulted facts stay excluded from consolidated financial data.

## Resource limits and evidence

Existing original-DTS limits remain: 16 documents, 2 MiB each, 8 MiB total, discovery
depth 8, 32 roots and 4,096 graph edges. V7 adds at most 64 definition links, 128
role declarations/references, 4,096 arcs, 32 cube dimensions, 2,048 role/member states
per domain, 32 traversal levels and 8 MiB retained output. Missing/unsupported content
and exceeded resource bounds remain errors.

Developer verification in `work/cross-role-v7/`: 35 focused adversarial tests pass;
259 related dimensional/instance/inline/collection/source-audit tests pass. Twelve
representative V1–V6 artifacts and selected-financial outputs are independently
canonical-identical to protected baseline `7cd99d4afd98f58330732ecfc0fd0b3303c49a3b`.
Fixtures cover role replacement, missing target fallbacks, cross-role descendants,
global defaults, directed cycles and converging paths, original role resolution and
placement, permission-before-XML, source/graph/proof corruption, malformed metadata,
32-axis/depth boundaries, two-document inline collection and batch atomicity.
These fixtures are authored offline evidence; no real filing/provider observation,
application/server, browser/device or owner acceptance was performed. SEC02 remains
PARTIAL and all external qualification blockers remain unchanged.
