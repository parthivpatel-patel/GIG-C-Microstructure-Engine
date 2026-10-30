# Final bounded-research requirement matrix

October 29, 2026 (America/New_York). Starting checkpoint `73d6725898f54ad97ff926e674e93f137c3d1fd7`.
Current executed counts, source fingerprints and command receipts are in
`evidence.json`;this is a source-level self-review with independent fixture/reference
calculations,not an external institutional audit or owner acceptance.

## Master directive phases

| Phase | Actual implementation and evidence | Engineering classification | Observed/target boundary |
|---|---|---|---|
| A IEX stream | `stocks/live.py`, `live_metrics.py`, `server/market_events.py`, `market_delta.py`;207 provider/stock tests plus94 source qualification cases/configuration | IMPLEMENTED AND FIXTURE-VERIFIED | No actual IEX observation received here;existing cloud/private-display gates stay disabled |
| B historical | `alpaca_history.py`, `historicalMarket.ts`, `HistoricalMarket.tsx`;bounded daily/hour/minute profiles,source clocks,raw adjustment,pagination,common-time comparison and negative controls | IMPLEMENTED AND FIXTURE-VERIFIED | Actual AAPL/MSFT IEX responses unqualified;partial pages/empty intervals remain explicit |
| C catalog | `alpaca_reference.py`, `market_catalog.py`, `discovery.py`, `UniverseWorkspace.tsx`;active/inactive us_equity,bounded UUID/symbol/reference checks,search/filter/cache | IMPLEMENTED AND FIXTURE-VERIFIED | Actual imported/searchable count in owner environment unknown;not a complete US master |
| D SEC | `sec_identity.py`, `service.py`, `sec.py`, `sec_history.py`, `vintages.py`, qualification tools;explicit routable-subset accounting,new13 boundary cases and existing26 CLI regressions | REPAIRED AND FIXTURE-VERIFIED | Owner reports ready identifying config and observed sec_directory_symbol;exact offending live entry and actual retrieval unverified here |
| E other sources | Existing `product/SOURCE_ACCESS_LEDGER.md` reviewed;official Nasdaq directory importer/rights gate and pinned official Alpaca SDK interface references reused | REVIEWED;NO UNJUSTIFIED NEW PROVIDER | Nasdaq directory-use/cloud rights unresolved;SEC registrants are not exchange listings. NYSE/Cboe rights/availability unverified. No extra acquisition justified |
| F end-to-end | Provider adapters → strict contracts → accepted state → bounded push → actual TS analytics/visuals;357 final browser checks across24 cohorts including performance | IMPLEMENTED AND FIXTURE-VERIFIED | Real source-to-private-target path needs one final session;fixture fallback is never relabeled observed |
| G workspaces | Exact12 names below;120 theme/width checks plus actual functional journeys | IMPLEMENTED AND AUTOMATED-VERIFIED | Owner's actual desktop/Android acceptance pending |
| H visualizations | Exact13 modes below;geometry/numerical tests,camera,input/fallback/cleanup/browser assertions;three emulated-touch renderer families | IMPLEMENTED AND AUTOMATED-VERIFIED | SwiftShader/Chromium,not physical GPU certification;live depth unavailable |
| I native | Existing engine/bindings preserved;full GCC Python-enabled158/158/159 CTest and Clang155/155/155;all8 frozen identities unchanged across6 configurations | PRESERVED AND LOCALLY VERIFIED | x86_64 only in this assignment;no current-candidate ARM64/hosted run |
| J security/reliability | Exact Origin/Host/proofs,permission/retention guards,source validation,rate/time/body budgets,cleanup;52 security/policy cases,8 real local TLS/WSS checks,NPM0 and official PyPI metadata0 across17 pinned server requirements | PASS WITH DECLARED SCOPE | Local proxy is not proof of actual Codespaces authentication;not a comprehensive penetration test or full transitive/OS advisory certification |
| K UI | Existing professional dark/light design retained;SEC subset disclosures and truthful refresh error;finite L1 display geometry repaired | VERIFIED IN FINAL BROWSER CAMPAIGN | Physical touch,device performance and final preferences need owner acceptance |
| L comprehensive tests | Exact commands/log receipts in evidence;zero final failures/errors/skips;original failing-before evidence retained | COMPLETED LOCALLY | Actual providers/current hosted ARM64 unexecuted;not replaced by fixtures |
| M release package | Final engineering report,matrix,evidence,private acceptance instructions and source archive inventory | COMPLETED FOR PRIVATE CANDIDATE | No tag,release,main merge or production authorization |
| N owner acceptance | One sequential final procedure;existing config reused,source-stage results separated from final acceptance | PREPARED;NOT EXECUTED | Only owner/source/target evidence can close Milestone2 |

## All twelve actual workspaces

Every row was navigated through ordinary controls at360/390/768/1280/1920px in both
themes. These120 matrix checks supplement functional browser journeys,not a product
completeness percentage. Original native replay/simulation functionality remains.

| Workspace | Actual path/function | Source and automated acceptance |
|---|---|---|
| Command Center | `ResearchDesk.tsx`, `App.tsx`;source/research entry points and status | Real native fixture transport,no invented live summary;browser/product journeys |
| Securities Universe | `UniverseWorkspace.tsx`, `discovery.py`;search,filters,pagination,refresh,company routing | Source classes separated;SEC source/accepted/excluded counts verified in actual browser |
| Stock Intelligence | `StockIntelligence.tsx`, financial views,v2 company/filing APIs | Selected facts,ratios,filing references,period filters,quality/empty states;NVDA/AAPL switching preserved |
| Live Markets | `LiveMarket.tsx`;watchlist,shared subscriptions,quote/trade cards,history,health | Explicitly authored IEX-shaped observations;limits/freshness/pause/reconnect tested |
| Multi-Stock Comparison | `LiveMarket.tsx`, `HistoricalMarket.tsx`;coordinated L1 and historical comparisons | Source-time alignment and separate per-symbol state;no synchronized-return inference from unmatched live baselines |
| Order Book | Native session + `App.tsx`;actual C++ snapshot/order state | Authored native state;never expanded from equity L1 |
| Market Depth | `Landscape3D.tsx`, `ResearchLab.tsx`;supplied depth and advanced models | Authored/replay source explicit;missing depth stays unavailable |
| Order Flow | `App.tsx`, native analytics/event tape | Only actual retained native event/analytic capability;not inferred aggressors from IEX |
| Historical Replay | Native replay controls,recorded playback | Deterministic seek/step/restart and source restrictions;no false complete initialization |
| Execution Simulator | Native simulation form,fill/cost/research results | Simulation only;no broker/account/order/position endpoint |
| Research & Validation | `ModelSurface.tsx`, `ResearchDiagnostics.tsx`, model/evaluation services | Declared HMM/GARCH/Kalman/risk/holdout results;no forecast efficacy claim |
| Operations | `MarketHealth.tsx`, source/transport/service diagnostics | Sanitized configuration/health/limits;credentials never rendered |

## All thirteen existing visualization modes

The final browser campaign preserves every mode. Underlying renderer touch behavior
was exercised in emulated390px Chromium for Level1,research and GARCH families with
nonempty authored/model inputs;this is not physical Android qualification.

| Mode | Actual component | Eligible data and interpretation |
|---|---|---|
| L1 quote evolution | `QuoteCloud.tsx`, `marketGeometry.ts` | Authorized quotes when available;per-symbol normalized prices,not depth |
| L1 coordinated midprice change | Same | First retained valid midpoint per symbol;baselines can have different times;nonrepresentable display changes explicitly omitted |
| L1 rolling variation | Same | Nine ordered positive quotes for eight log returns;stable across admitted binary64 extremes;not annualized |
| L1 trade activity | Same | Actual/fixture prints;log source size,not inferred order flow or a corrected tape |
| GARCH surface | `ModelSurface.tsx` | Declared fixed-parameter variance grid;modeled,not observed/implied volatility |
| Order-book height-map surface | `ResearchLab.tsx`, `ResearchScene.tsx`, `research3d.ts` | Supplied native depth or authored fixture;display interpolation explicitly labeled |
| V-canyon liquidity | Same | Derived cumulative supplied depth;no missing levels invented |
| Order-event voxels/point cloud | Same | Explicit authored order events;never inferred from coalesced snapshots |
| VWAP liquidity corridor | Same | Explicit execution price/quantity records only;native snapshot/L1 quote input alone ineligible |
| Order-flow streamlines/VPIN | Same | Explicit directions in authored events;toy uncalibrated VPIN,not observed toxicity |
| Cylindrical depth wheel | Same | Supplied depth;angle is categorical level rank |
| Volatility dome | Same | Eligible retained quote variation with modeled shape;not implied volatility |
| Bid-ask spread ribbon | Same | Eligible best quotes,including retained authorized L1;display joins do not create observations |

## Stop/continue classification

Essential independent engineering and final automated gates are complete for this
bounded private research contract. No speculative provider or model was added.
The external source/private-target/device/owner gates remain OPEN,not failed tests
or silently deferred engineering. Complete US security-master certification,full XBRL
presentation reconstruction,full original-availability PIT history,corrected lossless
market tapes,hot live recovery,SIP/OPRA/live depth,trading,formal accessibility
certification and empirical forecasting efficacy remain explicitly outside this
implemented contract. Do not advertise them as complete.
