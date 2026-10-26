# Provenance and validation boundaries

Provider configuration, source authenticity, parsed consistency and empirical agreement
are separate evidence levels. None implies the next automatically.

## SEC changes

`terminal/stocks/service.py` now records successful component URL, raw response SHA256,
and post-validation receipt timestamp. Parent `requested_at` and `received_at` are
separate; previously the request-start timestamp was labelled receipt time. Legacy
URL/hash arrays remain available. Source component failures remain explicit and do not
erase other accepted sections. Hashing a body establishes identity, not financial truth.

`terminal/stocks/sec.py` preserves issuer CIK, concept/unit, exact decimal text, actual
start/end, filing date/accession/form, optional frame and filing FY/FP. FY/FP describe
the filing context and must not relabel a prior-period comparison fact. A deterministic
SHA256 source_fact_id covers that normalized record. It is not the provider's raw-body
digest. Optional metadata stays null; no acceptance clock is invented.

Latest-filed selection is per concept/start/end/unit at the chosen filing-date cutoff.
History is bounded256 selected records per metric; revision observations are bounded16
per metric with explicit truncation/counts. Revisions are not summed. This is **not**
an original point-in-time research database: old filings may restate older periods and
companyfacts does not establish intraday publication availability. IFRS/custom taxonomy,
full dimensional XBRL contexts and older submission shards are outside this parser.

## Independent reconciliation tool

`scripts/qualify_sec_sources.py` independently selects source records from original JSON,
checks metric coverage/period keys/latest filing/value/unit/context/issuer, and recomputes
record identities without calling production selection or exact-value helpers. It emits
counts, mismatch categories and hashes, never raw financial rows. Missing metric records,
changed values or wrong issuer cannot pass. Empty selected scope is INCONCLUSIVE.

Offline input requires an authorized source JSON copy; file origin is explicitly not
authenticated. `--fetch` requires existing SEC review/contact gates and requests exactly
the fixed official companyfacts endpoint, no redirect/retry or source retention. The
optional `--compare-cache` addresses only127.0.0.1:8787 and requires equal issuer/as-of.
An output path is created exclusively, not overwritten.

Example after owner authorization/network/contact setup and actual SEC loading:

```bash
python scripts/qualify_sec_sources.py --symbol AAPL --as-of YYYY-MM-DD \
  --fetch --compare-cache --output /tmp/sec-reconciliation.json
```

Use the exact cache as-of date, not the placeholder. Review safe output before sharing.
A second network response can legitimately differ from a cached response; investigate
raw digest/cutoff/revisions rather than modifying expected numbers. A positive result
covers selected records only, not complete statements, ratios, predictions or L3.

## Market and model boundaries

No restricted LOBSTER content was inspected or processed. No market data was downloaded.
Alpaca support381230 is pending; IEX is venue-limited L1, indicative options are not
executable quotes or OPRA, and neither supports a fabricated equity depth ladder.
Historical, synthetic, simulated, observed response and user-authored model categories
remain distinct. Existing export verifier tests protect dataset/parent digest agreement
and VWAP profile dependencies. Eight frozen native canonical identities remain intact.
