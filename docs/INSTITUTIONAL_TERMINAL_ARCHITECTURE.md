# Institutional terminal architecture and execution checkpoint

Starting source:3dacd44f6d7bd0ca8325c662fb249cf40d9a2127, feature branch
feat/bootstrap-cpp20-engine. Remote main12f3a53943dc245e36f2cbbc35b9910fb21c0718
is protected and unchanged. Owner reports ARM64 qualification6 success on entry
source (8m03s); this is owner evidence pending independently archived run details,
not qualification of subsequent source.

## Decisions

The existing deterministic C++20 engine remains authoritative. Optional web
application lives under terminal/: React/TypeScript/Vite/Three.js client, a thin
Python ASGI gateway and provider adapters. Existing native Python Replay,
Simulation and execution/TCA APIs are reused, with bounded native aggregate L2
state added separately. L2 data is never converted into fabricated L3 orders.
Native state has one mutating event-loop owner; no unsynchronized worker accesses.
Every transport view is an owned snapshot, financial identity values are exact
strings and rational metrics retain numerator/denominator.

The first vertical slice is authored deterministic replay -> native L3 snapshot /
analytics -> versioned HTTP/WebSocket -> synchronized browser ladder/depth/3D.
Synthetic mode is always explicit. Live mode starts unavailable and must pass
provider access, permission and snapshot continuity gates. A mode switch clears
old presentation history so observations do not leak between modes. A limited
latest-state mailbox is acceptable for rendering; it must not silently drop source
updates before native state. Rendering state coalescing differs from feed loss.

Localhost is the default binding. No unrestricted upload, filesystem browsing,
external URL fetch, order-submission or shell execution API. Mutation requests and
WebSockets require same-origin/explicit local origin validation. Private forwarded
access requires the platform's supported authenticated forwarding mechanism; no
working external URL is assumed. The web frontend is a native backend consumer,
not a modification of GIG Quant Terminal.

LOBSTER private inputs remain untouched. Historical catalogs advertise permission
and initialization restrictions. Existing synthetic ITCH/LOBSTER tooling is reused
where interfaces support it; an available parser executable is not automatically
an interactive replay integration. Recording is off pending provider rights;
authored recorder fixtures may validate the mechanism without observed recording.

## Execution order and acceptance gates

1. Baseline inspection/shared contracts; unchanged core baseline evidence retained.
2. Browser/native replay vertical slice with actual REST/WS/browser checks.
3. Provider profile and independent authored fixtures; official access/terms ledger.
4. Separate native aggregate depth and failure-atomic checks, binding integration.
5. Premium synchronized UI/interactive 3D and mobile/fallback browser evidence.
6. Historical catalog/replay, permission-aware synthetic recording and native
   execution/TCA workflows; record actual supported interfaces and gaps.
7. Source freeze, full applicable compiler/sanitizer/Python/package regression,
   independent browser/security/performance checks, exact evidence and final report.

Independent workstreams own disjoint files. Root reviews shared integration,
commits validated checkpoints and verifies live remote SHAs. Commits use [skip ci]
to avoid dispatching automatic workflows. Manual ARM qualification remains owner-
gated. No unsupported completion, live connectivity or observed accuracy claims.

Targets in America/New_York:Oct27 vertical slice;Oct31 functional terminal;
Nov4 synchronized3D;Nov7 authorized live where feasible;Nov10 historical/simulation;
Nov12 engineering;Nov13–14 verification;Nov14 delivery. These are planning dates,
not claims of unattended future execution. Network/rights/browser support can be
external blockers; independent offline engineering continues.
