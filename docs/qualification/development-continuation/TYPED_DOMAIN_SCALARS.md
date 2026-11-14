# Standalone source-bound typed-domain scalar diagnostics

`check_typed_contexts(parsed, dts, documents,
profile='TYPED_DOMAIN_SCALAR_V1', allow_observed=False)` lives in
`terminal/stocks/xbrl_typed_dimensions.py`. It returns a separate hash-bound report;
it never mutates the parsed filing, DTS, original schemas, contexts, fact IDs,
financial admission or collection. Existing ingestion and dimensional profiles
are unchanged. Root integration can explicitly request this diagnostic after
`bind_declarations`, supplying the existing original schema/DTS document records.

Authority reviewed through documentation retrieval:
XBRL Dimensions1.0 Recommendation18September2006 with corrections to25January2012,
sections2.5.2.1/2.5.2.1.1 and3.1.4.4.3:
https://www.xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18+corrected-errata-2012-01-25-clean.html

The reference must identify a nonabstract global schema element inside the DTS;
the typed member must use that exact expanded element name. Only bare global ID
fragments are evaluated. Other pointer syntax is explicitly unsupported, rather
than guessed. The profile checks source URI/SHA and rederives original global
concept/type metadata before resolving the domain. Every loaded schema must be
supplied; extra source declarations cannot be invented by recomputing graph hashes.
A mismatched original, missing target, outside-DTS target, abstract target, invalid
axis declaration, wrong domain element or invalid supported scalar rejects.

Supported domain declarations have a named explicit simple type, no unknown
attributes and no content except optional annotation. Direct xs:string preserves
its lexical text; direct xs:boolean accepts its bounded XML lexical forms. Existing
numeric simple restrictions use NUMERIC_RESTRICTION_CONSTRAINTS_V5 for exact lexical,
range, digit, enumeration and supported derivation checks. Numeric values are never
reported as financial facts. Nonnumeric custom types, anonymous types, QName values, unresolved axis substitution chains,
complex content, attributes and nil typed members remain explicitly unsupported.
The report status cannot say validated if any member has unsupported semantics.

The existing parser's raw context tree and semantic identity are retained. Reported
member_tree_sha256 values identify that original normalized tree; they are derived
hashes, not invented raw-document hashes or evidence of typed dimensional equality.
Source context IDs, original context hashes, associated source fact IDs and actual
source schema identities are retained. No whitespace-normalized replacement member,
context merge, typed equality inference, hypercube validity, relationship closure,
full schema validation or complete DRS acceptance is claimed. No typed dimension
is promoted to a consolidated line item.

Limits reuse16documents,2MiBperoriginal,8MiBtotal originals and bounded XML parsing.
Parsed/DTS inputs and emitted reports are capped8MiB;512contexts,4096facts,
32dimensions/context,4096typed records and4096characters/string scalar are enforced.
Numeric text/type-path limits remain those of the numeric profile. Original XML is
not parsed until the observed-processing gate passes; observed artifacts additionally
require explicit allow_observed and their existing parsed/DTS permission-hash binding.
No source rights, transport or storage is enabled by this checker.

Eleven authored regressions cover source/graph/context/fact identity, exact numeric
and boolean lexical validation, source-backed restrictions, string preservation,
unsupported complex/nil/anonymous/QName values, missing/wrong/abstract/outside-DTS
references, tampered source metadata, resource/profile/closure limits, observed
gating and absence of typed members. Existing instance/DTS/binding/numeric tests
rerun. All operations are deterministic and offline; no provider or application
was contacted. Full typed schemas and DRS/hypercube integration remain separate
unsupported acceptance scope.
