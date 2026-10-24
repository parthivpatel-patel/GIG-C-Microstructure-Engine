# Four-phase engineering program — consolidated report

October24,2026 (America/New_York). **Bounded synthetic research GO. Formal security/
external-artifact closure and observed-market validation remain blocked. Production
trading is not established.** All four engineering phases were pursued sequentially
with separate validated feature-branch commits. Externally missing evidence is not
marked complete. No market-data acquisition, paid resource, workflow dispatch,
main merge, release, live order or Terminal change.

Entry883d91c32f428396f9ee412d07f14a13d14e36c3; qualified native implementation
f02363e0e09b9767b4dc6748737206254e5e4c6a. Main preserved at
12f3a53943dc245e36f2cbbc35b9910fb21c0718. No production engine implementation
changed; new scripts/tests, supply-chain controls and reports preserve all8 hashes.

## Phase delivery and precise status

| Phase | Commit / state | Deliverables and evidence |
|---|---|---|
|1 independent reproduction|b69558af1335bacfb31774cfa77be43457e16c91; clean local reproduction and permitted metadata fallback completed|[INDEPENDENT_REPRODUCTION.md](INDEPENDENT_REPRODUCTION.md), [manifest](evidence/reproduction_manifest.json), new verifier. Fresh Git worktree,119-step build,157/157,8 hashes,28 installed checks. Raw hosted artifact archival BLOCKED.|
|2 security/supply chain|7c5f022d33a2ae09756ead0759648ab453d54f1f; review/hardening delivered, full security qualification PARTIAL/BLOCKED|[SECURITY_QUALIFICATION.md](SECURITY_QUALIFICATION.md), [inventory](evidence/dependency_inventory.json).12 fresh PyPI/digest checks,7 official source receipts, immutable official Node24 checkout/no stored token. Parent-symlink receipt defect fixed. Provider clearance/new action hosted execution missing.|
|3 market readiness|0c5bb96fddc727332bd23687a1558602d6854fa2; synthetic readiness work completed, observed validation BLOCKED|[REAL_MARKET_VALIDATION_READINESS.md](REAL_MARKET_VALIDATION_READINESS.md), [matrix](evidence/itch_validation_matrix.json).255 invalid kinds +2 arbitrary boundary cases;67 independently modelled sessions/476 prefixes;1396 outcomes across9 configs. No observed adapter or false initial state.|
|4 engineering audit|This report's feature-branch commit; exact SHA reported after push|Historical audit preserved byte-for-byte and appended; [15 structured findings](evidence/institutional_audit_findings.json), [readiness matrix](ENGINEERING_READINESS_MATRIX.md).36 measured journal processes +12 warmups;6 installed export fault outcomes; no new critical/high production engine defect established. Larger redesigns deferred.|

For Phase4 exact SHA after delivery: `git log -1 --format=%H -- docs/FOUR_PHASE_ENGINEERING_REPORT.md`.
Its own commit cannot contain its literal hash. Final response supplies all four
SHAs and verifies remote/clean tree; no history rewrite or extra workflow is needed.
All pushes use [skip ci] to honor the no-new-workflow rule, not to skip tests on
changed engine behavior. Existing native qualification remains historical and intact.

## Executed validation

| New execution | Result |
|---|---|
|Clean checkout GCC Release with Python|157/157; zero failures/skips/disabled;8 canonical matches|
|GCC Debug/Release/ASan+UBSan after Phase3 tests|154/154 each|
|Clang Debug/Release/ASan+UBSan after Phase3 tests|154/154 each|
|Python Debug/Release/sanitizers after Phase3 tests|157/157,157/157,158/158|
|Total CTest suite executions above|1553 outcomes (157 fresh +1396 matrix); repeats are not distinct test-case identities|
|Supplemental independent ITCH reference|67 sessions/476 compared prefixes,3 negative controls, each of9 matrix configs; supplemental d0e09ee... digest,8 original identities unchanged|
|Receipt verifier|Phase1 six controls; Phase2 parent/leaf extension: before1/8 fails, after8/8 pass; current archive verification passes|
|Fresh installed checkout/source-wheel consumers|28 Phase1 +14 final-wheel checks=42;3 examples equal c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9|
|Filesystem error injection|ENOSPC at input fsync/final hard-link,2 tests ×3 installed consumers=6 passed; no actual disk fill/power-loss test|
|Other focused checks|4 diagnostic and3 packaging-pattern controls pass (packaging rerun with documented locked interpreter after an initial missing-dependency harness error); both workflow YAML/permission/pin/trigger/matrix and shell syntax checks pass|
|Memory/benchmark evidence|36 new measured Release journal processes +12 warmups; exact byte/count/cleanup checks;10 benchmark correctness cases in fresh suite|

These are native **x86_64 local** tests. The clean checkout uses the same Codex
physical host; it does not invent an independent machine or human reviewer.
Existing external native **ARM64** run40126420107 independently confirms six actual
job successes atf02363e,7m22s; no new ARM run, new checkout action qualification or
new supplemental test coverage on ARM is claimed. Old cross/QEMU results remain
cross/emulated evidence, not native. Full raw ARM logs/JUnit/tool versions still
need owner export; no authentication bypass or repeated blocked API request.

## Repairs, findings and measurements

Evidence correction: the Phase2 packaging-pattern invocation used the default
interpreter and failed missing scikit_build_core; initial pass wording was
premature. The failed log is preserved; Phase4 explicitly reran the three controls
with /workspace/gig-tools/bin/python and all pass. No tests were suppressed.

Confirmed new repair: Phase1 receipt verifier allowed an internal parent symlink
contrary to its no-symlink policy. A new test failed before repair; Phase2 checks
every component and8 controls pass. No external escape was reproduced. Checkout
Node20 deprecation was a confirmed hosted warning; configuration now pins official
v6.1.0 SHA d23441a48e516b6c34aea4fa41551a30e30af803, uses Node24 and disables
persisted credentials. Source/runtime/license inspected; new action execution not
claimed. Public-visibility/license wording corrected without granting distribution.
No engine API, accepted event, journal/canonical or arithmetic semantics changed.

New audit finds no further reproduced production defect warranting speculative
repair. It identifies explicit observed initialization/reference gaps, incomplete
provider/security and action-bundle applicability, large journal/reserve costs,
bounded64-order snapshot recovery, clone-based synthetic model costs, uncalibrated
analytics, ABI/platform limits and missing crash-durable operations. Each finding
has exact source range/hash, significance, evidence, acceptance, effort and risks.
Old four-defect audit and its subsequent repairs remain preserved, not rewritten.

Journal ordinary records remain12,232 bytes/logical entries15,944. At2048 events,
GCC live/peak PMR is25,051,552/37,577,120 bytes without resets and
25,527,712/37,815,200 at reset interval17. All36 process byte ledgers and zero-live
cleanup checks pass. Raw elapsed distributions are retained, but no exchange SLA,
compiler ranking, full-day volume or whole-allocator fragmentation result is claimed.
No risky storage rewrite was justified or implemented.

Final working-tree wheel additionally passed14 interface/export plus2 fault checks;
its updated third-party notice matches source. Final source archive inventory has
342 safe intended members; source/package digests are in the audit evidence.
These checks do not retroactively qualify new action/test code on ARM.

## Unfinished/external work and owner action

- Full security clearance: provider patch/backport/feature evidence for managed
  OpenSSL/CPython/Expat and wider vendor/kernel/toolchain coverage is missing. Obtain
  supported patched/runtime evidence and qualify updates; do not silently replace TLS.
- Raw independent native archive: owner exports the existing run's signed-in logs,
  JUnit/compiler/dependency/package/hash receipts. Existing public job metadata is
  preserved; missing artifacts are not invented.
- New checkout action: requires separately authorized hosted run, not launched here.
  Declared action dependency ranges are inventoried, not represented as a resolved,
  scanned bundled SBOM or proof of zero vulnerabilities.
- Observed-market L3: separate authorized acquisition, full artifact/profile integrity,
  complete initial context/FIFO state, observed adapter and aligned independent book
  reference. Existing synthetic seed cannot be relabeled observed; no3.5GB download.
- Operational production: crash journal/directory durability/HA/live safety and physical
  fault qualification remain outside research scope. No broker/Terminal changes.

Next highest-value milestone: close provider/security and existing-run evidence,
then explicitly authorize a narrow observed initialization/adapter/reference design.
Journal optimization requires measured bottleneck and equivalence/migration gates.
Do not build dashboards, live trading, broad persistence or institution-specific
features to substitute for missing evidence. No further phase starts automatically.

## Durable artifacts and resumption

Raw receipts under build/four-phase/phase1–4 remain private/ignored; manifest and
structured reports contain checksums rather than raw datasets. Reproduction receipt
verification is executable and was self-tested. Source-dependent artifact archives
are from their recorded working-tree/commit scopes, not relabeled final Git SHAs.
On resume verify branch/remote/status, read this report and preserve all work;
do not restart completed matrices without a source change/failure. Execution ends
with the final report; no background continuation after Codex stops is claimed.
