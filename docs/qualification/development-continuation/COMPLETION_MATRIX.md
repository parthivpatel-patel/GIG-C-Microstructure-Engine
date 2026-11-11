# GIG development completion matrix — November11,2026

Current runtime source `0c4196b2e0270dacfa07638c2c5d94f3de54cb49`;branch `development/gig-ui-redesign`.

50entries =previous49entries +explicitly requested Kraken official-L2 requirement MD07;49reviewed areas +1historical A18/A19 decision. No previous row removed.

**34COMPLETE /8PARTIAL /7BLOCKED /1NOT APPLICABLE. Full development is not complete.**

COMPLETE means stated bounded code contract exists and has cited automated evidence,not actual provider or owner acceptance. PARTIAL/NOT IMPLEMENTED remain explicit;blocked external evidence is not relabeled a missing UI feature.

|ID|Status|Requirement|
|---|---|---|
|CORE01|COMPLETE|C++20 typed order book,identity,FIFO and exact arithmetic|
|CORE02|COMPLETE|ITCH framing,decoding,context and synthetic L3 reconstruction|
|CORE03|COMPLETE|Python/native integration and native-backed browser|
|CORE04|COMPLETE|Deterministic replay,journal and recovery contracts|
|CORE05|BLOCKED|Complete observed historical Level 3 validation|
|UI01|COMPLETE|GIG-only branding,application shell,search,themes and navigation|
|UI02|COMPLETE|Command Center workspace|
|UI03|COMPLETE|Securities Universe workspace|
|UI04|COMPLETE|Stock Intelligence workspace|
|UI05|COMPLETE|Live Markets workspace|
|UI06|COMPLETE|Multi-Stock Comparison workspace|
|UI07|COMPLETE|Order Book workspace|
|UI08|COMPLETE|Market Depth workspace|
|UI09|COMPLETE|Order Flow workspace|
|UI10|COMPLETE|Historical Replay workspace|
|UI11|COMPLETE|Execution Simulator workspace|
|UI12|COMPLETE|Research & Validation workspace|
|UI13|COMPLETE|Operations workspace|
|VIS01|COMPLETE|Eight advanced research projections|
|VIS02|COMPLETE|Existing four L1 projections and three native/model scenes|
|VIS03|COMPLETE|3D camera,orbit,pause,reset,visibility,cleanup and fallback|
|VIS04|BLOCKED|Sustained physical GPU,mobile and independent-browser acceptance|
|DATA01|COMPLETE|Broad discovery independent of SEC/feed entitlement|
|DATA02|PARTIAL|Complete,current US-listed security universe|
|SEC01|COMPLETE|SEC identity admission,selected facts,ratios,filings and provenance|
|SEC02|PARTIAL|Complete historical financial statements and point-in-time source history|
|SEC03|BLOCKED|Real-provider SEC reconciliation for this delivered source|
|MD01|COMPLETE|Read-only IEX permissions,credentials and fixed destinations|
|MD02|COMPLETE|Live quote/trade infrastructure,ordering,dedup,reconnect,subscriptions|
|MD03|COMPLETE|Historical IEX bars,quotes,trades and explicit delayed-SIP profile|
|MD04|COMPLETE|Historical bar display and source error reporting|
|MD05|BLOCKED|Actual owner IEX live/historical qualification|
|MD06|PARTIAL|Complete corrected exchange tape and lossless reconnect|
|MD07|PARTIAL|Official-contract Kraken cryptocurrency L2 and native/product integration|
|RES01|COMPLETE|Research configuration,calculations,results and authored exports|
|RES02|COMPLETE|Historical bar-to-research/compatible3D workflow|
|RES03|BLOCKED|Empirical forecasting quality,calibrated fills or alpha|
|REL01|COMPLETE|Bounded observation persistence,recovery,backup and corruption rejection|
|REL02|PARTIAL|Crash-safe hot live/L3 recovery and hardware durability guarantees|
|SECURITY01|COMPLETE|Strict private Origin/Host,HTTP proof and WebSocket lifecycle|
|SECURITY02|COMPLETE|Frontend budgets,errors and disabled execution safeguards|
|SECURITY03|PARTIAL|Runtime/dependency security clearance|
|OPS01|COMPLETE|Private startup,exact-SHA upgrade,rollback and qualification tools|
|OPS02|BLOCKED|Owner-authenticated Codespaces HTTPS/WSS acceptance|
|OPS03|BLOCKED|Current-candidate genuine native ARM64 qualification|
|UX01|COMPLETE|Readable dark/light,responsive,keyboard and reduced-motion engineering|
|UX02|PARTIAL|Full WCAG2.2AA and physical-device acceptance|
|CLEAN01|COMPLETE|Obsolete user-facing branding and safe frontend cleanup|
|SCOPE01|NOT APPLICABLE|Real/paper execution,paid feeds,public deployment and redistribution|
|SCOPE02|PARTIAL|Historical A18/A19 requirement and concentration acceptance|

## CORE01 — C++20 typed order book,identity,FIFO and exact arithmetic

COMPLETE

Source:`include/gig/book/order_book.hpp`,`src/book/order_book.cpp`,`include/gig/analytics/exact.hpp`

Evidence:Current six native CTest configurations passed(148/148/149 GCC;148/148/145 Clang),including eight unchanged independent frozen identities. Current175 guarded Python cases passed in five supported binding environments;SDK installed-wheel8consumer+19distinct recovery cases passed. No application or browser was launched.

Contract:Checked mutations,explicit identities and bounded native resources exist;not an exchange-equivalence or live-depth claim.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## CORE02 — ITCH framing,decoding,context and synthetic L3 reconstruction

COMPLETE

Source:`src/itch/binary_file.cpp`,`src/itch/decoder.cpp`,`src/itch/context.cpp`,`src/itch/reconstruction.cpp`

Evidence:Current six native CTest configurations passed(148/148/149 GCC;148/148/145 Clang),including eight unchanged independent frozen identities. Current175 guarded Python cases passed in five supported binding environments;SDK installed-wheel8consumer+19distinct recovery cases passed. No application or browser was launched.

Contract:Explicit initialization eligibility,prepared transactions and unsupported outcomes;no inferred empty historical book.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## CORE03 — Python/native integration and native-backed browser

COMPLETE

Source:`python/gig_microstructure/__init__.py`,`terminal/server/engine.py`,`terminal/server/analysis.py`

Evidence:Current six native CTest configurations passed(148/148/149 GCC;148/148/145 Clang),including eight unchanged independent frozen identities. Current175 guarded Python cases passed in five supported binding environments;SDK installed-wheel8consumer+19distinct recovery cases passed. No application or browser was launched.

Contract:NativeSession owns gig.Replay and calls C++ calculations;this is not a mock implementation. No native source/build input changes in this sprint.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## CORE04 — Deterministic replay,journal and recovery contracts

COMPLETE

Source:`src/replay/replay.cpp`,`terminal/server/engine.py`

Evidence:Current six native CTest configurations passed(148/148/149 GCC;148/148/145 Clang),including eight unchanged independent frozen identities. Current175 guarded Python cases passed in five supported binding environments;SDK installed-wheel8consumer+19distinct recovery cases passed. No application or browser was launched.

Contract:Journal reservation and recovery-required state exist;authored replay and bounded snapshots remain separate from observed complete sessions.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## CORE05 — Complete observed historical Level 3 validation

BLOCKED

Source:`include/gig/itch/reconstruction.hpp`,`terminal/stocks/historical_v2.py`

Evidence:Retained prior checkpoint evidence unless updated below: No new observed dataset used

Contract:Requires independently complete initialization and order-level reference evidence. IEX L1 and five-level reference observations cannot supply it.

Dependency:Independently complete observed L3 initialization,source/order-level reference and lawful dataset use.

Next condition/action:Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## UI01 — GIG-only branding,application shell,search,themes and navigation

COMPLETE

Source:`terminal/web/src/App.tsx`,`terminal/web/src/Navigation.tsx`,`terminal/web/src/workstation.ts`,`terminal/web/src/workstation.css`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline frontend and workstation browser checks;prior screenshot manifest

Contract:All12 destinations have dedicated compositions;legacy atlas-* selectors/storage identifiers remain technical compatibility keys.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI02 — Command Center workspace

COMPLETE

Source:`terminal/web/src/ResearchDesk.tsx`,`terminal/web/src/WorkspaceLaunchpad.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Saved research and source-aware entry actions;no fabricated market summary.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI03 — Securities Universe workspace

COMPLETE

Source:`terminal/web/src/UniverseWorkspace.tsx`,`terminal/stocks/discovery.py`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Search,filters,pagination,identity-source and coverage are present;not a claim of complete US listing coverage.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI04 — Stock Intelligence workspace

COMPLETE

Source:`terminal/web/src/StockIntelligence.tsx`,`terminal/web/src/FinancialWorkspace.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Company identity,reported facts,periods,ratios,filings,source controls and theoretical tools are connected;missing values remain missing.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI05 — Live Markets workspace

COMPLETE

Source:`terminal/web/src/LiveMarket.tsx`,`terminal/stocks/live.py`,`terminal/web/src/TradeTapePanel.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Shared bounded quote/trade observations,subscription controls,per-symbol health and source labels;offline verified,not live qualified. New progressive retained-tape view exposes exact reference/lineage values and unresolved outcomes;application browser interaction was not launched.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI06 — Multi-Stock Comparison workspace

COMPLETE

Source:`terminal/web/src/LiveMarket.tsx`,`terminal/web/src/HistoricalMarket.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Up to4 active symbols,retained quote comparisons and exact shared historical timestamps;no interpolated source data.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI07 — Order Book workspace

COMPLETE

Source:`terminal/web/src/App.tsx`,`terminal/web/src/bookPresentation.ts`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Native price/quantity ladders,cumulative quantities and source status are accessible;observed IEX is not expanded into L3.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI08 — Market Depth workspace

COMPLETE

Source:`terminal/web/src/App.tsx`,`terminal/web/src/Landscape3D.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Native retained depth,2D alternatives,camera controls and source restrictions;not invented depth.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI09 — Order Flow workspace

COMPLETE

Source:`terminal/web/src/App.tsx`,`terminal/server/analysis.py`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Native event/imbalance/flow views retain exact metrics and provenance;coalesced snapshots are not a complete trade tape.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI10 — Historical Replay workspace

COMPLETE

Source:`terminal/web/src/App.tsx`,`terminal/server/engine.py`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Play,pause,step,seek,speed and dataset selection call the native research session;recorded and authored data are separately labeled.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI11 — Execution Simulator workspace

COMPLETE

Source:`terminal/web/src/App.tsx`,`src/simulation/simulator.cpp`,`src/execution/execution.cpp`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Native scenarios,fills/costs and lifecycle remain simulated;fake-paper sandbox and disabled broker boundary are separate.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI12 — Research & Validation workspace

COMPLETE

Source:`terminal/web/src/App.tsx`,`terminal/web/src/ResearchLab.tsx`,`terminal/web/src/ResearchDiagnostics.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Model scenarios,3D laboratory,validation and evidence workflows are accessible;no predictive-success claim.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UI13 — Operations workspace

COMPLETE

Source:`terminal/web/src/App.tsx`,`terminal/web/src/MarketHealth.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Contract:Health,source/configuration,retention and diagnostic statuses are read-only or explicitly gated;no credentials displayed.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## VIS01 — Eight advanced research projections

COMPLETE

Source:`terminal/web/src/research3d.ts`,`terminal/web/src/ResearchLab.tsx`,`terminal/web/src/ResearchScene.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline23advanced browser checks and frontend geometry tests

Contract:Height,canyon,events,VWAP,flow/VPIN,wheel,dome,ribbon use declared input classes. Depth/events/signed flow unavailable without eligible source. Snapshot changes never invent executions.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## VIS02 — Existing four L1 projections and three native/model scenes

COMPLETE

Source:`terminal/web/src/QuoteCloud.tsx`,`terminal/web/src/Landscape3D.tsx`,`terminal/web/src/VolatilitySurface.tsx`,`terminal/web/src/ModelSurface.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline advanced/native browser checks;retained15-mode controlled-input evidence

Contract:Four coordinated quote modes,native depth,option scenario/indicative-point and GARCH mathematical surfaces remain. Mathematical surfaces are not calibrated observed volatility.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## VIS03 — 3D camera,orbit,pause,reset,visibility,cleanup and fallback

COMPLETE

Source:`terminal/web/src/cameraMotion.ts`,`terminal/web/src/ResearchScene.tsx`,`terminal/web/src/QuoteCloud.tsx`,`terminal/web/src/Landscape3D.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline advanced/workstation browser checks;cameraMotion unit tests

Contract:Independent controls,hidden/reduced-motion suspension,explicit empty/recovery states and GPU disposal exist. Camera orbit is not a source update.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## VIS04 — Sustained physical GPU,mobile and independent-browser acceptance

BLOCKED

Source:`terminal/web/src/ResearchScene.tsx`,`terminal/web/src/OptionalBoundary.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Chromium/SwiftShader and emulated widths only

Contract:Actual owner hardware/browser sustained behavior is not established by software WebGL.

Dependency:Actual target hardware/browser/GPU and permission to launch.

Next condition/action:Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## DATA01 — Broad discovery independent of SEC/feed entitlement

COMPLETE

Source:`terminal/stocks/market_catalog.py`,`terminal/stocks/alpaca_reference.py`,`terminal/stocks/sec_identity.py`,`terminal/web/src/UniverseWorkspace.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Stock/catalog/SEC cohorts and historical browser identity checks

Contract:Accepted reference catalogs/SEC routing and curated fallback are separate;AAPL/APLD/CRWV have generic discovery paths without guessed CIKs.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## DATA02 — Complete,current US-listed security universe

PARTIAL

Source:`terminal/stocks/directory.py`,`terminal/stocks/alpaca_reference.py`,`terminal/stocks/discovery.py`

Evidence:Retained prior checkpoint evidence unless updated below: Parser/catalog fixtures;no fresh authoritative import

Contract:Existing bounded authoritative directory/asset importers are implemented. Current full listing coverage cannot be asserted without an actual authorized source import/reconciliation;SEC registrants alone are not complete US listings.

New implementation:Existing bounded importers reviewed;no new importer or authoritative listing data invented.

Remaining:Current complete listing coverage requires an actual authorized source import and reconciliation,not SEC registrants.

Dependency:Configured permitted listing source/private target;source coverage and freshness evidence.

Next condition/action:Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional estimate:0.5–1 engineer-day for bounded qualification after the source/target is available;ongoing listing completeness remains a source responsibility.

## SEC01 — SEC identity admission,selected facts,ratios,filings and provenance

COMPLETE

Source:`terminal/stocks/sec_identity.py`,`terminal/stocks/financials.py`,`terminal/stocks/ratio_history.py`,`terminal/stocks/sec.py`,`terminal/web/src/FinancialWorkspace.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline211stock/source cohort;financial browser references retained and rerun where affected

Contract:Exact reported periods,source/hash/missingness,terminal-marker reference admission,duplicates/conflicts and bounded filing pagination exist. Not a full financial-statement reconstruction.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## SEC02 — Complete historical financial statements and point-in-time source history

PARTIAL

Source:`terminal/stocks/sec_history.py`,`terminal/web/src/secHistory.ts`,`terminal/web/src/StockIntelligence.tsx`,`terminal/stocks/statements.py`,`terminal/stocks/vintages.py`,`terminal/stocks/test_filing_vintage.py`,`terminal/web/src/AcceptanceView.tsx`,`terminal/web/src/acceptanceContract.ts`,`terminal/web/src/AcceptanceFacts.tsx`,`terminal/stocks/xbrl_instance.py`,`terminal/stocks/xbrl_collection.py`,`scripts/inspect_xbrl_instances.py`,`terminal/stocks/test_xbrl_instance.py`,`terminal/stocks/test_xbrl_collection.py`,`terminal/stocks/test_xbrl_tool.py`,`terminal/stocks/inline_xbrl.py`,`terminal/stocks/xbrl_dts.py`,`terminal/stocks/test_inline_xbrl.py`,`terminal/stocks/test_xbrl_dts.py`

Evidence:48authored XML cases:32instance/collection/tool,7inline,9DTS;all five binding profiles passed,including final fact/output bounds. Full263guarded cohort per5profiles;existing13cross-language assertions preserved.

Contract:Existing filing batches/vintage selection now admit a bounded plain inline-XBRL1.1 profile with exact scaling/sign and original lexical/source lineage. Supplied-file DTS discovery binds source hashes,document kinds/import namespaces and missing references;simple presentation locators/order/cycles are supported. Unknown transforms/types/precedence remain explicit. No external URI is fetched.

New implementation:Fact interpreter refactored without changing strict instance API;plain inline scale/sign/nil/source gating;pre-materialization fact/output limits;DTS schema/import/include/linkbase discovery;declared concept metadata and conservative presentation graphs;missing/custom/conflicting semantics remain unvalidated.

Remaining:Full inline transformation/continuation/tuple/nested markup support,complete XML Schema/DTS custom-type and extension validation,equivalent/prohibited arc precedence across links,calculation relationships,complete statement assembly,v2/UI integration and authentic complete historical acquisition/receipt coverage remain missing.

Dependency:Choose a bounded full-statement/DTS/inline fidelity and extension profile;retain legitimately authorized instance/taxonomy/presentation originals with acceptance/receipt evidence. Much remaining work is engineering,not solely external access.

Next condition/action:Complete the next explicitly bounded transformation/type/relationship profile with independent fixtures,then statement/API integration. Structural closure is not schema or accounting validation.

Conditional estimate:Several engineer-weeks for scoped full transformation/DTS/extension/relationship and statement-integration coverage;original receipts and complete historical input coverage remain external evidence requirements.

## SEC03 — Real-provider SEC reconciliation for this delivered source

BLOCKED

Source:`terminal/stocks/qualification.py`,`scripts/qualify_sec_sources.py`

Evidence:Retained prior checkpoint evidence unless updated below: Existing owner observations retained separately;no request in this task

Contract:Identifying configuration and permitted target access are unavailable here;fixtures do not establish fresh provider results.

Dependency:Configured identifying SEC User-Agent and permitted owner target;current task forbids provider calls.

Next condition/action:Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## MD01 — Read-only IEX permissions,credentials and fixed destinations

COMPLETE

Source:`terminal/stocks/private_iex.py`,`terminal/stocks/auth.py`,`terminal/stocks/alpaca_transport.py`,`terminal/stocks/live.py`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline211cohort;private-IEX qualification tests retained

Contract:Explicit read-only stream gate,reviewed permission scopes,server-only credentials and fixed data hosts;real/paper execution remain independently disabled.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## MD02 — Live quote/trade infrastructure,ordering,dedup,reconnect,subscriptions

COMPLETE

Source:`terminal/stocks/live.py`,`terminal/stocks/retry.py`,`terminal/stocks/test_reconnect_stability.py`,`terminal/server/market_events.py`,`terminal/stocks/trade_tape.py`,`terminal/stocks/test_live_recovery.py`,`terminal/stocks/test_live_recovery.py`,`terminal/web/src/marketContract.ts`

Evidence:35 focused worker/checkpoint/retry tests;175 guarded offline cases per five environments;154 frontend checks and production build;phase/code diagnostic and stale-socket/concurrent-start regressions.

Contract:A reproduced one-quote-per-reconnect flap could reset failure count indefinitely. Retry count now resets only after a stable subscribed interval(default30s,bounded1–300),including quiet transport liveness without inventing observations. Backoff,permissions,generation isolation and source-gap limitations remain. Concurrent commands now serialize to prevent orphan workers;retired sockets cannot publish;provider error code and actual phase are bounded and redacted rather than inferred entitlement meanings.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## MD03 — Historical IEX bars,quotes,trades and explicit delayed-SIP profile

COMPLETE

Source:`terminal/stocks/alpaca_history.py`,`terminal/stocks/historical_v2.py`,`terminal/web/src/HistoricalMarket.tsx`,`terminal/web/src/HistoricalResearch.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline58focused historical tests and browser journeys

Contract:Bounded pages,exact nanoseconds,OHLC,duplicate accounting,cache TTL and explicit SIP15-minute boundary. No automatic feed upgrade;no complete-session inference.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## MD04 — Historical bar display and source error reporting

COMPLETE

Source:`terminal/web/src/barChart.ts`,`terminal/web/src/EquityPanels.tsx`,`terminal/stocks/alpaca_history.py`,`terminal/server/app.py`

Evidence:Retained prior checkpoint evidence unless updated below: New7unit+4Python+10browser checks;retained failing-before logs

Contract:This sprint fixes synthetic-as-observed chart labels,validates bounded exact OHLC before geometry,and distinguishes fixed safe failure categories without reflecting source bodies.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## MD05 — Actual owner IEX live/historical qualification

BLOCKED

Source:`scripts/private_iex.py`,`docs/qualification/PRIVATE_IEX_RUNBOOK.md`

Evidence:Retained prior checkpoint evidence unless updated below: Zero provider requests in this task

Contract:Owner-reported Support384778 covers the narrow private research use. This runtime has no configured credentials/private-owner environment. No fresh source/entitlement/freshness evidence.

Dependency:Owner-private target,credentials/authorized feed and a separately approved read-only test.

Next condition/action:Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## MD06 — Complete corrected exchange tape and lossless reconnect

PARTIAL

Source:`terminal/stocks/trade_tape.py`,`terminal/stocks/test_trade_tape.py`,`terminal/web/src/tradeTape.ts`,`terminal/web/src/TradeTapePanel.tsx`,`terminal/tests/check_trade_contract.py`

Evidence:Existing13 ledger tests/1000oracle candidates retained;new handover-window regression and actual TypeScript admission for the handover;8cross-language market checks. Observed cancellation profile still unqualified.

Contract:Bounded normalized reference ledger now supports exact original matching,correction chains,retirement,duplicates,capture-order replay,provenance and fail-closed totals. Explicit authored C-cancellation contract works. Observed cancellation/error action profile and complete/lossless exchange capture remain unimplemented/unqualified. Version 2 also fences local capture namespaces,so equal per-process generations cannot mix records from separate captures. This namespace is not an exchange session/sequence.

New implementation:Supported bounded correction/authored-cancellation rules preserved;symbol-handover published-window mismatch reproduced and fixed. Capture/source lineage remains isolated.

Remaining:Authoritative observed cancellation/error mapping and complete/lossless source-tape recovery are still absent. Current IEX profile has no independently complete exchange sequence/backfill proof.

Dependency:Authoritative action semantics and source completeness/backfill contract;no guessed C/E actions or missing trades.

Next condition/action:Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional estimate:1–2 engineer-days for a specified bounded observed-action profile;complete/lossless guarantees cannot be estimated or promised for a source that lacks that authority.

## MD07 — Official-contract Kraken cryptocurrency L2 and native/product integration

PARTIAL

Source:`terminal/providers/kraken.py`,`terminal/providers/supervisor.py`,`terminal/providers/test_recovery_hardening.py`,`terminal/providers/test_differential.py`,`terminal/server/engine.py`,`terminal/web/src/OrderBook.tsx`,`terminal/l2_research.py`

Evidence:62offline provider cases including10,000authored independent transitions;finite scientific JSON precision/CRC,one-worker concurrency,bounded retiring-worker fence,retry exhaustion and invalid jitter regressions;inside263guarded cases. No current official documentation or live payload received.

Contract:Existing provisional snapshot/absolute-update/top10CRC and native L2 projection are retained. Exact finite JSON scientific-number conversion and physical worker/retry recovery were repaired. Existing source-labelled native book/depth/research views remain connected. Official schema/options/checksum/session semantics and legal source qualification are not independently verified;provisional status is unchanged.

New implementation:Reproduced finite Decimal/scientific JSON rejection and concurrent2-worker/retry-cycle defects;fixed bounded exact conversion,serialization,cancel drain/re-admission fences,stable delivery retry reset and bounded jitter validation.

Remaining:Retrieve and verify the current official WebSocketv2 book/checksum/trade/status/session contract and applicable usage evidence;reconcile candidate rules and add source-versioned fixtures. Actual later private-provider and browser qualification remain unrun. Do not change the provisional flag before evidence exists.

Dependency:Current official protocol/rights evidence;earlier CONNECT403 and enforced policy excluding Kraken docs/feed domains remain recorded. No blocked operation was retried and no proxy bypass attempted.

Next condition/action:Obtain an authorized official specification copy or permitted documentation-only access,then implement verified source-specific differences. Continue offline contracts;never infer L3 or IEX equity depth.

Conditional estimate:1–3engineer-days for a bounded documented source-contract reconciliation/test package once authoritative material is available;live/owner qualification separate.

## RES01 — Research configuration,calculations,results and authored exports

COMPLETE

Source:`terminal/stocks/research.py`,`terminal/stocks/advanced_models.py`,`terminal/stocks/portfolio.py`,`terminal/stocks/evaluation.py`,`terminal/web/src/researchExport.ts`

Evidence:Retained prior checkpoint evidence unless updated below: Baselinefrontend and stock cohorts;native mathematical references retained Current guarded175-case cohort passed in all five supported binding environments;no source/target acceptance implied.

Contract:Bounded HMM/GARCH/Kalman diagnostics,causal strategy/walk-forward,risk/portfolio and deterministic exports exist. Native exact mathematics remain unchanged.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## RES02 — Historical bar-to-research/compatible3D workflow

COMPLETE

Source:`terminal/stocks/historical_research.py`,`terminal/web/src/historicalResearch.ts`,`terminal/web/src/HistoricalResearch.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline58historical Python checks;Sprint4 browser numerical/export assertions

Contract:Accepted revisions drive exact trailing returns,SMA,drawdown and log variation. Quotes feed quote projections;bars cannot become depth or signed events.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## RES03 — Empirical forecasting quality,calibrated fills or alpha

BLOCKED

Source:`terminal/stocks/evaluation.py`,`src/simulation/simulator.cpp`

Evidence:Retained prior checkpoint evidence unless updated below: No new observed evaluation dataset

Contract:Mathematical and causal fixture agreement do not establish predictive accuracy,profitability or exchange execution fidelity.

Dependency:Legitimate observed evaluation data and independently defined out-of-sample research protocol.

Next condition/action:Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## REL01 — Bounded observation persistence,recovery,backup and corruption rejection

COMPLETE

Source:`terminal/stocks/observation_store.py`,`terminal/stocks/history_store.py`,`terminal/stocks/history_backup.py`

Evidence:Existing10 persistence tests plus21new control/recovery tests inside121no-launch tests per environment;legacy/full recover() behavior preserved. Current guarded175-case cohort passed in all five supported binding environments;no source/target acceptance implied.

Contract:Preflight counts/bytes/types,single read snapshot,strict payloads/hash chain and private snapshots exist. Observed retention defaults off;no storage activated here.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## REL02 — Crash-safe hot live/L3 recovery and hardware durability guarantees

PARTIAL

Source:`terminal/stocks/live.py`,`terminal/stocks/live_checkpoint.py`,`terminal/stocks/observation_store.py`,`terminal/stocks/test_live_checkpoint.py`,`include/gig/itch/restart.hpp`,`include/gig/book/order_book.hpp`,`src/book/order_book.cpp`,`include/gig/replay/replay.hpp`,`src/replay/replay.cpp`,`include/gig/market_data/aggregate_depth.hpp`,`src/market_data/aggregate_depth.cpp`,`terminal/native_recovery.py`,`terminal/test_native_recovery.py`,`terminal/test_aggregate_recovery.py`,`tests/test_hot_checkpoint.cpp`,`include/gig/itch/hot_checkpoint.hpp`,`src/itch/context_checkpoint.cpp`,`src/itch/hot_checkpoint.cpp`,`src/itch/hot_identity.hpp`,`terminal/session_recovery.py`,`terminal/test_session_recovery.py`,`tests/test_itch_hot_checkpoint.cpp`

Evidence:Six full native profiles149/149/150GCC and149/149/146Clang,221ITCH hot-context checks,46actual restore failpoints,eight actual frozen hashes each. Nine new real-native product-session/file/migration cases inside263guarded cases per5binding profiles.

Contract:Owned typed ITCH source-context,receipt mapping and both native-book/replay images now restore isolated accepted authored-empty prefixes without source reapplication. Token ownership is fresh;active order identities/units and derived sequences agree. Explicit native product-session checkpoints restore position/speed paused,with immutable private files,canonical admission and bounded migration. No automatic application recovery or provider connection is enabled.

New implementation:Typed context/book/receipt hot capture/import;fingerprint optional-dispatch repair;pre-copy4096vector limit;physical allocation-failure tests;actual NativeSession integration;private atomic new-file publication;real process-exit-after-publish and explicit migration/rollback-input preservation.

Remaining:Stable durable encoding/admission of the full typed ITCH image,seeded hot reconstruction,gzip/partial-framer coordination and optional application startup wiring remain missing. Product file recovery currently supports authored-native sessions,not observed/provider/recorded sources. Filesystem power-loss/owner/observed source guarantees remain unqualified.

Dependency:Bounded typed-native contract now exists and is verified. Remaining work needs an explicit full source-image/migration profile,product integration tests and,for empirical claims,complete authorized source initialization plus actual target durability evidence.

Next condition/action:Implement a versioned bounded full-ITCH image codec and seed/framer integration against the current typed images;preserve explicit independently trusted identity. Do not reimplement the completed native/session APIs or activate startup/provider paths.

Conditional estimate:Planning range3–7engineer-days for a tightly scoped remaining codec/seed/framer/startup package and failure matrix after its artifact/migration profile is fixed;hardware/source qualification is separate.

## SECURITY01 — Strict private Origin/Host,HTTP proof and WebSocket lifecycle

COMPLETE

Source:`terminal/server/app.py`,`terminal/server/request_proofs.py`,`terminal/server/stream_tickets.py`,`terminal/server/connection.py`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline274native/API tests;existing localTLS/forged-header tests

Contract:Exact configured origins,bounded target-bound one-use proofs,Host checks and sanitized diagnostics retained;no wildcard CORS or arbitrary forwarded-header trust.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## SECURITY02 — Frontend budgets,errors and disabled execution safeguards

COMPLETE

Source:`terminal/web/src/response.ts`,`terminal/server/app.py`,`terminal/paper/alpaca.py`,`terminal/stocks/private_iex.py`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline130frontend and211/274backend checks;prior fake-broker evidence retained

Contract:Incremental2MiB read,abort/cancel,strict mutations and default-disabled independent paper/live controls. No provider/account calls or orders in this task.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## SECURITY03 — Runtime/dependency security clearance

PARTIAL

Source:`terminal/server/requirements.txt`,`terminal/web/package-lock.json`,`docs/qualification/institutional-sprint-2/DEPENDENCY_ARTIFACT_QUALIFICATION.md`

Evidence:New strict control/filing/response admission and source-bound current121/153checks;prior pinned-dependency advisory evidence retained,not target security clearance.

Contract:Current public advisory metadata was obtained without market/account access. Runtime dependency pins were not changed. This does not clear target OS,all optional/transitive deployment artifacts,private edge or future advisories.

New implementation:Checkpoint byte/type/hash/tail admission strengthened;source validation streamed;response admission/cancellation strengthened. Dependency pins and authorization boundaries unchanged.

Remaining:Owner-target OS,full deployed/transitive artifact and private-edge clearance remain pending. Prior advisory metadata remains source-bound prior evidence.

Dependency:Actual deployment artifacts/runtime/OS and private-edge environment;no production clearance from fixtures.

Next condition/action:Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional estimate:0.5–2 engineer-days after exact target artifacts are available;future advisory clearance is time-dependent.

## OPS01 — Private startup,exact-SHA upgrade,rollback and qualification tools

COMPLETE

Source:`scripts/start_terminal.sh`,`scripts/qualify_private_deployment.py`,`docs/qualification/institutional-sprint-2/DEPLOYMENT_ACCEPTANCE.md`

Evidence:Retained prior checkpoint evidence unless updated below: Prior clean receipt plus baseline development checks;no owner deployment claimed

Contract:Existing runbooks preserve local changes,do not reset/clean,bind source/assets and distinguish offline/edge qualification. No missing new deployment tool found.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## OPS02 — Owner-authenticated Codespaces HTTPS/WSS acceptance

BLOCKED

Source:`scripts/start_terminal.sh`,`terminal/tests/check_browser_handshake.mjs`

Evidence:Retained prior checkpoint evidence unless updated below: Only local browser/forwarding fixtures available

Contract:No actual owner edge,cookies/credentials or private-port authentication accessed.

Dependency:Actual owner-authenticated private Codespaces edge and authorized application startup.

Next condition/action:Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## OPS03 — Current-candidate genuine native ARM64 qualification

BLOCKED

Source:`.github/workflows/native-arm64.yml`,`terminal/test_arm64_terminal_policy.py`

Evidence:Retained prior checkpoint evidence unless updated below: Manual-only/free-owner/branch policy tests;not dispatched

Contract:Earlier tested SHAs do not qualify new code. Existing six-configuration workflow includes strict native/API and updated stock cohort.

Dependency:Current-candidate genuine free native ARM64 runner and owner-authorized manual execution.

Next condition/action:Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## UX01 — Readable dark/light,responsive,keyboard and reduced-motion engineering

COMPLETE

Source:`terminal/web/src/workstation.css`,`terminal/web/src/Navigation.tsx`,`terminal/web/src/cameraMotion.ts`

Evidence:Retained prior checkpoint evidence unless updated below: Baseline130frontend/workstation browser checks;prior5690text-contrast evidence

Contract:Semantic controls,focus,contained table/navigation scrolling,comfortable text and responsive canvases implemented;no new visual redesign in this sprint.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## UX02 — Full WCAG2.2AA and physical-device acceptance

PARTIAL

Source:`terminal/web/src/BarValues.tsx`,`terminal/web/src/EquityPanels.tsx`,`terminal/web/src/HistoricalMarket.tsx`,`terminal/web/src/barValues.test.ts`,`terminal/web/src/AcceptanceFacts.tsx`,`terminal/web/src/acceptanceFacts.test.ts`

Evidence:153frontend checks include2new actual acceptance-leaf SSR checks;no application,browser or physical-device launch.

Contract:Exact-value keyboard-readable bar tables now supplement hover-only candles in company/archive views;calendar-history reuses its existing table. Source caption,scoped headers,nanoseconds,units and zero volume are preserved. Native dialog,skip link and existing keyboard controls already existed and were preserved.

New implementation:Exact retained fact table now keyboard-scrollable with named region,scoped headers,time semantics,empty states and32-row pagination. Stale async results cannot replace the selected cutoff.

Remaining:Current real-browser,assistive-technology,device and exhaustive WCAG2.2AA qualification remain unperformed under the no-launch directive.

Dependency:Separate authorization to launch/test actual browsers and access to target devices/assistive technology.

Next condition/action:Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional estimate:1–3 engineer-days for targeted acceptance and resulting confirmed repairs once browser/device tests are authorized;unknown failures cannot be estimated in advance.

## CLEAN01 — Obsolete user-facing branding and safe frontend cleanup

COMPLETE

Source:`terminal/web/index.html`,`terminal/web/src/workstation.ts`,`terminal/web/src/App.tsx`

Evidence:Retained prior checkpoint evidence unless updated below: Branding unit/browser checks and source search

Contract:User-facing identity is GIG. Historical reports and compatibility technical keys are preserved;unused code is not deleted merely on a name-based guess.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## SCOPE01 — Real/paper execution,paid feeds,public deployment and redistribution

NOT APPLICABLE

Source:`terminal/stocks/private_iex.py`,`terminal/paper/alpaca.py`

Evidence:Retained prior checkpoint evidence unless updated below: Default-disabled boundary tests

Contract:Explicitly outside this observation-only sprint. Existing fake-paper harness is not owner order authorization.

Next condition/action:No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## SCOPE02 — Historical A18/A19 requirement and concentration acceptance

PARTIAL

Source:`terminal/server/concentration.py`,`docs/remediation/sprint-2/REMAINING_BLOCKERS.md`

Evidence:Retained prior checkpoint evidence unless updated below: Existing exact supplied-depth HHI tests;original69c9f48 audit read from Git

Contract:Exact source-bound supplied-depth HHI exists. Earlier audit preserves unknown original estimator/baseline. Attempt to recover the original pasted master text in this session failed authorization/resolution;no restricted dataset was accessed.

New implementation:Historical49th decision row preserved separately from48 reviewed areas. Existing exact supplied-depth HHI unchanged.

Remaining:Original A18/A19 baseline/estimator still unknown;no retroactive completion or substitute estimator.

Dependency:Recover original requirements or approve an explicitly prospective versioned contract.

Next condition/action:Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional estimate:Cannot estimate historical acceptance closure before the missing contract is resolved;writing a prospective contract is a distinct owner decision.

IEX final follow-through:36focused recovery/retry/checkpoint checks and263guarded cases per five binding profiles passed. See IEX_SHUTDOWN_REPAIR.md;all original rows and scopes remain retained.
