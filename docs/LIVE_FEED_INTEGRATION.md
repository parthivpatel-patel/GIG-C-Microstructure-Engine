# Live-feed integration — authored provider readiness, live access blocked

Current supervised candidate implementation: [LIVE_PROVIDER_OPERATIONS.md](LIVE_PROVIDER_OPERATIONS.md).
This section retains its earlier evidence scope; actual external provider qualification remains blocked.

## Actual delivery and boundary

`terminal/providers/kraken.py` supplies a provisional Kraken-v2-shaped L2/trade
normalizer and feed state machine, exercised only with independently authored toy
payloads. Current official documentation and terms are inaccessible through the
managed proxy (CONNECT403; see MARKET_DATA_PROVIDER_MATRIX.md). No real provider
connection, market subscription, observed trade, recording or empirical validation
is claimed. Live mode must expose UNAVAILABLE/BLOCKED instead of toy data.

`live_messages` is an opt-in future WSS transport, never used on import or default
startup. Its Permission record refuses before importing/connecting unless current
protocol review, private-display permission, cloud-processing permission and an
external evidence reference are asserted. This is not a legal verifier; the current
assignment has none of those verified. The terminal must not enable it by silently
setting flags. No route accepts credentials/trading commands. There is no order
submission, broker, paid feed or second provider implementation.

## Candidate profile contracts (not current official confirmation)

- One explicit BTC/USD symbol, ten retained aggregate bid/ask levels. Configurable
  integer price/quantity scales are exact representation choices, not inferred venue
  tick/lot rules. Default100 ticks/USD and100,000,000 units/BTC; nonintegral values
  reject rather than round. No order IDs, FIFO or full-market completeness invented.
- Snapshot is a complete replacement of the declared subscribed ten-level view.
  Updates are absolute level quantities; zero removes the price. Duplicate price
  entries in one side/message reject as ambiguous. Top-ten truncation is explicit,
  with native zero-deletes for discarded formerly retained levels. It does not prove
  deeper liquidity absence. Crossed/locked diagnostics remain a native concern and
  are never automatically uncrossed.
- Candidate CRC32 serializes asks ascending then bids descending, top ten each,
  strips decimal points/leading zeroes from exact wire price and quantity strings,
  and computes unsigned CRC32. An independently coded polynomial oracle checks
  authored expected values. This algorithm must be checked against current official
  Kraken guidance before activation; passing the authored CRC is not proof of
  official compatibility or authenticated market integrity.
- No exchange sequence is assumed or generated. A CRC failure/invalid batch sets
  GAP_DETECTED and requires a new snapshot. An identical last payload has an explicit
  duplicate-payload outcome, not a globally unique exchange event identity. Snapshot
  recovery is allowed even if its bytes equal the previously accepted snapshot.
- Incoming raw numbers are decoded with Decimal and checked integer/rational
  arithmetic; no binary float price/size conversion. Signed values, exponent syntax,
  off-unit decimals, overflow, duplicate keys, unsupported messages and invalid IDs
  reject. RFC3339 UTC time up to9 fractional places is converted to exact integer
  nanoseconds with calendar/boundary checks; original text retained. Receive time is
  explicitly local monotonic ns, not an invented exchange timestamp.
- Bounded trade deduplication retains256 IDs/events. Older IDs outside this window
  cannot be proven duplicates; no unbounded historical uniqueness claim. Prints stay
  separate from displayed-book state. Candidate trade aggressor side is not turned
  into a resting L3 order.

## Ownership and failure behavior

Call `KrakenBookAdapter(apply_native,...)`, then `feed(raw,now_ns)` from one owner.
The adapter builds bounded candidate wire-text checksum state and native projection
before application. Callback arguments are:

```
apply_native(snapshot=bool,
             bids=[{"price_ticks":"integer","quantity":"integer"},...],
             asks=[...],sequence=None)
```

Use native AggregateDepth with capacity>=32 for at most20 changed/deleted levels
per side while the retained provider scope is ten. Native callback must either
accept atomically or raise. Candidate checksum/normalization/native rejection leaves
accepted checksum cache unchanged and marks the feed unusable until snapshot. No
financial metrics/book matching are computed here: the native L2 component owns
state/analytics; Python caches exact wire text only to independently validate the
candidate checksum. Never route this aggregate projection through native L3 IDs.

## State machine and bounded resources

DISCONNECTED → explicit connect → CONNECTING → validated subscription acknowledgment
→ SYNCHRONIZING → valid snapshot → LIVE. Here LIVE denotes an **authored protocol
state** with provenance HISTORICAL_SYNTHETIC; it must never be used as a UI claim of
observed connectivity. Invalid/missing-snapshot/checksum/native failures →
GAP_DETECTED. Only a new valid snapshot restores usability. Transport close discards
provider cached depth and returns DISCONNECTED. Heartbeat timeout changes LIVE to
STALE; a heartbeat alone does not restore stale book publication. Backoff helper
returns deterministic1,2,4,8,16,30,30...seconds; transport never retries by itself.
An external owner must bound retry attempts and obey verified provider rate limits.

Payload limit65,536 UTF8 bytes; one book batch/symbol;<=100 update fields per side;
retained ten levels per side;256 retained trades; exact field length48; local
staleness budget10s default, max60s. Unsupported capabilities reject. Future WSS
transport max_size65,536/max_queue4/open_timeout10s/close3s/ping20s/ping_timeout10s;
stop event checked at least each one-second receive timeout. It uses inherited
proxy/TLS and no market-data persistence. No byte replay or continuity claim across
connection boundaries is made.

## Reproducible authored checks

From repository root:

```
python3 -m unittest terminal.providers.test_kraken -v
```

20 tests passed locally: exact integer/rational boundaries; candidate snapshot/native
projection; partial absolute update/deletion; missing snapshot; CRC failure and
snapshot recovery; native MemoryError rejection/cache atomicity; exact-payload
duplicate; symbol mismatch; duplicate levels; zero/negative/overflow prices/sizes;
malformed/duplicate-key/oversized/unsupported messages; huge exponent checksum safely
rejected before integer materialization; subscription/heartbeat/staleness; disconnected
snapshot requirement and bounded backoff; exact/invalid timestamps; clock regression;
trade precision/window dedup/batch rejection; explicit top-ten deletion; replacement
snapshot excludes zero deletes; permission gate. Expected CRC uses a separately
implemented bitwise polynomial, not production checksum output. No actual provider
payload or copyrighted market observation is embedded in fixtures.

## Remaining activation gates

Current protocol/terms verification; supported network allowlist publication; private
cloud/display rights; current venue instrument metadata; independently verified real
snapshot/update/checksum semantics; bounded non-recording live smoke test; native
integrated failure/recovery qualification; exact-SHA owner-authorized ARM64 run.
Recording and public exposure remain separately blocked. Current state is synthetic
adapter readiness only, not live qualification.

## Integrated authored provider path

The terminal's Historical Replay source selector includes a five-record independently
authored provider-shaped fixture. It exercises the provisional parser -> separately
bound C++ aggregate L2 -> native exact analytics -> gateway/WebSocket -> ladder/depth /
3D path. Two-sided snapshot, absolute replacement, a print without book mutation,
zero deletion/one-sided metrics and a new snapshot are represented. Classification
is always HISTORICAL_SYNTHETIC; provider is authored-kraken-profile; there are no
exchange observations or source sequence numbers. Quantity scale100000000 is explicit.
This verifies software integration, not the current Kraken wire profile or live access.
The L2 initialization scope is subscribed authored depth, never full L3 identity/FIFO.
