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

## Accepted historical-bar research

The separate exact-time historical workflow uses only a server-accepted revision,not arbitrary browser-provided prices. For close C(t):simple return=C(t)/C(t−1)−1;log return=ln(C(t)/C(t−1));SMA is the arithmetic mean of the last declared number of closes;close drawdown=1−C(t)/maximum close so far. Simple returns,SMA,drawdown,volume and supplied-VWAP notional use exact rational arithmetic. Logs and square roots explicitly use binary64.

Realized log variation is sqrt(sum(log-return²));rolling variation uses the last declared number of eligible consecutive return positions. Both are unannualized descriptive variation,not calibrated volatility forecasts. Warmup/missing inputs are unavailable,not zero. Caller-declared elapsed-gap thresholds can break return pairs;there is no inferred holiday/halt calendar. SMA uses the available supplied closes;it is not a filled calendar-time average. First-to-last interval return still spans the selected interval even if an internal return is excluded by gap policy.

Volume retains source units. Notional turnover requires each positive-volume bar's **supplied** VWAP;close×volume is not substituted. Raw/split/dividend/all adjustment is explicitly requested and disclosed,not independently corporate-action-reconciled. Cross-stock percentage comparisons start at identical exact shared source endpoints;unmatched timestamps are excluded without interpolation.

Outputs depend only on their accepted input prefix for fixed parameters. Source receipts,exact timestamps,window,gap policy and revision accompany the result. Authorized historical exports carry the exact Python-sorted UTF8 payload string and SHA256;the browser verifies those bytes rather than reserializing floats. Observed export requires its separate retention permission. This does not alter the existing authored JavaScript export contract or frozen native identities.
