# Current final acceptance procedure

Use [ONE updated final Codespaces session](../final_release/FINAL_OWNER_ACCEPTANCE.md)
after engineering,not repeated intermediate commands. Candidate implementation
f1516d03c66ee97850e1b4a7a0add9e90e9a607b includes SEC subset handling and the
MessagePack1.2.3 security update. Existing server requirements must be updated once;
keys and ready SEC configuration are preserved. The current procedure protects prior
source reports from overwrite. Earlier detailed limits/commands below are retained
as historical context;the linked final session is authoritative for this candidate.
No live/provider/owner acceptance is claimed by these instructions.

---

# Existing Codespace: bounded operational qualification

For the reported standalone SEC `ValueError`, use the focused
[diagnostic repair and single retest command](SEC_QUALIFICATION_REPAIR.md).

Engineering checkpoint: `40ca4e86ec4c7c5f339695768605e7453ae4603b`.
This is the final source/target acceptance workflow,not a request to repeat setup.
Existing `ALPACA_API_KEY_ID`, `ALPACA_API_SECRET_KEY` and approved SEC configuration
are reused. Never paste,print,copy to new files,or regenerate credential/contact values.
No account,order,position,trading,SIP,OPRA or depth endpoint is added.

## Before acquisition

Alpaca ticket381230 has no available resolution record in this repository. The
owner's private noncommercial research authorization is recorded;it does not itself
resolve every provider cloud-processing/private-display condition. Use the existing
source-specific permission evidence if applicable. Do not invent a support resolution,
use this checklist as a permission reference,or set flags solely to pass readiness.
If the applicable evidence remains unavailable,source acquisition stays blocked.

The helper checks the existing gates and identifying SEC configuration,without printing
values. It never grants permission. Its process-local changes only disable automatic
asset refresh and persistent history/market-data stores;the owner environment and
private files remain unchanged. Current configured flags are operator attestations,
not independent vendor or billing evidence.

Reserve a short free account-wide streaming window. Other private applications may
share the account's upstream allowance;this script does not inspect or modify GIG
Quant Terminal. `--exclusive-stream-window` confirms that an available slot has been
arranged,not an additional subscription or permission grant. Stop this ATLAS server
with Ctrl+C in its existing terminal first. The helper refuses an occupied8787 port
and never kills or changes an existing process. Do not make that port public.

## Minimal commands in the existing Codespace

No new dependencies or native rebuild are required for this checkpoint.

```bash
git switch feat/atlas-final-release
git pull --ff-only origin feat/atlas-final-release
npm --prefix terminal/web run build
```

After the existing server is stopped,and only when the applicable permission record
is available and a shared-account streaming slot is free:

```bash
umask 077
mkdir -p build/operational
.venv/bin/python scripts/qualify_atlas.py --execute --exclusive-stream-window > build/operational/source-qualification.json
```

Do not `cat` environment variables,write keys to commands,or upload this private report
as a replacement for reviewing it. The report contains configuration names/booleans,
identity counts,public CIKs,source receipts/hashes and aggregate diagnostics;no raw
quotes,trades,financial records,keys,contacts or pagination tokens. For a configuration-
only check,omit `--execute`;that sends zero provider requests. Missing credential names
in the separate Codex executor do not mean existing Codespace secrets need replacement.

If bounded probes pass,or to run the normal gated application independently:

```bash
GIG_ALPACA_STORE_ENABLED=0 GIG_HISTORY_STORE_ENABLED=0 bash scripts/start_terminal.sh
```

Open the existing authenticated **private** forwarded HTTPS address from the Codespaces
Ports tab. No new public URL or hosting is created. The qualification process is
transient;it does not persist observations or inject them into the normal server.
The shown launch also keeps observed stores off for this acceptance process,without
changing saved settings or old data. Normal startup/explicit loads acquire the application's own permission-gated source
receipts. An intentional private-catalog configuration retains its precedence;use
its declared reference or explicit authorized asset refresh,not an invented universe.

## What the single source command actually does

1. Resolve existing SEC settings;inspect credential presence and existing Alpaca gates.
   Do not activate options,paid feeds,trading or storage. Reject an active gateway.
2. Fetch fixed paper `/v2/assets` active/inactive US-equity responses once each,up to8MiB
   per response/50,000 accepted identities. Validate before publishing the new catalog.
3. Fetch at most one64-record daily-IEX-bars page each for AAPL and MSFT over fourteen
   UTC calendar dates ending yesterday (explicit `--end YYYY-MM-DD` supported).
   Empty data is INCONCLUSIVE,never successful qualification. Source identity,units,
   raw adjustment,nanosecond clocks,receipt accounting and incomplete-history flags stay
   explicit. This does not infer market-session completeness or historical ticker identity.
4. Intersect exact source timestamps. Independently calculate raw-close changes using
   Python Fraction,then compare with the actual frontend TypeScript implementation in
   a same-host Node subprocess. No forward/nearest fill,mixed provenance,duplicate
   symbols or total-return inference. Node receives no provider credentials/contact.
   Only counts and a calculation hash leave this comparison process.
5. Independently attempt eligible SEC work even when Alpaca is blocked:official ticker
   mapping,explicit AAPL mapping requirement,production filings/facts normalization,and
   separate official raw-facts reconciliation. APLD/CRWV CIKs are reported only if the
   accepted registry supplies them. Missing mappings stay null. No curated AAPL fallback
   can satisfy this operational identity gate. Reconciliation covers selected records,
   not full XBRL statements,ratios,or intraday historical information availability.
6. With existing live gates and the explicit free-window confirmation,open one IEX
   connection for AAPL/MSFT,or the existing stricter one-symbol limit. Require actual
   fresh observed quotes AND prints per requested symbol. Use a30-second window
   (`--seconds 5..60`);first transport failure stops the qualification attempt without
   retries. The normal application's five-failure recovery contract remains unchanged.
7. Close the stream/workspace on success,rejection,timeout or cancellation. Retention
   stays disabled in this helper. No raw observed records or browser screenshots are
   written. Do not mistake a source-access result for legal/billing certification.

Existing fixed-destination/rate/body limits are retained. REST cadence is at least
one second;SEC component requests also wait1.01 seconds. HTTP request timeout8s,
asset/local acquisition budgets25s,the raw synchronous SEC body deadline25s plus
bounded read timeout,and the aggregate asynchronous campaign deadline180s are declared
limits. Blocking-request cancellation/cleanup can extend process shutdown;180s is not
claimed as an externally measured hard wall-clock guarantee. No failure is automatically
retried. Main stream probes use retry_budget1;the production default remains5.

Default helper request budget is two asset requests,two historical requests,SEC
registry+submissions+companyfacts+independent companyfacts (four SEC reads),and one
bounded streaming connection. Independent SEC reconciliation intentionally uses a
separate raw read. Startup after qualification is a separate application lifetime;
its permitted reference refreshes are not shares of this temporary in-memory cache.
No full market history or large archive is downloaded. Shared provider limits still
apply,even when this local budget is lower.

## Interpreting the report

| Field/outcome | Required interpretation |
|---|---|
| `configuration.*.missing_configuration` | Exact local missing setting names;retain existing secrets;review the specific permission evidence,not a blanket new authorization |
| `PASS_OBSERVED_ACCOUNT_REFERENCE` | Accepted current account-reference response;not all US listings or market-data entitlement |
| `identity_coverage.runtime_searchable_identity_count` | This process's union of provider/SEC/fallback identities;inspect provenance/count_status and source-specific counts |
| `history_AAPL`/`history_MSFT` PASS | Positive bounded observed historical data;not full history/current-live or independent exchange validation |
| `comparison.frontend_agreement.status=PASS` | Python exact reference and actual frontend display agree on exact common timestamps;not total-return performance |
| SEC AGREEMENT | Selected source records,units,periods,values/context/identity agree;no full statements or PIT certification |
| Live PASS | Authenticated IEX source delivered requested fresh observations;not legal rights,billing plan,NBBO or market completeness proof |
| Empty/shared-coverage/quiet-window INCONCLUSIVE | Insufficient evidence. Do not substitute fixtures,assume market-open status,or automatically loop/retry |
| BLOCKED | No qualifying result. Preserve report and examine the named configuration/source condition privately |
| Exit0 | Only bounded source probes passed. **Milestone2 is still not verified** |
| Exit2 | Source campaign blocked,incomplete or rejected;not proof of a defective market feed or lost keys |

Source/receive clocks are explicitly unsynchronized. Source timestamp range and receive
age are diagnostics,not measured one-way exchange/network latency. A quiet feed can
be subscribed without supplying qualifying observations. Run once in a window with
expected IEX activity;do not infer an authoritative holiday/session state from a clock.
Account-wide legal terms,plan/free entitlement,and spare connection capacity need
actual owner/provider evidence;software cannot certify them from asset/credential presence.

## One final target acceptance session (after engineering completion)

This is final acceptance,not intermediate owner development testing. Keep the source
report and a private acceptance record tied to the exact checked-out commit.

- Confirm the forwarded port is Private and GitHub authentication is required. Verify
  the actual forwarded HTTPS origin and WSS/HTTP proof decisions in sanitized connection
  diagnostics. Do not capture cookies,stream/request proofs or tokens.
- Check actual catalog count/source and AAPL/APLD/CRWV discovery. Inspect SEC CIKs only
  when officially mapped;data missingness is independent of symbol discovery.
- Verify historical AAPL/MSFT results,exact shared timestamps and source labels. An empty
  or venue-limited response is not consolidated coverage. Watch the app's own source
  receipt timestamps after its new lifetime starts.
- Apply only authorized subscriptions;verify actual IEX quotes/prints,freshness,per-symbol
  status and no additional upstream opens on browser reconnect. Temporarily disconnect
  the browser network (not the provider account),then restore it and verify bounded
  browser resynchronization. Do not force upstream/provider faults without a separate
  bounded slot/budget. Upstream real-market failure recovery remains untested otherwise.
- Verify SEC statements/filings/ratios and their missing/quality/period disclosures.
  Current restated facts are not historical PIT observations. Check company switching.
- Review all12 workspaces and13 visualization modes. Native depth/event research remains
  authored/replay where true depth is unavailable. Only eligible Level1 views use actual
  observed quotes;dome shape is modeled and VPIN needs declared execution direction.
- Confirm camera/touch/keyboard interactions on the actual desktop/Android devices,
  source controls,private operation and appropriate unavailable states. No synthetic
  state may be relabeled observed. Do not publish screenshots containing provider data
  without separate applicable publication/derivative permission.
- Record owner acceptance (or exact reproducible defects),not just a green automated
  test count. Use the private template;do not commit observations/credentials or claim
  current-candidate ARM64/hosted qualification without an actual corresponding run.

A source CLI PASS,fixture browser PASS or older ARM64 commit cannot substitute for
this target/environment/owner evidence. Milestone2 remains OPEN until those gates close.

## Optional owner-only native qualification

The feature workflow remains workflow_dispatch-only,free_usage_verified defaults false,
and only feat/bootstrap-cpp20-engine or feat/atlas-final-release can run. Main and other
refs remain excluded. No workflow was dispatched here and the default branch workflow
file was not changed. If the owner later authorizes an eligible free run,select the
ATLAS feature branch and verify actual eligibility/free minutes before checking that
input. Preserve run ID,SHA,all six outcomes and canonical evidence. This permission is
not implied by a source-probe PASS,and a native result does not certify physical browser
GPU behavior,market rights or final user acceptance.
