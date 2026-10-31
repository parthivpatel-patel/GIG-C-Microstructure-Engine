# Existing SEC evidence binding — offline only

Source: `62d8d50e2dd629db181114eaceb5845509a137b6`.
CLI: `scripts/bind_sec_evidence.py`; implementation:
`terminal/verification/{artifacts,sec_binding}.py`.

No new SEC request is authorized by this procedure. Do not rerun `--fetch` merely
to recover missing evidence. The owner's reported 10,429 routable identities and
1,772 selected records with zero mismatches remain **OWNER-REPORTED**, not newly
verified observed evidence here. No exact real report was available to this sprint.

## Input contracts

Supply an existing **sanitized** `gig.sec.reconciliation.v1` report and its
independently recorded expected SHA256. The tool reads at most1MiB from an explicit
ordinary file; symlink/FIFO/nonregular/changed inputs fail. It does not scan private
directories, discover credentials, load contact configuration, inspect raw
companyfacts or transmit files. Duplicate JSON keys, nonfinite numbers, invalid
UTF8, excessive structure and unsupported schema reject before interpretation.

It checks:

- Exact supplied report bytes versus expected report SHA256.
- Declared source response SHA256 versus the company's diagnostic receipt, where
  supplied; source byte count1..8MiB. **Report hashes and source response hashes are
  different identities.** It does not re-fetch or independently hash absent raw data.
- Status versus nonnegative bounded integer match/mismatch counts, bounded detail
  count, exact selected-record scope, filing-date format, privacy flags, symbol/CIK
  identity and fixed official companyfacts URL when official-fetch authority is claimed.
- Optional directory receipt hash, timezone-bearing received time, explicit
  synthetic/observed classification and input=accepted+excluded count accounting.
- Explicit owner-declared tested Git SHA, qualification timestamp, exact scope/date/
  count agreement and directory count where original metadata supplies it. No current
  HEAD, current date, unrelated symbol or API availability fills a missing field.

The current producer does **not** embed tested Git SHA or qualification time in
its reports. These cannot be retroactively derived from a result's success status.
An optional sidecar is an explicit owner declaration, not authenticated execution:

```json
{
  "schema": "gig.sec.binding.declaration.v1",
  "report_sha256": "<64 lowercase hex from the original receipt>",
  "tested_source_sha": "<40 lowercase hex of the code actually tested>",
  "qualified_at": "<actual timezone-bearing qualification timestamp>",
  "as_of_filing_date": "<the report's exact YYYY-MM-DD>",
  "matched_records": 1772,
  "mismatch_count": 0,
  "scope": "selected raw SEC records/values/units/periods/context/identities only;not full statements,ratios or intraday PIT validation",
  "accepted_identities": 10429,
  "attestation": "OWNER_DECLARED_NOT_INDEPENDENTLY_VERIFIED"
}
```

Numbers above illustrate the owner's claim; use them only if the actual supplied
report supports them. Do not fabricate a sidecar timestamp/SHA. If these are
unknown, omit `--declaration` and preserve `INCOMPLETE_METADATA`. A missing original
directory or source-byte receipt remains incomplete even if a declaration supplies
a count. `accepted_identities` in the declaration may be null; a null does not
verify an absent directory count. Qualification before the as-of date, future time,
source receipt after qualification, naive time or precision beyond microseconds
rejects; offsets normalize to UTC without silent precision loss.

## Command

After placing authorized sanitized artifacts in an already ignored owner-private
directory, run from the exact candidate checkout (placeholders are intentionally
not executable evidence):

```bash
.venv/bin/python scripts/bind_sec_evidence.py --report build/private-sec/report.json --expected-report-sha256 <ORIGINAL_REPORT_SHA256> --declaration build/private-sec/declaration.json --expected-source-sha <ACTUALLY_TESTED_GIT_SHA> --output build/private-sec/binding-new.json
```

Do not pass contact information, keys or tokens. Expected source SHA refers to
the code that generated the historical report, which may differ from today's
candidate. Without a trustworthy recorded hash this can only bind owner-supplied
bytes, not prove their provenance. Do not overwrite a past output.

Exit0: internally consistent selected-record agreement with explicit owner metadata.
Exit2: incomplete metadata, preserved nulls and missing-field list. Exit1: rejected
artifact/contradiction or a bound report with mismatch/inconclusive result. Output
uses `BOUND_OWNER_DECLARATION`, never `REAL_PROVIDER_VERIFIED`; it always reports
`independent_provider_verification:false`, zero provider requests, no raw records
and no private contact. Unknown report metadata is not echoed. Mismatch details
are validated for count but not printed. A binding is not new reconciliation,
complete financial statements, ratios, intraday PIT, listing-universe validation
or evidence about other tickers.

## Executed tests

16 independent authored tests per Debug/Release/instrumented consumer pass. They
cover byte tampering, duplicate keys, invalid encoding/nonfinite/nested data,
symlink/FIFO/size limits, conflicting digests/SHAs/counts/dates/scope, false authority,
unknown sensitive metadata redaction, null provenance, contradictory directory
accounting, mismatch/inconclusive status, private0600 output, no overwrite and CLI
behavior. All fixtures are `HISTORICAL_SYNTHETIC`; repeating the owner's numerical
counts in a synthetic fixture is **not** empirical evidence. See the 30-test Sprint2
cohort logs and source-bound manifest. Existing SEC142 and stock207 cohorts also
pass in all three configurations. No owner secrets or provider gates were touched.
