# Explicit portfolio risk

**COMPLETE within caller-supplied bounded model:**1..4 explicitly named assets,20..64 aligned
returns each,decimal weights net exactly1,gross≤3. No holdings inferred from stock search.
No missing fill or mismatched-length truncation. Shared array index is caller-declared
alignment;not independently verified timestamps. Constant weights rebalanced each interval;
no transaction costs,borrowing charges,liquidity or actual execution model.

Exact Fraction calculations:portfolio returns,sum w_i*r_i;sample n−1 covariance;
weighted quadratic variance checked against direct portfolio sample variance;historical
VaR/ES worst ceil(5%N) losses;net/gross exposure;compounded drawdown and explicit asset-shock
weighted scenarios. Approximate correlation has null for zero variance. Gaussian VaR is
−mean+z_.95*sd;ES is−mean+phi(z_.95)/.05*sd. Rolling20 sample volatility is unannualized.
Drawdown unavailable for nonpositive leveraged wealth or4096-bit output capacity,not clipped.

Every result supplies method,confidence.95,horizon,sample count,fractional-equity units,
dataset/analysis identities,missingness assumptions and limits. No currency P&L or actual
holdings inferred. Synthetic UI defaults are explicit and edits invalidate old output.

Independent tests check anticorrelated equal-weight zero returns/covariance identities,
nonzero Gaussian tail constants,historical/scenario arithmetic,zero-variance correlation,
invalid weights/missing lengths. UI independently checks default historical VaR.006.
**NOT VERIFIED:**empirical calibration,portfolio tail coverage,exposure valuation/holdings
feeds,heterogeneous calendars,options convexity and predictive/stress significance.
