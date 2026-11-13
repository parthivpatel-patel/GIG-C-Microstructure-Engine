# GIG reported accuracy and source-scoped extension checkpoint

November 13, 2026 (America/New_York). Branch `development/gig-ui-redesign`.
Requested starting checkpoint:26432849a6a6bb0a373762b0e8829edd966f0901.
Recovery found local/remote already at **ae0d84125f42053082f2bf96af31463abe054afc**,
with surviving backend and partial frontend changes. They were preserved and
completed;no reset,discard,new branch,merge or force-push was used.

Final tested runtime: **5c77178e4ad75b47b5da3440a63b64e929b28a0f**. The enclosing
final report-only commit is identified by Git/remote receipt. Protected refs and
owner configuration are unchanged. Full source/log/artifact hashes and milestone
SHAs are in **ACCURACY_EXTENSION_EVIDENCE.json**.

## Published working code

|Checkpoint|Change|
|---|---|
|ae0d841|Exact bounded reported-accuracy enclosure primitive and16authored tests;already pushed when resuming.|
|dc772ce|Preserved opt-in backend statement/company-v2 extension,private CLI and supplied-declaration mapping.|
|b9a5f90|Frontend profile selection,accuracy/extension validation and displays;actual Python→TypeScript v2 checker.|
|19fe821|Reproduced and repaired unsupported embedded-linkbase omission;affected usable networks now fail closed.|
|5c77178|Reject requested accuracy exports that lack a company identity instead of silently returning legacy output.|

No GIG/ASGI construction,listener,application server,browser,provider/account
connection,workflow,deployment,paid service or trading operation was started.
No original provider/LOBSTER dataset or owner credential/contact was accessed.
All processed inputs were independently authored synthetic fixtures.

## Exact conservative accuracy engineering

`CLOSED_REPORTED_ACCURACY_V1` derives rational enclosures from supported numeric
accuracy. For finite decimals d,quantum q=10^(-d) gives [v-q/2,v+q/2]. INF is the
point [v,v]. For nonzero finite precision p,effective d=p-1-floor(log10(abs(v)))
is obtained from the exact decimal representation,never binary logarithms.
All arithmetic is Fraction/Decimal without context-dependent rounding.

Only disjoint parent and weighted-sum enclosures yield DEFINITELY_INCONSISTENT
within the supplied relationship/profile. Closed-boundary overlap is conservatively
ROUNDING_COMPATIBLE,not proof of exact accounting correctness or full XBRL conformance.
Signed-unit negative weights swap bounds. Exact-value residuals remain separate
so a rounding-compatible nonzero residual is not mislabeled a source defect.

Nil,missing terms,missing accuracy and unknown/conflicting duplicate values do
not become zero or infinite precision. Equal numeric duplicates intersect supported
enclosures while retaining every original fact ID. Differing values remain
conflicting even if their enclosures overlap. All participating period/unit/context
and filing identities must match;no dimensional aggregation or cross-filing filling
is introduced. Invalid declarations reject;unsupported semantics are explicit.

Limits:exponents±128,numeric strings80characters,8duplicates,128terms,bounded
finite base-ten rational endpoints. Finite precision at zero and reported values
not canonical for their declared quantum remain unsupported;no rounding/tie rule
is guessed. These restrictions and specification references are documented in
XBRL_ACCURACY_V1.md. This is not full Calculations1.1/rounding/duplicate conformance.

## Source-scoped extension mapping

The new opt-in `accuracy-extension-v2` returns distinct
`gig.sec.xbrl.statement_view.v2` / `gig.backend.company_xbrl.v2` schemas. Existing
statement/company defaults remain v1. Older clients reject the new schema rather
than ignoring its policy. SDK/native APIs and existing companyfacts are unchanged.

Extension QNames map to actual supplied declarations,presentation roles,roots and
incoming relationship indices. Source document SHA/URI,original order,preferred-label
role,arc provenance,filing/accession/amendment and nanosecond cutoff remain exact.
`accounting_metric` stays null—even for a company extension locally named Assets.
No name similarity,role name or adjacency creates a GAAP alias or ratio input.
This implements structural statement mapping,not universal accounting equivalence.

Numeric extension display requires supplied ordinary-item declarations,known numeric
base or supported bounded derivation/facets,valid units and matching period/context.
Unsupported types,substitution and DRS scope are explicit unavailable states.
Invalid numbers/facets/nil declarations reject the request without changing accepted
collections. Dimensional/opaque/defaulted inputs are not promoted into consolidated
facts. Exact source contexts and units are included in the v2 research view.

Original extension fact objects keep their original IDs and unverified value=null.
Separate `numeric_facts` records bind derived exact lexical interpretation to the
original fact ID,declared/resolved type,filing and parsed instance hash. Source facts
are not rewritten or provenance-relabeled. Missing,nil,conflicting and mixed-unit
rows remain explicit. Full statements/source history are not manufactured.

## Product and frontend integration

The existing cache-only company endpoint accepts explicit
`profile=accuracy-extension-v2`;default legacy-v1 behavior remains. Query bounds,
unique parameters,single analytical worker,cancellation and sanitized errors are
preserved. Actual endpoint bodies are exercised by AST extraction against real
workspace/worker classes without ASGI construction or sockets. This is not a
private-target authentication or HTTPS acceptance test.

Stock Intelligence → Statements now offers exact-value v1 or reported-accuracy/
supplied-extension v2. It shows exact rational enclosures,separate exact residuals,
source structure and diagnostics through accessible labels/tables/details.
Private offline exports can be opened locally,without upload. The selected API
profile must match its response;silent downgrade is rejected. Company/input changes
abort or invalidate older work. Existing financial facts/ratios/workspaces remain.

Both canonical hashes and symbol/CIK,filing,period/unit/fact provenance are checked.
A self-consistent hash is lineage/integrity,not SEC source authentication. The frontend
never recalculates a financial model to substitute for backend results. No browser
or visual/physical-device validation was performed under the no-launch restriction.

Offline export adds `--statement-profile accuracy-extension-v2` to the documented
private batch command with --company-symbol and --statement-role. Read/hash/path/
symlink/permission safeguards and new-only0600 output remain. No provider request,
credential read,new HTTP upload,execution gate or automatic source fetch was added.
See XBRL_ACCURACY_EXTENSION_PRODUCT.md for supported scope and operation.

## Reproduced source-scope defect

A supplied schema with an embedded linkbase was previously omitted from DTS
relationship processing while an external presentation remained usable. The
failing fixture exposed AVAILABLE instead of unavailable. An omitted embedded
arc could affect precedence or dimensional scope;it cannot be treated as absent.

Embedded relationship content now records EMBEDDED_LINKBASE_UNSUPPORTED and makes
affected candidate presentation/effective graphs unusable. Definition presence is
unknown (null),not false. Both statement profiles return an explicit unavailable
view until the embedded contract is implemented. The original failure and repaired
regression logs are retained. This is a fail-closed repair,not a claim that embedded
linkbase semantics have been implemented.

A final negative CLI check also reproduced a silently ignored profile request:
--statement-profile accuracy-extension-v2 without --company-symbol produced a legacy
acceptance export. It now rejects explicitly;unknown profile values also reject.
Existing successful v1/v2exports remain unchanged.

The partial resumed frontend also initially failed strict TypeScript narrowing.
An explicit never-returning validation function repaired it;compiler flags and
numerical assertions were not weakened. All final checks pass.

## Final developer validation

|Cohort|Result|
|---|---|
|GCC14.2 Debug/Release/ASan+UBSan Python/native-binding guarded cohort|457each;0failures/errors/skips|
|Clang19.1 Debug/Release guarded cohort|457each;0failures/errors/skips|
|Total guarded outcomes|2,285across5supported configurations|
|Authored XBRL cohort,included above|204cases;37new since requested baseline|
|Focused native recovery CTest|GCC6/6/6;Clang6/6/5 passed|
|Eight frozen native identities|8/8matched in each6compiler configurations|
|Frontend Node24.19|184passed;0failures/skips|
|TypeScript/Vite8.3.5 production build|Passed|
|Actual v2Python→TypeScript contract|10cases/57assertions passed|
|Preserved v1Python→TypeScript contract|8cases/58assertions passed|
|Installed default SDK/current extracted source|8SDK+55recovery+204XBRL;28native,58v1 and57v2contract assertions|
|Installed source-enabled SDK/current extracted source|8SDK+66recovery+204XBRL;35native,58v1 and57v2contract assertions|

Cohorts overlap;these are not unique-test totals. Final guarded checks ran at runtime5c77178. Native/frozen and frontend checks ran
at19fe821;the last repair changed only CLI argument admission and an existing Python
test. Final native/SDK/build/frontend inputs are byte-identical to19fe821. The strict configured builds were checked.
Native/core/SDK/build inputs are unchanged from baseline;the unrelated full CTest
matrix was not redundantly rerun. No frozen native expectation changed.

GNU Python/native sanitizer qualification uses the existing harness with interpreter
exit leak checking disabled;pure Python is not instrumented. Complete CPython
shutdown leak clearance is not claimed. Clang Python sanitizer runtime remains
unsupported and is not counted. Native GCC and Clang instrumented focused/frozen
checks actually ran. No native ARM64 execution occurred.

Observed guarded wall times:34.385s GCCDebug,29.924s GCCRelease,146.965s GCCsanitizer,
34.913s ClangDebug,18.407s ClangRelease (two independent processes concurrently).
These are test durations,not throughput/latency improvements or production SLAs.

## Clean source,artifacts and resources

A clean Git-export source archive from5c77178 contains1,302members;all1,301tracked
file contents matched Git byte-for-byte. Unsafe paths,duplicates,special members
and private/database/cache/build payloads were rejected by inspection. No raw
market data or generated owner-private export was committed.

Both22-member SDK wheels are explicitly reused from the qualified clean7aea334
build after verifying identical native/SDK/build inputs. They were NOT rebuilt
from the new archive. Both installed variants were tested against the final
extracted source,including the actual v1/v2TypeScript consumers. The default SDK
still rejects optional source recovery;the enabled SDK executes it. Artifact origins,
source hashes and all consumer logs are recorded in PACKAGE_CURRENT.json.

Current initial JS:256.34kB (79.63kB gzip);Stock Intelligence deferred chunk111.61kB
(30.88kB gzip). Deferred Three/OrbitControls remains517.06kB (128.66kB gzip),with
the existing large-chunk warning visible. No dependency was added or upgraded.
These are build measurements,not browser/GPU/mobile responsiveness evidence.

## Remaining scope and exact continuation

Counts remain **34 COMPLETE /8 PARTIAL /7 BLOCKED /1 NOT APPLICABLE**. There are50
rows:49reviewed areas plus the separate historical A18/A19 decision. The original
48-area set gained the explicit Kraken area. No blocked gate was promoted on
fixture evidence. SEC02 gained implemented bounded accuracy/extension/product
functionality but remains PARTIAL.

Remaining engineering:rounding/precision/tie/duplicate semantics outside the
conservative profile;explicit evidence-backed accounting-equivalence/full statement
mapping;embedded/generic relationships and labels;broader DTS/schema complex content,
attributes/substitution;open/negative/multiple-role/inherited/typed-domain DRS;
full inline transforms/named targets/tuples/escaped HTML;and automatic authorized
filing/DTS ingestion and independent historical source/vintage coverage.

Recovery was not widened speculatively. Existing source/native/product/restart/
corruption cases reran. Unknown schemas,source positions,sequence guarantees and
observed corrections remain fail-closed. IEXLevel1 never supplies fabricated L2/L3.
Kraken remains provisional;prior documentation CONNECT403/current enforced policy
are retained without another request or feed connection.

External qualification still requires lawful source corpora/current SEC and IEX
reconciliation,complete observed L3 initial/reference state,current-candidate native
ARM64,owner-private Codespaces HTTPS/WSS,target devices/security/accessibility,
hardware durability and historical requirement decisions. No full development,
provider,owner acceptance,empirical alpha or production readiness is claimed.

Next bounded work should select a precise authoritative contract for the remaining
rounding/duplicate semantics or embedded/DTS/accounting mapping. Do not repeat the
new profile or bypass its guards. Read ACTIVE_ENGINEERING_CHECKPOINT.md,
COMPLETION_MATRIX.json and ACCURACY_EXTENSION_EVIDENCE.json before continuing.
