# GIG final engineering and qualification sprint

Date: November 2, 2026 (America/New_York). Branch: `development/gig-ui-redesign`.

- Preserved redesign baseline: `7f43073dfb27dcf6613dea56f5274a69cacd4adb`.
- Implemented, tested, pushed and remotely verified application checkpoint: **`2689e0b5613710cd35cf5a6cbe002a56bf86d47b`**.
- The following documentation commit closes evidence only; its exact remote SHA is reported in delivery/Git history, avoiding a self-referential hash.

## Outcome

The two interrupted engineering gaps are implemented: separate read-only IEX stream admission and bounded injectable jitter. Added an explicit private-Codespaces process profile, a fixed existing-server launcher, a bounded owner provider probe, safe failure categories and target-branch manual ARM64 preparation. No frontend redesign was repeated. All 12 workspaces, 15 visualization modes, automatic camera lifecycle, source/provenance rules, native engine, SEC configuration and execution boundaries remain.

Engineering and offline qualification for this scope are complete. Actual live/historical Alpaca, owner-private Codespaces and current native ARM64 runtime acceptance remain **PENDING**. This task had neither Alpaca credentials nor the owner's private environment; it made no real provider/account/order request, workflow dispatch or paid-resource operation. It did not process restricted datasets.

## Admission and safety

`GIG_ALPACA_IEX_STREAM_ENABLED` is the explicit read-only quote/trade/bar stream gate. When present, only exact `'1'` enables it; false, empty or invalid values cannot fall back to the legacy name. For older consumers only, absence of the new key preserves the existing `GIG_ALPACA_LIVE_ENABLED` read-only alias. The legacy name was a market-data flag, not evidence of order execution. General market-data permissions and credential validation remain independently required.

The new owner-only launcher keeps **`GIG_ALPACA_LIVE_ENABLED=0` and `GIG_PAPER_EXECUTION_ENABLED=0`**. It also disables options, SIP, history export, disk capture and asset-reference startup. It configures only process-local read-only IEX/history scope under the owner-reported Alpaca Support **#384778** confirmation. Nothing writes secrets, changes saved SEC configuration or grants account/order authority. Ordinary startup remains default-disabled.

The profile requires Codespaces metadata, one exact configured HTTPS origin and an explicit owner assertion of private single-user use. Metadata and a CLI assertion are not independent proof of GitHub private-port authentication. The existing Origin/Host/proof, HTTPS/WSS and backend request boundaries are preserved. Port 8787 must remain Private.

Permission provenance and exclusions are recorded in [ALPACA_PERMISSION_LEDGER.md](ALPACA_PERMISSION_LEDGER.md). The support correspondence was provided by the owner; no vendor account/support call independently verified it here. No unrestricted data redistribution, paid feed, options entitlement or trading permission is inferred.

## Retry and resource contracts

The shared delay helper uses a bounded equal-jitter exponential window. Random samples are injectable without changing global seeds. Invalid attempts, nonfinite samples/bounds and an impossible Retry-After floor reject explicitly. Jitter changes scheduling, not event data or mathematical outputs.

- Normal IEX stream: the existing maximum five consecutive attempts remains; delays are capped at 30 seconds. Quiet subscribed feeds remain IDLE, not a forced reconnect. Transport ping/pong still supplies liveness checks. Stop/cancellation interrupts backoff, and subscriptions are rebuilt by the existing lifecycle.
- Historical v2: still at most three attempts for HTTP 429; no new retry of authentication/entitlement/other HTTP failures and no automatic feed fallback. Delay respects Retry-After, stays within five seconds, and a larger advertised wait fails closed. Permission/interval validation is repeated before the next request. The existing 30-second operation limit remains.
- Existing history bounds remain four pages × 64 physical rows, one active query, 512KiB wire/result, 16 accepted in-memory results, logical 60-second TTL and explicit deletion. Stream bounds remain four configured symbols, 32KiB frames, queue capacity four and 256 event/identity histories.

The owner probe is narrower: one AAPL page each for bars/quotes/trades, at most 192 physical rows and nine historical HTTP attempts, then one 30-second stream without reconnect; cooperative 120-second acquisition limit. Socket cleanup uses its existing three-second close timeout afterward; no OS-enforced total process deadline is claimed. It refuses an existing/uncertain local gateway and requires an exclusive shared-account stream window. HTTP 401/403 stop subsequent admission attempts. Counts/hashes/receipts are printed, never raw records or credentials. Empty history, an unavailable interval or quiet/off-session live window cannot produce a PASS.

IEX quote/trade provenance, source/receipt timestamps, stale/out-of-order diagnostics and observation-only corrections remain. There is no L1-to-L2/L3 fabrication. Historical research uses actual accepted observations when authorized; authored native L3 replay remains separately labeled. Persistence/recovery infrastructure remains fixture-tested but is not activated by this launcher, despite the newly reported personal-storage permission.

## Final executed validation

Final counts below have **zero failed or skipped outcomes**. These are overlapping cohorts, not a claim about unique requirements. Original failed development logs remain bound in the evidence ledger.

| Executed Python cohort | Debug | Release | ASan+UBSan |
|---|---:|---:|---:|
| New final qualification |35/35|35/35|35/35|
| Sprint 4 history/research/paper boundaries |96/96|96/96|96/96|
| Sprint 3 fake paper/risk/recovery |52/52|52/52|52/52|
| SEC/source qualification |142/142|142/142|142/142|
| Stocks/live/catalog/projection/persistence |207/207|207/207|207/207|
| Terminal/native API/security/financial contracts |274/274|274/274|274/274|
| **Total** |**806/806**|**806/806**|**806/806**|

Total Python outcomes: **2,418**. The new small cohort was rerun after the final diagnostic refinement; unchanged successful broad cohorts were reused rather than repeated.

| Other executed check | Result |
|---|---|
| GCC native Debug CTest |158/158|
| GCC native Release CTest |158/158|
| GCC native ASan+UBSan CTest |159/159|
| Frozen native identities |8/8 in each native configuration; 24/24 comparisons unchanged|
| Frontend Node tests |118/118|
| Strict TypeScript / production build |PASS|
| Browser suite |13/13 programs exit 0, including new GIG 10 checks and existing financial/replay/simulation/security paths|
| Responsive workspace checks |Existing 120 routes at 360/390/768/1280/1920px; new 48 settled desktop/phone/theme journeys|
| Rendered contrast sampling |24 workspace/theme views, zero recorded failures; not full WCAG certification|
| Verified local HTTPS/WSS/proof fixtures |20 checks across three programs|
| Source packaging patterns |3/3, including negative controls|
| Actual source archive |1,123 safe intended byte-identical members; new scripts/modules/tests present|
| Runtime dependency consistency |`pip check`: no broken requirements|

Native results are actual reruns of existing unchanged-source builds, not new compilation of a modified C++ engine. No C++/binding/native-test/build-definition source changed. Python ASan uses the existing instrumented binding/launcher with live LSan checkpoint zero; `leak_check_at_exit=0` remains explicitly disclosed. Native ASan/UBSan also ran. A new Clang full native matrix was not needed for unchanged native source; the available Clang was used for the ARM object check below.

Local toolchains: x86_64, GCC 14.2.0, Python 3.12.14, Node 24.19.0, Chromium 154.0.8037.57. The final source/asset/command/log evidence is in [FINAL_QUALIFICATION_EVIDENCE.json](FINAL_QUALIFICATION_EVIDENCE.json). Logs remain in ignored `build/final-qualification/`; their hashes are committed, not a claim that hosted artifacts exist.

### Browser and geometry evidence

The 22 production asset files are byte-identical to the verified redesign assets. No geometry, native numerical or frontend implementation changed. Browser tests exercised ordinary clicks, actual native transport, book/depth, source labels, camera orbit/pause, offscreen/reduced-motion suspension, recovery and disposal, financial research and simulator controls. No rebuild ran concurrently with browser tests.

The browser source receipt's only later changes are the new qualification test module and its runner, refreshed from 34 to 35 tests. Browser-loaded frontend/backend modules were unchanged; the 35-test cohort was rerun in all three configurations. This distinction is recorded rather than claiming identical hashes for those two test files. Existing numerical geometry mapping remains byte-identical to the redesign checkpoint; no new independent market-geometry validation is claimed.

The existing large deferred Three chunk warning and Starlette TestClient deprecation remain visible. No warning, assertion or test was suppressed. Physical Android/Safari, full assistive-technology/WCAG acceptance and long-session GPU behavior remain outside this local evidence.

### Measurements

Initial entry JavaScript remains **249,055 bytes**, approximately **77.55kB gzip**; Three stays deferred. In one warmup plus three local authored-browser samples, median initial navigation plus network-idle was **849.6ms**, company route **133.5ms**, and sampled JavaScript heap **4,420,220–4,506,252 bytes**. These concurrent shared-host software-browser measurements are not a speedup, live-provider latency or physical-device performance claim.

## ARM64 scope

The host is x86_64. No AArch64 runtime/QEMU or full target C++ sysroot was available. Clang 19.1.7 cross-compiled the actual exact-arithmetic function bodies, extracted unchanged with only an `ErrorCode` enum declaration stub, using C++20, `-O1`, UBSan and strict warnings. `file` verifies an AArch64 ELF object; symbol inspection contains no `__muloti4`. Expected unresolved C++/UBSan/division runtime symbols remain because this is an object-only check.

A full `flow_metrics.cpp` cross-compilation was attempted and stopped at missing target `<span>`. That is an environment/sysroot blocker, not a passed engine build or a reproduced arithmetic defect. No native arithmetic repair was justified or made.

The existing manual `native-arm64.yml` workflow now allows `development/gig-ui-redesign`, preserving the previous two branches, six compiler/configuration jobs, owner free-usage gate, default false input, fixed ARM runner and all eight canonical identities. GCC Release additionally runs the new offline cohort with all provider/order flags zero. The exact three-branch policy regression replaces the obsolete two-branch expectation; rejection of main, unknown and pull-request refs remains strict.

No workflow was dispatched, rerun or canceled. Current-candidate native ARM64 runtime qualification remains **PENDING**, regardless of older qualified commits. No main/release workflow file was modified.

## Preserved failed-before evidence

1. The surviving five gate methods failed before implementation: six assertion/subtest failures and one error. They demonstrated the absent new gate/precedence contract. Both original broad permissions and legacy compatibility remain tested.
2. An early regression invocation selected an interpreter lacking HTTP/protocol dependencies. Qualification moved to the existing pinned runtime environment; no dependency/security guard was bypassed.
3. The first broad terminal run rejected the intentional workflow branch expansion because its exact policy still listed only two branches. Its exact allowlist/guard tests were updated to the authorized three branches; all 274 tests then passed without weakening negative cases.
4. A test intercepted `execve` using RuntimeError, which the new safe exception boundary correctly sanitized. The test now models successful nonreturning exec with a SystemExit interceptor while retaining exact command/environment assertions.
5. Packaging was first attempted in the runtime-only venv, missing build tools. The existing pinned build-tool environment ran all three packaging tests and produced the verified archive. No package download was needed.
6. The full ARM cross-compilation limitation is retained separately as pending infrastructure evidence, not hidden as a PASS.

## Qualification matrix

| Area | Classification | Evidence / remaining gate |
|---|---|---|
| UI redesign | **Verified** | Automated local browser/build evidence; owner visual/device acceptance pending |
| C++ native engine | **Verified** | Existing-source Debug/Release/sanitizer reruns and eight frozen identities |
| Read-only Alpaca integration | **Verified (offline)** | 35 new regressions plus existing cohorts; fixed destinations and independent gates |
| Live IEX provider | **Pending** | No credentials/private owner environment available; no real stream attempted |
| Historical IEX provider | **Pending** | Fixture contracts verified; actual account/range/nonempty source results not measured |
| Codespaces deployment | **Pending** | Local TLS/WSS/native checks passed; real private authentication/forwarding not accessed |
| ARM64 native runtime | **Pending** | Fragment cross-object only; full native six-job run still required |
| Security | **Verified (executed offline scope)** | Gate/origin/proof/resource/redaction checks; owner edge/runtime advisory clearance pending |
| End-to-end acceptance | **Pending** | Offline workflows pass; owner/provider/current-ARM/device gates remain |

This scope is ready for owner-operated private qualification, not a declaration that the entire project is complete or production/trading ready.

## Owner-only acceptance

Follow [PRIVATE_IEX_RUNBOOK.md](PRIVATE_IEX_RUNBOOK.md) for short update, build, check, standalone probe, restart and exact-SHA receipt commands. Do not repeat key/contact setup when it is already configured. Keep the Codespace/port private; use the existing authenticated HTTPS address.

The two central commands, after updating/building and stopping the old gateway, are:

```bash
.venv/bin/python scripts/private_iex.py --qualify --confirm-private-single-user --exclusive-stream-window
```

Then:

```bash
.venv/bin/python scripts/private_iex.py --start --confirm-private-single-user
```

A provider probe is not private-edge authentication proof. Owner review must verify actual source/freshness labels, HTTPS controls and WSS reconnect across the agreed workspaces, and preserve observed-data privacy. Native ARM64 requires a separately owner-approved free-eligible manual run on the delivered SHA. Neither action was delegated to this task or fabricated here.

## Changed files

Application checkpoint:

- `.github/workflows/native-arm64.yml`
- `scripts/private_iex.py`
- `terminal/stocks/live.py`, `historical_v2.py`, `qualification.py`, `private_iex.py`, `retry.py`, `test_final_qualification.py`
- `terminal/tests/run_final_qualification.py`
- `terminal/test_arm64_terminal_policy.py`
- `docs/user-guide/GETTING_STARTED.md`
- `docs/qualification/ALPACA_PERMISSION_LEDGER.md`, `PRIVATE_IEX_RUNBOOK.md`, `PROGRESS.md`

Evidence closure adds this report and `FINAL_QUALIFICATION_EVIDENCE.json`, and updates the progress checkpoint. No frontend, C++, binding, execution implementation, credentials, dataset bytes or saved deployment/provider configuration changed.
