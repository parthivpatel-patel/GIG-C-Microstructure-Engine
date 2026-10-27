# Bounded SEC identity and historical acceptance engineering

Baseline:8cd87af51585023af875679affe136a91d816a81.
This is an offline-engineered extension,not a claim of observed SEC reconciliation.
The current execution environment has no valid identifying SEC User-Agent or enabled
review flags. No SEC data requests were attempted. APLD and CRWV therefore still
have null CIKs in the default application. No candidate CIK was guessed.

## Identity resolver

An explicit proof-authorized POST `/api/v1/stocks/sec-directory` with an empty object
fetches only `https://www.sec.gov/files/company_tickers.json`,using existing SEC
permission,identifying User-Agent,verified TLS,no redirects,no automatic retries,
eight-second transport and ten-second operation limits,8MiB response cap and the
shared one-request-per-second rate limiter. No browser URL is accepted.

The expected directory profile is the SEC's indexed objects containing exactly
cik_str,ticker,title. At most50000 entries are accepted. Booleans/floats/invalid CIKs,
invalid symbols,duplicate tickers,contradictory curated routes and changes/removal
of cached accepted issuers are rejected atomically. A future schema change fails
closed. Accepted identity carries URL,SHA256,receipt and OBSERVED_OFFICIAL_RESPONSE
or HISTORICAL_SYNTHETIC provenance. Fixtures use deliberately authored CIK42/43;
these are **not** the historical or current CIKs of APLD/CRWV.

Search and company selection use accepted mappings without granting market feed
permission,tradability,current listing status or historical symbol identity. Unknown
issuers retain null CIKs. Existing curated AAPL routing remains available. The cache
is process-local;restart requires an explicit authorized refresh. Selecting a symbol
alone never invents a mapping or obtains an automatic whole-market directory.

## Historical filings

Proof-authorized POST `/api/v1/stocks/sec-history` accepts only symbol,max_shards.
max_shards is an integer0–2. It requires an accepted/curated issuer identity and SEC
permission. Within25seconds it fetches current submissions,then at most two advertised
older shards at fixed data.sec.gov/submissions paths. Filenames must bind to that
same CIK;external URLs,traversal,duplicate names,malformed counts/dates and contradictory
overlap are rejected. Each shard must match its advertised input row count/date range.
The metadata profile is bounded to128 shard descriptors and10000 rows per source.

Each source is normalized with a1024-row output budget. The merged retained union
is deduplicated by accession,conflicts rejected,and bounded to1024 filings. Counts
explicitly describe retained/possibly truncated union,not complete source history.
Unrequested shards and truncation remain reported. All remote work is staged before
one cache publication;failed later shards preserve the entire previously accepted
financial cache. Financial-fact receipt time and source digest remain unchanged when
only filings are refreshed. Filing receipt is separate. The legacy source arrays
and per-component source receipts remain consistent.

The v2 readonly filing pager now accepts offsets0–1024 with up to50 rows/page;the
frontend enforces the same bound. GET never initiates shard acquisition. Default
existing normalization still retains128 recent filings,so ordinary refresh behavior
is preserved. Acceptance filtering supports the explicitly enlarged1024-file cache.
Companyfacts revisions remain bounded;this does not implement full XBRL contexts,
complete source vintages,or a complete point-in-time database.

## Acceptance and amendments

Normalization and retained-cache filtering now share one timezone-explicit ISO-style
acceptance grammar,with up to nine fractional digits and exact nanosecond comparison.
An independently reproduced inconsistency previously admitted a space-separated
timestamp during normalization,then rejected it at filtering. The normalization now
rejects that value consistently. Unknown acceptance is never substituted by midnight.

Tests independently establish original value100 before the authored amendment cutoff
and restated value200 only after the amendment's acceptance;10-K/A remains explicit.
Current companyfacts snapshots cannot prove what a past response contained. Missing
older revisions/acceptance metadata remain excluded and coverage stays PARTIAL.

## Frontend and security

Stock Intelligence offers explicit identity-resolution and bounded older-filing actions.
Both obey existing gates and endpoint-bound one-use request proofs,including private
Codespaces rewritten-Origin handling. Forwarding headers confer no authority.
No wildcard CORS or localhost allowance was introduced. Async responses are guarded
against overwriting a newly selected company. Operations now presents retained record
count/bytes/policy separately from live state;it does not initiate storage or acquisition.

## ARM64

This machine is x86_64,with neither an AArch64 compiler nor QEMU. No new native ARM64
qualification is claimed. The separate `.github/workflows/atlas-native-arm64.yml`
preserves the six native configurations,all eight frozen hashes,strict outcome counts,
wheel/source checks and private fixture tests. It is manual-only,requires the owner
free_usage_verified input,and runs only on feat/atlas-final-release using standard
ubuntu-24.04-arm. The existing bootstrap workflow remains unchanged. No workflow was
dispatched,rerun,cancelled,registered on main or treated as cost-approved execution.
Default-branch registration/owner-authorized execution is an external qualification
step;the file's presence is not evidence that ARM64 has run.
