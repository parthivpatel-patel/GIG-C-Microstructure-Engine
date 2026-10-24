# Current-HEAD native ARM64 qualification readiness

Prior qualified sourcef02363e, historical run40126420107; current local phase baseline
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
