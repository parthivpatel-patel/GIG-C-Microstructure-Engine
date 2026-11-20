# Bounded opt-in deeper Kraken book subscription

`KrakenBookAdapter(..., depth=25, ordered_updates=True,
book_session_profile='BOOK_SESSION_DEPTH_V2', book_request_id=100)` admits depths
10,25 and100 in a new offline parser/native callback profile. The legacy and
BOOK_SESSION_V1 profiles still require depth10. The application, supervisor,
transport request, recovery formats and product controls retain their existing
depth10 configuration. No new live connection or entitlement is enabled.

Official documentation independently read through the documentation tool:

- https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/book — Subscribe
  request/response depth options and echoed depth; Snapshot and Update sections.
- https://docs.kraken.com/exchange/guides/websockets/book-checksum-v2 — Maintaining
  the book and Checksum calculation sections, plus the published CRC example.

Rechecked on November20,2026: the book reference's Subscribe request/response
sections specify the depth options and matching acknowledgment; Update specifies
wire ordering for repeated prices. The checksum guide's Maintaining the book and
Checksum calculation sections establish zero deletion, subscribed-depth trimming,
decimal preservation and top-ten-only CRC scope. These are documentation reads,
not provider connections or independently observed market data.

The subscription specification offers10,25,100,500 and1000 levels per side.
This bounded implementation deliberately refuses500/1000. The checksum guide
requires processing all message updates, removing zero-quantity levels and
truncating to the subscribed depth; its CRC covers only the best ten levels per
side at every subscription depth. Decimal source text remains exact. Repeated
price updates retain wire order, including deletion/reinsertion, and the final
retained cache determines a single atomic native transaction. The new profile
requires ordered_updates=True rather than silently enabling different legacy
behavior. Matching depth, snapshot option, request and local generation remain
mandatory in its acknowledgment.

The existing64KiB JSON payload limit,100 wire updates per side/message, exact
decimal scale/range checks, duplicate snapshot refusal, checksum check and
acknowledgment/session fences remain enforced. These are local resource limits,
not a promise that every official protocol message fits. Short snapshots retain
their actual supplied levels; they neither create missing levels nor establish
complete market-depth coverage. Receipt fields disclose subscribed_depth,
checksum_depth=10, checksum_scope=top_10_per_side_only and actual retained_levels.
Changes outside the best ten can leave CRC unchanged; the report explicitly
preserves that limited integrity scope.

The callback owner must admit the bounded projection. A replacement can contain
up to twice the subscribed depth per side: explicit deletions of old trimmed
levels plus new retained levels. Native AggregateDepth256 admits the tested worst
case of200 changes on each side in one depth100 transaction. Native100 rejects
that bounded replacement without
changing either native state or the adapter cache. Such a native failure
invalidates the acknowledgment and requires reconnect. No native source or frozen
reference identity was changed. Existing application NativeDepth32 remains paired
with depth10; this package does not widen that product contract.

Fourteen new offline tests exercise both new depths and legacy refusal, strict
configuration/ordering, exact-depth acknowledgment, actual native retention,
worst-case200-change replacement, both-side trimming, repeated prices, deeper CRC
scope, checksum rollback, unchanged resource limits, undersized-native rollback,
reconnect fencing and unavailable depth preservation. The official guide's CRC
3310070434 example additionally passes the independent polynomial reference and
the actual adapter/native callback at depth25. The guide example is documentation;
all other books are authored fixtures, and none is observed provider evidence.

Kraken remains provisional: profile_verified=false, exchange_sequence=false and
live_connectivity_verified=false. Additional official depth/options, trade/status
and usage/target reconciliation remain open. Local generations are not exchange
sequences; top-ten CRC agreement does not establish source authentication,
lossless reconnection, deeper integrity, backfill or independent qualification.
