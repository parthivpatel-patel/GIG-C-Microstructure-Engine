# Source-bound statement and company-v2 extension

## Scope and compatibility

`FilingCollection.statement_at(at,role=...,form='10-K')` is a new explicit
`gig.sec.xbrl.statement_view.v1` contract. `gig.backend.company_xbrl.v1` wraps it
with exact product symbol/CIK identity. Existing company.v2, statements.v2,
ordinary SDK and companyfacts APIs are unchanged. This extension does not claim
full financial statements, XML Schema validation or independent source receipt.

Selection requires an explicit timezone-aware nanosecond cutoff, form family and
presentation role. Only one latest eligible filing supplies a view. Unknown
acceptance and future filings are excluded. A latest-time tie is ambiguous.
There is no fallback to an older graph when the latest filing lacks the role or
contains unsupported relationships. Amendments require a supplied predecessor
with known eligible acceptance; they are not additively merged or filled from an
older filing. Original receipt remains unknown when absent. All original inline
set document manifests are retained separately from the derived set hash.

Facts are grouped only by exact concept/context period and units. Dimensional,
opaque and default-dependent contexts are not consolidated. Missing/nil stays
missing. Equal duplicates retain all original fact IDs; differing values or
units remain unavailable. Unsupported input remains explicitly classified.
Presentation orders rows but does not assign accounting meanings or invent
labels. Abstract concepts can be headers only. Full declared QNames, lexical and
exact values, units, accuracy metadata, source SHA and amendment identity remain.

Calculation checks use exact rational reported values and supplied signed-unit
weights within the same role, period and unit. Missing terms do not become zeros.
EXACT_DIFFERENCE is a diagnostic, not an assertion of invalid accounting or XBRL
rounding inconsistency. Decimals/precision interval arithmetic is not implemented.
At most 128 presentation concepts, 12 output periods, 8 fact references per cell
and 256 KiB output are supported. Excess lineage/output rejects, not silently
truncates. Earlier periods beyond 12 have an explicit truncation flag.

## Product and browser workflow

`StockWorkspace.admit_xbrl_collection(symbol,collection)` is an explicit internal,
server-owned, bounded admission operation. It detaches caller state, checks issuer
identity and hashes and preserves all existing companyfacts/market state. There
is no HTTP mutation/upload route, automatic source download, configured secret
read or default startup load. Eight companies / 16 MiB total parsed collections
are bounded. Admission does not authenticate the original source.

GET `/api/v2/companies/{symbol}/xbrl-statements?at=...&role=...&form=10-K` is
read-only, cache-only and serialized by the existing analytical worker gate.
Duplicate/unknown parameters reject. With no explicit supplied collection it
returns an honest unavailable result. An AST-extracted actual route body is tested
without constructing ASGI or binding sockets; this is not HTTP/owner authentication
acceptance evidence.

Stock Intelligence → Statements now includes a separate supplied-XBRL section:
cutoff, exact role, form and period controls, source/fact disclosures, statuses
and exact-value diagnostics. It never replaces the existing selected reported
facts table. In addition to the read-only server view it can open an authorized
private offline export locally (256 KiB ceiling), without uploading it. SHA checks
bind both nested statement and product envelope to their canonical content; these
hashes are integrity, not SEC authenticity. Symbol/CIK, origin, periods, facts,
amendments and missingness are validated before display. Superseded requests and
company changes abort/invalidate old results. No chart or model inputs are invented.

A private supplied batch can be exported **offline**, without launching GIG:

```bash
.venv/bin/python scripts/inspect_xbrl_instances.py --batch /private/path/batch.json --as-of 2024-02-10T12:00:00Z --company-symbol AAPL --statement-role https://issuer.example/role/BalanceSheet --statement-form 10-K --output /private/path/company-xbrl.json
```

Use the actual supplied role and cutoff, not the illustrative URI/date. Existing
strict batch manifests/permissions/path/symlink/size checks still apply. Observed
inputs require an independently authorized copy and explicit `--allow-observed`;
this flag grants no rights and performs no network request. Output is new-only
0600. Do not commit private output. Selecting a company cannot fetch a filing/DTS
or load this private batch automatically. Production-wide source acquisition,
full taxonomy/statement mapping and source corpus qualification remain incomplete.

## Developer checks

Twenty statement-selection tests and eight product/route/export tests supplement
14 effective-relationship tests. Actual Python-product fixtures are consumed by
`node --experimental-strip-types terminal/tests/xbrl-statement-contract.mjs PATH`.
The test file PATH is a bounded authored export, never an owner dataset. Frontend
unit/contract checks do not substitute for browser acceptance. No GIG startup,
server, provider/account call, deployment, trading or paid resource is required.
