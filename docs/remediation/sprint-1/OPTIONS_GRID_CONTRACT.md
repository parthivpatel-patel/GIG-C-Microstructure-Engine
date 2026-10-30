# Options scenario grid v2: valid base versus unavailable auxiliary prices

A04 reproduced valid S=K=1e-6 or1e7 with T=1, sigma=.2:the base price succeeded,
but the auxiliary .6S–1.4S grid invalidated the complete HTTP response (422).
The failing-before regression log is preserved separately from final passes.

Base domain remains exactly `price()`'s bounded contract: S, K∈[1e-6,1e7],
T∈[1e-6,10], sigma∈[1e-6,5], r, q∈[-.5,.5], call or put. Invalid/nonfinite
base inputs still fail; large integer bounds now reject before float conversion.
Valid metrics and optional IV semantics remain unchanged.

The 9×17 auxiliary grid retains all153 original coordinates, input volatility and
ordinary-case prices. No strike is clipped. If a derived strike leaves the declared
price domain, its `theoretical_price` is null and its reason is
`derived_strike_outside_price_domain`. Other calculation errors are not swallowed.
The additive `surface_coverage` contract `gig.options.grid.v2` reports total,
available and unavailable cells. Thus previously rejected base-valid scenarios
now return200 with explicit partial auxiliary pricing; ordinary S=K=100 retains
153identical priced cells. The browser reports priced coverage and preserves exact
metrics/Greeks/grid detail. Its flat input-volatility renderer does not imply an
observed smile or synthesize an unavailable option price.

New tests cover both boundaries, nextafter-adjacent valid inputs, ordinary153cells,
independent elementary-price reference, opposite extreme valid parameters,
nonfinite/oversized/invalid values, origin rejection and native canonical isolation.
