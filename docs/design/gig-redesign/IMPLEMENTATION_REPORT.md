# GIG institutional frontend redesign

## Delivered candidate

- Branch: `development/gig-ui-redesign`.
- Preserved Sprint 4 baseline: `0c03a698fdac1be8b1032b255208a3ef2320341a`.
- Final application-source commit: `8971257af4e1400726d8aa72d33e0dd9debf4b79`.
- The delivery commit adds documentation and authored visual evidence only. Its exact SHA is reported after pushing.

Recovery preserved the surviving camera work and completed it in an isolated worktree. No main, release, Sprint 3, Sprint 4 or audit branch was merged or modified. The target branch was absent locally and remotely at the initial check; it was created from the exact Sprint 4 application baseline.

## Implemented interface

The visible product identity is **GIG — Order Book & Market Microstructure Terminal**, with **C++20 Research & Execution Simulation** as its descriptor. Browser title, navigation and accessible branding use GIG. Internal `atlas-*` classes, storage keys, APIs, IDs and test selectors remain stable.

The new `Navigation`, `TerminalHeader`, `WorkspaceLaunchpad` and `OrderBook` components replace the former inline shell and book presentation. All 12 workspaces remain available. Navigation groups Market Structure, Research and System work. Global company search preserves the existing API/proof boundary and NVDA-to-AAPL selection behavior. Command Center displays current native/source state. Native API connectivity and upstream provider feed health remain separate statuses.

The order book uses paired bid/ask tables on desktop and stacked, full-width tables on phones. Each shows price, size and exact cumulative displayed quantity, with bounded vertical scrolling. BigInt presentation totals avoid binary64/uint64 overflow without modifying native state. Prices and quantities retain their source scales. The larger cumulative-depth chart uses occupied-level rank, explicit units, step geometry and inspectable values; it does not imply continuous price-distance liquidity.

Replay/session setup and concentration diagnostics use disclosures. Playback remains directly accessible; Historical Replay opens its source configuration by default. Financial facts retain exact backend values, reporting periods, accession numbers, provenance and missing-data explanations. Financial ratios are not recalculated in JavaScript.

The requested local system-font stack replaces Inter as the preferred font. Body text is 15px, ordinary controls/tables 14–16px and secondary annotations 12–14px. Tabular numerals, stronger headings, larger canvases, clear focus states and responsive layouts apply in both themes. Teal bids, coral asks, blue neutral information and amber warnings have accompanying text labels.

## Automatic 3D motion

A shared lifecycle now serves all five renderer families: native depth, the eight advanced research models, the four Level 1 models, GARCH and option scenarios. All 15 existing visualization modes and input restrictions remain.

Populated, visible scenes orbit automatically when motion is permitted. The speed is approximately 2.1 degrees/second; automatic draws are capped at 30Hz, with a 0.1-second delta clamp to prevent catch-up jumps. Motion changes the camera only. Source observations, geometry calculations, replay position and native state remain unchanged.

Each visualization has accessible pause/resume independent of data pause. Manual rotation, pan, zoom, reset/presets, hover inspection and exact tables remain available. Interaction suspends orbit while manipulating the camera. Reduced-motion preference, hidden documents, offscreen scenes and unavailable data suspend automatic work. Advanced-lab pause intent survives context loss/retry.

Cleanup cancels animation frames, disconnects observers, removes media/document/control listeners and disposes GPU resources. WebGL failures retain explicit 2D/table alternatives and retry behavior. Hidden-document browser testing uses a controlled visibility event; it is not a physical operating-system tab acceptance test.

The advanced ask-side display color intentionally changed from `#f5a869` to `#f27b89`. Across 384 baseline comparisons, source data, coordinates, values, axes and labels are identical with color excluded. The presentation hash changed from `222811765f4d91b5ac85af367c28cbbd2a01664d58c99dd1e77322e58365eaaa` to `2f04850cfc04e07559999d7afd3c1ea14a1f0161fa7c549827efab3dfb376143`. These display hashes are distinct from the eight frozen native identities, which are unchanged.

## Safe frontend cleanup

Removed `styles.css`, `atlas.css` and `institutional.css` after checking imports and used selectors. New `terminal.css` owns shared tokens, shell, controls, book/depth and responsive behavior. `workspaces.css` preserves component-specific contracts. The cleanup removed 61 overwritten declarations within identical selector/at-rule contexts, respecting important priority, and 148 superseded shell selectors after their ownership moved.

Touched renderer/App/desk source was formatted with the pinned TypeScript printer. No dependency or lockfile change was needed. There is no diff to C++ source, native tests, Python bindings, backend, provider or paper implementation, build contracts or permission policies. Existing optional 3D code splitting remains. This does not claim every legacy component or unused CSS rule has been eliminated.

## Final executed validation

All final checks below passed, with zero failed or skipped test outcomes. Counts overlap and must not be summed into a claim about unique requirements.

| Check | Actual result |
|---|---|
| Frontend Node tests | 118/118: 102 existing, 12 camera lifecycle, 4 exact ladder |
| Strict TypeScript and production build | PASS |
| New redesign browser program | 10 checks; 48 settled workspace/theme/width journeys |
| Existing browser programs | All 12 programs exit 0; 13 total including redesign |
| Existing responsive workspace matrix | 120 routes at 360/390/768/1280/1920px, both themes |
| Backend/native binding regressions | Debug 274/274; Release 274/274; ASan+UBSan 274/274 |
| Frozen native references, GCC Release rerun | 8/8; all identities unchanged |
| Independent native dictionary/Fraction oracle | 241 states; 17,143 assertions; zero failures |
| Geometry/source parity | 384 cases; numeric/source fields unchanged except documented display color |
| Local HTTPS/WSS/proof tests | 20 checks across three programs |
| Rendered contrast sampling | 24 workspace/theme views; zero recorded failures |

Existing browser outcomes include native workflow 21, Stock Intelligence 10, stock loading 10, Atlas 21, Atlas Phase 2 11, advanced research 23, workspace qualification 120 and Sprint 3 checks 7, plus contrast, performance, same-origin and handshake programs. Ordinary clicks are used; no forced click conceals inaccessible controls.

Browser programs ran against one finalized immutable asset set. Source, asset, test-log and screenshot digests are bound in [EVIDENCE.json](EVIDENCE.json). The captured source receipt predates the final source commit, but every recorded source byte hash was verified against that commit. Test logs remain locally under the ignored evidence directory; their digests are committed, not a claim of externally available CI artifacts.

No standalone lint configuration/script exists. Strict TypeScript with unused-local/parameter checks, production build and Node tests provide the available static checks; ESLint is not claimed. Existing Vite deferred-chunk and Starlette TestClient deprecation warnings remain visible. ASan/UBSan Python evidence uses the existing compiled native binding and a live LSan checkpoint of zero, with shutdown leak checking disabled. No fresh native compilation or hosted/ARM64 qualification is claimed.

## Measurements and actual visual review

- Initial JavaScript: **249,055 bytes**, approximately **77.55kB gzip**, versus 242.59kB at Sprint 4. No size-reduction claim is made.
- Main CSS: **74,337 bytes**, approximately **12.58kB gzip**. The larger shared design system adds bytes despite duplicate removal.
- Deferred Three/OrbitControls chunk: **516.95kB**, approximately **128.60kB gzip**. Its existing large-chunk warning remains. The initial Command Center requests no optional Three/research-scene/quote-cloud/paper-sandbox chunk.
- Local authored browser measurement: one warmup, three samples; median initial navigation plus network-idle **826.5ms**, company route **126.4ms**; sampled JavaScript heap **4,351,872–4,439,392 bytes**.
- Native camera check: **18 automatic frames in 800ms**, within its 30Hz draw ceiling. Suspension tests verify counters stop while native state and replay position remain equal.

These shared-host headless measurements are not comparative speedups, provider latency, physical-device performance or a long-session GPU leak qualification.

Seven representative screenshots are committed under [visual/](visual/), with hashes and fixture classifications in the manifest. Desktop Command Center, desktop/mobile order book, advanced multicolor 3D and populated financial statements/trends/light theme were captured. Representative screenshots were opened and inspected. All populated observations in these captures are authored native/financial fixtures, not provider or owner-account data.

| Screenshot | Input classification |
|---|---|
| [Command Center](visual/command-center-dark.png) | Authored native fixture |
| [Desktop order book](visual/order-book-desktop-dark.png) | Authored native fixture |
| [Phone order book](visual/order-book-phone-light.png) | Authored native fixture |
| [Multicolor research scene](visual/research-3d-dark.png) | Authored synthetic research fixture |
| [Financial statements](visual/financial-statements-dark.png) | Historical synthetic financial fixture |
| [Financial trends](visual/financial-trends-dark.png) | Historical synthetic financial fixture |
| [Financial light theme](visual/financial-light.png) | Historical synthetic financial fixture |

## Development failures retained and repaired

- TypeScript rejected an unknown quantity-scale ReactNode and a misplaced disclosure wrapper. Both were fixed before final compilation.
- Source capture encountered pending stylesheet deletions; legitimate deletions were staged. A browser-runner loop variable shadowing parsed CLI arguments was renamed.
- New browser tests now explicitly enable the existing optional 3D view and create a genuinely offscreen layout. A proposed eight-draw-call threshold was corrected to the existing nine-call ceiling. Original geometry and safety assertions were preserved.
- A new source-stability assertion raced the last asynchronous replay action. It now awaits each ordinary-click POST and completed action before retaining the same strict before/after assertion.
- Advanced renderer pause intent was moved to its parent so context recovery preserves it. Descriptor layout, phone ladder width, metric readability and keyboard skip-link behavior were repaired after screenshots and interaction tests.
- The existing native browser workflow now opens the new source/session disclosure before its original source selection. Numerical, financial and provenance assertions are unchanged.

Failed development logs are retained locally and their digests are bound. No mathematical test or warning was removed to manufacture a pass.

## Remaining boundaries

This is a built and automatically verified private frontend candidate, not production trading readiness or empirical market validation. Owner private Codespaces authentication, physical Android/Safari/assistive-technology acceptance, current-candidate ARM64 and live-provider qualification remain separate. Local TLS/proxy fixtures do not establish owner-edge authentication.

Contrast checks cover their executed scope, not full WCAG 2.2 certification or every shader color. Long-session GPU behavior remains unqualified; exact tables and 2D alternatives remain available. No provider calls, credential inspection, market-data acquisition, real orders, entitlement changes, paid services, public port changes or workflow dispatch occurred.

## Checkpoint commits

1. `96bd77cd70b8abb70ddd2a6749b7e1afa6669ba0` — camera-only orbit lifecycle and tests.
2. `47b9ed8e977cf0d887fbf211737bbe7f5715d837` — GIG shell, exact ladders and consolidated themes.
3. `86b6a3aa98afe0c7536b8feda9eff76b527052d9` — mobile ladders, hierarchy and settled visual checks.
4. `8971257af4e1400726d8aa72d33e0dd9debf4b79` — keyboard-safe navigation and camera operating guide.

All were pushed only to the redesign branch. The final delivery commit contains this report, manifest, screenshots and checkpoint closure.

## Changed-file inventory

```text
A	docs/design/gig-redesign/EVIDENCE.json
A	docs/design/gig-redesign/IMPLEMENTATION_REPORT.md
A	docs/design/gig-redesign/PROGRESS.md
A	docs/design/gig-redesign/visual/command-center-dark.png
A	docs/design/gig-redesign/visual/financial-light.png
A	docs/design/gig-redesign/visual/financial-statements-dark.png
A	docs/design/gig-redesign/visual/financial-trends-dark.png
A	docs/design/gig-redesign/visual/order-book-desktop-dark.png
A	docs/design/gig-redesign/visual/order-book-phone-light.png
A	docs/design/gig-redesign/visual/research-3d-dark.png
A	terminal/tests/gig-redesign-validation.mjs
A	terminal/web/src/Navigation.tsx
A	terminal/web/src/OrbitMotion.tsx
A	terminal/web/src/OrderBook.tsx
A	terminal/web/src/TerminalHeader.tsx
A	terminal/web/src/WorkspaceLaunchpad.tsx
A	terminal/web/src/bookPresentation.test.ts
A	terminal/web/src/bookPresentation.ts
A	terminal/web/src/cameraMotion.test.ts
A	terminal/web/src/cameraMotion.ts
A	terminal/web/src/terminal.css
A	terminal/web/src/workspaces.css
D	terminal/web/src/atlas.css
D	terminal/web/src/institutional.css
D	terminal/web/src/styles.css
M	docs/user-guide/GETTING_STARTED.md
M	docs/user-guide/THREED_VISUALIZATIONS.md
M	terminal/tests/browser-validation.mjs
M	terminal/tests/run_sprint3_browser.py
M	terminal/web/index.html
M	terminal/web/package.json
M	terminal/web/src/App.tsx
M	terminal/web/src/DepthChart.tsx
M	terminal/web/src/Landscape3D.tsx
M	terminal/web/src/ModelSurface.tsx
M	terminal/web/src/QuoteCloud.tsx
M	terminal/web/src/ResearchDesk.tsx
M	terminal/web/src/ResearchLab.tsx
M	terminal/web/src/ResearchScene.tsx
M	terminal/web/src/VolatilitySurface.tsx
M	terminal/web/src/main.tsx
M	terminal/web/src/research3d.css
M	terminal/web/src/research3d.ts
```

## Safe Codespaces update

Preserve local edits first;do not reset/clean or overwrite them. When ready to review this completed candidate:

```bash
git fetch origin development/gig-ui-redesign:refs/remotes/origin/development/gig-ui-redesign
```
```bash
git switch development/gig-ui-redesign
```
```bash
git pull --ff-only origin development/gig-ui-redesign
```
```bash
npm --prefix terminal/web ci && npm --prefix terminal/web run build
```
Stop the previous server with Ctrl+C in its terminal. Keep provider/order gates off:
```bash
GIG_ALPACA_ENABLED=0 GIG_ALPACA_LIVE_ENABLED=0 GIG_ALPACA_HISTORY_ENABLED=0 GIG_PAPER_EXECUTION_ENABLED=0 bash scripts/start_terminal.sh
```
Use the existing authenticated forwarded HTTPS address with port 8787 Private. Hard-refresh Chrome if it has an older bundle. No new keys,SEC contact setup,public forwarding or native engine rebuild is required. Enable optional 3D;its camera now starts automatically unless reduced motion or a prior scene pause applies. Camera pause and replay/data pause are separate controls.
