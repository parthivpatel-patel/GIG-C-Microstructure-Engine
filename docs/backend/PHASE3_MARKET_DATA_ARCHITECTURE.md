# Phase 3 market-data architecture

Existing gated provider fetch → provider-specific validation → history.normalize →
accepted process cache → exact descriptive analytics → cache-only v2 API → ATLAS.
No browser-supplied destination,automatic acquisition,pagination expansion or gate change.

`HistorySource` is frozen and carries provider,feed,coverage,adjustment,origin,
entitlement statement,receipt and explicit provider-reported price/volume units.
Neutral normalization accepts1..4 already acquired primitive pages,max256 total bars,
2MiB serialized input and bounded64-character fields. Producer digests are64 lowercase
hex. Every page/row is checked before publishing;bad later pages cannot partially
commit. Duplicate nanosecond timestamps,decreasing order,invalid OHLC/volumes or malformed
metadata fail. Input objects are not mutated. Existing workspace's last accepted cache
survives normalization failure;separate error metadata identifies rejected refresh.

Source bar timestamps require the existing UTC-Z wire grammar and signed64-bit ns
range;original wire and exact ns are retained. UTC display is labelled microsecond
precision. Receipts separately accept UTC-Z orUTC+00:00. Input offsets are not silently
reinterpreted. Prices/volumes retain exact decimals;no share/lot inference.

Nominal minute/hour/day gaps are candidates only. No holiday,halt,DST-session or auction
calendar is fabricated. has_more preserves bounded provider pagination;no advertised
next page does not prove complete history. Raw/split/dividend/all/unknown adjustment
policy stays explicit. Historical state is HISTORICAL for accepted official-source
receipts,SIMULATED for injected authored bodies. A newly downloaded historical response
is never LIVE. Missing cache is BLOCKED when access gates prohibit acquisition,otherwise
UNAVAILABLE. Cache age and refresh failure stay separate from market-observation age.

GET /api/v2/companies/AAPL/historical accepts no query parameters and does not acquire
or mutate state. Schema:terminal/server/schemas/backend_history_v2.schema.json.
It exposes source integrity,coverage,exact descriptive research and cache metadata.
Canonical digest scope explicitly excludes derived research and ephemeral cache ages.
V1 remains compatible with an additive history_integrity summary rendered in ATLAS.

`ObservationMonitor` is offline preparation,not an Alpaca client. Authorized adapter
state can represent LIVE/DELAYED/SIMULATED/STALE;without permission or a fresh acknowledged
observation it is BLOCKED/UNAVAILABLE. Generations fence delayed previous-connection
messages. Reconnect clears acknowledgements/receipts;heartbeats affect transport only.
Monotonic receipt clocks are not exchange latency. Maximum8 subscriptions;invalid
clock,unknown/stale generation or excess subscriptions reject before accepted mutation.
No network code invokes this monitor yet. Alpaca protocol authentication,rate-limit
backoff,wire subscription/heartbeat semantics and actual reconnect driver remain missing.

Resource bounds are deliberately conservative,not performance promises. The cache still
stores only the latest accepted query per each of8 symbols;no persistent history cache,
automatic multi-query cache,real exchange calendar or complete upstream paging is claimed.
