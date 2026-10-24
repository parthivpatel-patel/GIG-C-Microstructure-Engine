# Phase 4 trade, quote and flow analytics

IMPLEMENTED / MUST HAVE: a pure bounded offline calculation over explicit ordered
quote/trade observations, as-of time and configuration. Outputs expose const getters,
owned per-trade results and every parent snapshot/journal reference (including
pre-window context). Quotes can be formed from validated healthy replay depth.
No exchange adapter, live service, inferred missing events or hidden calibration.
Kyle lambda and VPIN are LATER / EXPERIMENTAL, not implemented: this synthetic input
has no defensible volume-bucket calibration or causal impact-regression population.

## Clock, scope, observation and availability contracts

One run/instrument/venue/session/epoch, identical instrument rules, declared common
UTC clock identity. Times must be nondecreasing and journal prefixes strictly
increasing within each family. Combined prefix/time order is checked without
sorting; backwards clocks reject. Equal-prefix quote/trade views must agree on time.
Every supplied timestamp must be <= as_of; future inputs reject rather than hide
look-ahead. Clock identity is a declared synchronization assumption, not verified
physical clock calibration. Reset/session changes reject: partition the calculation
and carry explicit continuity flags. A gap-marked window produces unavailable metrics
and unknown signs, not biased complete-window estimates.

Window is (as_of-window_ns, as_of], integer nanoseconds. Positive window and sample
interval, exact divisibility and <=4096 intervals; <=4096 quotes and <=4096 trades
including context. Quote/trade prices and quantities obey declared rules; positive
quantity, valid level counts, noncrossed top and checked combined quantity. Empty or
one-sided quotes are explicit. Observations may be arbitrarily old context; quote
selection requires last timestamp <= target and age <= max_quote_age. It never
skips a newer one-sided quote to revive an older two-sided quote. Book snapshot
references describe accepted source state; manually supplied refs remain caller claims.

quote_lag >=0 is an explicit research convention, NOT a universally correct default.
Signing uses last quote at/before trade_time-quote_lag, within max_quote_age measured
at that target, and STRICTLY EARLIER journal prefix than the trade. Thus no same-
event posterior quote or equal-time later record signs the trade. Above midpoint is
buy, below is sell. At midpoint, tick test uses previous trade price change; repeated
prices inherit the last nonzero tick, using provided causal pre-window context.
Without a valid quote or prior nonzero tick where required, direction is unknown.
This is Lee–Ready-style quote/tick signing, not a claim of true aggressor identity.
No exchange execution's resting side is silently relabeled as observed aggression.

## Formulas and units

For consecutive top updates, bid price/quantity B,b and ask A,a (previous subscript 0):

    e = 1[B>=B0]*b - 1[B<=B0]*b0 - 1[A<=A0]*a + 1[A>=A0]*a0
    OFI(window) = sum e for quote observations in the window

Units lots. Need a predecessor at/before the left boundary, complete top updates,
two-sided observations and no over-age intervals. Missing predecessor, stale terminal
quote, one-sided transition, gap or complete_top_updates=false makes OFI unavailable.
No updates within a covered window gives exact zero, never an invented quote event.
Trade/quote intensities count supplied canonical observations in the window divided
by window seconds (events/second). Completeness is a caller/run-manifest assertion;
zero intensity is valid only under that assertion. These are event intensities, not
volume intensities or a point-process fit. The input journal defines what is counted.

For signed trade direction s in {-1,+1}, trade price P, causal contemporaneous
midpoint M0 (last quote <=trade_time with earlier prefix), horizon H>=0 and carried
midpoint MH at/before trade_time+H:

    effective spread = 2*s*(P-M0)
    realized spread  = 2*s*(P-MH)
    price impact     = 2*s*(MH-M0)

Units ticks, signed values permitted. When all available, effective=realized+impact.
Lag controls SIGNING, not the contemporaneous M0 spread benchmark. Horizon price is
last-observation-carried-forward with declared max age, not the first later quote.
Results are retrospective research outcomes published only once as_of>=trade_time+H.
H=0 uses the same causal pre-trade quote. Pending horizons, unknown signs, stale or
one-sided observations remain explicit missing states; no future fill/decision uses
these results. These are quoted-price diagnostics, not calibrated causal impact.

Fixed sampling grid from window start through as_of inclusive, previous-quote carry
with age bound, all midpoints positive:

    simple return r_j = M_j/M_(j-1) - 1
    window return = M_end/M_start - 1
    realized variance = sum_j r_j^2
    realized volatility = sqrt(realized variance)

Returns/volatility dimensionless over the declared window, NOT annualized/log-return
or drift-adjusted volatility. Zero denominator and nonpositive reference are explicit
invalid states. Missing grid observations invalidate the whole variance rather than
silently changing frequency. No interpolation with future quotes. Variance/returns
use exact rational arithmetic; sqrt is explicitly approximate long double, checked
finite. Long-double last bits are not cross-platform canonical evidence.

## Safety, complexity, alternatives and validation

Exact operations use Phase 3's checked 128-bit intermediate contract. Individual
capacity failures produce arithmetic_capacity metric states; a global arithmetic
failure returns structured error. No silent overflow or round/truncate to integer.
Output vectors use caller-owned PMR (default provided); resource must outlive result.
Calculation stages complete owned outputs; bad_alloc returns resource_exhausted with
no input mutation or partial result. Two reached PMR fault positions are tested,
including cleanup of the first allocation when the second fails.

Baseline time O(Q*T + Q*S + Q + T), S<=4096 grid points, memory O(Q+T) parent/trade
outputs. Linear quote search is intentionally simple and bounded; future profiling
may justify a monotone cursor/binary search, with independent equivalence tests.
No callbacks, external I/O or mutable state inside the calculation. Interview defense:
explicit causal source prefixes prevent a subtle equal-timestamp look-ahead bug,
and complete-window validity prevents apparently precise statistics on missing data.

Independent Python Fraction compares 2000 deterministic randomized OFI/sign/spread/
return/variance cases (seed 4099). Hand examples test spread decomposition, tick-rule
repeats, quote lag, stale clocks, missing sides, pending horizons, gaps/session reset,
sampling divisibility, zero midpoint and source refs. All inherited suites remain.
Benchmark uses a real five-record replay with three complete top states and one print,
checks hand-worked OFI=30 and effective/realized spread=2/0 ticks, embeds the canonical
journal in the manifest, records raw timing/PMR scope and never claims production speed.
