# Bounded descriptive L2 research methodology

The native C++ AggregateDepth remains the financial book owner. Existing exact
native spread/midpoint/microprice/depth totals/imbalance are preserved. New window
research is a separate bounded Python Fraction module at display cadence, not a
replacement native book, inferred L3 or an empirically validated trading strategy.

Scope: one venue, symbol, capture segment and receive-monotonic clock. Every event
uses captured ordinal tie-breaking. No exchange timestamp is invented, aligned to
receive clock, or assumed unique. Native supervisor samples research at most4Hz;
its explicit as_of_receive_ns can lag current native book by250ms. Recorded research
is computed from each validated native prefix at load, with no future prefix access.

Definitions:
- Relative spread=(ask-bid)/mid; depth imbalance=(sum bid-sum ask)/(sum bid+sum ask).
- Weighted midpoint and microprice intentionally use the same top-quantity weighted
  formula (ask*bid_qty+bid*ask_qty)/(bid_qty+ask_qty); they are not independent signals.
- OFI follows best-price displayed-size indicator changes for adjacent complete
  captured quotes. It does not identify executions, orders, cancellations or queue.
- Replenishment/depletion sums positive/negative quantity changes only at prices
  present in adjacent subscribed views. Entry/exit at depth boundaries is excluded.
- Trade intensity uses actual retained arrivals divided by the available captured
  exposure, not an invented full10s interval. Historical trade snapshots are excluded.
- Reported-side net quantity retains source side semantics. Effective spread is
  unavailable unless aggressor-side semantics are explicitly confirmed in server
  GIG_LIVE_AGGRESSOR_SIDE_REVIEWED=1 after current documentation review. It uses a
  strictly prior captured valid quote, maximum age10s, quantity weighting and no
  future quote; receive causality is not proof of exchange-time ordering.
- Realized variance sums squared simple midpoint returns at event arrivals; it is
  neither regular-sampled nor annualized. The square root is separately labelled
  approximate Decimal34, while the variance remains exact.
- Concentration is top occupied quantity divided by observed-side depth, not a
  hidden-liquidity measure or whole-market concentration claim.

At most128 quote and128 trade observations are retained. Requested window is10s,
configurable1ns..60s through trusted code. Warmup/effective-start and truncation flags
are explicit. Coverage-dependent metrics become unavailable when needed observations
were evicted; no misleading whole-window result. Missing/crossed quotes, stale prior
quote, zero denominators and sparse observations are not replaced with invented data.
Exact arithmetic has1024-bit capacity; oversized reduced results return an explicit
unavailable reason without corrupting the native book. Source resnapshot resets scope.

Independent evidence: hand-derived rational cases,2,000 seeded integer OFI candidates,
future-quote negative control, simultaneous timestamps, historical trade snapshots,
missing/stale/crossed quotes, resets, truncation, exact input grammar and boundaries.
Native core and independent level-map/Fraction oracles remain unchanged. No real
observations were collected, and these tests do not establish empirical accuracy.

Kyle's lambda, Lee–Ready, VPIN, predictive features and future-horizon impact are
not added merely to display numbers. They require reviewed sign conventions,
clock/lag selection, sampling/volume-bucket choices, sufficient observations and
independent empirical calibration. Current live/rights verification is still blocked.

Compatibility note: reviewed candidate hardening now rejects unknown heartbeat/trade
fields instead of silently discarding them; optional source ord_type is retained only
when present. Older provisional logs with previously ignored extensions may be refused
on strict normalization replay. They are not silently migrated or relabelled. Existing
authored raw fixture identities and the eight native canonical identities are unchanged.
