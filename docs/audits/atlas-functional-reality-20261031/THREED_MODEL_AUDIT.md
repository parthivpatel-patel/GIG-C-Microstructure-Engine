# 3D rendering, animation and data-driven reality

Candidate: `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`.
**15 modes inspected and exercised:**13 advertised modes plus2 legacy scenes.
All15 are data/parameter-driven **under authored inputs**. None is independently
qualified against real market observations. Camera motion is not that evidence.

## Source and runtime architecture

- `ResearchLab.tsx:11–24` selects retained native snapshots,retained IEX quotes or
  the explicitly selected authored two-symbol fixture. It filters symbol/time/side,
  computes a Plot and passes it to lazy `ResearchScene.tsx`. It does not silently
  select the authored fixture when a real source is missing.
- `ResearchScene.tsx:10–39`: Three r180 instanced samples,batched line segments,
  triangle meshes;OrbitControls camera and damping RAF only while needed;no
  perpetual market animation or automatic spin. Input changes replace geometry
  and explicitly draw. GPU resources,observers,listeners and RAF are disposed.
- `QuoteCloud.tsx:8–25`: four L1 projections,≤512 instanced points,independent
  pause/camera/palette/scale,exact retained source strings in inspection. Geometry
  identity avoids rebuilding unchanged input;source-state inspection can refresh.
- `ModelSurface.tsx`: parameter-driven GARCH grid;declared parameters,not market
  observations. `Landscape3D.tsx` and `VolatilitySurface.tsx` are additional legacy
  scenes;the latter can show a theoretical flat-volatility plane or discrete
  indicative IV points,never a calibrated observed smile.
- Shared source normalization retains capture order and timestamps. Time axes are
  usually **capture ordinal**,not physical elapsed exchange time. Geometry uses
  bounded approximate display coordinates;raw exact prices/quantities remain in
  labels/tables. Changing an input can change exact values without pixel motion
  when window normalization rescales it;no fake motion is added to compensate.

## Every model and mathematical mapping

All rows have primary SIMULATED in this audit. “L1 capable” means compatible with
valid future authorized quotes,not a currently operating provider session.

| Mode/component and workspace | Quantitative input and encoding | Render / interaction / changing-input evidence | Limitation |
|---|---|---|---|
| Height map;ResearchLab in depth/flow/research |Discrete occupied levels;linear price X,5q/max(q) Y,capture Z;adjacent matched prices only mesh.|Numerical increase/decrease/flat/empty/extreme cases and actual canvas/tooltip/2D checks pass.|Requires supplied depth;no L1 expansion. Surface triangles are display interpolation.|
| V-canyon;same |Mid-relative signed price versus cumulative side quantity,capture Z.|Independent changed quantity values;browser mode,camera and filters pass.|Discrete cumulative walls;not inferred liquidity between snapshots.|
| Event voxels/point cloud;same |Explicit ADD/CANCEL/DELETE/EXECUTE source price,quantity,capture;glyph/color by category.|Changing declared quantities,voxel/point selection,symbol/side/time and native isolation pass.|No events inferred from depth differences. Native retained snapshot source has no order-event history to populate it.|
| VWAP corridor;same |Exact cumulative Σ(price·executed quantity)/Σ(executed quantity);best-quote floor rails.|Independent3/7 weighted price and changing execute-price references pass;canvas/inspection pass.|No executions means VWAP unavailable even if rails exist. Not executable capacity or a forecast band.|
| Flow/VPIN;same |Declared aggressor direction sets signed lane;execution size sets height. Equal20-unit buckets,rolling4 absolute imbalance toy.|Independent splitting/balanced-volume reference,known changing sizes and browser inputs pass.|Unsigned IEX prints/quotes cannot establish direction. Not classical market-wide calibrated toxicity.|
| Depth wheel;same |Angle categorical side/rank,radius1+4q/max(q),capture vertical.|Changed quantity/radius/source values and interactive rendering pass.|Angle is not price distance;requires depth.|
| Dome;same;L1 capable |√Σ8(log mid changes)²,requiring9 valid quotes;normalized height with decorative circular cross-section.|Flat path gives0;doubling/tripling paths match independent √8·log(factor). Missing/stale/retained labels and browser input paths pass.|Not IV,annualized volatility,fitted forecast or measured market curvature. Cross-section explicitly VISUAL_ONLY.|
| Spread ribbon;same;L1 capable |Best bid/ask edges against capture;exact spread value. Mesh joins discrete observations.|Zero/increasing spreads,large exact integers,retained status and actual fixture stream canvas pass.|No NBBO/depth inference. Between-capture path unknown.|
| L1 quote evolution;QuoteCloud in Live Markets/comparison |Actual bid/ask prices,per-symbol normalized vertical range,capture and symbol lanes.|Independent price increase/decrease/constant/extreme cases;4-mode browser selection passes.|Point sizes equal;source sizes inspected,not deeper levels.|
| L1 mid comparison;same |10,000(mid/first retained valid mid−1),shared scale.|Independent doubling series gives(2^11−1)·10,000;flat0 and down/up tests pass.|Per-symbol baselines can have different times;not synchronized investment returns.|
| L1 rolling variation;same |√Σ8 squared log-mid changes,shared scale.|Independent √8·log2,flat0,range/insufficient cases pass.|Event-sampled;not annualized/clock-time risk.|
| L1 trade activity;same |log(1+source print size),capture/symbol lanes;price retained in inspection.|size12→log13 reference and browser mode pass.|Not corrected complete volume,aggressor flow or depth;unreconciled prints are disclosed.|
| GARCH response;ModelSurface in Research |ω+α·shock²+β·priorVariance over441 declared vertices.|All441 vertices,parameter up/down/flat/invalid tests;camera/context-loss/retry browser pass.|A mathematical response grid,not an estimated market volatility surface.|
| Legacy native Landscape;Market Depth |Retained native snapshot price/quantity/capture grid.|With camera unchanged,a native replay step increments actual native position and changes canvas pixels.|Synthetic default book;not genuine AAPL/Nasdaq depth.|
| Legacy VolatilitySurface;Stock Intelligence Options |Strike X,input IV Y,years Z;theoretical constant-IV grid or gated discrete indicative IV points.|Declared volatility .2→.3 changes actual canvas pixels with no camera operation;raw option price independently verified.|Scenario plane is not an observed smile;indicative provider mode remains unqualified.|

## Executed controls and negative cases

New independent Node tests:14/14 (13 advertised mappings plus separate VWAP/VPIN
oracle). Original frontend81/81 include exact decimals,provenance,source mixing,
generation isolation,2^53 narrow spreads,overflow and bounds. Advanced browser23/23
includes all8 models,4 L1 modes,GARCH,camera/key/drag/wheel/fullscreen,real WebGL
context loss/construction failure/retry,2D,table/filter/time/pause,closed-canvas cleanup,
and80 grouped theme/width/model combinations. Two additional legacy input-change
browser checks pass. No forced clicks or source/asset rebuild during tests.

Inputs included identical-repeat,zero variation,increase/decrease,missing/sparse,
stale/disconnected retained status,wrong symbols and numerical extremes. Stale
history may remain displayed as retained history;it must not become current live
data. A model with no market input (GARCH) has no invented market timestamp or
staleness. Six depth/event modes correctly stay empty on L1-only input.

An initial audit-authored dome test mistakenly supplied decimal `337.5` where
the typed QuoteSample contract requires scaled integer strings. It threw before
rendering. Correcting the **temporary fixture**,not production code,to integer
ratios yielded14/14. Original failure log is retained and not called an application
defect. The unrelated committed stock browser assertion failure is also retained.

## Resource measurements and interpretation

Three r180/Chromium154/SwiftShader on x86_64,not physical GPU/Android. Eight actual
renderer samples:3.9–57.8ms for the recorded draw,maximum9 draw calls and7 geometries;
these are single synchronous render observations,not steady FPS or frame-time tails.
No continuous60FPS or smooth live-market claim follows.

Node projection profile:10 warmups/model,100 measured projections/model,240 fixed
authored events. Median/p95 ms:height1.048/1.660;canyon1.045/1.582;events.142/.210;
VWAP.117/.176;flow.129/.261;wheel.490/.685;dome.119/.194;ribbon.126/.206.
Process maxRSS124,340KiB. This measures projection/allocation only,not network orGPU.
Source/render receipts,screenshot hashes and original warnings are in evidence.

**Verdict:** these are functioning analytical visualizations with explicitly modeled
or decorative dimensions,not merely spinning decorations. They do not currently
demonstrate motion driven by genuine ongoing provider observations. Prioritize
lawful IEX qualification and honest missing states over additional visual modes.
