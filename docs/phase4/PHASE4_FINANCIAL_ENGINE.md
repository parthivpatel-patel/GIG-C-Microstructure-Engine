# Financial intelligence

Existing stocks/sec.py and financials.py remain the authoritative exact normalization
and12-descriptor implementations. No duplicate JavaScript financial calculation added.
The requested growth,margins,ROA,ROE,current ratio,debt/equity,FCF and EPS growth already
exist;their period/unit/formula/source-input/missingness contracts are preserved and
retested. Cash conversion remains the twelfth descriptor. Official reconciliation is
still an owner gate;no approved identifying User-Agent is available here.

New stocks/statements.py aligns selected income,balance and cash-flow items by exact
(start,end). It does not combine different durations under one fiscal label. Annual
uses350..380-day10-K/A facts;quarter means actual75..105-day reported duration;YTD means
106..349-day10-Q/A duration. These are duration categories,not invented fiscal-quarter
identities. Balance sheets remain reported instants independent of duration filter.

Each selected field contains its exact value/unit/status and original normalized source
facts,including concept,filing/accession and source identity. Missing fields are null,
not zero;multiple competing eligible concepts are ambiguous,not arbitrarily selected.
Maximum12 period packets;truncation explicitly reported. Amendments/restatements use
existing latest-per-concept as-of policy;not original intraday point-in-time histories.

Financial Statements now offers an explicit Load aligned reported periods action next
to the retained original exact fact table. Compact values preserve full precision in
expandable details. The response and UI say SELECTED_REPORTED_FACTS_NOT_COMPLETE_STATEMENTS.
No claim of complete XBRL presentation,accounting taxonomy,dimensional context,quarterly
cash-flow reconstruction or independent statement reconciliation follows.

Tests retain original independent12-formula/2000-margin references and add packet
alignment,missing quarters,competing concepts and browser source/missing-item controls.
The dedicated browser fixture intentionally omits one2023 gross-profit fact;that omission
is independently authored,not an observed Apple accounting discrepancy.
