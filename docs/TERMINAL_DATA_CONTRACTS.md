# Terminal transport v1

HTTP `/api/v1/state` and WebSocket `/api/v1/stream` deliver the same owned snapshot.
`schema_version` is string1. Modes:HISTORICAL_REPLAY,SIMULATION,LIVE.
Observation categories:LIVE_OBSERVED,LIVE_DELAYED,HISTORICAL_OBSERVED,
HISTORICAL_SYNTHETIC,SIMULATED,ESTIMATED,UNAVAILABLE. Current observed modes are
unavailable, never backed by synthetic fallback. One browser session shares a
single native owner with other connected clients; not multi-user isolation.

Financial integers are canonical decimal strings; metrics preserve exact rational
numerator/denominator strings or null. Prices are ticks divided by price_scale;
quantities are units divided by quantity_scale. BigInt formatting preserves values
above JS safe integer; normalized geometry alone uses bounded approximate floats.
Counts/positions are bounded JSON integers, not financial quantities or source IDs.
No source exchange sequence is invented from the replay position or render revision.

State includes:mode,origin,instrument/provider/venue/feed_type,book bids/asks
(price_ticks/quantity strings),revision,metrics,position/event_count/playing/speed,
source_timestamp_ns,replay_time_ns,received_at_ns,feed,provenance,capabilities,
engine,diagnostics and notifications. Missing metadata remains null; authored
logical time is not a historical market clock. The native event wire stays v1.0.

POST control accepts action/value only:play,pause,step,restart,speed(1/2/4/8),
seek(bounded source position),mode,connect. Live connect returns explicit unavailable
status, not a successful subscription. Seek reconstructs an authored prefix from
its declared complete empty boundary; it does not seed from visible aggregate data.
POST simulate accepts algorithm(TWAP/VWAP/POV),canonical quantity1..1000000,
slices1..16 no more than quantity. All fills/benchmark/latency/TCA are SIMULATED.
POST validate accepts only profile itch/lobster; whitelisted authored native
executables,20s deadline/192KiB per output pipe,no private paths or external URLs.
These results are native diagnostics, not imported interactive observed replay.
POST recording accepts save(enabled:true)/verify/load/delete for one fixed authored
source identity. No user path/origin/event payload. Off by default,observed forbidden.

4KiB request bodies,5s read deadline,30 mutations/sec,8 WS clients,2s send deadline,
latest-state publication at10Hz. Intermediate render snapshots can coalesce; native
source events remain deterministic and are not silently discarded. Every mutation
requires configured exact Origin,Host is allowlisted; local single-worker deployment.
No concurrent native access, upload or arbitrary filesystem API. A browser frame is
not an authenticated research export; exported view snapshots preserve classification
and provenance but do not claim the complete engine run-manifest export contract.

Machine-readable snapshot grammar:terminal/contracts/state.schema.json,served at
GET/api/v1/schema. Independent tests validate both sources/all modes;TypeScript
validator separately enforces mode/origin compatibility and exact BigInt values.
JSON Schema specifies bounded lexical representations;native checks supply numeric
range/cross-field semantics. No remote schema resolution is used. Fixture v2 has
no exchange EventTimestamp;replay logical time is separate. Dataset selection accepts
terminal-authored-v2 or kraken-authored-profile-v1 only. No private source path.
