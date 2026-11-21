# Explicit offline Kraken trade/status session profile

`terminal.providers.kraken_public_session.KrakenPublicSession` is a new, explicit
`TRADE_STATUS_SESSION_V1` opt-in parser/state machine. It constructs requests and
consumes supplied frames; it never opens a transport, sends an order or changes a
permission. Existing Kraken book/trade defaults, adapter methods, top-ten CRC scope
and native state are unchanged. This is an offline prerequisite, not observed Kraken
qualification or full protocol coverage. MD07 remains PARTIAL.

## Official authority and supported slice

Reviewed on November 20, 2026 using the public documentation tool, without connecting
to a provider: [Kraken v2 Trades](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/trade)
and [Kraken v2 Status](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/status).

The trade specification supports explicit per-symbol subscribe/unsubscribe requests,
matching client request identifiers, optional subscription snapshots, and both trade
message types. Its snapshot contains up to the most recent fifty trades. Events
retain exact price/quantity, taker side/type, timestamp and per-book trade identifier;
a batch does not establish a single taker order. This implementation preserves wire
order and never interprets identifier gaps as missing L2 updates or a recovery cursor.

The status specification defines four engine states and connection/version metadata.
Optional maintenance and emergency arrays must appear together. Published service,
phase, impact/action and recovery-step categories are validated. Timestamps documented
as UTC must carry zero UTC offset. Public incident URLs remain inert metadata and are
never fetched. A non-online state or changed connection identifier conservatively
fences this local session until reconnect; this is local admission policy rather
than an exchange-wide continuity promise.

## Entry points, provenance and lifecycle

Instantiate the class explicitly with supported symbol BTC/USD or ETH/USD, positive
integer price/quantity scales up to 10^9, local request seed and snapshot choice.
`connect()` advances a local generation and clears retained identities. Request IDs
are distinct for subscribe/unsubscribe and never wrap. `subscription_request()` and
`unsubscription_request()` only return owned dictionaries; the latter records local
unsubscribe intent. An online status must precede acknowledgment admission in this
bounded profile. Successful matching acknowledgment admits trades; failed requests
return explicit rejection receipts and require reconnect. Trade traffic requires
current-generation acknowledgment and an online connection. Requested snapshots must
precede updates and may occur only once per generation.

`feed(raw, receive_monotonic_ns)` uses the existing strict duplicate-key JSON decoder
with exact Decimal numeric tokens before any binary-float conversion. It hashes the
actual UTF-8 frame and marks `source_hash_basis=HASHED_RAW_FRAME`. The lower-level
`accept_payload(payload, receive_monotonic_ns, source_sha256)` additionally accepts an
already decoded bounded mapping. Its digest is explicitly marked
`CALLER_SUPPLIED_DIGEST`; that entry point cannot independently prove which original
bytes produced the mapping. Both receipts declare no independent source authentication
and no complete protocol qualification. Caller origin labels, including permission
fixtures labelled LIVE_OBSERVED, do not establish actual observed data.

Receipts retain local generation, connection ID, exact source and receive timestamps,
source digest and unchanged original decimal text. Exact scaled integer quantities
are decimal strings. RFC3339 source timestamps retain lexical spelling and exact
nanoseconds, including supported nonzero offsets for trade/ack timestamps. Unsupported
precision, invalid calendar values, unknown offsets, range excess and nonintegral
scales reject. No financial value, correction, sequence or missing history is inferred.

Trade-ID deduplication is limited to the most recent 256 retained trades. Identical
retained repeats are idempotent; contradictory retained identities reject. Duplicate
IDs inside one batch reject rather than silently selecting a member. Validation and
receipt allocation precede retained trade publication; a bad late member leaves the
prior trade cache/receive clock unchanged and fences the session. Returned receipts
cannot mutate retained trade records. Reconnect clears the bounded window; an evicted
identifier does not imply globally complete deduplication.

## Resource and unsupported boundaries

Raw frames retain the existing 65,536-byte limit. Decoded entry points additionally
bound depth to 12, visited nodes to 8,192, dictionaries to 32 members, arrays to 100
and estimated payload bytes to the same frame budget. Scalars reject Python binary
floats/nonfinite values and oversized integers/Decimal coefficients. Trade snapshots
are bounded to 50 events; updates to 100 as a local resource policy. Maintenance and
emergency arrays each allow 16 events, with at most 16 recovery steps and bounded
text/URL/service lists. All fields and published enum choices are strict. Unknown
fields/features reject; future documentation additions need an explicit profile review.

This standalone session does **not** automatically couple status/connection fencing
to `KrakenBookAdapter`, mutate native depth or replace its existing admin profile.
Book/native eligibility coupling is a separate integration milestone. Ping/heartbeat,
authenticated/private channels, multi-symbol batches, complete trade history,
backfill, exchange-wide losslessness and actual provider/usage qualification remain
outside this package. Native identities/defaults remain unchanged.

## Offline developer evidence

`terminal/providers/test_kraken_public_session.py` supplies independently authored
fixtures only. The focused tests cover negotiation/generations, rejection/unsubscribe,
source hashes, exact exponent/large-integer numeric tokens, snapshots, wire ordering,
deduplication/conflicts/eviction, clocks/RFC3339, all engine states, paired maintenance
metadata, malformed/unknown/resource-excess frames and atomic cache publication.
The source digest distinction and returned-receipt ownership have separate regressions.

From repository root, without application/server/provider access:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python -m unittest terminal.providers.test_kraken_public_session -v
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python -m unittest terminal.providers.test_kraken_public_session terminal.providers.test_kraken terminal.providers.test_kraken_ordered terminal.providers.test_kraken_book_session terminal.providers.test_kraken_depth_session terminal.providers.test_kraken_admin terminal.providers.test_differential -v
```

Exact results/logs are in `work/nov20-public-session/`; final source-bound counts and
publication SHA belong to the enclosing sprint evidence. These fixtures are neither
real observations nor substitutes for external qualification.
