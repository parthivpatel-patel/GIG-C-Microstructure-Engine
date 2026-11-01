# Sprint 3 implementation checkpoint

Application source: `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`.
Isolated branch: `feat/atlas-sprint-3-functional-completion`.
Audit source: `69c9f48e061c96e7151f80ffba53a2d3813d08a8` (read without merging).

## Package A — verified

- Incremental frontend response reader checks declared and actual bytes before copying or decoding. Retained application buffer is at most 2 MiB. Fetch transport may prefetch separately; this is not a network-transfer limit.
- Unknown/chunked lengths, false lengths, split UTF-8, malformed text, abort and stalled cancellation have explicit errors. Startup catalog/health/recording errors remain visible.
- Independent 3 MiB, 64 KiB-chunk unit reproduction stops after 33 reads: 2 MiB retained plus one rejected chunk; cancellation observed. Real Chromium probe observed no `Response.text()` calls and cancellation, with a visible startup error. Browser prefetch received all 3 MiB; no transport-byte-cap claim.
- Frontend tests: 91 passed, 0 failed/skipped. Response cohort: 10 passed. Production TypeScript/Vite build passed (existing optional chunk-size warning retained).
- Entire Stock Intelligence browser program: 10 passed, 0 failed. UI expects `≈7.966`; independent zero-rate reference remains 7.965567455405804 at 1e-12 tolerance; exact input units and expanded full precision checked. Pricing implementation unchanged.
- During repair, browser runs exposed missing disclosure accessible naming, transient CDP response-body lifetime and asynchronous disclosure rendering. Corrected naming and explicit waits; numerical API checks use independent same-origin HTTP requests rather than brittle CDP body retrieval. These failed attempts are retained in ignored local evidence.

Evidence: `build/atlas-sprint3/evidence/` outside this worktree. No provider requests, secrets, raw market data, native code or canonical definitions changed.

## Fake-only paper backend — verified checkpoint

Implemented durable fake intent/risk/reconciliation infrastructure, default-off workspace, strict Origin/proof API, exact-cent limit/day integer-share contract and independent no-network tests. See `PAPER_SANDBOX_CONTRACT.md`.

Final backend cohort: **51/51** in native-backed Python Debug, Release and ASan/UBSan; zero failures/skips. Live LSan checks returned0; this excludes CPython shutdown-leak certification. The earlier47-test runs and two subsequent49-test checks are superseded for the new cohort by51-test runs. Existing Python regressions separately passed678/configuration (2,034 total). Native unchanged-source existing builds passed940 CTest outcomes and48/48 frozen identity comparisons across six GCC/Clang configurations. Existing Starlette TestClient deprecation warnings remain visible.

Paper UI, typography/canvases, company-to-research navigation and authored export are currently uncommitted but survived. New actual-browser cohort passed6 groups,120 dark/light viewport/workspace combinations and28 screenshots. Its initial selector and shorthand-color-parser failures are preserved in ignored evidence; controls were never force-clicked and thresholds were not weakened.

Next: checkpoint frontend after advanced15-mode and financial/security browser regressions, finish guides and source-bound evidence. Actual Alpaca access and order submission remain prohibited. No claim of current native ARM64, owner Codespaces authentication or observed-market qualification.
