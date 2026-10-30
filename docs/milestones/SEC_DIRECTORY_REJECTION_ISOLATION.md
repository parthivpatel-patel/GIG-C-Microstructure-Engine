# SEC directory rejection: remaining condition isolated

**Follow-up:** Owner diagnostics now identify a five-character terminal-marker
reference at key7324/ordinal7325 of10430. See [the bounded terminal-reference repair](SEC_TERMINAL_REFERENCE_REPAIR.md).
The older uncertainty and unchanged-policy findings below describe the isolation
checkpoint; the new report documents the justified version3 policy change and its
regressions. Actual SEC requalification remains unverified here.

2026-10-30 UTC. Baseline and verified remote branch:
`5b5eb36aaa21fd259028daf06f28b3277133e9b5`, `feat/atlas-final-release`.
Main remains `12f3a53943dc245e36f2cbbc35b9910fb21c0718`.

## Decision

**The actual Codespaces SEC blocker is not declared fixed.** The owner reports that
the earlier reference/routing repair still fails with `sec_directory_symbol` during
`identity_resolution`. This investigation repairs the reproduced loss of the exact
rejection context. It deliberately does not accept previously rejected source values
without evidence of what the official response contains.

The command's remaining failure is isolated to the reference-admission ticker guard.
The next ordinary qualification command now identifies its precise predicate, record
position, requested-symbol relation and source/parser fingerprints. A successful live
SEC identity fetch or financial reconciliation was not possible in this executor.

## Complete production trace

1. `scripts/qualify_sec_sources.py:180-186` runs the `identity_resolution` step.
   Its `resolve_reference` at lines 145-153 calls
   `StockWorkspace.refresh_identities(requested_symbol=symbol)`.
2. `terminal/stocks/service.py:51-68` fetches the fixed official directory and calls
   `parse_reference`. This path does **not** call the legacy `parse` API.
3. `terminal/stocks/sec_identity.py:15-20,66-75` checks the directory budget, record
   shape and CIK, then evaluates the ticker predicate. These are all four branches
   capable of producing `sec_directory_symbol` in this command:

| Diagnostic condition | Exact rejection |
|---|---|
| `NON_STRING` | `type(ticker) is not str`, including null, boolean, number, array or object |
| `EMPTY` | String has length zero |
| `TOO_LONG` | String exceeds 64 characters |
| `REFERENCE_PATTERN` | String does not fully match the unchanged local reference pattern |

4. `terminal/stocks/sec_identity.py:91-97` is the other production raise path: legacy
   `parse` rejects any otherwise valid reference excluded by routing policy. It now
   reports `LEGACY_EXCLUSIONS_NOT_ALLOWED` and `parser_path: legacy_all_rows`.
   Its rejection behavior is unchanged. It is not the owner's CLI call path.
5. The exception constructor at line 26 retains the original fixed error token.
   `scripts/qualify_sec_sources.py:60-69` exposes only its bounded diagnostic, preserving
   external `error_type: ValueError`, failure schema v2 and exit status 2.

The previous repair separated safe reference text from routable application symbols.
It cannot help a value rejected **before** routing/exclusion, which is where this
remaining CLI failure occurs. Repeating that approach or broadening punctuation by
guessing would not establish the actual cause.

Literal `AAPL` passes the reference guard, independently tested. Thus a rejected field
cannot be exactly that string under this source version. It may be another reference,
a whitespace/case variant, or an invalid/missing value belonging to an unidentified
issuer. The old report cannot distinguish those possibilities. We do not claim that
the failing record necessarily belongs to another company.

## Source schema comparison and uncertainty

The fixed official source is
[SEC company_tickers.json](https://www.sec.gov/files/company_tickers.json).
The existing adapter expects a numeric-keyed object whose records contain exactly
`cik_str`, `ticker` and `title`, with integer CIK and string ticker/title. The ticker's
reference pattern is `[A-Za-z0-9]+(?:[.\-/$^][A-Za-z0-9]+)*`; the separate application
routing grammar remains unchanged. These are **implementation policies**, not a claim
that SEC guarantees that lexical grammar, nonempty tickers, or this exact schema
forever. Extra/missing fields or invalid CIKs produce different errors, not the
reported `sec_directory_symbol`.

The current official response and any current official allowance for blank/null or
other ticker forms could not be independently retrieved here. Runtime status is current
and its network policy is enforced; neither `www.sec.gov` nor `data.sec.gov` is allowed.
This executor also has no identifying SEC User-Agent. The safe configuration checker
reports `ready: false` here, unlike the owner's confirmed ready Codespace. Running the
actual CLI here stops at `sec_configuration` before source access. No SEC request,
proxy bypass, mirror, invented contact, or configuration change was attempted.

Consequently the live rejected record, current directory hash, exact guard branch,
and whether a legitimate source variation requires a narrowly scoped policy change
remain **unverified**. The safe record diagnostic is the missing evidence. We do not
silently discard malformed rows, normalize source symbols, or trust only a selected
AAPL row while ignoring directory conflicts.

## Safe diagnostic contract

`diagnostic.directory_rejection` contains:

- Local parser profile and source-file SHA256, parser path, exact condition.
- Validated numeric record key, one-based JSON insertion-order ordinal, record count.
  The ordinal is not an exchange sequence number or a promise about future ordering.
- Finite value type, string length and structural flags over the first 64 codepoints.
  No raw ticker, row, title, CIK, header, URL, file path or contact value is serialized.
- Validated requested symbol, exact/ASCII whitespace/case relationship, and count of
  records with an exact requested ticker anywhere in the bounded response, including
  records after the rejection. This count **does not validate those records or their
  identities** and does not authorize choosing one of duplicate mappings.
- Whole-response SHA256 when supplied by the existing verified fetch path. The digest
  must be lowercase hexadecimal of length 64. No digest of an offending field is added.
- `publication: REJECTED_NO_NEW_SNAPSHOT`. A previously accepted directory is preserved.

The class stores only this public metadata. Arbitrary exception text/attributes are
not copied into diagnostic JSON. Legacy and ordinary failures remain safely redacted.
Diagnostic whitespace/case comparisons do not normalize or admit any source value.
Source fingerprint reads add no network requests. The existing 50,000-record/8 MiB
bounds cap the diagnostic scan; shape analysis examines at most 64 codepoints.

All admission, duplicate/conflicting identity, curated identity, title, cache, rate,
TLS, redirect, response-body and permission checks remain. Failure still publishes
no partial directory and releases the refresh lock. No Alpaca, trading, retention,
frontend, dependency, native C++, workflow or credential setting changed.

## Reproduction and validation

All source fixtures are authored. They do not reproduce an unknown captured live row.

The baseline CLI reproduced the **diagnostic ambiguity**: one regression method with
seven failing subcases, covering all four guard branches, emitted only
`sec_directory_symbol`. Its failing-before log is preserved. The repaired CLI reports
the exact predicate and record metadata for the same fixtures. Fifteen new test methods
also cover requested-record position and absence/duplicates, syntax classes, legacy
rejection, fingerprints, source-digest validation, contact-marker redaction, forged
exception attributes, strict schema/identity/duplicate rejection, and failure atomicity.

| Executed check | Passed | Failures / errors / skips |
|---|---:|---:|
| Targeted new regression methods | 15 | 0 / 0 / 0 |
| SEC/source qualification, Debug bindings | 109 | 0 / 0 / 0 |
| SEC/source qualification, Release bindings | 109 | 0 / 0 / 0 |
| SEC/source qualification, ASan+UBSan bindings | 109 | 0 / 0 / 0 |
| Stock/provider/SEC regressions, Debug bindings | 207 | 0 / 0 / 0 |
| Stock/provider/SEC regressions, Release bindings | 207 | 0 / 0 / 0 |
| Stock/provider/SEC regressions, ASan+UBSan bindings | 207 | 0 / 0 / 0 |
| Native-backed terminal/security compatibility, Release | 274 | 0 / 0 / 0 |
| Frozen independent native reference CTest cases, Release | 8 | 0 / 0 / 0 |

Both sanitizer cohorts report `LIVE_LSAN_CHECK=0`. This is the existing live-interpreter
check, not a claim of CPython shutdown leak cleanliness. Existing Starlette/httpx
deprecation warnings remain visible. All eight frozen hashes match their prior values.
Counts are per-cohort outcomes, not unique tests or a coverage percentage. No unchanged
frontend/browser/packaging or full C++ compiler matrix was rerun. No ARM64/hosted run
was launched or newly qualified. Exact commands, counts, source/log hashes and frozen
comparisons are in [the evidence manifest](sec_directory_rejection_evidence.json).
Detailed local logs remain ignored under `build/sec-identity-isolation/`.

Changed implementation: `terminal/stocks/sec_identity.py`, `service.py`,
`qualification.py`, `scripts/qualify_sec_sources.py`. New regressions:
`terminal/stocks/test_sec_identity_diagnostics.py`; strict cohort registration:
`terminal/tests/run_source_qualification_suite.py`. Documentation and the safe evidence
manifest accompany the change. Existing historical reports are retained with a current
blocker note. No source rows or private configuration are committed.

## One owner verification command

From the existing repository on `feat/atlas-final-release`:

```bash
git pull --ff-only origin feat/atlas-final-release && .venv/bin/python scripts/qualify_sec_sources.py --fetch --resolve-identity --symbol AAPL --as-of 2026-10-28
```

No setup, dependency install or application restart is required. The existing explicit
fetch, SEC permission check and identifying contact remain required and unchanged.
The command makes at most one registry request and, only if identity succeeds, one
companyfacts request after the existing 1.01-second cadence; no automatic retries.
On rejection, the printed safe JSON now isolates the actual condition and record
relation without requiring raw response data or contact disclosure. On success, the
existing selected-fact reconciliation scope still applies. Milestone 2 remains open
until actual authorized source qualification succeeds; a diagnostic release is not
live-provider qualification.
