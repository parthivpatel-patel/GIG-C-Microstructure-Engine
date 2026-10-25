# Market-data provider assessment

Assessment scope: October 25, 2026, private development environment. No observed
provider payloads were obtained, no subscription opened and no market observations
were recorded or redistributed. Source access below is actual; protocol proposals
below are explicitly unverified current profiles. A no-auth endpoint is not a data
license. User-supplied public availability is not inferred authorization.

## Source-access ledger

Bounded HTTPS requests used inherited proxy, default TLS verification, timeout10s,
no retries, no bypass. Each request inspected at most65,537 response-body bytes;
CONNECT403 failures occurred before any destination body was received.

| Official URL | Actual outcome | What this establishes |
|---|---|---|
|https://docs.kraken.com/api/docs/websocket-v2/book/|Proxy tunnel403 Forbidden|Current book schema not independently retrieved|
|https://docs.cdp.coinbase.com/exchange/websocket-feed/channels|Proxy tunnel403 Forbidden|Current Exchange channel documentation not retrieved|
|https://www.kraken.com/legal|Proxy tunnel403 Forbidden|No current applicable rights/retention/display terms verified|
|https://www.coinbase.com/legal/market_data|Proxy tunnel403 Forbidden|No current applicable market-data terms verified|
|https://raw.githubusercontent.com/krakenfx/api-specs/master/README.md|HTTP404|Guessed repository path provides no specification evidence|
|https://raw.githubusercontent.com/coinbase/coinbase-pro-node/master/README.md|HTTP200,15,618bytes,SHA2561764c7d83c7f753d6e277a17f2991ed9d17b4e5f43e19130548300dedc72fe1e|Provider-owned legacy SDK identifies itself as official Coinbase Pro client and links legacy documentation. Not verification of current Exchange API or rights.|

The GitHub read used the same permitted proxy path and provider-owned repository;
it was not a mirror or an attempt to evade the blocked destination. No repeating
CONNECT probes were performed. No Kraken/Coinbase WebSocket handshake was attempted:
provider domains are absent from the supported environment destination configuration
and current legal/protocol evidence is unavailable.

## Candidate capabilities and verification status

| Provider | Proposed scope | Current verification | Retention/display/redistribution |
|---|---|---|---|
|Kraken public WebSocket v2|BTC/USD L2 snapshot/absolute updates and prints; no fabricated L3/FIFO; candidate top10 CRC32|Authored profile only. Current official protocol, access and live connectivity UNVERIFIED.|No affirmative current permission verified; recording disabled; no observed display or public redistribution.|
|Coinbase Exchange|Potential public spot trades/L2 alternative; public legacy SDK demonstrates historical unauthenticated market-data methods only|No production adapter, no current feed/schema verification, no live test|Unverified; no recording/display/redistribution enabled.|
|Equities provider (not selected)|Potential entitlement-gated L1 trades/quotes, not invented aggregate depth|No credentials or reviewed free entitlement supplied; UNAVAILABLE|Owner must identify provider/plan and review permitted cloud/private display and retention. No paid subscription purchased.|

Kraken is a **candidate**, not an evidence-backed final provider selection. Current
implementation under terminal/providers is a provisional, narrowly declared profile
using independently authored data. Official live activation remains BLOCKED. Current
rate limits/auth requirements/depth options/reconnect guarantees cannot be represented
as verified facts from unavailable documentation. No claim of free unlimited API use,
SIP/consolidated equities coverage, market completeness or exchange-equivalent L3.

## Smallest supported owner action

1. Through the supported environment configuration workflow, allow
   `docs.kraken.com`, `ws.kraken.com` and `www.kraken.com` for official documentation,
   terms and WSS. Publish the environment change; this assignment does not edit the
   network policy or bypass its proxy. If choosing Coinbase instead, relevant
   candidate destinations are `docs.cdp.coinbase.com`, `ws-feed.exchange.coinbase.com`
   and `www.coinbase.com`; verify current official endpoint before connecting.
2. Supply or retrieve current official applicable terms and review private cloud
   processing/display, geography, retention and derivative/publication scope. Recording
   stays off until an explicit retention basis is established. Credentials are not
   requested for the proposed public candidate and must never be pasted into browser
   configuration or logs.
3. Review actual current schema/checksum/update/heartbeat/rate-limit rules against
   the authored profile, repair/version any differences, then run a separately
   bounded authorized live smoke test with no recording. Capture only safe status /
   count/hash evidence permitted by the terms. The existing permission attestation is
   an operator assertion, not an automatic legal verifier.
4. For equities, supply an authorized provider/account entitlement and secure backend
   credential binding. Do not imply that a broker account/free API provides Nasdaq
   depth or consolidated real-time data. Keep L1/L2/L3 and delayed flags explicit.
