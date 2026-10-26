# Diagnostic quantitative models

New models.py has bounded deterministic offline fitting alongside the unchanged existing
fixed-demonstration endpoint. All models use explicitly authored20..256 decimal returns
in[-1,1],also subject to the4096-byte HTTP envelope. No observations are invented or
labelled company data. Parameters and in-sample assumptions are visible.

HMM:two Gaussian states;log-domain forward likelihood,backward responsibilities and
Baum-Welch updates;deterministic mean-offset initialization,variance floor1e-12,
transition/initial-probability floor1e-6,max40 updates. Trace,iterations,relative-likelihood
stopping,collapsed-state/constrained-update/iteration-budget reasons and convergence flag
are returned. Constant samples are unidentifiable,not fitted successes. States are not
labelled bull/bear or inferred exchange regimes. Full-sample fitted parameters contaminate
historical filtered probabilities with estimation look-ahead;the UI warns explicitly.
No global optimum,model selection,predictive accuracy or out-of-sample claim.

An adversarial equal-likelihood case at variance1e-12 reproduced probability sums
0.9999709114517753 and1.00003194669523. Subtracting a huge log normalizer lost precision.
Relative max-shifted weights normalized by their own sum repair filtered probabilities,
responsibilities and transition counts. Independent four-observation16-path enumeration
checks likelihood;negative controls assert equal-state probabilities exactly1/2.

GARCH(1,1):finite Gaussian likelihood grid with positive omega,alpha/beta nonnegative and
alpha+beta<.995;sample mean/initial variance;constant-variance baseline included. Evaluated
candidate count,likelihood,conditional variance and conditional next variance returned.
Grid exhaustion is explicitly not continuous-optimizer convergence or global MLE.
Constant samples are unidentifiable. Independent two-step recurrence/likelihood and
baseline/constraint/determinism tests pass. No fitted innovation distribution or OOS test.

Kalman:fixed scalar local-level Q=1e-5,R=.001,mean0,covariance1. Explicit missing observation
performs prediction-only update;Joseph covariance update preserves nonnegative variance.
It is not parameter estimation. Independent missing/prediction/covariance references pass.

Correlations,multivariate covariance,model uncertainty,robust empirical calibration,
rolling refits and pre-registered causal train/test protocols remain separate work.
