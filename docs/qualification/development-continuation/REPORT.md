# GIG XBRL and source-recovery development — November 12, 2026

Branch:`development/gig-ui-redesign`. Starting local/remote checkpoint was clean
and matched **57e7bc2df3a7a11af3acc036b0231dae293bcb92**. Final tested runtime is
**f7c1e0df2fb95e48f84752de51fc396daf0518f8**. The enclosing documentation commit
is identified by Git/remote receipt rather than self-embedded here. Existing
uncommitted work was preserved. Protected branches,provider permissions,UI identity
and trading-disabled configuration were not changed.

## Published implementation

|Commit|Completed change|
|---|---|
|186d54c7dd8d8772f25f7e6072fb5fc4587f09cd|UTC-consistent filing-vintage selection and strict significant context/unit text admission.|
|6d97e95f3ba77ab99c0000bbc594cb555fc70ab0|Opt-in supplied-taxonomy numeric value/facet corroboration and usable offline DTS export.|
|d84578587ad99cee78f08b1ff738971070762177|Native source-recovery SDK bridge,private product revision2 lineage and immutable continuation CLI.|
|7aea334f0171b862b055f9b3ebda46a78894dc7a|Five-state native-to-TypeScript contract and empty continuation progress repair.|
|f7c1e0df2fb95e48f84752de51fc396daf0518f8|Full-width browser provenance and native-bound lineage validation,with real high-generation fixture.|

## XBRL correctness repairs

Four authored methods reproduced six failing assertions/subtests against the
starting source. Exact acceptance filtering used UTC nanoseconds but its extra
filing-date guard used the cutoff's lexical date prefix. Equivalent offset
spellings crossing a calendar boundary could therefore select different facts;
a positive offset could also admit a future filing date. The guard and descriptor
date now derive from the same UTC instant using integer arithmetic. Original
source acceptance/receipt values and caller as_of spelling remain preserved.
Equivalent instants have equivalent eligibility;complete output hashes still
identify the explicitly supplied as_of string.

Significant unmodeled text in context/entity/period/segment/scenario or unit
containers now rejects explicitly. Previously an opaque text-only segment could
be discarded and leave a fact apparently consolidated. Whitespace and actual
identifier/measure/period-leaf/typed/opaque payload text retain their existing
contracts. No unknown context qualifier is interpreted as absent.

## Numeric taxonomy and filing-vintage integration

`NUMERIC_VALUE_FACETS_V1` is an explicit optional profile on
`FilingCollection.ingest_dts_batch`. It resolves supported decimal/integer bases
and named simple restrictions,checks exact lexical/range/digit facets and known
unit forms,and preserves original document/fact/type lineage. All supported
inherited facets apply. Decimal precision cannot round a comparison. Unsupported
selected types,cycles,depth/resource excess,corrupt hashes and contradictions
reject the entire candidate batch. Existing declaration-only ingestion remains
compatible. Nil remains missing,not zero;unknown concepts remain unselected.

The existing offline CLI now accepts `gig.sec.xbrl.input_dts_batch.v1` with explicit
supplied documents,hashes and the chosen numeric profile. It preserves permission
admission,relative-path/symlink restrictions,bounded reads,atomic collection
publication and exclusive private result files. No URI is fetched. This is a
working path from supplied source/DTS through filing-vintage selection to a
reproducible private export,not an unconnected parser demonstration.

This profile validates selected numeric values against retained supported
restrictions. It does not validate complete XML Schema construction,complex
content,custom type derivation,DRS/hypercube/default relationships or accounting
meaning. `schema_type_validation` and `complete_statements` remain false.
Presentation order still does not invent financial-statement mappings. Source
SHA values,amendment lineage,missing receipts and original lexical values remain
intact. See XBRL_NUMERIC_PROFILE.md and XBRL_VINTAGE_REPAIRS.md.

## Native/source/product recovery integration

The existing C++ `resume_hot_source` coordinator is now exposed through the Python
SDK when `GIG_BUILD_ITCH_STREAMING=ON`. Default OFF builds preserve their existing
dependency contract and fail explicitly if source continuation is requested;
there is no unverified Python decoder fallback. No build option authorizes a
provider connection,observed capture,execution or application startup.

A separate typed `ItchSourceAdmission` supplies independently retained source
hash,capture,generation,container and first frame/ordinal. The native coordinator
verifies committed prefix receipts without applying them,then applies only new
complete frames in an isolated owner. Plain BinaryFile and one complete
CRC-verified gzip member are supported. Gaps,changed prefixes,wrong scope,
partial/terminal frames,extra members and resource refusal reject. The returned
SDK admission hashes the newly encoded image rather than retaining the old image
hash. Existing native allocation-failure behavior remains unchanged.

The private `continue-source` operation requires an exhausted authored product
continuation;it will not silently replace pending records. It creates a new
immutable product revision2 with source/bundle/image hashes,container,capture,
generation and source-cursor lineage. Revision1 remains compatible. Repeating an
identical verified source with no new events returns identical bundle bytes.
Both books restore paused;capture and explicit migration retain lineage. The
original writer's process-interruption and private-file contracts remain in use.
No arbitrary compressed seek or unknown native schema conversion was added.

Final review reproduced an actual precision defect in the new provenance
projection. With a real native generation9007199254740993,the previous view method
passed that integer through JSON;Node received9007199254740992. The public history
projection now uses canonical decimal strings,with `DECIMAL_STRINGS_V1` metadata.
Private revision2 remains integer-compatible. Every retained initial frame and
ordinal is also compared with native configuration on restore. The regression
uses the actual old view method and real native fixture,then validates the fixed
JSON with Node;no application is constructed. See ITCH_SOURCE_PRODUCT.md.

## Frontend integration repair

The actual native-to-TypeScript check now exercises five states,including a
source-restored revision2. It exposed an empty replayable range displayed as100%
progress. That range now displays0%;completed nonempty continuations still show
100%. The original assertions are retained and a new unit case covers the empty
restored range. All12workspaces and existing visualizations remain accessible;
this is a focused correctness change,not another redesign.

## Executed developer validation

|Current check|Result|
|---|---|
|Rebuilt full GCC14.2 Release CTest|152/152 passed|
|Focused recovery CTest:GCC Debug/Release/ASan+UBSan|6/6/6 passed|
|Focused recovery CTest:Clang19.1 Debug/Release/ASan+UBSan|6/6/5 passed|
|Frozen reference reruns|8/8 identities matched in each of6profiles|
|Final optional-fixture rebuild/durable CTest|1/1 passed in each6profiles|
|Final guarded Python:CPython3.12.14|336 each across GCC Debug,Release,sanitizers and Clang Debug,Release;1,680 outcomes;0failures/errors/skips|
|Affected authored XBRL|83 cases,included in336 and repeated from extracted source|
|Original product+durable+new source-product checks|38 cases;includes11new source-product cases and real u64/Node regression|
|Frontend Node24.19 tests|161 passed;0failures/skips|
|TypeScript/Vite8.3.5 production build|Passed|
|Actual native-to-TypeScript contract|35 assertions /5states;no browser/application|
|Installed default SDK and extracted source|8SDK+55recovery+83XML cases;28contract assertions;actual disabled source capability verified|
|Installed source-enabled SDK and extracted source|8SDK+66recovery+83XML cases;35contract assertions|
|Runtime `pip check`|No broken requirements;not a security-advisory clearance|

These are overlapping cohorts,not a claimed unique-test sum. The full GCCRelease
and six focused/frozen runs preceded the final public-projection repair and
optional high-generation fixture branch. Native SDK/core/build inputs are
byte-identical between7aea334 andf7c1e0d. The final durable test recompiled and
passed again in all6profiles;the final336binding cohorts include the high-generation
branch. Original native `src`/`include` algorithms are unchanged from57e7bc2.
Earlier full six-configuration native CTest totals remain historical evidence and
are not relabeled newly rerun.

The full Release detail records363 durable assertions,57restore/63encode
allocation-failure points,163 source assertions and67source-restore failure
points. Native GCC/Clang sanitizer checks and GNU Python-binding sanitizer
regressions passed. The existing Python harness disables interpreter-exit leak
checking and retains separate live-interpreter coverage;this is not complete
CPython-shutdown leak clearance. Clang Python sanitizer runtime remains unsupported
by the existing harness;it is not marked PASS or counted as an executed profile.

All final guarded cohorts forbid socket bind/connect and the application factory
and assert no ASGI application construction. No browser or visual acceptance was
performed under the explicit no-launch directive.

## Clean-source packaging and measured observations

A source archive generated from a verified Git export of f7c1e0d contains1,266
members. All1,265tracked file contents were compared to that exact commit;
changed runtime files were explicitly checked. Traversal,duplicate paths,unsafe
member types,private-data/database/archive/cache/build payloads were rejected by
the inspection. Only generated PKG-INFO is outside tracked content. Pending
report edits remained preserved in the working tree and were not substituted for
committed archive bytes.

Both22-member wheel variants were rebuilt from the earlier clean7aea334 source
archive. SDK/native/build inputs remain byte-identical atf7c1e0d,so those wheels
were reused with the new extracted server/source archive. They were **not rebuilt
from the final source archive**. PACKAGE_CURRENT.json records both source identities,
byte-equivalence verification,artifact hashes and installed-consumer results.
The default binary was tested without patching:its source capability is absent
and a valid request fails explicitly. The enabled binary executes the actual
native coordinator. No SDK wheel,raw source fixture or private data was committed.

Final336-case profile wall times:31.389s GCCDebug,26.735s GCCRelease,137.438s
GCCsanitizer,21.884s ClangDebug and18.676s ClangRelease. Two independent profile
processes ran concurrently. The frontend initial JavaScript is255.86kB
(79.46kB gzip);the deferred Three/OrbitControls chunk is517.06kB(128.66kB gzip).
The existing chunk-size warning remains visible. These are test/build observations,
not latency,throughput,memory,SLA or browser responsiveness claims.

Intermediate failures were retained:the four original XBRL regressions,the
zero-length-range contract failure,the u64 projection failure,a new test helper
that initially hashed a negative string input before calling the SDK,an incorrect
dependency-cache working-directory prefix,and an inherited CXX setting naming an
unavailable compiler. The last two were corrected with an explicit matching
same-project dependency cache and an installed GNU compiler,without dependency
or production-source workarounds. Warnings were not suppressed and mathematical
assertions were not weakened. Details/receipts are in
XBRL_SOURCE_CONTINUATION_EVIDENCE.json;all earlier source-bound manifests remain
available in Git and PRODUCT_SESSION_EVIDENCE.json.

## Matrix and remaining work

50rows =49reviewed areas+one historical A18/A19 decision. The old48-area set gained
the explicit Kraken MD07 area;the historical decision is separate. Counts remain
**34 COMPLETE /8 PARTIAL /7 BLOCKED /1 NOT APPLICABLE**. SEC02/REL02/UI10 now have
substantially expanded implementation/evidence;no external gate was promoted.

Actual remaining engineering includes broader inline transformations/continuations,
complex schema validation,dimension/DRS/hypercube/typed-domain/default relationships,
effective presentation/calculation precedence,complete statement mappings and
read-only v2 integration. Supported-source correction/losslessness and additional
recovery positions/schema migrations require authoritative explicit contracts;
unsupported actions still reject. These gaps are not silently declared optional
or attributed only to missing credentials.

Kraken remains provisional. The prior official-documentation CONNECT403 is
preserved;the current restricted access policy is unchanged,so no repeated request
or feed connection was attempted. Future protocol/checksum expansion needs the
actual authoritative contract. Offline Kraken fixtures passed within336;they do
not prove the live contract.

External gates remain complete lawful observed-L3 initialization/reference
coverage;current permitted listing,SEC and IEX reconciliation;current-candidate
native ARM64 runtime;owner-private Codespaces HTTPS/WSS;physical GPU/mobile and
assistive-technology testing;target security/artifact and hardware durability
qualification;and the unresolved historical A18/A19 contract. No secrets or
provider permissions were changed. No accounts,orders,trading,paid resources,
deployments or workflows were used.

**Full approved development remains incomplete.** This sprint published concrete
bounded XBRL/source/product improvements and repaired reproduced defects. The next
bounded inline/relationship profile is a multi-day package;full XBRL fidelity is
a multi-week engineering/conformance effort whose exact size depends on explicit
supported specification/source coverage. External qualification timing cannot be
inferred from fixtures. Do not initiate owner acceptance under this directive.

## Reproduction and exact next step

Use the intended already-built binding profile on PYTHONPATH,with an absolute
GIG_ITCH_FIXTURE path. The full336cohort requires a source-enabled SDK build
(`GIG_BUILD_ITCH_STREAMING=ON`,existing zlib>=1.3.1);the default SDK's explicit
unavailable-capability behavior is separately tested.

```bash
<venv>/bin/python terminal/tests/run_no_launch_suite.py
<venv>/bin/python terminal/tests/check_itch_product_contract.py
<venv>/bin/python -m unittest terminal.stocks.test_xbrl_types terminal.stocks.test_xbrl_tool
```

GNU sanitizer preload/options follow the existing harness and manifest. These
commands are offline developer checks,not launcher/deployment instructions.
Private XBRL supplied-DTS and ITCH continue-source commands are documented in
XBRL_NUMERIC_PROFILE.md and ITCH_SOURCE_PRODUCT.md. They require trusted explicit
input hashes and grant no dataset or provider authorization.

Next implementation:select the next bounded authoritative inline transformation/
continuation or dimensional-relationship profile,add independent conformance
fixtures and integrate its validated outputs with the existing vintage/statement
contracts. Do not duplicate numeric facets,UTC guards,full-source SDK recovery,
private product continuation or full-width provenance. Preserve no-launch,
no-provider,no-trading and protected-branch restrictions.
