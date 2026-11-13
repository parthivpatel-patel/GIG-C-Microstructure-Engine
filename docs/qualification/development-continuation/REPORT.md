# GIG multi-workstream engineering checkpoint

November 13,2026 (America/New_York). Branch `development/gig-ui-redesign`.
Starting checkpoint `ff0fcdcda7bb65a1669501fa5fe4f653a3ecb33d`.
Final tested implementation: **7931641397878cb660f00c847cc5e38f175debc0**.
The enclosing documentation-only delivery commit is identified by Git/remote;
it does not change tested runtime inputs. Prior report/evidence remains available
at the starting Git object and ACCURACY_EXTENSION_EVIDENCE.json.

Recovery found the first three implementation commits already pushed,plus two
untracked CLI files and a temporary dependency symlink. The interrupted CLI log
contained5/5passing tests. All surviving work was preserved;no branch recreation,
reset,discard,merge,force-push or protected-branch change was used.

## Published implementation packages

|SHA|Working implementation|
|---|---|
|44e0eeecc348c2dd6113564a483a723bdd697a8f|Explicit schema-appinfo embedded presentation/calculation/definition linkbases with original source-node provenance.|
|52fd5eddc210536c98c528d375006fcc12404e32|Default-disabled SEC XML filing/DTS transaction,read-only bounded wire,private immutable revisions,reparse/restart and workspace installation.|
|45588bd2ab534ace9dc9d97def5c10adf212058a|Duplicate accuracy ambiguity,source-ingestion status and actual Python→TypeScript product integration.|
|5e5d34f513cb9a9dd61764e8ec332e042f6384bc|Preserved explicit offline qualification CLI,independent source-processing/retention gates and CLI regressions.|
|7931641397878cb660f00c847cc5e38f175debc0|Reproduced concurrent restore and late CLI validation failures;minimal admission repairs and four regressions.|

All implementation SHAs are ancestors of the verified remote branch. Exact
changed-file hashes,commands/results,log and artifact receipts are in
MULTI_WORKSTREAM_EVIDENCE.json and PACKAGE_CURRENT.json. Runtime changes cover
27files;three package design documents describe their supported contracts.

## Embedded relationships and source-grounded mapping

SCHEMA_APPINFO_LINKBASE_V1 explicitly processes supported linkbase containers
inside schema/annotation/appinfo. Locators use the actual containing schema URI.
Source SHA,root/link/arc node ordinals distinguish multiple containers in one
source. Existing effective priority/prohibition and supported restricted explicit
DRS processing are reused. No fabricated URI or replacement source document is
created. Legacy profiles still classify embedded scope as unsupported rather than
silently using partial graphs. Invalid placement,unknown root attributes/resources,
xml:base and unsupported semantics remain rejected/unavailable.

13new tests include multiple roots,cross-root priority/prohibition,legacy refusal,
relative locators,restricted closed-cube behavior,atomic rollback and private export.
The existing source-scoped extension mapping retains namespaces,declarations,
roles,source order,periods,contexts,units and filing lineage. No name-similarity or
presentation-neighbor heuristic creates a GAAP alias or accounting equivalence.

## SEC acquisition,product integration and source recovery

FilingIngestor has no default transport or startup activation. Explicit permission,
valid identifying User-Agent,CIK,accession,processing scope and advertised file
binding precede admission. The supported transaction reads current submissions,
exact filing directory,plain XML instance and bounded DTS closure. Same-filing
resources must be advertised with exact sizes. External taxonomy resources require
an exact fixed-official-host allowlist. Redirects,unapproved hosts,cross-accession
references,encoded/path traversal and ambiguous namespaces reject.

Limits are2MiB/source,8MiB transaction/retained bodies,32source records,8filings,
16DTS documents,24request attempts and30seconds pertransaction. Reads are bounded
to64KiB with8second limits,1.01second request spacing and at most one bounded
retry. Transport prefetch is separately capped64KiB;application body ceilings do
not establish a global process-RAM or wire-byte SLA. Cache TTL600seconds preserves
original receipt timestamps. Filing acceptance is independent of source receipt.
Failed/canceled/unsupported transactions do not publish candidate collection state.

Private source revision storage requires separate enabled+retention approval.
Existing owner-private0700directories and0600regular files are required;symlinks
reject.16revision/64MiB quotas include orphan temporary files. Existing immutable
native/source publication is reused (file fsync,exclusive publication,directory
fsync);no C++ journal redesign. Revisions are never overwritten/pruned implicitly.
Schema1/source/body/metadata/collection identities are revalidated before restoration.
Unknown versions reject;restore reparses original sources and stays PAUSED_RESTORED
without network. Independent child-process restore,disk/allocation failures,
corruption,publication uncertainty,cancellation and idempotency are tested.

The workspace factory shares its source-rate lock,requires known CIKs and refuses
replacement registration. Explicit installation admits the issuer-bound collection.
Company-v2/Stock Intelligence can display sanitized source state,counters and whether
the installed view matches that collection. This is observation/export-cache status,
not a live feed or complete historical source-accounting claim. There is no new
HTTP acquisition/mutation route. Existing v1/v2 defaults and SDK remain compatible.

The CLI requires either --fixture or --fetch. Fixture mode reads no owner config.
Future owner --fetch requires existing SEC identification plus separate explicit
processing gates;raw checkpoint persistence needs an independent retention gate.
No permission is enabled or written. Failures never substitute fixtures. Only
fixture mode and blocked negative fetch tests were executed in this sprint.

## Duplicate accuracy and explicit non-selection

DUPLICATE_ACCURACY_DIAGNOSTICS_V1 distinguishes equal values,overlapping-accuracy
ambiguity,disjoint intervals,nil/mixed nil and unsupported accuracy. It preserves
all source IDs,original values and exact rational enclosures. Differing reported
values remain CONFLICT even when their accuracy enclosures overlap. No value is
selected or manufactured;missing/nil never becomes zero. V2 rows/UI provide
progressive diagnostic disclosure;the default v1 result stays compatible.
Six new math/product regressions and actual cross-language contract tests cover
these outcomes. This is a conservative bounded accuracy profile,not complete
XBRL Calculations1.1 conformance or proof of accounting correctness.

## Reproduced defects and retained failures

1. A suspended authored source read showed restore replacing state while ingestion
held the shared source lock. Restore now rejects sec_ingest_busy before parsing or
replacement. Tests preserve LOADING/accepted bytes,cover another shared-lock owner,
and verify normal restore after cancellation/release. The API is event-loop-owned;
arbitrary-thread coordination is not claimed.
2. A malformed CLI cutoff reached coordinator construction. Cutoff and symbol now
validate before configuration lookup/source setup;negative tests prohibit both.
3. An intermediate diagnostic-order test exposed resource-change errors being
masked by a later filing comparison;the specific source check now runs first.
4. A negative permissions fixture assumed mkdir(0755) defeated inherited umask077.
It now explicitly chmods the deliberately public test directory. The required
rejection assertion was preserved.

Failing-before and passing-after receipts remain in the evidence manifest. No
numeric assertion,compiler warning,security boundary or test was weakened.

## Final developer validation

|Configuration/cohort|Actual result|
|---|---|
|GCC Debug bindings,guarded no-launch subset|514passed;0failure/error/skip;26.681s|
|GCC Release bindings,same subset|514passed;0failure/error/skip;27.757s|
|GCC ASan+UBSan/native Python,same subset|514passed;0failure/error/skip;150.045s|
|Clang Debug bindings,same subset|514passed;0failure/error/skip;30.764s|
|Clang Release bindings,same subset|514passed;0failure/error/skip;20.065s|
|Native GCC Debug/Release/ASan+UBSan recovery|6/6/6passed|
|Native Clang Debug/Release/ASan+UBSan recovery|6/6/5passed|
|Eight native frozen references,each of6compiler profiles|48passed;all8hashes unchanged|
|Frontend unit tests|186passed;0failed/skipped|
|TypeScript and Vite production build|Passed;no server started|
|Actual v2Python→TypeScript product contract|11cases,65assertions passed|
|Existing v1Python→TypeScript product contract|8cases,58assertions passed|
|Default installed SDK from clean source|8consumer+55recovery+261XML/source tests passed;28native frontend assertions,58v1+65v2assertions|
|Source-enabled installed SDK from clean source|8consumer+66recovery+261XML/source tests passed;35native frontend assertions,58v1+65v2assertions|
|Offline CLI fixture|OFFLINE_FIXTURE_PASS;1filing,5authored requests,4,051bytes;no provider|
|Offline dependency consistency|pip check:no broken requirements;not vulnerability clearance|

Final Python total2,570outcomes.57new tests are13embedded,23ingestion,8store,
6duplicate and7CLI. Their XBRL/source cohort totals261. Counts across configurations
are repeat outcomes,not distinct test implementations. Native focused/frozen checks
ran at5e5d34f;final native/core/SDK/build inputs are byte-identical. The final two
repairs were Python-only and their full selected cohort reran at7931641. Earlier
510-case/profile results at5e5d34f remain intermediate evidence,not final totals.

GCC14.2,Clang19.1.7,CPython3.12.14,Node24.19.0,Vite8.3.5,x86_64Linux. Existing
incremental CMake native/binding builds were checked;this is not a fresh full
unrelated CTest matrix. Native GCC/Clang sanitizers ran. GNU Python/native uses the
existing GNU ASan/libstdc++ preload with CPython interpreter-exit leak checking
excluded. Pure Python is not sanitizer-instrumented;complete CPython shutdown leak
clearance and Clang Python sanitizer integration are not claimed.

Retained warnings:Starlette/httpx TestClient import deprecation (no client launched),
asyncio slow-task diagnostics under instrumentation,pip cache permissions and the
existing optional Three/OrbitControls517.06kB chunk warning. Initial JS256.34kB,
gzip79.63kB;no browser runtime responsiveness or speed improvement is inferred.

## Packaging and artifact origins

A new sdist was built from clean Git archive7931641:1,315members,1,314tracked files
byte-compared to that commit. All changed runtime files were present;no build tree,
node_modules,symlink,private dataset,ZIP,database,credential file or compiled binary
was admitted. Extraction used data-only safe archive rules. Final report-only
updates are newer than this runtime archive and are not represented as packaged.

Default/source SDK wheels are **reused**,not newly built from this sdist:verified
source7aea334f0171b862b055f9b3ebda46a78894dc7a. Native/SDK/build inputs are byte-identical
to the final runtime,installed source files were compared,and wheel hashes/member
counts/original build logs are in PACKAGE_CURRENT.json. Both were installed offline
without dependencies into isolated targets and exercised with this extracted source.
The actual default binary rejects unavailable optional source-streaming capability;
there is no patched substitute. No dependency addition/upgrade occurred.

## Measured authored-source envelope

A reproducible in-process fixture loop used one warm-up plus20repetitions of
`client();await c.ingest(ACC);raw=c.checkpoint();r.restore(raw,sha256(raw))`.
Each transaction asserts5authored requests and identical restored collection pages.
`client`/ACC are imported from terminal.stocks.test_sec_filing_ingest. Rate time is
virtual;wall/CPU times are real and include tracemalloc overhead. No network/disk
performance or exchange/provider SLA is measured.

Ingest median87.039ms (range84.281–94.212);restore median58.107ms
(range53.884–60.184). Source bytes4,051;checkpoint7,828bytes. Total21loops3.115s
wall/3.096sCPU. Python-tracked peak348,436bytes;process ru_maxrss26,488KiB.
Concurrent compiler/test workload and tracing affect timings. This is one small
fixture,not a sustained-memory/leak proof or an improvement-versus-baseline claim.
The ignored measurement program SHA and full result are retained in evidence.

## Remaining scope and external blockers

Matrix: **34COMPLETE /8PARTIAL /7BLOCKED /1NOT APPLICABLE**,50rows.
Earlier48reviewed areas plusA18/A19decision became49entries;the explicitly requested
KrakenMD07added one area. Current total49reviewed areas plus1historical decision.
No prior requirement was removed or externally blocked row promoted.

Remaining engineering includes HTML/inline-primary source acquisition and older
submissions scheduling in the new coordinator;broader inline transform/document-set,
XML Schema and DRS semantics;full rounding/duplicate conformance;source-evidenced
accounting-equivalence and complete statements. Existing supplied-inline APIs and
bounded structural extension mapping must not be confused with those contracts.
Native/source recovery remains limited to its validated cursor/container/schema
boundaries;no new provider sequence/backfill guarantee is invented. Existing IEX/
Kraken supervision,differential,source-store and recovery fixtures reran without
changing their provider assumptions.

Kraken remains provisional. One bounded GitHub candidate-document request returned
404/14bytes,not a verified official book/checksum contract. Prior official-host
CONNECT403 remains historical evidence;no market endpoint was contacted. Do not
repeat failed candidates or remove provisional status without authoritative text.

External acceptance remains blocked by the no-launch/no-provider directive and
actual target/data evidence:authorized SEC/IEX qualification,owner-private Codespaces
HTTPS/WSS,real browsers/devices/assistive technology,current-candidate native ARM64,
complete observed L3 initialization/reference,empirical models and deployed runtime
security clearance. A18/A19historical requirement evidence remains unknown.

The next **bounded** source package (inline-primary manifest plus older-shard
scheduler) is estimated2–4engineering days including offline faults/packaging,subject
to agreeing exact supported document contracts. Broader schema/DRS/inline conformance
and accounting equivalence require multiple scoped milestones and an independent
corpus;the full original scope has no defensible fixed completion date yet. Provider,
owner-target and missing historical evidence have externally determined elapsed time.
No full-development or production-readiness declaration is made.

## Reproduction and exact continuation

With existing dependencies/native builds,from repository root:

```
PYTHONPATH=build/remaining-engineering/native-release/python:. python terminal/tests/run_no_launch_suite.py
PYTHONPATH=build/remaining-engineering/native-release/python:. python terminal/tests/check_xbrl_accuracy_contract.py
PYTHONPATH=build/remaining-engineering/native-release/python:. python terminal/tests/check_xbrl_statement_contract.py
PYTHONPATH=build/remaining-engineering/native-release/python:. python scripts/qualify_sec_filing_ingestion.py --fixture
cd terminal/web
npm test
npm run build
```

Use the intended supported Python/native binding environment;see evidence for the
five actual environments and sanitizer preload/limitations. These commands do not
launch GIG. Do not run --fetch,launch servers or dispatch qualification workflows
under this sprint's restrictions. No intermediate owner testing is requested.

Resume from the enclosing pushed documentation commit,read this report,
COMPLETION_MATRIX.json,MULTI_WORKSTREAM_EVIDENCE.json and the three package documents.
Preserve the five published implementations;do not rebuild their architecture or
repeat the whole audit. Start the next precisely scoped source/conformance package
with synthetic fixtures and keep unsupported cases explicit.
