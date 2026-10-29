# SEC qualification: bounded failure diagnostics

October 29, 2026 (America/New_York). Starting local and verified remote commit:
`47d0f57331dee73fb44ac66c39d5dc87caa44f23`, clean on `feat/atlas-final-release`.
Main remains `12f3a53943dc245e36f2cbbc35b9910fb21c0718`.

## What is established

The owner reports SEC readiness in the existing Codespace, including private-file
configuration with environment precedence. This report does not challenge or repeat
that setup. Disabled Alpaca gates do not block SEC-only qualification.

The reported old `ValueError` / `sanitized_source_or_configuration_failure` cannot
identify which source check failed. The old exception handler printed messages only
when they began with `SEC_` or `backend_`. Actual registry and financial validators
mostly emit lower-case `sec_*` codes. The handler discarded those codes and did not
record the pipeline stage. Readiness establishes configuration, not successful
network access, registry acceptance, or financial reconciliation.

**The actual rejected Codespaces source condition is still unverified.** No captured
source response or authenticated execution in that Codespace is available here.
Do not call this an SEC outage, invalid account setup, malformed official response,
or completed live qualification without the new diagnostic evidence.

## Conditions capable of producing the old generic ValueError

Assuming the reported exception class and reason were exact, these paths in the
owner's command could produce that pair:

| Stage | Plain ValueError conditions hidden by the old filter |
|---|---|
| Identity resolution | `sec_directory_budget`, `sec_directory_schema`, `sec_directory_cik`, `sec_directory_symbol`, `sec_directory_title`, `sec_directory_duplicate_symbol`: registry limits, shape, identifiers, text, or ambiguous duplicate symbols |
| Registry JSON decoding | Duplicate fields or nonstandard JSON constants (`duplicate_field`, `invalid_constant`) |
| Company-facts decoding | `source_body_budget`, `source_duplicate_field`, `source_constant`: body/duplicate/constant rejection |
| Company-facts normalization | `sec_structure`, `sec_identity`, `sec_facts`, `sec_fact_budget`, `sec_fact_record`, `sec_date`, `sec_text`, `sec_numeric`, `sec_accession`, `sec_fact_period`, `sec_filing_fiscal_year`, `sec_contradictory_fact` |
| Calendar validation | A syntactically date-shaped but impossible calendar date previously raised Python's unclassified ValueError |

The supplied AAPL symbol and `2026-10-28` are valid inputs; an invalid input is not
inferred. Normal configuration refusals and asynchronous HTTP refusals use the
`AccessError` subclass, with a different reported error type. Synchronous `SEC_HTTP_*`
errors previously retained their uppercase reason. JSON syntax errors normally report
`JSONDecodeError`. These distinctions narrow possibilities; they do not establish
which one happened. Unknown errors remain safely redacted.

## Repairs and output contract

1. Replace prefix disclosure with an exact, finite code allowlist. Recognized source
   failures retain their fixed code. Unknown exception text, names, URLs, paths,
   response bodies and contact values are not copied into output.
2. Add `gig.sec.qualification.failure.v2`, preserving `status`, `reason`, `error_type`
   and `raw_retained`, with `diagnostic.stage`, `category`, `code`, and an integer HTTP
   status when appropriate. Completed stages distinguish registry failure from a
   later company-facts failure. Additional metadata contains only configuration
   booleans/source/setting names and company-facts byte count/SHA256 when available.
3. Use the existing private SEC loader, environment precedence and SEC-specific
   permission check. Never require or enable Alpaca for this command. No saved setting
   or contact value is changed. Close the temporary identity workspace on rejection.
4. Preserve strict calendar validation while making all invalid calendar dates raise
   the same existing `sec_date` token. No formerly rejected date is accepted.
5. Validate the fixed-format CIK and declared company-facts response length before
   body iteration. Existing streaming body checks remain; excessive declared bodies,
   compression, non-200 responses and redirects are still refused.

For example, an **authored invalid ticker fixture**, not an actual SEC observation,
now returns the bounded diagnostic:

```json
{"stage":"identity_resolution","category":"SOURCE_SCHEMA","code":"sec_directory_symbol"}
```

A company-facts HTTP refusal reports `stage: companyfacts_fetch`, `category:
HTTP_STATUS`, `code: sec_http_status`, and its numeric `http_status`. A registry HTTP
refusal reports the same category/status at `identity_resolution`. Other categories
include CONFIGURATION, SOURCE_JSON, SOURCE_IDENTITY, SOURCE_SEMANTICS, RESOURCE_LIMIT,
SOURCE_ENCODING, SOURCE_HEADERS, RATE_LIMIT, TIMEOUT, PROXY and CONNECT_OR_TLS.
Unrecognized exceptions remain UNCLASSIFIED with a sanitized reason, rather than
guessing their cause. The script's exact allowlist is the authoritative code inventory.

Successful reconciliation retains `gig.sec.reconciliation.v1`, exact independent
record calculations and its selected-record scope; diagnostics are additive. Exit 0
still requires agreement with supported records; mismatch/empty results remain exit 1;
blocked/invalid failures remain exit 2. This command cannot certify Milestone 2 alone.

## Reproduction and automated validation

All fixtures are independently authored and make no real SEC requests.

- Preserved initial failing-before log: three failures, covering hidden directory
  validation, hidden period validation, and prefix-lookalike exception-text disclosure.
  The disclosure reproduction used an authored contact marker, not an actual leak.
- Preserved additional failing-before calendar regression: one failure, demonstrating
  loss of the fixed date code. The corrected version rejects invalid start/end/filed
  dates consistently.
- New SEC qualification cohort: 26 tests. This includes the exact owner CLI with a
  mocked invalid registry, private-file ready configuration with disabled Alpaca, full
  fixture reconciliation, both HTTP failure stages, missing authoritative identity,
  JSON/duplicate/constant/budget rejection, contradictory facts, transport categories,
  contact redaction, no retry, and identity failure atomicity/cleanup.
- Combined affected cohort: **79/79** each with Debug, Release and ASan+UBSan native
  bindings: 26 new + 32 existing operational + 21 existing backend tests. Zero failures,
  errors or skips. Sanitizer live-interpreter LSan check: 0.
- Existing stock/SEC/live cohort: **207/207** with Release bindings, zero failures,
  errors or skips, rerun after the final source change.
- Native independent frozen cases: **8/8**, all eight expected hashes unchanged.
- Syntax and `git diff --check`: PASS.

Exact commands, source/log hashes, counts and initial failures are recorded in
[the evidence manifest](sec_qualification_repair_evidence.json). Local detailed logs
are in ignored `build/sec-qualification-repair/`. No native C++ or frontend source,
provider gate, workflow, dependency or frozen expectation changed. Unrelated browser,
compiler and packaging matrices were not repeated. The existing Starlette/httpx
deprecation warning was retained. The sanitizer result checks a live interpreter,
not CPython shutdown leak cleanliness. No new hosted or ARM64 run was launched.

## Limits preserved

The CLI remains explicit `--fetch` only, fixed official SEC destinations, identifying
User-Agent required, TLS verified, no redirects or automatic retries. The registry
retains its 10-second operation timeout, 8-second HTTP timeouts, 8 MiB body and 50,000
issuer bounds. The registry-to-companyfacts cadence remains 1.01 seconds. Companyfacts
retains 8-second HTTP timeouts, 25-second body deadline and 8 MiB ceiling. Blocking
read/cleanup can exceed the body deadline; this is not a hard process-runtime promise.
Qualification disables observed stores only in its process, without changing saved
configuration or enabling retention. No trading or Alpaca operation is added.

The Cloud runtime has no configured provider credentials/contact and enforced network
policy excludes SEC hosts. The actual CLI here stopped at `sec_configuration` with
exit 2 before source access. This is distinct from the owner's ready Codespace; it is
not a request to repeat setup. No SEC network request or restricted dataset access
was attempted. Live SEC qualification and the exact owner-side failure remain open.

## One safe Codespaces retest

Run this from the existing repository on `feat/atlas-final-release`. No server restart,
new keys, configuration edit or contact disclosure is required:

```bash
git pull --ff-only origin feat/atlas-final-release && .venv/bin/python scripts/qualify_sec_sources.py --fetch --resolve-identity --symbol AAPL --as-of 2026-10-28
```

This makes at most one registry GET and one companyfacts GET, with the existing
cadence and no automatic retries. On failure, the printed safe JSON identifies the
failed stage/code; it does not print the SEC User-Agent or response contents. On
success, agreement still covers selected reported facts only, not complete statements,
intraday point-in-time correctness, provider-wide availability or final acceptance.
