# Quantitative models: use and limitations

Use Stock Intelligence → **Options**, **Quant & Risk**, portfolio/history tools or Research & Validation as applicable. Source implementations are under `terminal/stocks/`, `include/gig/analytics/`, `include/gig/execution/` and `include/gig/simulation/`. Model inputs are bounded and validated; invalid inputs are errors, not silently clipped observations.

| Calculation | What it does / inputs | What it does not establish |
|---|---|---|
| Spread, midpoint, quote-size imbalance | Ask−bid; (ask+bid)/2; (bid size−ask size)/(sum of sizes). Native/Python exact rational outputs; approximation only for display. | Venue-limited best quotes are not market-wide liquidity or depth. |
| Native microprice / flow metrics | Size-weighted opposite best prices; bounded quote/trade windows with explicit clocks and available horizons. | Future horizons/signs may be unavailable; a depth delta is not a classified trade. |
| Black–Scholes | European call/put price and Greeks from spot/strike, years, volatility, continuously compounded rate/dividend. Enter 20% volatility as 0.20. IV uses bounded bisection and rejects unidentifiable boundaries. | No American exercise, discrete-dividend model, observed option calibration or profit claim. Price 7.965567455405804 for S=K=100,T=1,σ=.2,r=q=0 displays **≈7.966**; expanded details retain precision. |
| Fixed HMM demonstration | Gaussian hidden-state transition/filtering with declared means/variances. | State probabilities are conditional on assumptions, not proven economic regimes. |
| HMM fit / missing-emission diagnostic | Bounded two-state Baum–Welch/log likelihood; separately, fixed-parameter missing emissions advance the transition without inventing an observation. | Full-sample fitted historical probabilities have parameter look-ahead. Fixed missing-emission handling is not missing-data parameter estimation. |
| GARCH | h(next)=ω+α(r−μ)²+βh. Bounded finite-grid or constrained coordinate search; separate parameter-only 3D surface. | No global-MLE, confidence interval or forecast superiority guarantee. The 3D surface is a declared equation, not market IV. |
| Kalman local level | Recursive mean/variance estimate using declared process and measurement noise; missing observations predict without measurement. | Noise settings are not learned fair value. |
| Empirical risk / portfolio | Exact covariance and aligned-return arithmetic; historical tail order statistics, weighted wealth/drawdown and declared scenarios. | Small tails are unstable; raw unadjusted price history, corporate actions, missing sessions and source alignment matter. No portfolio optimizer or Euler risk attribution is implied. |
| Toy backtest / chronological evaluation | Long when strictly preceding five returns sum positive, otherwise flat; 1 bp turnover cost. Separate bounded training/validation/test and expanding-fold diagnostics. | No empirical alpha, full transaction-cost model, tradable availability proof, statistical significance or strategy-selection correction. |
| SEC descriptors | Backend exact period/unit-aligned ratios, growth, cash-flow and accounting checks. | Missing fiscal periods, source acceptance times and tags cannot be invented. Annual, quarter and YTD are different. |
| TWAP / VWAP / POV / TCA | Native deterministic schedules, synthetic matching and exact fee/benchmark decomposition on declared authored inputs. | No broker routing, complete empirical market-impact model or observed execution-quality claim. |
| HHI concentration proposal | Sum(q²)/sum(q)² with exact declared quantities and explicit normalization. | This is a proposed contract; original historical A18/A19 acceptance remains unresolved. |

The advanced research laboratory can export only its unchanged public authored fixture, selected model/symbol/capture/depth/side, results and SHA256. Retained provider observations are excluded from that export. Recompute through `authoredResearchBundle`/`buildResearchPlot` for deterministic comparison. This is not a general empirical provenance or retention grant.

No implemented cointegration/pairs-selection, cross-sectional factor engine, portfolio optimizer, learned fair-value signal or profitable strategy should be claimed. Adding speculative models is outside this remediation sprint.
