# SEC EDGAR engineering validation

## Independently verified here

Two baseline failures were reproduced before repair, using authored inputs only:

| Finding | Source/root cause | Repair and regression |
|---|---|---|
| High: numeric magnitude boundary | sec.py exact(); `abs(Decimal)` rounds under the active Decimal context, permitting an infinitesimally over1e30 value | Compare `copy_abs()` exactly; both signs tested at context precisions8/28/80 |
| High: contradictory filing identity | sec.py filings(); repeated accession rows had no identity-consistency check | Compare selected filing rows by accession, reject contradictory fields, count/deduplicate identical rows |
| Medium: malformed provider containers | Nested `.get` assumed dictionaries | Explicit dict validation for root/facts/filings/concept/units; structured ValueError and negative fixtures |
| Low: receipt labelled request start | service.py refresh() used start stamp as received_at | Separate requested_at, completed receipt time and per-component receipts |

Failing-before evidence: ignored `build/backend-audit/sec-integrity-before.log` contains
two failed assertions that ValueError was not raised. Both regressions now pass. No
actual filing was used to construct these examples and no empirical defect is alleged.

A related offline options audit reproduced the same context-rounding pattern in
`terminal/stocks/option_feed.py:signed()`: precision8 admitted1000000.000000000001.
It now uses copy_abs(); the same focused regression checks both signs and valid
boundaries. This does not imply observed-provider defects or enabled Alpaca access.

## Financial normalization and calculations

Selected16 metrics preserve exact reported decimal digits (finite,string length≤64,
absolute value≤1e30, exponent−128..30); no silent rounding. Longer precision acceptance
is an intentional bounded v2 normalization expansion. Unsupported units do not become
USD by assumption. Actual durations/instant periods and filing fiscal context are
separate. Latest as-of restatements are explicit; revision retention is bounded.

New12-metric financial calculator uses Fraction arithmetic and up to4096-bit outputs.
Margins align income/revenue periods. Current/debt ratios require same instant.
Debt uses only three declared borrowing/debt components, never total liabilities or
an invented missing zero. FCF is CFO less cash PP&E payments, explicitly non-GAAP.
ROA/ROE require beginning and ending balances and report the exact income period,
without annualization. Annual revenue/income/EPS growth requires unique adjacent
350..380-day10-K/A periods and positive prior base;52/53-week differences remain visible.
Ambiguous concepts, incompatible periods or missing components yield null plus reason.
No quarterly derivation from annual/YTD data, smoothing or imputation is performed.

Tests cover all12 formula references,2000 independent signed margin candidates,
negative/zero bases, missing and ambiguous inputs, fiscal contexts, revision selection,
precision,53-week boundaries, schema/null behavior and independent raw reconciliation.
Full expanded native-consumer cohorts include these tests.

## Actual source validation: BLOCKED

The owner's Codespaces readiness/Apple statements are OWNER_REPORTED only. This task
has not independently retrieved or reconciled an official Apple statement. Current
managed environment has no SEC host allowance and no enabled/reviewed/contact SEC
configuration. No proxy bypass, invented user agent or provider request was attempted.
The directive's actual SEC source-validation acceptance gate is **not satisfied**.

Owner action: use the supported environment configuration review/publication workflow
for data.sec.gov/www.sec.gov if Codex access is desired; configure a truthful identifying
SEC User-Agent server-side after fair-access review. Alternatively execute the gated
qualifier in the already authorized private Codespace and retain original source/hash/
cutoff evidence. Reconcile at least current+prior annual and interim periods, revisions,
units and filings to official source statements before declaring empirical acceptance.
The new tool is readiness infrastructure, not a substitute for that evidence.
