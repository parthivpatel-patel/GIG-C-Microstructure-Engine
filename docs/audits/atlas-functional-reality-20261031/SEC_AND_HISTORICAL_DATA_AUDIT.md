# SEC and historical research evidence

Candidate: `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`.
No SEC retrieval,private owner configuration,raw market archive or restricted
LOBSTER data was accessed. Current evidence is code,authored fixtures and explicit
owner observations. Previously reported operational results remain attributed.

## Identity,financials and source boundaries

- `stocks/sec_config.py:7–34`:SEC-only flags and identifying-contact User-Agent
  validation;private config permissions and environment precedence. Readiness is
  not permission to run a request in this audit. Values were not inspected/exposed.
- `stocks/sec_identity.py:12,57–90`:reference admission accepts bounded terminal-marker
  strings as opaque SEC text;unsupported routing forms are counted/excluded,never
  inferred aliases. Duplicate/conflicting symbols and malformed records reject
  atomically. Exact AAPL mappings preserved. Current SEC schema was **not fetched**.
- `stocks/service.py:37–78`:accepted SEC identities join catalog by exact symbol,
  not company-name guessing. Default curated APLD/CRWV can resolve withnull CIK
  until an authoritative exact mapping is accepted. Search and live entitlement
  remain separate. The default catalog has13 seeds;this is not the owner's accepted
  SEC count or a complete US equity universe.
- `stocks/discovery.py`:exact-symbol union preserves separate listing and SEC
  classifications. Accepted SEC registrants do not become verified exchange listings.
- `stocks/sec.py:51–75,77+`:filing accession/document/date validation,amendment
  identity,contradictory duplicate rejection,retained selected us-gaap facts with
  unit,period,issuer,accession and source-fact identity. Latest filing-per-concept
  selection is not complete original XBRL reconstruction.
- `financials.py`, `statements.py`, `ratio_history.py`, `accounting.py`:twelve exact
  descriptors,reported period alignment,annual/quarter/YTD eligibility,explicit
  ambiguous/missing facts,source links and calculation limitations. No quarter
  subtraction,missing-zero fabrication,full statement/IFRS/presentation/dimension
  reconstruction or cash/debt inference from a different concept.

## Point-in-time,amendments and historical coverage

`vintages.at_filing_date()` selects only retained revisions withfiled≤cutoff,
reports ambiguous same-date facts and retained truncation. It does not establish
intraday availability. `at_acceptance_time()` matches retained accession to cached
submissions acceptance timestamp,excludes unknown/ambiguous/future facts and never
substitutes midnight. Current companyfacts retrieval cannot authenticate what a
historical response contained;omitted older revisions stay unknown.

`sec_history.py` validates only advertised fixed-name submissions shards,at most2
additional shards/request and1024 selected filings. Pagination/filtering refer to
the current bounded cache,not a pinned complete historical filing database.
`service.fetch()` uses a conservative one-request-per-second cadence,no redirects,
bounded bytes/time,identity encoding and per-domain failure cooldown. Parser or
fetch failures do not publish partial contradictory identity/cache state. These
paths pass the current142 source and207 stock tests in all three configurations.

Ticker changes,delistings,corporate actions and historical security identity are
not solved by the current SEC ticker mapping. A CIK is not an instrument-history
or market-data entitlement key. Fiscal durations are actual source start/end
periods;52/53-week differences are disclosed,not silently calendar-normalized.

## Existing owner observations

The owner reports genuine SEC financial information visible in the private terminal,
10,429 routable ticker mappings and1,772 selected reconciled records withzero
mismatches. This is positive **OWNER_REPORTED** evidence,not a fresh audit failure.
Exact original report bytes/hash,tested Git SHA,qualification time and source receipt
were not supplied. No fixture or performance counter promotes the claim into
independently verified complete financial coverage.

Sprint2's binder was rerun on authored metadata in the30-case cohort. It verifies
explicit supplied report bytes/hash,source digest/count/date/scope contradictions
and an explicitly owner-declared source/time sidecar. It does not authenticate
historical execution or fetch missing data. Use
[the existing procedure](../../remediation/sprint-2/SEC_EVIDENCE_BINDING.md) with
already authorized sanitized artifacts;unknown SHA/time must remain incomplete.
Do not reconfigure contact information or initiate another fetch during this audit.

## Historical market paths and research limits

- `alpaca_history.py`/`acquisition.py`:explicit authorized raw IEX bars/quotes/trades,
  bounded pages/counts,byte/time budgets,source receipts and incomplete coverage.
  No actual IEX history was qualified here. Feed/display/cloud/historical permissions
  remain the specific unresolved scope questions.
- `history.py`:strict OHLC/time/identity/duplicate/page ordering,source hashes,
  missing/gap/incomplete-session reporting. A gap candidate is not proof of missed
  exchange events or a holiday calendar. Exact input values retained;no imputation.
- `history_store.py`/`history_backup.py`:immutable bounded private revisions,explicit
  observed-retention permission,expiry,backup validation,SQLite transaction restore.
  Current interrupted-process/corruption tests pass. This is not provider backfill,
  crash-safe full-session hot recovery or a brokerage order ledger.
- `datasets.py`:independent immutable revision reads,exact matching interval start
  AND end,explicit weights and disclosed excluded intervals. The inner intersection
  may introduce selection bias. Raw prices have no verified corporate-action/FX or
  survivor-safe-universe treatment.
- `include/gig/itch/*` and `include/gig/lobster/*`:real bounded native decoders,
  source context,initialization eligibility,replay and independent synthetic oracles.
  Browser catalog explicitly marks them CLI_AVAILABLE,not imported live data.
- Native authored replay,aggregate-profile replay and retained source recordings
  are separate. A file boundary/system-open event/top-five snapshot cannot prove a
  complete L3 empty boundary or observed queue identities. No such inference occurred.

## Readiness

Selected cached SEC research is conditionally useful when the owner's genuine
source/identity/period provenance is visible. This audit independently qualifies
its finite transformation contracts,not complete facts,full PIT or all issuers.
Authored historical replay passes;genuine historical strategy/reconstruction
acceptance remains UNVERIFIED. A five-level reference or synthetic agreement is
not full observed L3 proof. No forward-looking investment or alpha result follows.
