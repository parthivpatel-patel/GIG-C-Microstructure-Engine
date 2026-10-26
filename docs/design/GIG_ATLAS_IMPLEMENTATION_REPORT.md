# GIG ATLAS implementation report

## Executive assessment and baseline

Implemented an integrated shared shell and substantial Stock Intelligence redesign,
using backend checkpoint805294762f55efbbeb6fd988f7b8d842eb474654 on
feat/bootstrap-cpp20-engine. Starting local/remote HEAD matched and working tree was
clean. Main12f3a53943dc245e36f2cbbc35b9910fb21c0718 is preserved. No C++20,backend,
provider gate or canonical fixture implementation changed.

Initial audit:financial facts were plain paragraphs,ratios largely hidden in JSON,
v2 unused,native and stock navigation fragmented,and source setup dominated research.
The implementation adds restrained dark/light tokens,global search,accessible shell,
focused financial views,readable exact-value cards,lightweight SVG trends,v2 ratios and
filings,source/freshness indicators,simulation tables and model diagnostic cards.
No external chart framework,font service or paid infrastructure was added.

Verified implementation checkpoint: `895e34f9cad6d0da4adf68e1a5f7a0b7a4f9d174`,
pushed and remotely verified. A subsequent documentation/evidence commit records
package closure;its exact SHA is in Git and the final delivery response.

## Delivery by phase

| Phase | Implemented | Remaining |
|---|---|---|
|A|Baseline/source/schema/UI audit and architecture|Full independent product research with actual users|
|B|Themes,tokens,shell,search,focus/help/navigation|Complete replacement of legacy component CSS|
|C|Stock summary/trends/statements/ratios,v2 contracts,filings|Backend ratio histories,older SEC shards,multipage explorer|
|D|Command Center shortcuts,native simulation tables,model summaries,shared native workspace treatment|Bespoke redesign of every microstructure/operations control|
|E|Five-width responsive layout,contrast tokens,skip link,dialog,focus,chart/table alternatives|Physical Android,screen reader,full WCAG2.2 AA audit|
|F|Actual Chromium/native/API integration,negative cases,regressions and screenshots|External authenticated Codespaces owner acceptance,new-HEAD hosted qualification|

## Backend compatibility and financial integrity

V1 consumers/protected mutations remain intact. Company identity,source classification,
cache age and latest cached filing date are visible. The twelve descriptors come from
actual v2 data,not independent JavaScript formulas. Missing means unavailable,not zero.
Compact display rounds with BigInt arithmetic and exposes exact values. Filing references
remain official links;no generated interpretation or AI filing summaries are added.
Actual SEC source reconciliation remains blocked in Codex;authored fixtures do not
establish real-market correctness. Alpaca support381230 remains pending;no gates changed.
Restricted LOBSTER data was not accessed. Native source and eight frozen identities remain.

## Tests and evidence

Exact commands,outcomes,source/tree hashes and screenshot identities are recorded in
`gig_atlas_evidence.json`. Fresh runs include frontend build/unit tests,the expanded
274-case terminal cohort in installed Release,Debug binding and ASan/UBSan binding,
46 strict security tests,8 TLS/WSS checks,8 native canonical references,existing native
and stock/replay/live-control browser regressions,and the new ATLAS browser suite.
|Fresh check|Pass / fail / skip|
|---|---|
|Frontend pure unit tests(existing4+new7)|11 /0 /0|
|ATLAS browser(includes45 workspace/viewport combinations)|21 /0 /0|
|Existing native application/3D/replay/simulation browser|21 /0 /0|
|Existing configured stock browser|9 /0 /0|
|Existing unavailable stock/model browser|10 /0 /0|
|Existing recorded replay browser|9 /0 /0|
|Existing authored live-control browser|9 /0 /0|
|Terminal installed Release native consumer|274 /0 /0|
|Terminal Debug native consumer|274 /0 /0|
|Terminal ASan/UBSan native consumer|274 /0 /0|
|Strict security|46 /0 /0|
|Local TLS/rewritten HTTPS/WSS|8 /0 /0|
|Fresh frozen canonical reference checks|8 /0 /0|
|Installed wheel interface/export checks|8+6 /0 /0|
|Packaging patterns|3 /0 /0|
|Safe intended byte-identical source-archive members|604 /0 /0|
|Browser wait/safety guard controls|5 /0 /0|

Representative commands from the repository root:

```bash
npm --prefix terminal/web test
npm --prefix terminal/web run build
node terminal/tests/atlas-validation.mjs
python terminal/tests/run_native_suite.py --expected-tests 274
python -m unittest terminal.test_request_proof terminal.test_stream_proof terminal.test_browser_access terminal.test_codespaces_origin
```

Use the isolated fixture servers and configured native-binding/sanitizer environments
recorded in the evidence;do not run mutation browser scripts on an observed/live instance.

Full six155-test native matrices were not repeated because all native source/build/
fixtures are unchanged;their baseline evidence remains distinct from fresh8 checks.
The live sanitizer cohort reports LIVE_LSAN_CHECK=0;full interpreter-finalization
qualification is not implied. No warning/sanitizer/test was disabled.

Visual review found inherited vertical stock tabs and excessive financial-page scrolling;
both were repaired. Focused Summary/Trends/Statements/Ratios cut the representative
active financial-summary DOM from the initial1012-node combined view to roughly260
nodes(measured exact counts in evidence). This is a view-structure comparison,not a
universal performance gain. Three.js still dominates the approximately780kB minified JS
bundle;the existing>500kB build warning remains and is not suppressed. No tail-latency,
physical-mobile,GPU or production responsiveness claim is made.

Two existing stock browser assertions were updated to verify the redesigned compact
Revenue card plus its unchanged exact100 USD detail,and the filing table's amendment/
official-source links. Their original semantics and scenario counts are preserved;
local search is now explicitly expanded before use. Tests were not removed.

## Known limitations and next20 priorities

1. Owner private Codespaces acceptance of exact delivered HEAD.
2. Physical Android touch/rotation/font-size review.
3. Screen-reader and complete WCAG2.2 AA audit,including legacy charts.
4. Lazy-load optional Three.js workspaces with measured download/CPU baselines.
5. Measure sustained browser heap/render profiles,not just DOM and load observations.
6. Review all legacy light-theme colors,canvas contrast and color-independent encoding.
7. Add keyboard chart-point inspection beyond exact accessible tables.
8. Improve financial-period taxonomy only when authoritative backend contexts permit.
9. Add backend ratio histories before drawing ratio trends.
10. Add filing page navigation using explicit bounded cached pagination.
11. Independent official SEC statement/selected-fact reconciliation.
12. Historical original point-in-time financial revision policy/warehouse.
13. Paired assets/liabilities chart with explicit shared scale and units.
14. Richer selected-statement comparison/export after rights/provenance review.
15. Complete reusable component consolidation without changing existing contracts.
16. More detailed native execution lifecycle and TCA explanatory views.
17. Dedicated source/model/recording inventory cards in Operations.
18. Provider authorization,current schema/delay/retention qualification before live use.
19. Exact-new-HEAD owner-authorized ARM64/hosted evidence(no dispatch here).
20. Independent usability/research workflow acceptance before institutional-readiness claims.

## Codespaces update and launch

Stop the existing server with Ctrl+C,then use the existing clean feature checkout:

```bash
git switch feat/bootstrap-cpp20-engine
git pull --ff-only
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

Build the frontend explicitly before starting;start_terminal.sh checks prerequisites
and launches the server with the real native binding. It does not rebuild assets. Keep8787 PRIVATE
in Ports and Open in Browser using its authenticated HTTPS forwarded URL. Hard-refresh
Chrome if an older bundle is cached. Use the theme button and global company search;
Financials opens focused views. Existing server-side provider permissions are not granted
by this update. Do not paste credentials into browser/chat or make the port public.
No externally authenticated browser URL was independently exercised by this task.

Overall:working private research terminal improvement with tested native continuity,
not certification of institutional/production readiness or observed-market accuracy.
Exact source/evidence commits and final remote verification are recorded in delivery.

A global/local company-selection bridge regression was reproduced during implementation:
local NVDA followed by global AAPL could retain NVDA when the parent symbol was already
AAPL. An explicit selection revision now delivers each user intent;the browser regression
verifies the selected company changes. This was caught before the delivery commit.
