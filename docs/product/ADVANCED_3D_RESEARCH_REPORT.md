# Eight advanced research visualizations — October 29,2026

Implemented on `feat/atlas-final-release`,starting from independently verified local/
remote `9e1443849adf8d5928895f88e5af2b5295d41aee`. Implementation commit:
`841e6e6186866c73e599dd7e633874b40c079330`;final source/provenance repair
`5e68cf4b60a41e04d93670b59f7d17e6540cbf89`. Both pushed and remotely verified.
Main remained `12f3a53943dc245e36f2cbbc35b9910fb21c0718`.

The owner's immediate authorization supersedes the previous conditional development
sequence. All eight views are implemented and fixture/browser validated. This does
not establish live-provider qualification,observed depth availability,empirical L3
correctness,physical-device acceptance,or production readiness.

[Machine-readable evidence](advanced_3d_evidence.json) binds implementation files,
commands' outputs,actual counts,screenshots,performance and frozen native identities.
Local artifacts are in ignored `build/advanced-3d/`;no market data or screenshots were
added to Git. All captured pictures depict independently authored synthetic inputs.

## Implemented models and eligible inputs

| Model | Actual implementation | Genuine Level 1 capability | Current validation boundary |
|---|---|---|---|
| Order-book height-map surface | Price × displayed quantity × capture-order mesh;separate sides,occupied-price holes,exact sample inspection | No depth expansion from quotes | Supplied native snapshots and authored depth;surface connects adjacent retained frames only at matching occupied prices |
| V-canyon liquidity | Cumulative side quantities on signed mid-relative price walls;side/depth filters | No | Supplied book snapshots;display connectors are interpolation,not an unobserved liquidity path |
| Order-event voxels / point cloud | Switchable instanced glyphs for explicit add,cancel,delete,execute records;order identity,price,quantity,time inspection | No order identities inferred | New authored two-symbol event fixture only;native snapshot API currently supplies no explicit event tape to this view |
| VWAP liquidity corridor | Exact integer execution price×quantity sums and denominator;VWAP trajectory with supplied best-quote floor rails | Not connected to unsigned IEX prints in this scope | Explicit authored EXECUTE records;window VWAP,not full-session VWAP or executable capacity |
| Order-flow streamlines / VPIN | Directional execution connectors;exact equal-volume bucket splitting;rolling absolute directional imbalance | No verified trade direction in current IEX profile | Authored declared aggressors;20-unit buckets,last4 completed buckets,incomplete last bucket excluded;toy/un-calibrated,not toxicity evidence |
| Cylindrical market-depth wheel | Retained capture slices,side/rank angular sectors,quantity radii,exact price tooltips | No | Supplied native/authored depth;angles are categorical rank,not price distance |
| Volatility dome | Rolling sqrt(sum of8 squared log-mid changes),with labeled decorative semicircular cross-section | Yes,from at least9 valid ordered quotes | Authored IEX streaming integration and replay snapshots tested;derived unannualized variation,not implied volatility,forecast,or measured depth |
| Bid-ask spread ribbon | Best-quote edges on a time/capture axis;exact integer spread inspection,interpolated display sheet | Yes,ordered best quotes | Authored IEX/replay tested;venue-limited,retained,incomplete;not SIP/NBBO |

Existing four Level 1 geometries (source quotes,shared-basis-point comparison,rolling
variation,trade-size activity),GARCH response surface,and native liquidity landscape
remain available. New browser checks exercise all four existing modes and GARCH
parameter validation,camera and context recovery;existing native browser checks
exercise the original landscape and replay/simulation contracts.

## Access and interactions

The laboratory is available in Market Depth,Historical Replay,Order Flow,and Research
& Validation. It is also available in Live Markets and Multi-Stock Comparison,where
its default source is the existing retained Level 1 history. Click **Open advanced
research**. No 3D selection starts an upstream feed or grants a permission.

Source selection distinguishes supplied native snapshots from `authored-research-v1`.
The latter declares DEMO-A/DEMO-B,240 events/snapshots,integer prices/quantities,known
order references and authored execution directions. It is not an alternative native
book implementation or an observed exchange dataset. Native snapshots remain the
actual C++ application's supplied state;their changes are never converted to invented
order events or fills.

Each open laboratory owns its camera and WebGL resources. Controls include drag
rotation,pinch/wheel zoom,right-drag and keyboard pan,top/front/reset cameras,
fullscreen,symbol selection,time slider/step/follow,pause/resume,side/depth filters,
voxel/point selection,and manual2D/retry controls. Filters that do not apply to a model
are disabled. Hover/tap inspection retains exact source strings or exact integer
VWAP fractions;the accessible paginated table provides the same inspection without
WebGL or precise pointer targeting. Time is explicitly capture order,not elapsed
exchange time. Source/replay nanoseconds are separately exposed;missing clocks stay
unavailable. Display coordinates are approximate binary64/Float32 geometry.

The visible source card records origin,provider,coverage,symbol,input status and
view endpoint. Derived/model status is immediately beneath the selected model title.
The parent's paused/disconnected status is forwarded;retained quote state is disclosed
without asserting currentness. Display pause does not stop ingestion. Synthetic,
observed,derived and modeled meanings are never interchanged.

## Numerical and input boundaries

- Native history is restricted to the latest matching provider/instrument/origin/mode/
  session/scales;invalid,crossed,or non-increasing snapshots are excluded with notes.
- Level 1 uses current-generation,ordered,known-origin quotes only. Missing or mixed
  origin,invalid decimals,crosses,out-of-order messages and out-of-budget fixed-point
  values are excluded or explicitly rejected. Decimal quote prices are converted
  exactly to a common10^18 integer scale before spread/range projection.
- Price/quantity strings remain available;no native-engine arithmetic changed. Exact
  VWAP accumulation uses BigInt. VPIN splits each declared directional quantity across
  equal-volume buckets exactly;missing direction makes it unavailable. Deletes and
  cancellations cannot become traded volume. There is no unsigned-print classifier.
- Volatility uses approximate `log1p` on exact integer mid differences for display;
  no annualization or fitted distribution. Fewer than9 valid quotes gives an empty
  state. Dome width has no independent market interpretation.
- Default source depth is at most12 levels/side,not a claim of complete L3 state.
  Surface/ribbon interpolation is explicitly visual;missing observations stay missing.

## Resource design and measurements

No dependency was added. Both the laboratory and Three renderer use existing lazy
chunks;the shared Three/OrbitControls chunk is not requested by Command Center. Entry
JavaScript is236,210 bytes versus235,735 previously (+475 bytes). The existing514 KB
optional shared Three chunk warning remains visible;it was not suppressed.

Inputs/display budgets:48 candidate native snapshots,32 displayed snapshots,12 levels
per side,256 selected-symbol explicit events,256 total Level 1 observations,128 quotes
per symbol,and at most768 geometry samples. VPIN is capped at512 completed buckets
and100,000 units per declared execution. Tables mount at most24 rows. The fixed
240-event authored fixture is generated once;no retained arrays grow without bound.

One instanced sample mesh and line segments batched by color keep the measured
models at3–9 draw calls and fewer than12 geometries. Rendering is demand-driven with
bounded camera damping;hidden tabs stop drawing. Reduced motion disables damping
when a renderer is created. Pixel ratio is capped at1.25. Geometry,materials,controls,
observers,listeners and renderer/context are disposed on close,retry,or unmount.
Context loss and constructor failure retain2D/table access.

Measured on x86_64 Intel Xeon Platinum8573C,Node24.19.0,10 warmups and100 measured
projections/model,authored input only:

| Model | Median projection ms | p95 ms |
|---|---:|---:|
| Height |1.328|1.964|
| Canyon |2.333|3.450|
| Events |0.346|0.686|
| VWAP |0.282|0.638|
| Flow/VPIN |0.265|0.443|
| Wheel |1.148|2.135|
| Dome |0.154|0.317|
| Ribbon |0.159|0.294|

Process peak RSS122,672 KiB includes Node/runtime and all projection allocations;it
is not isolated geometry memory. Repeated full output hash:
`222811765f4d91b5ac85af367c28cbbd2a01664d58c99dd1e77322e58365eaaa`.
Browser per-model cold/current render submission samples range5.2–49.6 ms in headless
SwiftShader. These are not physical GPU completion times,FPS,exchange latency,or a
mobile performance guarantee. Long-duration physical GPU/device qualification remains
unexecuted.

## Executed final validation

Zero final failures/errors/skips in each listed cohort. Counts overlap and must not be
summed as unique tests. No mandatory native expectation was altered.

| Cohort | Result | Local evidence |
|---|---:|---|
| Frontend unit/numeric/contract |71/71 (26 new)|`unit.log`|
| Terminal/C++ consumer Debug |274/274|`terminal-debug.log`|
| Same,Release |274/274|`terminal-release.log`|
| Same,ASan+UBSan |274/274;liveLSan0|`terminal-sanitizer.log`|
| New ordinary-click browser suite |23/23|`browser.json`|
| Existing native/replay/simulation/landscape browser |21/21|`native-browser/results.json`|
| REST/WS boundary cohort |17/17|`security.log`|
| Verified local HTTPS/WSS proxy |8/8|`tls.log`|
| Frozen native independent references |8/8;all8 hashes identical|`canonical.xml`|
| Installed existing native wheel0.1.1 |14/14|`wheel-consumer.log`|
| Packaging regressions |3/3|`packaging.log`|
| Implementation source archive |831 safe,byte-identical members|`sdist-final-inventory.json`|
| TypeScript strict/production build |PASS;existing chunk warning retained|`build.log`|

The final source archive was built from a clean detached worktree of5e68cf4,excluding
uncommitted report files and all generated/private artifacts.

The live-interpreter LSan checkpoint does not establish stock CPython shutdown leak
qualification. Native sources/backend/provider contracts were unchanged,so no unrelated
full six-compiler engine matrix was repeated. No new ARM64 or hosted workflow ran.

Browser coverage includes80 model×theme×viewport combinations within one check:
all8 models × dark/light ×360,390,768,1280,1920px. Tests use normal clicks,actual
WebGL context-loss extensions,constructor-failure injection,fullscreen,keyboard,
symbol/time/side/glyph controls,2D/retry,source restrictions and native-book isolation.
Observed-origin labels do not arise from fixtures. Chromium154/SwiftShader is not a
physical Android/GPU or owner-authenticated Codespaces preview qualification.

## Failures preserved and resolved

Initial artifacts remain hashed in the evidence manifest:

1. An independent quantity-coordinate assertion exposed needless1e-9 fixed-point
   truncation. Display ratios now use checked finite binary64 division of exact
   centered integers;source arithmetic stays exact. The original assertion passes.
2. Native nested select labels included option text in their accessible names. Explicit
   accessible names now identify the controls;ordinary browser selectors pass.
3. The first Level 1 test froze browser data before it contained9 quotes,despite the
   server already having them. It now waits for at least18 ribbon samples in the
   actual browser before freezing. This preserves the minimum-coverage assertion.
4. An attempted parallel native-browser run altered the shared fixture while this
   suite checked book immutability. Suites now run exclusively against those fixture
   servers. A separate standalone attempt also exposed a test race:click completion
   did not await the last control POST. It now awaits each successful mutation response
   before capturing the isolation baseline. Production immutability checks remain.
5. The Level 1 source card initially omitted the literal coverage class while notes
   contained it. The browser correctly rejected that. The prominent card now states
   IEX venue-limited Level 1 only;parent status is forwarded as well.

6. Final review reproduced cross-dataset snapshot mixing when instrument/session
   fields were identical. The regression failed with2 frames instead of1. Dataset,
   fixture/recording digest,clock and initialization-class identities now also bound
   every native history window. All five independent identity changes are tested.

No assertion,security gate,expected native hash,test buffer,or warning was removed to
obtain a pass. Final browser assets were hashed before/after;no rebuild occurred during
the successful suite. Test servers were stopped before evidence receipts were finalized.

## Visual evidence

Twelve actual browser captures and their hashes are in the evidence manifest,including
all8 authored models,390px light/dark,and the authored IEX-derived dome. Paths are local
ignored artifacts,not files shipped in Git:

- `build/advanced-3d/height-synthetic-desktop.png`
- `build/advanced-3d/canyon-synthetic-desktop.png`
- `build/advanced-3d/events-synthetic-desktop.png`
- `build/advanced-3d/vwap-synthetic-desktop.png`
- `build/advanced-3d/flow-synthetic-desktop.png`
- `build/advanced-3d/wheel-synthetic-desktop.png`
- `build/advanced-3d/dome-synthetic-desktop.png`
- `build/advanced-3d/ribbon-synthetic-desktop.png`
- `build/advanced-3d/ribbon-synthetic-mobile-{light,dark}.png`
- `build/advanced-3d/iex-authored-{ribbon,dome}.png` (actual authored streaming quotes).

Height,flow,mobile light,and IEX-derived dome images were visually inspected in this
session. A separate390px focus probe verified the existing skip link is offscreen
(bottom−30.31px) and the research select center is unobstructed. Tall stitched element
captures can nevertheless include that fixed element;ordinary pointer interaction
works in the actual viewport. See `mobile-focus-probe.json`.
No physical-device visual quality or full WCAG certification is claimed.

## Reproduce offline

Build finalized assets first. Do not rebuild or run another mutating browser cohort
against the same fixtures while this suite runs.

```bash
npm --prefix terminal/web test
npm --prefix terminal/web run build
# Separate shell1: explicit empty provider configuration,never owner-private settings
python - <<'PYTHON'
import os
for key in ('CODESPACES','CODESPACE_NAME','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN'):
    os.environ.pop(key,None)  # this separate fixture process only
for key in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):
    os.environ[key]='0'
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:8787'
from terminal.server.app import create_app
from terminal.stocks.service import StockWorkspace
import uvicorn
uvicorn.run(create_app(stock_workspace=StockWorkspace(environment={})),host='127.0.0.1',port=8787)
PYTHON
# Separate shell2: authored protocol fixture;never real provider transport
python terminal/tests/live_market_fixture_server.py
# Separate shell3,after both health endpoints are ready
node terminal/tests/advanced-research-validation.mjs
node --experimental-strip-types terminal/tests/measure_research3d.mjs
```

Use the existing validated project virtual environment/PYTHONPATH for native bindings.
The native gateway must be a separate test instance with no provider/private settings;
`assertFixtureServer` rejects non-fixture-safe servers. Do not run this test against the
owner's active acquisition session. Detailed local test environment used
`/workspace/gig-terminal-clean-venv/bin/python`,with each
`build/python-{debug,release,asan-ubsan}/python` binding path. The project sanitizer
wrapper was used with live-interpreter leak checking;see the prior setup reports.

Existing Codespace update,after stopping its old server with Ctrl+C:

```bash
git switch feat/atlas-final-release
git pull --ff-only origin feat/atlas-final-release
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

No new npm dependency or native rebuild is required. Keep8787 private and use its
existing authenticated forwarded HTTPS URL. Existing keys/SEC settings are preserved;
this update does not enable any unresolved provider or retention gate.

## Remaining boundaries

- New depth/order-event views have no new live L2/L3 source or full observed event
  integration. Native snapshot coalescing cannot establish event identities or queues.
- VWAP/VPIN currently use authored explicit executions;real unsigned IEX prints do not
  establish native resting-order executions or aggressor direction. No fabricated
  current-session VWAP or toxicity claim.
- Dome/ribbon accept genuine eligible Level 1 observations through the existing
  infrastructure,with exact-origin checks. This session qualified authored transport,
  not actual Alpaca account access,entitlements,history,asset count,or live delivery.
- Exact-candidate ARM64/hosted,physical-device/GPU,long-run resource behavior and owner
  private-Codespaces acceptance remain unexecuted. Older qualified commits do not
  automatically qualify the new tree. No workflow was dispatched.
- Existing large optional Three chunk and backend Starlette/httpx deprecation warning
  remain visible. No paid services,trading,observed retention,restricted LOBSTER access,
  main change,provider permission fabrication,or security-boundary relaxation occurred.

These are implemented research visualizations with scoped evidence,not eight new
market-data feeds. Essential work authorized in this visualization assignment is
complete;further source/device qualification is separate from synthetic correctness.
