# GIG ATLAS overnight scope and gap inventory

October 29, 2026, America/New_York. Starting checkpoint:
`e6517314cb843cdad1e14281dbcd1001e7bee6d5`, `feat/atlas-final-release`.
This is a targeted source-level engineering review with independently calculated
fixtures, not an external institutional audit or proof of absence of defects.
COMPLETE below always means the stated bounded contract; empirical qualification is
a separate column. Test receipts are in `overnight_evidence.json` after final validation.

## Implemented components and actionable gaps

| Component | Status | Actual implementation / relevant tests | Remaining work or boundary |
|---|---|---|---|
| C++20 numeric/event contracts | COMPLETE | `include/gig/core/numeric.hpp`, `events/contracts.hpp`, `src/events/validation.cpp`; `test_types`, `test_numeric`, `test_events` | Strong distinct types, exact conversions and explicit failure results;not arbitrary precision |
| L3 FIFO book | COMPLETE synthetic contract | `src/book/order_book.cpp`, `include/gig/book/order_book.hpp`; invariant/reference/allocation tests | No exchange-equivalent or observed full-L3 claim without complete initialization/reference |
| Replay/journal/recovery | COMPLETE bounded contract | `src/replay/replay.cpp`, `canonical.cpp`; replay,journal storage,allocation,equivalence tests | 100000-record cap;substantial record overhead;not crash-safe continuous market capture |
| Synthetic matching/latency | COMPLETE synthetic contract | `src/simulation/simulator.cpp`; simulation/reference tests | Discrete deterministic assumptions,not calibrated queue/latency or live execution |
| TWAP/VWAP/POV/TCA | COMPLETE bounded mathematics | `src/execution/execution.cpp`; execution/cost/reference tests | Ex-ante versus hindsight profiles explicit;no real fills,broker or execution-quality calibration |
| Microstructure book/flow analytics | COMPLETE bounded mathematics | `src/analytics/book_metrics.cpp`, `flow_metrics.cpp`; quote lag,OFI,classification,impact/missingness tests | Clock/continuity assumptions required;single-venue L1 is not complete depth or aggressor evidence |
| ITCH framing/decode/context/reconstruction | COMPLETE authored profiles | `src/itch/{binary_file,decoder,context,reconstruction,streaming,restart}.cpp`;8 frozen reference families plus adversarial tests | Explicit unsupported semantics and initial-state eligibility;no complete observed archive reconstructed here |
| Historical LOBSTER | BLOCKED empirical / COMPLETE synthetic adapter | `src/lobster/adapter.cpp`, `reconstruction.cpp`; parser/workflow/differential tests | Attached private sample remains unprocessed pending cloud-use authorization;five-level reference cannot establish full L3 |
| Native/Python interfaces | COMPLETE local contract | `python/gig_microstructure`, bindings and consumer/export/packaging tests | Exact-candidate hosted/ARM64 and independent-machine evidence remain external |
| Fixed Gaussian HMM | COMPLETE bounded library filter after repair | `terminal/stocks/advanced_models.py:missing_hmm`; overnight Decimal path enumeration,capacity,missingness,prefix tests | Library-only custom missing-emission profile;no UI for arbitrary parameters or empirical regime truth |
| Fitted two-state HMM | COMPLETE diagnostic algorithm | `models.py:fit_hmm`, `hmm_filter`; likelihood/label/constant/causal-holdout tests | Local EM optimum/floors;full-sample historical probabilities have parameter-estimation look-ahead;not predictive signals |
| GARCH(1,1) grid and coordinate search | COMPLETE diagnostic algorithms | `models.py:fit_garch`, `advanced_models.py:optimize_garch`; independent recursion/likelihood/constraint tests | Gaussian conditional likelihood,fixed mean/initial variance;no global MLE,uncertainty or efficacy claim |
| Kalman state estimation | COMPLETE fixed local-level filter | `models.py:kalman`;Joseph covariance/missing observation tests;research workflow | Fixed Q/R,not calibrated general multivariate state-space estimation |
| Realized volatility/descriptive price risk | COMPLETE bounded descriptors | `risk.py`, `price_research.py`, `live_metrics.py`, `marketGeometry.ts`;exact references/finite range tests | Unadjusted/gappy retained intervals,not annualized or a calibrated forecast |
| Portfolio/risk decomposition | COMPLETE explicit-weight analysis | `portfolio.py`;exact covariance,w'Σw,correlation,VaR/ES,drawdown,scenario tests | Caller-declared aligned intervals;no inferred holdings,FX,tail calibration or portfolio optimization |
| Backtest / chronological evaluation | COMPLETE declared authored rules | `research.py`, `evaluation.py`;lagged-position,cost,train-only and future-mutation tests | Fixed-rule toy strategy,max4 expanding folds;no selection-adjusted profitability or authenticated PIT data |
| SEC directory/financial ingestion | COMPLETE bounded engineering / BLOCKED live qualification | `sec_identity.py`, `sec.py`, `sec_history.py`, `service.py`;strict source/identity/period suites | v3 terminal-marker repair fixture-verified;actual current directory/facts must qualify in owner Codespace |
| SEC point-in-time/provenance | PARTIAL empirical coverage | `vintages.py`, historical filings,acceptance-time filtering,source fact/revision hashes | Acceptance times improve known filing scope;current restated companyfacts cannot establish complete original historical availability/full XBRL statements |
| Alpaca catalog/history/IEX | COMPLETE bounded adapters / BLOCKED live qualification | `alpaca_reference.py`, `alpaca_history.py`, `live.py`;shared subscription/ACK/order/dedup/reconnect/quiet-feed tests | Credentials reported ready in Codespaces;applicable private/cloud/display rights and actual observations not verified here;gates unchanged |
| Broad symbol discovery | COMPLETE source-separated infrastructure / PARTIAL coverage | `market_catalog.py`, `directory.py`, `discovery.py`;AAPL/APLD/CRWV discovery and exact/null CIK tests | No imported live count here;SEC registrants are not complete listed securities;fallback counts are not provider coverage |
| Persistence and recovery | COMPLETE bounded private implementation | `history_store.py`, `observation_store.py`, `datasets.py`;SQLite crash/hash/expiry/atomic publication tests | Observed retention stays disabled unless separately permitted;no lossless tape,hot recovery,hard global storage quota or physical-erasure guarantee |
| Backend analytical resource admission | COMPLETE repaired engineering | `server/analysis.py`, analytical routes in `app.py`;canceled-request,shared-budget,repeated-cancel,drain/error tests | One physical analytical worker per application/event loop;not global machine/cluster quota or a hard preemptive CPU deadline |
| Browser push and private transport | COMPLETE local protocol / BLOCKED target qualification | `market_events.py`, `market_delta.py`, request proofs,tickets,exact Origin/Host;SSE/WS/TLS/security tests | Latest-state coalescing,not lossless exactly-once delivery;actual private Codespaces authentication must be accepted on target |
| Institutional browser / mobile | COMPLETE authored journeys / PARTIAL accessibility certification | Actual React/TS workspaces,source badges,lazy renderers;ordinary-click/theme/viewport/keyboard tests | Chromium/SwiftShader/emulated touch,not physical Android/GPU or formal WCAG/screen-reader certification |
| Deployment/startup/package | COMPLETE local engineering | `start_terminal.sh`, config helpers,CMake,locked server requirements,anchored sdist inventory | No persistent Cloud browser hosting or public release is promised;private Codespace process lifetime remains operational |
| Security/entitlements/trading | COMPLETE tested research boundary | Fixed origins/hosts/proofs,redaction,budgets,provider and storage gates,read-only adapters | Not an external penetration test/legal entitlement opinion;no trading/purchases/feed activation authorized |

## Candidate quantitative areas that do not justify speculative additions

| Candidate | Classification | Reason / prerequisite |
|---|---|---|
| Cointegration / statistical arbitrage | OUT OF SCOPE for current bounded release | No agreed estimator,stationarity testing/multiple-testing policy,pairs universe or execution/cost contract. Price comparison alone is not cointegration evidence |
| Mean-reversion strategy estimation | OUT OF SCOPE extension | Existing lagged authored strategy is implemented;fitted OU/pairs strategies need a separate mathematical/data/validation contract |
| Cross-sectional factor research | OUT OF SCOPE extension | Needs survivorship-safe historical universe,corporate actions,publication-time fundamentals and aligned observations. Current SEC registrant directory is not that dataset |
| Portfolio optimization | OUT OF SCOPE extension | Existing explicit-weight portfolio analysis is complete;an optimizer needs constraints,cost model,conditioning/estimation choices and independently specified optimality tests |
| EGARCH/GJR/stochastic/implied volatility | OUT OF SCOPE extension | Existing Gaussian GARCH and modeled surfaces are the scoped capability. No calibrated options surface or empirical forecasting claim is justified |
| VPIN / flow toxicity calibration | PARTIAL research illustration | `research3d.ts` computes declared toy buckets from explicit event directions. Real L1 prints lack authoritative trade signs/full volume;no empirical toxicity claimed |
| Market impact / trade classification | COMPLETE conditional research mathematics;BLOCKED calibration | Native quote-lag classification/impact exist;observed causal evaluation needs venue coverage,source continuity and suitable independent reference |

## Twelve workspace integration paths

| Workspace | Actual path | Status and interpretation |
|---|---|---|
| Command Center | `ResearchDesk.tsx`, `App.tsx` | COMPLETE source/status/research navigation;no fabricated market overview |
| Securities Universe | `UniverseWorkspace.tsx`, discovery APIs | COMPLETE bounded search/filter/pagination/exact identity routing;coverage source-specific |
| Stock Intelligence | `StockIntelligence.tsx`, `FinancialWorkspace.tsx`,v2 APIs | COMPLETE selected reported facts/periods/ratios/filings and safe missingness;not complete financial statements |
| Live Markets | `LiveMarket.tsx`, `market_events.py`, `live.py` | COMPLETE bounded authorized L1 path;actual provider qualification BLOCKED here |
| Multi-Stock Comparison | `LiveMarket.tsx`, `HistoricalMarket.tsx` | COMPLETE exact-common-time historical and independently labeled live baselines;not portfolio holdings |
| Order Book | Native `NativeSession` → `App.tsx` | COMPLETE native authored/replay state,not reconstructed from equity L1 |
| Market Depth | `Landscape3D.tsx`, `ResearchLab.tsx` | COMPLETE supplied depth/geometry/fallback;live L2/L3 entitlement absent |
| Order Flow | Native analytics/event tape → `App.tsx` | COMPLETE retained native observations;no invented print aggressors |
| Historical Replay | Native replay/session controls | COMPLETE deterministic supplied-source seek/step/restart;initialization restrictions remain |
| Execution Simulator | Native simulator/schedule/cost APIs and form | COMPLETE synthetic simulation only;no account/order placement |
| Research & Validation | `ResearchDiagnostics.tsx`, `ModelSurface.tsx`, evaluation/dataset APIs | COMPLETE bounded diagnostics/holdouts;analytical cancellation/resource defect repaired |
| Operations | `MarketHealth.tsx`, sanitized health/source diagnostics | COMPLETE available status/limits/error visibility;no credentials or empirical success invented |

## Thirteen visualization modes

| Mode | Actual code | Eligible input / status |
|---|---|---|
| L1 quote evolution | `QuoteCloud.tsx`, `marketGeometry.ts` | COMPLETE;retained best quotes,not depth |
| L1 comparative midprice change | Same | COMPLETE;per-symbol retained baseline,not synchronized total returns |
| L1 rolling variation | Same | COMPLETE;ordered quotes/enough returns,not annualized forecast |
| L1 trade activity | Same | COMPLETE;actual/fixture prints,not inferred depth/queue |
| GARCH surface | `ModelSurface.tsx`, `modelSurface.ts` | COMPLETE;declared modeled variance grid |
| Book height surface | `ResearchLab.tsx`, `ResearchScene.tsx`, `research3d.ts` | COMPLETE;supplied/replay depth with labeled display interpolation |
| V-canyon | Same | COMPLETE;derived cumulative supplied depth |
| Event voxels / points | Same | COMPLETE;explicit event input only |
| VWAP corridor | Same | COMPLETE;explicit executions required,not generated from quotes |
| Flow / VPIN illustration | Same | COMPLETE toy projection;PARTIAL empirical calibration,explicit directions required |
| Depth wheel | Same | COMPLETE;categorical level angle,not circular market mechanics |
| Volatility dome | Same | COMPLETE;eligible retained variation plus modeled geometry,not implied volatility |
| Spread ribbon | Same | COMPLETE;best-quote observations and labeled display joins |

## Remaining acceptance and engineering decision

The two newly reproduced software defects are repaired and offline-verified. No
other essential independently implementable gap was established by this
review. Do not turn the candidate-area list into another unapproved model expansion.
Required external work remains:actual SEC requalification,current lawful Alpaca
catalog/history/IEX observations,private target authentication and real desktop/Android
acceptance,exact-candidate hosted/ARM64 qualification if required,and independent
observed L3/PIT/calibration evidence before broader claims. Production trading remains
OUT OF SCOPE. See `MORNING_ACCEPTANCE.md` for the short source/target sequence.
