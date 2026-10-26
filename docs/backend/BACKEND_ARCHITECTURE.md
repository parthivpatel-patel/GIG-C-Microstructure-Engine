# Backend architecture and integration contracts

The application uses one ASGI worker and deterministic C++ state. Python orchestrates
validated sources and research descriptors; it does not replace the native book with
a browser mock. `terminal/server/engine.py` calls the installed `gig_microstructure`
extension. `include/gig/book/order_book.hpp` and `src/book/order_book.cpp` own native
order state; replay and simulator are separate contracts. Synthetic simulation is not
an execution gateway.

## Data paths

1. Authored replay or explicitly gated provider transport → bounded decoding → native
   aggregate-depth/order-book validation → state receipts → WebSocket → browser/3D.
2. Stock load/refresh → fixed provider URL → exact JSON parsing → per-component SEC,
   IEX or indicative-option validation → bounded in-memory cache → read-only views.
3. SEC selected facts → period-aware rational descriptors → versioned company view.
   This path performs no native L3 mutation and never invents missing financial inputs.
4. User-authored scenarios → European pricing/fixed-parameter research models. Outputs
   remain theoretical/authored, not observed forecasts or executable quotes.

Source context/native reconstruction has its own prepared transaction boundaries.
Replay rejects sequence/capacity/recovery failures explicitly. The new SEC work does
not modify those contracts, matching, TCA, gzip handling or journal layout.

## HTTP and WebSocket inventory

Routes are defined in `terminal/server/app.py`. Existing v1 contracts remain available:

| Interface | Access/meaning |
|---|---|
| GET /api/v1/health,state,schema,connection,catalog | Health/native state/schema/bounded sanitized diagnostics/capabilities |
| GET /api/v1/request-proof; POST /api/v1/stream-ticket | Bounded endpoint/session proof bootstrap; not arbitrary forwarded-header trust |
| WS /api/v1/stream | Bounded native observation stream; exact Origin or approved one-use proof |
| GET /api/v1/stocks/search,company | Curated identities and cached source views; GET does not refresh upstream |
| POST /api/v1/stocks/load,refresh | Protected explicit loading, provider gates/rate and cache budgets apply |
| POST /api/v1/stocks/options,research | Protected bounded authored model requests |
| POST /api/v1/control,simulate,validate | Protected replay/simulation/validation operations |
| GET /api/v1/recordings; POST /api/v1/recording | Private bounded discovery and protected recording operations |
| GET /{path:path} | Frontend assets with existing path validation |

New cache-only GET interfaces:

* `/api/v2/companies/{symbol}`: schema `gig.backend.company.v2`, curated instrument,
  data origin, observed/as-of dates, quality, rational financial descriptors and source
  receipts. JSON Schema: `terminal/server/schemas/backend_company_v2.schema.json`.
* `/api/v2/companies/{symbol}/filings?form=10-K&offset=0&limit=25`: supported form,
  offset0..128, limit1..50; recent cached filings only. Returns filtered cached count,
  next offset, coverage and limitations. It is not SEC shard pagination.

Unknown v2 filing query keys/invalid numeric bounds are rejected. No new mutation or
proof target is added. A read-only response is not permission to expose the private port.

## ATLAS contract rules

Available metric values are `{numerator:string,denominator:string}` in the documented
unit; unavailable values are JSON null with a reason. Frontends must not coerce null to
zero, annualize returns implicitly, add indicative sizes as full depth, or label cached
responses live. Financial descriptors include formula, period, duration, source facts,
as-of date, quality and limitations. `timestamp:null` is deliberate: a filing date is
not authenticated intraday availability. The source reconciliation status remains
`NOT_INDEPENDENTLY_RECONCILED_BY_THIS_SERVER` even when the cache is configured.

The v1 financial records gain additive metadata and expanded selected metrics; the
financial normalization version is2. Existing keys are retained. The redesigned
frontend has not yet been migrated to or accepted against v2.

## Ownership, persistence and operations

StockWorkspace serializes refreshes and commits a bounded normalized result only after
validation; malformed components do not become accepted facts. A process restart clears
financial caches. Disk-backed recordings have separate retention and integrity checks.
Do not add Redis/Kafka or a general database without a measured requirement and recovery
contract. Start with `bash scripts/start_terminal.sh`; keep Codespaces8787 PRIVATE,
use its forwarded HTTPS URL, and restart after updates. No paid hosting is required.
