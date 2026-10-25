# Stock Intelligence repair and actual-data qualification handoff

Starting local/remote HEAD:`43ba291c7fd07f6f2317dec4e09ddd897a27f08f`. Branch:feat/bootstrap-cpp20-engine.
Initial validated repair:`caa9639117e93592d6df6fac6b313dadd173aa6e`. Final validated runtime:
`18d67fba941a96aff68ac459179cf365379868f7`. Both pushed and verified with git ls-remote. Main remains
12f3a53943dc245e36f2cbbc35b9910fb21c0718. Final evidence-only commit is identified by
Git/delivery,not a recursive assertion inside itself. Additional budget spent:$0.

## Executive finding

The three founder-reported failures were real implementation gaps:selection read cache
without initiating loading,only APCA_* credentials were recognized,and prices/quotes
were buried in JSON rather than visible candles/L1 panels. All three are repaired and
independently exercised through the actual ASGI/native/browser application with authored
provider responses. This is not a claim that actual AAPL market data was obtained.

**Actual market-data acceptance remains UNVERIFIED.** This Codex environment has no
Alpaca credential pair and its direct SEC/Alpaca hosts are not allowlisted. No provider
market request was attempted,no credentials copied/printed,and no blocked destination
was bypassed. The current owner Codespace can differ;configure it privately and run the
bounded acceptance steps in STOCK_DATA_REPAIR_GUIDE.md. Do not paste keys into chat.

## Reproduced root causes and repair

|Finding|Before evidence|Repair/acceptance|
|---|---|---|
|Cache-only selection|43ba291 service has no start_load interface;frontend selects GET company only;founder browser report|new protected POST load,60s cancellable task,per-source status,polling/version guards;AAPL→NVDA fixture browser9 passes|
|Wrong credential convention|baseline service with reviewed flags+ALPACA-only pair rejects alpaca_server_credentials_required|ALPACA_* and legacy APCA_* supported;partial/conflicting/invalid pairs reject;fixed data host never paper URL|
|Hidden market data|baseline UI lacks quote/candlestick components and exposes source values chiefly in Details|visible L1 bid/ask/sizes/trade/native spread,candles,VWAP/change,source age and setup/error cards|
|All-or-nothing source losses|valid bars lost when quote failed;two controlled SEC tests show valid filings/facts discarded when the other endpoint failed|each component validates independently;PARTIAL retains available sections;all-component failure preserves prior accepted cache|
|Diagnostic regression during repair|expanded gate caught rate-limit error masked by all-SEC-unavailable wrapper|safe per-component causes retained,including rate/HTTP/timeout/proxy classifications;unchanged assertion passes|

Baseline reproduction is in safe repair-before metadata;failing-before SEC tests and
intermediate diagnostic failures have log digests in evidence/stock_data_repair.json.
No assertion weakened,no failed checks silently skipped. A transient stylesheet edit
was caught by the production build and corrected by restoring baseline CSS plus only
intended stock additions;its resulting temporary404 test environment was rebuilt and
restarted before all final browser/TLS checks. It was not an engine or provider outage.

## Working feature matrix and real-versus-fixture evidence

|Capability|Implemented/verified|Actual observed-data status|
|---|---|---|
|Search/company/CIK/exchange|8 curated identities,ticker/name search,watch/recent lists|not a fresh full listing-directory verification|
|Selection/loading|protected auto-load after selection when configured;explicit reload;60s total;switch cancels old job|no eligible account request executed here|
|Equity prices|daily/hourly/minute candidate OHLCV,candles,volume,VWAP,changes,source timestamps|fixture-tested;no real bars|
|Equity quote/trade|IEX best bid/ask/supplied sizes,latest print,errors/freshness|fixture-tested;not SIP/NBBO/consolidated market data|
|Native L1 analytics|actual C++ AggregateDepth on one quote,exact spread/mid/microprice/imbalance;no rounding of unsupported precision|fixture-tested;not book reconstruction or inferred orders|
|Quote changes/history|max32 received snapshots and midpoint visualization;explicit refresh-based updates|not historical archive or continuous stock streaming|
|Equities L2/3|no fake levels or queues;native crypto L2 preserved|no current authorized $0 full-depth source established|
|Indicative options|fixed indicative-only snapshot subset,calls/puts,expiry/strike selectors,optional quotes/trades/IV/Greeks|fixture-tested;actual account entitlement and feed delay unverified|
|3D options|discrete provider-IV point cloud separate from theoretical constant-volatility grid|no interpolation,complete observed chain or calibrated arbitrage-free surface claim|
|SEC fundamentals/filings|independent validated recent filings and selected US-GAAP facts/period-aligned ratios with partial results|fixture-tested;no actual SEC response|
|Descriptive/risk research|exact returned-close changes/drawdown/simple-return risk;minimum20 returns for empirical VaR/ES;exact-capacity limits explicit|fixture-tested;raw corporate actions/partial history limit interpretation,no alpha/portfolio claim|
|Broader models/news/ownership|existing authored filters/models and SEC timeline/offline13F schema preserved|no new fitted forecasts,complete statements,holder registry or licensed news claim|

The full feature scope is partial pending actual source qualification and larger research
work. A configured flag is an operator attestation,not independent evidence of entitlement.
A successful selection with fixtures does not count as live-market acceptance.

## Existing Alpaca account and secure configuration

No second account or paid subscription was created or required. No mounted Quant Terminal
repository was identified in the workspace inventory,so its nonsecret integration code
was not claimed inspected. Credential sharing between Codespaces was not assumed.
Only presence of the five named variables was inspected;all were absent here. No .env,
secret store or credential file contents were opened. Variable convention support follows
the owner's explicit ALPACA_API_KEY_ID,ALPACA_API_SECRET_KEY and ALPACA_PAPER_BASE_URL.

Use GitHub account Settings→Codespaces→Secrets and grant this repository access to the
existing account pair. If existing secret entries already hold the values,update their
repository access instead of creating another account. Stop/restart Codespace to inject
changes. Never put keys in chat,source,browser forms,URLs or shell history. Paper URL
is metadata only:market requests always use data.alpaca.markets. Legacy APCA_* aliases
remain compatible,but contradictory pairs fail closed. Diagnostic prints names/presence,
never values. Common review/no-cost/private-display/cloud gates remain and have explicit
missing-variable actions. Optional indicative access adds three separately reviewed gates.

## Official Alpaca source corroboration

Five small **official public SDK** files were retrieved through permitted HTTPS GitHub
access,HTTP200,no redirects/retries,max128KiB each. Not market data,not an unauthorized
mirror,and no source-access restriction was bypassed. Exact URLs,content SHA256 and
retrieval time are in evidence. master is mutable;hashes identify inspected bytes,not
an asserted immutable upstream commit.

- alpaca/data/historical/option.py:64–71 uses v1beta1;204–231 uses
  /options/snapshots/{underlying_symbol}.
- alpaca/data/requests.py:442–466 documents chain filters and indicative default when
  there is no options subscription.
- alpaca/data/models/snapshots.py:89–136 corroborates optional quote/trade/IV/Greeks.
- alpaca/data/mappings.py:36–44 maps latestQuote/latestTrade/impliedVolatility/greeks.
- alpaca/data/models/quotes.py:9–33 describes source sizes/prices;it does not independently
  establish share/round-lot units or this account's data rights.

Official SDK references support the candidate implementation. They do **not** prove
current Basic free entitlement,private-cloud use,redistribution,retention or exact
indicative quote/trade delay. Direct provider documentation,terms and live responses
were not retrieved here. Owner must verify them before enabling review flags. No OPRA
fallback:feed=indicative is hard-coded even if the account also has paid entitlements.
SDK raw source stays ignored in build;only safe references/hashes are committed.

## Limits,semantics and error handling

Fixed HTTPS GET endpoints only,no account/broker/order calls or browser-provided URLs.
One request/s,8s HTTP limit,25s refresh,60s selection job;strict TLS/inherited proxy,
zero redirects/retries. SEC body cap8MiB,Alpaca512KiB;identity encoding only. At most256
bars,100 option records,32 quote observations,8 issuers and2MiB normalized result per
provider (48MiB serialized ceiling for3 providers,not a total Python RSS guarantee).
No raw provider response is written to disk;source hashes and exact timestamps persist
in the accepted cache. Data is not publicly redistributed or observed-recorded here.

429/503 cooldown60s and other failed refresh cooldown10s;SEC and Alpaca host budgets are
isolated,while options share Alpaca's host budget. HTTP401/403/429 are preserved as codes,
not guessed entitlement decisions;proxy/connect/TLS/timeout are distinct sanitized
classes. Independent endpoint reads are bounded,not indefinite retries. All-failed
refresh leaves accepted prior state unchanged. No missing fact,quantity,price or execution
is invented. Native quote sizing preserves raw source units and rejects nonintegral
representation;no silent100-share conversion. Locked/crossed quotes remain labelled.

Returned bar timestamps preserve exact nanoseconds and must lie within requested UTC
calendar dates;end date is inclusive,so current-day eligible intraday observations are
not excluded by an accidental midnight boundary. Partial/latest-bar completeness and
pagination remain unknown/explicit. New York weekday trading-clock window is not an
exchange holiday/halt/calendar authority. Snapshot age is not live-stream proof.

SEC fiscal periods are preserved;ratio matching does not invent calendar quarters or
combine incompatible periods/concepts. Full accounting-statement/IFRS reconstruction
and full holder mapping are outside the implemented subset. Indicative IV/Greeks are
provider-derived estimates,not independently calibrated observations. Missing Greeks,
quotes,open interest or contracts stay unavailable;no complete chain or executable
quote claim. Independent Black–Scholes/IV/Greek references remain separate.

## Validation evidence

|Executed cohort|Pass|Fail|Skip|
|---|---:|---:|---:|
|Full terminal with installed Release native binding|253|0|0|
|Full terminal with Debug native binding|253|0|0|
|Full terminal with ASan/UBSan native binding|253|0|0|
|Focused stock cases (included in above)|77|0|0|
|Existing private Origin/Host/proof security|46|0|0|
|Configured-source browser using authored responses|9|0|0|
|Unavailable-source stock/3D/mobile browser|10|0|0|
|Existing actual crypto browser|21|0|0|
|Recorded native replay/research browser|9|0|0|
|Gated provider controls browser|9|0|0|
|Verified local HTTPS/rewrite/WSS|8|0|0|
|Frontend units|4|0|0|
|Async/browser-safety controls|5|0|0|
|Packaging patterns|3|0|0|
|Installed0.1.1 wheel interface/export|8+6|0|0|
|Native aggregate target,each six GCC/Clang configs|1 each|0|0|

Live LSan check0;no suppression,assertion weakening,test removal or timeout inflation.
No final unresolved failure/error/skip. Some cohorts overlap,not unique-test totals.
Full253 matrix was executed after final runtime changes. Final browser path uses real
ASGI/native engine and authored provider injection,not mock financial/native logic.
Independent Fraction references cover spread/mid/microprice/imbalance,VWAP and returned-
price drawdown/risk;existing options Greek/IV/causal models remain independently checked.
Source mocks never authorize a LIVE classification;test responses remain synthetic.

The existing full155 native tests per six GCC/Clang Debug/Release/sanitizer configurations
and eight frozen hashes are **reused** with exact matching native source/binding/root
fixture/build/schema tree objects from 54fa2303c3beac03181d2ff73724ad51aba2dd52. Six fresh aggregate
checks retained10,000-transition/PMR failure coverage. No new C++/binding sources changed,
so no unnecessary wheel/native rebuild/full-oracle rerun is claimed. Three manual-workflow
policy tests preserve frozen hash constants and exact native counts. Hosted CI/current-
HEAD ARM64 were not run. Manual workflow now expects253 terminal tests;owner controls
its free-eligibility gate. Previous ARM64 success remains tied to its tested SHA.

Local Chromium uses SwiftShader/mobile viewport emulation;not owner external private
Codespace or physical Android acceptance. Existing Vite chunk-size and Starlette
TestClient deprecation warnings remain. No new dependencies were introduced.

## Clean-source performance and package evidence

At clean `18d67fba941a96aff68ac459179cf365379868f7`,Python3.12.14,GCC14.2 Release native binding,
shared x86_64 Xeon Platinum8573C,3 repetitions×30 calls,5 warmups per operation:

-512 authored facts:6.916ms median/call.
-153-point theoretical grid:0.517ms/call.
-128-return authored model/risk:1.737ms/call.
-Native L1 quote calculator with Python parsing/marshalling/snapshot/normalization:
 25.48µs/call,not pure C++ cycles or network/exchange latency.
-Separate untimed traced peak:229,647bytes;
 whole-process peak RSS:20,744KiB. No tail-latency/allocator-call count or
 production performance claim. No journal optimization or speculative C++ migration.

Source archive for this exact runtime:574 safe,intended,byte-identical members,
13,064,874uncompressed bytes,SHA256 `3a0ae764f8ee2a8272de9b2687752607e4a13fba90c869b3bd64cf8e6416a6dc`.
No ZIP/CSV/private recordings,raw observations,secrets,binaries,dependency/build caches
or downloaded SDK files. Archive stays ignored/unpublished. Final report-only additions
are outside this named source archive checkpoint. Full safe source inventory and log
hashes are in evidence/stock_data_repair.json.

## Owner actions and remaining blockers

1. Ctrl+C,update/rebuild/restart the existing private Codespace;do not make port public.
2. Grant this repository access to the existing Alpaca Codespaces secret pair and restart
   Codespace to inject it. Do not paste values here. Run the zero-request diagnostic.
3. Review actual IEX/indicative plan entitlement and policy;configure reviewed flags and
   real SEC identifying User-Agent privately. A successful handshake is not permission.
4. Search/select AAPL,inspect source errors/provenance,then NVDA and browser refresh.
   Share sanitized counts/status/hash/error codes only. Actual acceptance is still pending.
5. Owner separately verifies eligible no-cost runner/quota and manually qualifies latest
   source. No workflow dispatch,runs,cancellation,paid infrastructure or main merge here.

No current authorized $0 full equities L2/3 source was established. No new Kraken/Coinbase
market subscription or written-rights confirmation occurred. Current direct SEC/Alpaca
responses,size-unit/delay semantics and empirical comparisons remain unverified. Full
options-chain discovery/pagination,corporate-action-aware historical research,full
financial statements,holdings/news/fitted portfolio models remain explicit future work.
November 10 is the final owner deadline,not a verified promise of those external gates.

## Exact update and continuation

```bash
git pull --ff-only origin feat/bootstrap-cpp20-engine
npm --prefix terminal/web run build
.venv/bin/python scripts/check_stock_configuration.py
bash scripts/start_terminal.sh
```

Stop the old server first;no C++ rebuild needed. Use your existing private forwarded
Codespaces URL/Ports→Open in Browser,not localhost on a remote phone. Configuration and
bounded qualification steps are in STOCK_DATA_REPAIR_GUIDE.md. No engineering continues
in the background after this task ends.

> Resume from the final stock-data-repair documentation commit on
> feat/bootstrap-cpp20-engine. Verify Git/read CONTINUOUS_ENGINEERING_STATUS.md,
> STOCK_DATA_REPAIR_REPORT.md and STOCK_DATA_REPAIR_GUIDE.md. Source 18d67fb has full253
> Release/Debug/ASan,77 focused cases,configured-fixture browser9/unavailable10,crypto21,
> recorded9/provider9/TLS8/security46 and574-member source inventory. Preserve all work;
> do not repeat unchanged native155×6/eight-hash evidence without reason. Obtain owner
> private credential/configuration and current entitlement/rights evidence before actual
> provider qualification. No paid OPRA/depth fabrication,restricted data,broker calls,
> workflow dispatch or exact-HEAD ARM64 claim without matching evidence/authorization.

## Changed files

- `.github/workflows/native-arm64.yml`
- `docs/CONTINUOUS_ENGINEERING_STATUS.md`
- `docs/STOCK_DATA_REPAIR_GUIDE.md`
- `docs/STOCK_INTELLIGENCE_GUIDE.md`
- `scripts/benchmark_stock_intelligence.py`
- `scripts/check_stock_configuration.py`
- `terminal/server/app.py`
- `terminal/server/request_proofs.py`
- `terminal/stocks/auth.py`
- `terminal/stocks/option_feed.py`
- `terminal/stocks/price_research.py`
- `terminal/stocks/quote_analytics.py`
- `terminal/stocks/service.py`
- `terminal/stocks/test_repair.py`
- `terminal/test_arm64_terminal_policy.py`
- `terminal/tests/run_native_suite.py`
- `terminal/tests/stock-loading-validation.mjs`
- `terminal/tests/stock_fixture_server.py`
- `terminal/web/src/EquityPanels.tsx`
- `terminal/web/src/OptionChain.tsx`
- `terminal/web/src/StockIntelligence.tsx`
- `terminal/web/src/VolatilitySurface.tsx`
- `terminal/web/src/styles.css`

This report,evidence/stock_data_repair.json and finalized progress form a separate safe
documentation commit. Main/history/private data and browser security are preserved.
