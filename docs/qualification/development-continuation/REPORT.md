# GIG inline-XBRL and dimensional engineering — November 12, 2026

Branch:`development/gig-ui-redesign`. Starting local/remote checkpoint was clean
and matched **a2841e6e0e59c393bb26182a6b87156800e4686a**. Final tested runtime is
**3436ff56a3e223cad192223062c83d5a11da8282**. The enclosing report-only commit is
identified by Git/remote receipt. Existing work and protected branches were
preserved;no reset,merge,force push or owner configuration change was used.

## Published implementation

|Commit|Change|
|---|---|
|d8e1b85dd18b9458a79619132d1a53cbe9ad8085|Bounded inline document sets,continuations,transforms,ordered source lineage,atomic vintage/CLI integration.|
|a50fc52cd5883c0252fcaba9b3fe72a7b545124e|Explicit numeric simpleContent derivation V2,retaining V1 scope.|
|8393a082a13d15768a4ba7528defd105647de5e5|Restricted closed-hypercube/domain/default corroboration without synthesizing financial facts.|
|afea8ab2ed460a9119dfd351f91b3fe3bb44ea63|Distinct dimensional-result schemas to prevent old-code eligibility downgrade.|
|3436ff56a3e223cad192223062c83d5a11da8282|Fail-closed dimensional proof coverage,missing-policy and relabeling guards.|

## Inline document sets and source identity

The new explicit default-target inline1.1 profile processes bounded supplied
XHTML sets with shared contexts/units,cross-document nonNumeric continuation
chains,ordered passive markup and exclusions. Two narrow2015numeric transformation
subsets support exact scaling/sign conversion;the new profile bounds scale to±18.
The original plain parser retains its strict unsupported-feature policy and±6.
Missing/wrong-kind/shared/orphan continuations,cycles,nested facts,numeric
continuations,named targets,escaped HTML,unknown transforms and unmodeled markup
reject. No browser rendering,URI fetch or inferred financial value is involved.

All originals are permission/hash/filing-scope checked before any XML in a set is
parsed. Output has a distinct inline_set.v1 schema and explicitly derived manifest
hash. It does not pretend that a composite hash is an original SEC response SHA.
Actual document URI/raw SHA,receipt/acceptance metadata and fact/node/continuation
segments remain visible. Context/unit source locations are retained. Selected
financials expose original input SHA sets and the derived set identity;single-source
attribution is null where no one original contains the inputs. Aggregate receipt
remains unknown rather than replacing per-document receipts.

The existing immutable FilingCollection and private offline inspect tool now
accept these sets. Supplied DTS discovery traverses the exact reference union,
binds a distinct dts_set identity and can apply numeric/dimensional profiles.
Amendments and exact acceptance-time selection use the existing policy. Failed
later entries leave accepted collection state unchanged. Reordered input documents
do not invent a filing chronology;deterministic URI ordering binds the result.

A separate failing-before case proved a real context-identity defect:typed
`A<Code/>B` and `AB<Code/>` previously collided because interleaving was lost.
The XML representation now retains ordered text/children and opaque context trees
record normalized content_order under **DIM_CONTEXT_ELEMENT_V3_ORDERED**. Affected
derived context/fact hashes and parsed-artifact profile hashes intentionally change.
Raw source hashes,numeric values and all native frozen identities remain unchanged.
Old stored artifacts are not silently rewritten or overwritten.

See INLINE_DOCUMENT_SETS.md for exact limits,source contracts and exclusions.

## Bounded complex-type and dimensional profiles

`NUMERIC_SIMPLE_CONTENT_V2` adds explicit named simpleContent extension/restriction
value corroboration,including inherited supported numeric facets and units. V1
continues to refuse these complex derivations. Complex content,mixed types,
attribute declarations/wildcards and other schema features remain unsupported.
This is numeric-value validation,not complete XML Schema construction/derivation
validity. Global schema/statement flags stay false. See XBRL_SIMPLE_CONTENT_V2.md.

`EXPLICIT_CLOSED_HYPERCUBE_V1` uses supplied definition metadata to check a deliberately
restricted case:one role/link,one direct positive closed cube,explicit declared axes,
one domain root per axis and usable domain/member relationships. It checks required
axes,membership,placement,closed extras and defaults;cycles (including diamond paths)
and conflicts reject. Cached adjacency/domain analysis bounds repeated work.

Open/negative/multiple-role or assignment semantics,primary inheritance,targetRole,
precedence,unusable arcs,typed axes and broader DRS remain unsupported. Missing
source taxonomy cannot produce validity. Defaults are reported as derived evidence;
no dimensions/values are inserted into source contexts. Default-dependent facts
also stay excluded from consolidated financial selection. Complete DRS/schema and
statement flags remain false.

Dimensional results have distinct dimensional_instance.v1/dimensional_inline_set.v1
schemas. Older selection code therefore rejects instead of ignoring the new
eligibility policy. New selection verifies complete supported-policy coverage and
rejects missing,empty,unknown or relabeled dimensional guards even after rehashing.
No existing ordinary-instance contract was weakened. See XBRL_DIMENSION_PROFILE.md.

## Developer validation actually executed

|Cohort|Result|
|---|---|
|GCC14.2 Debug/Release/ASan+UBSan guarded bindings|378 each;zero failures/errors/skips|
|Clang19.1 Debug/Release guarded bindings|378 each;zero failures/errors/skips|
|Total final guarded outcomes|1,890 across5profiles|
|Authored XBRL cohort|125cases,42more than the starting83;included in378|
|Native focused recovery CTest|GCC6/6/6;Clang6/6/5 passed|
|Eight frozen native references|8/8matched in each6profiles|
|Frontend Node24.19|161passed;zero failures/skips|
|TypeScript/Vite8.3.5 production build|Passed|
|Actual native-to-TypeScript contract|35assertions with source-enabled SDK;28with default SDK|
|Installed default SDK/current extracted source|8SDK+55recovery+125XBRL cases;28contract assertions|
|Installed source-enabled SDK/current extracted source|8SDK+66recovery+125XBRL cases;35contract assertions|

These cohorts overlap;they are not a claimed unique-test sum. Native/core/SDK/build
and frontend source inputs are unchanged froma2841e6. The existing strict compiler/
instrumented builds were checked and focused/frozen tests reran in six profiles.
Those runs preceded final pure-Python dimensional-result guards;native inputs
remain identical. Older full CTest matrices remain historical evidence and were
not relabeled newly executed. No native arithmetic/reference expectation changed.

Final378profile wall times:27.614s GCCDebug,22.239s GCCRelease,153.019s GCCsanitizer,
24.975s ClangDebug,27.842s ClangRelease;two independent processes ran concurrently.
These are test durations,not a throughput/latency SLA. Native GCC/Clang sanitizer
checks passed. Pure Python is not sanitizer-instrumented. The existing GNU Python
harness disables interpreter-exit leak checking and retains separate live-interpreter
coverage;complete shutdown leak clearance is not claimed. Clang Python sanitizer
runtime remains unsupported and is not counted as executed.

Every final guarded cohort forbids socket bind/connect and application construction.
No ASGI factory,listener,browser or actual owner-target acceptance was run. Warnings
including the existing optional Three/OrbitControls chunk warning remain visible.
The unchanged initial JS is255.86kB(79.46kB gzip);deferred chunk517.06kB(128.66kB gzip).
No physical-device,GPU or browser-responsiveness measurement is inferred.

The context collision failure is retained. An intermediate DTS refactor omitted
an edge-list initializer and existing tests failed;the initializer was restored
without removing assertions.359/365/376/377intermediate cohorts are preserved as
intermediate evidence,not final counts. All final outcomes,source/log digests and
qualification exclusions are in INLINE_DRS_EVIDENCE.json. Earlier manifests remain
in Git and XBRL_SOURCE_CONTINUATION_EVIDENCE.json.

## Packaging,privacy and compatibility

The clean committed source archive contains1,274members. All1,273tracked file
contents were compared byte-for-byte to runtime3436ff5. Traversal,duplicate/unsafe
members and private-data/database/cache/build payloads were rejected by inspection;
only generated PKG-INFO is outside tracked source. Inputs used in tests are authored
fixtures,not original market data or actual SEC observations.

Both22-member SDK wheels were reused from the qualified clean7aea334 build after
proving byte-identical native/SDK/build inputs. They were **not rebuilt from the
new source archive**. Both installed variants were exercised against the new
extracted source. The default SDK still explicitly refuses optional source recovery;
the enabled SDK executes it. PACKAGE_CURRENT.json records all source identities,
artifacts,hashes and consumer results. No raw input or SDK wheel was committed.

Original plain XML/inline contracts,version1 numeric admission,native/Python/product
recovery,read-only company-v2 consumers and frontend workspaces remain compatible.
New derived schemas are explicitly opt-in and fail closed in older consumers.
The new numeric V2 profile is not a claim that application company-v2/browser
integration of these new XBRL artifacts is complete.

## Matrix and remaining scope

The matrix remains50rows =49reviewed areas+one historical A18/A19 decision. The
original48-area set gained the explicit Kraken area;the historical decision is
separate. Counts remain **34 COMPLETE /8 PARTIAL /7 BLOCKED /1 NOT APPLICABLE**.
SEC02 now has working document-set/simple-content/dimensional/export profiles;
no blocked requirement was promoted.

Actual remaining engineering:full inline registry/named-target/tuple/escaped-HTML
behavior;general complex content/attribute/substitution/schema construction;
open/negative/multi-role/assignment and inherited/typed-domain DRS/effective
relationships;presentation/calculation precedence;complete financial-statement/
extension-taxonomy mapping;and versioned read-only company-v2/frontend integration
of the new artifacts. Complete historical source/vintage evidence remains separate.
These are not silently dropped or all blamed on missing credentials.

Recovery was not speculatively widened. Existing plain/gzip,product,corruption,
resource,restart and lineage contracts were rerun. Arbitrary compressed/partial/
terminal positions,unknown schemas and unsupported observed corrections still
fail closed until explicitly specified and tested. No exchange semantics were
invented. IEX L1 is not treated as full depth.

Kraken remains provisional. The prior official-documentation CONNECT403 and current
unchanged restricted policy were retained;no repeated request or provider connection
was made. Offline fixtures do not establish the official live contract.

External gates remain lawful complete observed L3/reference initialization,current
provider/listing/SEC reconciliation,current-candidate native ARM64,owner-private
Codespaces HTTPS/WSS,target devices/accessibility/security/hardware durability and
historical A18/A19 requirements. No credentials,provider/trading gates,private-port
visibility,paid resources or protected branches changed.

**Full engineering remains incomplete.** The next bounded work package should
specify effective presentation/calculation and statement mapping or expand the
inline/DRS conformance profile,then add the versioned application-v2/browser path.
Each is a multi-day package;full XBRL/conformance and corpus coverage remains a
multi-week undertaking with source/specification dependencies. No overnight or
production-readiness promise follows from fixtures.

## Reproduction and continuation

Use an already-built intended binding profile on PYTHONPATH and an absolute
GIG_ITCH_FIXTURE path. The full378cohort requires the existing source-enabled SDK
profile;default-SDK unavailable behavior is separately qualified.

```bash
<venv>/bin/python terminal/tests/run_no_launch_suite.py
<venv>/bin/python terminal/tests/check_itch_product_contract.py
<venv>/bin/python -m unittest terminal.stocks.test_inline_set terminal.stocks.test_xbrl_dimensions
```

Existing GNU sanitizer preload/options remain as recorded in the manifests.
The private offline inspect tool accepts the new document-set schema and explicit
numeric/dimensional profile choices. It grants no source rights and fetches nothing.
Do not launch GIG,servers,providers,deployment,trading,workflows or owner acceptance
under this directive. Preserve current bounded profiles and add independent
conformance fixtures before expanding semantic claims.
