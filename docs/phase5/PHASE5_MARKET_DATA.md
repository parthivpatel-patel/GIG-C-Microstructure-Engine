# Historical-data subsystem

**COMPLETE within bounded offline contract:**typed provider-neutral canonical bars,
immutable revisions,multisymbol/1Day-1Hour-1Min retention,duplicate/out-of-order rejection,
source digests,UTC timestamps,raw-adjustment disclosure,bounded queries and pinned analysis.
**PARTIAL:**official acquisition qualification,exchange sessions,corporate actions beyond
raw metadata,per-page row lineage,resumable paging and exact-once request acknowledgements.

acquisition.py reuses StockWorkspace.permission/fetch and prices.bars. One curated symbol
per acquisition,max4 pages,max64 bars/page,max256 aggregate,512KiB raw response/page,
fixed data.alpaca.markets path,feed=iex,adjustment=raw. Daily/hour/minute windows cap366/31/7
days. Opaque cursors are bounded/URL-encoded;repeated cursors,empty pages with more data,
wrong identities,duplicates,invalid prices/order or out-of-interval timestamps reject the
entire acquisition before publishing a revision. Existing one-request/s and429/503 cooldown
behavior retained. No automatic retry or page expansion. A page budget may yield has_more;
complete_history always false. Only cursor hash is exposed,not a resumable credential.

Source coverage retains requested UTC bounds/limit/budget;receipt is last-page receipt,
not an invented timestamp for every source record. Every received page has an ordered
response SHA256. No raw pages/cursors or credentials are committed. Publisher uses injected
fixtures in this task;real-source path requires every existing Alpaca gate and explicit
observed-retention approval before requesting data.

25-second server acquisition budget;30-second client bound. If timeout occurs during a
final storage worker,an immutable revision may have committed:inspect the revision list
before retry. No cross-system exactly-once guarantee or silent cache publication claimed.
Archive data must be explicitly selected for chart/risk inspection by revision.

Gap candidates remain nominal-timeframe observations. coverage_against_declared_schedule
can compare against≤256 caller-supplied expected UTC timestamps and reports missing/extra
instants. That is not an independently verified exchange holiday/halts/session calendar.
No inferred missing trades/orders or Level2/3 state from bars.
