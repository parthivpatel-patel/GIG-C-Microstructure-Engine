# GIG ATLAS — provider reference and historical-data integration

Date: October29,2026 America/New_York.
Starting local/remote checkpoint: `c8022a3b4edbdd482d1945c972c4414a344bcd8c`,clean.
Branch: `feat/atlas-final-release`.
Final implementation: `89d06adb973c4a3f5cb8f3da3e734721a63bfe02`.
Main unchanged: `12f3a53943dc245e36f2cbbc35b9910fb21c0718`.
Delivery documentation has its own subsequent commit,reported in Git/final response.

## Outcome and actual coverage

Automatic Alpaca paper-account asset discovery,source filters,bounded historical
bars/quotes/trades,matched-timestamp historical comparisons and non-seed SEC
qualification are implemented. Existing live IEX,SEC,12 workspaces,3D,private settings,
native C++ behavior and frozen reference expectations are preserved.

**Actual default-environment searchable identities:13 curated fallback identities.**
**Imported official exchange listings:0. Imported Alpaca asset identities:0.
Accepted official SEC mappings:0. Actual live-provider observations qualified:0.**
The environment reports no ready credential bindings,SEC readiness=false and no
ALPACA/APCA credential pair. Alpaca/SEC destinations are outside the current enforced
HTTP allowlist. No account,market-data or SEC acquisition request was attempted.
CLI execution checks refused before network on this configuration.

The authored browser instance has60 provider-shaped identities,including inactive
identities. The performance fixtures contain11000 assets and50002 directory identities.
None of these numbers is actual US stock coverage. AAPL,GOOGL,MSFT,NVDA,AMZN,APLD and
CRWV pass source-fixture discovery tests. APLD/CRWV retain null CIKs in the default
unreconciled environment. CIK42/43 in SEC tests are explicitly fictional fixtures.

This does **not** deliver or claim complete current US-listed coverage,full financial
history,live-provider qualification,observed-market reconstruction,ARM64 qualification
of the new commits or production readiness. The current software can now acquire
and measure its declared account-reference/source scope when configured and authorized.

## Implementation and requirement matrix

| Requirement | Implementation / source path | Status |
|---|---|---|
| Broad authoritative discovery | Existing Nasdaq two-file adapter and SEC registry retained;new `terminal/stocks/alpaca_reference.py` uses fixed paper GET `/v2/assets` for active and inactive `us_equity` | IMPLEMENTED AND TESTED;actual ingestion BLOCKED by credentials/access/review |
| Automatic initialization/refresh | Normal server starts asset worker when configured;startup/six-hour refresh,300s manual cooldown,explicit disable/enable;private catalog/Nasdaq selection takes default precedence | IMPLEMENTED AND TESTED;not source-qualified |
| Search,index,pagination | Existing indexed exact/prefix/name-word search,20-row browser pages;server filters exchange,security classification and source status before pagination | IMPLEMENTED AND TESTED |
| Asset identity/classification | Canonical UUID,exact provider symbol,exchange,active/inactive and explicit flags;duplicate UUID/symbol reject;unsupported symbols counted,share-class punctuation retained | IMPLEMENTED AND TESTED;US-equity subtype remains unverified;no name-inferred ETF/common/preferred classification |
| Graceful catalog recovery | Both bounded responses validated before one publication;failure/allocation error preserves prior catalog;cached provider-ID changes or missing protected identities reject | IMPLEMENTED AND TESTED |
| SEC identity | Existing authoritative registry/cache/CIK conflict checks;qualification CLI now has `--resolve-identity` for non-seed tickers | IMPLEMENTED AND TESTED;actual seven-company reconciliation BLOCKED by missing identifying configuration/access |
| SEC financials/filings | Existing Company Facts,selected reported concepts,exact period-aware descriptors,filing/amendment/acceptance views and bounded older shards retained | EXISTING IMPLEMENTATION REGRESSION-PASSED;complete statements/full historical PIT coverage remain PARTIAL,not invented |
| Historical bars | New `alpaca_history.py`:fixed bulk endpoint,Daily/Hourly/Minute,date bounds,pagination,exact decimals,OHLC/order validation,source receipts | IMPLEMENTED AND TESTED;MOCK-QUALIFIED ONLY |
| Historical quotes/trades | New bounded bulk reads,preserved nanosecond timestamps,source IDs/exchange/condition annotations,marked duplicates,no corrected-tape claim | IMPLEMENTED AND TESTED;MOCK-QUALIFIED ONLY |
| Rate limits/resource control | Existing one REST request/second,429/503 cooldown,no automatic HTTP retries;four pending history requests,total25s operation budget,coalesced identical intervals | IMPLEMENTED AND TESTED |
| Historical retention | At most16 accepted queries in process memory;four pages×64 records/query,60s accepted-result reuse;no disk retention enabled | IMPLEMENTED AND TESTED;observed storage still separately permission-gated |
| Real-time Level1 | Existing `live.py`:fixed IEX WSS,quotes/trades/bars,shared upstream,1–4 symbols,acknowledged in-place changes,backoff/ping/health,256-event/identity windows | EXISTING IMPLEMENTATION REGRESSION-PASSED;actual provider qualification BLOCKED |
| Securities Universe | Separate Nasdaq/SEC/Alpaca refresh controls,source counts/timestamps,exchange/classification/activity filters,company routing | IMPLEMENTED AND BROWSER-VERIFIED WITH FIXTURES |
| Stock Intelligence | Existing SEC financial research retained;new historical observations panel,source-kind/date/timeframe controls,OHLC chart,exact table and page receipts | IMPLEMENTED AND BROWSER-VERIFIED WITH FIXTURES |
| Multi-stock workflows | Existing watches/subscriptions/quote comparison retained;new raw-close comparison uses exact common timestamps and first common close | IMPLEMENTED AND BROWSER-VERIFIED WITH FIXTURES;not consolidated total returns |
| Command Center | Research desk now recognizes accepted provider-reference count separately from official listing count | IMPLEMENTED AND BROWSER-REGRESSION-PASSED |
| 3D | Existing four L1 modes,independent cameras/fallbacks,modeled GARCH and separate native L3 unchanged | PRESERVED;browser/context-loss regressions passed;not observed depth |
| Credential status | Existing ALPACA/APCA aliases and conflict checks;configuration checker returns readiness/presence only;new CLI receipts contain no key values | IMPLEMENTED AND TESTED;actual credential usability UNVERIFIED |
| Research-only boundary | `alpaca_transport.py` permits fixed market-read paths and only paper `/v2/assets`;transport method is GET;no trading/account/position client or arbitrary host | IMPLEMENTED AND TESTED |
| Native/package compatibility | No include/src/python/CMake/schema changes;native consumers,frozen references,installed wheel and source inventory pass | LOCAL VERIFIED;new exact-candidate hosted/ARM64 remains externally unqualified |

## Source evidence and rights

Official Alpaca SDK repository `alpacahq/alpaca-py`,pinned commit
`1b7bf9b922944adc8823ccf88ada5ea4646877ca`,was inspected through permitted official
GitHub URLs. Public reference receipts/hashes are in `phase_next_evidence.json`:

* `alpaca/trading/client.py:375`–396 documents asset master references and GET `/assets`;
  `trading/requests.py:134`–148 defines status/asset_class/exchange filters.
* `alpaca/common/enums.py:23` fixes the paper base;market-data bases are separate.
* `alpaca/data/historical/stock.py:75`–138 identifies bulk bars/quotes/trades paths.
* `alpaca/data/requests.py:20` onward documents UTC time bounds,sorting and symbol
  requests;`common/rest.py` demonstrates `next_page_token` and grouped response handling.

No SDK dependency was installed or trading client imported. The SDK's Apache2 code
license is **not** a license to use/retain/redistribute account market data. The owner's
paper-account research authorization remains subject to existing actual entitlements
and usage gates. No claim of SIP,OPRA,NBBO,depth,paid-tier access or free account-specific
entitlement verification is made. Fixed `feed=iex` has no paid fallback.

Prior Nasdaq definitions/terms/HEAD metadata remain in the source ledger. Directory
body/derived-cloud rights remain unestablished;no directory body was acquired. SEC
registrants are not a complete listed-security universe. Alpaca asset records are
authoritative for that provider/account reference,including inactive or OTC records
if supplied;they are not a complete independently verified primary-exchange master.
NYSE/Cboe alternative rights/formats/access remain unverified,not silently substituted.

## Architecture and exact bounds

`AssetReference` shares the existing upstream lock/pacing. It reads two fixed paper
asset arrays,8MiB each,at most50000 source rows per response and50000 accepted combined
identities. Response JSON forbids duplicate fields/nonfinite constants;UUID,symbol,
status,text and boolean flag validation precede indexing. No raw directory is persisted.
Real source sizes/schema need qualification;an exceeded cap rejects instead of truncating
and may require a separately reviewed resource plan. Source exclusions are counted.

The normal factory enables automatic assets only when no explicit private catalog or
approved Nasdaq catalog takes precedence. `GIG_ALPACA_ASSET_REFERENCE_ENABLED=0` disables
automatic refresh;1 explicitly selects its automatic path. Injected tests do not acquire
implicitly. Manual refresh requires existing Alpaca permission and exact endpoint-bound
mutation proof. An explicit successful manual refresh replaces the in-memory primary
catalog with its disclosed source;it does not merge guessed cross-source security IDs.
SEC mappings remain a separate exact-symbol union. Source status is cache-only on GET.

Historical reads accept one known symbol,kind and inclusive UTC dates. Daily spans
at most366 calendar dates,hourly31,minute7;quotes/trades2. Each page≤512KiB/64 records;
at most4 pages/256 records. Source timestamps must lie in the requested interval;
bars strictly increase,quotes/trades retain equal-timestamp source order. Token cycles,
empty continuing pages,foreign symbols,bad OHLC,numeric/time bounds and invalid metadata
reject the operation without replacing accepted cache. Duplicate observations remain
marked;no exchange sequence or exactly-once guarantee is invented. Pagination tokens
never appear in receipts or frontend URLs. `has_more` is explicit at the page budget.

Four historical requests may wait/process,with25 seconds including local lock wait.
Identical queued intervals reuse a newly accepted result. Permission and instrument
metadata are checked again after local waiting. Sixteen bounded queries are retained
in memory;60-second reuse preserves original receipts/hashes and rechecks permissions.
Cancellation releases lock/capacity and does not publish a partial result. Existing
observed-storage gates are not enabled by this in-memory research path.

Price/time wire values remain source strings;decimal calculations avoid float parsing.
Browser geometry and historical comparison percentages are approximate binary64
visualization,not replacement financial descriptors. A comparison uses only identical
source timestamps in all series,raw closes and one shared percentage scale. No missing
bar is filled;no dividend-adjusted,total-market or synchronized investment return is
claimed. The price chart is rank-spaced over returned observations,not missing intervals.

## Defects/recovery findings

1. Asset startup could lose the first six hours when SEC initialization owned the lock.
   A new regression fails on `e6feab0`'s worker. Automatic initialization now waits within
   a55-second local budget;remote rejection is not retried. Explicit private catalog
   precedence is tested rather than overwriting the configured source implicitly.
2. Retained provider identities could be relabelled after a symbol's asset UUID changed.
   Publication now refuses changed/missing protected identities;cache/catalog remain
   unchanged. History results also retain the exact instrument-reference metadata used.
3. A history request could reject immediately while company loading held the local lock.
   Regression on `4bcbb5e` fails with `upstream_refresh_busy`. Bounded queue/coalescing
   repairs the workflow without remote retry,larger timeouts or disabled validation.

Early validation failures are preserved under `build/phase-next/`:an absent AMZN in an
authored fixture,Playwright relative API URL without a base URL,a shared mutable test
environment,and a404 expectation for the SPA's correct405 unsupported POST. Fixtures
and harness construction were corrected,not production assertions weakened. The old
fixture also returned AAPL-labelled data for CRWV;production correctly rejected that
and applied its cooldown. The new fixture authors the requested symbol and proper
option underlying. No source identity checks/cooldowns were bypassed. Earlier failed
browser logs and both failing-before reproductions remain available and hashed.

## Actual final validation

All listed final cohorts have zero failures/errors/skips. Counts are outcomes per
suite/configuration,not unique tests;some suites overlap. No new hosted/ARM64 run launched.

| Cohort | Result | Local log prefix `build/phase-next/` |
|---|---:|---|
| Stock/provider/SEC/backend Debug |207/207|`stocks-final-qualified-debug.log`|
| Same,Release |207/207|`stocks-final-qualified-release.log`|
| Same,ASan+UBSan binding |207/207;liveLSan0|`stocks-final-qualified-sanitizer.log`|
| Terminal/native consumers Debug |274/274|`terminal-delivery-debug.log`|
| Same,Release |274/274|`terminal-delivery-release.log`|
| Same,ASan+UBSan binding |274/274;liveLSan0|`terminal-delivery-sanitizer.log`|
| Frontend contracts/numeric references |45/45|`frontend-final.log`|
| Seven stable-asset browser suites |91/91|`stable-browser/`|
| Additional ratio/live/SEC/discovery/GPU browsers |50/50|`regression-browser/`|
| New reference/filter/history browser |10/10|`browser-final-qualification.log`|
| Origin/proof/security |53/53|`security-final.log`|
| Verified local HTTPS/WSS proxy |8/8|`tls.log`|
| Frozen native independent cases |8/8;all8 hashes unchanged|`canonical.xml`|
| Installed existing0.1.1 wheel |14/14|`wheel-consumer.log`|
| Packaging regressions |3/3|`packaging.log`|
| Source archive at implementation checkpoint |819 safe byte-identical members|`sdist-final-inventory.log`|
| New Alpaca CLI safety |4/4|`cli-safety.log`|

The sanitizer wrapper checks the live interpreter's LSan roots;it does not claim stock
CPython shutdown leak qualification. Native C++ sources did not change,so unrelated
full GCC/Clang rebuilds were not repeated. The bindings above are the existing supported
local native builds. Starlette TestClient deprecation and deferred >500kB chunk warnings
were retained. The evidence manifest binds receipts,source/asset hashes,counts and captures.

## Browser and performance observations

Ordinary clicks/select/check actions exercise the real native-backed application with
independently authored provider bytes. No forced click. Seven original suites build
once and assert unchanged assets throughout;the new journey runs afterward. Existing
NVDA-to-AAPL selection,financial source/period integrity,replay,simulation,themes and
WebGL recovery regressions remain. All12 workspaces fit60 width/section and120 theme
combinations. Populated historical controls also fit360/390/768/1280/1920px.

New captures (local,synthetic,not committed data):
`build/phase-next/historical-comparison-synthetic.png` and
`historical-mobile-synthetic.png`. Their images were inspected;exact tables/source
receipts,clear historical labels and inner scrolling remain usable. Previous captures
were archived under `build/phase-next/prior-captures/` before regression output refresh.
No external Codespaces authentication,physical Android,GPU FPS or screen-reader claim.

Measured x86-64 local/shared host:

* 11000 authored assets:median parse/index0.1266s (one warmup,three repetitions);
 process high-water RSS64140KiB,including dependencies/native test imports.
* 50002 authored directory identities:parse/index0.4587s;exact search0.0070ms,
 1000-hit ticker prefix0.0385ms,broad50000-hit name query31.63ms median;RSS82068KiB.
* Initial entry JS235735 bytes;optional Three/OrbitControls remains deferred. Three
 measured cold-context navigation/settle samples739/783/784ms;Stock Intelligence
 route145–161ms;sampled JS heap4.35–4.55MB. These include loopback/networkidle wait,
 not production latency;uncontrolled prior/current samples are not a causal speedup.

No real-provider throughput,latency,source completeness or sustained GPU memory result
is inferred. Full test/performance/source receipts are in `phase_next_evidence.json`.

## Delivery and remaining gates

| Commit | Checkpoint |
|---|---|
|`e6feab0f804b6a37ffeaf91433e514dfdbcccd3b`|Read-only provider reference/history infrastructure|
|`4bcbb5e86a730746edd7a4c8db38f034d761cf44`|Startup wait and retained asset-ID protection|
|`6ce1382228227a163f71dc5368c56ef2548497e5`|Bounded local history queue/coalescing and private-source precedence|
|`1ea9c86e0fc3273ae102032478fa641d18f2b9a9`|Historical/filter institutional UI and ordinary-click validation|
|`89d06adb973c4a3f5cb8f3da3e734721a63bfe02`|Non-seed authoritative SEC qualification path|

Every implementation milestone was pushed and its exact remote SHA checked. Git diff
review shows no native/source schema or main changes. No secret,raw market data,ZIP,
generated bundle,SDK source dump or screenshot binary is committed.

Remaining external gates:repository-scoped paper credentials;documented no-cost feed,
private display/cloud use and separate retention rights;appropriate official-host access;
ready existing SEC identifying configuration;actual source-body/account/API qualification;
exact-candidate native ARM64/hosted and independent device/product acceptance. Full
historical financial/PIT archives,corrected complete tape,official halt/calendar authority
and comprehensive listing-master equivalence remain outside the bounded verified claim.
Account-wide socket/subscription/rate limits may also include the separate GIG Quant
Terminal's activity. Local1–4-symbol/shared-socket/request limits do not establish an
independent account quota. That project and its credentials were not accessed or changed.
Byte/row limits are explicit,but a fixed process-RSS ceiling is not implemented;the
reported memory samples are representative fixtures,not worst-case heap qualification.

See [private setup/qualification guide](ALPACA_RESEARCH_DATA_SETUP.md). No intermediate
owner manual UI test was requested. The next milestone is actual source-backed coverage
and provider qualification under authorized configuration,not a restart or a speculative
rewrite. Engineering here is implemented/fixture-qualified;live qualification is blocked.
