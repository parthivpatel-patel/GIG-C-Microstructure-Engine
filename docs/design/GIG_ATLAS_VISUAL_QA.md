# GIG ATLAS visual and interaction QA

Actual application:real ASGI server/native extension plus independently authored local
financial source fixtures. No observed SEC/Alpaca data or restricted dataset is used.
Screenshots of named companies with fixture amounts are SYNTHETIC TEST EVIDENCE,not
company financial statements. Test server hardcodes loopback and never calls upstream.

## Executed review

Headless Chromium154 with SwiftShader and America/New_York display timezone. Native/browser transport,company routing,v2
ratios/source fields,reported trends/exact tables,period exclusions,filing amendments,
stale/error handling,themes,keyboard skip/help and layout tests execute actual pages.
All360/390/768/1280/1920 widths are checked;the cross-workspace matrix covers all nine
persistent workspaces at these widths. Internal table scrolling is intentional;
horizontal document overflow is rejected. Token text/link contrast must be≥4.5:1 in
both themes. These bounded checks do not amount to full WCAG compliance.

Visual review found and corrected inherited vertical stock tabs,an overly long combined
financial page,and duplicate local search occupying prime screen area. The focused views
and search/watchlist expander preserve access while making financial research easier to
scan. Exact values/formulas/source receipt disclosures remain one action away.

## Capture locations

Ignored workspace artifacts under `build/atlas/visual/`:

* financial-viewport-1280.png — actual desktop first viewport.
* financial-viewport-390.png — actual mobile viewport emulation.
* financial-dark-{360,390,768,1280,1920}.png — full-page financial summaries.
* financial-ratios-dark.png — all twelve backend descriptors.
* financial-trends-dark.png — reported-history charts.
* financial-light-1280.png — light theme.
* results.json — checks,counts,layout/DOM observations and actual browser version.

Native/replay/3D/simulation captures and timing observations are separately under
`build/atlas/native-browser/`. Captures remain local rather than adding binary imagery
or market data to Git. Their hashes are in `gig_atlas_evidence.json` for review integrity.
A source-only clone can reproduce the captures with the following local fixture setup:

```bash
npm --prefix terminal/web ci
npm --prefix terminal/web run build
# In a terminal with the validated native wheel and server requirements installed:
python terminal/tests/atlas_fixture_server.py
# Separate terminal,after installing existing terminal/tests development dependencies:
node terminal/tests/atlas-validation.mjs
```

The fixture server is18788 on127.0.0.1;it is not an owner live server. Browser checks
require installed Chromium/Playwright. Existing general regression scripts use dedicated
8787/18787 fixture instances. Never run fixture mutation scripts against an observed or
operator live instance;the health safety guard must pass first.

## Exceptions

No physical Android,screen-reader,external Codespaces authentication or real GPU review.
SVG/3D graph positions are approximate projections,not monetary calculations. Native
3D colors and some legacy diagnostic controls need further light-theme/accessibility
review. Full keyboard manipulation of3D graphics is not claimed;exact tables/fallbacks
remain available. Ratio history cannot be visualized until supplied by a versioned
backend contract. The task does not prove forecast accuracy or real L3 initialization.

A global/local company-selection bridge regression was reproduced during implementation:
local NVDA followed by global AAPL could retain NVDA when the parent symbol was already
AAPL. An explicit selection revision now delivers each user intent;the browser regression
verifies the selected company changes. This was caught before the delivery commit.


Phase 2 recovery: see [Phase 2 report](GIG_ATLAS_PHASE2_REPORT.md) and
`gig_atlas_phase2_evidence.json` for current refinements,stable-build browser checks,
viewport screenshots,performance observations and remaining accessibility limits.


Current expanded product:see [product visual QA](../product/PRODUCT_VISUAL_QA.md).
The executed cross-workspace matrix is now12 workspaces,60 width combinations and
120 dark/light combinations. It preserves the original assertions while moving native
controls to their dedicated pages. New screenshots/ordinary-click interactions and
limitations supersede the old nine-workspace description above;historical captures
are preserved.
