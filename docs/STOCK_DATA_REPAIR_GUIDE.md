# Stock data repair: existing-account setup and qualification

The active repair supersedes the earlier cache-only workflow. Search/select initiates
bounded authorized loading,not just a cache read. An explicit Load available data button
repeats it. With no approved configuration,panels explain missing variables and next steps;
no fabricated observations are substituted. Stock-source configuration is independent
of the cryptocurrency provider settings and existing native replay.

## Update the existing private Codespace

Ctrl+C in the server terminal. Keep port8787 Private and preserve exact Codespaces Origin:

```bash
git pull --ff-only origin feat/bootstrap-cpp20-engine
npm --prefix terminal/web run build
.venv/bin/python scripts/check_stock_configuration.py
bash scripts/start_terminal.sh
```

No C++ rebuild or new account is required. The diagnostic makes zero network requests,
prints only configuration names/presence/error codes,and never prints secret values.
Do not run fixture-server/browser test commands against your operating provider server.

## Use the existing Alpaca account securely

In GitHub account Settings → Codespaces → Secrets,create or update these private secrets
with the existing account's market-data credentials and grant **this repository** access:

- ALPACA_API_KEY_ID
- ALPACA_API_SECRET_KEY
- ALPACA_PAPER_BASE_URL (optional existing nonsecret convention)

Enter values only in GitHub's private secret UI,never chat,source files,URLs or shell
history. Stop/restart the Codespace so the new secrets are injected,then restart the GIG
server. Credentials in the separate Quant Terminal Codespace do not automatically exist
here. No mounted Quant Terminal repository or credential pair was identified in this
Codex workspace;no secret files were opened/copied. Convention support comes from the
owner's explicit variable names,not a claim that account credentials were shared.

The old APCA_API_KEY_ID/APCA_API_SECRET_KEY pair also works. Partial pairs reject;
if both conventions exist they must contain the same pair,otherwise remove the obsolete
pair or correct it privately. Diagnostic codes distinguish missing/partial/conflicting/
invalid values without exposing them. ALPACA_PAPER_BASE_URL is accepted as configuration
metadata but never used for market data. Only fixed data.alpaca.markets paths are used;
no paper/live account,order or broker endpoint is called. Never point data requests at
an arbitrary or paper trading URL.

After reviewing actual current Basic entitlement,current API/units and private display/
cloud usage,no-cost status,set the existing nonsecret server attestation variables:
GIG_ALPACA_ENABLED=1,GIG_ALPACA_PROTOCOL_REVIEWED=1,
GIG_ALPACA_PRIVATE_DISPLAY_APPROVED=1,GIG_ALPACA_CLOUD_PROCESSING_APPROVED=1,
GIG_ALPACA_NO_COST_CONFIRMED=1,and GIG_ALPACA_PERMISSION_REFERENCE documenting the review.
These flags do not prove permission;do not set them just to remove a warning. No setting
was enabled here. The diagnostic and browser list precisely what remains missing.

## Indicative options are separately gated

The candidate reads only
https://data.alpaca.markets/v1beta1/options/snapshots/{underlying}?feed=indicative&limit=100
using the same existing credentials. It never defaults/falls back to paid OPRA. Require
GIG_ALPACA_OPTIONS_ENABLED=1,GIG_ALPACA_OPTIONS_PROTOCOL_REVIEWED=1,
GIG_ALPACA_OPTIONS_INDICATIVE_APPROVED=1 **in addition** to the common reviewed gates.
Actual account availability,licensing,quote/trade delay and exact current REST behavior
still need owner qualification. HTTP403 alone does not distinguish bad authorization,
plan restrictions or policy;the response code is shown without copying response bodies.

Alpaca's official public alpaca-py source was retrieved through allowed GitHub access:
option.py confirms v1beta1 and /options/snapshots/{underlying};requests.py describes
opra/indicative and indicative default without the options subscription;model/mapping
files corroborate latestQuote/latestTrade/impliedVolatility/Greeks fields. The retrieved
content hashes/URLs and line references are in the repair evidence/report. This is
SDK corroboration,not proof of this owner's current free entitlement,terms,delay or a
successful live query. No market-data request was made in this execution.

Only returned contracts are shown,with calls/puts,expiration/strike filters,indicative
bid/ask and source timestamps,provider IV and Greeks. Missing fields stay unavailable.
A discrete3D point cloud shows supplied IV/strike/calendar time;no interpolation or
calibrated surface is invented. The separate Black–Scholes laboratory is theoretical.
No open interest or complete-chain guarantee. At most100 snapshots/one512KiB body;
next-page availability is explicit and not automatically fetched. More contracts need
a separately bounded filter/pagination design,not a silent limit increase.

## SEC setup

Review official SEC fair-access policy and configure GIG_SEC_ENABLED=1,
GIG_SEC_POLICY_REVIEWED=1 and GIG_SEC_USER_AGENT with a real organization/contact.
Keep contact configuration private if desired;the diagnostic reports presence only.
Current fixed paths are data.sec.gov submissions/companyfacts for the selected curated
CIK. One request/s,8MiB body cap,strict TLS,no redirects/retries/compressed expansion;
429/503 cooldown60s and other failed refreshes10s. No approved SEC configuration existed
here. Direct SEC/Alpaca hosts are absent from the Codex allowlist;do not bypass it.
Owner Codespaces connectivity is a separate observation,not inferred from this cloud.

SEC accepted responses retain actual periods/concepts/accessions and daily as-of
restatement policy. No invented missing statements or fiscal/calendar-quarter
interchange. See STOCK_INTELLIGENCE_GUIDE.md for supported tags/ratios/13F limitations.

## What loading and market depth mean

One cancellable job at a time,60s total;each bounded source refresh remains25s. Selecting
another symbol cancels the prior job before changing its shared status. Accepted results
stay keyed by issuer/provider. Browser responses are version-guarded so a late AAPL
response cannot populate NVDA. Refresh/browser restart can reload approved sources.

SEC,Alpaca equities and indicative options have separate outcomes. Submissions and
companyfacts also validate independently:available filings survive unavailable facts,
and valid financials survive unavailable filings,with explicit PARTIAL status. SEC failures/cooldown
do not block Alpaca's host. For equities,bars,quote and trade validate independently:
a403 quote cannot discard accepted bars/trade. PARTIAL and per-component reasons are
explicit. No prior response is presented as newly observed when a refresh fails.

IEX L1 best bid/ask/supplied sizes are prominent,with native C++ spread/midpoint/microprice/
imbalance when exactly representable. Raw provider size units are not multiplied into
100-share lots. Zero/missing/unrepresentable liquidity produces a specific native
unavailable reason while preserving the original quote. Crossed/locked source quotes
stay labelled. No invented levels,order identities,FIFO or full L2/3 book. No authorized
$0 full-depth feed was established. Native crypto L2 is unchanged.

Quote history is at most32 received snapshots per symbol,not a historical quote archive
or live streaming feed. Load/Refresh updates it. Candles display returned raw OHLCV;
end date is inclusive on a UTC calendar boundary,so today's eligible intraday bars are
not accidentally excluded. Returned bars outside that range reject. Pagination and
incomplete history remain explicit. Market session is only a New York weekday clock
window,not a verified holiday/halt calendar. Source timestamps/age and errors are shown.

Returned-bar changes,VWAP and exact descriptive drawdown/risk are available separately
from authored models. VaR/ES require at least20 returns;capacity-limited exact rationals
remain unavailable rather than rounded. Raw corporate actions,missing bars and short
samples limit interpretation. No predictive alpha,portfolio or execution-fill claim.

## Owner acceptance and failure interpretation

1. Run configuration diagnostic;resolve reported missing names privately.
2. Open Stock Intelligence,search AAPL and select Apple Inc. Watch load progress.
3. Confirm bars/candles,L1 quote,trade,timestamps,VWAP and per-source status.
4. Confirm SEC facts/filings retain periods/source references.
5. Open Options and inspect returned **indicative** subset/IV/Greeks,not an invented chain.
6. Switch NVDA and verify all visible data identities;refresh and check watchlist.
7. Share only sanitized statuses,counts,source hashes/error codes,never credentials or
   unrestricted provider payloads. Do not describe this as live-verified until actual
   source evidence and rights have been checked.

401:check the privately configured pair;403:check account/feed/policy with provider;
429/503:respect cooldown,do not repeatedly retry. A proxy failure is classified separately
from an origin HTTP code;connect/TLS and timeout failures are sanitized. No automatic
SIP/OPRA fallback or limit expansion. Check age before treating any snapshot as current.

Latest-source native ARM64 still requires an owner-controlled,no-cost-eligible manual
workflow. Its terminal cohort is now253;no dispatch or qualification was performed here.
