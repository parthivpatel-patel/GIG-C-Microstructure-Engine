# Metric scope

Phase 3 IMPLEMENTED (see PHASE_3_CONTRACTS.md): spread a-b, midpoint (a+b)/2,
microprice (a*qb+b*qa)/(qb+qa), and declared-depth imbalance (Qb-Qa)/(Qb+Qa).
Use checked exact intermediates; midpoint may require half-tick precision. Empty
sides, missing depth and zero denominators yield explicit unavailable states.

SHOULD HAVE later: OFI, trade classification, intensities, effective/realized
spread and horizon impact, with documented lag, sampling and unknown states.
LATER / EXPERIMENTAL: Kyle-style regression, VPIN and calibrated impact models.
Each metric needs definition, units, assumptions, required inputs, timestamps,
sampling, invalid states, numerical limits and independent reference tests before
using the established financial name. No economic results exist yet.
