# Multi-stock Level 1 and 3D implementation checkpoint

Baseline: `6af0bdef51007d6058f4f3119ecf5bac21c61ceb`, branch `feat/atlas-final-release`.
Classification: authored synthetic protocol/browser validation, **not observed Alpaca acceptance**.

## Implementation

The existing fixed official IEX socket and all permission checks remain. One manager serves
all selected stocks; there is no connection per card. Ten curated routing choices include
GOOGL, AMD and SPY. This is not a current exchange listings service. The concurrent limit is
four, optionally reduced to one–three using `GIG_ALPACA_LIVE_MAX_SYMBOLS`. Configuration does
not establish entitlement. Reapplying an identical running subscription does nothing;
changing symbols/channels closes the old connection before starting another generation.
This is controlled replacement, **not in-place subscription deltas**.

`/api/v1/stocks/live` keeps its v1 schema and old fields, adding bounded history, metrics,
readiness, receipt/ordering/eviction counters, channels and clock-window disclosures. POST
optionally accepts `channels` (quotes/trades,with optional bars). Bars-only is rejected
because the transport liveness profile requires a quote/trade channel. Existing scoped proof/Origin/Host policy
is unchanged. The local `app.state.stock_live` reference permits fixture injection; no HTTP
endpoint can inject observations or credentials. No provider gate was enabled here.

Accepted q/t/b/c/x observations retain source timestamps, receipt ordering, generation,
source/identity hashes, optional conditions/exchange/tape identifiers and binary64 hex.
Bars carry OHLCV; updated/daily bars and status/LULD are unsupported and fail explicitly.
Corrections/cancels are typed observations, not resting liquidity or automatic tape rewrites.
Trade aggregates are suppressed when corrections/cancels occur in the retained window.
Unknown/malformed frames reject before committing accepted containers/counters. Accepted
old event dictionaries are immutable to the processing path; new containers stage a frame
without deep-copying every historical dictionary. Tests verify bad batches preserve state.
History and dedup each retain at most256 entries. Dedup is not global exactly-once; no
exchange sequence, dropped-message count, full session or complete tape is inferred.
Older same-kind timestamps remain diagnostic and cannot roll back latest price. Equal
timestamps retain capture order. No cross-channel exchange order is invented.

The Stock Intelligence **Live Market** tab adds pinned multi-stock quote cards, discrete
2D bid/ask traces, optional bars subscription, health/freshness, bounded view selection and
pause-display/resume. Pins persist as identifiers only in browser local storage. Acquisition
requires an explicit action and server authorization. Polling uses one request at a time,
one-second sampling, an eight-second request deadline and unmount abort; hidden tabs stop
reads, not ingestion. Network errors label observations unavailable. Paused observations
are labelled retained, not current. The older Overview single-stock widget is preserved.

The optional lazy Level 1 cloud uses one renderer and512 instanced points, per-symbol
normalized price lanes, source tooltips, orbit/pan/zoom, keyboard camera controls, presets,
fullscreen and an alternate teal/amber palette. It renders on updates/interactions, without
fabricating intermediate ticks. Symbol lane scales are explicitly independent; this is
not a liquidity-depth surface. 2D/cards survive WebGL failure. GPU objects, controls,
listeners and observers are disposed on unmount. Browser tests exercise hide/remount.
Native L3 replay stays separate; its two instanced meshes are now reused (960 instances
per side =48 observations ×20 levels), instead of recreated for every update.

## Numeric changes and defects repaired

1. Older timestamps previously overwrote latest prices: retain the event and mark it
   out of order, while leaving latest unchanged. Independent expected values cover it.
2. Newly introduced bar `c` was misread as conditions, and cancel used an uninitialized
   local: message-family-specific condition handling. Preserved initial focused failures.
3. Browser fixture exposed valid binary64 shortest decimals beyond the old12-place bound.
   Accept finite nonnegative binary64 up to1e15 without rounding, positive where required;
   preserve shortest decimal and hex. String/integer validation remains unchanged. Tests
   cover `100.01+.01` and extreme finite prices. This intentionally widens float acceptance.
4. Direct float conversion of extreme rational mid ratios could overflow. Realized
   variation computes differences of logarithms of integer numerators/denominators.
   Exact spread/mid/relative spread/size imbalance/returns/frequencies remain Fractions.

Display uses the existing bounded integer rational formatter, with exact fractions in
metric titles. Log-mid quadratic variation is an approximate unannualized retained-window
statistic, not a forecast. Quote-size imbalance is best-quote only. Sizes retain unverified
provider units; no lot conversion is invented. Source/receive clocks are unsynchronized:
reported age is not exchange/network latency. Weekday session windows are not calendar,
halt, auction or market-open authority.

## Requirement closure matrix

| Requirement | Status | Evidence / boundary |
|---|---|---|
| Preserve engine, SEC and security | COMPLETE | Unchanged native sources; regression cohorts, TLS/proof checks and eight oracle hashes |
| One bounded upstream manager | COMPLETE | Existing transport tests plus no-op/replacement tests;32KiB frame,4-frame queue |
| Ten symbol routing choices | COMPLETE | Curated identity tests;not independently refreshed listings |
| Multi-stock subscriptions/watchlist | PARTIAL | Four concurrent maximum;controlled reconnect,not in-place deltas |
| Quotes/trades/basic minute bars | PARTIAL | Authored q/t/b profile;observed source acceptance blocked;bar optional fields not projected |
| Corrections/cancels | PARTIAL | Preserved observations;no reconciled historical tape |
| Bounded history/order diagnostics | COMPLETE |256 retention/dedup,eviction counters,atomic malformed batch,old timestamps |
| Frontend updates | PARTIAL |1Hz bounded HTTP sampling;not dedicated browser-push or tick-complete transport |
| Reconnect/freshness/health | PARTIAL | Existing bounded retry fixtures + new state tests;no observed reconnect qualification |
| L1 analytics | COMPLETE | Independent Fraction/log references,explicit source/window/missingness |
| Multi-stock 2D and optional 3D | PARTIAL | Shared camera/renderer/normalized lanes;independent per-panel cameras not implemented |
| Native L3 replay | COMPLETE | Separate workspace,existing browser/oracle regressions;no observed L3 claim |
| Licensed live L2/L3 | BLOCKED | No depth entitlement;no L1-to-depth fabrication |
| Smooth interaction | PARTIAL | Interactive event-driven cameras;no interpolated observations or continuous animation |
| GPU cleanup/performance | PARTIAL | Instancing,disposal,remount check;no sustained physical-GPU leak/FPS qualification |
| Responsive/accessibility | PARTIAL | Five viewport widths,semantic labels/cards/2D;not physical Android or full WCAG audit |
| Actual live provider qualification | BLOCKED | No configured secrets/independent entitlement evidence;support381230 pending |
| Current market calendar/halts | NOT IMPLEMENTED | Clock-window hint only |
| Backend queue depth/drop instrumentation | NOT IMPLEMENTED | Explicitly unknown;no exchange sequence to establish completeness |
| Crash recovery / persistent market tape | NOT IMPLEMENTED | Memory-only bounded observation window |
| Real provider end-to-end journey | BLOCKED | Authored browser coverage is separately labelled |

No FAILED VALIDATION remains in the final executed cohort. This is not100% completion or
production trading readiness. Earlier failures remain recorded in the evidence inventory.

## Performance interpretation

`terminal/tests/measure_live_market.py` warms256 events,then measures1000 authored single-
symbol events with full metrics/view after each event and tracemalloc enabled. Before
container-only staging:42.6583s,23.4421 events/s,1,218,812 peak traced bytes,36,024KiB process
peak RSS. After:17.1772s,58.2167 events/s,848,944 peak traced bytes,35,952KiB RSS. Both end
with256 retained events/identities and1256 receipts. Single repetitions on shared x86_64
CPython3.12.14;instrumented workload,not socket throughput,latency or a stable baseline.
The remaining full-window Fraction calculations/copies need profiling before any scale
claim. Native journal behavior was not changed.

Final entry JS is230.88kB (72.37kB gzip);the first in-task build was230.73kB. Optional Three/OrbitControls chunk508.73kB still
triggers the existing500kB build warning;it is deferred,not eliminated. Stock workspace
and new cloud sizes are recorded in the final build log. Native C++ was not rebuilt
because no native sources/contracts/build flags changed. Reused native builds/wheel are
identified explicitly in the evidence;new HEAD has no fresh hosted/ARM64 qualification.

## Protocol evidence

Previously retrieved official `alpacahq/alpaca-py` source pinned to
`3da132c6407792310bfbaca1b3114863c44d5bda` supports the transport/channel and field profile:
[websocket.py](https://github.com/alpacahq/alpaca-py/blob/3da132c6407792310bfbaca1b3114863c44d5bda/alpaca/data/live/websocket.py),
[stock.py](https://github.com/alpacahq/alpaca-py/blob/3da132c6407792310bfbaca1b3114863c44d5bda/alpaca/data/live/stock.py),
[mappings.py](https://github.com/alpacahq/alpaca-py/blob/3da132c6407792310bfbaca1b3114863c44d5bda/alpaca/data/mappings.py).
Local file hashes are preserved in the evidence manifest. SDK source evidence does not
independently establish current account entitlements,complete protocol coverage or licensing.
No new official-source or market-data request was made during this resumed checkpoint.

Final chart review also corrected shared-axis and generation boundaries:the four stock
lanes use one global capture ordinal range (not independently stretched symbol windows),
and current plots exclude retained observations from previous connection generations.
Those rows remain available diagnostically at the API with UNAVAILABLE status. Independent
coordinate/window tests cover these cases. A flat2D price range labels the actual observed
minimum/maximum rather than inventing a one-unit price range.
