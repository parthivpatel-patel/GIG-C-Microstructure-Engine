# Phase 3 quantitative validation

Input is validated returned historical bars,not invented market history. Exact Fraction
arithmetic computes close-to-close simple returns,total return,maximum close drawdown,
mean,sum of squared returns,sample variance(n−1),and95% empirical loss-tail VaR/ES.
At least20 returns are required for tail estimates;tail is worst ceil(5%N),not a claimed
population quantile confidence interval. Existing exact4096-bit output limits remain.

New realized simple-return volatility is sqrt(sum r²),unannualized,binary64 approximation
with its exact squared quantity available separately. It is not demeaned sample standard
deviation or exchange-calendar annualized volatility. Missing samples/capacity failures
are null with reasons. Raw corporate actions/gaps/session uncertainty can dominate these
metrics;this is descriptive returned-interval research,not an adjusted total-return study.

Independent tests use256 seeded integer closes,Fraction formulas for every return,
maximum preceding peak and13-of255 loss tail. A separate80-digit Decimal.sqrt checks
100→110→99:returns±0.1,sample variance1/50,realized volatility sqrt(1/50).
No expected output is copied from production output.

GARCH/HMM/Kalman remain existing fixed-parameter causal illustrations;new recurrence and
prefix tests preserve their honest labels. No GARCH likelihood estimation,HMM training,
Kalman parameter fit,residual diagnostics,predictive accuracy or observed out-of-sample
performance is claimed. Those require pre-registered,permitted,adjusted data and research
protocols. The native microstructure/matching/replay/TCA matrix is separate from these
statistical limitations. Mathematical agreement is not empirical forecast validation.
