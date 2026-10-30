# Prioritized readiness findings

Source `10eaee30d598807a23e42a8b60abe3d5a5dc2514`. Findings describe actual defects, qualification gaps, external blockers,
and explicitly optional enhancements separately. No production modification was made.
**P0: 0; P1: 3; P2: 13; P3: 3.**
No P0 was established by this bounded audit; this is not proof no vulnerabilities exist.
The three P1 items block the requested complete operational product; they do not imply
SEC selected-fact/private synthetic research is unusable. Permissions are not defects.
Exact source line ranges refer to the audited commit. JSON companion: [findings.json](findings.json).

## A01 — P1 — Core live-equities workflow remains permission-blocked

**Classification:** External qualification blocker, not a software defect.

- **Evidence / affected components:** terminal/stocks/service.py:101–117; terminal/stocks/live.py:66–78, 156–158; owner current audit directive §9.
- **Impact:** Quotes/trades/catalog/history adapters cannot establish a working observed-market release while authorization remains intentionally disabled.
- **Reproduction / verification:** Source inspection and gate-denial fixtures; no Alpaca request was made.
- **Proposed remediation:** Keep gates disabled; obtain the specific private/cloud/display/feed permission decision and bind a subsequent authorized qualification to its source SHA.
- **Measurable acceptance:** After separate authorization:actual asset import count, one bounded AAPL historical query, shared IEX multistock/subscription/quiet/reconnect checks with source timestamps; no orders, paid feeds or retention.
- **Dependencies / risks:** Provider permission; existing credentials stay private; account-wide free allowance; owner-controlled target.
- **Relative effort:** Engineering small; external duration unknown.


## A02 — P1 — Broad listing-universe acceptance is not established

**Classification:** External source-coverage blocker; discovery infrastructure exists.

- **Evidence / affected components:** terminal/stocks/directory.py:1–57, 98–113; terminal/stocks/discovery.py:4–15; terminal/stocks/alpaca_reference.py:75–135; H04:52–94; H07:71–112.
- **Impact:** 10429 SEC registrant mappings do not prove all supported exchange listings, share classes, ETFs, delisted status or entitlement. Broad search is implemented, not qualified complete.
- **Reproduction / verification:** Inspect exact-source union and UNVERIFIED/NOT_ESTABLISHED_BY_SEC_TICKER_MAPPING classifications; no live import attempted.
- **Proposed remediation:** Accept a permitted authoritative listing snapshot with source-specific scope, exclusion counts, identity collisions, classification and freshness; keep SEC identity separate.
- **Measurable acceptance:** Reconcile accepted+excluded to source row totals; test target classes and AAPL/APLD/CRWV; show actual imported count and explicit coverage boundaries, not a complete-US claim from SEC alone.
- **Dependencies / risks:** Lawful official listing/asset source approval and snapshot; no paid subscription authorized.
- **Relative effort:** Small/medium implementation follow-through; external acquisition unknown.


## A03 — P1 — Exact-candidate private-target acceptance remains open

**Classification:** Verification gap, not renewed SEC configuration failure.

- **Evidence / affected components:** terminal/server/config.py:6–23; terminal/server/__main__.py:8–19; docs/overnight/MORNING_ACCEPTANCE.md:1–74; owner October 30 SEC evidence in H01 §8.
- **Impact:** Local proofs/TLS fixtures do not certify current GitHub authentication, phone browser behavior or the exact candidate that produced the successful SEC report.
- **Reproduction / verification:** Current audit never enters or mutates owner Codespace. Existing owner report lacks tested SHA/report hash in supplied evidence.
- **Proposed remediation:** Bind already-produced SEC results to tested SHA/time/hash; perform final target acceptance once the release owner authorizes that phase. Do not repeat SEC setup.
- **Measurable acceptance:** Private port only; working HTTP mutation+WS/SSE, replay and reconnect; AAPL/APLD/CRWV identity evidence, 1772-record selected-scope report attached to source identity; explicit pass/fail per workflow.
- **Dependencies / risks:** Owner target/environment; existing saved SEC evidence; subsequent final acceptance, not intermediate implementation testing.
- **Relative effort:** Small evidence binding; medium target acceptance.


## A04 — P2 — Valid option inputs rejected by derived scenario grid

**Classification:** Confirmed reproducible boundary-contract defect.

- **Evidence / affected components:** terminal/stocks/options.py:17–26, 39–53; terminal/server/app.py:643–649; evidence/options-boundary.json.
- **Impact:** The public scenario endpoint rejects base inputs accepted by its own price function because generated strikes leave the price-domain bounds. Ordinary AAPL-scale inputs are not shown broken.
- **Reproduction / verification:** spot=strike=1e-6 or1e7, years=1, volatility=.2:price succeeds; scenario raises model_parameter; HTTP422. spot=strike=100 returns200/153 cells. Native canonical unchanged.
- **Proposed remediation:** Specify one consistent endpoint domain; generate an admissible bounded grid or explicitly return a partial/omitted auxiliary surface while preserving valid metrics. Do not silently clip monetary inputs.
- **Measurable acceptance:** New endpoint/function boundary tests at minimum/maximum and adjacent admissible values; ordinary153-cell output unchanged; all Greeks finite; invalid inputs still rejected; no native state mutation.
- **Dependencies / risks:** Separately authorized minimal repair phase; no provider access required.
- **Relative effort:** Small.


## A05 — P2 — Point-in-time and statements remain selected retained-data views

**Classification:** Research/coverage limitation, not a demonstrated leak in current filters.

- **Evidence / affected components:** terminal/stocks/sec.py:79–127; terminal/stocks/sec_history.py:4, 21–54; terminal/stocks/vintages.py:26–58; terminal/stocks/financials.py:1–89.
- **Impact:** Latest companyfacts plus bounded retained revisions cannot prove an old response or complete filing presentation. Selected facts/acceptance filtering must not become a survivorship-safe backtest dataset.
- **Reproduction / verification:** Inspect max2 advertised shards, 1024 filings, revision truncation flags and PARTIAL_RETAINED_CACHE_NOT_AUTHENTICATED_SOURCE_VINTAGE output.
- **Proposed remediation:** Preserve exclusions and labels. If full historical finance is an agreed next scope, design authenticated original-vintage ingestion, dimensions/presentation, coverage and publication-time contract first.
- **Measurable acceptance:** Independent accession/acceptance cutoff tests including same-time ambiguity, amendments and missing acceptance; complete-vintage claims require original timestamped source artifacts and declared taxonomy coverage.
- **Dependencies / risks:** Authorized historical SEC source coverage and explicit expanded research contract.
- **Relative effort:** Large for complete XBRL/PIT; small for scope acceptance.


## A06 — P2 — Observed historical L3 correctness is unqualified

**Classification:** External initialization/reference dependency.

- **Evidence / affected components:** include/gig/replay/replay.hpp:6–20; docs/NASDAQ_SECOND_PREFIX_INSPECTION.md:1–23; docs/LOBSTER_EMPIRICAL_RECONSTRUCTION.md:1–24; src/itch/reconstruction.cpp.
- **Impact:** Small real ITCH prefixes establish decoded-frame compatibility only. Five-level aggregate snapshots cannot establish queue identities or complete historical L3 state.
- **Reproduction / verification:** Historical report labels observed-prefix PASS/incomplete-session INCONCLUSIVE; LOBSTER empirical counts null and cloud processing forbidden.
- **Proposed remediation:** Keep synthetic/known-subset claims. A future separately authorized pilot needs valid complete starting evidence, source completeness and independent observed comparison denominator.
- **Measurable acceptance:** Authenticated empty/complete seed boundary; complete transitions; source counts and hashes; independent orders/FIFO/depth comparisons after every eligible event; unknown initialization blocks full claims.
- **Dependencies / risks:** Data rights/resources and observed reference. Do not inspect private LOBSTER ZIP or download more data in this audit.
- **Relative effort:** Large study; external dependency.


## A07 — P2 — Model calibration and economic validity are not established

**Classification:** Research qualification gap; mathematical implementations exist.

- **Evidence / affected components:** terminal/stocks/models.py:31–66, 76–109; terminal/stocks/advanced_models.py:5–30; terminal/stocks/evaluation.py:6–37; terminal/stocks/research.py:11–29.
- **Impact:** Local EM optimum, bounded GARCH search, caller-declared chronology and short holdouts are not predictive significance, robust strategy returns or causality. Whole-sample fit parameters cause estimation look-ahead if reused historically.
- **Reproduction / verification:** Inspect explicit warnings, finite candidate search, maximum4 folds and fixed-parameter demo contracts; no observed predictive claim is reproduced.
- **Proposed remediation:** Keep demo/offline labels. Specify lawful aligned sample, baseline, residual diagnostics, selection protocol, costs and uncertainty before promoting any model.
- **Measurable acceptance:** Train-only fitting; authentic chronology/corporate actions/universe; untouched held-out interval; baseline and residual/coverage diagnostics; report unsuccessful findings without tuning test data.
- **Dependencies / risks:** Observed PIT data and predeclared model study; not authorization to add unrelated ML.
- **Relative effort:** Medium/large research qualification.


## A08 — P2 — Journal is bounded but still expensive for long research sessions

**Classification:** Measured scalability limitation.

- **Evidence / affected components:** include/gig/replay/replay.hpp:19, 59–63, 89–94; src/replay/replay.cpp:49, 113–127; docs/PHASE5_ENGINEERING_REPORT.md:69–89; docs/overnight/OVERNIGHT_COMPLETION_REPORT.md:178–191.
- **Impact:** 100000 ordinary12232-byte records imply1223200000bytes element payload per book before slack, orders, context and transient allocations. Two books can exceed modest research RAM.
- **Reproduction / verification:** Retained controlled4096/no-reset measurement:50102688 live PMR, 75153824 peak; 50744KiB child RSS in recent probe. No allocator-leak finding; all tracked memory released.
- **Proposed remediation:** First enforce a measured session budget and explicit capacity failure. Any separate optimization needs owned-event equivalence, migration/failure-atomicity design and benchmark gate.
- **Measurable acceptance:** Measure representative lengths/reset mixtures, peak coexistence and per-book budgets; forced exhaustion must preserve accepted prefix; all 8 hashes and restart equivalence unchanged.
- **Dependencies / risks:** Representative lawful workload and separately approved optimization; do not repeat the completed Phase5 split merely to claim progress.
- **Relative effort:** Medium design/benchmark; potentially large redesign.


## A09 — P2 — Sustained streaming/endurance and complete local telemetry are unqualified

**Classification:** Operational verification and instrumentation gap.

- **Evidence / affected components:** terminal/stocks/live.py:144–158, 193–215; terminal/server/market_events.py:8–33, 40–52; terminal/server/analysis.py:4–37; docs/overnight/OVERNIGHT_COMPLETION_REPORT.md:159–177.
- **Impact:** Bounded queues, deadlines and latest-state coalescing exist; short fixture timings do not establish sustained CPU/RSS/connection behavior. Upstream queue_depth explicitly NOT_INSTRUMENTED.
- **Reproduction / verification:** Inspect diagnostics and short repetitions. No hang, unbounded per-client backlog or current leak is confirmed.
- **Proposed remediation:** Define bounded private-research endurance profile and local metrics; retain UNKNOWN for source losses without exchange sequence. Distinguish transport age from unsynchronized clock latency.
- **Measurable acceptance:** Declared-duration burst/quiet/reconnect/slow-reader/cancel/shutdown campaign with peak RSS, local backlog, worker count, drop/coalesce counters and recovered generations; stable memory after warmup within declared budget.
- **Dependencies / risks:** Offline soak possible after authorized engineering; observed phase awaits provider permission.
- **Relative effort:** Medium.


## A10 — P2 — Full runtime and transitive dependency clearance remains unresolved

**Classification:** Security qualification gap; no new exploitable vulnerability established.

- **Evidence / affected components:** docs/SECURITY_RESIDUAL_RISKS.md:3–29; terminal/server/requirements.txt:1–21; terminal/web/package-lock.json; .github/workflows/ci.yml:16–18.
- **Impact:** Direct package scans/pins and a pinned checkout action do not close managed interpreter, TLS, Expat, host or bundled-action advisories on actual deployment.
- **Reproduction / verification:** Existing register explicitly says unresolved vendor/backport/feature mapping and no accepted residual risks. Current Codex OS is not automatically owner Codespace OS.
- **Proposed remediation:** Reconcile deployed SBOM/runtime identities and vendor patches/reachability; document exclusions or remediation rather than blindly upgrading managed platform components.
- **Measurable acceptance:** Dated actual-target versions/advisory mapping, reachable-feature evidence, clean relevant regression after changes, explicit owner residual-risk decision if needed.
- **Dependencies / risks:** Actual deployment inventory and vendor evidence; no credential disclosure or intrusive external testing.
- **Relative effort:** Medium.


## A11 — P2 — Current-candidate hosted/native ARM64 evidence is absent

**Classification:** External execution/attestation gap.

- **Evidence / affected components:** .github/workflows/atlas-native-arm64.yml:1–25, 63–78; .github/workflows/ci.yml:1–18, 44–78; docs/overnight/overnight_evidence.json:assessment; docs/PHASE13_NATIVE_ARM64_VALIDATION.md.
- **Impact:** Historical native ARM64 pass applies to its tested SHA, not current Python/frontend/model changes. Local x86_64 tests cannot certify current native ARM64 behavior.
- **Reproduction / verification:** Inspect manual-only/free_usage_verified/feature guard and retained current_candidate_ARM64 NOT_EXECUTED. No workflow was dispatched or API evidence claimed in audit.
- **Proposed remediation:** After owner authorization and free eligibility verification, qualify exact candidate and export immutable run/job/compiler/architecture/hash receipts.
- **Measurable acceptance:** Six actual native ARM64 configurations pass at recorded SHA, all 8 hashes match and relevant Python/wheel/source tests pass; no claim until actual hosted evidence.
- **Dependencies / risks:** Owner-controlled eligible free infrastructure and run authorization.
- **Relative effort:** Small preparation; external run.


## A12 — P2 — Formal accessibility and physical-device acceptance remain partial

**Classification:** Target verification gap.

- **Evidence / affected components:** terminal/web/src/App.tsx:40–60; terminal/web/src/ResearchScene.tsx:10–35; terminal/web/src/QuoteCloud.tsx:9–23; terminal/tests/mobile-camera-validation.mjs; docs/overnight/REMAINING_GAPS.md.
- **Impact:** Keyboard/viewport/reduced-motion/fallback fixtures and retained screenshots do not certify Android GPU/touch, screen-reader semantics or WCAG2.2AA.
- **Reproduction / verification:** Retained Chromium/SwiftShader/emulated-touch scope; inspect reviewed mobile screenshots. Colorblind quote palette and independent controls are implemented, not missing.
- **Proposed remediation:** Perform scoped accessible journey/contrast/screen-reader and physical-device verification after code acceptance; record exceptions and actionable defects.
- **Measurable acceptance:** Named browser/device/assistive tech, ordinary clicks/focus/touch, 360/390px no page overflow, chart alternatives, context-loss fallback and measured frame behavior.
- **Dependencies / risks:** Actual devices and assistive technology; no intermediate owner test requested by this audit.
- **Relative effort:** Medium qualification.


## A13 — P2 — Evidence is consistent but not a portable independent qualification bundle

**Classification:** Reproducibility/attestation limitation.

- **Evidence / affected components:** docs/overnight/overnight_evidence.json:production_sources, logs, screenshot_inventory; evidence/prior-receipts.json; docs/overnight/OVERNIGHT_COMPLETION_REPORT.md:195–223.
- **Impact:** 232 local receipts match, but ignored build artifacts may vanish with the workspace. Hash consistency is not a signed or independent observed-provider attestation.
- **Reproduction / verification:** Current audit rehashed232 retained source/document/log/image receipts:0 missing/0 mismatch. No claim that every historical run was rerun.
- **Proposed remediation:** Produce a privacy-reviewed version-bound export of required logs and summaries to an owner-approved durable private location; do not add raw datasets/secrets to Git.
- **Measurable acceptance:** A clean independently authorized machine can verify artifact inventory/bytes/hashes, source SHA, commands/toolchains/results; owner supplied SEC/hosted evidence clearly distinguished.
- **Dependencies / risks:** Owner-controlled durable private artifact destination if desired; no paid resource required.
- **Relative effort:** Small/medium.


## A14 — P2 — Production restart objectives/global resource envelope are not qualified

**Classification:** Institutional operations gap, not missing SQLite transaction safety.

- **Evidence / affected components:** terminal/stocks/observation_store.py:5–51; terminal/stocks/history_backup.py:7–34, 37–79; terminal/server/__main__.py:17–19; terminal/server/analysis.py:18–37.
- **Impact:** Private ledgers have physical/page/logical bounds and secure_delete; history backup exists. These do not prove end-to-end production RPO/RTO, global disk quota or hard-preemptive compute deadlines.
- **Reproduction / verification:** Source review confirms32 MiB SQLite cap plus rollback-journal/transient space, 16 MiB observation payload, 10000 row trim. No false claim that these limits are missing.
- **Proposed remediation:** Document acceptable research restart loss, backup expiry and rollback/drain objectives; test actual process interruption and disk/worker exhaustion. Do not redesign into a lossless exchange tape without scope.
- **Measurable acceptance:** Crash/reopen/hash-corruption/expiry/disk-budget drills plus authenticated source restart; published worst-case staging space; fail closed without partial accepted state; document residual loss.
- **Dependencies / risks:** Deployment target disk/process model; observed retention remains forbidden until separately permitted.
- **Relative effort:** Medium.


## A15 — P3 — Some risk/model summaries expose excessive floating-point precision

**Classification:** Confirmed user-facing presentation gap.

- **Evidence / affected components:** terminal/web/src/PortfolioLab.tsx:7; terminal/web/src/ResearchDiagnostics.tsx:23–26; reviewed retained atlas5/visual/research-mobile-dark.png.
- **Impact:** Raw Gaussian ES, likelihood/variance and covariance ratios are difficult to interpret and imply more useful precision than warranted. This is not a reproduced numerical calculation error.
- **Reproduction / verification:** Render authored portfolio research result; source directly interpolates result.gaussian_es. Screenshot and JSX agree. Held-out score toFixed4 already exists, so formatting is inconsistent rather than universally absent.
- **Proposed remediation:** Use a shared unit-aware significant-digit formatter in summary cards; retain exact/fullprecision values under details and preserve null/missing reasons.
- **Measurable acceptance:** Tests for tiny values, zero, negative/nonfinite/missing, units and exact expandable evidence; ordinary mobile summary stays readable.
- **Dependencies / risks:** Authorized presentation repair; no financial recomputation in JS.
- **Relative effort:** Small.


## A16 — P3 — Historical model documentation can be mistaken for current status

**Classification:** Documentation maintainability gap.

- **Evidence / affected components:** docs/backend/QUANT_MODEL_VALIDATION.md:11–18; terminal/stocks/portfolio.py:12–56; terminal/stocks/models.py:31–109; docs/overnight/QUANTITATIVE_CONTRACTS.md.
- **Impact:** Older report says portfolio NOT IMPLEMENTED and no fitted HMM/GARCH, while later code implements bounded research fits and explicit-weight portfolio analysis.
- **Reproduction / verification:** Compare historical table with current source; do not treat that table as proof code is missing.
- **Proposed remediation:** Keep historical evidence; add prominent snapshot date/supersession links and one current status index.
- **Measurable acceptance:** Readers can identify source SHA/date and current replacement from each historical model report; no history deletion or retroactive evidence rewrite.
- **Dependencies / risks:** Documentation-only follow-up.
- **Relative effort:** Small.


## A17 — P3 — IV solver lacks exposed conditioning/error diagnostics

**Classification:** Optional research robustness extension, not a confirmed wrong price.

- **Evidence / affected components:** terminal/stocks/options.py:28–37, 52–53; terminal/stocks/test_workspace.py:92–111.
- **Impact:** 100-step bounded bisection and strict bracket rejection exist, but a user cannot inspect residual, vega sensitivity or identifiability near a flat price/volatility curve.
- **Reproduction / verification:** Inspect return of single scalar after fixed iterations. No observed options or ordinary-input solver error demonstrated.
- **Proposed remediation:** Optional structured residual/bracket-width/conditioning diagnostics; retain current explicit rejection semantics and European-model limitations.
- **Measurable acceptance:** Independent repricing residual plus deep ITM/OTM/short-tenor cases, ill-conditioning classification and backward compatibility.
- **Dependencies / risks:** Separately accepted enhancement, not permission to fetch options.
- **Relative effort:** Small.


## A18 — P2 — Universal original-requirement closure cannot be certified

**Classification:** Requirements evidence gap.

- **Evidence / affected components:** H08 original master attachment retrieval failed; docs/ARCHITECTURE.md:1–80; docs/completion/DEVELOPMENT_SCOPE_AUDIT.md; H04:6–21; H06:806–822.
- **Impact:** Recoverable 176-row matrix is substantial but is not a universal original-spec denominator. Prior self-authored bounded completion cannot silently erase broader approved requirements.
- **Reproduction / verification:** Six historical directives recovered and fingerprinted; earliest complete C++ master could not be authorized/resolved. This is UNKNOWN, not inferred complete.
- **Proposed remediation:** Recover original approved text or obtain explicit acceptance of a reconstructed baseline and exclusions; retain current scope evidence in this audit.
- **Measurable acceptance:** Each mandatory original requirement has owner/source provenance, code, test and acceptance mapping; unknowns resolved explicitly rather than counted as passes.
- **Dependencies / risks:** Original requirements archive or owner scope decision at final acceptance.
- **Relative effort:** Small/medium reconciliation; external evidence.


## A19 — P2 — Explicit liquidity-concentration requirement has no implemented estimator

**Classification:** Missing recoverable requirement.

- **Evidence / affected components:** H02 original unified directive:542–553; include/gig/analytics/book_metrics.hpp:19–30; src/analytics/book_metrics.cpp:22–44; terminal/server/engine.py:154–217.
- **Impact:** Cumulative quantities, depth imbalance and liquidity geometry are implemented, but none is an explicitly defined or exposed liquidity-concentration statistic. Passing geometry tests cannot close this separate original requirement.
- **Reproduction / verification:** Review BookMetric enumeration and emitted native metrics; targeted search for concentration/Herfindahl/HHI in include, src, server, stocks and frontend found no estimator. No observation or source identity is needed for an authored test.
- **Proposed remediation:** In a separately authorized repair phase, define a bounded supplied-depth concentration contract or obtain explicit deferral. A possible concentration formula must be specified and independently validated, not silently chosen during this audit.
- **Measurable acceptance:** Document formula/depth/units and truncated-data scope; independent authored concentrated/equal-volume/empty/one-sided/overflow examples; versioned backend field and accessible UI explanation; unchanged original hashes unless justified.
- **Dependencies / risks:** Accepted mathematical contract; no live feed necessary. Never imply full-market concentration from IEX L1 or partial depth.
- **Relative effort:** Small/medium.
