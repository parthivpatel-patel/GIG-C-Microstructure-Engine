# GIG — workstation redesign delivery

Review date: 2026-11-03 (America/New_York). Branch: `development/gig-ui-redesign`. Starting source: `237167358969b0c7cec04c639b412fbe494bb192`.

Implementation checkpoints: `08d2a9505c025792c585ba0d3cb02ed779d6eb34` (shell and12workspace compositions), `6d1f5123db874b3df23d9b3161004749a54ec35e` (native ladder visual repair and regression). The following delivery commit contains only documentation/evidence. Source/asset digests and exact test artifacts are in GIG_WORKSTATION_REDESIGN_EVIDENCE.json.

## Implemented system

The new React compositions use an original GIG mark, near-black/charcoal planes, restrained cyan/emerald/coral/amber tokens and system typography. Body text is16px, controls/data rows generally14–16px, primary financial values24–32px. Tabular numerals, visible keyboard focus, semantic native tables, high-contrast light/dark themes and reduced-motion behavior remain. Navigation is grouped into overview, markets, microstructure, laboratory and system. The desktop frame uses an independently scrolling content pane; the mobile frame provides a horizontal workspace navigator. Global security search supports Ctrl/Cmd+K and `/`, with Escape dismissing results; it does not start acquisition.

This changes actual page composition, not just colors. Shared headers provide purpose, source boundary and real related-workspace navigation. Discovery, subscriptions, observations, company context, native analysis and operations now have different arrangements. Simulator and research view selectors replace long stacked laboratories while retaining all existing controls. Advanced company acquisition/provenance detail is disclosed on request. No provider/schema, C++ mathematics or API endpoint was replaced.

The authoritative stylesheet is `terminal/web/src/workstation.css`; the unused339-line `terminal.css` was removed. Existing `workspaces.css` and technical `atlas-*` selectors/storage keys remain compatibility primitives. They are not user-facing branding. The theme preference key is preserved so an existing owner's preference is retained.

## Twelve workspace outcomes

| Workspace | Implemented composition / useful behavior | Verification |
|---|---|---|
| Command Center | Research brief, exact native rank-profile/quote snapshot, actionable workflow links, working saved-symbol table and separate source-readiness summary | Native/fixture navigation and actual captures |
| Securities Universe | Discovery/filter console beside provenance, accepted identity counts, results and pagination; acquisition controls remain gated | Target-view matrix; existing directory contracts |
| Stock Intelligence | Company masthead, primary research actions, acquisition disclosure, financial tabs, reported-data/quote composition, concise SEC availability disclosure and retained exact-detail views | NVDA→AAPL selection; theoretical numerical reference; populated financial/filing fixtures |
| Live Markets | Separate subscription console and per-symbol observation stage; bounded selectors, visible status/age/source and honest unavailable cards | Provider-disabled and authored Level1 browser programs |
| Multi-Stock Comparison | Shared monitoring console, comparison matrix, per-symbol observations and opt-in coordinated geometry | Layout and existing Level1 modes/entitlement negatives |
| Order Book | Readable dual ladders, explicit cumulative quantities, snapshot summary, bounded full view and diagnostics | Exact native prices/quantities; non-overlapping cells |
| Market Depth | Large camera stage with compact five-level-per-side context ladder and source integrity | Orbit/drag/zoom/presets, context recovery, 2D fallback |
| Order Flow | Dedicated metrics/tape arrangement and accessible advanced research entry | Native state, causal metadata and research regression |
| Historical Replay | Transport dock, timeline, scene/context split and progressive source/recording configuration | Exact step/seek/restart/EOF/recorded replay |
| Execution Simulator | Native simulator/result composition with separate explicit offline-sandbox and disabled-provider views | Three native schedule/cost references; fake-only persistence/restart |
| Research & Validation | Separate model scenarios, 3D laboratory and validation/evidence views | Existing parameter modes, exact diagnostics, authored export, model/input boundaries |
| Operations | Health/runtime split plus separate source/safety diagnostics | Source/transport UI, existing security and health contracts |

All12 are redesigned and **fixture-browser verified**. This does not mean that unavailable sources became available, that every provider is qualified, or that all independent target acceptance gates passed.

## Three-dimensional behavior

The existing15visualization modes and mathematical mappings remain. The bounded camera scheduler already stopped for reduced motion, hidden/offscreen scenes, missing eligible input, explicit pause and interaction. Optional depth3D also starts behind an explicit enable action. Those legitimate states can look static; no broken underlying orbit loop was reproduced in this task. The new visible camera-status overlay distinguishes those reasons and says when motion is camera-only. It never labels camera motion as market activity.

Actual Chromium checks prove automatic movement with input, manual drag/zoom/pan/presets, pause/resume/reset, reduced-motion suspension, context-loss retry, independent controls and disposal on navigation. The eight advanced modes, four existing Level1 modes and existing model surfaces remain available under their original input rules. L1 cannot create depth/order identities. Empty/no-WebGL cases retain2D and exact/source inspection. Renderers use the original bounded frame owner and lazy imports; no unnecessary hidden-scene loop was introduced.

## Executed validation

- TypeScript and Vite production build: PASS; existing deferred-chunk warning retained.
- Frontend unit tests: **123 passed,0 failed/skipped** (118 retained +5 new metadata/motion-description tests).
- Python native/API suite: **274 passed**; stock/provider/SEC suite: **207 passed**; zero errors/failures/skips. Provider transports are authored and external sockets are guarded.
- Native Release references: **8/8 passed**, all eight frozen hashes unchanged. Existing unchanged-source binaries were exercised. No fresh Debug/Clang/sanitizer/ARM64 compilation is claimed; their prior engine evidence is retained because native/build inputs were not changed.
- Browser: new workstation **6**, existing GIG **10**, native UI **21**, Stock Intelligence **10**, advanced3D **23**, Sprint3 functional **7**, recorded replay **9**, populated financial/layout **11**: **97 checks passed**, zero final failures/skips. All retained mathematical/source/persistence assertions remain.
- New layout matrix: **120** combinations,12workspaces ×2themes ×5viewports:1366×768,1440×900,1920×1080,390×844,360×800. Financial/model programs additionally cover their existing viewport matrices.
- Rendered HTML text contrast: **24** workspace/theme contexts, **5,686** sampled elements, **0** failures against applicable3:1/4.5:1 thresholds. This is sampling, not full WCAG2.2 certification or screen-reader acceptance.
- Verified local TLS proxy programs: **6+6+8=20** checks, including rewritten Origin/Host, strict rejection and repeated WSS upgrades. Certificate and hostname validation stayed enabled. Actual owner GitHub authentication was not tested.
- Clean implementation checkpoint: source/runtime/assets offline receipt passes, actual loopback native startup receipt matches, and browser Origin/ticket/WS correlation passes. No provider or secret inspection.

Build finishes before browser execution. Every browser group checks asset hashes before and after execution; final groups used the same assets. `run_sprint3_browser.py --programs` permits selection from a fixed allowlist, enabling focused regression recovery without rerunning unchanged groups or arbitrary script paths.

## Failures found and corrected

1. Screenshot review caught legacy fixed-main offsets leaving an empty gutter and column-oriented related navigation. The grid now owns the entire frame; navigation orientation is explicit.
2. Unbroken authority tokens overflowed the new narrow subscription console. Display labels use readable separators and bounded wrapping; the authority itself is preserved in source metadata.
3. Legacy `.book-row {display:grid}` interfered with table semantics, overlapping values in narrow ladders. Explicit table-row/table-cell rules restore alignment; compact context ladders show a labeled subset rather than tiny columns. New browser assertions check every displayed cell at allthree desktop widths.
4. Some reset/shortcut glyphs lacked font coverage. Shortcuts use original SVGs; reset uses readable text.
5. Initial test code expected the wrong paper-boundary heading. Existing stock/paper/diagnostic browser flows needed the new explicit view/disclosure navigation, including reselecting the sandbox after reload. The numeric, risk, provenance and FILLED/persistence assertions were preserved. Failing logs/screenshots remain ignored and hash-bound.
6. The source-inventory runner initially encountered the intentionally deleted stylesheet before its deletion was staged. No app failure was inferred; the staged deletion and subsequent source receipts correctly reflect the new tree.

## Measured frontend cost

Previous entry:249.05kB,77.55kB gzip. Delivered entry:254,545bytes, approximately79.06kB gzip; exact bytes/hashes are in the manifest. CSS grows from74.33kB to 94.93kB (15.51kB gzip) to cover the new compositions. Optional Three.js/OrbitControls remains a deferred roughly517kB chunk; Command Center makes no Three.js request. No dependency or external font was added. This is a design-coverage tradeoff, not a bundle-size improvement claim.

One warmup and three independent disabled-cache Chromium contexts measured navigation plus network-idle settling at758/825/816ms and company route handling at127/120/114ms. Sampled JS heap was4.89–4.99MB and DOM nodes1,213. Chromium154, local x86_64, authored fixtures/software renderer. Network-idle is included; these are not pure render latency, production SLA, physical-mobile or GPU-memory measurements. Raw performance metadata is hash-bound.

## Visual evidence and limitations

Actual browser captures include every workspace, both themes, mobile layouts, financial trends/statements/filings, native depth and all advanced modes. Paths/SHA256/classification are in the evidence manifest. They remain in ignored build directories rather than committing screenshots or private state. Captured financial/provider inputs are **independently authored fixtures**, not actual SEC/Alpaca observations or empirical qualification. Images were also inspected visually; passing counts alone were not the visual acceptance criterion.

No external provider request, account access, market-data download, paid resource, public port, order submission or permission gate activation occurred. `terminal/stocks`, `terminal/server`, native/build/Python source and provider configuration are unchanged. The owner's uncommitted subscription-acknowledgment fix was not present in this clean task worktree; no claim is made to have accessed or replaced it.

Remaining limitations: real owner-private Codespaces forwarding/browser acceptance, actual authorized provider observations, physical Android/GPU/screen-reader review, current target security/advisory clearance and exact-candidate native ARM64 remain unverified. Complex research pages/tables intentionally retain internal scrolling and progressive detail. Historical audit documents and technical schemas were not renamed. Institutional production readiness is not established by this frontend delivery.

## Existing Codespace update

Stop the current server with Ctrl+C in its terminal. Preserve any local acknowledgment patch or other edits; do not reset/clean/stash automatically. Run one command at a time:

```bash
git status --short --branch
```

```bash
git switch development/gig-ui-redesign
```

```bash
git pull --ff-only origin development/gig-ui-redesign
```

```bash
npm --prefix terminal/web run build
```

```bash
bash scripts/start_terminal.sh
```

If dependencies are missing, use the existing pinned `npm --prefix terminal/web ci --ignore-scripts`; no dependency versions changed here. Stop if Git refuses the fast-forward or reports overlapping local work. Backend files were not modified by this redesign. Keep port8787 **Private**, open the existing authenticated Codespaces URL and hard-refresh. Existing credentials/configuration remain server-side; these commands add no market-data/execution permission flags. Real/paper execution must stay disabled.

Offline reproduction: after installing existing runtime/browser dependencies, run `npm --prefix terminal/web test`, build finalized assets, then `.venv/bin/python terminal/tests/run_sprint3_browser.py --skip-build --redesign --output build/gig-visual-new`. For focused programs use the allowlisted `--programs` option; never rebuild assets while a browser group is running. The native module is required. This launches owned loopback fixture servers and removes only its own temporary state; no provider is contacted.
