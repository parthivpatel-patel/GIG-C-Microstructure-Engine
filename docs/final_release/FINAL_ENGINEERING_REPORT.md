# GIG ATLAS: final engineering and operational readiness

**Latest SEC follow-up, October29,2026 America/New_York:** Owner diagnostics identify
an unrelated terminal-marker reference rejected by local syntax. The bounded
[version3 reference-policy repair](../milestones/SEC_TERMINAL_REFERENCE_REPAIR.md)
reproduces and fixes that shape while preserving exact AAPL routing and directory
conflict checks. Actual SEC source qualification remains unverified in this executor.
Earlier findings and evidence below are retained as historical checkpoints.

**SEC follow-up, 2026-10-30 UTC:** The owner confirms that release `5b5eb36` still
rejects the actual directory with `sec_directory_symbol`. The earlier routing repair
did not resolve that source condition. See [the remaining rejection investigation](../milestones/SEC_DIRECTORY_REJECTION_ISOLATION.md).
Exact guard/record diagnostics are now fixture-verified; actual SEC qualification
and the specific live rejected value remain unverified. Historical evidence below is
preserved and does not establish resolution of this blocker.

October29,2026,America/New_York. Baseline `73d6725898f54ad97ff926e674e93f137c3d1fd7`.
Validated implementation,committed,pushed and remotely verified:
`f1516d03c66ee97850e1b4a7a0add9e90e9a607b` on `feat/atlas-final-release`.
The evidence/report-only delivery commit follows this checkpoint. Main remains
`12f3a53943dc245e36f2cbbc35b9910fb21c0718`. No merge,tag,release or workflow dispatch.

## Decision

**Milestone1 — ENGINEERING COMPLETE for the declared bounded private research scope.**
Source/normalization,application workflows,all12 workspaces and13 modes,security,
packaging and final local automated gates have been inspected and verified below.
No confirmed unresolved critical/high code defect remains from this campaign. This
is a self-reviewed engineering assessment with independent reference calculations,
not a separate external certification or proof that all possible defects are absent.

**Milestone2 — NOT VERIFIED / BLOCKED BY EXTERNAL REQUIREMENTS.** No real Alpaca
IEX quote/trade or SEC source was acquired here. Owner reports existing Codespaces
credentials and ready SEC configuration;this executor has no corresponding secret
bindings,permitted SEC/Alpaca egress or authenticated Codespaces access. No forbidden
access was retried. Applicable Alpaca cloud/private-display evidence remains
unavailable;ticket381230 resolution is not invented. Physical devices,current-candidate
ARM64/hosted qualification and final owner acceptance remain open.

The complete [requirement matrix](REQUIREMENT_MATRIX.md) maps every master-directive
phase,all12 actual workspaces,and all13 visualization modes to code/evidence and source
limits. The [one final acceptance session](FINAL_OWNER_ACCEPTANCE.md) reuses existing
configuration;it does not request another account,keys or SEC contact setup.

## Reproduced defects and repairs

### SEC reference admission versus market routing

Owner-reported live symptom: `identity_resolution / SOURCE_SCHEMA /
sec_directory_symbol`. Actual rejected symbol/response is unavailable in this Cloud
executor. The old parser applied the application's narrow market-routing grammar to
every reference entry,so one otherwise safe but unrepresentable reference prevented
publication of all mappings,including AAPL. An authored four-row witness reproduced
that all-or-nothing failure before repair.

`sec_identity.parse_reference` now validates the entire bounded reference structure,
CIKs,names and exact duplicate symbols. Safe reference text outside the unchanged
routing grammar is explicitly excluded,never normalized or routed. Accepted+excluded
equals input;first16 exclusions have only source keys/hashes and fixed reasons.
Invalid types,paths,controls,structure,CIKs,duplicates and cached identity conflicts
still reject atomically. Zero usable mappings cannot claim successful discovery.
The legacy `parse` all-rows contract still rejects any exclusions;old callers cannot
silently lose entries. Share-class punctuation/case is never substituted to invent
aliases or CIKs. The source remains SEC registrants,not complete exchange listings.

Production discovery uses the explicit subset contract,and the actual UI validates
and displays source/accepted/excluded counts. Automatic startup/cache/refresh keeps
existing permissions,receipt hashes,TTL,rate limits and accepted-state protection.
The consolidated qualifier now preserves fixed safe SEC codes and failed stages
instead of replacing them with another generic message.

**Resolution boundary:** the routing/reference fragility is repaired and independently
fixture-verified. The exact live response and successful real SEC requalification are
still UNVERIFIED. No current official symbol grammar,actual excluded symbol or live
AAPL/APLD/CRWV CIK is invented. Unknown/malformed source forms can still reject
explicitly rather than being accepted merely to turn a result green.

### Per-event provenance exceeded the browser budget

Adding bounded reference diagnostic examples revealed a new integration failure:
copying them into all256 retained quotes caused `MARKET_SNAPSHOT_BUDGET` under the
existing1MiB limit. The failing browser-frame regression is retained. Per-event source
metadata now retains identity,digest,coverage and counts;full exclusion diagnostics
remain once in directory status. No limit was increased and no provenance identity
was lost. A four-symbol,256-event authored snapshot now measures469693 bytes.

### Finite Level1 chart calculations

Two independent numeric regressions reproduced NaN comparison points from subnormal
positive midquotes and infinite rolling variation from an overflowing price ratio.
The stable midpoint is `bid+(ask-bid)/2`;log changes use differences of logarithms.
Unrepresentable display changes are omitted with an explicit disclosure,not clamped
or reported as observed zero. Original source values and exact backend rational
metrics remain available. This is binary64 geometry,not a new financial calculation
or an empirically observed market defect. All77 frontend tests pass.

### MessagePack error-path memory leak

Official PyPI metadata reported three advisory records covering two issues in the
old msgpack1.1.2 pin: CVE-2026-57585 / GHSA-6v7p-g79w-8964 and
CVE-2026-114613 / GHSA-j586-36cw-2gc2. The latter was reproduced through the actual
production `unpack` function with independently authored MessagePack bytes:256 rejected
16006-byte frames retained4137216 bytes. Bounds on individual frames do not prevent
cumulative leakage. No real provider attack or streaming-Unpacker misuse is claimed.

The existing dependency is pinned/upgraded to Apache-2.0 msgpack1.2.3. Runtime checks
reject older versions before decoding or upstream admission;startup gives a precise
dependency-update instruction without changing configuration. Positive allocation
controls prove the regression's memory tracker is active. The same malformed-input
experiment now retains0 bytes,and all affected Debug/Release/sanitizer and browser
tests passed again. No warning/assertion/sanitizer finding was suppressed.

Official per-version PyPI metadata now lists0 advisories for all17 direct pinned server
requirements;NPM audit reports0 across its dependency tree. This is a dated advisory
snapshot,not a complete transitive/OS/native security certification. No new runtime
dependency or paid service was added. Owner update must install the existing revised
requirements once;this is a security patch,not another credential/SEC setup.

## Actual source status

| Source | Implemented capabilities | Actual qualification in this executor |
|---|---|---|
| Alpaca IEX live | Fixed WSS authentication/ACKs,quote/trade/bar/correction observations,in-place subscription lifecycle,shared connection,limits,ordering/dedup,bounded history,quiet-feed health,backoff,cancellation,browser push/recovery | NO OBSERVED DATA;permissions/credentials/egress unavailable;account-wide available slot cannot be inferred |
| Alpaca historical | Daily/hour/minute profiles,exact timestamps and source receipts,raw adjustment,pagination,partial/empty states,independent same-source-time comparisons | NOT EXECUTED AGAINST PROVIDER;no consolidated/NBBO/full-history claim |
| Alpaca assets | Read-only paper assets active/inactive us_equity,UUID/exact identities,exclusions,search/cache/refresh | Actual provider imported count and target searchable count UNKNOWN;Cloud fallback identities are not imported securities |
| SEC | Authoritative mapping interface,selected companyfacts/filings,units/periods/restatements,acceptance safeguards and independent reconciliation | Owner readiness and source rejection are reported;actual successful retrieval/reconciliation remains UNVERIFIED |
| Other free sources | Existing official Nasdaq directory importer and source-access ledger reviewed;rights stay gated | No new listing,NYSE/Cboe/economic source body acquired;no material justified integration with established current rights/access |

No account/order/position endpoint,trading,SIP/OPRA feed,new subscription or observed
retention was enabled. Source access never grants legal display/cloud/storage rights.
No LOBSTER or additional Nasdaq historical data was inspected/downloaded.

## Executed final validation

All final cohorts had zero failures,errors and skips. Counts are outcomes per cohort
and configuration,not a unique-test total or product-coverage percentage.

| Gate | Actual final outcome |
|---|---:|
| Native GCC Debug / Release / ASan+UBSan,Python+streaming enabled |158 /158 /159 CTest PASS |
| Native Clang Debug / Release / ASan+UBSan,streaming enabled |155 /155 /155 CTest PASS |
| Eight frozen identities | Identical across all6 complete native configurations |
| Native-backed terminal Python Debug / Release / ASan+UBSan |274 /274 /274 PASS |
| Stock/SEC/provider Python Debug / Release / ASan+UBSan |207 /207 /207 PASS |
| Source qualification Python Debug / Release / ASan+UBSan |94 /94 /94 PASS |
| Frontend contracts/numerical units + strict TS/Vite |77 PASS;build PASS |
| Final browser campaign on msgpack1.2.3 |357 checks across23 functional cohorts +1 performance cohort |
| Explicit workspace/theme/width matrix |120 checks within the browser total |
| Emulated mobile touch |3 nonempty renderer-family cases within the browser total |
| Security/manual-workflow policy |52 PASS |
| Actual local verified HTTPS/WSS proxy |8 PASS |
| Actual startup,occupied-port protection,shutdown |3 PASS |
| Existing installed native wheel0.1.1 consumers/exports |14 PASS |
| Source packaging pattern regressions |3 PASS |
| Clean implementation sdist |852 intended byte-identical source members;two archives exactly identical |
| Dependency metadata | NPM0 known advisories;official PyPI0 for17 direct pins |

GCC14.2.0,Clang19.1.7,CPython3.12.14,Chromium154.0.8037.57 on x86_64 were used.
GCC's Python-enabled configurations include three binding cases and an additional
sanitizer control. Existing cached core-only GCC builds initially passed133 each with
streaming OFF;these are preserved supplemental results,not substituted for the complete
158/158/159 qualification. No CMake gate,test inventory or frozen value was weakened.

Sanitizer consumers reported LIVE_LSAN_CHECK=0. These are instrumented native bindings
with live-interpreter leak checkpoints and the installed MessagePack wheel;they do not
certify stock CPython shutdown or fully instrument every third-party binary. Native
C++/binding code and expectations did not change. The full native engine matrix was
not unnecessarily repeated after the terminal-only dependency patch;all affected
Python and browser cohorts were rerun. Existing Starlette/httpx deprecation and large
optional Three chunk warnings remain visible.

The final browser campaign uses one stable production build,ordinary clicks/taps and
asset hashes. A preliminary browser pass was superseded after the numeric repair;
the strengthened touch cohort waits for actual authored input instead of accepting
an empty chart. Earlier campaign/log/screenshot evidence is preserved. No forced click
was introduced to conceal inaccessible controls.

## Performance and visual evidence

The initial entry asset remains236210 bytes with Three.js deferred;exact gzip/chunk
sizes,three browser repetitions,source fixture identity,source timing/heap/RSS and
limitations are in `evidence.json`. Browser timings are loopback navigation including
settling,not exchange latency or Android performance guarantees.

The indexed50000-entry authored registry is4681674 bytes,with45000 independently
expected accepted mappings and5000 exclusions. One warmup/three measured parser runs
achieved approximately243k–260k source entries/second. A separate decode+parse tracing
pass peaked at36396501 tracked bytes;whole-process peak RSS was137420KiB,including
input,warmup and instrumentation. These are synthetic process measurements,not a
certified worst-case service-memory bound. No RNG seed is invented for indexed data.

The final campaign captured99 screenshots with individual hashes. Representative
review includes SEC exclusion accounting,ready financial trends,mobile quote/research
camera scenes,and declared GARCH rendering. Screenshots are authored fixtures/models,
not observed company/market data. They remain in ignored local artifacts rather than
being published as provider data. The manifest lists exact paths and review scope.

## Packaging and delivery integrity

Clean detached source worktree at f1516d0,with fixed SOURCE_DATE_EPOCH,produced two
identical2705295-byte archives,each SHA256
`773ca360bf89201e5eeeed019528968362b585ae5ff168735ad173717ec6bc0c`.
Inventory checks verified852 intended source members against the checkout. No raw
market rows,private data,ZIP,keys,contacts,build artifacts or compiled binaries were
staged. This archive is the implementation snapshot;the final report-only commit is
separate. Exact changed-file inventory,commands,receipt hashes and commit IDs are in
`evidence.json`;detailed ignored logs are under `build/final-master/`.

## Remaining gates and final owner action

1. Applicable Alpaca private-cloud/display/free-plan evidence and an available shared
   account streaming window. Existing credentials are not requested again;disabled
   gates are not bypassed. No legal prohibition is inferred from missing records.
2. Actual SEC and authorized Alpaca catalog/history/IEX source results in the existing
   Codespace. Ready SEC configuration is not asked to be recreated. The exact live
   offending symbol is still unknown;safe unsupported reference forms are accounted
   rather than globally blocking discovery.
3. Actual private GitHub authentication/forwarding,HTTPS/WSS,source-backed UI and
   desktop/Android behavior. Local TLS fixtures and emulated touch cannot close this.
4. A separately authorized eligible/free ARM64/hosted run on the actual candidate.
   The manual workflow is prepared and includes the94-case fixture cohort;no run was
   launched. Older qualified SHAs do not qualify the new Python/TS changes.
5. Final owner acceptance of the exact candidate and its limitations.

Use [ONE consolidated session](FINAL_OWNER_ACCEPTANCE.md) later when convenient.
It updates the existing dependency,executes bounded probes once,starts privately
with observed retention off,and provides sequential PASS/BLOCKED/INCONCLUSIVE criteria.
No intermediate owner testing,output copying or screenshots were requested here.

**Release decision: ENGINEERING COMPLETE;operational qualification OPEN/BLOCKED BY
EXTERNAL REQUIREMENTS;NOT production-ready or release-authorized.** Full US master
coverage,complete XBRL/PIT history,lossless corrected tapes,live L2/L3,hot live recovery,
trading,formal accessibility certification and empirical forecasting efficacy are not
silently claimed or added as speculative scope. No further speculative feature was
built to disguise the external source/target/acceptance boundary.
