# Market-data reality and provenance

Exact application: `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`.
No provider contacted. Offline tests inherited a Python socket guard denying
non-loopback connections, and fixture servers used explicit injected transports.
Owner Codespace credentials/configuration/data were not inspected.

## Source inventory

| Source | Implemented path | Reality established here / boundaries |
|---|---|---|
| Native authored L3 |`terminal/server/fixtures.py`, `engine.py:64–93,155–219`|Default `terminal-authored-v2`/SYNTH-USD,known synthetic empty boundary,logical replay clock. Real C++ transitions on synthetic inputs.|
| Authored aggregate profile |`terminal/providers/fixtures.py`, `NativeSession.reset_aggregate`|Provider-shaped synthetic L2;not a current independently verified protocol or real crypto observation.|
| Eight-model research fixture |`web/src/research3d.ts:49`|Two declared symbols,explicit authored orders/executions/directions. Generated independently of native replay;never an exchange observation.|
| Alpaca IEX REST |`stocks/service.py:101–117,166–198`, `alpaca_history.py`|Fixed HTTPS GET allowlist,raw historical bars/quotes/trades,latest inputs;all genuine data disconnected in audit.|
| Alpaca IEX stream |`stocks/live.py:10,73–151`|Fixed IEX WebSocket,MessagePack,bounded protocol state. Fixture socket explicitly labelsHISTORICAL_SYNTHETIC. Actual feed not activated.|
| Indicative options |`stocks/option_feed.py`, `alpaca_transport.py`|Explicit indicative gates;no paid OPRA fallback. Real option observations/entitlement unverified;European model is separate.|
| SEC facts/submissions/tickers |`stocks/sec.py`, `sec_identity.py`, `service.py:53–78`, `sec_history.py`|Official fixed URLs/identifying UA/rate policy;fixtures only here. Owner reports visible genuine facts and10,429 identities/1,772 selected matches. Original exact report/source context absent.|
| Curated/catalog/listing references |`stocks/identity.py:4`, `market_catalog.py:9`, `directory.py`|13 curated default symbols includingAPLD/CRWV with no guessed CIK. SEC and Nasdaq-style directory imports supported subject to scope.50,002 performance records are authored,not actual stock count.|
| Kraken/Coinbase |`providers/kraken.py`, `coinbase_candidate.py`, `supervisor.py`|Aggregate depth/native flow integration and bounded lifecycle exist;all real protocols/rights/network acceptance remain gated/unverified here.|
| Recorded crypto aggregate data |`terminal/recording`, `server/engine.py`|Bounded capture/retained replay contracts and synthetic fault tests;no actual observed recording loaded. Permission/retention gates stay off.|
| Historical ITCH/LOBSTER |`include/gig/itch`, `include/gig/lobster`,examples|Bounded CLI decoders/reconstruction/CSV comparison tested with authored data. No historical bytes read/downloaded;not browser-imported live depth.|

## Actual IEX path and source boundaries

Future authorized provider → fixed IEX MessagePack transport → bounded decoder
(32KiB frame,≤128 records/≤32 map fields) → lifecycle/subscription validation →
exact source timestamp and local receipt/provenance → atomic accepted memory/store
publication → per-generation metrics → proof-authorized SSE snapshots/deltas →
validated browser projection → L1 cards/traces/3D. Native global replay remains a
different WebSocket/state path and is not overwritten by equities L1.

`LiveIEX.process()` stages a complete frame before publication. Known subscriptions
and channels required;bad/unknown types reject;source-ahead tolerance is explicit.
Duplicates use bounded exact-message identities;late events remain diagnostic and
do not replace latest accepted quote. This is not exchange sequence reconstruction
or arbitrary-history deduplication. History and dedup retain256 entries;evictions
are counted. Corrections/cancels remain observations;unreconciled trade totals are
suppressed. No trade-direction or deeper book is invented.

Quotes/trades expose source nanoseconds,receipt wall/monotonic times,source age,
generation,provider/feed,wire binary64 hex where relevant and conditions/venue
codes. Binary64 provider amounts are round-trip strings,not exact exchange ticks.
Size units remain provider-reported/unverified;no inferred share/lot conversion.
Native best-quote projection can reject quantities/prices not exactly representable
without losing the retained source observation.

Receipt/source age>30s becomesSTALE (bars120s);phase/generation/symbol mismatch
becomesUNAVAILABLE. No quiet-market price movement is fabricated. Stream connection
and source freshness are distinct. Frontend receives bounded heartbeats;browser
retries at most5 opening attempts with bounded backoff;provider retry budget≤5.
Shared connection/subscription replacement uses explicit acknowledgments and clears
generation-local latest state. Default internal cap4 symbols does not grant more
connections or prove an account-wide free allowance.

Session state is intentionally partial. `prices.market_window()` is a New York
weekday-clock window,explicitly not holidays/halts/auctions. `SessionSchedule`
uses a validated owner-declared bounded file;absent coverage staysUNKNOWN. No
official real-time calendar/halt authority or corporate-action adjustments exist.

## Future authorized quote qualification — executable criteria, NOT_RUN here

After specific permission review and separate session authorization, use the
existing `scripts/qualify_alpaca_live.py` in the private owner target,not this audit.
Review its exact flags and bounds before execution. A bounded test harness must:

1. Pin candidate SHA and permission reference;confirm Basic IEX/free-account scope,
   existing connection usage and credentials server-side without printing values.
2. Subscribe to explicitly bounded known symbols;record source/provider/feed and
   symbol mapping,accepted/excluded counts,source/receipt timestamps,units,age.
3. Independently validate bid/ask,size,locked/crossed outcomes and exact descriptive
   metrics. Preserve zero-sided/crossed/ineligible observations diagnostically.
4. Count updates when events occur;do not require invented ticks during quiet markets.
   Record verified session coverage orUNKNOWN;weekday clock is not exchange authority.
5. Force only an approved local interruption;verify stale/disconnected state, bounded
   retries,acknowledged generation/subscriptions and no cross-symbol contamination.
6. Assert no synthetic fallback or native-depth mutation. Do not infer SIP/NBBO,
   all-market tape,aggressor direction,L2/L3 or calibrated VPIN from IEX L1.
7. Stop at byte/event/wall/subscription limits and retain safe aggregate receipts only;
   no orders,paid feeds,extra subscriptions or observed persistent retention.

These criteria are BLOCKED,not failed provider tests. Basic personal research/IEX
availability is owner-confirmed;private cloud processing,authenticated browser
display and historical access/limits remain the specific pending questions. No
repeat setup,keys or general authorization discussion is needed.
