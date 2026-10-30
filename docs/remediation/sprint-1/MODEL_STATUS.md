# Current bounded model status and historical supersession

Release source baseline:`10eaee30d598807a23e42a8b60abe3d5a5dc2514`.
This sprint adds the options-domain repair, proposed concentration postprocessing
and presentation/operational instrumentation. Exact implementation source identity
and test-file hashes are recorded in the sprint evidence manifest.

The preserved older `docs/backend/QUANT_MODEL_VALIDATION.md` is explicitly marked
with its historical source SHA and supersession links; its portfolio NOT IMPLEMENTED
and fixed-only HMM/GARCH rows must not be read as current implementation status.
No old result or test count is retroactively rewritten.

| Current implementation | Actual scope | Remaining evidence |
|---|---|---|
| models.py HMM EM | Bounded deterministic two-state Gaussian local fit | In-sample parameters cause estimation look-ahead; no empirical state validation |
| advanced_models.py missing HMM | Stable fixed-parameter prefix filtering; missing emission likelihood1 | No calibration or inferred economic regime |
| models.py/advanced_models.py GARCH | Finite grid and constrained conditional coordinate search | No global MLE, confidence intervals or predictive superiority |
| models.py Kalman | Fixed Q/R scalar local-level filter, Joseph covariance | No fitted state-space/noise calibration |
| evaluation.py | Train-only conditional likelihood/maximum4expanding folds | Caller chronology is not authenticated PIT; dependent folds |
| portfolio.py | Exact explicit weights, aligned covariance, total risk, tail/drawdown/scenarios | No optimizer, inferred holdings, Euler attribution, execution costs or survival-safe sample |
| options.py | European BSM/Greeks/IV; partial auxiliary-price grid v2 | No observed chain, American/discrete-dividend calibration or scalar-IV conditioning diagnostics |
| server/concentration.py | Proposed exact supplied-depth HHI v1 | Historical estimator definition/acceptance remains OPEN |
| Native book/flow/execution | Exact bounded supplied-state analytics; separate synthetic matching/schedules/TCA | No exchange equivalence, causal impact or observed full L3 calibration |

Summary formatting uses four significant digits, explicit units/approximation and
scientific notation for extreme magnitudes. Zero remains zero; null/nonfinite are
Unavailable. Exact ratios and backend binary64 values remain in expandable JSON.
Frontend formatting does not recalculate financial descriptors or model results.
See [quantitative contracts](../../overnight/QUANTITATIVE_CONTRACTS.md) and
[current coverage/limits](../../overnight/REMAINING_GAPS.md). No empirical forecasting,
profitability, complete statements or production trading claim is authorized.
