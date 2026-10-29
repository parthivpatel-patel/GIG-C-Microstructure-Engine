# Automatic reference discovery

This implements broad identity discovery,not complete US exchange-listing coverage.
SEC registrants,Nasdaq primary-listing directories and provider subscriptions remain
separate sources. No CIK is inferred from company names or punctuation substitutions.

## Startup and refresh

The normal server constructs StockWorkspace from its existing server environment/private
SEC configuration. When SEC identifying/fair-access configuration is ready,it loads the
fixed official company_tickers.json endpoint at startup and every six hours. Missing or
invalid identifying configuration prevents requests. Explicitly injected workspaces do
not start this source implicitly;tests use authored fetchers only.

GIG_SEC_DIRECTORY_AUTO_REFRESH=0 disables automatic SEC-reference refresh,including when
Nasdaq directory use is approved.1 enables the automatic path explicitly. Other nonempty
values report invalid configuration. The default automatic path does not enable SEC
financial permissions,Alpaca,observed retention,paid sources or trading.

Manual refresh is available through the existing endpoint-bound-proof protected
POST /api/v1/stocks/sec-directory,Stock Intelligence's identity action,and Securities
Universe's separate SEC-registrant refresh control. Successful responses are reused for
60 seconds after rechecking permissions;cached reads retain the original source hash
and receipt time. No upstream request is made on a cache hit. Subsequent downloads have
a ten-second budget and existing shared conservative SEC request pacing. Failures retain
the prior accepted mapping;no automatic retry loop is added. Restart requires a fresh
permitted acquisition;this process-lifetime reference cache is not a persistent archive.

## Index and provenance

GET /api/v2/securities searches an indexed exact-symbol union of the accepted listing
catalog/fallback and accepted SEC ticker mappings. Rows identify SEC-only mappings as
SEC_REGISTRANT_NOT_LISTING_CLASSIFICATION with exchange UNVERIFIED. Matching identifiers
can carry their SEC CIK;different share-class/vendor spellings are not guessed equivalent.
The paginated count is a count of identifiers,not unique economic securities or verified
current listings. Listing files retain a100000-row resource ceiling;the union supports
up to150000 identifiers including the bounded50000-row SEC source. Excess input is
rejected,not silently truncated. Browser responses are bounded to20 rows here.

The indexed cache holds the actual snapshot objects and invalidates on replacement,
preventing object-id reuse from selecting an old identity index. Receipts include source
URL,hash,retrieval time and authored/observed classification. HTTP GETs never acquire
provider data. The browser periodically rereads accepted reference state,without polling
upstream providers. Manual refresh rejection and accepted cache reuse remain visible.

The existing seed-consistency and cached-issuer-change checks remain in place. A changed
or removed cached CIK requires investigation rather than relabelling old company facts.
Current ticker mappings do not establish historical listing identity or point-in-time
financial information availability. Selected facts/ratios retain their existing period,
unit,amendment and restatement limitations.

## Actual coverage in this Codex instance

Safe configuration inspection:SEC ready=false,no identifying User-Agent configured,
no Alpaca credential pair. No official SEC reference request was attempted. Actual
imported SEC mappings=0;actual imported official listings=0;fallback routing identities=13.
Authoritative APLD/CRWV CIKs remain unverified here. Authored fixtures do not change this
coverage statement. See the product evidence/report for executed synthetic tests.

Nasdaq's two candidate files returned200 to metadata-only HEAD requests in the earlier
checkpoint;their bodies were not downloaded. Their linked terms do not establish the
required derived-cloud catalog use. Source permission remains a genuine external gate.
SEC is an authoritative registrant reference candidate when the existing approved
identifying configuration is available;it is not an exchange security master. Existing
provider reference imports remain permission-dependent. No unauthorized mirror or paid
source is used. Source classification and rights review must precede any redistribution.
