# Private Alpaca/SEC setup and eventual source qualification

This guide does not assert entitlements or request intermediate manual UI testing.
Use the existing paper account only. No order/account/position operation is implemented.
Do not copy credentials from GIG Quant Terminal or paste them into chat/reports.

## Configuration

In GitHub Settings → Codespaces → Secrets,authorize this repository for private
`ALPACA_API_KEY_ID` and `ALPACA_API_SECRET_KEY` using the appropriate existing paper
account keys. Legacy `APCA_API_KEY_ID`/`APCA_API_SECRET_KEY` aliases work;conflicting
pairs reject. Never commit these values or place them in frontend/Vite variables.
Do not duplicate a conflicting pair already available in the Codespace.

Existing server-side review controls remain mandatory:

* `GIG_ALPACA_ENABLED`, `GIG_ALPACA_PROTOCOL_REVIEWED`,
 `GIG_ALPACA_PRIVATE_DISPLAY_APPROVED`, `GIG_ALPACA_CLOUD_PROCESSING_APPROVED`,
 `GIG_ALPACA_NO_COST_CONFIRMED`:each1 only after its specific current condition is met.
* `GIG_ALPACA_PERMISSION_REFERENCE`:a bounded non-secret reference to the applicable
 permission/entitlement determination. A flag/reference is not proof of actual rights.
* `GIG_ALPACA_LIVE_ENABLED=1`:separate explicit activation of authorized IEX streaming.
 `GIG_ALPACA_LIVE_MAX_SYMBOLS` is1–4 and must not exceed actual account allowance.

No paid/SIP/OPRA/depth feed is selected automatically. Paper-account ownership does not
independently grant every display,cloud,retention or redistribution use. The owner's
research authorization does not remove the existing review controls. Options and
observed disk-retention gates remain separately disabled unless specifically permitted.

The account is also used by GIG Quant Terminal. Actual connection/subscription/request
limits may aggregate across applications. ATLAS shares one upstream within this
application;it cannot infer another application's usage or grant an independent quota.
Verify the actual account-wide allowance at qualification. No particular remote limit
is assumed,no cross-project credentials/configuration were inspected,and the separate
terminal must not be modified to bypass a provider limit.

Normal ready server startup automatically acquires the fixed paper asset reference
unless an explicit private catalog or approved Nasdaq catalog takes default precedence.
`GIG_ALPACA_ASSET_REFERENCE_ENABLED=0` disables its automatic worker;1 explicitly
selects it. The refresh uses two GETs (active/inactive us_equity),8MiB each,25-second
operation cap,50000 accepted identities,then every six hours. An explicit manual
refresh is available in Securities Universe;300-second cooldown applies. Failure
preserves accepted source state. No source body is persisted. Never enable Nasdaq
directory acquisition merely because its public URL exists;its usage rights are separate.

`ALPACA_PAPER_BASE_URL` is not used as an arbitrary endpoint override. Asset reads
are fixed to `https://paper-api.alpaca.markets/v2/assets`;historical reads go to
`https://data.alpaca.markets/v2/stocks/{bars,quotes,trades}`;live uses
`wss://stream.data.alpaca.markets/v2/iex`. No live brokerage host/order client exists.

Preserve the existing private SEC configuration and identifying User-Agent. Do not
overwrite or print its contact value. Ready SEC auto-discovery is independent of
Alpaca identity discovery;SEC registrants are not the complete listed universe.

Safe checks (no source requests/no credential values):

```bash
.venv/bin/python scripts/check_stock_configuration.py
.venv/bin/python scripts/configure_sec.py --check
```

`ready:true` means configuration checks passed,not that remote credentials or feed
entitlements were actually accepted. Account/reference/market-data qualification must
establish that separately. This Codex environment had neither credential pair nor ready
SEC configuration and made no credentialed/provider/SEC request.

## Network access

The current Codex allowlist does not include Alpaca/SEC hosts. Do not bypass its proxy
or disable TLS. Codespaces may already have permitted outbound access;it is a separate
environment and its secrets are not inherited here. For a future approved cloud
qualification,configure appropriate HTTPS/WSS proxy access to:

* `paper-api.alpaca.markets` — exact read-only asset reference path only in the adapter.
* `data.alpaca.markets` — historical/IEX REST.
* `stream.data.alpaca.markets` — reviewed IEX WSS.
* `www.sec.gov`, `data.sec.gov` — official reference and EDGAR endpoints with identifying
 configuration,conservative pacing and response budgets.

Use the supported environment publication workflow for a changed cloud allowlist.
No network setting was changed or blocked host repeatedly retried in this assignment.

## Update/launch after source review

```bash
git switch feat/atlas-final-release
git pull --ff-only origin feat/atlas-final-release
npm --prefix terminal/web ci
npm --prefix terminal/web run build
# Stop the existing task-owned GIG server with Ctrl+C first.
bash scripts/start_terminal.sh
```

Use the existing private8787 HTTPS-forwarded Codespaces URL. Keep visibility Private.
Initial dependency installation,if needed,uses the existing `scripts/setup_terminal.sh`.
No new native C++ engine rebuild is required solely for these Python/TypeScript changes.

## Eventual authorized qualification

These commands execute requests only with `--execute` and the existing permission
checks. Run only after the required actual configuration/usage rights are satisfied;
no owner-run command was required during intermediate development.

```bash
# Two bounded asset-reference requests;outputs counts/source hashes,not raw rows/keys.
.venv/bin/python scripts/qualify_alpaca_reference.py --execute

# One historical page,process memory only;date is an example,not a trading-day assertion.
.venv/bin/python scripts/qualify_alpaca_market_history.py --execute \
  --symbol AAPL --kind bars --start 2026-10-20 --end 2026-10-20 --max-pages 1

# Separate live IEX qualification,not market-wide completeness or exchange accuracy.
.venv/bin/python scripts/qualify_alpaca_live.py --execute --exclusive-stream-window --symbol AAPL --seconds 30

# Exact official SEC registry resolution before facts,including non-curated symbols.
.venv/bin/python scripts/qualify_sec_sources.py --fetch --resolve-identity \
  --symbol APLD --as-of 2026-10-28
```

The same SEC path supports CRWV and the other representative companies. An absent
official ticker mapping stops;no name-based CIK guess. Company Facts empty/unsupported
concepts remain unavailable. SEC facts/filing-date comparisons do not prove full intraday
historical information availability. Preserve actual source receipts/classifications.

A successful reference acquisition establishes only its accepted provider-account scope.
Report actual counts,active/inactive/exchange coverage,exclusions and source time;do not
call it complete US exchange coverage. A successful historical page is bounded IEX
history,not complete/consolidated/corrected tape. `has_more` signals an incomplete prefix.
The live command can be inconclusive during a quiet/closed market;do not invent prints
or loosen freshness rules. No disk retention is enabled by these commands.

Tests needing authored fixtures are documented in the engineering report. Never aim
fixture mutation scripts at an operator/observed instance. New implementation commits
require separate owner-authorized native ARM64/hosted qualification;no workflow was
dispatched. Physical-device/product acceptance remains a later gate.
