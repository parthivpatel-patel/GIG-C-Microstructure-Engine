# Quantitative contracts reviewed in this sprint

October 29, 2026, America/New_York. These are bounded research algorithms,not
empirically calibrated trading models. No new statistical-arbitrage,portfolio
optimization or forecasting product is asserted. Source traceability and deferred
candidate areas are in `REMAINING_GAPS.md`.

## Fixed-parameter Gaussian HMM: repaired numerical boundary

Implementation: `terminal/stocks/advanced_models.py:missing_hmm`.
Two states,at most256 ordered emissions;each emission is either missing (`None`) or
an authored decimal string representing a return in[-1,1] with at most12 decimal
places. Parameter means,variances,prior and2×2 transition matrix are length2 lists or
tuples of finite binary64-representable real numbers. Boolean values are rejected.
Variances are strictly positive;prior and transition probabilities strictly positive
and normalized within1e-12. No parameter is fitted by this function.

Let p(t-1,i) be the previous posterior and A(i,j) the transition probability.
The initial prior is supplied directly;for subsequent records q(t,j)=Σᵢp(t-1,i)A(i,j).
For an observed return r(t),the log emission is

```text
z(j) = (r(t)-mean(j))/sqrt(variance(j))
log f(j) = -0.5*(log(2*pi)+log(variance(j))+z(j)*z(j))
ell(j) = log(q(t,j)) + log f(j)
log Z(t) = logsumexp(ell)
p(t,j) = softmax(ell)
```

The observation log likelihood sums log Z(t). For a missing emission,its likelihood
is1,the transition still advances and p(t)=q(t). No imputation,dropping of clock
positions or future smoothing occurs. Inputs are not modified.

Previously `log(2*pi*variance)` overflowed for finite variance1e308,producing all-inf
log weights and NaN probabilities. Separate logarithms avoid this intermediate
overflow. Standardized multiplication avoids Python `**2` raising on large finite
residuals. A negligible state can have zero binary64 posterior while another valid
state remains usable. If every log weight or accumulated likelihood is beyond
binary64 capacity,the function raises fixed `ValueError('hmm_likelihood_capacity')`;
it does not return NaN or silently floor/clip the model's parameters.

The output retains per-record probabilities/observed flags,total observed log
likelihood and the existing explicit method description. Normal finite results can
differ by a few rounding bits from the old expression;no bitwise HMM-output guarantee
was invented. All eight independently frozen **native** reference hashes are unchanged.

Independent tests enumerate every latent-state path for short authored inputs using
70-digit Decimal Gaussian densities and marginalize by final state. Additional tests
cover missing emissions,prefix causality,large finite variance,one negligible state,
capacity failure,malformed parameters,nonfinite values,and the256-record budget.
Existing label-permutation and deterministic fit tests are retained. Complexity is
O(4T),memory O(2T) for returned probabilities;T≤256. Performance measurements include
allocations and are shared-host diagnostics,not a forecasting-performance claim.

## Existing research algorithms and their limits

| Algorithm | Actual calculation/input | Integration / validation boundary |
|---|---|---|
| Fitted HMM | Two-state Gaussian Baum-Welch,deterministic initialization,variance/transition floors,nondecreasing accepted likelihood | `models.py`,model endpoint,ResearchDiagnostics. Full-sample parameter estimation leaks future information into historical fitted probabilities;chronological evaluator fits training only |
| GARCH grid | h(next)=omega+alpha*residual²+beta*h;Gaussian conditional likelihood,constant-variance candidate plus bounded grid | Independent recursion and likelihood reference;not continuous/global MLE or empirically calibrated forecast |
| Constrained GARCH search | Positive omega and simplex alpha/beta with alpha+beta<.995;deterministic coordinate search,max120 iterations,grid boundary retained | Research control/API and independent likelihood/constraint tests;fixed sample mean/initial variance,no parameter confidence intervals |
| Kalman | Scalar local level,fixed Q=1e-5,R=.001,Joseph covariance update;prediction-only on missing observations | Model diagnostics and fixed authored demonstration;not fitted multivariate estimation |
| Portfolio risk | Exact supplied aligned simple returns/weights,sample n-1 covariance,w'Σw,empirical worst ceil(5%N) tails,Gaussian approximation,drawdown/scenarios | Up to4 assets,20–64 intervals,net exposure1/gross≤3;no optimization,inferred holdings,FX or calibrated tail forecast |
| Chronological evaluation | Training-only HMM/GARCH fits,conditional validation/test likelihood,state updates using only prior observations;max4 expanding folds | Independent future-mutation tests;caller-supplied order is not authenticated PIT evidence,fold scores dependent |
| Authored backtest | Long only when preceding5 returns sum positive;linear1bp turnover cost,current return excluded from signal | Exact rational positions/terminal wealth;not executable fills,slippage calibration,model selection or empirical alpha |
| L1 / native microstructure | Exact best-quote spread/mid/size imbalance;native conditional OFI,lagged trade sign/impact;retained-window realized variation | Only eligible supplied observations;units,continuity,clock and provenance limits remain explicit |

## Analytical execution boundary: repaired cancellation

`terminal/server/analysis.py` owns one worker task per application/event loop for
diagnostic fits,GARCH search,chronological evaluation,ratio history and dataset
analysis. Admission contains no suspension before worker assignment. Request
cancellation is shielded from the thread future;later analytical requests return
their structured429 busy error until physical work finishes. No per-request work
queue is created. Worker exceptions are consumed even if the browser disconnects;
normal request errors still reach the existing sanitized API handlers. Completed
jobs are not retained as a result/input history. Graceful lifespan shutdown closes
admission and drains any accepted worker.

This is not preemptive thread termination or a hard wall-clock shutdown guarantee.
It is not a host-wide or multi-process quota. The worker only runs existing bounded
read-only Python calculations;native C++ book ownership and trading controls are
unchanged. Cancellation cannot grant provider access,retain observed data or mutate
the native book. Dataset analysis now shares this budget,with additive structured
`DATASET_ANALYSIS_BUSY`429;normal successful schemas remain unchanged.
