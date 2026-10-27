# GIG ATLAS final development completion checkpoint

Baseline: `9a5ad1b013ab30d2697a9e55686a53f256acad2d`.
Branch: `feat/atlas-final-release`. Date: October 26, 2026 (America/New_York).
Backend checkpoint: `5919729e7ab906bd83bd0560f7fd6560b60459b5`.
UI checkpoint: `27433e147f6e91efcff685f446a531f4843585ae`.
Final handover/response-contract repair: `ca5cd02a869c21888850adc63e53d69fa30fa6e6`.
Exact subsequent evidence commits are recorded in the delivery manifest
and final delivery response. Main, prior commits, SEC configuration and native code are preserved.

## Assessment

The primary remaining transport/product backlog is implemented: endpoint-proof-authorized
browser push, acknowledged in-place shared-provider subscription handover, independent
multi-stock 3D controls, searchable configured symbols, persistent research watchlists,
per-symbol health, explicit session evidence, and an equity Operations snapshot.
This is a fixture-qualified private research candidate, not an entirely live-qualified
or production trading platform. Current provider listings/calendar authority, account
permissions, observed-market acceptance, physical devices and exact-candidate ARM64
remain unresolved. Complete accounting statements and observed forecasting validation
are not established by the existing selected-fact/model-demo interfaces.

## Transport and subscription architecture

`POST /api/v1/stocks/events` returns incremental SSE state frames. It uses the same
one-use, 30-second, endpoint-bound request proof and strict Origin/Host boundary as
existing native mutations. It does not put credentials or capabilities in URLs, DOM,
local storage or logs. Codespaces-rewritten HTTP Origin/Host is accepted only through
the existing proof policy; arbitrary forwarded headers confer no authority. CORS and
private forwarded-port authentication remain unchanged. No localhost Origin was added.
The native `/api/v1/stream` WebSocket remains independent.

Eight browser streams maximum; no per-client FIFO; snapshots coalesce at most four times
per second with a one-second heartbeat. Source ingestion continues independently. The
serialized SSE wire-frame limit, including its envelope, is 1 MiB; each ASGI send has a two-second deadline. Cancellation,
disconnect, oversized snapshots and slow sends release slots. Counters distinguish sent
snapshots/coalesced checks from unknown exchange-message loss. They do not pretend to
measure proxy delivery or complete tick history. Browser decoding is incremental, strict
UTF-8, bounded to a 1 MiB frame/carry buffer, four-MiB read chunks and64 frames per batch, with independently tested fragmented UTF-8/frame decoding, a ten-second opening deadline and fifteen-second heartbeat
deadline, abort cleanup, bounded reconnect attempts and an explicit reconnect control.

Subscription changes on an authenticated socket send unsubscribe for the old channel
sets, validate the empty acknowledgement, then subscribe and validate the requested sets.
There is no second upstream connection during this handover and no transient eight-stock
subscription. Identical requests are no-ops; concurrent changes are rejected. The source
capture generation advances only after the new acknowledgement; pending/new/old state
is not silently merged. A handover gap exists and is disclosed. This is in-place
unsubscribe/subscribe, not minimal per-symbol delta optimization or an atomic exchange
capture transaction. Changes during authentication/backoff may replace the connection.
Reconnect restores the desired set; stale/wrong acknowledgements fail explicitly.
Auth/subscription sends are bounded to three seconds and acknowledgement wait to fifteen.

A discovered liveness defect was repaired: absence of quote/trade messages is not proof
of transport failure or market closure. Quiet authenticated streams now report IDLE;
WebSocket ping/pong continues monitoring the connection, old observations become STALE,
and no false market-open/closed inference is made. Actual socket failures retain the
bounded reconnect policy. Lifetime socket-open counts are labelled as lifetime counts,
not concurrent sockets. Existing 256-event/identity retention, exact metrics, source hashes,
correction observations, numeric limits and permission gates are preserved.

## Product, visualizations and operations

Stock Intelligence's Live Market tab uses browser push instead of one-second polling.
Search queries the full currently configured curated directory (11 identities), not an
invented current exchange listings universe. Saved research watchlists hold at most 20
identifiers; simultaneous subscription selection remains capped at four or a stricter
configured limit. Saving a symbol never acquires data. Selection and watchlists persist
without storing observations or secrets. Old Overview quick controls remain for compatibility
and explicitly describe replacing the shared selection; they do not create another manager.

Each displayed symbol has its own bounded renderer, camera, palette, orbit/pan/zoom,
reset/presets, local pause, fullscreen and source tooltips. Global pause also remains.
There are at most four contexts, with capped DPR, instanced geometry, two geometries/draw
calls per panel in measured fixtures, and explicit disposal on unmount. Standard lighting
improves point visibility. Camera inertia respects reduced-motion preference at mount;
source prices/events are never interpolated. Axes share the global capture ordinal range;
price normalization is per panel and explicitly disclosed. No depth, queue priority,
NBBO or native orders are fabricated from Level 1. 2D traces/cards remain available if
WebGL cannot initialize. Physical-GPU context-loss recovery and long-duration leak/FPS
qualification remain partial, not established by a successful software-renderer journey.

The new lazy Operations panel reads an explicit equity-health snapshot. It reports source
state, lifetime opens, generation, accepted observations, evictions and per-symbol health
without starting acquisition. Existing native transport/source Operations remain intact.
All nine workspaces, financial APIs/ratios/filings, replay, simulation and theoretical
research interfaces remain available; their existing automated journeys are preserved.

## Session evidence and privacy

`GIG_MARKET_SESSION_FILE` optionally selects a bounded owner-supplied JSON schedule.
The `.gig-session/` directory is ignored. Reads accept regular files only, refuse symlinks
where supported, use nonblocking opens, and cap input at 64 KiB/1,000 sorted nonoverlapping
intervals. Duplicate fields, malformed intervals and unsupported symbols are rejected.
No file path or private content is returned on failure. Valid responses report source
reference/hash and explicit OWNER_CONFIGURED authority; gaps, absent schedules, unknown
symbols or missing timestamps yield UNKNOWN. It is not live exchange/holiday/halt authority.
The existing weekday hint stays explicitly nonauthoritative. Nothing resets native books
at a session boundary. No schedule or historical dataset was acquired during this task.

Existing Alpaca credential aliases, five permission gates plus explicit live enable,
SEC private configuration, fixed provider endpoint/TLS policy, trading exclusions and
private Codespaces boundary are unchanged. No real provider/SEC request, paid dependency,
market download, broker action, workflow dispatch, merge, tag or release occurred.

## Executed qualification

| Cohort | Passed | Failed | Skipped |
|---|---:|---:|---:|
| Native GCC Debug |155|0|0|
| Native GCC Release |155|0|0|
| Native GCC ASan/UBSan |155|0|0|
| Native Clang Debug |155|0|0|
| Native Clang Release |155|0|0|
| Native Clang ASan/UBSan |155|0|0|
| Terminal native-binding Release |274|0|0|
| Terminal native-binding Debug |274|0|0|
| Terminal native-binding ASan/UBSan |274|0|0|
| Stock/SEC/research/completion Release |114|0|0|
| Stock/SEC/research/completion Debug |114|0|0|
| Stock/SEC/research/completion ASan/UBSan |114|0|0|
| Origin/proof/browser boundary regressions |46|0|0|
| Verified local HTTPS/WSS proxy |8|0|0|
| Frontend formatting/financial/plot/push protocol |22|0|0|
| Existing stable-asset browser journeys |91|0|0|
| Expanded stock push/watchlist/independent3D journey |20|0|0|
| Default-gated native application,360px unavailable view |1|0|0|
| Installed wheel interface/export contracts |14|0|0|
| Source packaging regressions |3|0|0|

Total: 2,299 selected final outcomes; these are configuration/cohort outcomes, not 2,299
unique test functions. All eight native hashes match in all six configurations (48
comparisons). Source C++/headers/CMake/bindings were not edited or rebuilt; existing
validated build artifacts were executed. There is no fresh compiler-build or ARM64 claim.
Sanitized Python consumers use the existing live-interpreter LSan methodology; both
checkpoints are zero. Third-party Python codecs are not claimed sanitizer-instrumented.
Strict cohort-count/skip checks and compiler/test requirements were not weakened.

Original failures are preserved under ignored `build/completion`: a slow-send deadline
was translated by Starlette into ClientDisconnect, requiring handling the specific deadline
inside stream_response and preserving cleanup; nested watchlist buttons changed accessible
checkbox names, repaired with separate controls; a reused fixture's lifetime-open count
invalidated an absolute-one assertion, repaired to assert no increase during handover.
An early incomplete test accidentally used an already-configured local Origin and waited
on a legitimate stream; its negative fixture now uses an unauthorized Origin. A final handover regression reproduced old retained quotes labelled current after an empty
unsubscribe acknowledgement. Freshness now requires active symbol membership. Frontend
push/mutation responses are validated before reaching charts, including bounded shapes,
finite numeric fields, receipt/generation consistency and inactive-symbol states. No security
policy was broadened to pass it. Existing Starlette TestClient deprecation and deferred
Three chunk warnings remain visible.

## Resource evidence

`measure_live_market.py` measured 1,000 authored events after 256 warmups with full view
calculation and tracemalloc: 17.5823 seconds, 56.8754 events/second, 848,294 peak traced bytes,
35,916 KiB peak process RSS, and exactly 256 retained events/identities at 1,256 receipts.
This includes instrumentation and is not provider throughput or exchange latency. The
previous checkpoint's comparable single run was 17.1772 seconds/58.2167 events per second;
shared-host single runs do not establish a meaningful regression or production baseline.
No journal storage change was made.

Browser artifacts include CPU submission timings from each renderer, geometry/draw counts,
CDP JS heap/node/layout/script counters and desktop/mobile screenshots. Software-renderer
submission time is not physical GPU frame latency/FPS or end-to-end feed latency. Source
and receive clocks remain unsynchronized. Final exact bundle sizes, screenshots/hashes,
resource values, source inventory and log hashes are in EVIDENCE.json. Initial code remains
about 232 kB; Three remains optional/deferred and still emits the chunk-size warning.
No hardware-GPU, physical Android or full WCAG certification claim is made.

See COMPLETION_MATRIX.md for remaining gaps and DEPLOYMENT.md for reproducible commands.

A separate reproducible `measure_market_ingestion.py` isolates the Python adapter tiers
at source checkpoint ca5cd02: three authored four-symbol trials, 256 warmups, 10,000 quote
frames/800,000 input bytes per trial. Median validation/context-commit throughput was
38,249.0 events/s; individual trials29,364.8–38,320.4. This excludes frame generation,
analytics,serialization,network and browser work and is not C++ matching throughput.
One hundred full analytics/JSON snapshots per trial averaged4.95–9.64ms each,283,181 bytes
per snapshot. At the configured four-Hz maximum this payload size could imply about1.13MB/s
per active browser before transport overhead;that is arithmetic,not measured wire traffic.
Full snapshots favor consistent retained history/freshness and bounded recovery. A future
versioned delta/projection protocol needs independent reconstruction/status equivalence
checks before reducing that mobile bandwidth;it is not silently claimed implemented.

Final boundary regressions also reproduced rejection of two valid coalesced600KB frames
and an envelope/payload budget mismatch. The decoder now bounds carried frames separately
from four-MiB read chunks, and the sender includes the SSE envelope in its one-MiB limit.
Original failing-before tests are preserved;no unsupported input is silently skipped.
