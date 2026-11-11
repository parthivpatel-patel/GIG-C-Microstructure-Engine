# GIG ITCH recovery and remaining-development checkpoint — November11,2026

Branch:`development/gig-ui-redesign`. Starting remote53e5892c58390d9a5bd935d7a40a452beb842497 was clean and verified. Latest implementation source:`0c4196b2e0270dacfa07638c2c5d94f3de54cb49`. All source milestones below were pushed and independently checked against the remote. Final documentation closure is identified by Git rather than a self-referential commit hash.

## Published implementation

|Commit|Verified working change|
|---|---|
|`b2e05dc5b65f9127a9ecf9f1064bf5af1b38e68c`|Preserved/fixed the interrupted fingerprint writer;owned ITCH context/receipt/two-book hot images and isolated import.|
|`56cd5c698fecfff3e31a309ee6c6a997137adc37`|Actual NativeSession hot-state integration,private immutable checkpoint files,explicit native-validated migration;L2 precision/worker/retry repairs.|
|`5768da42f25321257047208b92f580f83be788cc`|Bounded plain inline-XBRL1.1 and supplied DTS discovery/simple presentation relationships.|
|`20a63d90095cbd24b84215668dbae4c7c13b0d8f`|Hot context pre-copy bounds and complete inline-output/fact bounds,with regressions.|
|`0c4196b2e0270dacfa07638c2c5d94f3de54cb49`|Bounded IEX cancellation drain,retiring-worker admission fence and late socket publication rejection.|

The initial native milestone was published before continuing the other packages. No surviving code was discarded or left intentionally uncommitted. Protected branches,provider permissions,trading controls and frontend design remain unchanged.

## ITCH hot-context recovery

`SourceContext::checkpoint/restore` own directories,active/inactive lifetime orders,seed-retired references,matches/broken flags,manifest,policies,lifecycle,source locations/ordinals/timestamps and resource accounting. `SyntheticReconstructor::hot_checkpoint/restore_hot` additionally own receipts,per-book derived sequences and both native replay/book images. Direct isolated restoration verifies independently retained identity,expected code/configuration,receipt adjacency and active source/native identities,side,exact price/quantity and counts. It does not reapply source records to reconstruct the book. Donor prepared tokens cannot cross into the restored context;new token guards do not enter deterministic fingerprints.

The interrupted writer matched empty optionals through `value()` before `has_value()`,causing bad_optional_access. Dispatch order was repaired. Strict ByteOffset/compiler errors were corrected without weakening warnings. A later4097-order context reproduced image allocation before the declared4096-row limit;preflight now rejects before any attempted copy and preserves accepted state.

**This is a bounded owned typed C++ image**,not a deployed durable full-ITCH file loader. Authored-empty accepted complete-record boundaries are supported. Seeded hot reconstruction,stable serialized artifact admission,Python/full-ITCH bridge,gzip/partial-framer coordination and actual source/hardware recovery remain open. Existing seeded prefix replay and gzip-boundary replay remain unchanged. See `ITCH_HOT_CONTEXT.md`,`ITCH_HOT_CONTEXT_EVIDENCE.json` and final `HOT_IMAGE_LIMITS_EVIDENCE.json`.

## Product-session and market-data follow-through

The actual NativeSession now supports explicit capture/restore APIs. Restore bypasses default20-event startup replay,restores native state/position/speed and resumes paused with fresh process-local controls. Only the authored native dataset is admitted;LIVE,SIMULATION,provider-shaped and recorded sessions are rejected. There is no new startup switch or network/file HTTP endpoint.

Private revisions use complete write/file fsync followed by exclusive atomic link publication and directory fsync. Rollback input is never overwritten. Before/after publication fault tests and a real child exit79 verify admissible restart behavior within this local filesystem. Explicit migration validates the native schema/rules/configuration/canonical state before rebinding implementation/binary metadata,and retains bounded source lineage. This is not proof of equivalence of arbitrary historical code semantics or hardware power-loss durability. See `SESSION_L2_RECOVERY.md`.

L2 regressions reproduced finite scientific JSON quantity rejection,concurrent2-worker admission and endless snapshot/corruption retry cycles. Exact bounded Decimal expansion,serialized ownership,retiring-worker fences,8-consecutive-failure exhaustion and stable30-second retry reset now pass fixtures. Jitter is bounded/finite. Existing crypto L2 native/source-labelled book/depth/research interfaces are retained. **Kraken remains provisional**:current official protocol/rights evidence was not independently retrieved;the known blocked host was not retried or bypassed. No real Kraken data was obtained.

IEX shutdown now revokes socket publication rights before waiting,retains a cancellation-resistant worker on timeout and denies replacement. The original published close failed the deterministic regression;the repaired36-case IEX recovery/retry/checkpoint cohort passes. Permission gates,read-only destinations,subscription bounds,source accounting and execution/retention defaults are preserved. See `IEX_SHUTDOWN_REPAIR.md`.

## SEC/XBRL

Plain inline-XBRL1.1 admits exact bounded scale/sign values,nil and original lexical/source lineage into the existing filing/vintage pipeline. DTS discovery consumes supplied files only,verifies source digests,document kinds/import namespaces,and preserves missing references without network fetches. Simple presentation locators/order/cycles are supported;unresolved/custom/precedence/split-role semantics are not labelled usable full hierarchies. Structural closure is separate from type/accounting validation.

All XML source/permission admission precedes XML processing. Entity/DTD/XInclude rules and bounded fact/complete-output limits remain enforced. Full transforms,continuations,tuples,nested fact markup,complete XML Schema/custom types,extension semantics,relationship precedence/calculation networks,complete statement assembly and read-only v2/UI integration remain missing. No missing historical periods or original receipts were fabricated. See `XBRL_NEXT_PROFILE.md`.

## Actual developer validation

|Cohort/configuration|Outcome|
|---|---:|
|GCC14.2 Debug /Release /ASan+UBSan CTest|149/149 ·149/149 ·150/150|
|Clang19.1.7 Debug /Release /native ASan+UBSan CTest|149/149 ·149/149 ·146/146|
|New ITCH hot-context checks in **each** native profile|221passed;46actual restore allocation-failure points|
|Eight frozen native identities in **each** of6profiles|All actually executed and matched|
|Final guarded Python,each GCC Debug/Release/ASan+UBSan and Clang Debug/Release binding profile|263/263 in each of5profiles;0failures/errors/skips|
|XML affected cohort|48/48 per5binding profiles|
|Focused L2/provider +product session|62+9cases passed|
|Focused IEX recovery/retry/checkpoint|36/36|
|Actual Python→TypeScript market/SEC admission|8+5assertions passed|
|Packaging patterns|3/3|
|Source-built installed SDK consumer /native+session recovery|8/8 +28/28|
|Current source archive|1,233members;24runtime/test entries byte-compared;no private/build/cache/DB/ZIP/native binary payload|

These are separate overlapping cohorts,not a fabricated single assertion total. Clang Python ASan remains unsupported by the repository's existing GNU/Linux-only Python harness;Clang native sanitizer and GCC Python sanitizer profiles passed. Existing live-LSan coverage is not whole-CPython exit-leak clearance.

One focused command initially misspelled the test-class locator. A strengthened fake worker then omitted the initial CONNECTED_PENDING handshake phase,so five broad attempts and one focused attempt stalled at fixture setup. Only those task-owned test processes were terminated;their partial logs are retained and not counted as passes. The fixture phase/readiness wait was corrected,and the final263-case cohort passed in all5profiles. Original reproducible production defects and intermediate new-code failures are retained separately. Existing Starlette/httpx deprecation remains visible;no assertions or warnings were suppressed.

Frontend source is byte-unchanged by this continuation. Its prior154-test/production-build evidence remains bound to53e5892 and was **not rerun**. No current browser/WebGL/app/HTTPS/WSS target acceptance is claimed. No new production throughput,latency,RPO/RTO or hardware SLA is claimed;the older HOT_RECOVERY_BENCHMARK remains historical source-bound evidence,not a new ITCH-context measurement.

## Completion accounting and remaining work

The previous49rows are preserved. The user's explicit official-contract Kraken L2 requirement is now tracked as MD07,so **50entries =49reviewed areas +1historical A18/A19 decision**. Counts:34COMPLETE /8PARTIAL /7BLOCKED /1NOT APPLICABLE. This is an explicit new requirement row,not an extra historical decision or an invented completion percentage.

Full development remains incomplete. Next engineering packages:

1. Serialize/admit the full typed ITCH image with independently trusted artifact/source identity;add seeded hot reconstruction and coordinated framer/gzip recovery. Preserve the completed typed/native APIs.
2. Complete remaining XBRL transformation/type/relationship/statement profiles and v2 integration;preserve unknown source coverage and missing receipts.
3. Reconcile Kraken candidate semantics against verified official documentation before changing provisional status. Do not guess current wire/CRC/update options or exchange continuity.
4. Obtain authoritative observed cancellation/backfill semantics and the missing historical A18/A19 contract. Do not invent complete/lossless tape guarantees.

Actual observed L3 initialization/reference,private owner IEX/SEC/browser deployment,current native ARM64,device/WCAG and target dependency/hardware qualification remain separate blocked evidence. Existing owner-reported source observations stay owner-reported. Planning ranges remain conditional:days for a tightly bounded remaining recovery codec/seed/framer package;engineer-weeks for full XBRL semantics/statement scope. No defensible whole-project completion date or production-readiness claim follows from fixture success.

## Resume without launching

Use the final development-branch HEAD and the source-bound matrix/evidence. Do not repeat completed recovery implementation or unrelated compiler matrices. Focus the next batch on the remaining full-ITCH codec/seed/framer contract. Developer tests only:

```bash
ctest --test-dir <native-build> --output-on-failure -j 4
PYTHONPATH=<native-build>/python:. <venv>/bin/python terminal/tests/run_no_launch_suite.py
PYTHONPATH=<native-build>/python:. <venv>/bin/python terminal/tests/check_trade_contract.py
```

Use the existing supported sanitizer preload/CMake harness. No application/server/provider/account/order/workflow/deployment or owner acceptance operation was performed. Current artifacts and failure receipts are in EVIDENCE.json and PACKAGE_CURRENT.json. Keep main/release/Sprint4 refs unchanged.
