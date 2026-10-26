# Phase 3 SEC validation

## Verified offline

Inspected sec.py,financials.py,service.py and scripts/qualify_sec_sources.py. Existing
independent raw-record reconciliation does not call production selection/exact/source-ID
helpers. It checks issuer,selected concepts,values,units,periods,filing context and IDs;
wrong issuer/missing metric/mutated value fail,and empty supported data is inconclusive.
Existing backend tests include exact12-descriptor Fraction references and2000 signed
margin candidates. This phase reruns them through the274-case native-consumer cohorts.
The new AAPL workflow independently exercises authored SEC acceptance and source labels.

## External result: BLOCKED,not independently reconciled

Safe environment inspection reported GIG_SEC_USER_AGENT absent and SEC permission
sec_disabled_pending_fair_access_review. No User-Agent value was printed or changed.
No official request was made and no actual AAPL amount is claimed verified. The owner's
Codespace configuration does not establish configuration in this Codex environment.
No proxy restriction was bypassed and no fabricated contact identity was used.

## Owner-run official reconciliation

In the authorized Codespace with existing reviewed SEC settings and valid identifying
User-Agent,load AAPL SEC disclosures through the normal UI/proof-protected action first.
Then use its validated Python environment:

```bash
mkdir -p build/atlas3-owner
python scripts/qualify_sec_sources.py --symbol AAPL --as-of "$(date -u +%F)" \
  --fetch --compare-cache --output build/atlas3-owner/sec-aapl-reconciliation.json
```

This performs one fixed official HTTPS companyfacts request,8MiB cap,8-second timeout,
no redirects/retries,keeps no raw response,compares exact selected facts against the
local cache and creates an output file exclusively. Do not run during another SEC
refresh;space requests at least one second apart. Run once and stop on proxy/SEC errors.
Gate failure occurs before network acquisition. No secret belongs in output or Git.
If cache is stale/different filing date,refresh through UI and investigate rather than
editing expected values. Agreement is limited to selected supported records,not full
statements,fiscal-quarter reconstruction,ratios or intraday point-in-time availability.
Owner should inspect and share safe counts/hash/status only for evidence review.
