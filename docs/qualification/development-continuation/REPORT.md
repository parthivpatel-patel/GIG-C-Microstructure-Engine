# GIG development continuation report

Date: November 10, 2026 (America/New_York). Branch: `development/gig-ui-redesign`.

## Result and scope

The interrupted implementation was preserved and extended. Bounded trade-reference reconciliation, local capture isolation and hot worker recovery are now implemented and offline verified. The full historical development scope is **not declared complete**: stronger corrected exchange-tape, durable hot L3, full historical statement/vintage and legacy acceptance contracts remain explicit in the matrix. No feature was silently excluded as optional. The earlier report's optional-scope wording is superseded by this report.

No application, server, browser application, provider connection, deployment or final acceptance test was started. No credentials, raw market dataset, account/order operation or observed storage were used. Public npm/PyPI advisory metadata queries were performed; these were not market-data requests. GIG branding, all 12 workspaces/15 visualization modes, native calculations, execution-disabled controls and private-Origin boundaries were preserved.

The reviewed baseline is `e0d5741dcef172b9d7cd30754221429479f67192`. The user's latest interrupted checkpoint `f35c0ca84a7cec9425987caf2d011709ec7b87a0` was preserved. It contained the SEC continuation, retry-stability and text-alternative work below. Follow-up implementation commits:

- `9984b87725ddfcb2afbe6cdaa582569b1cc60ddb`: bounded trade reconciliation, progressive frontend view, orphan/interrupted worker recovery and regressions.
- `f046f653b64f7064314cf2f24c63f04d17a56d10`: actual Python-to-TypeScript packet contract check and strict feed/generation admission.
- `69fa9be4fb9eb0a5062ed4f37ab1c31c704d740e`: local capture namespace, versioned derived contract and cross-capture rejection.
- `ff5e06d965b6859a856ef857c4ebdde36f64cc87`: executable no-application developer subset.
- `b37fd030375a93f6f79ae389505fb278d66304ed`: persistence and projection compatibility included in that fixed subset.

The final documentation-only commit is identified by Git, avoiding a recursively embedded self-hash. Evidence binds the tested source and each changed file separately.

## Implemented behavior

### Corrected trade references

`terminal/stocks/trade_tape.py` consumes the existing bounded normalized observation contract without mutating its inputs or the native book. Exact decimal/rational arithmetic matches original price and size before applying corrections. It preserves original source time/capture priority, correction lineage, venue/tape/reference scope and source-frame hashes. Different replacement IDs retire old IDs; same-ID corrections retain original lineage. Identical semantic duplicates are counted; conflicting duplicates, missing originals, reused IDs, malformed values, mixed origin and changed capture context fail closed. Receipt order is respected even when source clocks move backwards. A causal-prefix test verifies future corrections cannot change earlier results.

The derived `gig.bounded.trade_reconciliation.v2` includes the local capture namespace plus generation and symbol. A namespace is generated per LiveIEX instance and retained with its observations. It is **not an exchange sequence, exchange session or trading date**. Equal generations from separate process captures cannot be merged. Legacy records without that field are still retained as historical observations; a corrected derived total cannot be certified from them. The raw observation/metrics contracts remain available. This derived schema is additive and versioned; none of the eight native reference identities changes.

Cancellation removal is implemented only for an explicitly selected **authored** `AUTHORED_CANCEL_C_V1` fixture contract. Observed cancellation/error action codes remain unqualified; the implementation does not guess their meaning. An observed cancellation, unknown original or evicted original produces `UNRESOLVED` with a null aggregate, never automatic liquidity restoration. Existing raw metrics continue to suppress ambiguous correction/cancellation volume. The new panel exposes an independently validated derived result without replacing those conservative raw metrics.

Budgets remain 256 retained observations and at most four symbols. The reducer validates reference/data lengths, source hashes, origin, positive exact price/size, safe generation/receipt integers and capture order. A derived complete-tape flag is always false and native-book mutation count always zero. MemoryError propagates; input observations remain unchanged. Hashes establish deterministic retained-content consistency, not authenticated exchange completeness. Replaying the same retained records with the same capture metadata reproduces the same derived result; newly captured sessions intentionally have distinct namespaces.

Frontend admission checks validate symbol/generation/capture, lineage membership in the actual retained window, counts, decimal precision and rational totals using integers. The progressive text table exposes exact price/size/source nanoseconds and lineage, paginates 32 rows, and explicitly labels incomplete known prefixes. Missing input is unavailable, not zero full-market volume. The actual Python decoder/view output is accepted by the actual TypeScript contract checker in the no-server regression.

### In-memory feed recovery

A reproduced orphan subscription previously blocked explicit restart after its worker had ended. Restart now recognizes only a known completed worker in DISCONNECTED phase as orphaned. Inputs/authorization are validated before its state is cleared. An active handover still cannot be overwritten by another start.

Unexpected coroutine cancellation previously left a misleading worker state. It now publishes `RECOVERY_REQUIRED` and clears socket/phase; explicit owner stop instead publishes `STOPPED`. Cleanup, pending subscriptions and fresh-observation requirements are tested. Source accounting/generation fences and existing backoff/jitter remain in effect. Recovery diagnostics explicitly say `hot_l3_restored=false` and source loss is unknown because no exchange sequence is supplied.

At the preserved f35 checkpoint, one quote on each flapping connection previously reset the failure counter indefinitely. Reset now requires a configured stable subscribed interval (default 30 seconds, bounded 1–300), including a quiet healthy connection. A quote alone is insufficient. Retry exhaustion, rapid reconnects, quiet feeds, unauthorized attempts and malformed restart isolation are covered with fake sockets/clocks. No live provider was contacted.

These are runtime worker/subscription repairs, not durable joint native/source hot restoration after process loss. The historical observation store and authenticated authored cold replay remain separate. No crash-safe hot L3 guarantee, exact-once exchange delivery or no-loss backfill claim is made.

### Preserved SEC and accessibility completion

SEC history now supports explicit continuation through up to 128 validated advertised older-shard descriptors. Each operation remains bounded to at most two older shards, 25 seconds and 1,024 selected filing entries. A digest binds the continuation to CIK and the validated advertisement; source changes reject before shard publication. Fixed official source paths, shared request-rate waits and per-read permission checks remain mandatory. A selected batch replaces the filing view; it does not imply cumulative full financial history. Original financial receipt metadata is preserved, with a separate filing receipt driving frontend refresh.

Exact keyboard-readable tables supplement historical candlestick hover values in company/archive views; the calendar-history workspace reuses its existing table. Units, source captions, nanosecond timestamps and zero volume remain visible. Native help dialogs, skip link, keyboard controls, GIG identity and existing theme/layouts were preserved. SSR checks validate actual leaf markup; they are not visual browser or assistive-device acceptance.

## Reproduced failures and retained limitations

Failing-before logs are bound in EVIDENCE.json:

- Retry-flap regression expected two attempts but made six before a fixture guard stopped the old loop.
- Orphan-worker restart raised `subscription_update_pending`.
- Interrupted worker remained CONNECTING instead of RECOVERY_REQUIRED.

Final versions pass without reducing retry assertions or weakening risk/security checks. Early developer attempts also exposed a test-side Fraction string conversion issue and TypeScript import/unused-variable errors; these were corrected before final test/build success. A no-launch guard caught two app/API tests in an early broad selection; the fixed 86-test developer subset deliberately excludes those app-factory tests. The future full 244-case cohort still contains them and is registered, not executed. No original full-suite assertion was removed. Retained setup/cache/path failures and older exploratory logs are not presented as final passes.

## Executed developer validation

| Check | Passed | Failed / errors | Skipped | Scope |
|---|---:|---:|---:|---|
| No-launch subset, existing Release bindings | 86 | 0 / 0 | 0 | Fake transports, SEC fixtures, reducer, persistence and projection |
| Same subset, existing Debug bindings | 86 | 0 / 0 | 0 | Same tests; no fresh native build |
| Same subset, existing ASan/UBSan bindings | 86 | 0 / 0 | 0 | Halt-on-error; existing CPython sanitizer policy |
| Frontend Node tests | 143 | 0 | 0 | Includes 5 tape admission, 2 actual tape SSR, 3 bar SSR and 3 SEC cursor tests |
| Python normalized packets → TypeScript contract | 6 | 0 | 0 | Real decoder/view, authored trade/correction/cancel; no app |
| Source archive include-pattern regressions | 3 | 0 | 0 | Packaging pattern scope only; no new installed-wheel campaign |
| TypeScript + Vite production build | PASS | 0 | n/a | Build only; no serving assets |
| Dependency consistency | PASS | 0 | n/a | Existing runtime environment |
| Public npm audits, production and full graph | 0 listed vulnerabilities | 0 findings | n/a | Current public advisory metadata |
| pip-audit 2.10.1, 17 pinned server requirements | 0 listed vulnerabilities | 0 findings | 0 | Public PyPI service; isolated audit tool |

The 13 reducer tests include 1,000 seeded independently computed integer-map candidates plus deliberately corrupted expected totals. They also cover allocation failure, causal prefixes, precision, generation/symbol/capture boundaries, source inconsistencies and cancellation rejection. Those candidates are assertions inside a test, not 1,000 additional unittest cases. Ten persistence tests include interrupted writes, corruption, abrupt process exit, 10,050-observation capacity trimming and concurrent pruning. Three projection tests include 1,000 reconstructed windows; they do not establish actual browser-push latency.

The no-launch runner hard-rejects socket bind/connect/connect_ex and application factory calls, with an exact expected count of 86. It is committed at `terminal/tests/run_no_launch_suite.py`. The dedicated cross-language tool applies the same no-server policy. Fake lifecycle coroutines and temporary private synthetic SQLite files are not application startup or enabled observed-data retention.

No new C++ compilation, native CTest, eight-hash execution, real API server, browser application, TLS/WSS service, screenshot or ARM64 run occurred. The baseline's eight frozen identities and prior API/browser evidence are retained as source-bound prior evidence, **not rerun results**. Native sources, bindings, CMake and reference expectations are unchanged. Existing Release/Debug/sanitized binding artifacts were used for these Python environments. ASan options include `detect_leaks=1:leak_check_at_exit=0:halt_on_error=1`; this does not prove Python process-shutdown leak clearance. UBSan halts on errors.

Warnings retained: Starlette/httpx TestClient deprecation on import (no TestClient is started), the existing deferred Three.js chunk advisory (>500 kB), and a pip-cache permission warning on `pip check` (consistency check passed). The pip-audit tool also warned that `--no-deps` is intended for pinned requirements and recommends fully hashed pins; this bounded audit is not a new reproducible lockfile or full transitive resolution. No warnings were suppressed. Advisory success does not clear target OS, all optional/transitive artifacts, future CVEs or the owner-private edge.

## Measured resource sample

The source-bound pure reducer sample used 256 authored normalized observations across AAPL/MSFT/NVDA/CRWV, five warmups and 30 repetitions, checking 64 active records per symbol on each pass. CPython 3.12.14, Linux x86_64. Four-symbol reducer time: median 5.644 ms, minimum 5.086 ms, maximum 7.485 ms. Additional traced peak excluding input construction/imports: 79337 bytes. Whole-process peak RSS: 21140 KiB. This was measured at `ff5e06d965b6859a856ef857c4ebdde36f64cc87`; the later no-launch-runner-only commit does not alter measured reducer code.

This is a small deterministic function measurement. It is not source/network/ingestion latency, total terminal memory, a full-session capacity claim, p99 service latency or an institutional SLA. No equivalent full corrected-tape baseline was available, so no speedup is claimed. Built initial JS remains about 254.5 kB, while the approximately 517 kB Three.js/OrbitControls chunk remains deferred. Exact final asset bytes/hashes are in EVIDENCE.json; no browser execution or GPU performance was measured here.

## Requirement reconciliation and unfinished work

The matrix retains 48 reviewed implementation/qualification areas plus the separate historical A18/A19 decision row: **34 COMPLETE, 7 PARTIAL, 7 BLOCKED, 0 wholly NOT IMPLEMENTED, 1 NOT APPLICABLE**. COMPLETE refers to each stated bounded contract and cited evidence. It is not an overall readiness percentage.

Both formerly unimplemented rows are now partially implemented, with missing subrequirements explicit:

- **MD06:** canonical correction chains and authored cancellation work. The observed cancellation/error action mapping and complete/lossless exchange-tape recovery still need authoritative source semantics and replay/completeness authority. These cannot be guessed from field shape or IEX Level 1.
- **REL02:** hot in-memory worker recovery works. Joint durable source/native hot checkpoints are still missing; a coherent state/initialization contract and target durability qualification are required. Authored cold replay and retained historical observations are not a substitute.

The other five PARTIAL rows remain: full current listing coverage (importers exist; actual source coverage must be reconciled); full statement/XBRL and PIT-vintage fidelity (bounded filing batches now reachable; original missing source receipts are not recreated); target runtime/artifact security clearance; exhaustive accessibility/device acceptance; and the original A18/A19 baseline/estimator decision. Attempting to resolve the original pasted master attachment failed authorization/resolution. The documentation-only audit preserves the unknown requirement; this task does not invent an estimator or retroactive acceptance. No LOBSTER attachment was opened.

The seven BLOCKED rows remain complete observed L3/reference validation, physical GPU/browser/device acceptance, current real SEC reconciliation, owner IEX qualification, empirical forecasting/fill/alpha validation, private Codespaces edge acceptance, and current-candidate genuine ARM64. No new dataset, source authority, owner credentials or hardware evidence was fabricated.

**Required decisions/evidence before stronger implementation claims:** an authoritative observed cancellation/error profile; the intended tape completeness/backfill guarantee and source; a defined joint durable hot-checkpoint contract; a full financial-statement/vintage fidelity contract with legitimate input authority; and the missing historical A18/A19 specification or explicitly prospective versioned decision. These are narrower unresolved contracts, not requests to repeat credentials or an invitation to add speculative features. No general provider-authorization discussion was reopened.

No deployment instructions are being executed and no intermediate manual test is requested. Existing exact-SHA private deployment/rollback and provider qualification runbooks remain available for a later separately authorized acceptance phase. Keep real and paper execution off, private ports authenticated, storage separately permission-gated and IEX Level 1 distinct from replay/model depth.

## Reproduce developer checks without launching

Run from the repository root using an existing appropriate binding build and installed project test dependencies:

```bash
PYTHONPATH=<binding-build>/python:. <venv>/bin/python terminal/tests/run_no_launch_suite.py
PYTHONPATH=<binding-build>/python:. <venv>/bin/python terminal/tests/check_trade_contract.py
```

These commands need no provider credentials. The sanitizer profile additionally requires its matching ASan/libstdc++ preload and the options documented above. The root `terminal/tests/offline_guard` can also be added to inherited PYTHONPATH to prevent external network use in fixture child processes. Release/Debug/sanitized source receipts, exact local commands and log hashes are recorded in EVIDENCE.json.

Frontend-only checks:

```bash
npm --prefix terminal/web test
npm --prefix terminal/web run build
```

They compile/test without starting a server. The full `run_live_market_suite.py`, browser programs, deployment qualification and launcher must wait while the no-launch directive is active. The pure reducer resource experiment is reproducible using `event(i+1,symbol=['AAPL','MSFT','NVDA','CRWV'][i%4],price=100+i,size=1+i%10)` for i in 0..255, then four `reconcile(rows,symbol,1)` calls per pass. See the measured parameters and code/source hashes in the evidence manifest.
