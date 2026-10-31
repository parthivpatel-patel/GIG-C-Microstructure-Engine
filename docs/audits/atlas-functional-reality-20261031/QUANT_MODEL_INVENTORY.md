# Quantitative implementation and correctness inventory

Candidate `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`. All current numerical
claims below concern authored/supplied inputs,not real-market calibration.
Full-sample estimation,chronological filtering and actual tradable point-in-time
availability are separate concepts. No empirical profitability or predictive
accuracy was measured. Paths below are repository-relative at the exact candidate.

| Capability / actual implementation | Formula,inputs,estimation and stability | Independent evidence / user integration / limitation |
|---|---|---|
| Native book metrics;C++ `analytics/book_metrics.hpp`,`tests/test_book_metrics.cpp` |Exact spread,midpoint,microprice=(ask·bidQty+bid·askQty)/(bidQty+askQty),top/depth imbalance,Fraction with capacity rejection.|Native six-configuration tests;new L1 exact case:100/102,80/20→spread2,mid101,micro508/5,imbalance3/5. Native book and L1 quote projection;not full exchange liquidity.|
| Native flow;C++ `analytics/flow_metrics.hpp`,`tests/test_flow_metrics.cpp` |Bounded ordered quote/trade window,declared clocks,quote lag/horizon/age,OFI,sign,effective/realized spread,impact,counts and variation.|Exact/oracle/negative native tests actually rerun. Quote direction/sign can beunknown;horizon/continuity unavailable rather than guessed. IEX L1 frontend does not become a complete order-flow feed.|
| Retained IEX metrics;Python `stocks/live_metrics.py`, `quote_analytics.py` |Exact spread/mid/size imbalance/first-to-last retained return;frequency(N−1)/source span;approx log-mid variation. Excludes crossed/late quotes;correction/cancel suppresses unreconciled trade sums.|Stock207 and new exact native-quote reference. Feed cards/3D;source size units unverified;no synchronized clock,previous close or complete tape.|
| HHI proposal;Python `server/concentration.py` |Σq²/(Σq)² and normalized(nHHI−1)/(n−1),bounded≤40uint64 quantities,exact Fraction,explicit zero/missing outcomes.|Rerun hand/256Decimal independent cases and HTTP isolation. Readonly UI;historical A19 estimator not approved.|
| Black–Scholes/Greeks/IV;Python `stocks/options.py` |European constant-volatility/rate/dividend Gaussian formula,explicit finite bounds. IV bracket1e−6..5,100 bisection steps,unidentifiable boundary rejection.|Known raw7.965567455405804 reference passes,put/call/finite-difference/existing boundary cases. UI theoretical only. No American exercise/discrete-dividend/market calibration;IV conditioning diagnostics optional.|
| HMM diagnostic fit;Python `stocks/models.py:21` |Two-state Gaussian Baum–Welch≤40iterations,log-domain forward/backward,variance/probability floors,monotonic constrained update/stop reasons.|New brute-force all8 three-step hidden paths agrees with forward likelihood/posterior. Existing state-permutation,collapse/constant/underflow cases pass. Full-sample fit historical probabilities have parameter look-ahead;warning retained.|
| Missing-emission HMM;`stocks/advanced_models.py:32` |Fixed declared Gaussian parameters;missing emission likelihood1,transition still advances;no imputation or missing-data fitting. Stable log terms and capacity errors.|Existing independent missing/extreme/label tests rerun. Diagnostic API,not economic regime proof.|
| GARCH finite grid;`stocks/models.py:72` |Gaussian conditional likelihood,h(next)=ω+α(r−μ)²+βh;training sample mean/variance;constant baseline and bounded grid.|New two-step .01→.008→.007 variance/log-likelihood reference passes;existing grid likelihood/bounds tests. No global MLE or parameter confidence intervals.|
| GARCH coordinate search;`stocks/advanced_models.py:5` |Logω/simplexαβ,α+β<.995,≤120iterations;fixed mean/initial variance;retain boundary grid if better.|Existing candidate/likelihood/constraint tests and SEC/stock cohorts;UI explicit conditional search. In-sample optimization,not forecast superiority.|
| Kalman;`stocks/models.py:110` and fixed demo `research.py` |Scalar local level,Q=1e−5,R=.001,initial mean0/P1;Joseph covariance. Missing observation predicts variance only.|New closed-form first gain/posterior and missing prediction passes. No fitted noise/state model or hidden fair-value claim.|
| Holdouts/walk-forward;`stocks/evaluation.py` |Fit only training;carry filtering/variance through validation then test;≤4 expanding folds,5validation/5test,unused suffix disclosed.|Existing future-mutation/heldout references rerun. Caller chronology is not authenticated timestamps;dependent folds,no model-selection/significance correction.|
| Portfolio;`stocks/portfolio.py` |1–4 explicit assets,20–64 aligned returns,net weights1/gross≤3;exact n−1 covariance,weighted returns,empirical tails,Gaussian tails,wealth/drawdown,scenarios.|New alternating two-asset case gives exact variance1/237500 and VaR/ES1/500;covariance identity holds. UI explicit weights;not actual holdings,optimizer,leverage finance or Euler attribution.|
| Raw bars/risk;`stocks/price_research.py`, `risk.py`, `datasets.py` |Exact simple returns/moments;binary64 sqrt/logs;historical worstceil(5%N) tails;matched interval start AND end across immutable revisions.|Stock207,exact alignment/revision/capacity tests;cached/history research UI. Raw unadjusted prices,session gaps,corporate actions/selection may dominate. No full-history guarantee.|
| Toy causal backtest;`stocks/research.py` |Long if strictly preceding5returns sum positive;otherwise flat;1bp linear turnover cost,constant-weight wealth recursion,no end liquidation.|New constant path wealth=(10099/10000)(101/100)^14 and future-change prefix invariance passes. No spread/fees/impact/partial fills/short funding or actual strategy selection study.|
| Stress scenarios;`stocks/risk.py:26` |Declared signed quantity×price×shock,exact rational outputs;bounded inputs,no inferred USD/holdings.|Existing independent long/short/shock references;UI assumptions only,no option convexity/correlation/margin.|
| SEC descriptors/accounting;`stocks/financials.py`, `accounting.py` |12 exact period-aligned ratios/growth/FCF,explicit concept/unit/missingness,positive denominators,begin/end balances where required;residual checks not fabricated identities.|Source142/stock207 and provenance/period/ambiguity tests. Selected tags,not reconstructed complete statements;filing/acceptance time limits remain.|
| Synthetic execution/TCA;C++ `simulation/simulator.hpp`, `execution/execution.hpp` |Separate deterministic FIFO synthetic matching;latency seed,jitter,reports/partial fills. TWAP bins,ex-ante VWAP weights,causal POV;exact benchmark/fee decomposition.|Native execution/simulation/export/oracle tests rerun. Browser uses fixed authored liquidity,zero-fee scenario;not a broker or empirical execution-quality model.|

## Absent or not established

No implemented cointegration/pairs trading,statistical-arbitrage selection,
cross-sectional factor model,portfolio optimizer or Euler risk decomposition was
found in production source. Do not infer these from broad historic candidate lists.
Their addition requires a separate justified specification;they are not all
mandatory repairs to current read-only research. No reliable signal-generation
service or empirical walk-forward trading result is established.

Native/Python interfaces expose more mechanics than every browser workspace.
CLI ITCH/LOBSTER ingestion/reconstruction and source-preserving exports exist;
browser import is explicitly absent. Calculation existence is not end-to-end
research dataset availability. Actual prices/filing history/complete initialization
cannot be synthesized to make these workflows look populated.

## Correctness verdict

New9 Python independent checks pass,including2 paper-boundary negative tests.
New14 geometry/mathematical checks pass. Existing model/source207+142 cohorts,
native940 cases and exact reference hashes were actually rerun. These support
the finite stated algorithmic contracts. They do not certify arbitrary parameter
space,economic validity,causal market impact or profitable signals. The committed
browser display assertion fails separately;raw pricing correctness was verified.

Before relying on a real research result:bind exact source/date/universe,rights,
adjustments/session/missingness and as-of availability;declare estimator and costs;
use independent references/negative controls;validate out-of-sample with uncertainty,
selection and survivorship considerations;retain reproducible input/config hashes.
Where those facts are absent,the honest output is UNVERIFIED,not an investment signal.
