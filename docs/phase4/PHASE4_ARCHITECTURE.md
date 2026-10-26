# Phase 4 architecture and scope

October26,2026 America/New_York. Exact baseline696c4c940a311d39a50114606724dfdb5326096d;
dedicated branch feat/atlas-phase4-platform. Main and both prior ATLAS branches preserved.

Implemented integrated milestones:

* Existing SEC normalization → selected facts aligned by exact actual period → new
  cache-only v2 statement packets → explicitly labelled comparison UI.
* Existing validated historical cache → canonical core revalidation → opt-in private
  immutable SQLite revisions → restart/read/list/delete APIs → private archive UI.
* Accepted cached bars → descriptive risk API → Stock Intelligence diagnostics.
* Explicit authored returns → bounded HMM/GARCH diagnostic fits/fixed Kalman filter →
  likelihood/convergence/assumption UI. No stock observations inferred from this input.
* Full-width shared shell → compact accessible navigation → larger charts/type →
  retained replay,simulation,source disclosures and optional3D.

No native implementation changes,provider activation,new dependency,broker capability,
external-data acquisition or licensing acceptance. Request-proof allowlist adds only
three explicit mutation endpoints;Origin/CORS/Host/one-use/endpoint binding rules stay.
Heavy diagnostic fits and SQLite calls run in worker threads,not the native-owner thread.
One active HTTP model fit is admitted;busy callers receive429. Native data stays owned
by the existing engine/event-loop architecture. Worker cancellation/OS scheduling and
long-duration operational load still require separate qualification.

New APIs:

|Method/path|Scope|
|---|---|
|GET /api/v2/companies/{symbol}/statements?statement=income\|balance\|cash&period=annual\|quarter\|ytd\|all|Latest selected cached facts grouped by actual period,max12 packets|
|GET /api/v2/companies/{symbol}/risk|Cache-only descriptive risk;no acquisition|
|GET /api/v1/stocks/history-store[?revision=SHA256]|Owner-private revision list or verified v2 snapshot|
|POST /api/v1/stocks/history-store|Proof-protected save current accepted symbol cache or explicit revision deletion|
|POST /api/v1/stocks/models|20..256 authored decimal returns;bounded diagnostic fits|
|POST /api/v1/stocks/scenarios|Explicit authored quantity,price,1..16 shocks;linear scenario only|

All new POSTs retain existing4096-byte body and30-mutation/s session bounds. No arbitrary
source URL,file path,credentials,SQL,model parameters or optimizer iteration budget can
be supplied by browser callers. Existing v1/v2 consumers remain available unchanged.
