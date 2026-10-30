# Quantitative model validation matrix

Source `10eaee30d598807a23e42a8b60abe3d5a5dc2514`. **25 families/helper variants/transforms** inspected; this is
not a claim of 25 independent predictive models. Some rows group shared
implementations and expose meaningful variants. [models.json](models.json) supplies
structured contracts and validation limits. Every current fitted model remains an
offline research implementation; no independently established empirically validated
predictor or production-calibrated model was found. Owner SEC fact reconciliation
is positive selected-data evidence, not a model forecasting study.

No original requirement unconditionally mandates cointegration, OU, pairs selection,
cross-sectional factors, an optimizer, American options or every fashionable volatility
family. These need an approved estimator/data/acceptance contract; absence is not
invented as a release defect. Current explicit-weight portfolio analysis does not
claim an optimizer or per-asset Euler attribution.

| Family | Evidence level | Actual integration | Principal limitation |
|---|---|---|---|
| European Black–Scholes and analytical Greeks | OFFLINE_RESEARCH_IMPLEMENTATION | POST /api/v1/stocks/options → VolatilitySurface/OptionChain scenario UI | No independently verified observed out-of-sample performance or production calibration; European-only. Scenario grid endpoint boundary needs repair. |
| Bracketed implied volatility | OFFLINE_RESEARCH_IMPLEMENTATION | Theoretical scenario target_price field | No independently verified observed out-of-sample performance or production calibration; near-flat inversion diagnostics optional A17. |
| Provider indicative option IV/Greeks | OFFLINE_RESEARCH_IMPLEMENTATION | OptionChain.tsx; options permission gates remain disabled | BLOCKED real indicative-feed permission and observations; not OPRA, executable chain or independent calibration. |
| Fixed Gaussian HMM demonstration | MATHEMATICAL_DEMONSTRATION | POST stocks/research → ResearchSummary/ResearchDesk | No independently verified observed out-of-sample performance or production calibration; not an estimator; no broad empirical regime label meaning. |
| Two-state Gaussian HMM EM fit | OFFLINE_RESEARCH_IMPLEMENTATION | stocks/models → ResearchDiagnostics; authored returns clearly labeled | No independently verified observed out-of-sample performance or production calibration; economic regimes and classification accuracy not established. |
| Missing-emission fixed HMM | OFFLINE_RESEARCH_IMPLEMENTATION | stocks/hmm-filter endpoint; not falsely shown as live regime | No independently verified observed out-of-sample performance or production calibration; parameter source and empirical state meaning remain caller responsibility. |
| Fixed GARCH(1, 1) demonstration | MATHEMATICAL_DEMONSTRATION | ResearchSummary/GARCH modeled display | No independently verified observed out-of-sample performance or production calibration; not forecast validation. |
| Gaussian GARCH finite-grid likelihood fit | OFFLINE_RESEARCH_IMPLEMENTATION | stocks/models → ResearchDiagnostics/ModelSurface | No independently verified observed out-of-sample performance or production calibration; no standardized residual/ARCH-LM/parameter interval study. |
| Constrained GARCH coordinate likelihood search | OFFLINE_RESEARCH_IMPLEMENTATION | stocks/garch-fit → ResearchDiagnostics advanced disclosure | No independently verified observed out-of-sample performance or production calibration; coordinate convergence is not statistical identification. |
| Scalar local-level Kalman filters | OFFLINE_RESEARCH_IMPLEMENTATION | stocks/models and stocks/research; research workflow | No independently verified observed out-of-sample performance or production calibration; not empirically calibrated latent fair value. |
| Train-only held-out likelihood evaluation | OFFLINE_RESEARCH_IMPLEMENTATION | ResearchDiagnostics held-out controls and likelihood table | No independently verified observed out-of-sample performance or production calibration; scores compare same observations only; no predictive significance or confidence interval. |
| Bounded expanding-window walkforward | OFFLINE_RESEARCH_IMPLEMENTATION | ResearchDiagnostics walkforward checkbox | No independently verified observed out-of-sample performance or production calibration; not broad walkforward coverage of long histories. |
| Historical return/tail/drawdown descriptors | OFFLINE_RESEARCH_IMPLEMENTATION | Accepted historical price views → ResearchDiagnostics/risk endpoints | No independently verified observed out-of-sample performance or production calibration; small-tail uncertainty and incomplete source intervals remain. |
| Explicit-weight portfolio covariance and tail risk | OFFLINE_RESEARCH_IMPLEMENTATION | stocks/portfolio → PortfolioLab; summary precision issue A15 | No independently verified observed out-of-sample performance or production calibration; no per-asset Euler attribution or cost/liquidity model. |
| Authored lagged strategy backtest | MATHEMATICAL_DEMONSTRATION | stocks/research → ResearchSummary, not live execution | No independently verified observed out-of-sample performance or production calibration; no fills/spread/impact/borrow/corporate actions. |
| Native spread/depth/microprice/imbalance | OFFLINE_RESEARCH_IMPLEMENTATION | NativeSession metrics → OrderBook/Depth browser; Python binding | Correct supplied-book metrics do not prove underlying exchange reconstruction or available executable liquidity. |
| Native OFI, intensity, trade classification and impact | OFFLINE_RESEARCH_IMPLEMENTATION | Native research/export and OrderFlow; not fabricated from unsigned IEX prints | Needs valid comparable observed quotes/trades and qualified clocks/continuity; no exchange-wide or causal evidence. |
| IEX L1 retained-window analytics | OFFLINE_RESEARCH_IMPLEMENTATION | live.view → SSE/LiveMarket/QuoteCloud | BLOCKED actual authorized provider acceptance; partial received window cannot prove market-wide realized volatility. |
| Toy signed-volume VPIN-style buckets | MATHEMATICAL_DEMONSTRATION | ResearchLab Flow/VPIN mode | PARTIAL empirical capability; do not label all 13 visuals as13 validated quantitative models. |
| Execution VWAP corridor and supplied-depth transforms | MATHEMATICAL_DEMONSTRATION | Eight ResearchLab modes with provenance and camera controls | No live depth from L1; VWAP corridor is not executable capacity; dome not implied volatility. |
| GARCH modeled visualization surface | MATHEMATICAL_DEMONSTRATION | Research/StockIntelligence modeled surface | Geometry tests validate display, not a volatility-forecast model. |
| Deterministic matching and latency simulator | OFFLINE_RESEARCH_IMPLEMENTATION | Execution Simulator via NativeSession | No exchange-specific hidden/auction/latency calibration or fill-probability validation. |
| TWAP/VWAP/POV schedule planning | OFFLINE_RESEARCH_IMPLEMENTATION | NativeSession simulation controls/research exports | Plans are synthetic, not a routing/execution service; queue/cost assumptions remain declared. |
| Transaction-cost analysis | OFFLINE_RESEARCH_IMPLEMENTATION | Native execution research exports and simulation UI | Actual execution-quality validation needs actual lawful fills/benchmarks; simulation success is not empirical TCA. |
| Twelve SEC financial descriptors | OFFLINE_RESEARCH_IMPLEMENTATION | v2 company/financials → FinancialWorkspace/RatioHistory | Selected reported tags are not full statements or complete historical ratios; company-specific taxonomy/context coverage incomplete. |


## Q01 — European Black–Scholes and analytical Greeks

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** C=S exp(-qT)N(d1)-K exp(-rT)N(d2); put parity; delta/gamma/vega/theta/rho. Same currency spot/strike; vega/rho per1.0, theta per year.
- **Source:** terminal/stocks/options.py:17–26.
- **Executed test evidence:** terminal/stocks/test_workspace.py:92–111:parity, finite differences and invalid-domain checks; A1 renewed API boundary probe. See evidence index for renewed versus retained runs.
- **Numerical stability:** erfc CDF; finite bounded positive S, K, T, sigma; floating binary64; price floored at0; scenario-domain defect A04.
- **Calibration/training:** User-authored sigma/r/q; no estimation or calibration.
- **Look-ahead/survivorship/chronology:** Single theoretical scenario; not data training; no implied trading opportunity.
- **Missing data/failure:** Missing/invalid fields reject; American/discrete dividends excluded.
- **Actual integration:** POST /api/v1/stocks/options → VolatilitySurface/OptionChain scenario UI.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; European-only. Scenario grid endpoint boundary needs repair.


## Q02 — Bracketed implied volatility

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Invert European BSM price on sigma=[1e-6, 5] with100 bisections; strictly interior identifiable target only.
- **Source:** terminal/stocks/options.py:28–37.
- **Executed test evidence:** terminal/stocks/test_workspace.py:103–104:known-vol inversion/out-of-range. See evidence index for renewed versus retained runs.
- **Numerical stability:** Finite bounds, reject bracket endpoints; no residual/vega conditioning in output.
- **Calibration/training:** Single-price inversion, not volatility-surface calibration.
- **Look-ahead/survivorship/chronology:** Target source not assumed observed; no future data.
- **Missing data/failure:** Unidentifiable/outside bracket explicit ValueError.
- **Actual integration:** Theoretical scenario target_price field.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; near-flat inversion diagnostics optional A17.


## Q03 — Provider indicative option IV/Greeks

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Validate and display provider-supplied estimates with exact contract shape; not a locally derived pricing model.
- **Source:** terminal/stocks/option_feed.py:1–32.
- **Executed test evidence:** terminal/stocks/test_repair.py:42–45, 109:separate indicative gate, no OPRA fallback; workspace fixtures. See evidence index for renewed versus retained runs.
- **Numerical stability:** Decimal finite/range guards; OCC-shaped identity validation; max100 partial contracts.
- **Calibration/training:** Provider methodology not independently verified.
- **Look-ahead/survivorship/chronology:** Quote/trade timestamps preserved; source-specific delay unknown; no OI or complete chain.
- **Missing data/failure:** Missing quote/trade/IV/Greeks nullable; pagination not declared complete.
- **Actual integration:** OptionChain.tsx; options permission gates remain disabled.
- **Qualification still needed:** BLOCKED real indicative-feed permission and observations; not OPRA, executable chain or independent calibration.


## Q04 — Fixed Gaussian HMM demonstration

- **Class:** MATHEMATICAL_DEMONSTRATION.
- **Mathematical/input/output contract:** Two zero-mean Gaussian states with sigma .01/.05, transition .95/.05; causal forward filtering.
- **Source:** terminal/stocks/research.py:5–29.
- **Executed test evidence:** terminal/stocks/test_workspace.py; prefix/causality fixtures. See evidence index for renewed versus retained runs.
- **Numerical stability:** Bounded20–256 return strings[-1, 1]; ordinary density arithmetic; explicit zero-total likelihood guard. No new underflow defect was reproduced in its bounded domain.
- **Calibration/training:** Fixed authored parameters, not trained.
- **Look-ahead/survivorship/chronology:** Filter uses prefix; external parameter-estimation origin not authenticated.
- **Missing data/failure:** Reject invalid/missing sample; underflow is a failure, not inferred regime.
- **Actual integration:** POST stocks/research → ResearchSummary/ResearchDesk.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; not an estimator; no broad empirical regime label meaning.


## Q05 — Two-state Gaussian HMM EM fit

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Scaled log-domain forward/backward Baum–Welch; two Gaussian emissions, deterministic initialization, variance/transition floors, max40iterations.
- **Source:** terminal/stocks/models.py:16–66.
- **Executed test evidence:** terminal/stocks/test_backend.py; terminal/stocks/test_overnight.py; normalization/constant data/likelihood and reference tests. See evidence index for renewed versus retained runs.
- **Numerical stability:** logsumexp, normalized weights, variance>=1e-12; variance<1e-14 input unidentifiable; reject/regard constrained nonimproving updates.
- **Calibration/training:** Local EM fit; converged/iterations/likelihood_trace/stop_reason returned; no global optimum, parameter CI or label-identification claim.
- **Look-ahead/survivorship/chronology:** Full-sample historical filtered outputs have parameter-estimation look-ahead; explicit warning. Train-only heldout wrapper is separate; no survival-safe universe.
- **Missing data/failure:** Bounded finite authored values; collapsed states/transitions explicit stop.
- **Actual integration:** stocks/models → ResearchDiagnostics; authored returns clearly labeled.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; economic regimes and classification accuracy not established.


## Q06 — Missing-emission fixed HMM

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Predict by A each step; missing emission contributes likelihood1; observed emissions log Gaussian/softmax. No smoothing or imputation.
- **Source:** terminal/stocks/advanced_models.py:32–52.
- **Executed test evidence:** terminal/stocks/test_overnight.py:independent oracle, huge variance/opposite extrema/tiny variance, missing/invalid parameters; S1 renewed. See evidence index for renewed versus retained runs.
- **Numerical stability:** Separate logs avoid2*pi*variance overflow; capacity errors explicit; finite probabilities normalized; at most 256 emissions.
- **Calibration/training:** Fixed supplied means/variances/transitions/prior; not trained.
- **Look-ahead/survivorship/chronology:** Prefix-causal conditional on supplied parameter provenance; cannot make retrospectively fitted parameters causal.
- **Missing data/failure:** None is explicit missing emission; invalid data rejects; unrepresentable all-state likelihood rejects.
- **Actual integration:** stocks/hmm-filter endpoint; not falsely shown as live regime.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; parameter source and empirical state meaning remain caller responsibility.


## Q07 — Fixed GARCH(1, 1) demonstration

- **Class:** MATHEMATICAL_DEMONSTRATION.
- **Mathematical/input/output contract:** h(t+1)=1e-6+.08*r(t)^2+.90*h(t), initial h=.0001; h(t) emitted before observing r(t).
- **Source:** terminal/stocks/research.py:11–18.
- **Executed test evidence:** terminal/stocks/test_workspace.py:recurrence and prefix fixtures. See evidence index for renewed versus retained runs.
- **Numerical stability:** Bounded returns/positive fixed coefficients ensure finite tested paths.
- **Calibration/training:** Coefficients fixed, not fitted.
- **Look-ahead/survivorship/chronology:** One-step chronology correct; no future fitting implied.
- **Missing data/failure:** No missing input imputation; invalid sample rejects.
- **Actual integration:** ResearchSummary/GARCH modeled display.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; not forecast validation.


## Q08 — Gaussian GARCH finite-grid likelihood fit

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Gaussian conditional likelihood with sample mean/initial variance; constant-variance baseline plus bounded omega/alpha/beta grid, alpha+beta<.995.
- **Source:** terminal/stocks/models.py:69–92.
- **Executed test evidence:** terminal/stocks/test_backend.py; terminal/stocks/test_phase4.py; independent recurrence/constraint tests. See evidence index for renewed versus retained runs.
- **Numerical stability:** Positive omega floors; finite bounded returns; constant sample unavailable; bounded candidate work.
- **Calibration/training:** Finite-grid conditional fit, not global MLE; diagnostic likelihood and next variance.
- **Look-ahead/survivorship/chronology:** Full supplied sample used to fit; past variance curve not a causal historical fitted signal.
- **Missing data/failure:** Malformed/nonfinite values rejected; constant samples explicit unidentifiable.
- **Actual integration:** stocks/models → ResearchDiagnostics/ModelSurface.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; no standardized residual/ARCH-LM/parameter interval study.


## Q09 — Constrained GARCH coordinate likelihood search

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Log omega and .995-scaled simplex coefficients; deterministic coordinate moves, step halving, max120iterations; retain grid boundary if better.
- **Source:** terminal/stocks/advanced_models.py:5–30.
- **Executed test evidence:** terminal/stocks/test_phase5.py; terminal/stocks/test_overnight.py; constraints, baseline no degradation, hashes. See evidence index for renewed versus retained runs.
- **Numerical stability:** Parameter clamp/log/simplex guards; bounded evaluations; stop_reason and convergence returned.
- **Calibration/training:** Conditional local pattern search with fixed sample mean/initial variance; not joint global likelihood.
- **Look-ahead/survivorship/chronology:** Training scope is supplied sample; not a walkforward trading forecast unless separately wrapped.
- **Missing data/failure:** Constant sample unidentifiable; no imputation.
- **Actual integration:** stocks/garch-fit → ResearchDiagnostics advanced disclosure.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; coordinate convergence is not statistical identification.


## Q10 — Scalar local-level Kalman filters

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Predict covariance P+Q; gain=Ppred/(Ppred+R), mean update; models.py uses Joseph posterior covariance. Q=1e-5, R=.001.
- **Source:** terminal/stocks/models.py:94–102; terminal/stocks/research.py:12–18.
- **Executed test evidence:** terminal/stocks/test_backend.py; terminal/stocks/test_phase4.py; independent recurrence and missing observation tests. See evidence index for renewed versus retained runs.
- **Numerical stability:** Bounded finite inputs; positive fixed Q/R; Joseph sum of squares for updated implementation.
- **Calibration/training:** Fixed noise parameters; no state-space parameter estimation.
- **Look-ahead/survivorship/chronology:** Filter only, not smoother; given fixed parameter history, prefix-causal.
- **Missing data/failure:** models.kalman None means prediction-only; fixed demo requires actual return.
- **Actual integration:** stocks/models and stocks/research; research workflow.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; not empirically calibrated latent fair value.


## Q11 — Train-only held-out likelihood evaluation

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Fit HMM/GARCH/baseline on prefix; validation/test update filter/variance states only; score conditional Gaussian likelihood.
- **Source:** terminal/stocks/evaluation.py:6–26.
- **Executed test evidence:** terminal/stocks/test_phase4.py; terminal/stocks/test_phase5.py:training hashes/holdout perturbation/chronology. See evidence index for renewed versus retained runs.
- **Numerical stability:** Bounded sample and valid split requirements; normalized probabilities; model fit failure explicit.
- **Calibration/training:** Train once; no tuning on held-out test by implementation.
- **Look-ahead/survivorship/chronology:** Index chronology caller-declared, not authenticated timestamps/PIT. Full-sample UI fit remains separate.
- **Missing data/failure:** No rows dropped or imputed; invalid/insufficient samples reject.
- **Actual integration:** ResearchDiagnostics held-out controls and likelihood table.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; scores compare same observations only; no predictive significance or confidence interval.


## Q12 — Bounded expanding-window walkforward

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Training starts20; five validation thenfive nonoverlapping test observations; refit each fold, max4 folds; unused suffix reported.
- **Source:** terminal/stocks/evaluation.py:29–37.
- **Executed test evidence:** terminal/stocks/test_phase4.py; terminal/stocks/test_phase5.py:fold boundaries/training identity. See evidence index for renewed versus retained runs.
- **Numerical stability:** Bounded fitting work, no unbounded rolling loop.
- **Calibration/training:** Independent prefix refit per fold; fixed protocol, not optimization.
- **Look-ahead/survivorship/chronology:** No future rows in fit; fold scores dependent, source timestamps/universe not verified.
- **Missing data/failure:** Minimum sample; unscored suffix explicit.
- **Actual integration:** ResearchDiagnostics walkforward checkbox.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; not broad walkforward coverage of long histories.


## Q13 — Historical return/tail/drawdown descriptors

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Raw close-to-close simple returns; sum r², sample variance(n-1), sqrt(sum r²), peak close drawdown; 95%loss tail worst ceil(.05N).
- **Source:** terminal/stocks/price_research.py:5–26; terminal/stocks/risk.py:7–25.
- **Executed test evidence:** terminal/stocks/test_backend.py; terminal/stocks/test_phase4.py; terminal/stocks/test_alpaca_data.py. See evidence index for renewed versus retained runs.
- **Numerical stability:** Fraction arithmetic with4096-bit wire capacity; explicit approximate square root; positive prices; bounded256bars.
- **Calibration/training:** Descriptive estimators, not trained/calibrated forecast.
- **Look-ahead/survivorship/chronology:** Raw/unadjusted returned sample; no corporate actions/survivorship-safe universe or annualization claim.
- **Missing data/failure:** Risk unavailable below20returns; missing values not filled; capacity reason explicit.
- **Actual integration:** Accepted historical price views → ResearchDiagnostics/risk endpoints.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; small-tail uncertainty and incomplete source intervals remain.


## Q14 — Explicit-weight portfolio covariance and tail risk

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** 1–4aligned assets, 20–64 returns; net weights1, gross<=3; exact sample covariance and w′Σw; historical/Gaussian95%VaR/ES; rebalanced wealth/drawdown/20 step rolling/scenarios.
- **Source:** terminal/stocks/portfolio.py:7–60.
- **Executed test evidence:** terminal/stocks/test_phase4.py; terminal/stocks/test_phase5.py; independent rational/covariance/boundary tests. See evidence index for renewed versus retained runs.
- **Numerical stability:** Fractions and exact covariance invariant; binary64 Gaussian/correlation; null zero-variance correlation; 4096-bit display capacity/nonpositive wealth reason.
- **Calibration/training:** No optimizer or holdings inferred; fixed user weights; Gaussian tail assumption not calibrated.
- **Look-ahead/survivorship/chronology:** Caller declares alignment; no timestamps/authenticated PIT/corporate actions/tradability or survivorship controls.
- **Missing data/failure:** Reject mismatched lengths/missing assets; no imputation; nonpositive leveraged wealth stops drawdown.
- **Actual integration:** stocks/portfolio → PortfolioLab; summary precision issue A15.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; no per-asset Euler attribution or cost/liquidity model.


## Q15 — Authored lagged strategy backtest

- **Class:** MATHEMATICAL_DEMONSTRATION.
- **Mathematical/input/output contract:** Long when preceding5 simple returns sum>0, otherwise flat; wealth multiplies1+position*return-.0001*turnover; no terminal liquidation.
- **Source:** terminal/stocks/research.py:19–29.
- **Executed test evidence:** terminal/stocks/test_workspace.py; prefix/return perturbation assertions. See evidence index for renewed versus retained runs.
- **Numerical stability:** Signal/wealth uses Fraction; display curve floating; extreme returns may make wealth nonpositive, explicit limitation.
- **Calibration/training:** Rule and linear cost fixed; no fitted alpha or strategy search.
- **Look-ahead/survivorship/chronology:** Signal uses only previous returns; caller input chronology not independently verified; no survivorship-safe sample.
- **Missing data/failure:** Malformed/missing returns reject.
- **Actual integration:** stocks/research → ResearchSummary, not live execution.
- **Qualification still needed:** No independently verified observed out-of-sample performance or production calibration; no fills/spread/impact/borrow/corporate actions.


## Q16 — Native spread/depth/microprice/imbalance

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Spread=a-b; mid=(a+b)/2; microprice=(a*qb+b*qa)/(qb+qa); top/depth imbalance=(bidqty-askqty)/(bidqty+askqty).
- **Source:** include/gig/analytics/book_metrics.hpp:6–30; src/analytics/book_metrics.cpp.
- **Executed test evidence:** tests/test_book_metrics.cpp; independent rational calculations; N1 retained. See evidence index for renewed versus retained runs.
- **Numerical stability:** Checked exact128-bit fractions; structured arithmetic capacity; no silent division/rounding.
- **Calibration/training:** Pure snapshot mathematics; no estimation.
- **Look-ahead/survivorship/chronology:** Owned snapshot run/prefix/revision/session lineage; no future observations.
- **Missing data/failure:** Explicit empty, one-sided, zero-denominator, truncated-depth outcomes.
- **Actual integration:** NativeSession metrics → OrderBook/Depth browser; Python binding.
- **Qualification still needed:** Correct supplied-book metrics do not prove underlying exchange reconstruction or available executable liquidity.


## Q17 — Native OFI, intensity, trade classification and impact

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Configured UTC clock/window/quote lag/horizon/max quote age/sampling; OFI from eligible top changes; quote-lag trade sign; effective/realized spreads, price response and sampled return variation.
- **Source:** include/gig/analytics/flow_metrics.hpp:6–41; src/analytics/flow_metrics.cpp.
- **Executed test evidence:** tests/test_flow_metrics.cpp; independent rational boundaries/quote horizons/gaps. See evidence index for renewed versus retained runs.
- **Numerical stability:** Checked exact arithmetic, including portable128-bit multiply; approximate volatility sqrt explicitly labeled.
- **Calibration/training:** Deterministic conditional estimators; no calibrated causal-impact function.
- **Look-ahead/survivorship/chronology:** As-of cutoff and required future horizon availability explicit; not same as causal intervention effect.
- **Missing data/failure:** Incomplete continuity, unknown direction, stale quote or pending horizon produces missing reason.
- **Actual integration:** Native research/export and OrderFlow; not fabricated from unsigned IEX prints.
- **Qualification still needed:** Needs valid comparable observed quotes/trades and qualified clocks/continuity; no exchange-wide or causal evidence.


## Q18 — IEX L1 retained-window analytics

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Exact best spread, mid, relative spread, size imbalance; retained mid change; frequency(N-1)/elapsed; log-mid sqrt(sum log-return²); unsigned print size totals only when uncorrected.
- **Source:** terminal/stocks/live_metrics.py:5–22.
- **Executed test evidence:** terminal/stocks/test_live_market.py; terminal/stocks/test_completion.py:generations, late/zero/crossed/correction cases. See evidence index for renewed versus retained runs.
- **Numerical stability:** Fraction outputs; binary64 log variation; generation-scoped bounded256 events.
- **Calibration/training:** Descriptive, not fitted; size unit explicitly unverified.
- **Look-ahead/survivorship/chronology:** Ordered accepted current-generation observations only; source/receive clocks unsynchronized; no NBBO or previous-session close.
- **Missing data/failure:** No quote→null metrics; unsigned trades do not acquire aggressor side; corrections suppress unreconciled volume.
- **Actual integration:** live.view → SSE/LiveMarket/QuoteCloud.
- **Qualification still needed:** BLOCKED actual authorized provider acceptance; partial received window cannot prove market-wide realized volatility.


## Q19 — Toy signed-volume VPIN-style buckets

- **Class:** MATHEMATICAL_DEMONSTRATION.
- **Mathematical/input/output contract:** Declared execution sides/quantities form equal-volume illustrative imbalance buckets; streamlines are glyph connections, not physical trajectories.
- **Source:** terminal/web/src/research3d.ts:vpinBuckets, buildPlot(flow).
- **Executed test evidence:** terminal/web/src/research3d.test.ts; terminal/tests/advanced-research-validation.mjs. See evidence index for renewed versus retained runs.
- **Numerical stability:** BigInt/exact input validation; bounded authored events; display conversion only.
- **Calibration/training:** No empirical calibration, trade classifier, adaptive bucket fit or toxicity forecast.
- **Look-ahead/survivorship/chronology:** Capture order preserved; only explicit sides eligible; no inferred live L1 signs.
- **Missing data/failure:** Unsigned/insufficient executions→unavailable; no invented toxicity.
- **Actual integration:** ResearchLab Flow/VPIN mode.
- **Qualification still needed:** PARTIAL empirical capability; do not label all 13 visuals as13 validated quantitative models.


## Q20 — Execution VWAP corridor and supplied-depth transforms

- **Class:** MATHEMATICAL_DEMONSTRATION.
- **Mathematical/input/output contract:** Execution VWAP=sum(price*quantity)/sum(quantity); height/canyon/wheel summarize supplied levels; event voxels explicit events; quote ribbon/dome geometry uses eligible retained data.
- **Source:** terminal/web/src/research3d.ts:21–105 and remaining buildPlot modes.
- **Executed test evidence:** terminal/web/src/research3d.test.ts; terminal/tests/advanced-research-validation.mjs. See evidence index for renewed versus retained runs.
- **Numerical stability:** BigInt/decimal scales preserved in labels; binary64 geometry explicitly approximate; bounded samples/marks.
- **Calibration/training:** Transforms not fitted liquidity forecasts; interpolation is display only.
- **Look-ahead/survivorship/chronology:** Mixed origins/generations/nonincreasing positions excluded; no order events inferred from coalesced snapshots.
- **Missing data/failure:** Missing events/depth/direction→mode-specific unavailable state and2D table.
- **Actual integration:** Eight ResearchLab modes with provenance and camera controls.
- **Qualification still needed:** No live depth from L1; VWAP corridor is not executable capacity; dome not implied volatility.


## Q21 — GARCH modeled visualization surface

- **Class:** MATHEMATICAL_DEMONSTRATION.
- **Mathematical/input/output contract:** Project declared GARCH conditional-variance horizons across a labeled parameter/scale grid.
- **Source:** terminal/web/src/modelSurface.ts; terminal/web/src/ModelSurface.tsx.
- **Executed test evidence:** terminal/web/src/modelSurface.test.ts; browser model/touch fixtures. See evidence index for renewed versus retained runs.
- **Numerical stability:** Finite geometry/budget validation; deferred renderer; WebGL fallback.
- **Calibration/training:** Uses declared model inputs; not observed option smile or fitted term structure.
- **Look-ahead/survivorship/chronology:** No historical-provenance upgrade from modeled grid.
- **Missing data/failure:** Insufficient/invalid inputs show unavailable.
- **Actual integration:** Research/StockIntelligence modeled surface.
- **Qualification still needed:** Geometry tests validate display, not a volatility-forecast model.


## Q22 — Deterministic matching and latency simulator

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Single-threaded synthetic price/time matching with explicit arrivals, latency ordering, partial fills/cancel/replace and maker/taker reports.
- **Source:** include/gig/simulation/simulator.hpp; src/simulation/simulator.cpp.
- **Executed test evidence:** tests/test_simulation.cpp; native independent regressions and allocation tests. See evidence index for renewed versus retained runs.
- **Numerical stability:** Strong units, checked quantities and stable ordering; resource-exhausted outcomes.
- **Calibration/training:** Authored assumptions, not calibrated venue queue probability.
- **Look-ahead/survivorship/chronology:** Simulation clock/provenance distinct from observed fills; no real order submission.
- **Missing data/failure:** Inadmissible orders reject atomically; unknown historical queue not invented.
- **Actual integration:** Execution Simulator via NativeSession.
- **Qualification still needed:** No exchange-specific hidden/auction/latency calibration or fill-probability validation.


## Q23 — TWAP/VWAP/POV schedule planning

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Exact bounded quantity allocation over explicit time/profile/volume inputs; no inferred future executable volume.
- **Source:** include/gig/execution/execution.hpp; src/execution/execution.cpp.
- **Executed test evidence:** tests/test_execution.cpp; independent schedule totals/rounding/overflow. See evidence index for renewed versus retained runs.
- **Numerical stability:** Integer/rational arithmetic; quantity conservation; invalid profiles reject.
- **Calibration/training:** Explicit supplied volume profile; not fitted future volume forecast.
- **Look-ahead/survivorship/chronology:** VWAP planned profile provenance required; POV depends on declared eligible volume, not unseen history.
- **Missing data/failure:** Missing/invalid profile not replaced by fabricated market data.
- **Actual integration:** NativeSession simulation controls/research exports.
- **Qualification still needed:** Plans are synthetic, not a routing/execution service; queue/cost assumptions remain declared.


## Q24 — Transaction-cost analysis

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Compare eligible fills with declared arrival/benchmark prices and quantities; explicit costs/slippage/shortfall/sign convention.
- **Source:** src/execution/execution.cpp; include/gig/execution/execution.hpp.
- **Executed test evidence:** tests/test_execution.cpp; tests/test_export_contracts.py; overfill and maker report regressions. See evidence index for renewed versus retained runs.
- **Numerical stability:** Checked arithmetic and declared quantity maxima; no silent extra fills.
- **Calibration/training:** Accounting of supplied fills; no calibrated slippage prediction.
- **Look-ahead/survivorship/chronology:** Benchmark/profile/source lineage retained; synthetic reports never real executions.
- **Missing data/failure:** Unsupported/missing benchmark components explicit.
- **Actual integration:** Native execution research exports and simulation UI.
- **Qualification still needed:** Actual execution-quality validation needs actual lawful fills/benchmarks; simulation success is not empirical TCA.


## Q25 — Twelve SEC financial descriptors

- **Class:** OFFLINE_RESEARCH_IMPLEMENTATION.
- **Mathematical/input/output contract:** Exact ratios and annual comparisons from compatible selected facts, units and periods; balance means only with valid endpoints; null missingness.
- **Source:** terminal/stocks/financials.py:1–89; terminal/stocks/ratio_history.py.
- **Executed test evidence:** terminal/stocks/test_ratio_history.py; source qualification tests; O1 owner1772 selected-record reconciliation is underlying fact evidence, not all ratios independently observed. See evidence index for renewed versus retained runs.
- **Numerical stability:** Fraction arithmetic; unit/denominator checks; no quarterly subtraction, imputation or JS recomputation.
- **Calibration/training:** Deterministic accounting descriptors, not a predictive model.
- **Look-ahead/survivorship/chronology:** Selected filing/acceptance views protect known cutoffs; retained-cache/PIT limitations A05 apply; current registrant universe not survival-safe.
- **Missing data/failure:** Unavailable inputs/zero denominator/incompatible duration yield explicit reason.
- **Actual integration:** v2 company/financials → FinancialWorkspace/RatioHistory.
- **Qualification still needed:** Selected reported tags are not full statements or complete historical ratios; company-specific taxonomy/context coverage incomplete.


## Independent validation standard for promotion

An independently implemented recurrence or numerical finite difference is useful
algorithmic evidence; it does not validate the market assumptions. Before promoting
a model to observed research, bind immutable lawful input hashes and publication
times, declare sample selection/corporate actions/market coverage, train on a prefix,
reserve an untouched test interval, and report baselines, errors, residual diagnostics
and uncertainty. Economic strategy claims additionally need an executable cost,
liquidity and fill contract. Serial filtering using full-sample-fitted parameters is
not a causal historical signal. Model outputs with absent data stay unavailable.
