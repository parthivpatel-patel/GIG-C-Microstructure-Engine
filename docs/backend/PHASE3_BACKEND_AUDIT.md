# ATLAS Phase 3 source-level backend audit

October 26, 2026 America/New_York. Baseline3596c38f2b606fd463cf50dea2b6a873ce8f1407;
work isolated on feat/atlas-phase3-backend. Source inspection and fresh tests,not old
reports,are the basis of the classifications below. No critical native defect was
reproduced in this phase. The new history receipt bug was found and repaired during
implementation;initial9-test attempt had1 failure/1 error and is preserved locally.

|Capability|Status|Actual implementation and limit|Evidence / next gate|
|---|---|---|---|
|Identity/search|Partial|stocks/identity.py:instrument/search;8 curated CIK routes,not official live directory|Existing identity tests;official directory reconciliation missing|
|SEC transport|Implemented/gated|stocks/service.py:permission/fetch/refresh;fixed HTTPS,identifying UA,one request/s,no redirects/retries,bounded bodies,partial results|Workspace/security tests;no current UA,so official request not executed|
|SEC financial parsing|Implemented selected facts|stocks/sec.py:facts;16 metric tag families,exact decimals,as-of filings,256 rows/metric,16 revisions|Existing backend and independent raw-record tests;not full statement reconstruction|
|SEC periods/amendments|Partial|Actual start/end/duration,filing fiscal context;latest-per-concept restatements;amendments distinct|Period/53-week/missing/ambiguous cases;no inferred Q4/YTD subtraction|
|Financial descriptors|Implemented|stocks/financials.py:calculate;12 exact period-aware descriptors|null/reason if incompatible;source reconciliation externally blocked|
|SEC filings|Partial|Recent submissions,128 selected rows;v2 offset/form pagination|Filing/browser tests;older shards not acquired|
|Official SEC reconciliation|Blocked here|scripts/qualify_sec_sources.py independently checks selected raw records|Current User-Agent absent and local review gates disabled;owner command supplied|
|Historical prices|Implemented bounded core|stocks/history.py:normalize/from_workspace;typed source,four pages/256 bars,exact units/timestamps,digests,transactional cache boundary|New13-case cohort;no automatic upstream paging or exchange calendar|
|Historical cache|Partial|Existing eight-symbol process cache,manual refresh;last accepted query per symbol|Cache rejection regression;no persistent/multi-query history cache|
|IEX REST|Implemented/gated provisional|stocks/prices.py and service.py;raw bars/latest L1 quote/print|Authored source tests;support381230 unresolved,zero live activation|
|Indicative options|Implemented/gated provisional|stocks/option_feed.py and OptionChain.tsx;not OPRA or executable depth|Existing fixture/model tests;separate permission gates remain|
|Alpaca WebSocket transport|Missing/blocked|No actual Alpaca wire authentication/subscription/reconnect client|No protocol invented from crypto adapters;requires official current protocol and permission review|
|Freshness/subscription preparation|Implemented offline core|stocks/feed_health.py;generation-bound acknowledgements,8 symbols,receipt-clock stale policy;heartbeat cannot refresh data|New deterministic disconnect/reconnect/forgery/clock tests;not a network qualification|
|Crypto live architecture|Implemented/gated|terminal/providers supervisors/transports;separate receipt/heartbeat/stale/recovery semantics|Existing native-consumer/provider tests;configuration not proof of entitlement|
|Descriptive research|Implemented|stocks/price_research.py;exact returns/drawdown/tail risk/sample variance;approximate realized volatility|Independent rational and Decimal.sqrt references;raw adjustments/session gaps disclosed|
|GARCH/HMM/Kalman|Partial fixed demonstrations|stocks/research.py;fixed causal recurrences/filter,no parameter estimation|Existing and new prefix/recurrence tests;fitted models/residual diagnostics/OOS evaluation missing|
|Native book/matching/TCA|Implemented synthetic scope|include/gig and src;bounded journal/replay,recovery,matching,analytics|Fresh six native CTest configurations;not exchange-equivalent empirical L3 validation|
|ITCH/initialization|Implemented bounded profiles|include/gig/itch;framing/context/reconstruction/streaming/admin/HY;explicit authenticated starting-state evidence|Independent8 canonical references;unsupported historical semantics remain explicit|
|LOBSTER empirical work|Blocked|Private attached archive remains unauthorized for cloud processing|No inspection/extraction/processing in this assignment|
|Browser integration|Implemented|Phase2 preserved;Stock overview shows history boundary;new cache-only v2 endpoint|Stable-assets browser suite including AAPL/NVDA selection/native transport|
|Security/operations|Implemented bounded local scope|Private8787,server secrets,origin/proofs,no broker execution|46 security/8 TLS-WSS checks;external Codespaces acceptance remains owner gate|
|Release/production|Not qualified|No HA/durable recovery/operational SLO/exchange certification claimed|Owner exact-HEAD ARM64 and external research acceptance required|

No speculative native repair,warning suppression or canonical acceptance change was
made. Native prebuilt trees match unchanged native source scope;fresh tests exercise
those existing binaries rather than claiming fresh cross-toolchain compilation.
