# Coinbase Exchange: supervised provisional candidate

terminal/providers/coinbase_candidate.py implements an independently authored,
legacy Exchange-shaped profile, not a currently verified Coinbase protocol adapter.
The current official documentation/terms remain blocked; no fresh denial retry,
provider socket, subscription, account, market-data collection or recording occurred.
A separate Coinbase UI choice and permission-gated supervisor are implemented. Neither provider is enabled by default; no Coinbase live qualification is claimed.

Assumptions tested with toy data only:
- snapshot(product_id,bids,asks), absolute l2update(changes,time), match/last_match,
  subscriptions and heartbeat. Unknown types/fields explicitly reject.
- BTC-USD and ETH-USD are separate configured identities, never Kraken symbols/venues.
- Exact representation scale1e8 for both price/quantity; this is not a verified venue
  tick/lot rule. Reject off-unit, invalid side, duplicates, overflow and crossed candidate.
- Bounded64KiB JSON,256 levels/side and256 changes/message. No top-N truncation that
  pretends to reconstruct deeper liquidity. Real full snapshots can exceed this budget
  and must reject; the candidate is not claimed sufficient for full production depth.
- A callback applies one native AggregateDepth transaction only after validation.
  Error/disconnect requires a fresh snapshot. Trade identities are bounded128.
- Optional source sequence is preserved exactly as metadata, never passed off as a
  contiguous L2 sequence. No universal gap proof or CRC is invented.
- Match side is a maker-side *candidate* role from legacy assumptions, not silently
  used as aggressor direction. Source order references, if supplied, stay external
  observations and do not create resting L3 identities. Current semantics need review.
- last_match is classified historical, not a new live arrival. Heartbeats cannot make
  unchanged depth fresh. Injected fixture status is always HISTORICAL_SYNTHETIC/not LIVE_VERIFIED. The fixed real transport may use LIVE_OBSERVED only after separate permission gates.

Twelve candidate and nine supervisor native-backed authored tests cover exact levels, absolute deletion, sequence
scope, missing snapshot, product isolation, candidate/native rejection atomicity,
maker-side distinction, dedup, freshness, resource limits, unsupported data and resync.
They establish this declared profile's behavior, not current compatibility or rights.

Next: obtain current official channels/message/sequence and applicable usage evidence
from docs.cdp.coinbase.com and Coinbase legal sources; reconcile/version differences;
then reconcile the provisional bounded transport/supervisor against that evidence. See PROVIDER_QUALIFICATION_GUIDE.md for separate gates, depth scopes and the owner handshake check.
No source mixing, guessed free entitlement, unrestricted retention or new live claim.
