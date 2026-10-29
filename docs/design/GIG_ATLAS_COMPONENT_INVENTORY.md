# GIG ATLAS component inventory

| Source/component | Responsibility | Verification |
|---|---|---|
|App.tsx|Shell,global search,theme/help,navigation,Command Center,native simulation controls|Existing native browser21;ATLAS workspace matrix|
|StockIntelligence.tsx|Memoized company loading/selection,watchlist,legacy workspaces,v2 fetch lifecycle|Configured/unavailable stock browsers;v2 error/stale cases|
|FinancialWorkspace.tsx / FinancialWorkspace|Focused summaries,trends,selected statements,exact descriptors|ATLAS browser and pure display/period tests|
|FinancialWorkspace.tsx / Trend|Bounded SVG comparable-period projection,description,exact table|Independent raw fixtures,ambiguity/mixed-period negatives|
|FinancialWorkspace.tsx / FilingExplorer|Read-only filing page/filter/source references|Amendment and official-link browser checks|
|financial.ts|Exact compact display,descriptor unit display,period selection,comparability,contract validation|Seven new unit tests plus existing four formatting/contract tests|
|ResearchSummary.tsx / ResearchSummary|Fixed HMM/GARCH/Kalman and empirical-tail summaries|Existing authored model endpoint/browser tests;no empirical claim|
|ResearchSummary.tsx / SimulationSummary|Actual native cost,child-order and fill presentation|Existing three-algorithm independent native browser comparisons|
|api.ts / readCompanyV2|Same-origin,GET-only,bounded/timeout v2 read|Real API browser tests with malformed/stale response interception|
|atlas.css|Tokens,theme,layout,cards,focus,skeletons,tables,dialog,responsive rules|Five widths,contrast tokens,keyboard/dialog checks|
|Landscape,EquityPanels,OptionChain,VolatilitySurface|Existing native/observed/theoretical chart boundaries|Preserved Chromium/WebGL/native/stock regressions|
|atlas_fixture_server.py|Local-only authored multiyear financial fixture,no provider requests|Fixture safety health guard and explicit synthetic classification|
|atlas-validation.mjs|Actual browser integration,visuals,negative controls,responsiveness|JSON evidence and screenshots under ignored build/atlas|

Existing Panel/Box wrappers remain compatible. This checkpoint shares visual primitives
through tokens/classes rather than introducing a new component framework. Further
consolidation should preserve existing semantic labels and regression coverage.

## Phase2 additions

DepthChart(lightweight),Landscape(optional boundary/loader),Landscape3D(preserved renderer),
OptionalBoundary(deployment-chunk isolation),BalanceComparison(shared-scale matched
instants),FilingExplorer(server-filtered bounded cache pages),and two Phase2 browser/
performance harnesses. See GIG_ATLAS_PHASE2_REPORT.md for current loading policy;
prior Phase1 capture/evidence remains historical.


## Product-development expansion (October28,2026)

The shell now preserves the original nine workspaces and adds Securities Universe,
Live Markets and Multi-Stock Comparison. `ResearchDesk` is the company-first overview;
`UniverseWorkspace` consumes bounded versioned discovery/contracts;`CompanyCoverage`
separates identity,financial and acquisition evidence. `WorkspaceIcon` supplies twelve
original SVG marks. `QuoteCloud` delegates four source-aware modes to pure
`marketGeometry`;`ModelSurface`/`modelSurface` independently render the declared GARCH
response grid. Native L3 remains in its existing renderer,not inferred from live L1.
All optional renderers remain lazy-loaded. See the current product report/evidence for
actual browser,cleanup,responsive and qualification boundaries.


## Provider/history integration (October29,2026)

`HistoricalMarket` supplies bounded date/kind/timeframe queries,exact source tables,
OHLC views and matched-timestamp raw-close comparison. Pure `historicalMarket`
contracts/normalization have independent reference tests;no SEC ratio is recalculated
in JavaScript. Securities Universe adds source exchange/classification/activity filters
and a separate approved Alpaca asset refresh. Existing3D remains lazy/native-separated.
See `docs/product/PHASE_NEXT_DATA_INTEGRATION_REPORT.md` for fixture-vs-live boundaries.

## Eight advanced research views — October29,2026

| Component | Responsibility | Executed evidence |
|---|---|---|
|research3d.ts|Bounded native/Level1/authored source adapters;eight pure projections;exact VWAP/volume buckets;no snapshot-to-order inference|26 new independent numerical/lifecycle/boundary tests within71 frontend cases|
|ResearchLab.tsx + research3d.css|Lazy source/model/symbol/time/filter controls;prominent evidence labels;bounded table/2D alternative;theme/mobile layout|23 ordinary-click checks including80 model/theme/width combinations|
|ResearchScene.tsx|One independently owned camera/renderer;instancing,batched lines,surface meshes;inspection,fullscreen,loss/retry,cleanup|Actual SwiftShader context loss/constructor failure,keyboard/pointer/camera/fullscreen and disposal checks|
|advanced-research-validation.mjs|Stable-asset native/authored transport integration;existing4 Level1 modes and GARCH preservation|23/23;no real provider qualification|
|measure_research3d.mjs|Fixed authored fixture;10 warmups/100 measured projections per model;deterministic output hash/RSS|Repeated identical output hashes;current numbers in linked report|

[Implementation,source boundaries,measurements and limitations](../product/ADVANCED_3D_RESEARCH_REPORT.md).
