# Stock Intelligence and live-data readiness

Starting local/remote SHA:`d79c891bf2eb645dd8853c19329a5a58c1c78e9d`. Feature branch only.
Implementation:`716939db2a2bbac2e76dc241d34af06e641bfcca`. Focused identifier/model hardening and clean
validated source:`783eb8188bb7d8f4fc34d45a8ae3c4c86c0e43a6`. Both pushed and remote SHAs verified.
Main remains 12f3a53943dc245e36f2cbbc35b9910fb21c0718. Final evidence documentation
commit is identified by Git/delivery,avoiding a recursive self-SHA assertion.

## Executive assessment

A working Stock Intelligence workspace now runs beside the actual native C++ terminal.
Ticker/company search,CIK routing,watch/recent symbols,theoretical options/3D surface and
causal authored research work locally. SEC/Alpaca adapters and financial/reference parsers
are bounded and independently fixture-tested,with secure optional server configuration.
**No SEC/Alpaca observation was obtained. No live-market qualification is claimed.**
This is a validated private synthetic/research checkpoint,not completion of every
institutional analytics,production or observed-data requirement.

Current cloud configuration lists no SEC/Alpaca/vendor documentation hosts;no forbidden
requests,retries,proxy bypass,network changes,paid resources or datasets occurred. Current
protocol,free entitlement and use terms remain unverified. New owner-supplied Kraken
Codespaces DNS/TLS/HTTP101/passive-control success is connectivity evidence only. The
underlying diagnostic JSON was not independently collected here. Zero subscriptions or
market observations;written private research/cloud/recording clarification remains pending.

## Stock feature matrix

|Feature|Status|Actual implemented boundary|
|---|---|---|
|Ticker/name search,exchange,CIK|COMPLETE within declared scope|8 curated seeds;not all U.S. listings or fresh official mapping|
|Watchlist/recent symbols|TESTED_WITH_FIXTURES|private browser20/8 symbol lists,persist refresh,no secrets|
|SEC filings10-K/10-Q/8-K|TESTED_WITH_FIXTURES|fixed official candidate endpoint,recent arrays,acceptance/date/accession/amendment/link validation|
|Company facts/statements|PARTIAL|selected US-GAAP revenue,income,cash flow,assets,liabilities,equity,cash,EPS histories;not full accounting statements|
|Financial ratios|TESTED_WITH_FIXTURES|exact net margin and liabilities/assets on compatible periods;ambiguous concepts unavailable|
|Historical/intraday prices|TESTED_WITH_FIXTURES|provisional Alpaca IEX daily/hourly/minute OHLCV,max256 rows,raw adjustment,no auto pagination|
|Latest quotes/trades|TESTED_WITH_FIXTURES|single-venue IEX snapshots,exact source values/timestamps;size units unverified,no NBBO/depth claim|
|Volume/VWAP/freshness/session|TESTED_WITH_FIXTURES|exact supplied-bar VWAP weighting,cached receipt age/source age,weekday clock only,no holiday/halt authority|
|13F research|PARTIAL|bounded offline XML table parser,explicit historical value units,amendments/delay rules;no downloaded holdings or holder registry|
|Option identity/call-put/IV/Greeks|TESTED_WITH_FIXTURES|OCC-shaped parsing20YY,European model,exactly labelled theoretical assumptions|
|3D option visualization|TESTED_WITH_FIXTURES|interactive constant-volatility153-point plane;no observed chain,smile or fitted term surface|
|HMM/GARCH/Kalman|TESTED_WITH_FIXTURES|bounded fixed-parameter filtering/recurrence,not fitting or calibrated forecasts|
|Risk/strategy research|PARTIAL|exact univariate empirical VaR/ES,causal5-lag long/flat,explicit turnover cost;not portfolio factors or selection walk-forward|
|News/timeline|PARTIAL|SEC event timestamps/attribution from accepted disclosures;third-party articles/sentiment unavailable|
|FinBERT|UNIMPLEMENTED|no weights/dependencies downloaded or inference benchmarked|
|Crypto L2/native replay/3D|PRESERVED|same native binding,book contracts,recorded replay and private browser proof architecture|

The terminal shows UNAVAILABLE by default for prices/fundamentals,not fake company data.
Selecting a stock does not route equities into crypto books or infer queues/orders.
Financial refresh writes only an in-memory accepted provider cache after complete
validation. Options/research inputs are explicitly authored/theoretical,not observed
market returns for the selected company. Native matching/execution/TCA stay available
in their existing separate authored workspace;no new equity execution claim.

## Provider and licensing matrix

|Provider|Implemented access|Current evidence/permission|
|---|---|---|
|SEC EDGAR|fixed data.sec.gov submissions/companyfacts candidate|offline fixtures only;current fair-access policy/identifying User-Agent review required|
|Alpaca candidate|fixed data.alpaca.markets v2 feed=iex bars/latest quote/trade|actual Basic/no-cost entitlement,schema,private display/cloud rights and keys unverified|
|Kraken v2|existing native-backed supervised candidate plus new bounded test tool|OWNER_SUPPLIED handshake101;written rights clarification pending;no observations|
|Coinbase Exchange|existing independent supervisor and candidate profile retained|no actual observations/current official schema or permission review|
|Options/news|no approved observed quote/article feed|theory/SEC disclosure timeline only;no invented open interest or sentiment|
|LOBSTER|no access|restricted dataset remains untouched|

No source is described as unrestricted merely because public/free in name. Official
reference links and all explicit gates are in STOCK_INTELLIGENCE_GUIDE.md. No additional
provider dependencies or model weights were introduced. FinBERT resource feasibility
has not been established by an actual artifact/inference measurement;CPU5 and roughly
34GiB system memory were observable,not a guarantee of model performance or entitlement.
Issuer IR/news feeds and any alternative quote sources require separate current policy
review;no unofficial scrape or mirror was substituted to bypass it.

## SEC and market-data implementation evidence

Curated CIK maps have no claimed verification date. SEC parsers retain tag,unit,period,
filing/accession/frame and amendment metadata. Daily filing-date as-of filtering chooses
latest filing per tagged period,not original intraday availability. Competing concepts
stay separate;contradictory same-filing values reject. Ratios cannot mix duration/instant,
quarter/year,or mismatched periods. Missing/IFRS/unsupported facts remain unavailable;
no inferred quarters,FX conversions or invented earnings. Raw observed disclosures were
not processed. All numerical examples are independently authored schema fixtures.

13F parsing explicitly takes USD versus USD_THOUSANDS from the applicable profile,
rejects DTD/entities,encoding tricks,duplicates,over1MiB or256 rows. It preserves delayed
report/filing dates and separate amendments,never a live position/complete issuer holder
count. No manager downloader,CUSIP-to-ticker registry or current13F unit policy was verified.

Equity response candidates preserve UTC nanoseconds and compare them as integers rather
than truncated datetimes. Quote/trade age is explicitly approximate display;future clocks
are flagged. Bar VWAP uses exact Fraction arithmetic. Quotes are IEX,not NBBO;provider
size units are not silently multiplied into shares/lots. Corporate actions are raw and
partial history is explicit;latest quote/trade snapshot receipt never means a live stream.

Reads are fixed HTTPS with inherited TLS/proxy,zero redirects/retries,one request/s,
identity encoding and raw8MiB SEC/512KiB Alpaca caps,8s HTTP timeout,25s complete refresh.
429/503 cooldown60s,other failures10s. All required responses validate before cache commit.
Cache at most8 issuers/two provider results,2MiB serialized each;Python RSS/transient raw
objects are larger than serialized budgets and not falsely guaranteed32MiB. No disk
recording or API keys/browser credentials;server-only environment gates and fixed hosts.
No browser-supplied URLs,CIKs,headers or paths are forwarded upstream.

## Protocol and reliability repairs

1. New stock POST routes were added individually to the existing endpoint-bound proof
   allowlist. Exact configured Origin/Host,SOP/private-port authentication,one-use/target
   checks and denial of forged forwarding headers remain. No wildcard CORS/public port.
2. Real Chromium caught a noncanonical authored decimal default rejected with422;the UI
   was corrected rather than weakening validation. No crypto source strip appears as a
   stock source. Watchlist refresh and concurrent symbol response version guards preserve
   identity. App and theoretical geometry clean up resources,no new animation loop.
3. A full sanitizer run caught first authored Save returning409. Controlled reproduction
   held the immediate startup retention sweep's shared lock and reproduced409 BUSY.
   Cleanup now first waits its60s interval;expiry remains enforced on reads and periodic
   cleanup remains bounded. No retry masking,timeout inflation or assertion removal.
4. Review reproduced newline accepted in an OCC-shaped padded root. ASCII-space-only
   padding fixes it;failing-before and final regression preserved. YY interpretation is
   explicit2000+YY,not verified listing/exercise metadata.

Prepared subscription test is **not executed**. It requires per-provider review gates
plus GIG_PROVIDER_SUBSCRIPTION_TEST_APPROVED=1,at most20s/256 frames/2MiB consumed
application bytes,one connection,no recording,raw payload output or automatic reconnect.
It reserves room for a maximum-size next frame;wire/TLS traffic is not misreported as
measured application bytes. Injected transport stays synthetic. Acceptance counts/native
state digest are candidate checks,not an independent official protocol oracle. Generic
transport failures are sanitized. Do not run while Kraken clarification is pending.

## Validation matrix and independence

|Executed check|Passed|Failed|Skipped|
|---|---:|---:|---:|
|Full installed Release terminal/native consumer|224|0|0|
|Full Debug binding terminal cohort|224|0|0|
|Full ASan+UBSan binding terminal cohort|224|0|0|
|Final changed stock component:Release/Debug/ASan|48 each|0|0|
|Dedicated Origin/Host/proof/security|46|0|0|
|Stock Chromium workspace/model/3D/mobile/native isolation|10|0|0|
|Existing Chromium crypto application|21|0|0|
|Recorded native L2 replay/research Chromium|9|0|0|
|Gated provider controls Chromium|9|0|0|
|Verified local HTTPS/rewrite/WSS|8|0|0|
|Frontend units|4|0|0|
|Async/browser fixture guards|5|0|0|
|Packaging patterns|3|0|0|
|Installed-wheel interface/export consumers|8+6|0|0|
|Fresh native aggregate test,each six GCC/Clang configurations|1 each|0|0|

Full224 Debug/ASan preceded the final padding-only identifier repair;all48 changed-component
cases were rerun in Release/Debug/ASan after that repair and stronger numerical assertions.
Full224 Release also passed after the repair. No monetary/numerical/native implementation
changed in that focused checkpoint;unchanged expensive full matrices were not repeated.
Both final live LSan checkpoints reported0. Test counts overlap,not unique-test totals.
No final unresolved failure/error/skip. Earlier failing sanitizer221 cohort and controlled
startup/identifier regressions are retained as explicit failing-before evidence.

References independently check standard Black–Scholes values/put-call parity,all five
Greek finite differences,IV round trips,exact fiscal ratios/VWAP,submicrosecond ordering,
HMM zero-observation posterior1/6,Kalman/GARCH first-step formulas,exact causal strategy
wealth/cost and sorted-order-statistic VaR/ES. Tail mutations cannot change prior filter
or position outputs. Negative controls cover malformed data,duplicate keys/fields,
period/identity mismatch,limits,compressed/redirected HTTP,unknown metadata,missing facts,
proof forgery/reuse,target confusion and startup cleanup. Native PMR/allocation and
10,000-transition independent tests are preserved. No Python allocator-failure campaign
for the new disclosure cache is claimed.

All eight frozen native identities/full155-case native suites per six configurations are
reused from `54fa2303c3beac03181d2ff73724ad51aba2dd52` with identical Git tree objects for native
source,binding,root tests,schemas and build files. They were not freshly rerun. Six fresh
aggregate checks and workflow policy checks confirm the unchanged native boundary. Wheel
0.1.1 interface/export tests ran without an unnecessary native rebuild. No current hosted
CI,ARM64,external private Codespace stock acceptance or physical Android claim. Local
Chromium uses SwiftShader/mobile viewport emulation. Existing Vite bundle-size and
Starlette deprecation warnings remain,not suppressed. No new dependencies.

## Clean-source measurements and archive

Clean `783eb8188bb7d8f4fc34d45a8ae3c4c86c0e43a6`,Linux x86_64,Xeon Platinum8573C,
Python3.12.14,GCC14.2 Release binding. Three repetitions of30 calls,5 warmups each:

-512 authored selected SEC facts:median 6.862ms/call.
-153-point theoretical options grid:median 0.518ms/call.
-128 authored returns/filter/risk/strategy:median 1.728ms/call.
-Separate untimed traced peak:229,647bytes;
 whole-process RSS high-water:17,096KiB. Fixture/output identities,
 compiler/build metadata and raw repeated timings are in evidence/stock_intelligence.json.

These are shared-machine Python compute calls,not exchange latency,observed inference,
production tail latency or total allocation counts. Input creation is outside timing/
tracing. No measured reason currently justifies replacing exact descriptive Python
research with a broad C++ port;the native L2/L3/execution contracts remain untouched.

Source archive at this exact source checkpoint:560 safe intended byte-identical members,
12,863,622uncompressed bytes,SHA256 `150f633ef473cf1cdd6d9b2daefda48cd6e50bc118d7cbc06c94bfa44774b51e`.
All required sources included;no ZIP/CSV/raw data,recordings,private cache,node_modules,
binaries or credentials. Archive is ignored and not published. Report-only additions
are outside this explicitly named archive checkpoint. Full inventory/log digests in
safe evidence,not raw provider content.

## Remaining work and November 10 critical path

- **External gates:**current SEC fair-access review/real identifying contact;Alpaca
  actual no-cost entitlement,current schema,source size units,keys and permitted use;
  Kraken written cloud/research/recording clarification and current protocol review;
  Coinbase current channel/auth/order semantics and rights. None was inferred from access.
- **Owner qualification:**update private Codespace,rebuild frontend,accept new stock
  workspace;only then perform separately approved bounded source refresh/subscription,
  independently compare official filings/frames and retain hashes/coverage. Do not set
  attestation flags simply to enable buttons. Do not process restricted LOBSTER.
- **ARM64:**manual workflow remains exact feature-branch/free-usage gated and now expects
 224 terminal fixtures with crypto/SEC/Alpaca flags0. No dispatch. Owner must confirm
  eligible no-cost quota and qualify latest source;previous SHA success does not qualify it.
- **Unimplemented engineering independent of permissions:**full listing-directory refresh,
  complete statement/IFRS/taxonomy reconciliation,manager13F ingestion/CUSIP mapping,
  portfolio/factor risk,fitted HMM/GARCH,model-selection walk-forward,observed options
  chain/calibrated arbitrage-aware smiles/term surfaces,and licensed news/sentiment/report
  exports. Existing causal evaluation is not silently relabelled as those capabilities.
- **Research gates:**point-in-time acceptance/disclosure delays,corporate actions,
  survivorship/missing intervals,transaction costs and independent observed-data test
  denominators must precede empirical predictive claims. No alpha result is supplied.

November 10 readiness is **PARTIAL**:a locally tested stock/theoretical workspace plus
preserved crypto terminal exists now. Full Stock Intelligence/observed-market delivery
remains contingent on the above evidence and substantial explicitly unimplemented work;
no deadline or production-readiness guarantee is supported. Prioritize single-issuer
permitted SEC+IEX qualification before adding more unvalidated panels or heavy models.

## Update and continuation

Ctrl+C in existing Codespace,keep port8787 Private/exact Origin:

```bash
git pull --ff-only origin feat/bootstrap-cpp20-engine
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

No native rebuild needed. STOCK_INTELLIGENCE_GUIDE.md has exact optional configuration,
official review links and future bounded commands. Do not run the subscription tool while
permission is pending. This execution starts no ongoing background engineering.

Ready-to-paste continuation:

> Resume on feat/bootstrap-cpp20-engine from the final stock-readiness documentation
> commit. Verify Git and read CONTINUOUS_ENGINEERING_STATUS.md,
> STOCK_INTELLIGENCE_READINESS.md and STOCK_INTELLIGENCE_GUIDE.md. Source783eb81 has
> 224-case full local binding evidence plus48 final focused stock checks,stock Chromium10,
> crypto21,recorded9,provider9,TLS8,security46 and560-member source inventory. Preserve
> all work and reuse unchanged native155x6/eight hashes transparently. Review owner
>SEC/Alpaca/Kraken/Coinbase protocol/permission evidence before source access. No
> subscription,restricted LOBSTER access,workflow dispatch or current-HEAD ARM64 claim
> without corresponding authorization/evidence. Continue the explicitly unimplemented
> backlog with independent numeric,causal,security and source-provenance checks.

## Changed source inventory

- `.github/workflows/native-arm64.yml`
- `docs/CONTINUOUS_ENGINEERING_STATUS.md`
- `docs/STOCK_INTELLIGENCE_GUIDE.md`
- `scripts/benchmark_stock_intelligence.py`
- `scripts/qualify_provider_subscription.py`
- `terminal/server/app.py`
- `terminal/server/request_proofs.py`
- `terminal/stocks/__init__.py`
- `terminal/stocks/disclosures.py`
- `terminal/stocks/identity.py`
- `terminal/stocks/options.py`
- `terminal/stocks/prices.py`
- `terminal/stocks/research.py`
- `terminal/stocks/sec.py`
- `terminal/stocks/service.py`
- `terminal/stocks/test_workspace.py`
- `terminal/test_arm64_terminal_policy.py`
- `terminal/tests/run_native_suite.py`
- `terminal/tests/stock-intelligence-validation.mjs`
- `terminal/web/src/App.tsx`
- `terminal/web/src/StockIntelligence.tsx`
- `terminal/web/src/api.ts`

This report,evidence/stock_intelligence.json and finalized progress are a separate
safe documentation checkpoint. Main/history/private datasets/security are preserved.
