# SEC terminal-marker reference repair

October 29, 2026, America/New_York. Baseline and verified remote feature HEAD:
`eb5e4bb0fd53bf93990d148aa0dfcf94626ccc19`, `feat/atlas-final-release`.
Main remains `12f3a53943dc245e36f2cbbc35b9910fb21c0718`.

## Finding and evidence boundary

The owner reports a current official SEC directory response with 10,430 records and
SHA256 `b5be63822ef78687908848b349820d9d6a962af9287e2164f44f4b217259f4ea`.
Record key `7324`, insertion ordinal `7325`, has a five-character string ticker,
`TRAILING_SEPARATOR` shape, relation `OTHER_STRING` to AAPL, with one exact AAPL
reference elsewhere. These are **owner-observed diagnostics**, not an independently
downloaded response in this environment. The actual ticker and its CIK were not
provided and are not guessed.

The root cause is the local reference pattern in `terminal/stocks/sec_identity.py`:
`[A-Za-z0-9]+(?:[.\-/$^][A-Za-z0-9]+)*`. Every separator had to be followed by an
alphanumeric group. Consequently a terminal marker rejected the entire directory
before routing eligibility was evaluated, although it was unrelated to the exact
requested AAPL symbol. A symbol's difference from AAPL was never itself a rejection
condition. The earlier routing-exclusion repair could not handle this preceding guard.

A terminal separator is not sufficient evidence of a malformed **reference**. The
reported official response establishes that such a representation was encountered;
it does not establish its security type, listing status, tradability, provider alias,
or exchange semantics. No current official lexical specification or the exact source
row was acquired here. This repair accepts bounded opaque reference text, rather than
declaring every terminal-marker form a legitimate routable equity ticker.

## Exact bounded policy change

The reference pattern now permits **one** terminal character from the existing
separator set, `. - / $ ^`:

```text
[A-Za-z0-9]+(?:[.\-/$^][A-Za-z0-9]+)*[.\-/$^]?
```

The profile is intentionally versioned as `sec.reference.terminal-marker.v3`.
Failure JSON remains schema `gig.sec.qualification.failure.v2`. No new external
endpoint, runtime dependency, request, or configuration setting is introduced.

- Exact source text is preserved. There is no stripping, case folding, punctuation
  substitution, inferred class suffix or cross-provider alias.
- The application routing grammar is unchanged. All terminal-marker forms fail it
  and become explicit `unsupported_routing_symbol` exclusions. They cannot enter
  `workspace.issuers`, affect AAPL's CIK, become routing inputs, or acquire feed rights.
- Every record still passes schema, CIK, ticker safety and title validation before
  exclusion. Exact duplicate ticker strings, including excluded strings with the
  same or conflicting CIK, still reject the whole refresh. Different exact tickers
  may share a CIK, as before; an issuer can have multiple securities/classes.
- Duplicate AAPL records appearing after an excluded reference, curated CIK conflicts,
  and disappearance of cached identities into exclusions remain fatal. Accepted
  state is published atomically only after the entire directory validates.
- Empty/non-string/over-64-character values, leading or repeated separators, spaces,
  control characters, non-ASCII and disallowed characters remain rejected. The 64
  character limit includes the marker. This is not an unrestricted printable-text
  admission policy, and unknown future formats may still require explicit review.
- Existing integrity totals satisfy `input_rows = accepted_rows + excluded_rows`.
  Excluded examples remain limited to 16 record-key/ticker-digest/reason entries;
  the original whole-response digest and received timestamp are preserved. Coverage
  stays `ACCEPTED_ROUTABLE_SUBSET`, never a claim of complete listings or entitlement.
- Legacy all-rows `parse` still refuses any exclusion. The requested-symbol qualifier
  uses `parse_reference`; absence of an exact AAPL mapping still fails without falling
  back to an AAPL-like terminal reference or the curated seed.

## Reproduced failing-before and regression coverage

An independently authored directory reproduces the reported **shape and position**:
10,430 rows, five-character `AUTH-` at key `7324`/ordinal `7325`, and one exact AAPL
mapping. `AUTH-`, its CIK, filler rows, AAPL's fixture position and companyfacts are
authored, not the actual SEC source. Its digest is distinct from the owner's digest.

Before the fix, the direct parser regression errored with `sec_directory_symbol`;
the actual CLI with mocked transports returned exit 2 instead of reaching independent
fact reconciliation. The two-case failing-before log is preserved. After the fix,
the authored directory produces 10,429 routable mappings and one explicit exclusion;
AAPL resolves to its exact fixture identity and the fixture CLI reconciles successfully.
These are engineering regressions, **not successful live-provider qualification**.

Seventeen new test methods cover all five terminal markers, mixed reference formats,
exact symbol/CIK preservation, no aliasing, duplicate/conflicting excluded mappings,
late AAPL duplicates, schema/CIK/title validation, unsafe syntax, limits, bounded
exclusion examples, full CLI/source receipts/contact redaction, cache preservation,
curated identity conflicts and failure atomicity. The prior diagnostic test's single
terminal-marker negative input is replaced by a double marker; its rejection and
shape assertions remain, and the new positive/exclusion tests enforce the changed
contract. No failing test is removed or broadly relaxed.

| Executed cohort | Debug | Release | ASan+UBSan |
|---|---:|---:|---:|
| SEC/source qualification, including all new regressions | 126/126 | 126/126 | 126/126 |
| Stock/provider/SEC regressions | 207/207 | 207/207 | 207/207 |
| Native-backed terminal compatibility | 274/274 | 274/274 | 274/274 |

All final rows have zero failures, errors and skips. All three sanitizer cohorts
report `LIVE_LSAN_CHECK=0`, using the existing live-interpreter checkpoint, not a
claim of CPython shutdown leak cleanliness. The existing Starlette/httpx deprecation
warning remains visible. Additional executed checks: 52/52 security, 8/8 verified
local HTTPS/WSS checks and 8/8 frozen native reference CTest cases; all eight frozen
hashes are unchanged. No native C++ or frontend source changes require an unnecessary
full compiler/browser/package rebuild. No hosted or ARM64 qualification was launched.
Exact commands, counts, source/log hashes and frozen comparisons are recorded in
[the safe evidence manifest](sec_terminal_reference_evidence.json).

## Operational status and one verification command

**Engineering: the reported terminal-marker rejection is reproduced and repaired.**
**Actual SEC/Codespaces qualification: still unverified by this executor.**
The managed runtime has current enforced network policy without `www.sec.gov` or
`data.sec.gov` and no identifying SEC User-Agent. No SEC request, proxy workaround,
alternate mirror or restricted market-data access was attempted. The owner already
has ready SEC configuration; no setup or contact change is required.

From the existing repository on `feat/atlas-final-release`, run:

```bash
git pull --ff-only origin feat/atlas-final-release && .venv/bin/python scripts/qualify_sec_sources.py --fetch --resolve-identity --symbol AAPL --as-of 2026-10-28
```

This uses the existing explicit authorization checks, fixed official destinations,
one registry request and, only after identity success, one companyfacts request with
the existing 1.01-second cadence and no automatic retries. No rebuild, dependency
install or restart is required for this CLI. If another record or a later stage
fails, its bounded diagnostics remain available; this repair does not predict the
unseen remainder of the current official response. Exit 0 establishes only the
existing selected-fact reconciliation scope. Milestone 2 remains open until actual
authorized source verification succeeds. Alpaca gates, trading, retention, private
configuration, main and frozen native contracts are unchanged.
