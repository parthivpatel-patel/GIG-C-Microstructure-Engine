# Workspace-level functional acceptance

Application SHA: `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`.
The actual React application and native C++ extension ran locally. All12 workspaces
passed ordinary-click navigation, matching heading/section, active navigation and
contained layout at360/390/768/1280/1920, dark/light:120 checks. This is Chromium154
with SwiftShader/emulated viewports, not actual Android or owner-target acceptance.
Source: `terminal/web/src/App.tsx:19–20`; detailed declarations are in the CSV.

| Workspace | Primary observed mode / source | Actually verified | Remaining qualification or functionality limits |
|---|---|---|---|
| Command Center |SIMULATED native session plus curated references|Navigation/search shell,watchlist paths and research warnings render;all viewport/theme checks pass.|No genuine live overview established. Dynamic search combinations/recent state branches not all individually exercised.|
| Securities Universe |SIMULATED authored listing/SEC fixture in browser;default curated13 references|Search/filter source paths,coverage disclosure and responsive table container;parser/index tests and50,002-authored-record scaling.|No fresh complete US listing feed. SEC registrants are not exchange listings;tradability and feed entitlement separate.|
| Stock Intelligence |SIMULATED authored financial/model responses;owner SEC state independently UNVERIFIED|Company/UI render,backend exact descriptors/period/provenance tests,original search/watchlist steps,raw pricing reference and theoretical plane updates.|Committed stock browser fails stale display assertion;remaining steps of that program NOT_RUN. Full XBRL/IFRS/taxonomy/PIT and every filing/filter UI branch not independently qualified.|
| Live Markets |DISCONNECTED actual Alpaca path;explicit injected fixture used only in dedicated3D test|Bounded SSE/MessagePack/ordering/reconnect/permission tests;per-symbol fixture quote/trade rendering,4 L1 modes.|No live provider session or authorized account/feed limits verified. Readiness flags/keys do not prove entitlement.|
| Multi-Stock Comparison |DISCONNECTED actual feed;shared LiveMarket component with comparison flag|Separate navigation/container,per-symbol fixtures,normalized basis-point/variation geometry and isolation tests.|No actual synchronized cross-stock observations;baselines may have different times. Watchlist does not increase subscription allowance.|
| Order Book |SIMULATED native L3 authored replay|Actual C++ levels,metrics/FIFO tests,exact units,provenance,proposed HHI,all viewport/theme checks.|Not AAPL/Nasdaq observed depth. HHI proposal is not original A19 acceptance.|
| Market Depth |SIMULATED native snapshots or authored provider-shaped aggregate profile|Cumulative depth/2D source path;legacy3D pixels change after native step with camera unchanged;input/source/camera table available.|L1 does not populate deeper levels. Snapshot history coalesced;unknown unobserved paths remain unknown.|
| Order Flow |SIMULATED event/native source;crypto observed flow gated|Event tape/source state,advanced event/flow glyphs,exact native flow test cases;explicit aggressor input requirement.|Quote changes cannot identify individual orders/trades. Real IEX unsigned prints cannot establish full OFI/queue or calibrated VPIN.|
| Historical Replay |SIMULATED complete authored boundary;retained recording support separate|Step/seek/speed/play/pause/restart tested in native/server suites;frozen identities deterministic;source labels.|ITCH/LOBSTER browser import not implemented;CLI contracts exist. Genuine historical initialization/full history remains unqualified.|
| Execution Simulator |SIMULATED native fixed-liquidity scenario|TWAP/VWAP/POV/native matching,TCA,partial/rejected/cancelled reports tested;simulated labels preserved.|No broker calls,account reconciliation,buying power or observed fill model. Fixed zero-fee benchmark scenario is not execution-quality calibration.|
| Research & Validation |SIMULATED / user-authored assumptions|HMM/GARCH/Kalman/portfolio/backtest numerics,holdout contracts,GARCH441-vertex surface/parameters/cameras/context-loss tested.|No empirical alpha/significance,cointegration/factor/optimizer implementation or reliable trading signal. Model controls are not all individually browser-tested.|
| Operations |Local operational diagnostics;source status disconnected|Health/source receipt/private-output contract,policy/TLS/quiet feed/counters/shutdown tests;actual local receipt MATCH.|Owner authentication,system advisory clearance,upstream telemetry,long sessions and current-candidate ARM64 remain separate.|

## Common interaction, accessibility and failure findings

- The120 checks prove rendering/navigation/layout, not every button's semantics.
  The CSV deliberately leaves288 individual control/option declarations unverified
  where this audit lacks an individual executed flow. Some share backend contracts
  or prior tests;that is not a replacement for current interaction evidence.
-23 additional advanced browser checks verify actual camera presets,keyboard pan,
  drag,wheel,fullscreen,timeline,symbol/side filters,point/voxel selection,pause,
 2D fallbacks,construction/context-loss/retry and canvas disposal. All8 advanced
  modes were exercised across80 theme/width combinations inside one grouped check;
  those are not80 additional independently counted tests.
- Theoretical model/return forms are explicitly authored,not values from the
  selected equity. Options,models and scenario labels must remain so.
- Existing backend tests cover loading/missing/stale/errors and safe structured
  responses;they do not establish real-provider behavior. Source failures retain
  accepted cache state rather than invent new observations.
- Keyboard navigation,semantic labels/reduced motion/table alternatives are
  present and partly exercised. No comprehensive screen-reader,contrast/WCAG2.2AA
  certification,physical Android or prolonged mobile-GPU test was performed.
- The inspected mobile ribbon screenshot includes a visible focused global skip
  link over part of the model-selector area. This may be the intentional focused
  skip-link state;its persistence/pointer impact was not independently reproduced.
  Preserve keyboard access and verify touch/focus dismissal before mobile acceptance.
  No overlapping-control defect is claimed resolved by layout counts. No forced
  clicks were used. An unknown/unexercised branch is not silently marked PASS.

Source freshness differs from transport status. A connected local WebSocket or SSE
heartbeat is not evidence of a fresh market quote. Observed/private target facts
are separately recorded in SECURITY_AND_DEPLOYMENT and MARKET_DATA_PROVENANCE.
