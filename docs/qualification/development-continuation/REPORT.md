# GIG product-session recovery and XBRL continuation — November 12, 2026

The user-verified starting checkpoint was `6026368c74fe72ceeca8e529b8c0e7b84bad6dfb` on `development/gig-ui-redesign`. The recovered workspace preserved newer pushed implementation milestones and an uncommitted replay-worker repair. The final tested runtime is **`03078f65b2d7907fd78a52bf7f25d9c8d2c74a0c`**. The enclosing documentation commit is intentionally identified by Git/remote receipt rather than self-embedded here. No reset, merge, branch replacement, force push or protected-branch modification was used.

## Published implementation

|Commit|Change|
|---|---|
|`0014a19afe69679ed8eb23dc1b3a5e87e5b576be`|Preserve XBRL segment/scenario context placement and reject ambiguous containers/mixed typed text.|
|`4bff719ea6c527c1324689d521f36d21f6d09afb`|Full typed ITCH product selection/restoration, private immutable bundles, migration, paused replay and both-book controls.|
|`a3640d7fb59572c5179dfc49de1879f2d537763a`|Exact source-unit projection, three-unit price/ten-share lot fixture and real native-to-TypeScript contracts.|
|`f5c3f40375ff5dbaf6d123d29c981a127ad635b0`|Atomic supplied-DTS declaration binding into filing-vintage research and exports.|
|`2eb38f4312f4afb3de266648b746d16873e4f0f3`|Preserve verified clean `a3640d7` source/wheel packaging evidence; documentation only.|
|`03078f65b2d7907fd78a52bf7f25d9c8d2c74a0c`|Prevent a classified ITCH source rejection from terminating the actual background replay worker.|

## Full ITCH product-session engineering

The real `NativeSession` and server-owned selector now support explicit opt-in restoration of the complete typed artifact alongside the unchanged default authored-native workflow. Selection requires a private path and independently retained bundle digest; unknown/incomplete configurations fail closed. Browser requests cannot choose filesystem paths or confer source authority. Restoration skips default startup replay, retains both independent native books/context/source state and starts paused. Source capture/generation/configuration, order and match state, receipts and replay cursors remain native-owned.

The immutable version-1 bundle bounds image/continuation/migration sizes, validates the complete supplied suffix in an isolated candidate, and publishes by exclusive, synchronized private-file admission. Rejected candidates leave the accepted owner unchanged. Hot steps apply only new events. Capture records the current accepted boundary and remaining suffix. Source-minimum seek bounds prevent pretending that missing committed history is available.

Migration is explicit: trusted old version-1 bytes are admitted against current invariants, re-encoded under the current code/binary identity and checked again for canonical/source consistency. Unknown schemas, arbitrary historical algorithm equivalence and unsupported positions are rejected. No automatic migration, observed dataset, provider connection or live-depth initialization is inferred.

Replay reaches terminal/end-of-input or resource rejection in a paused state. Speed changes cannot revive it. The final new regression extracted the actual nested worker coroutine without constructing the application. Before repair, a refused native frame surfaced `ItchProductError: itch_product_source_rejected` and exited that worker because it caught only `EngineError`. After repair, `NativeSession.tick()` pauses both control states, retains accepted books, emits a bounded notification and keeps the worker alive for later explicit recovery. The test verifies subsequent explicit resume.

The actual product state projects native ticks/lots into original source Price(4)/shares using exact native-admitted rational units. The authored quantum-3/lot-10 fixture verifies native bid33/quantity10 maps to source price99/shares100; ask34/lots5 maps to102/shares50. Spread is3 and midpoint is201/2 source units. Native state/calculations are unchanged. The Replay UI can select both restored books, shows the real continuation range and disables exhausted controls. UI work preserves existing workspaces, source labels and security gates.

See [ITCH_PRODUCT_SESSION.md](ITCH_PRODUCT_SESSION.md) for bounds, private selection and offline inspect/migrate tooling.

## XBRL work

Context semantic identity now preserves segment versus scenario placement. Duplicate containers and unmodeled mixed typed-member text reject explicitly. Affected derived context/fact/output hashes intentionally change under `DIM_CONTEXT_ELEMENT_V2`; raw source digests, financial numerical contracts and the eight native frozen identities do not.

`FilingCollection.ingest_dts_batch` adds an explicit supplied-only contract. Existing source/permission admission and total-byte preflight run before parsing. Selected facts join declarations by exact source hash, origin and expanded QName. Missing selected declarations, period contradictions, abstract facts and nil-not-nillable contradictions reject the entire candidate batch. Original collection state survives a bad later entry. Existing plain ingestion remains compatible.

Acceptance-time exports retain document/source hashes, declaration/type metadata, unsupported features, original receipts and fact IDs. Custom types are not relabeled validated. `schema_type_validation` and `complete_statements` remain false. No missing financial history, taxonomy or receipt timestamp was manufactured. See [XBRL_CONTEXT_PLACEMENT.md](XBRL_CONTEXT_PLACEMENT.md) and [XBRL_DTS_BINDING.md](XBRL_DTS_BINDING.md).

## Executed developer validation

|Profile/check|Actual results|
|---|---|
|GCC14.2 Debug / Release / ASan+UBSan native CTest|152 /152 /153 passed|
|Clang19.1.7 Debug / Release / ASan+UBSan native CTest|152 /152 /148 passed|
|Fresh frozen-reference reruns|8/8 matched in each of six profiles;48 outcomes|
|Final guarded Python cohort, CPython3.12.14|301 passed in each GCC Debug, Release, sanitizer and Clang Debug, Release binding profile;1,505 outcomes;0failures/errors/skips|
|Focused real-native product session|18 cases, included in the301; final worker failure reproduced before repair|
|Affected authored XBRL|59 cases, included in the301;also rerun from the clean extracted source|
|Frontend Node24.19 tests|160 passed;0failures/skips|
|TypeScript/Vite8.3.5 production build|Passed|
|Real native → actual TypeScript admission|28 assertions /4 authored states passed;no application/browser construction|
|Clean-source/installed SDK|8 SDK +55 recovery +59 XBRL cases, plus28 contract assertions passed|
|Runtime dependency consistency|`pip check`: no broken requirements;not an advisory/security clearance|

The full native matrix ran before the last binding-descriptor/unit-fixture refinement. Focused rebuild/checks then passed (6/6/7 GCC,6/6 Clang;Clang native sanitizer durable test passed) and **all eight identities were freshly rerun after that refinement**. Native `src`, `include` and core build inputs are unchanged from the starting checkpoint; the final worker repair is Python-only and received the final301-per-profile run. These overlapping checks are not summed into a fictitious unique-test count.

The native durable/source tests retain the previous full363/163 assertions and57 restore,63 encode and67 source-restore allocation-failure points. Product tests additionally cover resource refusal, immutable file failure, abrupt subprocess restart, explicit migration, state isolation and rejected-tail admission. No memory-safety failures were observed in the executed sanitizer profiles. The existing GNU Python harness disables exit leak checking and has separate live-interpreter coverage; this is not full CPython-shutdown leak clearance. Clang Python sanitizer execution is unsupported by the existing harness and is not claimed.

All source/log digests, exact profile outcomes and original failure receipts are bound in [PRODUCT_SESSION_EVIDENCE.json](PRODUCT_SESSION_EVIDENCE.json). Prior receipts are retained in Git and `DURABLE_ITCH_EVIDENCE.json`. Intermediate failures remain failures in their original receipts. The earlier no-launch harness imported an eager ASGI module before replacing its factory: it created an application object, although no listener/server ran. Current lazy export plus assertions enforce the stronger **no application construction** boundary in every final cohort. Earlier evidence is not retroactively relabeled.

## Packaging and measured observations

The new clean source archive is bound to runtime `03078f6`:1,259 archive members;1,258 tracked file contents compared byte-for-byte to Git;22 changed runtime/test files explicitly checked. Paths, member types, duplicates, private-data/database/archive/cache/build payloads were rejected by the inspection. Only generated `PKG-INFO` is outside tracked source. Tests above used this extracted source, not a checkout accidentally masking omissions.

The installed22-member SDK wheel was built from the previously qualified clean `a3640d7` archive. All SDK/native/build inputs are byte-identical between that source and `03078f6`; the wheel was deliberately reused. It was **not rebuilt from the new server-source archive**. `PACKAGE_CURRENT.json` records both source identities and receipts explicitly. This is a private developer artifact, not a release/publication.

The initial frontend JavaScript is255.88kB (79.46kB gzip); deferred OrbitControls chunk517.06kB (128.66kB gzip). The optional chunk warning remains visible. These are build sizes, not browser responsiveness measurements. Final301-case elapsed wall times were21.930s GCCDebug,18.317s GCCRelease,129.898s GCCsanitizer,21.516s ClangDebug and16.156s ClangRelease;two independent profile processes ran concurrently. No throughput, exchange latency, production SLA or new memory benchmark is inferred from test durations.

## Scope, remaining engineering and blockers

The matrix remains **50 rows =49 reviewed areas +one historical A18/A19 decision**. The formerly48-area matrix gained the explicitly requested Kraken `MD07` area; the historical decision is not another new implementation. Counts remain **34 COMPLETE /8 PARTIAL /7 BLOCKED /1 NOT APPLICABLE**. The REL02 and SEC02 evidence is substantially expanded; neither broad requirement is falsely closed by a bounded profile.

Remaining engineering includes full XML Schema/custom types, authoritative inline transformation/continuation support, dimension/DRS and relationship precedence, calculation/statement mapping and read-only v2 integration. Existing partial profiles remain usable and explicit. Full supported-source tape correction/losslessness requires authoritative source semantics and continuity evidence; unsupported actions still fail closed. Unknown checkpoint-schema/source-position migrations remain unsupported rather than guessed.

The one bounded official Kraken documentation request returned proxy CONNECT403. No retry or feed connection occurred. Existing deterministic checksum/integrity fixtures passed, but **Kraken remains provisional**. Verification needs an accessible authoritative message/decimal/checksum specification before expanding claims. Do not repeat policy-blocked operations.

Other open dependencies are complete lawful observed L3 initialization/reference evidence; current permitted listing/provider/SEC source reconciliation; exact-candidate ARM64 runtime; owner-authenticated private Codespaces HTTPS/WSS; physical GPU/mobile/assistive-technology acceptance; target OS/artifact security and hardware/power-loss durability. Historical A18/A19 still requires the original requirement or an explicitly prospective owner decision. No new credentials or intermediate owner tests are requested here.

Product-session publication/validation is complete for its stated authored profile. **Full approved development remains incomplete**, chiefly broader XBRL semantics and supported-source/target contracts. The next bounded XBRL profile is a multi-day engineering package; comprehensive XBRL fidelity is a separate multi-week effort requiring explicit supported-specification coverage, not a reliable overnight estimate. External qualification dates cannot be estimated from these fixtures.

## Reproduction and continuation

Developer-only commands use an already built intended binding profile on `PYTHONPATH`, plus the matching authored fixture executable in `GIG_ITCH_FIXTURE`:

```bash
<venv>/bin/python tests/test_itch_product_python.py
<venv>/bin/python terminal/tests/run_no_launch_suite.py
<venv>/bin/python terminal/tests/check_itch_product_contract.py
```

The second command asserts301 selected cases and forbids socket binds/connects and the application factory. GNU sanitizer runs need the existing ASan runtime preload and harness options recorded in the evidence. Native developer commands remain `cmake --build <profile> -j2` and `ctest --test-dir <profile> --output-on-failure`;frontend developer commands remain `npm test` and `npm run build`. These are not launcher/deployment/acceptance instructions.

Exact next implementation: add the next bounded authoritative XBRL type/transform profile with independent fixtures, then integrate supported statement/vintage outputs with existing v2 contracts. Preserve the version1 private product workflow; do not reimplement the typed codec or reopen validated unit math. Keep Kraken provisional until its actual contract is verifiable. Do not launch GIG, ASGI factories, servers, providers, workflows, trading or owner acceptance under this directive.
