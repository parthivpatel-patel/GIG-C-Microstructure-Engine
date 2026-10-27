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


## Continued engineering closure (recovered baseline6f7e33c)

The prior sections are historical evidence for the earlier checkpoint. Current
implementation checkpoint:a8f9d7e791cd9c5aed952ac1dc8e5c608134f975,remotely verified
on feat/atlas-final-release. The recovered uncommitted implementation was preserved
and completed;no reset/restart,native source change,provider activation or data download.
See CONTINUATION_CONTRACTS.md for exact interfaces,private configuration and bounds.

Implemented:opt-in versioned retained-history projection with strict browser
resynchronization;bounded private catalog import and shared discovery/company routing;
exact acceptance-time retained-SEC filtering and optional Financials UI;permission-gated
normalized observation ledger;quiet/paused3D upload avoidance. AAPL,APLD and CRWV pass
search/company/v2 API checks and actual browser global selection. AAPL retains its CIK;
APLD/CRWV have explicitly null,unverified CIKs. Discovery never grants a feed entitlement.
No current full exchange directory or real financial observations were acquired.

### Final executed validation

| Cohort | Pass | Fail | Skip |
|---|---:|---:|---:|
| Terminal with Debug native binding |274|0|0|
| Terminal with Release native binding |274|0|0|
| Terminal with ASan/UBSan native binding |274|0|0|
| Stock/SEC/live/persistence Debug |134|0|0|
| Stock/SEC/live/persistence Release |134|0|0|
| Stock/SEC/live/persistence ASan/UBSan |134|0|0|
| Origin/proof/security |46|0|0|
| Verified HTTPS/WSS proxy boundary |8|0|0|
| Frontend unit |24|0|0|
| Seven stable-asset browser suites |91|0|0|
| Multi-stock authored browser |21|0|0|
| AAPL/APLD/CRWV gated browser selection |3|0|0|
| Native eight frozen canonical reference tests |8|0|0|
| Installed0.1.1 wheel interfaces/export contracts |14|0|0|
| Packaging pattern regressions |3|0|0|
| **Selected final outcomes** |**1442**|**0**|**0**|

Two live LSan checks returned0. The new20 Python component tests include1000
independent projection windows,10000-entry catalog search,acceptance nanosecond
boundaries,transaction rollback,an actual precommit child-process exit,corruption,
tail deletion,expiry and10050-record retention pressure. An additional40 actual
production-source snapshots were restored exactly by the TypeScript reader and
compared with full Python views,including freshness/expiry and generation change.
These are separate comparisons,not inflated CTest totals. Production TypeScript/Vite
build passed. Stable-asset driver completed before the final21-check live browser
run. All8 canonical hashes equal the prior frozen values. Existing binaries were
reused;no fresh six-compiler build or ARM64/hosted qualification is claimed.

### Measurements and defects

Four-symbol,256-row authored projection fixture:39 post-initial snapshots including
a forced full generation resync total13,400,005 full-view bytes versus1,167,822
projection bytes,91.2849% reduction. This is encoded fixture size,not measured network
traffic or provider latency;full latest observations/metrics remain. Reproduce with
terminal/tests/check_market_projection.py. Initial app JS232.10kB/gzip72.66kB;
Three remains deferred and its existing large-chunk warning remains visible.

A single local SQLite run appended1000 authored events in0.034675s and reopened/
verified them in0.058467s;database2,121,728bytes,peak processRSS49,152KiB including
interpreter/native import/fixture/reference construction. This is not isolated
allocation cost,crash-safe live recovery or production throughput. Reproduce with
terminal/tests/measure_observation_store.py. Browser software-renderer snapshot:
1732nodes,8,916,444bytes used JS heap;four charts each2geometries/2draw calls.
No hardware GPU/FPS or physical Android qualification is inferred.

Review reproduced an expired later ledger record surviving physical prune after a
backward storage-clock adjustment. Original test failed2 retained versus expected0.
Pruning now removes through the last expired record as a contiguous prefix,with a
regression in all three stock configurations. Earlier unexpired records may be
evicted to preserve a verified suffix. Immutable original expiry prevents policy
extension after restart. Offline hosts cannot guarantee timed physical deletion.

An initial archive inspection ran before the archive writer finished and reported
an empty file. Sequential completed-build inspection passed;this was validation
scheduling,not a packaging-source defect. The failed log is retained and hashed.
No tests,warnings,assertions or security policies were disabled to obtain a pass.

### Remaining boundaries and exact next work

Complete observed provider qualification,official current symbol/CIK reconciliation,
current calendar/halts authority,storage permission/host backup policy,complete XBRL
PIT history,corrected tape reconciliation,physical device/GPU/accessibility audit
and exact-candidate owner-authorized ARM64/hosted evidence remain open. Market-only
APLD/CRWV resolution is complete;their SEC financial loading remains blocked by
unverified issuer mapping. No data entitlement is implied by a selectable symbol.

For existing Codespaces:stop this application's old foreground server withCtrl+C;
run git switch feat/atlas-final-release,git pull --ff-only origin feat/atlas-final-release,
then bash scripts/setup_terminal.sh and bash scripts/start_terminal.sh. Preserve
private configuration and keep port8787 Private;use its authenticated forwarded URL.
No extra gate or permission variable is required for discovery or projection.

Sequential closure source-archive inspection passed753 intended,byte-identical members,
with complete required source trees and no private output paths. Its checksum and
pre-receipt evidence snapshot are recorded in EVIDENCE.json;the final archive receipt
necessarily postdates the archive itself. This does not claim a newly rebuilt native
wheel. Existing installed-wheel14 checks and packaging3 regressions passed.

## SEC identity/history and qualification continuation — 2026-10-27

Recovered exact clean baseline8cd87af51585023af875679affe136a91d816a81.
Pushed services4ec38a210b77a7ba347ba0530bd7b5034f937bb8;
manual ARM64 preparationd4d5f150ee50933529e5414c56fb8947de554701;
filing-page receipt correctiona640826a72bfeb3974cf8ea428a8d0149604476d;
PIT ambiguity/UI7d2eb21 checkpoint (full SHA in EVIDENCE.json).
Main and all native source contracts/canonical identities are preserved.

The actual implementation now supports bounded official SEC ticker-directory
resolution,explicit advertised older-submissions loading with1024 cached filings,
shared exact acceptance parsing,amendment cutoffs,ambiguity-safe date-only vintages,
extended cached filing navigation and history/identity actions in Stock Intelligence.
Directory conflicts and changed/removed cached issuer identities fail atomically.
Unknown CIKs remain null. In this environment SEC configuration is disabled and the
identifying User-Agent is absent;no SEC requests occurred. Fixtures deliberately
use authored CIK42/43,not asserted APLD/CRWV mappings. The resolver is engineered;
actual authoritative reconciliation remains BLOCKED. See SEC_HISTORY_AND_IDENTITY.md.

Confirmed failing-before defects:normalization accepted a timestamp grammar the PIT
filter rejected;date-only vintage chose among same-day facts using accession order.
The shared exact parser and explicit ambiguous-day exclusion repair these. The latter
intentionally makes ambiguous results unavailable rather than changing expected values
to fit an invented chronology. Native canonical outputs remain unchanged.
Integration guards preserve financial receipt/hash when only filing metadata refreshes,
reject contradictory shard overlap and prevent late responses from replacing another
selected company. New endpoint proof targets are explicitly allowlisted;all existing
Origin/Host/private-Codespaces controls remain. No forwarded-header trust was added.

Final selected outcomes:1535 passed,0 failed,0 skipped (1493 broad selected outcomes plus42 focused post-receipt-correction outcomes):

- Terminal consumer274 in each Debug/Release/ASan+UBSan configuration:822.
- Stock/SEC/live/persistence149 in each of those configurations:447.
- Security/proof/ARM64 static policy48;verified TLS/WSS8.
- Frontend25;seven stable-asset browser suites91.
- Authored multi-stock browser21;gated AAPL/APLD/CRWV discovery3;new SEC/late-response/retention browser3.
- Frozen native reference tests8;installed-wheel interfaces/export contracts14;packaging3.
- Final filing-page receipt correction14 focused tests per Debug/Release/sanitizer:42. The full cohorts precede this final metadata-only change;the affected SEC/API cohort was then repeated in all three configurations.

Three LSan checks returned0. All8 actual canonical hashes equal the frozen values.
An additional40 cross-language projected/full snapshot comparisons passed,not counted
as extra CTest outcomes. C++ code/binaries were not rebuilt;prior full six-native
configuration evidence is retained,not represented as a new build. No new ARM64 or
hosted success is claimed. The new branch-specific workflow is only prepared,manual,
free-usage-owner-gated and independently policy checked. Existing workflow is unchanged.
No workflow,paid resource,feed,observed retention or trading connection was activated.

One initial browser assertion checked enablement before the existing source-load lock
finished. The test now waits for actual readiness before checking the new action;
original failure is preserved. Earlier authored tests also needed an advancing fixture
clock to exercise multiple rate-limited requests and to preserve the fixture's existing
options entitlements. These fixture errors were repaired without weakening production
rate limits,permission controls,assertions or test coverage. Final cohorts have no skips.

Measured localx86_64 fixture:50000 issuer rows parsed in0.161870s;100 bounded searches
took0.573283s (5.73283ms mean);peak processRSS57644KiB includes interpreter,fixture,
normalized rows and search. This is not SEC/provider throughput. Initial JS232.14kB,
gzip72.67kB versus previous232.10/72.66;Three remains deferred,its warning unsuppressed.
The unchanged projection fixture again reconstructs40 exact views and reduces encoded
bytes91.2849%;not a wire-traffic measurement. Software-renderer screenshots/counters are
recorded separately;no physical GPU/FPS/Android/accessibility certification is implied.

Remaining implementation:complete XBRL context/presentation and authenticated historical
fact vintages,corrected trade-tape reconciliation,authoritative current session/halts,
and hardware/context-loss/accessibility qualification. Remaining external acceptance:
SEC identifying configuration and official identity reconciliation;actual entitled
market observations/retention rights;owner-authorized exact-SHA ARM64 and hosted evidence.
No intermediate owner testing was requested. The next engineering milestone is a
bounded authenticated fact-vintage archive with independent source reconciliation;
current selected-fact/metadata services must not be called a complete PIT database.

The final readonly filing page now reports its separate filing receipt rather than
the preserved older financial receipt. Debug/Release/sanitized focused SEC tests14
each passed afterward. One initial targeted sanitizer invocation used an unsupported
-m option;the corrected script-runner invocation passed with LSan0. The invocation
error is retained as procedural evidence,not a sanitizer finding.

Final sequential source archive inspection passed761 safe,intended,byte-identical
members with complete required source trees. Archive checksum and pre-receipt evidence
snapshot are recorded in EVIDENCE.json;the final receipt necessarily postdates archive
creation. No restricted data,private database,credential or build binary was committed.
