# GIG development completion matrix — November 11, 2026

Current runtime source `1f07e43c71e8db7377a1e16c6b88c049a6591b4f`; branch `development/gig-ui-redesign`.

50 entries = 49 reviewed areas + one historical A18/A19 decision. The prior explicit Kraken MD07 row is retained; no scope row was removed.

**34 COMPLETE / 8 PARTIAL / 7 BLOCKED / 1 NOT APPLICABLE. Full development remains incomplete.**

COMPLETE means the stated bounded implementation has source/test evidence; it does not mean real-provider or owner acceptance. Current recovery tests and all eight native identities were actually rerun. Frontend/browser/target evidence was not recreated.

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

## CORE01 — COMPLETE

C++20 typed order book,identity,FIFO and exact arithmetic

Source: `include/gig/book/order_book.hpp`, `src/book/order_book.cpp`, `include/gig/analytics/exact.hpp`.

Evidence: Current six native CTest configurations passed(148/148/149 GCC;148/148/145 Clang),including eight unchanged independent frozen identities. Current175 guarded Python cases passed in five supported binding environments;SDK installed-wheel8consumer+19distinct recovery cases passed. No application or browser was launched.

Checked mutations,explicit identities and bounded native resources exist;not an exchange-equivalence or live-depth claim.

Disposition: Implemented bounded research contract;retain tested behavior

## CORE02 — COMPLETE

ITCH framing,decoding,context and synthetic L3 reconstruction

Source: `src/itch/binary_file.cpp`, `src/itch/decoder.cpp`, `src/itch/context.cpp`, `src/itch/reconstruction.cpp`.

Evidence: Current six native CTest configurations passed(148/148/149 GCC;148/148/145 Clang),including eight unchanged independent frozen identities. Current175 guarded Python cases passed in five supported binding environments;SDK installed-wheel8consumer+19distinct recovery cases passed. No application or browser was launched.

Explicit initialization eligibility,prepared transactions and unsupported outcomes;no inferred empty historical book.

Disposition: Implemented bounded research contract;retain tested behavior

## CORE03 — COMPLETE

Python/native integration and native-backed browser

Source: `python/gig_microstructure/__init__.py`, `terminal/server/engine.py`, `terminal/server/analysis.py`.

Evidence: Current six native CTest configurations passed(148/148/149 GCC;148/148/145 Clang),including eight unchanged independent frozen identities. Current175 guarded Python cases passed in five supported binding environments;SDK installed-wheel8consumer+19distinct recovery cases passed. No application or browser was launched.

NativeSession owns gig.Replay and calls C++ calculations;this is not a mock implementation. No native source/build input changes in this sprint.

Disposition: Implemented bounded research contract;retain tested behavior

## CORE04 — COMPLETE

Deterministic replay,journal and recovery contracts

Source: `src/replay/replay.cpp`, `terminal/server/engine.py`.

Evidence: Current six native CTest configurations passed(148/148/149 GCC;148/148/145 Clang),including eight unchanged independent frozen identities. Current175 guarded Python cases passed in five supported binding environments;SDK installed-wheel8consumer+19distinct recovery cases passed. No application or browser was launched.

Journal reservation and recovery-required state exist;authored replay and bounded snapshots remain separate from observed complete sessions.

Disposition: Implemented bounded research contract;retain tested behavior

## CORE05 — BLOCKED

Complete observed historical Level 3 validation

Source: `include/gig/itch/reconstruction.hpp`, `terminal/stocks/historical_v2.py`.

Evidence: Retained prior checkpoint evidence unless updated below: No new observed dataset used

Requires independently complete initialization and order-level reference evidence. IEX L1 and five-level reference observations cannot supply it.

Disposition: External source/rights/reference evidence;not fabricated or inferred

Dependency: Independently complete observed L3 initialization,source/order-level reference and lawful dataset use.

Next action: Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## UI01 — COMPLETE

GIG-only branding,application shell,search,themes and navigation

Source: `terminal/web/src/App.tsx`, `terminal/web/src/Navigation.tsx`, `terminal/web/src/workstation.ts`, `terminal/web/src/workstation.css`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline frontend and workstation browser checks;prior screenshot manifest

All12 destinations have dedicated compositions;legacy atlas-* selectors/storage identifiers remain technical compatibility keys.

Disposition: Implemented bounded research contract;retain tested behavior

## UI02 — COMPLETE

Command Center workspace

Source: `terminal/web/src/ResearchDesk.tsx`, `terminal/web/src/WorkspaceLaunchpad.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Saved research and source-aware entry actions;no fabricated market summary.

Disposition: Implemented bounded research contract;retain tested behavior

## UI03 — COMPLETE

Securities Universe workspace

Source: `terminal/web/src/UniverseWorkspace.tsx`, `terminal/stocks/discovery.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Search,filters,pagination,identity-source and coverage are present;not a claim of complete US listing coverage.

Disposition: Implemented bounded research contract;retain tested behavior

## UI04 — COMPLETE

Stock Intelligence workspace

Source: `terminal/web/src/StockIntelligence.tsx`, `terminal/web/src/FinancialWorkspace.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Company identity,reported facts,periods,ratios,filings,source controls and theoretical tools are connected;missing values remain missing.

Disposition: Implemented bounded research contract;retain tested behavior

## UI05 — COMPLETE

Live Markets workspace

Source: `terminal/web/src/LiveMarket.tsx`, `terminal/stocks/live.py`, `terminal/web/src/TradeTapePanel.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Shared bounded quote/trade observations,subscription controls,per-symbol health and source labels;offline verified,not live qualified. New progressive retained-tape view exposes exact reference/lineage values and unresolved outcomes;application browser interaction was not launched.

Disposition: Implemented bounded research contract;retain tested behavior

## UI06 — COMPLETE

Multi-Stock Comparison workspace

Source: `terminal/web/src/LiveMarket.tsx`, `terminal/web/src/HistoricalMarket.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Up to4 active symbols,retained quote comparisons and exact shared historical timestamps;no interpolated source data.

Disposition: Implemented bounded research contract;retain tested behavior

## UI07 — COMPLETE

Order Book workspace

Source: `terminal/web/src/App.tsx`, `terminal/web/src/bookPresentation.ts`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Native price/quantity ladders,cumulative quantities and source status are accessible;observed IEX is not expanded into L3.

Disposition: Implemented bounded research contract;retain tested behavior

## UI08 — COMPLETE

Market Depth workspace

Source: `terminal/web/src/App.tsx`, `terminal/web/src/Landscape3D.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Native retained depth,2D alternatives,camera controls and source restrictions;not invented depth.

Disposition: Implemented bounded research contract;retain tested behavior

## UI09 — COMPLETE

Order Flow workspace

Source: `terminal/web/src/App.tsx`, `terminal/server/analysis.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Native event/imbalance/flow views retain exact metrics and provenance;coalesced snapshots are not a complete trade tape.

Disposition: Implemented bounded research contract;retain tested behavior

## UI10 — COMPLETE

Historical Replay workspace

Source: `terminal/web/src/App.tsx`, `terminal/server/engine.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Play,pause,step,seek,speed and dataset selection call the native research session;recorded and authored data are separately labeled.

Disposition: Implemented bounded research contract;retain tested behavior

## UI11 — COMPLETE

Execution Simulator workspace

Source: `terminal/web/src/App.tsx`, `src/simulation/simulator.cpp`, `src/execution/execution.cpp`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Native scenarios,fills/costs and lifecycle remain simulated;fake-paper sandbox and disabled broker boundary are separate.

Disposition: Implemented bounded research contract;retain tested behavior

## UI12 — COMPLETE

Research & Validation workspace

Source: `terminal/web/src/App.tsx`, `terminal/web/src/ResearchLab.tsx`, `terminal/web/src/ResearchDiagnostics.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Model scenarios,3D laboratory,validation and evidence workflows are accessible;no predictive-success claim.

Disposition: Implemented bounded research contract;retain tested behavior

## UI13 — COMPLETE

Operations workspace

Source: `terminal/web/src/App.tsx`, `terminal/web/src/MarketHealth.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline12-workspace dark/light/layout browser cohort;related native/stock journeys

Health,source/configuration,retention and diagnostic statuses are read-only or explicitly gated;no credentials displayed.

Disposition: Implemented bounded research contract;retain tested behavior

## VIS01 — COMPLETE

Eight advanced research projections

Source: `terminal/web/src/research3d.ts`, `terminal/web/src/ResearchLab.tsx`, `terminal/web/src/ResearchScene.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline23advanced browser checks and frontend geometry tests

Height,canyon,events,VWAP,flow/VPIN,wheel,dome,ribbon use declared input classes. Depth/events/signed flow unavailable without eligible source. Snapshot changes never invent executions.

Disposition: Implemented bounded research contract;retain tested behavior

## VIS02 — COMPLETE

Existing four L1 projections and three native/model scenes

Source: `terminal/web/src/QuoteCloud.tsx`, `terminal/web/src/Landscape3D.tsx`, `terminal/web/src/VolatilitySurface.tsx`, `terminal/web/src/ModelSurface.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline advanced/native browser checks;retained15-mode controlled-input evidence

Four coordinated quote modes,native depth,option scenario/indicative-point and GARCH mathematical surfaces remain. Mathematical surfaces are not calibrated observed volatility.

Disposition: Implemented bounded research contract;retain tested behavior

## VIS03 — COMPLETE

3D camera,orbit,pause,reset,visibility,cleanup and fallback

Source: `terminal/web/src/cameraMotion.ts`, `terminal/web/src/ResearchScene.tsx`, `terminal/web/src/QuoteCloud.tsx`, `terminal/web/src/Landscape3D.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline advanced/workstation browser checks;cameraMotion unit tests

Independent controls,hidden/reduced-motion suspension,explicit empty/recovery states and GPU disposal exist. Camera orbit is not a source update.

Disposition: Implemented bounded research contract;retain tested behavior

## VIS04 — BLOCKED

Sustained physical GPU,mobile and independent-browser acceptance

Source: `terminal/web/src/ResearchScene.tsx`, `terminal/web/src/OptionalBoundary.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Chromium/SwiftShader and emulated widths only

Actual owner hardware/browser sustained behavior is not established by software WebGL.

Disposition: Owner/environment qualification;not additional visualization implementation

Dependency: Actual target hardware/browser/GPU and permission to launch.

Next action: Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## DATA01 — COMPLETE

Broad discovery independent of SEC/feed entitlement

Source: `terminal/stocks/market_catalog.py`, `terminal/stocks/alpaca_reference.py`, `terminal/stocks/sec_identity.py`, `terminal/web/src/UniverseWorkspace.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Stock/catalog/SEC cohorts and historical browser identity checks

Accepted reference catalogs/SEC routing and curated fallback are separate;AAPL/APLD/CRWV have generic discovery paths without guessed CIKs.

Disposition: Implemented bounded research contract;retain tested behavior

## DATA02 — PARTIAL

Complete,current US-listed security universe

Source: `terminal/stocks/directory.py`, `terminal/stocks/alpaca_reference.py`, `terminal/stocks/discovery.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Parser/catalog fixtures;no fresh authoritative import

Existing bounded authoritative directory/asset importers are implemented. Current full listing coverage cannot be asserted without an actual authorized source import/reconciliation;SEC registrants alone are not complete US listings.

Disposition: No missing importer was found. Actual acquisition/source coverage needs the authorized configured target;no CIK or listing contents invented.

Remaining: Current complete listing coverage requires an actual authorized source import and reconciliation,not SEC registrants.

Dependency: Configured permitted listing source/private target;source coverage and freshness evidence.

Next action: Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional effort: 0.5–1 engineer-day for bounded qualification after the source/target is available;ongoing listing completeness remains a source responsibility.

## SEC01 — COMPLETE

SEC identity admission,selected facts,ratios,filings and provenance

Source: `terminal/stocks/sec_identity.py`, `terminal/stocks/financials.py`, `terminal/stocks/ratio_history.py`, `terminal/stocks/sec.py`, `terminal/web/src/FinancialWorkspace.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline211stock/source cohort;financial browser references retained and rerun where affected

Exact reported periods,source/hash/missingness,terminal-marker reference admission,duplicates/conflicts and bounded filing pagination exist. Not a full financial-statement reconstruction.

Disposition: Implemented bounded research contract;retain tested behavior

## SEC02 — PARTIAL

Complete historical financial statements and point-in-time source history

Source: `terminal/stocks/sec_history.py`, `terminal/web/src/secHistory.ts`, `terminal/web/src/StockIntelligence.tsx`, `terminal/stocks/statements.py`, `terminal/stocks/vintages.py`, `terminal/stocks/test_filing_vintage.py`, `terminal/web/src/AcceptanceView.tsx`, `terminal/web/src/acceptanceContract.ts`, `terminal/web/src/AcceptanceFacts.tsx`, `terminal/stocks/xbrl_instance.py`, `terminal/stocks/xbrl_collection.py`, `scripts/inspect_xbrl_instances.py`, `terminal/stocks/test_xbrl_instance.py`, `terminal/stocks/test_xbrl_collection.py`, `terminal/stocks/test_xbrl_tool.py`, `terminal/stocks/inline_xbrl.py`, `terminal/stocks/xbrl_dts.py`, `terminal/stocks/test_inline_xbrl.py`, `terminal/stocks/test_xbrl_dts.py`.

Evidence: 49authored XML cases including malformed simple-XLink references;273guarded tests per5binding profiles. Original49fixture/instance/vintage/DTS behavior retained;no provider request.

Existing filing batches/vintage selection now admit a bounded plain inline-XBRL1.1 profile with exact scaling/sign and original lexical/source lineage. Supplied-file DTS discovery binds source hashes,document kinds/import namespaces and missing references;simple presentation locators/order/cycles are supported. Unknown transforms/types/precedence remain explicit. No external URI is fetched.

Disposition: Bounded instance parsing and filing-vintage research/export are implemented. Full DTS/inline/presentation/extension semantics,complete statements and original historical source coverage remain incomplete within the approved scope.

Remaining: Full inline transformation/continuation/tuple/nested markup support,complete XML Schema/DTS custom-type and extension validation,equivalent/prohibited arc precedence across links,calculation relationships,complete statement assembly,v2/UI integration and authentic complete historical acquisition/receipt coverage remain missing.

Dependency: Choose a bounded full-statement/DTS/inline fidelity and extension profile;retain legitimately authorized instance/taxonomy/presentation originals with acceptance/receipt evidence. Much remaining work is engineering,not solely external access.

Next action: Complete the next explicitly bounded transformation/type/relationship profile with independent fixtures,then statement/API integration. Structural closure is not schema or accounting validation.

Conditional effort: Several engineer-weeks for scoped full transformation/DTS/extension/relationship and statement-integration coverage;original receipts and complete historical input coverage remain external evidence requirements.

## SEC03 — BLOCKED

Real-provider SEC reconciliation for this delivered source

Source: `terminal/stocks/qualification.py`, `scripts/qualify_sec_sources.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Existing owner observations retained separately;no request in this task

Identifying configuration and permitted target access are unavailable here;fixtures do not establish fresh provider results.

Disposition: Owner existing configured environment;no secret/contact re-entry requested

Dependency: Configured identifying SEC User-Agent and permitted owner target;current task forbids provider calls.

Next action: Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## MD01 — COMPLETE

Read-only IEX permissions,credentials and fixed destinations

Source: `terminal/stocks/private_iex.py`, `terminal/stocks/auth.py`, `terminal/stocks/alpaca_transport.py`, `terminal/stocks/live.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline211cohort;private-IEX qualification tests retained

Explicit read-only stream gate,reviewed permission scopes,server-only credentials and fixed data hosts;real/paper execution remain independently disabled.

Disposition: Implemented bounded research contract;retain tested behavior

## MD02 — COMPLETE

Live quote/trade infrastructure,ordering,dedup,reconnect,subscriptions

Source: `terminal/stocks/live.py`, `terminal/stocks/retry.py`, `terminal/stocks/test_reconnect_stability.py`, `terminal/server/market_events.py`, `terminal/stocks/trade_tape.py`, `terminal/stocks/test_live_recovery.py`, `terminal/stocks/test_live_recovery.py`, `terminal/web/src/marketContract.ts`, `terminal/stocks/test_live_recovery.py`.

Evidence: 36focused IEX recovery/retry/checkpoint cases and263final guarded cases per five supported binding environments. Cancellation-resistant worker timeout and late-frame rejection reproduced/fixed;no live provider. Current273guarded cases per5binding profiles passed;source/provider gates and provisional Kraken status unchanged.

A reproduced one-quote-per-reconnect flap could reset failure count indefinitely. Retry count now resets only after a stable subscribed interval(default30s,bounded1–300),including quiet transport liveness without inventing observations. Backoff,permissions,generation isolation and source-gap limitations remain. Concurrent commands now serialize to prevent orphan workers;retired sockets cannot publish;provider error code and actual phase are bounded and redacted rather than inferred entitlement meanings. Bounded cancellation drain now revokes publication before await,retains a pending worker and denies replacement until drain;accepted prefix stays unchanged.

Disposition: Repaired and offline verified;not a lossless-capture claim

## MD03 — COMPLETE

Historical IEX bars,quotes,trades and explicit delayed-SIP profile

Source: `terminal/stocks/alpaca_history.py`, `terminal/stocks/historical_v2.py`, `terminal/web/src/HistoricalMarket.tsx`, `terminal/web/src/HistoricalResearch.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline58focused historical tests and browser journeys

Bounded pages,exact nanoseconds,OHLC,duplicate accounting,cache TTL and explicit SIP15-minute boundary. No automatic feed upgrade;no complete-session inference.

Disposition: Implemented bounded research contract;retain tested behavior

## MD04 — COMPLETE

Historical bar display and source error reporting

Source: `terminal/web/src/barChart.ts`, `terminal/web/src/EquityPanels.tsx`, `terminal/stocks/alpaca_history.py`, `terminal/server/app.py`.

Evidence: Retained prior checkpoint evidence unless updated below: New7unit+4Python+10browser checks;retained failing-before logs

This sprint fixes synthetic-as-observed chart labels,validates bounded exact OHLC before geometry,and distinguishes fixed safe failure categories without reflecting source bodies.

Disposition: Implemented bounded research contract;retain tested behavior

## MD05 — BLOCKED

Actual owner IEX live/historical qualification

Source: `scripts/private_iex.py`, `docs/qualification/PRIVATE_IEX_RUNBOOK.md`.

Evidence: Retained prior checkpoint evidence unless updated below: Zero provider requests in this task

Owner-reported Support384778 covers the narrow private research use. This runtime has no configured credentials/private-owner environment. No fresh source/entitlement/freshness evidence.

Disposition: Environment-dependent read-only qualification;do not activate credentials or gates here

Dependency: Owner-private target,credentials/authorized feed and a separately approved read-only test.

Next action: Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## MD06 — PARTIAL

Complete corrected exchange tape and lossless reconnect

Source: `terminal/stocks/trade_tape.py`, `terminal/stocks/test_trade_tape.py`, `terminal/web/src/tradeTape.ts`, `terminal/web/src/TradeTapePanel.tsx`, `terminal/tests/check_trade_contract.py`.

Evidence: Existing13 ledger tests/1000oracle candidates retained;new handover-window regression and actual TypeScript admission for the handover;8cross-language market checks. Observed cancellation profile still unqualified.

Bounded normalized reference ledger now supports exact original matching,correction chains,retirement,duplicates,capture-order replay,provenance and fail-closed totals. Explicit authored C-cancellation contract works. Observed cancellation/error action profile and complete/lossless exchange capture remain unimplemented/unqualified. Version 2 also fences local capture namespaces,so equal per-process generations cannot mix records from separate captures. This namespace is not an exchange session/sequence.

Disposition: PARTIAL because working reference reconciliation now exists,not because the stronger requirement was removed. Observed action semantics and lossless/source-complete contract still need authoritative evidence and an explicit decision.

Remaining: Authoritative observed cancellation/error mapping and complete/lossless source-tape recovery are still absent. Current IEX profile has no independently complete exchange sequence/backfill proof.

Dependency: Authoritative action semantics and source completeness/backfill contract;no guessed C/E actions or missing trades.

Next action: Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional effort: 1–2 engineer-days for a specified bounded observed-action profile;complete/lossless guarantees cannot be estimated or promised for a source that lacks that authority.

## MD07 — PARTIAL

Official-contract Kraken cryptocurrency L2 and native/product integration

Source: `terminal/providers/kraken.py`, `terminal/providers/supervisor.py`, `terminal/providers/test_recovery_hardening.py`, `terminal/providers/test_differential.py`, `terminal/server/engine.py`, `terminal/web/src/OrderBook.tsx`, `terminal/l2_research.py`.

Evidence: 62offline provider cases including10,000authored independent transitions;finite scientific JSON precision/CRC,one-worker concurrency,bounded retiring-worker fence,retry exhaustion and invalid jitter regressions;inside263guarded cases. No current official documentation or live payload received. Current273guarded cases per5binding profiles passed;source/provider gates and provisional Kraken status unchanged.

Existing provisional snapshot/absolute-update/top10CRC and native L2 projection are retained. Exact finite JSON scientific-number conversion and physical worker/retry recovery were repaired. Existing source-labelled native book/depth/research views remain connected. Official schema/options/checksum/session semantics and legal source qualification are not independently verified;provisional status is unchanged.

Disposition: Track the explicitly requested Kraken requirement without calling candidate fixtures an official verified adapter. No observed display,retention or connectivity is activated.

Remaining: Retrieve and verify the current official WebSocketv2 book/checksum/trade/status/session contract and applicable usage evidence;reconcile candidate rules and add source-versioned fixtures. Actual later private-provider and browser qualification remain unrun. Do not change the provisional flag before evidence exists.

Dependency: Current official protocol/rights evidence;earlier CONNECT403 and enforced policy excluding Kraken docs/feed domains remain recorded. No blocked operation was retried and no proxy bypass attempted.

Next action: Obtain an authorized official specification copy or permitted documentation-only access,then implement verified source-specific differences. Continue offline contracts;never infer L3 or IEX equity depth.

Conditional effort: 1–3engineer-days for a bounded documented source-contract reconciliation/test package once authoritative material is available;live/owner qualification separate.

## RES01 — COMPLETE

Research configuration,calculations,results and authored exports

Source: `terminal/stocks/research.py`, `terminal/stocks/advanced_models.py`, `terminal/stocks/portfolio.py`, `terminal/stocks/evaluation.py`, `terminal/web/src/researchExport.ts`.

Evidence: Retained prior checkpoint evidence unless updated below: Baselinefrontend and stock cohorts;native mathematical references retained Current guarded175-case cohort passed in all five supported binding environments;no source/target acceptance implied.

Bounded HMM/GARCH/Kalman diagnostics,causal strategy/walk-forward,risk/portfolio and deterministic exports exist. Native exact mathematics remain unchanged.

Disposition: Implemented bounded research contract;retain tested behavior

## RES02 — COMPLETE

Historical bar-to-research/compatible3D workflow

Source: `terminal/stocks/historical_research.py`, `terminal/web/src/historicalResearch.ts`, `terminal/web/src/HistoricalResearch.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline58historical Python checks;Sprint4 browser numerical/export assertions

Accepted revisions drive exact trailing returns,SMA,drawdown and log variation. Quotes feed quote projections;bars cannot become depth or signed events.

Disposition: Implemented bounded research contract;retain tested behavior

## RES03 — BLOCKED

Empirical forecasting quality,calibrated fills or alpha

Source: `terminal/stocks/evaluation.py`, `src/simulation/simulator.cpp`.

Evidence: Retained prior checkpoint evidence unless updated below: No new observed evaluation dataset

Mathematical and causal fixture agreement do not establish predictive accuracy,profitability or exchange execution fidelity.

Disposition: Requires independently justified observed-data study;not software completion evidence

Dependency: Legitimate observed evaluation data and independently defined out-of-sample research protocol.

Next action: Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## REL01 — COMPLETE

Bounded observation persistence,recovery,backup and corruption rejection

Source: `terminal/stocks/observation_store.py`, `terminal/stocks/history_store.py`, `terminal/stocks/history_backup.py`.

Evidence: Existing10 persistence tests plus21new control/recovery tests inside121no-launch tests per environment;legacy/full recover() behavior preserved. Current guarded175-case cohort passed in all five supported binding environments;no source/target acceptance implied.

Preflight counts/bytes/types,single read snapshot,strict payloads/hash chain and private snapshots exist. Observed retention defaults off;no storage activated here.

Disposition: Implemented bounded research contract;retain tested behavior

## REL02 — PARTIAL

Crash-safe hot live/L3 recovery and hardware durability guarantees

Source: `terminal/stocks/live.py`, `terminal/stocks/live_checkpoint.py`, `terminal/stocks/observation_store.py`, `terminal/stocks/test_live_checkpoint.py`, `include/gig/itch/restart.hpp`, `include/gig/book/order_book.hpp`, `src/book/order_book.cpp`, `include/gig/replay/replay.hpp`, `src/replay/replay.cpp`, `include/gig/market_data/aggregate_depth.hpp`, `src/market_data/aggregate_depth.cpp`, `terminal/native_recovery.py`, `terminal/test_native_recovery.py`, `terminal/test_aggregate_recovery.py`, `tests/test_hot_checkpoint.cpp`, `include/gig/itch/hot_checkpoint.hpp`, `src/itch/context_checkpoint.cpp`, `src/itch/hot_checkpoint.cpp`, `src/itch/hot_identity.hpp`, `terminal/session_recovery.py`, `terminal/test_session_recovery.py`, `tests/test_itch_hot_checkpoint.cpp`, `include/gig/itch/durable_checkpoint.hpp`, `src/itch/hot_codec.cpp`, `src/itch/hot_codec_fields.hpp`, `include/gig/itch/source_recovery.hpp`, `src/itch/source_recovery.cpp`, `python/bindings/itch_recovery.cpp`, `python/gig_microstructure/itch_recovery.py`, `terminal/itch_recovery.py`, `terminal/test_itch_durable_recovery.py`, `tests/test_itch_durable_checkpoint.cpp`, `tests/test_itch_source_recovery.cpp`.

Evidence: Six full CTest profiles:152/152/153 GCC;152/152/148 Clang. Each ran363durable+163source checks,57decode/restore+63encode+67source allocation failpoints and all8frozen identities. Nine real-native Python/file/cross-process cases inside273guarded tests per5binding profiles.

Bounded version1 deterministic full typed ITCH serialization now restores context,receipts,retired/match/lifecycle/cursor state and both native books/journals. Independently retained artifact/config/code/capture/generation admission;authored-empty and complete-seed hot profiles. Plain and complete-member gzip coordination verifies committed prefix receipts without applying them and applies only suffix events. Private immutable files survive tested local process interruption;no automatic application startup or provider activation.

Disposition: Bounded authored full-ITCH hot recovery and Python/private-file admission are implemented and offline verified. Full product/startup and observed/hardware qualification remain open;do not reimplement the codec.

Remaining: Bounded durable full-ITCH/seed/framer/gzip contracts are implemented. Automatic application startup selection/full-ITCH product-session integration remains unwired;no provider/observed data or target power-loss acceptance. This preserves the no-launch directive and existing startup behavior;it is not full operational completion.

Dependency: Product session selection/recovery policy and integration tests;observed initialization/source continuity and actual private-target/hardware evidence for empirical claims.

Next action: Integrate an explicit opt-in,fail-closed product-session selection policy using the completed SDK/files rather than replaying committed events. Continue remaining XBRL semantics. Keep target/provider qualification separate.

Conditional effort: Conditional planning range1–3engineer-days for narrowly scoped opt-in full-ITCH product-session wiring and its failure matrix;not a guarantee. Observed/source/hardware qualification depends on actual external evidence.

## SECURITY01 — COMPLETE

Strict private Origin/Host,HTTP proof and WebSocket lifecycle

Source: `terminal/server/app.py`, `terminal/server/request_proofs.py`, `terminal/server/stream_tickets.py`, `terminal/server/connection.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline274native/API tests;existing localTLS/forged-header tests

Exact configured origins,bounded target-bound one-use proofs,Host checks and sanitized diagnostics retained;no wildcard CORS or arbitrary forwarded-header trust.

Disposition: Implemented bounded research contract;retain tested behavior

## SECURITY02 — COMPLETE

Frontend budgets,errors and disabled execution safeguards

Source: `terminal/web/src/response.ts`, `terminal/server/app.py`, `terminal/paper/alpaca.py`, `terminal/stocks/private_iex.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline130frontend and211/274backend checks;prior fake-broker evidence retained

Incremental2MiB read,abort/cancel,strict mutations and default-disabled independent paper/live controls. No provider/account calls or orders in this task.

Disposition: Implemented bounded research contract;retain tested behavior

## SECURITY03 — PARTIAL

Runtime/dependency security clearance

Source: `terminal/server/requirements.txt`, `terminal/web/package-lock.json`, `docs/qualification/institutional-sprint-2/DEPENDENCY_ARTIFACT_QUALIFICATION.md`.

Evidence: New strict control/filing/response admission and source-bound current121/153checks;prior pinned-dependency advisory evidence retained,not target security clearance.

Current public advisory metadata was obtained without market/account access. Runtime dependency pins were not changed. This does not clear target OS,all optional/transitive deployment artifacts,private edge or future advisories.

Disposition: Repository-level advisory review completed;target-specific OS/artifact/security clearance still required.

Remaining: Owner-target OS,full deployed/transitive artifact and private-edge clearance remain pending. Prior advisory metadata remains source-bound prior evidence.

Dependency: Actual deployment artifacts/runtime/OS and private-edge environment;no production clearance from fixtures.

Next action: Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional effort: 0.5–2 engineer-days after exact target artifacts are available;future advisory clearance is time-dependent.

## OPS01 — COMPLETE

Private startup,exact-SHA upgrade,rollback and qualification tools

Source: `scripts/start_terminal.sh`, `scripts/qualify_private_deployment.py`, `docs/qualification/institutional-sprint-2/DEPLOYMENT_ACCEPTANCE.md`.

Evidence: Retained prior checkpoint evidence unless updated below: Prior clean receipt plus baseline development checks;no owner deployment claimed

Existing runbooks preserve local changes,do not reset/clean,bind source/assets and distinguish offline/edge qualification. No missing new deployment tool found.

Disposition: Implemented bounded research contract;retain tested behavior

## OPS02 — BLOCKED

Owner-authenticated Codespaces HTTPS/WSS acceptance

Source: `scripts/start_terminal.sh`, `terminal/tests/check_browser_handshake.mjs`.

Evidence: Retained prior checkpoint evidence unless updated below: Only local browser/forwarding fixtures available

No actual owner edge,cookies/credentials or private-port authentication accessed.

Disposition: Single final owner acceptance after delivery;no intermediate manual tests requested

Dependency: Actual owner-authenticated private Codespaces edge and authorized application startup.

Next action: Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## OPS03 — BLOCKED

Current-candidate genuine native ARM64 qualification

Source: `.github/workflows/native-arm64.yml`, `terminal/test_arm64_terminal_policy.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Manual-only/free-owner/branch policy tests;not dispatched

Earlier tested SHAs do not qualify new code. Existing six-configuration workflow includes strict native/API and updated stock cohort.

Disposition: Owner-authorized free runner execution against exact delivered SHA;not cross-compile-as-runtime evidence

Dependency: Current-candidate genuine free native ARM64 runner and owner-authorized manual execution.

Next action: Cannot resolve through code alone within no-launch/no-unauthorized-access/no-paid-resource constraints

## UX01 — COMPLETE

Readable dark/light,responsive,keyboard and reduced-motion engineering

Source: `terminal/web/src/workstation.css`, `terminal/web/src/Navigation.tsx`, `terminal/web/src/cameraMotion.ts`.

Evidence: Retained prior checkpoint evidence unless updated below: Baseline130frontend/workstation browser checks;prior5690text-contrast evidence

Semantic controls,focus,contained table/navigation scrolling,comfortable text and responsive canvases implemented;no new visual redesign in this sprint.

Disposition: Implemented bounded research contract;retain tested behavior

## UX02 — PARTIAL

Full WCAG2.2AA and physical-device acceptance

Source: `terminal/web/src/BarValues.tsx`, `terminal/web/src/EquityPanels.tsx`, `terminal/web/src/HistoricalMarket.tsx`, `terminal/web/src/barValues.test.ts`, `terminal/web/src/AcceptanceFacts.tsx`, `terminal/web/src/acceptanceFacts.test.ts`.

Evidence: 153frontend checks include2new actual acceptance-leaf SSR checks;no application,browser or physical-device launch.

Exact-value keyboard-readable bar tables now supplement hover-only candles in company/archive views;calendar-history reuses its existing table. Source caption,scoped headers,nanoseconds,units and zero volume are preserved. Native dialog,skip link and existing keyboard controls already existed and were preserved.

Disposition: Feasible text alternative implemented. Physical devices,screen readers and exhaustive WCAG2.2AA/current browser qualification remain unverified.

Remaining: Current real-browser,assistive-technology,device and exhaustive WCAG2.2AA qualification remain unperformed under the no-launch directive.

Dependency: Separate authorization to launch/test actual browsers and access to target devices/assistive technology.

Next action: Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional effort: 1–3 engineer-days for targeted acceptance and resulting confirmed repairs once browser/device tests are authorized;unknown failures cannot be estimated in advance.

## CLEAN01 — COMPLETE

Obsolete user-facing branding and safe frontend cleanup

Source: `terminal/web/index.html`, `terminal/web/src/workstation.ts`, `terminal/web/src/App.tsx`.

Evidence: Retained prior checkpoint evidence unless updated below: Branding unit/browser checks and source search

User-facing identity is GIG. Historical reports and compatibility technical keys are preserved;unused code is not deleted merely on a name-based guess.

Disposition: Implemented bounded research contract;retain tested behavior

## SCOPE01 — NOT APPLICABLE

Real/paper execution,paid feeds,public deployment and redistribution

Source: `terminal/stocks/private_iex.py`, `terminal/paper/alpaca.py`.

Evidence: Retained prior checkpoint evidence unless updated below: Default-disabled boundary tests

Explicitly outside this observation-only sprint. Existing fake-paper harness is not owner order authorization.

Disposition: Keep disabled;no expenditure,provider/account mutation or public forwarding

Next action: No additional faithfully specified code repair identified after this continuation;see remaining source/target/contract requirements

## SCOPE02 — PARTIAL

Historical A18/A19 requirement and concentration acceptance

Source: `terminal/server/concentration.py`, `docs/remediation/sprint-2/REMAINING_BLOCKERS.md`.

Evidence: Retained prior checkpoint evidence unless updated below: Existing exact supplied-depth HHI tests;original69c9f48 audit read from Git

Exact source-bound supplied-depth HHI exists. Earlier audit preserves unknown original estimator/baseline. Attempt to recover the original pasted master text in this session failed authorization/resolution;no restricted dataset was accessed.

Disposition: Owner decision:recover the original requirement or approve a prospective versioned baseline/HHIv1 contract. No retroactive acceptance or new estimator invented.

Remaining: Original A18/A19 baseline/estimator still unknown;no retroactive completion or substitute estimator.

Dependency: Recover original requirements or approve an explicitly prospective versioned contract.

Next action: Independent offline package completed;the listed missing contract/source/target requirement remains open.

Conditional effort: Cannot estimate historical acceptance closure before the missing contract is resolved;writing a prospective contract is a distinct owner decision.
