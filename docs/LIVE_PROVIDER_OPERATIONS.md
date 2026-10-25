# Provider operations: supervised candidate, not live-qualified

Current implementation: [RECORDED_L2_IMPLEMENTATION.md](RECORDED_L2_IMPLEMENTATION.md),
[CONTINUOUS_RESEARCH_METHODOLOGY.md](CONTINUOUS_RESEARCH_METHODOLOGY.md) and
[CONTINUOUS_ENGINEERING_STATUS.md](CONTINUOUS_ENGINEERING_STATUS.md). Earlier
offline-only statements below retain their baseline scope; current capture is separately gated.

October25,2026. The owner confirms the baseline private Codespaces connection and
replay controls work. New feed code retains that v4 Origin/Host/proof boundary.
No provider socket opens on startup, import, mode selection, or without explicit
server permission plus a protected Connect action. Recording stays off.

## Verified versus blocked

Kraken is the sole implemented candidate; BTC/USD and ETH/USD, ten aggregate levels
per side. The source is the fixed wss://ws.kraken.com/v2 endpoint. Redirects are
rejected, TLS verification and inherited proxy settings are preserved, text payloads
are capped at64KiB and the socket queue at4 messages. There are no arbitrary URLs,
credentials, orders or provider endpoint settings in the browser. No Coinbase
production adapter is claimed. Its current official documentation remains blocked.

Fresh metadata-only requests to both official documentation hosts returned curl56,
proxy CONNECT403, before origin response. No additional blocked-host retry or live
handshake was attempted. Applicable terms, cloud/private display, geography and
retention remain unverified. The existing provisional protocol still requires review
against the current official schema; notably status/admin messages and unknown fields
fail closed. Passing authored fixtures does not establish Kraken compatibility.

## Exact activation prerequisites

1. Obtain official book/trade/checksum/session/heartbeat and rate-limit documentation
   from https://docs.kraken.com/api/docs/websocket-v2/book/ and the corresponding
   trade guidance; review https://www.kraken.com/legal for applicable terms. No
   assertion of unrestricted cloud processing, free unlimited usage or retention.
2. Confirm the chosen operator's private cloud display/processing rights and current
   feed rules. Repair/version any actual schema differences before activation.
3. If running in this managed task, publish supported environment allowlisting for
   docs.kraken.com, www.kraken.com and ws.kraken.com. Do not bypass the proxy.
   The owner's Codespace has its own networking, not this task's allowlist.
4. Only after those reviews, the operator may configure GIG_LIVE_ENABLED=1,
   GIG_LIVE_PROTOCOL_REVIEWED=1, GIG_LIVE_PRIVATE_DISPLAY_APPROVED=1,
   GIG_LIVE_CLOUD_PROCESSING_APPROVED=1 and a non-secret
   GIG_LIVE_PERMISSION_REFERENCE identifying the reviewed basis. These are explicit
   operator attestations, not automated legal verification. Do not set them simply
   to remove the blocked message. No field enables recording in the live supervisor.
5. Restart the private terminal, select Live Market Data, provider, instrument and
   Connect public feed. Or run the bounded, non-recording CLI:

```bash
.venv/bin/python scripts/verify_terminal_feed.py --symbol BTC/USD --seconds 20
```

The CLI exits2 before opening a socket when permission/configuration is missing;
1 for an incomplete/failed observation;0 only for a currently validated production
transport snapshot. It prints summary counts/metrics, never raw source frames or
credentials. Do not publish observed output without applicable rights. It does not
verify browser display or demand that all snapshot/update/trade/reconnect gates pass.
Those remain separate acceptance checks, not inferred from one successful snapshot.

## Lifecycle and integrity

One event-loop-owned feed, one selected symbol, separate native aggregate book.
Reconnect never reuses accepted old depth: a new snapshot is mandatory. Bounded
backoff uses random jitter0.8..1.2 around1,2,4,8,16,30 seconds (maximum36s), not
exchange chronology. Subscription/connect receive budget15s; receive budget10s;
depth freshness budget10s. Heartbeats and trades cannot extend depth freshness.
These are local conservative policies, not universal exchange guarantees.

State becomes LIVE_VERIFIED only after real production transport and a validated
snapshot accepted by native C++; fixture transports remain TESTED_WITH_FIXTURES.
This label refers to that connection's declared subscribed aggregate view, not full
market completeness, current protocol independently verified here, L3/FIFO, or
production readiness. An Origin-connected browser is not a live-provider proof.

Invalid CRC, crossed candidate, unknown source semantics, native rejection, deadline
or disconnect hides depth/metrics before awaiting socket cleanup. RESYNCING requires
a fresh snapshot. Missing exchange timestamps remain null. No synthetic sequence,
order ID, cancellation identity, missing levels or liquidity is invented. Locked
books are not silently uncrossed; native locked/crossed diagnostics remain available.
Trade deduplication is bounded256 identities, not an unlimited historical guarantee.

Source receive time uses monotonic_ns for age and Unix_ns for wall display. Exchange
RFC3339 nanoseconds are optional and exact. Local capture segment identifies
reconnect/symbol boundaries; it is not an exchange session or sequence. Browser
history resets across segments/symbols, is capped96 observations and is a sampled
latest-state view. Required provider updates are applied before display coalescing.
Pause visualization freezes the landscape only; ingestion and current book continue.

## Owner update

Stop server (Ctrl+C), stay on feat/bootstrap-cpp20-engine, then:

```bash
git pull --ff-only origin feat/bootstrap-cpp20-engine
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

No native wheel rebuild is required for these Python/browser changes. Keep port8787
Private, internal protocolHTTP, and open its authenticated forwarded HTTPS address.
Until review is complete, Connect shows ERROR/UNAVAILABLE with no substitute book.
Confirm historical Step, private WSS101, provider failure indicators and visualization
pause after updating. This task cannot independently enter the owner's private page.
