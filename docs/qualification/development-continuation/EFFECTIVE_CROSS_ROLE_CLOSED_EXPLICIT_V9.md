# Original-source effective closed explicit DRS — V9

`ORIGINAL_DTS_EFFECTIVE_CLOSED_EXPLICIT_V9` adds an explicit opt-in profile and
versioned dimensional instance/inline-set schemas. Existing V1–V8 profiles, tuple
order, default selection and artifact identities remain unchanged. The actual
FilingCollection original-DTS and multi-document-inline paths pass original bytes,
permissions and source identities through this profile. Selected financials
independently validate the retained result and keep dimensional/defaulted facts out
of consolidated history. No frontend allowlist or automatic provider activation is
added; this is not full XBRL, XML Schema, Dimensions, OIM or statement conformance.

Authority is the corrected [XBRL 2.1 Recommendation](https://www.xbrl.org/Specification/XBRL-2.1/REC-2003-12-31/XBRL-2.1-REC-2003-12-31%2Bcorrected-errata-2013-02-20.html),
sections 3.5.3.9 and 3.5.3.9.5–3.5.3.9.7.5, with 4.10 value equality;
[Dimensions 1.0](https://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18%2Bcorrected-errata-2012-01-25-clean.html)
continues to bound the inherited positive closed-cube evaluator. The normative
[dimensional attribute schema](https://www.xbrl.org/2005/xbrldt-2005.xsd) supplies
boolean attribute types. Public normative documentation was consulted; no SEC or
market-data provider was contacted.

The supported definitionLink/definitionArc vocabulary fixes link/arc QNames and
arcroles. Base sets preserve role and arcrole. Equivalence requires exact endpoint
identity and all supported non-exempt attributes, including order and targetRole.
Order uses its declared default of 1 and exact decimal comparison; boolean lexical
forms compare in their declared value space. Dimensional attributes admitted via
the lax wildcard retain authored presence: an absent global attribute is not an
invented PSVI attribute use. Semantic DRS defaults do not authorize such insertion.
Distinct exact orders that collide in XPath-number space explicitly reject.

Priorities are bounded signed six-digit integers. Highest priority optional arcs
participate unless any equivalent highest-priority arc is prohibited. Equal
optional winners choose the first original source URI/node ordinal deterministically;
all alternatives and their receipts remain retained. The proof records every input
arc, source hash, original link/arc ordinal, locator labels, lexical order,
dimensional attributes, priority/use, equivalence group, chosen original index and
suppression result. Duplicate XLink from/to pairs within one original link reject,
regardless of arcrole. Surviving parallel nonequivalent relationships remain an
explicit unsupported case in the bounded cube evaluator.

Source identity is stricter than QName similarity: each endpoint must have exactly
one original schema declaration source in the correct namespace. An independent
review reproduced an otherwise accepted case in which identical declarations in
two original schema documents were merged by QName and one falsely prohibited the
other. V9 now rejects that ambiguity, including on suppressed arcs. Source-bound
schema namespace receipts cover every original schema. Supplied definitions in
normative XML/XBRL/link/dimensional namespaces reject until a separately pinned
normative-schema contract exists; they cannot replace the assumed arc types/defaults.
The consumer independently checks source coverage, hashes, namespace identities,
role/node consistency, effective selection and inherited context results. Retained
receipt consistency does not authenticate original XML bytes or the issuer; the
producer replays actual original DTS bytes before generating those receipts.

The existing V8 limits remain: 16 DTS documents, 128 role references, 64 links,
4,096 input arcs, 64 positive assignments/16 per fact, 32 dimensions/depth, global
traversal budgets and 8 MiB canonical output. Suppression does not exempt malformed
or unsupported input from validation. Negative/typed/open cubes, unusable members,
alternative base-role OR, cross-base primary inheritance, custom arc attributes and
general schema validation remain explicit unsupported cases.

Verification: 45 new authored offline tests and 75 V7/V8 regressions pass. They
cover priority/prohibition across links/documents, exact attribute equivalence,
source ambiguity, namespace replacement, re-signed proof tampering, budgets,
permissions, conflicting facts and atomic original/inline collection admission.
Nineteen representative V1–V8 artifacts and selected outputs are byte-identical to
c45e198 (including all 14 earlier V1–V7 identity examples). Initial test fixtures
used an incorrect acceptance-envelope schema and omitted the required observed-source
URL; those fixture errors were corrected without weakening production assertions.
Logs and identities: `work/effective-drs-v9/`. Run:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python -m unittest \
 terminal.stocks.test_xbrl_effective_cross_role \
 terminal.stocks.test_xbrl_inherited_cross_role terminal.stocks.test_xbrl_cross_role -v
```

SEC02 remains PARTIAL. Full source/corpus, historical and broader conformance
acceptance is not established by these bounded engineering checks.
