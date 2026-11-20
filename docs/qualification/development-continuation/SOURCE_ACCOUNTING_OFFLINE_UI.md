# Private source-accounting and inline-original evidence UI

`SourceAccounting.tsx` adds two independent, explicitly selected local-file imports
within the existing Financial Intelligence/Stock Intelligence XBRL panel. The mount
is keyed to the exact symbol/CIK pair. No request, route, provider activation,
application/server launch or legacy profile switch is introduced. Both inputs use
the existing strict `readOfflineJson` before the new semantic admission validators
`verifySourceAccounting` and `verifyInlineAudit` in `financialSourceContract.ts`.
Each export is limited to 256 KiB; duplicate keys, ambiguous numbers, invalid UTF-8,
resource excess and mismatched issuer/source/cutoff/integrity reject. Importing a new
file clears that slot before admission. The other report remains independent.

The actual component uses `sourceImportGuard.ts` to abort replaced reads, keep the
two report channels independent and invalidate both on identity changes/unmount.
Every completion checks its captured identity and revision after asynchronous
validation. Displayed packets must also match current symbol/CIK. A keyed mount
clears prior states immediately when the parent changes issuer. Old event callbacks,
late file reads and old validator promises cannot install a prior company's report.

Source-accounting views retain every caller-designated statement role, exact period,
row status/reason, original lexical fact, nil/accuracy/unit/context identity, source
numeric record, explicit essence relationship and source declaration. Missing,
conflicting and unsupported rows remain unavailable. No displayed value is computed
from a relationship or another filing. Exact calculation intervals show rational
strings and their original open/closed endpoints; no JavaScript numeric conversion
or rounded display is used. Original parsed, admitted parsed, full DTS, source,
collection and explicit amendment lineage identities remain separately labelled.

Inline receipts retain original per-document hashes, acceptance/receipt instants,
processing-reference digests, immutable transformation and embedded profile choices,
original set/parse/DTS identities and taxonomy closure references. Supplied audit
input order and canonical parsed URI order are separate ordered lists. Accepted
acquisition intent is claimed only when its separately retained manifest identity
is present; otherwise its unavailability is disclosed. No raw XML or plaintext
processing references are displayed.

Both panels explicitly disclose caller-supplied receipt evidence, lack of independent
issuer authentication, lack of browser original-XML validation, incomplete statements
and history and bounded standards support. An unavailable receipt does not claim
successful original reconstruction. This UI consumes backend reconstruction receipts;
it does not perform or independently attest the Python XML audit.

File controls have native accessible labels, unavailable-identity explanations,
loading status announcements and validation error alerts. Source tables have
captions, row/column header scopes and named keyboard-focusable scroll regions;
metadata remains available in native disclosure controls. The component uses existing
application styles and does not introduce color-only statuses or motion.

Verification uses `sourceAccounting.test.ts` and the guarded original-byte generator
`terminal/tests/source_accounting_ui_fixtures.py`. The generator calls the actual
backend envelope APIs under forbidden socket bind/connect and supplies ten accounting
and six inline cases. Cases include reported and exact equivalence, contradictions,
missing facts, unsupported numeric declarations, preacceptance and original/amended
vintages, partial role designations, missing originals, no collection, default and
selected transformations, absent acquisition intent and permission-reference digests.
The actual React leaves render only after strict JSON and semantic admission. Separate
lifetime tests exercise replacements, independent channels, symbol/CIK changes,
late asynchronous completion and unmount/effect replay. SSR checks cover initial and
unavailable controls, loading/errors, every source reference and conservative claims.

This is code-level and browser-independent consumer evidence. It does not establish
browser/device/assistive-technology acceptance, owner acceptance, live source
reconciliation, complete financial reconstruction or production qualification.

## Recovered November20 admission and product checkpoint

Private backend APIs are `company_source_accounting` and `company_inline_audit` in
`terminal/stocks/financial_intelligence_product.py`. They produce canonical, bounded
256KiB source envelopes without HTTP routes or automatic source activation. The
accounting envelope includes original facts, contexts, units and full DTS alongside
the existing source-accounting report; inline envelopes retain the original audit
receipt and exact supplied lineage. Inline permissions, byte/URI/receipt/profile,
taxonomy membership and acquisition-intent/coordinator binding are checked before
XML. The exact embedded selector is bound by reconstructed graph identity because
the stored receipt does not separately retain that selector.

The browser independently derives numeric row eligibility/completeness, source
member equality, declaration restrictions, global requires-element occurrence,
exact period/row/network coverage, calculation groups and rational intervals.
Duplicate/dropped rows, periods and calculations reject. Re-signed relationship
claims are checked against source declarations, lexical entities and original facts;
finite accuracy does not establish exact equality. Relationship role/URI endpoints
are corroborated against the retained definition projection. That projection does
not retain every accounting arcrole/precedence detail: raw relationship authenticity
and omitted accounting networks remain the original-byte Python audit's authority,
not independent browser issuer authentication. Input metadata hashes are consistency
checks, not signatures or provider qualification.

The interrupted allowlist now admits the existing exact
`REGISTRY_2015_NUMERIC_V2` profile; no invented profile name is accepted. Two precise
TypeScript annotations were restored. Existing legacy exports/defaults are intact.

Developer verification:12 direct backend regressions;24 actual React SSR/import
lifetime checks;32 source-accounting check regressions;92 full admission checks
(28 actual Python exports,57 re-signed tamper variants,6 lexical-JSON checks and
one re-sign idempotency check). Integrated frontend345 and guarded Python967 pass,
with zero failures/errors/skips. TSC/Vite and9 existing cross-language scripts pass.
These cohorts overlap and are not summed. No browser, application or provider ran.
