# Stock Intelligence: implementation and safe qualification

Current loading,credential setup,L1 and indicative-options instructions:
**STOCK_DATA_REPAIR_GUIDE.md**. The repaired UI automatically loads approved sources
on selection and exposes exact missing-configuration actions.

## Working slice and classification

Stock Intelligence is a dedicated navigation workspace alongside the existing native
C++ cryptocurrency terminal. Search ticker or company name across AAPL,NVDA,TSLA,MSFT,
AMZN,GOOG,META,JPM. Exchange/CIK values are curated routing seeds,not a current official
listing-directory download. Watchlists (20) and recent symbols (8) are local browser
symbol lists,not server credentials or portfolio positions. Unavailable SEC/prices remain
unavailable;no fabricated company facts,prices,news or equity depth is substituted.

The current source was independently exercised with authored SEC/IEX-shaped responses,
not actual SEC/Alpaca observations. Both adapters are provisional until current official
schemas,entitlements and policies are reviewed. Public availability or a Basic plan name
alone establishes neither cloud processing nor free entitlement for this owner.

Theoretical European option prices,Greeks,IV and interactive 3D constant-volatility grid
work without external data. Spot,strike,volatility and maturity are explicit scenario
assumptions,not quotes for the selected ticker. A flat model grid is not an observed
smile or calibrated market term structure. OCC-shaped identifier parsing does not verify
listing,deliverable or exercise adjustments. Expiry YY is explicitly interpreted as
2000+YY;only ASCII spaces are accepted in the padded root field. American exercise/discrete dividends are
excluded. Greeks use per1.0 volatility/rate and annual theta;floating approximations
are separate from the native engine's exact monetary contracts.

Quant & Risk accepts authored decimal returns:fixed-parameter two-state Gaussian HMM
filter,GARCH(1,1) forecast recursion,scalar Kalman filter,exact empirical95% VaR/ES and
causal five-lag long/flat evaluation with explicit turnover cost. Parameters are reported,
not fitted. This is not empirical alpha,portfolio risk,model-selection walk-forward,
factor attribution or an exchange execution model. Existing native matching/TCA remain
available separately;no equity fill or queue identities are invented.

## Private Codespaces update

Stop the running server with Ctrl+C;retain private port8787 and exact Origin settings:

```bash
git pull --ff-only origin feat/bootstrap-cpp20-engine
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

No native C++ rebuild is needed for this change. Navigate to Stock Intelligence.
Search/select a company,save a watch symbol,open Financials/Filings/Options/Quant & Risk.
By default refresh buttons are disabled. Calculate theoretical options and rotate/pinch
the explicitly theoretical surface. Cryptocurrency book/replay remains independent.

## Official sources to review

These are official reference locations,not claims that their current contents were
retrieved or that a specific entitlement is free in this execution:

- SEC API documentation:https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- SEC fair access:https://www.sec.gov/about/developer-resources
- Alpaca market data:https://docs.alpaca.markets/docs/about-market-data-api
- Kraken book:https://docs.kraken.com/api/docs/websocket-v2/book/
- Coinbase Exchange:https://docs.cdp.coinbase.com/exchange/websocket-feed/channels

Current cloud policy lists none of those SEC/Alpaca/vendor documentation hosts. No
blocked request was attempted or bypassed. Owner may review them in an authorized
browser/Codespace;use the supported environment publication workflow for any required
allowlist change. Do not use mirrors or disable TLS. No external dataset was processed.

## SEC opt-in

After actual fair-access review,set server-only configuration in Codespaces:
GIG_SEC_ENABLED=1,GIG_SEC_POLICY_REVIEWED=1,and GIG_SEC_USER_AGENT containing the real
organization/contact email required by the reviewed policy. Do not use the authored
example.invalid test identity for real access. Restart the server to apply environment
changes. There is no SEC API-key browser field or arbitrary URL input.

Refresh fetches only fixed data.sec.gov submissions and companyfacts paths for the
selected curated CIK. Strict TLS/inherited proxy,no redirects/retries,8MiB raw response
cap per request,identity encoding only,8s HTTP timeout,25s whole refresh,one request/s.
429/503 impose60s cooldown;other failed refreshes impose at least10s. No older filing
shards or pagination are automatically fetched. A compressed response is refused rather
than unboundedly decompressed. Normalized cache is at most8 issuers/three providers,
2MiB per provider result (48MiB serialized payload ceiling,not a Python RSS guarantee).
Each published component validates before replacing accepted cache. Partial SEC/equities results explicitly retain successful sections;all-component failure preserves the prior cache.
Raw JSON bytes are hashed then discarded;no new disk cache or observed recording.

Filings preserve form,accession,filing date,optional acceptance timestamp,report date,
amendment and safely constructed official link. Recent filings include10-K/10-Q/8-K
and manager13F forms when present,not complete history or company holder totals.
Selected US-GAAP monetary/EPS tags retain concepts,units,periods,filing/accession and
frames. Alternative concepts remain distinct. Latest filing per tagged period as-of
filing date is an explicit restatement policy;this is not intraday point-in-time data.
Contradictory same-filing values reject. Missing/ambiguous or incompatible quarterly/
annual periods do not produce invented ratios. No IFRS mapping,fiscal-quarter subtraction,
full accounting-statement reconstruction,or average-balance return ratios is claimed.

Offline13F XML parsing rejects DTD/entities/encoding tricks,duplicates and input/record
budgets. Value units must be explicitly supplied as USD or USD_THOUSANDS from the
applicable filing profile. Amendments are separate observations;no blind netting. This
parser is fixture-tested but is not a downloaded manager-holdings integration. Quarter-end
disclosures and their delays never establish real-time institutional positions.

## Alpaca optional server credentials and entitlement

Review the owner's actual Basic entitlement,IEX channel availability,API schema,fees,
private display,cloud processing and retention before setting any flags. No purchase,
account creation or entitlement check occurred here. Keep keys in private Codespaces
secrets/environment;never commit,paste into browser forms,URLs,logs or reports.

Required server variables:

- ALPACA_API_KEY_ID,ALPACA_API_SECRET_KEY (legacy APCA_* pair also accepted;conflicting pairs reject)
- GIG_ALPACA_ENABLED=1,GIG_ALPACA_PROTOCOL_REVIEWED=1
- GIG_ALPACA_PRIVATE_DISPLAY_APPROVED=1,GIG_ALPACA_CLOUD_PROCESSING_APPROVED=1
- GIG_ALPACA_NO_COST_CONFIRMED=1,GIG_ALPACA_PERMISSION_REFERENCE documenting actual review

The fixed data.alpaca.markets v2 candidate reads bars/latest quote/latest trade only,
feed=iex and adjustment=raw. There are no account/order/trading endpoints. Max256 bars;
no automatic next-page acquisition. Daily window at most366 days,hourly31,minute7;
UI requests90/14/3 days respectively. Results explicitly report incomplete history and
next-page availability. One provider request/s,512KiB each,25s whole refresh and the same
cooldown/cache rules apply. Bars,quote and trade validate independently;PARTIAL status explicitly preserves accepted sections when another request fails. No invalid component is published.

Only IEX single-venue prices/prints are represented,never SIP/NBBO/market-wide volume
or Level2/3 equity depth. Quote/trade size units remain provider-reported and unverified;
no silent100-share-lot conversion. OHLCV and supplied bar VWAP are exact decimals within
explicit bounds;aggregate VWAP weights supplied bar VWAP by returned volume. Missing
VWAP remains unavailable. Corporate actions are not adjusted. UTC source nanoseconds
are preserved and compared exactly;display age is explicitly approximate. Weekday New
York09:30–16:00 is only a clock window,not holiday/halt/session authority. Latest snapshots
are labelled cached responses,not live streams. Future source clocks are flagged.

## Kraken/Coinbase gates and owner test preparation

OWNER_SUPPLIED new evidence:Kraken Codespaces DNS resolved,TLS hostname/certificate
verified,HTTP101 upgrade and passive control frame,no proxy,zero subscriptions/market
observations and no recording. This is connectivity evidence,not current protocol
conformance or private research/cloud/recording rights. Kraken written clarification is
pending. Coinbase remains separately fixture-tested,not live-qualified.

Keep both disabled until applicable reviews and explicit test approval. The existing
handshake tool remains safe without subscription flags:

```bash
timeout 20s .venv/bin/python scripts/diagnose_websocket_access.py --provider kraken
```

Prepared **future** subscription command (do not run while permission remains pending):

```bash
timeout 30s .venv/bin/python scripts/qualify_provider_subscription.py --provider kraken --seconds 10
```

Requires existing per-provider ENABLED,PROTOCOL_REVIEWED,PRIVATE_DISPLAY_APPROVED,
CLOUD_PROCESSING_APPROVED,PERMISSION_REFERENCE plus an additional explicit
GIG_PROVIDER_SUBSCRIPTION_TEST_APPROVED=1. Coinbase uses its separate namespace.
No flag is set by this assignment. At most20s/256 application frames/2MiB consumed
application bytes;one connection,no automatic reconnect,64KiB frame cap and bounded
close. It reserves space for a maximum-size next frame before reading. TLS/wire bytes
and library queue overhead are outside that consumed-application-byte metric.
No recording or raw payload output. Counts,native revision and state digest only.
An injected fixture is always synthetic. This is candidate parser/native validation,
not an independent vendor protocol oracle or new LIVE_VERIFIED claim. Share only the
sanitized summary. Actual observations must still be independently reviewed before
terminal live qualification. Recording has its separate existing rights gate.

## Native ARM64 and regression handoff

Manual-only,owner-gated,no-cost eligibility confirmation and exact feature-branch guard
are unchanged. Workflow now requires253 terminal tests in its GCC Release wheel step,
with all crypto/SEC/Alpaca live flags disabled. No workflow was dispatched;previous native
ARM64 results remain SHA-specific. Latest-source qualification is an owner action.

Local full binding cohort requires built authored diagnostic binaries via
GIG_TERMINAL_NATIVE_BUILD and the installed native wheel:

```bash
.venv/bin/python terminal/tests/run_native_suite.py --expected-tests 253
npm --prefix terminal/web run build
node terminal/tests/stock-intelligence-validation.mjs
```

Browser harnesses first require an explicitly fixture-safe server;enabled SEC/Alpaca or
crypto collection,observed cache/replay and recording refuse fixture testing. Do not run
these against an operating live terminal. Use a separate fixture instance. New stock POST
routes use the existing exact Origin/Host and one-use endpoint-bound Codespaces proof;
no wildcard CORS,forwarded-header trust or public-port change was added.
