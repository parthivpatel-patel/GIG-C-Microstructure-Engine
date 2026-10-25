# Current-HEAD native ARM64 qualification readiness

Phase2 checkpoint: prior qualified sourcef02363e, historical run40126420107; local baseline
c9df510a7f4c926715a8b0a8d0c1350cca33d85a (later phases require their own final gates).

**The previous native ARM64 qualification applies to the previously tested commit.
Current HEAD remains pending a new hosted qualification run.**

The existing native-arm64.yml still has workflow_dispatch only, default-false
free_usage_verified, feature-ref guard, contents:read, standard ubuntu-24.04-arm,
GCC/Clang ×Debug/Release/ASan+UBSan,60-minute job ceiling,180-second probe timeout,
Debug -g -O1 sanitizer flags with assertions and full instrumentation. Checkout is
immutable official Node24 v6.1.0 SHA d23441a48e516b6c34aea4fa41551a30e30af803,
persist-credentials:false. No owner gate or free-runner label/control was changed.
No artifact upload job/retention cost is introduced; logs expire under repository
policy and must be exported by owner. No signed-in artifacts are fabricated.

Before owner dispatch: verify current public standard runner eligibility/free
policy and exact feature SHA, review local evidence and updated action. In Actions,
select Native ARM64 qualification (owner-gated), Run workflow, choose
feat/bootstrap-cpp20-engine, enable free_usage_verified only after cost eligibility
verification, then owner may explicitly launch. This procedure was NOT executed.
Do not select main; branch guard skips it. No new main registration is needed.

Configured strict CTest counts remain154 native and157 GCC Release with Python,
all8 exact canonical checks, zero failed/skipped/disabled outcomes, installed wheels,
source archive/inventory and diagnostic controls. New test coverage is folded into
existing cases without changing golden identities. Current local comprehensive
matrix/packaging/security results are bound in the evidence manifest; later source
changes cannot inherit that statement without their relevant final validation.

Executed local gate:1396/1396 outcomes across9 configurations, zero failures/skips/
disabled;all8 hashes match.14 existing installed-interface/export checks and2
fault checks,10 security receipt controls and3 packaging controls pass. No native
engine/ABI change since the installed wheel was built; reuse is explicit.

## Final program source checkpoint

Feature source checkpoint75246ea7c4cd86ecfc11d254e2cec285352055b8 adds the
bounded adapter and independent byte-level differential validation. Final local
matrix1396/1396 across nine configurations passed, zero failed/skipped/disabled;
all eight hashes preserved and supplemental164 schedules/2228 prefixes agree in
every configuration. Fresh checkout/source-built wheels passed28 installed checks,
4 fault controls;358-member source archive verified. Evidence:
`evidence/order_book_validation_results.json`. The earlier paragraph's wheel reuse
applies only to Phase2, superseded here by fresh builds.

Ready for separately owner-authorized current-HEAD native qualification; NOT native
qualified yet. Report-only delivery commit does not change tested source. No workflow
was launched or control changed. Provider security, authenticated raw hosted archive,
observed initialization/L3 and production gates remain partial/blocked as described
in `VALIDATION_AND_MARKET_READINESS_REPORT.md`. No extra test run is inferred from
this documentation update.

## Observed-market program source qualification boundary

Run4 qualifies7fca902bac36e30befd657d2bb4e35fa92ec5a5f; owner6/6 and official
summary success independently verified, full archival remains partial. New typed
seed/adapter/comparison code atb06a417 and evidence closure8a80ffc pass final local
1396 CTest +108 focused diagnostic outcomes, all8 identities; new supplemental seed
receipts match across9 candidates. New source is ready for separately owner-approved
six-job ARM qualification, **not already native-qualified**. Workflow/manual/free
usage/feature guard unchanged. See OBSERVED_MARKET_ENGINEERING_REPORT.md for exact
hashes, package binding, observed gates and owner procedure. No run launched here.
