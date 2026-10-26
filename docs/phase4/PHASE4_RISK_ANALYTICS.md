# Descriptive risk and authored scenarios

GET risk uses accepted cached close observations only and returns source hashes/data
state. At least20 returns is an engineering minimum,not sufficient statistical precision.
No accepted source yields explicit UNAVAILABLE. No source acquisition occurs on GET.

* Historical VaR/ES:exact Fraction simple-return losses;worst ceil(5%N) order statistic
  and mean of that same tail;confidence0.95,uninterpolated returned-interval convention.
* Normal parametric VaR:−sample mean+Phi^-1(.95)*sample standard deviation(n−1).
  Binary64 approximation;Gaussian assumption,not empirically calibrated tails. Negative
  loss quantiles remain negative,not silently clipped.
* Log returns:binary64 log1p(exact simple return),with log-ratio fallback near rounded−1;explicitly approximate.
* Rolling volatility:20-observation,n−1 sample standard deviation,not annualized.
* Existing exact drawdown/simple returns/realized volatility remain available in Phase3
  descriptive research. Raw corporate actions and session gaps can dominate estimates.
* Linear scenario:explicit authored signed quantity×positive price exposure;P&L=exposure×
  supplied fractional shock. Up to16 shocks in[-1,10]. Exact decimal/Fraction arithmetic,
  no exponent/rational-string bombs;bounded magnitudes and input length. Currency is
  user-price currency,not inferred USD. No actual holdings,options convexity,margin,
  liquidity,correlation or portfolio aggregation inferred.

Every risk report states method,confidence,horizon(one supplied bar interval),sample
count,units(fractional return),assumptions and limitations. These are descriptive estimates,
not observed future losses,portfolio coverage or validated forecasts. Independent loss-tail,
rolling-count and signed-shock references support tests. Normal-tail estimation accuracy,
portfolio exposures and stress calibration remain unverified.
