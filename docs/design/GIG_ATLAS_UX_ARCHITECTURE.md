# GIG ATLAS UX and data architecture

The application remains React/TypeScript/Vite with its real ASGI gateway and native
C++20 extension. No mock backend replaces engine state. Source/security/replay contracts
from backend checkpoint8052947 remain unchanged.

## Global shell

GIG ATLAS branding,persistent nine-workspace navigation,breadcrumbs,global curated
company search,transport status,private-evaluation indicator,theme switch and native
help dialog. A keyboard skip link focuses the workspace. Tablet icon navigation retains
accessible names and title hints. On mobile,labels remain available in a scrolling nav.

Global search calls the existing bounded v1 identity directory. Choosing a result routes
to Stock Intelligence with that symbol. There is no fabricated all-market security
master. Local company search/watchlist/recent activity stay accessible through an
expander;no watchlist prices are invented. Company identity and source metadata are
above financial content. Provider setup is accessible but collapsed by default.

## Stock Intelligence

Overview:financial snapshot plus existing truthful IEX L1/candles/source details.
Financials contains focused Summary,Trends,Statements and Ratios views:

* Summary:eight human-readable monetary/EPS cards with full-precision/source details.
* Trends:reported revenue,income,CFO,assets,liabilities,equity and EPS. Competing concepts,
  mixed annual/YTD/quarter durations or duplicate end periods suppress a trend instead
  of silently choosing values. At most12 unambiguous points are drawn. Actual end-date spacing is used;missing
  years are not converted to evenly spaced invented periods.
* Statements:separate income,balance-sheet and cash-flow selected-fact tables;bounded
  internal scrolling. They are not full accounting statements. Tables show bounded slices;the full normalized
  SEC response remains available in an optional,lazily rendered advanced disclosure.
* Ratios:twelve exact backend descriptors with formula,actual period,quality,missing
  reason,input facts and limitations. Ratio histories are not supplied by v2 and are
  therefore not fabricated.

Duration filters are actual-date windows:annual350–380days in10-K/A,quarter-length
75–105days,YTD-length106–349days in10-Q/A. These are filters,not fiscal-quarter inference.
Balance-sheet instants are unaffected;no annual/YTD subtraction creates missing quarters.
Ratio periods stay those selected by the backend and do not follow a client-side filter.

Filings:recent cached v2 page,up to50 records,type filter,amendment indicator,filing/
report/acceptance dates,accession and validated official source links. Additional cached
pages are explicitly noted but not loaded by this checkpoint. Older SEC shards are not
implied. Institutional holdings,news/disclosure timeline,indicative-option candidate,
theoretical options and authored quant/risk workspaces remain available.

## v2 integration

`readCompanyV2()` only issues bounded same-origin GETs for curated symbols. Runtime
validation checks version/identity,all12 descriptor states,exact-string fractions,
positive denominators,source receipts and key metadata. Malformed values do not become
zeros or v1 substitute ratios. Legacy selected facts remain independently visible when
v2 fails. Existing protected v1 mutations retain endpoint-bound proof handling.

V2 reads occur on company identity or SEC receipt changes,not on every native streaming
message. StockIntelligence is memoized to isolate it from unrelated book updates.
Selection-generation and effect-cleanup checks prevent prior-symbol responses from
replacing the current view. Cache receipt age is not financial-period freshness;stale
responses remain visibly cached and source reconciliation is not asserted.

## Other workspaces

Command Center gains research shortcuts and explicit transport/source/replay status.
Order Book/Market Depth/Order Flow/Replay preserve native visualizations and controls,
with shared typography,themes,focus and surfaces. No equity L2/L3 is created from quotes.
Execution Simulator adds readable native child-order/fill/cost tables and keeps the exact
response/export;its requested-slices maximum now matches the backend's16 limit.
Authored model diagnostics gain labelled summary cards without forecasts or fitted-alpha
claims. Operations retains source/queue/build diagnostics behind disclosures. These
screens receive shared presentation improvements,not a claim that every interaction
has been independently redesigned from scratch.
