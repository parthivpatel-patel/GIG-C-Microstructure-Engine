# Institutional hardening Sprint 2 closure

Date: 2026-11-03. Branch: `development/gig-ui-redesign`. Baseline: `90ebb956df5143670702bcc512de81821cdfa23d`.

Completed checkpoints:

- `c9c75c486cf6ef44b1556bf3858eaaff53578aa0`: bounded recovery admission, independent corrupt-ledger fixtures, actual-clock four-symbol workload and manual ARM64 cohort inclusion.
- `b91de9e0189a6a4ebbcb1c1cbcc583945495e297`: recorded-replay browser response-capture repair and durable progress. Application/native/runtime sources are identical to the measured first checkpoint.
- The subsequent documentation-only closure commit binds this report, runbook and EVIDENCE.json. Its exact SHA is reported by Git/delivery, avoiding a self-referential commit hash.

## Resolved findings

Sprint 1 R06 is closed within the opt-in ObservationStore. SQL preflights reject count/aggregate/individual payload budgets, row metadata types/lengths and oversized/ambiguous metadata before full payload delivery to Python. An explicit read snapshot covers all admission/chain checks. Strict bounded JSON/policy/origin/receipt validation rejects malformed history rather than returning it as accepted observations. Existing damaged stores are not silently repaired during initialization. Details and failing-before evidence: RECOVERY_ADMISSION.md.

A final browser program reproduced a CDP response-cache failure after a successful backend save. The browser test now forwards the original paused request exactly once and captures its real response before fulfilling it; ten forwards/no retries are asserted. All nine original numerical, recording, replay and OFI assertions pass unchanged. No API, native mathematical expectation or production browser behavior was altered for this test repair. The original failure and server200 evidence remain hash-bound.

## Executed validation

| Cohort | Debug | Release | ASan/UBSan |
|---|---:|---:|---:|
| New recovery/workload | 33 | 33 | 33 |
| Sprint 1 production hardening | 29 | 29 | 29 |
| Final qualification | 35 | 35 | 35 |
| Sprint 4 adapters | 96 | 96 | 96 |
| Sprint 3 paper-only fixtures | 52 | 52 | 52 |
| Earlier remediation Sprint 2 | 30 | 30 | 30 |
| Stock/provider/SEC | 207 | 207 | 207 |
| Terminal/native/security integration | 274 | 274 | 274 |
| **Outcome count per configuration** | **756** | **756** | **756** |

All 24 cohort processes passed: **2,268 outcomes, zero failures/errors/skips**. Counts are cohort executions, not a claim of 2,268 distinct nonoverlapping assertions. Unchanged completed cohorts were retained; the new cohort and stock/provider suite were refreshed after final recovery changes. Actual commands, time, log digests and build paths are in EVIDENCE.json.

Sanitizer scope: Python drives the existing GCC ASan/UBSan native extension, using the established preload/`PYTHONMALLOC=malloc` runner and a successful `LIVE_LSAN_CHECK=0` checkpoint in each cohort. Existing `leak_check_at_exit=0` is recorded; no new shutdown leak-sanitizer certification is claimed. Starlette TestClient deprecation/asyncio diagnostic warnings remain visible. No assertions or warnings were suppressed to obtain a pass.

Additional executed checks:

- Native Release: 11/11 CTest cases, zero failures/skips, eight frozen reference identities unchanged and three Python binding contracts. Native/build inputs unchanged; existing binaries were exercised, not freshly compiled. Sprint 1's full native Debug/Release/sanitizer evidence remains prior evidence and is not counted again as a new build. No new Clang or ARM64 run is claimed.
- Installed existing Release wheel consumer: 8 interface + 6 export checks; authored Python research example completed. No unnecessary native wheel rebuild.
- Frontend: 118/118 unit checks; TypeScript/Vite production build passed; all 22 built asset hashes unchanged. Existing deferred chunk warning retained.
- Real Chromium: redesign10 + native/browser21 + recorded replay9 = **40 final checks**. The original recorded program failed once before instrumentation repair; the repaired whole program passes. Clean-candidate browser handshake/source-health receipt also matches. All 12 workspaces passed both themes at 1440/390 px within the redesign program; this is software-rendered viewport evidence, not owner/physical-device acceptance.
- Verified local TLS forwarding: 6 ordinary + 6 rewritten-WebSocket + 8 rewritten-HTTP checks = **20**, zero failures. Strict Origin/Host/proof/private-origin policies preserved.
- Legacy: **4 baseline-writer compatibility cases** passed independently.
- Packaging: **3/3** sdist pattern checks; candidate source archive inventory passes **1,142** safe intended byte-identical members; no private output admitted.
- Runtime: all direct pins match, 19 distributions inventoried; `pip check` passes with its existing cache warning. No advisory clearance inferred.
- Disposable exact-SHA upgrade/rollback: **5** checks passed. No owner/protected branch was changed.

## Workload and resources

The clean 900-batch run accepted/recovered **6,600 authored observations** in **92.874206 s**; **388** duplicates identified; **344** accepted events marked out of order; one automatic reconnect, two explicit restarts and one injected commit failure. Eight clients/ninth refusal, slow-client timeout, cancellation/reconnect, source accounting and restart assertions passed. History/seen sets remain at most256; final clients/in-flight sends/backlog are zero. Actual SQLite_FULL rollback is independently tested.

Measured parent CPU **68.011113 s**; peak RSS **164,192 KiB** including full recovery/independent harness; SQLite **13,889,536 bytes**; peak encoded in-flight bodies **1,059,586 bytes**. Full method/recipe/semantic hashes and memory checkpoints: SUSTAINED_WORKLOAD.md. This is a bounded approximately90-second profile, not full-session leak freedom, maximum throughput, independent exchange completeness, hardware durability or a production SLA.

## Remaining readiness matrix

| ID / priority | Item | Classification | Exact next evidence |
|---|---|---|---|
| R06 / P2 | Bounded damaged observation admission | VERIFIED within tested private v1 contract | Regression runner and baseline-writer compatibility hashes |
| S2-01 / P2 | Single snapshot, metadata/payload and restart validation | VERIFIED | Corrupt/snapshot/SQLITE_FULL cases; target filesystem still separate |
| S2-02 / P1 assurance | Four-symbol/250ms/bounded clients/reconnect | VERIFIED bounded offline envelope | Longer target run only if actual required usage demands it; do not extrapolate full session |
| S2-03 / P1 assurance | Dependency and artifact security | PARTIALLY VERIFIED | Target OS/transitive advisory clearance and installed artifact review |
| S2-04 / P1 assurance | Owner private Codespaces deployment | ENVIRONMENT-BLOCKED | Exact final SHA/assets/runtime; authenticated Private8787 HTTPS/WSS/browser evidence |
| S2-05 / P1 assurance | Native ARM64 current candidate | ENVIRONMENT-BLOCKED | Separately owner-authorized free-eligible six-job run, exact SHA/eight hashes |
| S2-06 / P1 assurance | Actual IEX/history | ENVIRONMENT-BLOCKED | Separately approved private owner-account read-only qualification; none attempted here |
| S2-07 / P2 assurance | Filesystem/power-loss durability | TARGET-PENDING | Actual provisioned private storage fault/recovery evidence; no invented RPO/RTO |
| S2-08 / optional | Full-session soak / 3,000-batch resource envelope | NOT EXECUTED | Approved target resources/window; 900-batch result cannot qualify larger duration |
| S2-09 / outside this sprint | Observed full L3 correctness | NOT ESTABLISHED | Independent complete order-level initialization/reference evidence; IEX L1 is insufficient |

No confirmed unresolved P0/P1 **code defect** was established by this bounded work. This is not proof of absence or a conversion of assurance gaps into PASS. No further architectural rewrite, feature expansion, native journal optimization or permission activation is justified by these results. Recovery still returns retained historical observations, not live/hot book state. SQL/materialized-row budgets do not guarantee a hard memory/CPU/I/O bound for arbitrary malicious schemas, the SQLite pager or a stalled filesystem. Whole-file loss lacks an external continuity witness; an empty file can only be treated as new.

## Remaining work and owner actions

Independently actionable scoped implementation is complete; the exact target acceptance procedure is DEPLOYMENT_ACCEPTANCE.md. Advisory/OS review, current ARM64 execution, owner-private authentication/browser and actual permitted provider evidence remain open. Relative effort: roughly1–2 active hours for a clean target upgrade/receipt/private-browser review, and2–4 hours for target dependency/advisory/artifact review if suitable evidence/tools are available; newly found defects add unestimated remediation. ARM/market windows and CI/environment waiting are excluded. These are task estimates, not a readiness date or institutional guarantee.

This sprint made no provider requests, accessed no credentials/accounts/restricted datasets, activated no real or paper execution, dispatched no workflow, exposed no port, and added no dependency/service/cost. Protected branch refs were checked independently before/after delivery. Only source, authored tests, manual-workflow coverage and privacy-safe documentation/evidence are committed.

**Assessment:** scoped recovery/streaming qualification is offline verified. Owner/private operational acceptance, live-provider qualification, current native ARM64 and institutional production readiness remain **NOT ESTABLISHED**.
