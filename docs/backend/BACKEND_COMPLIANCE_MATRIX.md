# Backend implementation and evidence matrix

Assessment date: October25,2026 America/New_York. Baseline feature commit
`f991c813749ad4c54e99943c51d7b1294f0cda20`. This is a bounded source-level
assessment, not certification or a claim about any firm's proprietary systems.
Status describes implementation within the stated scope; empirical evidence is
separate. Execution details are in FINAL_BACKEND_ENGINEERING_REPORT.md and the
machine-readable evidence manifest.

| Workstream/capability | Status | Source and executed tests | Evidence, limitation and next action |
|---|---|---|---|
| A inventory | COMPLETE | This matrix; server route inventory in BACKEND_ARCHITECTURE.md | Covers requested domains; not a line-by-line proof of the entire repository |
| B strong types/exact arithmetic | COMPLETE | include/gig/core/numeric.hpp, analytics/exact.hpp; native155-case suites | Six local compiler/configuration suites pass; not every possible integer operation formally proven |
| B FIFO native book | COMPLETE | src/book/order_book.cpp; tests/test_book.cpp, independent reference cases | Synthetic mutation/reference agreement; venue-specific rules remain limited |
| B synthetic matcher | COMPLETE | src/simulation/simulator.cpp; simulation.reports/faults/independent_reference | Both maker/taker reports tested; no real exchange queue/latency calibration |
| C ITCH/L3 reconstruction | PARTIAL | src/itch/{context,reconstruction,seed,streaming}.cpp; eight independent canonical references | Synthetic initial-state and transactional tests pass; real source completeness/initial L3 evidence missing |
| C LOBSTER | BLOCKED | src/lobster/{adapter,reconstruction}.cpp; existing synthetic tests | Attached historical data not inspected or processed; cloud permission unresolved |
| D replay/journal | PARTIAL | src/replay/replay.cpp; replay.journal_allocation/preoptimization_equivalence/memory_accounting | Deterministic bounded replay, allocation failures, archive accounting tested; no crash-safe persistent journal or long-market-session qualification |
| E TWAP/VWAP/POV/TCA | COMPLETE | src/execution/execution.cpp; execution.* and installed export tests | Exact authored schedule/cost identities; no empirical impact model or broker execution |
| F SEC transport | PARTIAL | terminal/stocks/service.py; workspace/repair transport tests | Fixed hosts, review/contact gates, bounded bodies, cooldown, partial components; official response reconciliation not executed here |
| F SEC normalization | PARTIAL | terminal/stocks/sec.py; new21 backend tests plus prior SEC tests | Two reproduced integrity defects repaired;16 selected metrics, revisions/fiscal context preserved; not full XBRL statements or original intraday PIT |
| G financial analytics | PARTIAL | terminal/stocks/financials.py;12 formulas and2000 independent margin candidates | Exact eligible reported periods; no quarterly inference, IFRS, annualized estimates or full accounting taxonomy |
| H Alpaca IEX | BLOCKED | terminal/stocks/{auth,prices,service,quote_analytics}.py; authored transport/browser tests | Credentials stay server-side; support381230 authorization pending; no gates enabled or actual request |
| I indicative option ingestion | BLOCKED | terminal/stocks/option_feed.py; option fixture tests | Bounded contract/quote parsing; current entitlement/delay/retention not independently qualified |
| I theoretical options | COMPLETE | terminal/stocks/options.py; finite-difference Greeks, parity/IV tests | European fixed-input Black–Scholes only; not American pricing, observed chain or calibrated volatility surface |
| J HMM/GARCH/Kalman | PARTIAL | terminal/stocks/research.py; prefix-causality/model reference tests | Fixed parameters and bounded authored returns; no fitting/convergence estimation, predictive or empirical validation |
| K risk descriptors | PARTIAL | terminal/stocks/{research,price_research}.py; tail/drawdown fixtures | Univariate empirical95% tail, drawdown and returns; portfolio exposure, correlations, scenario aggregation and concentration NOT IMPLEMENTED |
| L real-market validation | BLOCKED | docs/REAL_MARKET_VALIDATION_REPORT.md and existing pilot reports | Historical prefix format observations are not observed L3 validation; SEC owner dashboard report is not independent source reconciliation |
| M Python/C++ | COMPLETE | python/bindings and python/gig_microstructure; installed8+6, terminal native274x3 | Explicit types/rational strings and native replay; wheel does not package the terminal application; CPython shutdown LSan gap retained |
| N API | PARTIAL | terminal/server/app.py; new v2 company/filings tests and schema | v1 preserved; v2 cache-only exact financial descriptors available; ATLAS consumer not migrated or independently accepted |
| O data lifecycle | PARTIAL | terminal/l2_recording.py, l2_playback.py, recording.py; failure/retention tests | Bounded private recordings and process-local stock cache; no durable financial warehouse or restore-tested database |
| P security | PARTIAL | server request_proofs.py/stream_tickets.py/config.py;46 security+8 TLS checks | Exact origin/host/proof boundaries preserved; private Codespaces auth remains platform responsibility; no penetration-test certification |
| Q benchmarks | PARTIAL | benchmarks/journal_memory_probe.cpp; scripts/benchmark_stock_intelligence.py | Measured bounded shared-cloud synthetic workloads; not exchange latency or sustained production sizing |
| R toolchains/CI | PARTIAL | six fresh native155 suites; terminal274x3; packaging3 | All local gates pass; new HEAD not hosted/ARM64 qualified, no workflow dispatched |
| S operations | PARTIAL | scripts/start_terminal.sh; server/__main__.py/config.py | Single-worker private Codespaces deployment; local browser/TLS tests pass, external owner authentication not exercised |
| T frontend contract | PARTIAL | server/backend_contract.py; server/schemas/backend_company_v2.schema.json | Explicit nullable rational values/source/quality fields; existing frontend still v1, redesign acceptance outstanding |
| U documentation | COMPLETE | Nine files in this directory plus evidence manifest | Scoped assessment and reproducible commands; unresolved gates deliberately remain blocked |

## Historical defect recheck

All six fixes remain present; none needed another native repair. The fresh six155-case
suites include simulation.reports, execution.cost_limits, independent replay/journal
checks and benchmark artifact gates. Installed-wheel export-contract6 tests additionally
exercise missing VWAP dependencies and contradictory dataset/parent digests.

| Previous defect | Current source/regression |
|---|---|
| Fully executed maker lost client reports | tests/test_simulation.cpp:17, src/simulation/simulator.cpp; simulation.reports checks both sides and conservation |
| Over-limit TCA fills | src/execution/execution.cpp:94; tests/test_execution.cpp:33, execution.cost_limits rejects zero/over-max before allocation |
| VWAP profile omitted from complete export | tests/test_export_contracts.py:42; python/gig_microstructure export dependency validation |
| Contradictory known dataset digests | tests/test_export_contracts.py:105; read-only verifier negative controls and missing/known digest semantics |
| Compiler metadata misidentified | tests/test_benchmark_metadata.py:15; scripts/run_engine_baseline.py selected CMake compiler metadata |
| Compiler-dependent RNG draw order | fixtures/synthetic/phase2_workload.hpp:40–41 separate quantity/price draws; tests/test_workload.cpp and independent fixture checks |

Native source, bindings, root schemas and frozen fixture identities are unchanged by
this checkpoint. See REMAINING_GAPS.md for priority/dependency decisions.
