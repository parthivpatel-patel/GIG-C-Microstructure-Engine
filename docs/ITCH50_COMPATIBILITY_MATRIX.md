# Complete ITCH5.0 compatibility audit

Entry checkpoint:3ee54cf552c096bc8fe8f46b9237336bcd376473, October23,2026.
Retained official specification: NQTVITCHSpecification.pdf,1200722 bytes, SHA256
`45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3`.
Official URL: <https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf>.
Read offline; no new download. Sections/pages below refer to this document, whose
revision log includes April28,2023. It is not an authenticated frozen2019 profile.

All offsets are payload-relative; BinaryFile adds a two-byte big-endian length.
Every family has type0/1, stock-locate1/2, tracking3/2 and timestamp5/6. Integers
are unsigned big-endian unless explicitly stated; timestamps are nanoseconds
since midnight, not dates or UTC instants. Alpha is ASCII right-space-padded;
current local wire policy requires printable32–126. Price(4) has scale10000 and
maximum2000000000 raw. Price(8) has scale100000000; the retained general data-type
section states no separate Price(8) cap. Preserve its uint64 wire range without
applying the Price(4) maximum, floating conversion or invented cross-level ordering.

## Complete field and semantic inventory

Every message below has a recognized exact length already at entry. Recognition
alone neither decodes its fields nor makes its source context or reconstruction
eligible. Generic unknown type octets remain explicit unknown_type outcomes.

| ID /official name | Payload bytes | Fields after common header (offset:name/bytes) | Context/L3 implications and remaining requirements | Official reference |
|---|---:|---|---|---|
| `S` System Event |12|11:event/1|system OSQMEC observation; global locate0; no empty-book inference|§1.1 p4–5|
| `R` Stock Directory |39|11:stock/8;19:market/1;20:financial/1;21:round_lot/4;25:round_only/1;26:classification/1;27:subtype/2;29:authenticity/1;30:threshold/1;31:IPO/1;32:LULD_tier/1;33:ETP/1;34:leverage/4;38:inverse/1|unique daily locate/symbol admission, no initial orders|§1.2.1 p5–8|
| `H` Stock Trading Action |25|11:stock/8;19:state/1;20:reserved/1;21:reason/4|known directory; external only; no inferred absent-security state from incomplete spin|§1.2.2 p8|
| `Y` Reg SHO Short Sale Price Test Restricted Indicator |20|11:stock/8;19:action/1|known directory; external only, no execution-rule enforcement|§1.2.3 p9|
| `L` Market Participant Position |26|11:MPID/4;15:stock/8;23:primary/1;24:mode/1;25:state/1|known-directory external observation; not an order or MPID liquidity estimate|§1.2.4 p9–10|
| `V` MWCB Decline Level |35|11:level1/8 Price(8);19:level2/8 Price(8);27:level3/8 Price(8)|global locate0 observation; no reset/halt inference or native price conversion|§1.2.5.1 p10|
| `W` MWCB Status |12|11:breached_level/1|global locate0 external observation; no automatic book clearing|§1.2.5.2 p10–11|
| `K` IPO Quoting Period Update |28|11:stock/8;19:release_seconds/4;23:qualifier/1;24:IPO_price/4 Price(4)|unsupported; global locate0 despite stock field; cancellation zero values and contradictory decimal prose require explicit reviewed policy|§1.2.6 p11|
| `J` LULD Auction Collar |35|11:stock/8;19:reference_price/4;23:upper_price/4;27:lower_price/4;31:extension/4|unsupported; future contextual observation, not resting liquidity or auction matching|§1.2.7 p11–12|
| `h` Operational Halt |21|11:stock/8;19:market_code/1;20:action/1|known-directory external observation; venue-specific Q/B/X, distinct from H; no reset|§1.2.8 p12|
| `A` Add Order — No MPID Attribution |36|11:order_ref/8;19:side/1;20:shares/4;24:stock/8;32:price/4|new positive identity; exact units; new FIFO arrival; synthetic native projection only|§1.3.1 p13|
| `F` Add Order with MPID Attribution |40|11:order_ref/8;19:side/1;20:shares/4;24:stock/8;32:price/4;36:MPID/4|A plus exact attribution retention; no inferred aggressive order|§1.3.2 p13|
| `E` Order Executed |31|11:order_ref/8;19:executed_shares/4;23:match/8|known eligible order, checked decrement; zero retires; no aggressor|§1.4.1 p14|
| `C` Order Executed With Price |36|11:order_ref/8;19:executed_shares/4;23:match/8;31:printable/1;32:execution_price/4|decrement resting order; execution price separate; native projection requires explicit allow_c_book_only; avoid nonprintable double count|§1.4.2 p14–15|
| `X` Order Cancel |23|11:order_ref/8;19:cancelled_shares/4|checked partial decrement; equal-cancel policy explicit; no unknown-order synthesis|§1.4.3 p15|
| `D` Order Delete |19|11:order_ref/8|retire all remaining shares of known active order|§1.4.4 p15|
| `U` Order Replace |35|11:old_ref/8;19:new_ref/8;27:shares/4;31:price/4|retire old reference; preserve side/stock/MPID; new identity/priority; reject lifetime reuse|§1.4.5 p15–16|
| `P` Trade — Non-Cross |44|11:order_ref/8;19:side/1;20:shares/4;24:stock/8;32:price/4;36:match/8|non-displayed print, no native book mutation; reference0 after2010 and B placeholder after2014 are raw fields, not queue/aggressor|§1.5.1 p16–17|
| `Q` Cross Trade |40|11:shares/8;19:stock/8;27:cross_price/4;31:match/8;39:cross_type/1|typed observation; integration-ineligible external receipt, no invented auction/resting liquidity; zero cross shares allowed on wire|§1.5.2 p17|
| `B` Broken Trade / Order Execution |19|11:match/8|known match correction; no liquidity restoration; cross-break context remains unsupported; downstream research correction not complete|§1.5.3 p18|
| `I` Net Order Imbalance Indicator |50|11:paired/8;19:imbalance/8;27:direction/1;28:stock/8;36:far/4;40:near/4;44:reference/4;48:cross_type/1;49:variation/1|unsupported; aggregate indicative auction interest, not L3 orders; revision-specific P direction/A cross type|§1.6 p18–19|
| `N` Retail Price Improvement Indicator |20|11:stock/8;19:interest_flag/1|known-directory external BSAN observation; no inferred displayed quantities|§1.7 p19–20|
| `O` Direct Listing with Capital Raise Price Discovery |48|11:stock/8;19:eligible/1;20:min_price/4;24:max_price/4;28:near_price/4;32:near_time/8;40:lower_collar/4;44:upper_collar/4|unsupported; introduced2023, not asserted to occur in2019; no fabricated launch eligibility/book state|§1.8 p20|

## Support, evidence and prioritization

| Family | Entry v1 /v2 | v3 implementation | Independent evidence /remaining work |
|---|---|---|---|
| S,R,A,F,E,C,X,D,U,P,Q,B |Typed /Typed |Unchanged |P1E wire oracle, P1F context oracle, P1G L3 and P1H/P1I streaming oracles; synthetic scope. Context acceptance and book projection differ as above. |
| H,Y |Unsupported /Typed |Retain v2 semantics |Independent H/Y8002 wire+16000 context candidates; real4KiB350-frame agreement includes H2/Y2 only. |
| L,V,W,h,N |Unsupported /Unsupported |Explicit administrative_observations_v3; typed external observations |Prioritize due to precise documented layouts and accounting of administrative/global/security observations. No observed occurrence or frequency established. Independent25233-case wire oracle and16960 context candidates; enum/length mutations, failure atomicity, allocation and streaming/restart tests. Full results in engineering report. |
| J |Unsupported /Unsupported |Unsupported |Well-defined collar layout; deferred to separate small profile extension with independent price/symbol/auction-policy tests, no matching. |
| I |Unsupported /Unsupported |Unsupported |Separate versioned NOII layout/revision policy and independent exact unsigned/price/enum tests; no inferred orders. |
| K |Unsupported /Unsupported |Unsupported |Resolve global symbol routing and internally inconsistent price prose/cancel semantics; do not guess ASCII numeric encoding. |
| O |Unsupported /Unsupported |Unsupported |2023 addition; separate profile/near-time contract, not a2019 readiness requirement. |

Priority is engineering value and semantic certainty, not a claim about unseen
archive frequencies. Unsupported records stop with explicit diagnostics and do not
advance accepted context. None may silently disappear from research outputs.

## Historical ambiguities and limits

AppendixA records h addition in2018, J in2017, NOII cross A in2022 and direction P
and O in2023. Older Price(4),P reference/side and Y changes also predate2019 in the
retained log. These entries are supporting history, not complete authenticated
2019 contracts. New v3 observations must preserve raw fields and explicit profile;
no inferred enforcement, liquidity, market halt/reset or global ordering from
tracking numbers. S/R/H/Y actual prefix evidence covers only350 complete frames;
all other family correctness remains synthetic/source-review evidence.

Implementation and final measured results will be recorded in
HISTORICAL_ITCH_ENGINEERING_REPORT.md. Observed L3 readiness is a separate gate in
OBSERVED_L3_READINESS_CONTRACT.md, not implied by this matrix.
