# Live market /3D source audit before implementation

Baseline6af0bdef51007d6058f4f3119ecf5bac21c61ceb,feat/atlas-final-release.
Actual backend is Starlette/ASGI,not FastAPI. Native C++20/replay/matching/TCA and Python
bindings remain separate from venue-limited stock quotes. SEC repair/private configuration
must be preserved. No market data or external provider request authorized by test fixtures.

Source findings:
* terminal/stocks/live.py:fixed official IEX MessagePack endpoint,existing5 permission
  gates plus explicit live enable,4 symbols,32KiB frames,4 queued frames,atomic frame
  validation,256 identities,bounded reconnect. Only q/t;last-observation map overwritten by
  old timestamps;no retained history/analytics,receive wallclock or bar/correction contract.
* terminal/web/src/LiveIEX.tsx:single-symbol controls,5s polling,no multi-panel comparison.
* terminal/web/src/Landscape3D.tsx:two instanced meshes,but allocated/disposed every data
  update;event-driven render,resize/controls cleanup,no presets/fullscreen/palette selector.
* Landscape.tsx:optional lazy Three loading and independent2D native depth fallback.
  Native history is discrete book observations,not equity Level1 or observed L3 validation.
* identity.py:8 curated seeds;GOOGL/AMD/SPY missing. No official fresh directory claim.
* app.py:/stocks/live already protected by Origin/Host/scoped proof;one shared upstream
  manager. No browser push stream for stocks;native WS must not silently carry equity book
  mutations. Provider rights/credentials unavailable here;live acceptance remains blocked.

Plan:bounded typed live history/order diagnostics/exact L1 metrics,bars/correction
observations from pinned official SDK source;shared4-symbol controls;one optional GPU
renderer for comparison lanes (scissored independent panels deferred);2D fallback/explicit replay isolation. Preserve
security/canonical outputs. Dynamic changes may use controlled shared-stream replacement;
never one upstream socket per panel. Requirement matrix will distinguish partial/unverified
features,including exchange calendar authority and missing source sequence coverage.
