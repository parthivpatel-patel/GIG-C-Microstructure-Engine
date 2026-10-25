# Interactive liquidity landscape

Implemented React/Three.js instanced bars encode exact source price coordinate,
discrete observation time/replay clock and displayed quantity. Bid/ask colors match
the ladder and2D cumulative-depth view. BigInt differences/ratios precede bounded
float conversion for geometry; tooltips preserve original exact prices/quantities.
No interpolated orders, queue IDs, executions or missing snapshots are generated.

Orbit rotation,zoom,right-drag pan,hover,camera reset,8/24/48 observation windows
and5/10/20 levels per side are implemented. The last96 browser snapshots are bounded;
max48*20*2=1920 visual bars. Rendering is on observation/camera/resize changes,not
an unbounded animation loop. Device pixel ratio<=1.5; ResizeObserver,hidden-page
render guard and complete geometry/material/controls/renderer disposal are used.
WebGL construction failure produces the same-source2D fallback; explicit fallback
and reduced-motion styling are available. The2D x-axis is occupied-level rank,
not falsely labeled equal price distance. The3D x-axis uses actual price distance.

Browser source/mode/provider change or backward seek clears old history. Render
coalescing can omit intermediate source events at higher replay speeds; discrete
sample bars/tape never pretend to be an exhaustive event log. No source continuity
is inferred from smooth rendering. Live gaps are not empirically tested because
live access is blocked; actual future gaps must produce invalid/stale feed status.

Actual Chromium/SwiftShader tests cover native geometry,camera pixel changes,
window/range controls,fallback,mode isolation and412px mobile layout. Screenshots
are actual local application artifacts in ignored build/terminal/browser. They
are not generated mockups. Physical Android/GPU and external mobile forwarding
remain unverified. No browser frame-rate guarantee or public URL is claimed.
