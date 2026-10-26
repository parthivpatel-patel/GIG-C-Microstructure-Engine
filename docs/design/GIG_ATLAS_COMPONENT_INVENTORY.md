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
