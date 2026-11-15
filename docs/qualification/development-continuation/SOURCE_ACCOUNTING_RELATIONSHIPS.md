# Original-source accounting relationship assertions

`extract_accounting_relationships(parsed, dts, instance_raw, documents, *, manifest,
concepts, instance_uri, allow_observed=False, embedded_profile=None,
profile='SOURCE_ACCOUNTING_RELATIONSHIPS_V1')` is a new explicit, offline API. It
returns `gig.sec.xbrl.accounting_relationships.v1` with source_filing,
parsed_sha256, dts_sha256, source_audit, complete_definition_scope, networks and
sha256. It does not change default parsing, filing/statement selection or facts.

Authority independently reviewed: XBRL2.1 Recommendation31December2003 with errata
corrections20February2013, sections3.5.3.9.7.4–5,5.2.6.2.2 and5.2.6.2.4:
https://www.xbrl.org/specification/xbrl-2.1/rec-2003-12-31/xbrl-2.1-rec-2003-12-31+corrected-errata-2013-02-20.html

The normative essence-alias relationship is directed from essence to alias. Its
concept declarations must share item type/period; balance values must agree when
both are present. Requires-element instead constrains global concept occurrence,
without requiring common contexts, units or tuple locations. Essence directed
cycles are invalid; requires-element cycles are allowed. Optional essence-value
inference is deliberately not implemented by this package.

The existing original-source audit reparses the explicit plain instance and full
original DTS before any relationship is used. Permission approval, input/source
hashes, exact parsed/DTS reconstruction and receipt coverage remain prerequisites.
External linkbases and explicitly enabled schema-appinfo linkbases retain actual
containing URI/SHA and original link/arc node ordinals. No manufactured linkbase
URI or source is introduced. Only standard definitionLink/definitionArc and
locator-to-direct-item relationships are supported. Custom/unknown/XDT definition
content, unknown attributes/resources, unresolved locators and unknown direct-item
scope reject the whole explicit API. A successful report's
complete_definition_scope=true therefore cannot hide an omitted dimensional
network. No definitions produces an available empty network list, not a mapping.

Section3.5.3.9.7.4 exempts only use/priority and attributes in the XML namespace-
declaration and XLink namespaces from attribute equivalence; all other attributes
are non-exempt. In this strict standard-attribute subset, order is therefore
non-exempt. Attribute comparison uses schema value semantics after default/fixed
values: explicit1.0/+1 and the default1 compare equally, while order2 remains a
separate equivalence family. This authority was read through the public documentation
tool; a direct executor HTTP403 was not treated as a successful fetch.

Effective equivalence includes source/target and the exact normalized order value;
priority/use select effective records. Prohibition at maximum priority suppresses
the equivalent relationship; a higher optional priority can reinstate it. All
original provenance remains, including suppressed/overridden records. Source roles,
arcroles and link/arc QNames remain separate. Invalid supported essence type/period/
balance constraints and directed cycles reject rather than producing partial
mapping. The priority lexical subset remains bounded nonnegative integers.

Each active arc exposes from/to, source role/arcrole, declaration_constraints,
provenance and checks. Essence checks retain every original fact ID, lexical value,
context/unit reference and semantic hash, plus a bounded normalized reported value
for diagnostics. Different source contexts or units are never cross-joined. Original
identifier lexical spelling also fences contexts whose normalized CIK hashes collide.
Nil/dimensional/opaque/forever or unsupported type semantics stay explicit; no
representative duplicate or missing value is selected. Missing counterparts remain
missing. Conflicting duplicate or across-concept reported values remain visible.

`SUPPORTED_EQUAL` means exact reported-value agreement in the supported aspects.
For numeric facts without INF accuracy, standards_value_equality_established=false:
this package does not implement rounding-based XBRL V-Equality. Differing reported
values therefore use a conservative CONFLICTING_REPORTED_VALUES diagnostic without
claiming every such case violates full standards precision semantics. Unit conflicts
are UNSUPPORTED_ASPECTS with an explicit UNIT_SEMANTIC_CONFLICT reason. Every check
keeps selected_reported_value=null. Requires-element reports SATISFIED,
REQUIRED_ELEMENT_MISSING or NOT_TRIGGERED from global occurrence, including a
reported nil target. It neither synthesizes that target nor tests its value.

Limits reuse the source audit's2MiBoriginal instance,16original DTS documents,
8MiBcombined sources and existing XML/graph budgets. New limits are4096arcs,
64base sets,4096checks and4MiBreports. Output budgets are checked incrementally
while accumulating arc/check records. Existing bounded numeric value/restriction
validators check supported scalar lexicals and units. No source rights, transport,
retention, ledger or SDK/native format is enabled or rewritten.

Seventeen authored regressions cover exact provenance/source receipts, type/period/
balance constraints, effective prohibition/priority/order, essence/requires cycles,
missing/conflicting and duplicate facts, finite-accuracy non-inference, unit/context
separation, global required occurrence, embedded ordinals/profile gating, original
source tampering, budgets, nil source behavior, identifier lexical collisions and
empty definitions. An initial XDT negative fixture failed during legacy discovery
because its all arc omitted mandatory context placement; it was corrected to a
well-formed dimension-domain relationship, preserving the unsupported-scope
rejection assertion. A distinct-order high-priority prohibition regression preserves
the unrelated order1 relationship. Final source-audit/relationship cohort passes54tests.

This source-authored concept correspondence can support a separately explicit
statement classification, but does not invent a GAAP metric alias, infer missing
reported amounts, establish independent source authentication, prove complete
schema/DRS/accounting conformance or create a complete financial statement.

Root integration review added two source-validity regressions: actual abstract facts
and finite contexts that contradict declared periodType reject before any equality
claim;missing item periodType also rejects.19relationship checks now cover these
cases. The context-mismatch fixture uses two valid different instant periods while
retaining its original no-cross-join assertions. Full source validation/conformance
outside the stated original-byte and supported semantic scope remains unclaimed.
