# GIG ATLAS product-development checkpoint

Report date: October 28, 2026 America/New_York (execution continued into October 29 UTC).
Product baseline: `50b83c581297a200ffc15b6f5a4801b0a60a5d49`.
Recovered SEC checkpoint: `20b0a4fccbb286f536162ca88ea3ef091b22f3ee`.
Final tested implementation: `7b28431943d2eb3d63485bf248015242321da32e`.
Branch: `feat/atlas-final-release`. Main is unchanged at
`12f3a53943dc245e36f2cbbc35b9910fb21c0718`.

## Assessment

The narrow replay-oriented landing page has been replaced by a company-research desk,
with dedicated reference discovery, live-observation and multi-stock comparison
workspaces. All original nine workspaces remain accessible. New source-aware 3D
representations, a separate mathematical model laboratory and company-coverage
disclosures are implemented and exercised in the actual browser/native application.
Automatic SEC reference discovery is implemented, configuration gated and fixture
tested. The search index now avoids sorting already ordered ticker-prefix matches.

This is a substantial implemented product checkpoint, **not full real-market product
completion**. Actual runtime coverage here is **13 curated fallback identities,
0 imported official listing identities and 0 imported SEC mappings**. No SEC identifying
configuration or Alpaca credential pair is available in this execution environment.
No official financial reconciliation, provider activation, restricted LOBSTER processing
or market-data acquisition was performed. Authored 50k-identity benchmarks and browser
fixtures must not be reported as actual securities coverage.

## Verified milestones

| Commit | Delivered behavior |
|---|---|
| `c8ad81ff9d3b548917d5a506f48fb9217101c912` | Rights-gated two-file Nasdaq directory parser, bounded acquisition, atomic publication, indexed discovery and pagination |
| `3366541caa5c7e68a8c186b6f911476d4b8f5f24` | Read-only company availability contract and source-safety regressions |
| `20b0a4fccbb286f536162ca88ea3ef091b22f3ee` | Automatic SEC startup/refresh, permission-aware accepted-reference cache, exact-symbol union and provenance |
| `4eb310d4852a8e8e60e44dc60731fb210358c60d` | Faster ranked search with independent scan oracle and reproducible authored-directory measurement |
| `7b28431943d2eb3d63485bf248015242321da32e` | Twelve-workspace research interface, company coverage, Level 1 research geometries, GARCH response surface and browser regressions |

Each milestone was pushed to the authorized branch and its remote SHA checked. The
delivery documentation commit is intentionally separate; its exact SHA is in Git and
the delivery response, avoiding a self-referential document hash. No workflow was
dispatched, main changed, release published, paid resource created or native engine
source modified.

## Completion matrix

Status describes the declared implemented contract, not complete exchange coverage.

| Requirement / source path | Implementation and automated evidence | Qualification / remaining limitation |
|---|---|---|
| Automatic SEC discovery: `terminal/stocks/directory.py`, `service.py`, `discovery.py` | Ready default server loads official fixed reference at startup and six-hour intervals; explicit opt-out; 60-second accepted cache; failure retains accepted mapping; 180-case stock cohort and directory/discovery regressions | IMPLEMENTED, fixture verified; current official acquisition BLOCKED by missing identifying configuration |
| Broad directory: `directory.py`, `market_catalog.py` | Complete two-file parse before publication; bounds, enums, aliases, exclusions, pagination and collision rejection; independent search oracle | IMPLEMENTED; official body/rights/current coverage UNVERIFIED; fallback is not full US universe |
| Command Center: `ResearchDesk.tsx`, `App.tsx` | Company continuation, workflow shortcuts, saved watches, feed/reference/retention status; no replay controls presented as market summary | Browser verified; actual quotes unavailable without authorized source |
| Securities Universe: `UniverseWorkspace.tsx`, `directoryContract.ts` | Bounded 20-row pages, ticker/name prefixes, explicit listing/SEC counts, CIK/identity classes, separate gated refresh controls, 30-second accepted-cache reread | Browser AAPL/APLD/CRWV/GOOGL and newly refreshed fixture registrant pass; no tradability inference |
| Stock Intelligence: `StockIntelligence.tsx`, `CompanyCoverage.tsx`, `api.ts` | Separate identity/facts/acquisition coverage, source-aware v2 financials, exact backend ratios, shared-scale balance chart, reported statements, filing filters/pages, missing/stale/error states | Existing financial/browser regressions preserved; selected reported facts, not complete reconstructed XBRL/IFRS or complete PIT history |
| Live Markets: `LiveMarket.tsx` | Shared authorized subscription manager, search/watchlist controls, four simultaneous panels, per-symbol health, 256-observation retained window, original source timestamps and backend exact descriptors | IMPLEMENTED, fixture verified; credential/entitlement/provider qualification BLOCKED; full searchable identity catalog does not expand concurrent limit |
| Multi-Stock Comparison: `LiveMarket.tsx`, `marketGeometry.ts` | Dedicated comparison table, progressive source details and one coordinated renderer; retained selected symbols survive changing available choices | Browser subscription handover and isolation pass; unequal source times explicitly disclosed |
| Order Book, Market Depth, Order Flow: `App.tsx`, `Landscape.tsx`, `Landscape3D.tsx`, `ResearchPanel.tsx` | Original native book/depth/flow workspaces retained under common navigation/surfaces; optional native 3D and 2D fallback | Browser/native checks pass; no live L1-to-L2/L3 synthesis |
| Historical Replay: `App.tsx`, `ResearchPanel.tsx` | Native replay controls, session selection, recorded playback and OFI panel retained on dedicated page | Native/recorded browser regressions pass; source completeness restrictions unchanged |
| Execution Simulator: `App.tsx`, `ResearchSummary.tsx` | Existing bounded native schedules/fills/costs preserved; simulated labels; irrelevant replay toolbar removed | Native simulation/browser checks pass; no live order submission |
| Research & Validation: `ModelSurface.tsx`, `modelSurface.ts` | Existing model/validation features preserved; new declared 441-vertex GARCH one-step response grid with parameter checks/exact displayed grid | Numerical and browser controls pass; mathematical demonstration, not calibrated forecast/observed volatility |
| Operations: `MarketHealth.tsx`, `App.tsx` | Existing feed/native/resource/provenance diagnostics remain available with progressive detail | Browser/API/security checks pass; ready configuration is not provider qualification |
| Interactive Level 1 3D: `QuoteCloud.tsx`, `marketGeometry.ts` | Quote prices, basis-point midpoint change, rolling eight-return variation and log trade-size modes; independent cameras/presets, scale/palette/fullscreen, pause scope, pick details, WebGL recovery | Browser recovery/ordinary controls pass; approximate visualization, not exact monetary analytics or corrected tape |
| Resource cleanup/performance | Instancing, event-driven rendering, deferred Three.js, observer/listener/geometry/material/control disposal; single-pass scale bounds; paused geometry upload checks | Measured locally on SwiftShader; sustained hardware/mobile GPU leak/FPS qualification NOT EXECUTED |
| Responsive/accessibility: `atlas.css`, `WorkspaceIcon.tsx` | Shared dark/light tokens, SVG navigation, focus/skip/help, readable status, scoped table scroll, five widths; actual selected control contrast checks | 60 workspace-width and 120 theme-width combinations pass; partial accessibility validation, not WCAG certification or physical Android acceptance |
| Security/entitlements/persistence | Existing endpoint-bound proofs, exact origins, private source settings, feed and retention gates unchanged | 53 security and 8 verified local HTTPS/WSS proxy checks pass; no private data/credentials committed; real permissions not inferred |
| Native engine / packaging | No C++/binding/schema changes; native consumer cohorts, eight frozen reference cases, installed-wheel checks and source inventory retained | Local x86-64 evidence; this new HEAD has NOT received native ARM64 or independent hosted qualification |

## Source access and lawful-use investigation

See [source ledger](SOURCE_ACCESS_LEDGER.md). Nasdaq's official definitions and linked
terms were read. Fixed candidate directory URLs returned HTTP 200 to metadata-only
HEAD requests; their bodies were not acquired. Linked terms do not establish automatic
derived-cloud catalog processing rights. Approval flags remain off. SEC registrants
are an authoritative issuer-reference candidate under existing SEC identifying and
fair-access configuration; they are not a full primary-exchange listing universe.
No unconfigured alternative destination was repeatedly probed. NYSE/Cboe and provider
reference sources remain candidates requiring their own format/rights/access review.

Automatic startup, cache lifetime, explicit refresh/disable controls and source classes
are detailed in [SEC automatic discovery](SEC_AUTOMATIC_DISCOVERY.md). CIKs are never
guessed from names or share-class punctuation. Current ticker mappings do not prove
historical identity or financial information availability at a historical date.

## Executed validation

Counts are outcomes per suite/configuration, not a deduplicated total. All listed final
suites have zero failures/errors/skips. Full raw local logs are hashed in
`product_evidence.json`; the file also contains expected canonical hashes, compact
browser/performance results, environment and screenshot receipts. Earlier unsuccessful
attempts are separately preserved and described below.

| Cohort | Result | Evidence under `build/product/` |
|---|---:|---|
| Stock/backend fixtures, Debug native binding | 180/180 | `resume-stocks-debug.log` |
| Stock/backend fixtures, Release native binding | 180/180 | `resume-stocks-release.log` |
| Stock/backend fixtures, ASan+UBSan binding | 180/180; live LSan check 0 | `resume-final-sanitizer.log` |
| Terminal/native API consumers, Debug | 274/274 | `resume-native-debug.log` |
| Terminal/native API consumers, Release | 274/274 | `resume-native-release.log` |
| Terminal/native API consumers, ASan+UBSan | 274/274; live LSan check 0 | `resume-native-sanitizer.log` |
| Final indexed-search oracle under ASan+UBSan | 14/14; live LSan check 0 | `resume-index-sanitizer-final.log` |
| Frontend pure contracts/calculations | 41/41 | `resume-geometry-unit.log` |
| Seven stable-asset browser suites | 91/91 | `resume-qualified-stable-browser/` |
| New product interactions | 32/32 | `resume-product-32.log` |
| Ratio history / live market / SEC / discovery browsers | 14/14,21/21,3/3,3/3 | `resume-qualified-browser/browser-{1,2,3,4}.log` |
| Native landscape / Level 1 context-loss recovery | 5/5,4/4 | `resume-qualified-browser/browser-5.log`, `gpu-quote.log` |
| Origin/proof/security regression | 53/53 | `security-final.log` |
| Verified local HTTPS/WSS rewritten-proxy checks | 8/8 | `tls-final.log` |
| Frozen independent native reference cases | 8/8; all eight hashes unchanged | `resume-canonical.log`, `resume-canonical.xml` |
| Installed existing 0.1.1 wheel interface/export tests | 14/14 | `wheel-consumer.log` |
| Packaging pattern regressions | 3/3 | `packaging.log` |
| New source archive at implementation checkpoint | 803 safe byte-identical members | `resume-source-inventory.log`, `source-delivery/inventory.json` |

The sanitizer wrapper performs a live-interpreter LSan checkpoint; it does not claim
stock CPython shutdown leak qualification. Existing Starlette TestClient deprecation
warnings and Vite's optional >500kB chunk warning were retained. Full GCC/Clang native
rebuild matrices were not repeated: native sources and canonical expectations are
unchanged. No hosted, ARM64, real-provider or device pass is inferred from these checks.

### Browser sequencing and defects found during recovery

`run_atlas_browser_suite.py` builds once, records every asset hash, then executes seven
suites sequentially and rejects any asset change. Product checks run after the build
driver finishes. No forced clicks were used. Scripted DOM observation and intentional
WebGL loss are test instrumentation, not substitutes for clicking controls.

Recovered failures were investigated rather than hidden: native controls moved off the
old Command Center required navigation updates, with the numerical/native assertions
retained; four-panel controls overlapped; light-theme cross-fades temporarily reduced
contrast; long recording selectors overflowed mobile pages; a reference provenance
identifier overflowed 390px. Real sizing/wrapping and atomic theme color changes repaired
these issues. OFI was restored to dedicated replay. The NVDA-to-AAPL regression remains.
The final browser report records zero application errors.

One new geometry test initially read an old SSE window before the current subscription
generation had published enough observations. It now waits for current-generation
eligible quotes and visible geometry, not an arbitrary timeout or a weakened result.
The final 32 checks additionally prove a paused chart retains its original rows AND
symbol scope across subscription changes and that model camera changes do not mutate
the native book. An initial supplemental sanitizer command mistakenly passed `-m` to a
script-only wrapper and failed argument parsing; the corrected 14-case run passed.
Original logs remain under `build/product/`, including `resume-final-browser/`,
`resume-product-browser.log`, `resume-index-sanitizer.log` and earlier recovery logs.

## Measured performance

Local x86-64 Linux, Node24.19/Chromium154 SwiftShader; concurrent shared-host load.
These are reproducibility observations, not trading latency or capacity guarantees.

* Final entry JavaScript: **235,569 bytes**; approximately 73.8kB Vite gzip estimate.
  Earlier product baseline entry was 232,995 bytes. This checkpoint does not claim a
  further entry-bundle reduction. The research desk and contracts load separately;
  Three/OrbitControls remains deferred until an optional 3D page is requested.
* Cold-context navigation/settle samples with one warmup/three repetitions:
  911.8/846.7/1208.6ms; Stock Intelligence route 269.7/160.5/342.1ms. These include
  loopback/networkidle waits and are not pure render times. JS heap samples 4.30–4.66MB.
* Four authored live panels: two geometries/two draw calls each, selected renderer
  submission samples 6.7–15.9ms, sampled JS heap 10,559,496 bytes, paused upload counters
  unchanged while acquisition continues. This is not measured FPS, GPU completion,
  whole-process memory or long-run leak qualification.
* Authored 50,002-identity parse/index: 0.4074s, peak process RSS 82,360KiB. Median search
  times: exact ticker 0.00439ms, 1,000-match prefix 0.02652ms, 50k-match company prefix
  23.14ms (one warmup/five repetitions). Prior local rank-sort observations were
  0.00420/0.467/58.60ms; shared host conditions do not justify a causal speedup guarantee.
  Independent scan/rank results are unchanged. No actual exchange identities were used.

## Visual evidence and reproduction

[Visual QA](PRODUCT_VISUAL_QA.md) lists actual browser screenshot paths/hashes, observed
fixes and limitations. Screenshots contain independently authored financial/market
fixtures. They remain local; binary imagery and generated outputs are not source data.
The manifest binds each capture to its checksum. No proprietary asset was copied.

Existing Codespace update/launch after normal source review:

```bash
git switch feat/atlas-final-release
git pull --ff-only origin feat/atlas-final-release
npm --prefix terminal/web ci
npm --prefix terminal/web run build
# Stop the old task-owned server with Ctrl+C in its terminal first.
bash scripts/start_terminal.sh
```

Keep port8787 **Private** and open its forwarded HTTPS address. This is a deployment
procedure, not an intermediate manual-test request. Existing SEC private configuration
is read by the normal backend; this assignment did not alter it. If initial dependencies
are missing, use the existing `bash scripts/setup_terminal.sh` once. Do not enable Nasdaq
directory/provider/retention gates just to populate empty states.

Developer-only fixture reproduction (never against an owner/observed instance):

```bash
# Validated native wheel/server dependencies and Chromium/Playwright required.
npm --prefix terminal/web run test
npm --prefix terminal/web run build
python terminal/tests/product_fixture_server.py  # loopback18798;authored sources only
# In another terminal,after startup and with no concurrent asset build:
node terminal/tests/product-validation.mjs
node terminal/tests/product-performance.mjs
python terminal/tests/measure_directory.py
python terminal/tests/run_live_market_suite.py
python terminal/tests/run_native_suite.py --expected-tests 274
```

The stable seven-suite runner requires its existing authored native/stock/atlas/atlas2
servers on8787/18787/18788/18789. It checks fixture health before mutations. The separate
live-market fixture uses18797. No test should be aimed at a live operator endpoint.

## Remaining gates and next milestone

1. Establish actual permitted derived-cloud directory use, or independently qualify a
   lawful zero-cost authoritative listing source. Do not equate SEC registrants with it.
2. Use the existing approved identifying SEC configuration for bounded official
   reference/financial reconciliation; verify APLD/CRWV CIKs from that source, preserving
   null until then. No contact value should be pasted into Git or the browser.
3. Qualify actual provider permissions/credentials and venue-limited quotes/trades;
   observed retention stays disabled until permitted. No paid or depth feed is assumed.
4. Qualify this exact candidate on owner-authorized native ARM64/hosted infrastructure;
   historical ARM64 results apply to their tested commits only. No workflow was launched.
5. Complete later independent browser/device, physical GPU, assistive-technology and
   final product acceptance after source prerequisites are satisfied. No intermediate
   owner manual testing was requested here.

Not claimed or silently added: complete historical PIT/XBRL coverage, corrected complete
tape, authoritative halt/session calendar, observed L3 validation, live L2/L3 without
depth rights, calibrated forecast efficacy, production trading operations or deployment.
Full browser lifecycle/security tests do not establish those external properties.
Further speculative panels or a storage/journal rewrite are not justified by this
checkpoint. The next milestone should qualify actual permitted reference sources and
the exact product candidate, not restart completed UI/native engineering.
