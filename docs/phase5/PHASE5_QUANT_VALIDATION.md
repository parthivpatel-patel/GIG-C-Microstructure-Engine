# Chronological model validation

**COMPLETE bounded mechanics:**evaluation.py fits HMM/GARCH only on a declared training
prefix,then scores validation/test likelihood with fixed fitted parameters. Validation
observations update filtering/conditional variance state,not parameters. Test conditioning
uses past observed state. Constant-Gaussian baseline uses training-only mean/variance.
Training/dataset/configuration identities,split indices and declared limitations returned.

HMM uses existing deterministic Gaussian Baum-Welch;GARCH remains the finite likelihood
grid,not a continuous/global MLE. Five conditional variance horizons use h_next then
omega+(alpha+beta)*h for expected future innovation variance. Existing Kalman prediction,
Joseph covariance and missing-observation checks preserved. Missing HMM inputs reject;
missing-observation HMM estimation remains NOT IMPLEMENTED rather than silently dropping.

Bounded walk-forward starts20 training observations,then5 validation/5 test;expands by5,
refits each fold,max4 folds. Unused suffix count is explicit. Adjacent fold test blocks do
not overlap,while past test observations may later become available training/validation
history. Scores are dependent;no false confidence interval or forecasting significance.
No randomness in estimators;configuration and dataset hashes support local reproduction.

Independent tests:state-label permutation invariance,existing16-path forward-likelihood
oracle,normalization/EM constraints,training/test mutation controls,prefix-preserving
walk-forward mutations,GARCH recurrence/baseline and Kalman references. Changing future
held-out observations cannot change previously trained parameters or earlier fold scores.

**NOT VERIFIED:**observed out-of-sample performance,actual point-in-time data,causal
corporate-action/filing vintages,parameter uncertainty and continuous optimization.
Array order is caller-declared,not an authenticated time series. UI labels authored inputs
and binds displayed evaluations to the exact returns/split/mode inputs. No live forecasts.
