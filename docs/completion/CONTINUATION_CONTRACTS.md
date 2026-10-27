# Continued streaming, discovery, acceptance and retention contracts

Recovered baseline: `6f7e33cbe272417d95c0c2838c7eefe863ba422b`.
All provider experiments in this checkpoint use authored fixtures or the default
gated application. No observed-market qualification or permission is inferred.

## Browser projection

`POST /api/v1/stocks/events` accepts the legacy empty object or
`{"profile":"delta-v1"}`. Origin/Host and endpoint-bound proof checks are unchanged.
The new browser requests the opt-in projection. Each HTTP connection begins with
full retained history. Generation, symbol or channel changes also force a full
window. Subsequent frames contain new receipts and the authoritative retained
receipt/state/age list. Other state, metrics and latest observations remain full.
This is history projection, not complete tape or minimal field-level compression.
Transport sequence/base and receipt checks reject gaps, reuse, rollback, unknown
identities and inconsistent windows before publishing browser state. Reconnection
constructs a fresh reader and obtains a full window. Legacy consumers remain valid.
The eight-client, bounded-buffer, send/open/heartbeat deadlines remain in force.

## Discovery is not issuer identity or entitlement

Stock Intelligence global/local search and company selection use the same bounded
market catalog as subscription validation. AAPL retains its curated CIK. APLD and
CRWV have curated display identities but **null CIKs**, no SEC refresh capability,
and no invented financial observations. These display seeds are not freshly
reconciled official listing observations. Search never activates a feed.

An optional private catalog supports up to 50,000 identities, an 8 MiB source file,
and twenty results per search. An authorized owner may provide:

```json
{"schema":"gig.market.catalog.v1","source":{"reference":"owner documented authorized source","as_of":null},"assets":[{"symbol":"EXAMPLE","name":"Authored example","exchange":"AUTHORED","asset_id":null}]}
```

Use an owner-only regular file (mode 600) in ignored `.gig-symbols/`, with
`GIG_MARKET_CATALOG_FILE` and `GIG_MARKET_CATALOG_USE_APPROVED=1` only after
establishing permission. The imported catalog replaces market search entries;
known curated financial CIK routes remain separate. Unknown CIKs are never derived
from a symbol/name. No official directory was acquired or redistributed here.
Symbols not in the configured catalog remain explicitly unavailable.

## SEC acceptance filtering

Read-only `/api/v2/companies/{symbol}/acceptance-view?at=...` requires an explicit
RFC-style timestamp with timezone, preserving up to nanoseconds. It matches retained
facts/revisions to cached submissions accessions, excludes missing/conflicting
acceptance times and later facts, and uses the existing exact descriptor calculator.
No filing-date-to-midnight substitution or JavaScript ratio calculation is made.
The Financials view exposes this as optional retained-cache research, with exclusions.
Recent submissions and bounded retained revisions cannot reconstruct complete XBRL
history or authenticate what an older SEC response contained. This remains PARTIAL
point-in-time support, not a tradable, look-ahead-free database claim.

## Optional durable normalized observations

Default storage is **disabled**. No credentials/permissions were enabled here.
For observed storage, existing Alpaca permission gates plus all of
`GIG_ALPACA_STORE_ENABLED=1`, `GIG_ALPACA_STORAGE_APPROVED=1`, a documented
`GIG_ALPACA_STORAGE_REFERENCE`, and explicit `GIG_ALPACA_STORAGE_SECONDS` (1–86400)
are required. Set `GIG_ALPACA_STORE_DIRECTORY` to a private owner-only directory;
ignored `.gig-observations/` is the default. This configuration must reflect actual
retention rights, not merely a publicly accessible feed.

SQLite FULL synchronous transactions append an entire accepted source frame before
RAM publication. Local capture IDs and storage clocks never become exchange IDs.
Records retain source provenance but not dead monotonic clocks. Recovery verifies
hash links and the committed tail; returned observations are historical, never
restored as live/current or native L3 state. Tests include an actual precommit
process exit and disk failure. No crash-safe hot L3 recovery is claimed.

Limits: 128 records per transaction, 64 KiB per normalized record, 10,000 retained
records, 16 MiB logical payload, 32 MiB database, plus up to 32 MiB rollback journal
and filesystem overhead. Prefix pruning preserves chain verification. Immutable
per-record expiry cannot be extended by reopening with a larger retention policy.
Clock rollback can make expiry nonmonotonic: pruning through the last expired record
may deliberately evict earlier unexpired records to retain a contiguous verified
suffix. Reads exclude expired records; startup/append and the running minute sweep
prune them. An offline process cannot guarantee timed physical deletion, and the
host/filesystem backup policy remains an owner responsibility. Hash consistency
is not tamper-proof exchange authenticity; bounded retention is not global exactly-once.
No ledger/journal redesign or native behavior change is included.

## Reproduce offline

With existing validated bindings and dependencies:

```sh
PYTHONPATH=build/python-debug/python:. .venv/bin/python terminal/tests/run_live_market_suite.py
npm --prefix terminal/web test
npm --prefix terminal/web run build
PYTHONPATH=build/python-debug/python:. .venv/bin/python terminal/tests/check_market_projection.py
PYTHONPATH=build/python-debug/python:. .venv/bin/python terminal/tests/measure_observation_store.py
```

Browser tests require separate gated/authored loopback fixtures, stable production
assets and Chromium/Playwright. See existing browser driver and fixture-safety guard.
`discovery-validation.mjs` checks AAPL/APLD/CRWV against the gated native app on8787;
`live-market-validation.mjs` checks the authored source on18797, not an operator feed.
