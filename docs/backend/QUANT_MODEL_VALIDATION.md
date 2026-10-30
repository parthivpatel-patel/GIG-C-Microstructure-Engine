# Quantitative and risk model validation

> **Historical snapshot — superseded for current implementation status.**
> Original document source commit: `ae570a2778befff59ac0fe38c143ab083ea2046f`. The original table below is preserved
> as historical evidence;its `NOT IMPLEMENTED` portfolio row and fixed-only
> HMM/GARCH assessment do not describe the current release baseline
> `10eaee30d598807a23e42a8b60abe3d5a5dc2514`.
> Current bounded models and limits: [quantitative contracts](../overnight/QUANTITATIVE_CONTRACTS.md),
> [current gaps](../overnight/REMAINING_GAPS.md),and
> [Sprint1 contract/status index](../remediation/sprint-1/MODEL_STATUS.md).
> No historical test result is retroactively changed by this notice.

No new collection of fitted models is added. The audit distinguishes executable
mathematics from statistical estimation, calibration and observed performance.

| Model | Implementation/tests | Validated scope | Missing evidence |
|---|---|---|---|
| Financial descriptors | stocks/financials.py;21 backend cases,2000 randomized margins | Exact12 formulas, compatible reported periods, unavailable boundaries | Official selected-fact/statement reconciliation |
| Black–Scholes | stocks/options.py; workspace option tests | European call/put price, parity, finite-difference Greeks, bounded IV bisection | American exercise, discrete dividends, calibrated observed smile |
| IV | options.py implied() |100 bisections in volatility[1e-6,5], invalid/unidentifiable targets rejected | Dynamic bracket/adaptive error report and empirical stability study |
| GARCH | stocks/research.py | Fixed omega1e-6,alpha.08,beta.90,initial variance.0001; one-step causal recurrence | No estimated likelihood, fit/convergence or residual diagnostics |
| Kalman | stocks/research.py | Scalar fixed process/measurement variances, prefix invariance | No fitted state-space model, parameter uncertainty or calibration |
| HMM | stocks/research.py | Fixed symmetric transitions/two Gaussian emissions, forward filtering, prefix invariance | No training/smoothing or out-of-sample predictive validation; likelihood underflow explicitly rejects extreme inputs |
| Historical VaR/ES | research.py,price_research.py | Worst ceil(5%N) simple-return losses, ES same tail, minimum20 returns for bar risk | Tail uncertainty, conditional coverage, portfolio dependence, stress calibration |
| Drawdown/returns | price_research.py | Exact accepted unadjusted close-to-close return/drawdown formulas | Corporate-action-adjusted total return and complete market history |
| Microstructure | C++ analytics and terminal/l2_research.py | Native spread/mid/imbalance, exact bounded display-cadence OFI/trade windows | Display cadence is not exchange order-level causality; aggressor semantics/receive-clock assumptions explicit |
| Strategy illustration | research.py | Prior5-return signal only, linear turnover cost, deterministic authored path | No alpha/model-selection claim, spread/impact/fill realism or final liquidation |
| Portfolio risk | NOT IMPLEMENTED | No misleading zero-valued placeholders added | Exposures, concentration, scenario aggregation/correlation and horizon conventions require specified inputs |

Greek units: vega per1.0 volatility, rho per1.0 rate, theta per year. Spot/strike must
share currency and time is years; a theoretical scenario is not an observed contract.
Provider Greek units and model assumptions must be reviewed independently before
comparing them. Indicative snapshots do not establish executable liquidity.

The simple risk endpoint accepts20..256 authored returns in[−1,1]. Confidence.95 and
the sample-tail convention are documented; no automatic annualization, normality
assumption or guarantee is made. Extreme returns can yield nonpositive wealth in the
illustrative strategy; this is disclosed rather than hidden through clipping.

Financial descriptors use exact rational arithmetic; floating-point probabilistic/
option models are approximations tested with appropriate tolerances. Mathematically
checked implementations are not statistically fitted or empirically validated models.
Next research gate: pre-register an authorized dataset, time/adjustment conventions,
causal train/validation splits, parameter estimation and uncertainty diagnostics before
adding forecasts or reporting predictive performance.
