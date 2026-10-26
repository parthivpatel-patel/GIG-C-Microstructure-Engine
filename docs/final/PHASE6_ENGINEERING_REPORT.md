# Phase6 engineering report

Baseline `1f07a6fabc1a0cfd99e37d769d744a258126c14b`;isolated branch
`feat/atlas-final-release`. October26,2026 America/New_York.

## Implemented

* Official-source-grounded,independently authored IEX MessagePack transport,auth and
  explicit subscriptions,quotes/prints,32KiB frames/128 messages/4 symbols/4 queued frames,
 256 remembered identities,exact nanosecond timestamps and binary64 wire-hex disclosures.
* Failure-atomic semantic batches;unauthorized symbols,unknown/correction messages and
  provider errors fail explicitly. No native mutations or inferred exchange sequences.
* Bounded reconnect(2,4,8,16 seconds,5-failure ceiling),resubscription,ping/pong transport
 monitoring,30s observation staleness,graceful cancellation. Control traffic never freshens
 an observation. Provider errors stop for operator review,not blind entitlement retries.
* Existing Alpaca permission flags plus `GIG_ALPACA_LIVE_ENABLED=1` required before any
 connector. No activation on import,startup,search or subscription status reads.
* Exact shared start/end interval alignment across1–4 immutable raw revisions under one
 serialized SQLite read transaction. No missing fill/decimal rounding. Private rational
 portfolio path preserves repeating returns;public decimal endpoint remains unchanged.
* Separate conditional GARCH coordinate search(log omega/simplex coefficients) with
 stationarity constraint,grid boundary baseline and monotone candidate selection. Fixed
 training sample mean/initial variance;not joint/global MLE. Fixed-parameter HMM missing
 observations integrate emission likelihood1 while advancing transitions;no missing-data EM.
* Cache-only filing-date vintage endpoint retaining known revision identities/derived
 descriptors. Partial retention/truncation/filing-day granularity explicit;not full XBRL or
 intraday point-in-time authority.

## Protocol evidence

Official `alpacahq/alpaca-py` revision `3da132c6407792310bfbaca1b3114863c44d5bda`.

- https://raw.githubusercontent.com/alpacahq/alpaca-py/3da132c6407792310bfbaca1b3114863c44d5bda/alpaca/data/live/websocket.py SHA256 `ce4a21600663be6f2c5b714dd99695a43546b3b45b1d79c76caf6a8d00642ee2` (21432 bytes).

- https://raw.githubusercontent.com/alpacahq/alpaca-py/3da132c6407792310bfbaca1b3114863c44d5bda/alpaca/data/live/stock.py SHA256 `81bc98c9e9886dec392b6e95908d0851371b360e79045e7d0dfc04fcf6b850b9` (8613 bytes).

- https://raw.githubusercontent.com/alpacahq/alpaca-py/3da132c6407792310bfbaca1b3114863c44d5bda/alpaca/data/mappings.py SHA256 `7979ae408edbf287ccaa29c104b13b12dc7fd7d43f6773a647e328182791d82a` (1721 bytes).

The common/enums.py at the same revision supplies fixed stream base URL;stock.py maps
IEX to v2. websocket.py lines155–205/390–405 establish MessagePack/auth/subscription;
mappings.py names quote/trade fields. These are official SDK implementation references,
not a complete contractual market-data specification or permission grant. Copies remain
ignored under build/final;no third-party SDK code vendored. Added pinned codec
msgpack1.1.2(Apache-2.0),no Alpaca SDK dependency or paid service.

## Independent evidence

New18-case synthetic cohort checks authored expectations:atomic malformed batches,
byte/message limits,duplicate keys,identity dedup,staleness,symbol/enum rejection,
nanosecond timestamps,native isolation,real async fake transport/auth/subscription,
reconnection/cleanup,authorization and forged-header denial. Independent scalar variance/
likelihood recursion verifies continuous search result;HMM state permutation/missing
transition checks;exact1/99 dataset returns;retained vintage cannot invent older facts.
All18 pass,plus existing51 consumers in Release/Debug/sanitizer(69 each). Complete
qualification counts/eight frozen identities are in Phase8/evidence manifest.

## Boundaries

No market-data or SEC request. Runtime has no approved identifying SEC User-Agent or
Alpaca credentials. Support381230 remains an external permission gate. Actual transport,
entitlement,network/proxy behavior and browser-source delivery are NOT VERIFIED against
provider observations. SDK-based support is partial:trade corrections/cancels,other
feeds/message families,full exchange calendars/corporate actions,complete statement
presentation/dimensions,continuous missing-data estimation and parameter uncertainty are
not implemented. Existing finite-grid models and API contracts are preserved.
