# GIG effective XBRL relationships and statement/product integration

November 12, 2026 (America/New_York). Branch `development/gig-ui-redesign`.
Starting local/remote checkpoint **1d49ae2cf5df3659d97faf248c6a210e317c1684** was
clean and matched. Final tested runtime is **21160c43ee3be7cf0e91e064acf9e20333636746**.
The enclosing final documentation commit is identified by Git/remote receipt.
Protected branches and owner configuration are preserved. No reset, merge,
force-push, application startup, server, browser, provider connection, workflow,
deployment, paid resource or trading operation was performed.

## Working implementation published

|Checkpoint|Implementation|
|---|---|
|aec94eb|Bounded standard effective presentation/calculation relationships and source-bound DTS metadata.|
|f80a3eb|Statement selection, versioned company extension, read-only endpoint, private export and Stock Intelligence controls.|
|64b16ec|Strict calendar and UTC filing-cutoff validation for imported/browser statements.|
|96af263|Reproducible actual Python-product → TypeScript contract checker.|
|21160c4|Final statement SHA and company envelope included in output byte ceilings.|

Full SHAs, source receipts and logs: `EFFECTIVE_STATEMENT_EVIDENCE.json`.

### Effective relationships

The original strict presentation graph remains intact. New versioned
`STANDARD_EFFECTIVE_ARCS_V1` metadata handles supported standard presentation and
calculation base sets, combining split links across supplied taxonomy documents.
Equivalence preserves exact supported non-exempt attributes, including order,
preferred-label role and weight. Maximum priority and prohibition choose effective
arcs deterministically; duplicate/superseded/prohibited source arcs retain exact
URI/SHA and link/child positions. Unsupported attributes/roles/content invalidate
the affected whole role/kind, rather than disappearing from a usable partial graph.

Ordering is rational, not binary floating point. Calculation weights are restricted
to signed units; balance-sign conflicts, multiple effective calculation endpoint
pairs, unresolved locators, cycles and excessive depth remain unusable. Bounds:
64 networks, 4096 total input arcs, depth32 and 4 MiB final graph. Preferred labels
are retained as role URIs, not fabricated human text. Generic links/custom arcroles,
label-resource resolution and complete taxonomy/DRS validation remain unsupported.

See `XBRL_EFFECTIVE_RELATIONSHIPS.md` for the exact supported equivalence and
precedence contract and specification references. This is not full conformance
certification or a new network verification of the published specifications.

### Statement selection and provenance

`FilingCollection.statement_at` selects one latest acceptance-qualified filing in
an explicit form family at an exact timezone-aware nanosecond cutoff. Unknown or
future acceptance is excluded. Equal latest-time filings are ambiguous. A missing
or unsupported latest role cannot fall back silently to an older filing. Amendments
require an explicit supplied eligible predecessor; no additive or partial-fact
merge reconstructs a supposedly complete restatement.

Only supplied presentation concepts become rows. Facts preserve exact lexical and
numeric strings, units, period kinds, original fact IDs, source hashes, filing
identity, timestamps and accuracy metadata. Instant/duration contexts are separate;
there is no inferred fiscal quarter. Dimensioned, opaque or default-dependent facts
are not consolidated. Consistent duplicates retain every reference. Conflicting
values, multiple units, unsupported input, nil and missing facts remain explicit.
The new view does not invent balancing values, statement concepts or accounting
meaning from presentation order. All original inline document manifests remain
separate from the explicitly derived document-set identity.

Exact-rational calculation diagnostics compare reported parent and weighted terms
only in the same role, period and unit. Missing terms do not become zero.
`EXACT_DIFFERENCE` is not proof of an accounting defect or XBRL rounding inconsistency:
accuracy intervals are not implemented. Limits:128 concepts,12 output periods,
8 source references/cell and256 KiB final statement/product envelope. Output/lineage
excess rejects; an explicit flag reports older periods beyond12.

### Actual company/frontend integration

A distinct `gig.backend.company_xbrl.v1` extension wraps the versioned statement
view with exact symbol/CIK. Existing company.v2, statements.v2, companyfacts, SDK
and frontend flows remain available. StockWorkspace offers explicit server-owned
admission of a detached, bounded supplied collection (8 companies /16 MiB total).
There is no new HTTP upload/mutation route, automatic source fetch, startup load,
secret read, provider gate or replacement of companyfacts.

The new cache-only GET `/api/v2/companies/{symbol}/xbrl-statements` uses the existing
single analytical worker admission/cancellation gate. It requires `at`, accepts
bounded role/form and rejects duplicate/unknown parameters. The actual extracted
route body was executed against real StockWorkspace/AnalysisGate with fake request
metadata, without constructing ASGI or opening a socket. That is a code-path test,
not middleware, owner authentication or real HTTPS acceptance.

Stock Intelligence → Statements now has a separate source-bound XBRL section:
explicit cutoff/form/role, actual period selection, source and fact disclosures,
exact values, unit/status display and calculation diagnostics. It can read an
admitted cache or a private offline export locally, without uploading it.
Symbol/CIK, origin, timestamps, missingness and nested canonical hashes are checked.
Hash consistency is not SEC authenticity. Source receipt stays unknown when absent.
Company changes and superseded work invalidate/abort old responses. The existing
selected-facts table remains separate. No fixture is labeled live and no missing
L2/L3 depth is inferred.

See `XBRL_STATEMENT_PRODUCT.md` for offline batch/export instructions. Automatic
SEC/DTS acquisition and startup ingestion are still missing broader engineering;
they are not disguised as credential-only blockers. The current useful workflow
is explicit supplied admission or an authorized private export.

## Reproduced defects and repairs

1. An intermediate new statement selector omitted unsupported EUR input before
   checking unit ambiguity, allowing USD to look unambiguous. The fixture now
   retains ambiguity and suppresses a calculation result. Original failure and
   repaired tests are preserved.
2. An adversarial browser-artifact test proved that JavaScript normalized impossible
   calendar dates. Strict Gregorian date checks and UTC filing-cutoff checks now
   reject them. Exact acceptance comparison also uses the existing nanosecond helper.
3. An output-bound test proved that the new statement ceiling excluded its final
   integrity field (22-byte test ceiling produced97bytes). Final statement and
   company envelope size checks include all fields. Effective-relationship checks
   likewise include their final SHA.

These were failures in the newly developed pathways, not claims of historical
P0 engine defects. Intermediate TypeScript narrowing errors are retained; explicit
validated narrowing repaired them without disabling compiler checks. No financial
formula, assertion or native expectation was weakened.

## Final developer evidence

|Cohort|Actual result|
|---|---|
|GCC14.2 Debug/Release/ASan+UBSan guarded Python/bindings|420 each;zero failures/errors/skips|
|Clang19.1 Debug/Release guarded Python/bindings|420 each;zero failures/errors/skips|
|Final guarded outcomes|2,100 across5 supported configurations|
|Authored XBRL tests|167, including42 new relationship/statement/product cases|
|Focused native recovery CTest|GCC6/6/6;Clang6/6/5 passed|
|Frozen native identities|8/8matched in each of6compiler configurations|
|Frontend Node24.19|172passed;zero failures/skips|
|TypeScript /Vite8.3.5|Production build passed|
|Actual Python-product → TypeScript|8 cases /58assertions passed|
|Installed default SDK/current extracted source|8SDK+55recovery+167XBRL;28native-contract and58XBRL-contract assertions|
|Installed source-enabled SDK/current extracted source|8SDK+66recovery+167XBRL;35native-contract and58XBRL-contract assertions|

Cohorts overlap and are not a unique-test sum. The new actual contract checker is
reproducible as a developer-only command:

```bash
PYTHONPATH=build/remaining-engineering/native-release/python:. .venv/bin/python terminal/tests/check_xbrl_statement_contract.py
```

Use the installed/native-enabled Python appropriate to the existing development
environment. No server/browser/provider is required. For selected guarded regressions:

```bash
PYTHONPATH=build/remaining-engineering/native-release/python:. GIG_ITCH_FIXTURE=build/remaining-engineering/native-release/gig_itch_durable_checkpoint_tests .venv/bin/python terminal/tests/run_no_launch_suite.py
```

All final420-case cohorts run at runtime21160c4 with bind/connect/application factories
forbidden. Focused native/frozen execution ran at f80a3eb before subsequent pure
Python/TypeScript repairs; native/core/SDK/build inputs are byte-identical to both
starting and final runtime. Existing strict builds were checked; no unrelated full
CTest rerun is claimed. Full older native matrices remain historical evidence.
No native source/arithmetic or frozen hash changed.

GNU Python/native sanitizer checks use the existing harness with interpreter-exit
leak checking disabled;pure Python is not instrumented. Complete CPython shutdown
leak clearance is not claimed. Clang Python sanitizer runtime is unsupported and
not counted. Native Clang and GCC instrumented focused/frozen tests actually ran.
There is no native ARM64 execution in this task.

## Packaging, resources and privacy

A clean Git-export source archive from21160c4 has1,289members;all1,288tracked file
contents matched Git byte-for-byte. Unsafe paths, duplicate/special members and
private/cache/database/build payloads were excluded. SDK wheels are explicitly
reused from the qualified clean7aea334 build after confirming identical native/
SDK/build inputs. They were not rebuilt from the new archive. Both installed
variants were exercised against the final extracted source, including the actual
Python→TypeScript statement checker. Default optional source recovery remains
fail-closed;the enabled variant executes it. `PACKAGE_CURRENT.json` records bytes,
hashes, archive members, exact source and all consumer results.

Current initial JS:256.21kB (79.57kB gzip), compared with255.86kB (79.46kB gzip) at
the starting checkpoint. Stock Intelligence's deferred chunk is101.73kB (28.20kB
gzip). The deferred Three/OrbitControls chunk remains517.06kB (128.66kB gzip), with
the existing above500kB warning retained. No dependency was added or upgraded.
No browser responsiveness, visual quality, GPU, empirical latency or production
throughput claim follows from these build measurements. Test wall times in the
manifest are observations,not SLAs or before/after performance benchmarks.

Only authored fixtures were processed. No owner dataset, original provider record,
LOBSTER ZIP, credential or contact value was accessed or committed. The original
source hash receipts bind permitted fixtures, not an observed empirical corpus.
No provider permissions, execution gates or private-port configuration changed.

## Matrix, remaining implementation and qualification

Counts remain **34 COMPLETE /8 PARTIAL /7 BLOCKED /1 NOT APPLICABLE**:50rows =49
reviewed areas plus the separate historical A18/A19 decision. The original48-area
set gained the explicit Kraken area;the historical decision is not another product
feature. SEC02 now has working bounded effective relationships,source-bound
statement selection and company/frontend integration. No broad requirement or
externally blocked gate was promoted on fixture evidence.

Actual remaining engineering includes full inline transforms/named-targets/tuples/
escaped HTML;general complex schema construction/attributes/substitution;broader
open/negative/multi-role/inherited/typed-domain DRS and effective dimensional
precedence;generic/custom arcroles and label resources;rounding-aware calculation
consistency;extension/consolidated statement mapping;and automatic authorized
filing/DTS ingestion/history integration. Large statements outside explicit bounds
remain unsupported. Full historical source/vintage coverage needs a suitable
independently authorized source corpus.

Recovery was not widened speculatively. Existing source/native/product/fault/restart
contracts reran. Arbitrary compressed/partial/terminal recovery positions,unknown
schemas and unsupported observed correction semantics remain fail-closed until
specified and tested. IEX Level1 does not become full exchange depth.

Kraken stays provisional. Prior official-documentation CONNECT403 and unchanged
enforced restricted policy are retained;no repeated blocked request or feed was
attempted. Official contract verification remains separate from existing fixtures.

External gates still include current real-provider SEC/IEX reconciliation,complete
observed L3/reference initialization,current-candidate native ARM64,owner-private
Codespaces HTTPS/WSS,target browser/device accessibility/security,hardware durability
and the historical concentration requirements. No empirical trading-alpha or
production-readiness claim is made.

## Exact continuation

Read ACTIVE_ENGINEERING_CHECKPOINT.md,COMPLETION_MATRIX.json and
EFFECTIVE_STATEMENT_EVIDENCE.json. Do not repeat implemented relationships,private
exports or statement controls. Next bounded package:specification-grounded
calculation accuracy intervals and source-scoped extension/statement mapping,or
an explicitly restricted broader DRS/inline profile. Keep missing semantics
fail-closed. Full remaining conformance spans further engineering milestones;
no evidence supports declaring development or final acceptance complete today.
