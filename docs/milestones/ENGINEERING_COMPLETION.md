# GIG ATLAS: two-milestone engineering assessment

Date: October29,2026 (America/New_York). Baseline local/remote
`8f152b6e9c9a9113158fa15fa6019a3dde46f958`,clean on feat/atlas-final-release.
Validated implementation: `40ca4e86ec4c7c5f339695768605e7453ae4603b`,pushed and remote
verified. Main stayed `12f3a53943dc245e36f2cbbc35b9910fb21c0718`.
Source/qualification implementation was first pushed as8ae381e;the final40ca4e8
checkpoint additionally fixes the manual workflow allowlist. The report/evidence-only
delivery commit follows;no workflow was launched.

## Decisions

**Milestone1: ENGINEERING COMPLETE for the agreed bounded private research contract.**
All essential independently implementable functionality and the final automated gates
listed below passed. This is not a claim that every possible financial product feature,
source profile,market instrument,account,device or production behavior is covered.

**Milestone2: NOT VERIFIED / externally blocked.** No real provider,private Codespaces,
current-candidate ARM64,physical-device or final owner acceptance is claimed here.
The owner reports existing Alpaca Basic Paper credentials and SEC configuration ready
in Codespaces. They are not available in this separate executor;provider domains are
not in its enforced network allowlist and no authenticated Codespaces execution
capability is attached. No forbidden Codespaces attempt or provider retry was made.
The available records also do not resolve Alpaca ticket381230's applicable cloud/
private-display conditions. No permission flag or reference was invented.

The final operational workflow is implemented,not substituted by fixture evidence.
[Runbook](OPERATIONAL_QUALIFICATION_RUNBOOK.md),[gate/blocker matrix](RELEASE_READINESS.md),
[evidence and exact commands](engineering_evidence.json),and
[private final acceptance template](FINAL_ACCEPTANCE_TEMPLATE.json) separate the two milestones.

## Reproduced repairs and minimal changes

1. Historical responses could enter frontend charts with a contradictory ISO/ns clock,
   out-of-window rows,invalid OHLC,or inconsistent page receipt accounting. An authored
   regression failed before repair. `historicalMarket.ts` now checks UTC nanoseconds
   against the provider/native range,exact clock equality,inclusive/exclusive request
   boundaries,positive exact bounded decimals,OHLC relationships,and page/count totals.
   Fixture timestamps were corrected to real authored nanosecond values;no assertion
   was weakened. Nanosecond fractions and invalid calendar/numeric edges are tested.
2. Historical comparison accepted mixed synthetic/observed provenance or duplicate
   symbols. A separate regression failed before repair. Both the Python independent
   reference and actual TypeScript projection now reject differing source identities/
   origins/intervals. The UI gives a scope-specific unavailable explanation. No missing
   price/timestamp is interpolated or relabeled.
3. Standalone historical qualification returned success for an empty source response.
   The original CLI reproduction returned0 despite zero records. It now returns an
   explicit INCONCLUSIVE and nonzero status;fixture output cannot qualify a provider.
   Asset qualification also distinguishes accepted fixture references from observed
   provider evidence without changing browser API contracts.
4. Streaming qualification inherited configured disk capture at construction. A mocked
   constructor-boundary regression reproduced the inherited enable flags. No actual
   observed capture was performed. All qualification workspaces now disable market-data
   and history stores in their own effective environment only. Existing permission
   flags,credentials,private SEC settings and normal application storage contracts are
   preserved. The child comparison process gets only PATH/LANG,not provider keys/contact.
5. One-shot qualification needed to respect a shared free account slot. The helper
   refuses an active gateway and requires explicit window confirmation. A bounded
   retry-budget parameter defaults to the existing5 for production,with1 used by the
   qualification tools. Actual synthetic open-failure tests prove one attempted open,
   cleanup and unchanged default recovery. No live upstream failure was induced.
6. Independent synchronous SEC reconciliation had per-read timeouts but no total body
   deadline. A controlled-clock/response test failed before repair. A25-second body
   deadline now complements existing8-second reads and8MiB bounds. Cleanup/overshoot
   limits are disclosed;no hard wall-clock guarantee or TLS bypass is claimed.
7. The complete browser campaign exposed an obsolete nine-navigation assertion. It now
   requires all12 exact named destinations,keeping every old destination/assertion.
   The new12-workspace matrix performs120 theme/width/navigation checks. No existing
   functional test was removed.

8. Release audit found the manual ARM64 workflow excluded the current ATLAS branch.
   The feature-only allowlist now accepts both existing authorized development branches;
   main,unknown refs and an unconfirmed free-usage input remain rejected. The original
   before-fix failure is preserved. The same3 policy cases passed again in Debug,Release
   and ASan+UBSan;the original six-job matrix,manual trigger,free-runner gate,time limit
   and8 frozen hash checks are unchanged. No main workflow change or dispatch occurred.

New committed tools reuse the real adapters: `qualify_atlas.py` and
`terminal/stocks/qualification.py` run safe readiness,account reference,historical,
independent comparison,SEC and one-shot IEX stages. `check_actual_comparison.mjs` runs
actual frontend calculations against Python Fraction references over exact source
intersections. A missing authoritative AAPL registry entry cannot pass via a curated
fallback;APLD/CRWV mappings remain null unless supplied by the accepted official source.
No provider receipt is inferred from credential presence or public accessibility.

`qualify_atlas_offline.py` builds once,runs23 browser/performance cohorts serially,
hashes production assets between every cohort,and isolates artifacts in its output
workspace. Resume checks retain completed results and failed attempts;no old task
screenshots/logs are overwritten. New diagnostics add no endpoint,dependency,broker,
paid feed,or retention activation.

## Source/functionality audit

The prior full scope/design reports,source access ledger,completion matrix,and current
code were reviewed;historical completion labels were not used as independent proof.
This is a self-reviewed independent-style engineering audit,not a separate external audit.
Tests/oracles below provide independently authored references within their declared scope.

| Area | Actual code path | Engineering status / evidence | Operational boundary |
|---|---|---|---|
| Native C++20,L3/FIFO,replay/journal,simulation,TCA | include/gig + src;terminal/server/engine.py | Preserved;274 consumers/config and8 frozen independent cases | New-candidate ARM64/observed L3 not established |
| Discovery/assets | alpaca_reference.py,market_catalog.py,directory.py,UniverseWorkspace.tsx | Bounded validated provider/private/SEC catalogs,search/filter/cache/recovery;browser AAPL/APLD/CRWV | Actual target accepted/searchable count unknown;not complete US listings |
| Historical market data | alpaca_history.py,HistoricalMarket.tsx,historicalMarket.ts | Bounded exact-source ingestion/clock/receipt checks,graphs and common-time comparisons;Fraction/TS negative controls | Actual AAPL/MSFT reads and provider rights not verified here |
| Streaming | stocks/live.py,live_metrics.py,server/market_events.py,market_delta.py | Shared IEX source,4-or-stricter symbols,ACK lifecycle,ordering/dedup,bounded history,push,backoff/IDLE/freshness;207/config,21 live browser | Observed account/protocol/quiet-session/recovery qualification still open |
| SEC identity/facts/filings | sec_identity.py,sec.py,sec_history.py,vintages.py | Authoritative mapping interface,reported facts,acceptance/amendment safeguards and missingness;SEC browser6+3 and stock cohorts | Existing Codespace config reported ready;not available here;no full PIT/statement claim |
| Financial/ratio UI | FinancialWorkspace.tsx,AlignedStatements.tsx,ratio_history.py | Exact backend descriptors,shared-scale balances,period filters,filing navigation,source/quality disclosures;74 frontend and financial browser cohorts | Selected reported facts,not full presentation-tree XBRL |
| Multi-stock workflows | LiveMarket.tsx,HistoricalMarket.tsx,QuoteCloud.tsx | Search/watchlists/per-symbol panels,limits,pause,common-axis comparison,independent camera controls | Actual subscribed symbols/feeds/entitlements need source evidence |
| Four Level1 + GARCH + eight advanced modes | QuoteCloud.tsx,ModelSurface.tsx,ResearchLab.tsx,research3d.ts | All13 exercised in final browser23;source/binary64/model labels,inspection,cameras,fullscreen,2D/retry | No fabricated L2/L3,aggressor direction,or implied volatility |
| Nine original plus3 new workspaces | App.tsx,ResearchDesk.tsx,StockIntelligence.tsx,MarketHealth.tsx | All12×2 themes×5 widths=120 explicit matrix checks;original journals preserved | Actual owner desktop/Android acceptance remains open |
| Order Book/Depth/Flow | App.tsx,DepthChart.tsx,Landscape3D.tsx,native analytics | Actual native state and capability-aware unavailable flow;browser21+9 controls | Native authored depth is not live equity depth |
| Replay/Execution | NativeSession,ReplayBar,ResearchSummary.tsx | Actual native seek/restart/step/simulation/fills/costs;recording9 and native21 | Simulation only;unknown initialization never completed by assumption |
| Research/validation | models.py,evaluation.py,portfolio.py,ResearchDiagnostics.tsx | HMM/GARCH/Kalman/risk/holdout/dataset controls and authored forecasts labeled;phase4/5/final browsers | No empirical forecasting efficacy claim |
| Persistence | history_store.py,observation_store.py,l2_playback.py | Existing bounded,permission-gated,cold historical recovery;207/274 regression cohorts | Off in new probes;no approved observed retention or hot-live durability claim |
| Security/privacy | request_proofs.py,stream_tickets.py,config.py,auth.py |50 security cases,8 verified local HTTPS/WSS checks;unchanged exact Origin/Host/private-source gates | Actual external authentication/private port requires target evidence |
| Performance/resources | lazy chunks,instanced/batched3D,admission/backpressure limits | Final Chromium measurement and existing bounded algorithms;no added dependency | No physical-GPU/FPS/production SLO certification |
| Build/package | CMake preserved,Python bindings,strict TS/Vite,sdist inventory |74 units,14 installed-wheel,3 packaging;839 safe source members | Existing wheel/native source unchanged;no new hosted build dispatched |

No confirmed unresolved critical/high code defect remains from this campaign. That is
not a proof of absence:source/host/device behavior and optional production extensions
remain explicit. Full exchange master coverage,complete corrected tape,full-taxonomy
XBRL,a historical response warehouse,lossless/exactly-once ingestion,hot crash recovery,
SIP/OPRA/live depth,trading and forecast certification are not silently added to scope.

## Actual final gates

All listed final cohorts had zero failures/errors/skips. Counts are outcomes per
cohort/configuration,not unique tests or coverage percentages. The full final browser
campaign ran from scratch on the last frontend assets and completed without failures.

| Gate | Actual result |
|---|---:|
| Frontend numerical/contracts + strict production build |74/74;build PASS |
| Existing stock/provider/SEC cohort Debug / Release / ASan+UBSan |207 /207 /207 |
| Native-backed terminal cohort Debug / Release / ASan+UBSan |274 /274 /274 |
| New qualification/security/reconciliation cohort Debug / Release / ASan+UBSan |32 /32 /32 |
| Browser functional/layout/recovery checks |353/353 across22 test cohorts |
| Separate browser performance cohort |1 warmup,3 measured repetitions;exit0 |
| Original/new13 visualization modes |Executed,including actual WebGL failure/retry and camera controls |
| Security unit cohort |50/50 |
| Workflow allowlist policy after final workflow-only fix |3/3 each Debug/Release/ASan+UBSan;liveLSan0 |
| Local verified HTTPS/WSS proxy |8/8 |
| Frozen native independent canonical cases |8/8;all8 expected hashes identical |
| Existing installed wheel0.1.1 interfaces/exports |14/14 |
| Packaging pattern regressions |3/3 |
| Clean implementation source distribution |839 safe,intended,byte-identical members |

All three sanitizer cohorts reported LIVE_LSAN_CHECK=0. This checks a live CPython
interpreter,not stock shutdown leak cleanliness. Native C++/bindings,matcher,execution,
TCA and canonical definitions were unchanged;unrelated compiler rebuild matrices were
not repeated. No new hosted/ARM64 run was launched. The existing Starlette/httpx
deprecation and large optional Three chunk warning are retained,not suppressed.

Initial failing-before regressions and first-campaign failures remain hashed. The new
runner initially omitted two legacy stdout formats and an output directory;the tests
had passed until evidence collection failed. It now recognizes those exact formats,
creates isolated paths and retains failed attempts. Successful recorded cohorts were
recovered/reused with original logs. The obsolete9-destination assertion was strengthened.
After the mixed-origin guard changed frontend assets,a completely fresh final campaign
ran all23 cohorts (353 checks plus performance) against a single stable build.

## Measurements and visual evidence

Local x86_64,Python3.12,Node24.19.0,Chromium154/SwiftShader. No actual account/source or
hardware/mobile performance result is inferred.

One browser warmup/three measured cold-context repetitions with cache disabled:
initial navigation+networkidle settle730.8–783.4ms,stock route142.6–252.6ms,
loopback health3.07–12.94ms,sampled JS heap4.53–5.00MB,and1284–1285 DOM nodes.
These include loopback fixture/networkidle work,not pure paint/exchange latency/GPU
completion or sustained leak/production capacity evidence. All numbers are recorded,
not a declared SLA. Three remains deferred on Command Center.

95 actual final-campaign screenshots are inventoried with SHA256s. All use authored
fixtures. Representative artifacts under `build/milestones/browser-final/workspace/`:

- `build/atlas2/visual/financial-trends-dark.png` and financial-statements/filings/replay/
  simulation/operations captures:loaded source-labeled financial/native workflows.
- `build/product/quotes-3d-after-synthetic.png`,comparison/volatility/trades captures,
  and `model-surface-after-synthetic.png`:the four original Level1 modes and GARCH.
- `build/advanced-3d/{height,canyon,events,vwap,flow,wheel,dome,ribbon}-synthetic-desktop.png`:
  all eight new research projections,plus light/dark mobile and authored IEX captures.
- `build/workspaces/`:all12 desktop workspaces and4 mobile/light captures,including
  deliberately captured loading/unavailable states. A cold initial Stock Intelligence
  snapshot is loading evidence,not a screenshot of a completed company refresh.

Representative financial trends,Stock Intelligence loading,and mobile Live Markets
images were visually inspected. No physical Android/GPU,screen-reader certification,
external Codespace authentication or final owner aesthetic acceptance is claimed.
Raw market data,secrets and screenshots were not committed. Artifacts are local ignored
files;the committed manifest provides hashes and command/source traceability.

## Operational result and next action

The new command's local default and explicit-execute/fail-closed paths were exercised.
Actual result: INCOMPLETE_OR_BLOCKED_SOURCE_QUALIFICATION;Alpaca permissions/credentials,
SEC configuration,and existing live gate unavailable in this executor. **Zero provider
requests** were made. The13 fallback identities are not a measured Codespace catalog
count. No real AAPL historical data,IEX stream,SEC mapping or observed comparison was
claimed. No forbidden Codespaces access was retried.

Proceed only through the [final Codespace source/target runbook](OPERATIONAL_QUALIFICATION_RUNBOOK.md)
when the specific provider-use record and free account window exist. The software
campaign is complete;this is the remaining external source/environment/final acceptance
phase. A source CLI exit0 cannot close Milestone2 by itself.
