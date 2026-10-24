# Metric scope

Phase 3 IMPLEMENTED (see PHASE_3_CONTRACTS.md): spread a-b, midpoint (a+b)/2,
microprice (a*qb+b*qa)/(qb+qa), and declared-depth imbalance (Qb-Qa)/(Qb+Qa).
Use checked exact intermediates; midpoint may require half-tick precision. Empty
sides, missing depth and zero denominators yield explicit unavailable states.

Phase 4 IMPLEMENTED: OFI, quote/tick signing, event intensities, effective/realized
spread, horizon impact, exact sampled returns/variance and approximate volatility.
See PHASE_4_CONTRACTS.md for lag, causal timing, sampling, invalidity and missingness.
LATER / EXPERIMENTAL: Kyle-style regression, VPIN and calibrated impact models.
Each metric needs definition, units, assumptions, required inputs, timestamps,
sampling, invalid states, numerical limits and independent reference tests before
using the established financial name. No economic results exist yet.
