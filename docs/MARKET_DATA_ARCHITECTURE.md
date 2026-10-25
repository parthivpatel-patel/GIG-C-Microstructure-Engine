# Market-data boundaries

Authored native L3 events -> existing single-owner Replay -> owned snapshot/exact
analytics -> Starlette gateway -> bounded latest-state WebSocket -> React views.
Independently authored provider-shaped fixture -> provisional Kraken normalization /
CRC profile -> separate native AggregateDepth -> owned exact analytics -> same API.
That second path is HISTORICAL_SYNTHETIC,never LIVE_OBSERVED. Aggregate L2 state
has no order IDs,FIFO or matching inference. Current provider transport is opt-in
code only and is not activated by UI/default startup.

L2 native snapshot/absolute updates stage both sides and exact metrics before
nonthrowing swap; failures preserve revision/sequence/book. Limits<=4096 levels /
side; configured terminal32. Optional exchange sequence accepts contiguous values
only when a provider actually has them; Kraken candidate declares none. Top10
candidate CRC verification is narrower than full market or sequence completeness.
Depth trim generates explicit native deletes. Python prepares receipt/cache/counters
before native commit; trade batches stage replacement bounded deque/set.

Source receipts retain wire decimals/timestamps/missingness. Decimal conversion
uses integer coefficients/divisibility,not binary floating point or context-rounded
Decimal multiplication. Feed lifecycle includes disconnected,connecting,synchronizing,
accepted,stale,gap,recovery; malformed/native failure invalidates source continuity.
A candidate checksum/profile does not establish the current official exchange spec.

No mutable native object is accessed by a worker thread. Gateway asyncio locks /
non-await native calls provide one mutation owner. Private filesystem I/O runs in
bounded whitelisted operations; publication coalesces view snapshots,not source
transitions. No external provider load test,real order or broker access exists.
