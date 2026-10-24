# Native Linux ARM64 qualification — closed

October 24, 2026 (America/New_York). **Milestone CLOSED for the bounded synthetic
engine at `f02363e0e09b9767b4dc6748737206254e5e4c6a`.** This closes the six-configuration
native ARM64 engineering qualification, not formal release, observed-market L3
validation or production trading readiness.

## Independent verification

Official GitHub [run 40126420107, workflow run #3](https://github.com/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/runs/40126420107)
is **Success**, feature branch `feat/bootstrap-cpp20-engine`, exact full commit
hyperlink above, total duration **7m 22s**. These facts and each individual job's
`succeeded` state were independently retrieved via bounded HTTPS GETs of the
public GitHub summary and six job pages, not inferred solely from the owner's
message. Public page metadata identifies this repository as public.

| Configuration | Job ID | Conclusion | Whole-job duration |
|---|---:|---|---:|
| GCC Debug |120968725499|Success|1m 31s|
| GCC Release |120968725573|Success|4m 36s|
| GCC ASan+UBSan |120968725538|Success|7m 16s|
| Clang Debug |120968725587|Success|1m 32s|
| Clang Release |120968725484|Success|2m 32s|
| Clang ASan+UBSan |120968725390|Success|2m 27s|

The public `check-step` attributes bind step log paths to the full commit and
independently show `Authenticate fresh native runner and source`, `Configure`,
`Build` and `Test` succeeded in every job. GCC Release's private-wheel,
duplicate-source-archive/integrity, and source-built-wheel consumer steps also
succeeded. Conditional packaging steps skipped in other jobs are expected;
CTest's zero-skipped requirement remains mandatory in all six jobs.

The tested workflow uses standard GitHub-hosted `ubuntu-24.04-arm`, asserts
`runner.arch == ARM64` and `uname -m == aarch64`, and checks exact clean source.
Successful architecture-authentication steps support genuine native hosted ARM64
qualification under GitHub's runner trust model; no QEMU or cross compiler is
configured. Raw uname/CPU/image/compiler/dependency output is not independently
exported, and this is not hardware attestation. Public standard ARM runner
eligibility is supported by the previously recorded official GitHub runner and
billing documentation; no new infrastructure or execution was requested here.

A single normal `gh run view 40126420107 --json databaseId,headSha,event,status,conclusion,jobs,url` failed with API Forbidden.
The public GitHub website was read normally over the inherited proxy/TLS trust;
no API/proxy/credential bypass, mirror or configuration change. The public pages
say sign in to view logs. No raw step log/JUnit download is claimed. Sanitized
facts, step metadata, URLs and HTML SHA256 receipts are in
[NATIVE_ARM64_QUALIFICATION_EVIDENCE.json](NATIVE_ARM64_QUALIFICATION_EVIDENCE.json).
Raw public pages remain private in build/arm64-closure/evidence; dynamic page
nonces/live-update tokens are not committed.

## What the successful workflow establishes

The frozen f02363e workflow is inspected and its blob hash recorded. It requires:

- Six GCC/Clang Debug, Release and combined ASan+UBSan builds; strict warnings and
  fatal sanitizer errors. Native sanitizer jobs use Debug `-g -O1`, assertions
  and frame pointers retained, without NDEBUG or sanitizer exclusions.
- 154 CTest outcomes in each of five C++ configurations; 157 in GCC Release with
  Python: **927 configured outcomes**. Zero failed/skipped/disabled cases required.
- Exact comparison of all eight canonical SHA256 identities; independent replay,
  source accounting, numeric and frozen-journal regressions remain enabled.
- GCC Release Python bindings, installed interface/export/example checks, private
  checkout and source-built wheels, byte-identical fixed-epoch sdists and safe
  source inventory.
- Full-capacity replay/resource/failure checks in the bounded sanitizer allocation
  profile, diagnostic regressions and complete phase output retention.

The success of those steps verifies the workflow-enforced gates. **927 is the
configured required count, not a separately parsed hosted JUnit total.** Likewise,
all eight checks are enforced by successful Test steps, but raw emitted digest
strings and per-test results have not been independently exported. The previous
local 1704-outcome/11-configuration and 88-focus evidence remains separate in
NATIVE_ARM64_RUN2_EVIDENCE.json; none was rerun or relabeled as hosted evidence.
ARM Python Debug and Python sanitizer configurations were not added by this run.

The public step timestamps show GCC sanitizer Test took about **330 seconds**
and Clang sanitizer Test **34 seconds** (second-resolution metadata; includes
four diagnostic controls, CTest and result/hash verification). Whole-job durations
above include build/setup; 7m22 is whole workflow walltime. These are distinct
measurement scopes. No per-probe timing, peak RSS or causal speedup is inferred.
Both earlier failures are closed at this tested commit by actual successful
native sanitizer jobs. The 180-second probe and 60-minute job ceilings remain.

## Warnings and remaining risk

Six public annotations repeat one maintenance issue: pinned checkout v4.2.2
(action SHA 11bd71901bbe5b1630ceea73d27597364c9af683) targets deprecated Node20;
GitHub reports forcing Node24. No compiler warning, sanitizer defect or engine
failure is inferred from this annotation. A separate authorized, SHA-pinned
checkout action/runtime update and regression check is recommended; this
assignment changes documentation only and does not suppress warnings.

Journal/resource budgets, 12,232-byte ordinary records, incomplete-session handling,
restart-from-boundary limitations and lack of crash durability remain material
engineering constraints. No full-day market capacity, tail-latency SLA or allocator
fragmentation qualification follows from this functional native run.

Current gate overlay, superseding historical ARM-unverified claims:

| Gate | Current scope/status | Remaining boundary |
|---|---|---|
| RC18 platforms |PASS scoped: native Linux ARM64 six-job milestone|Windows/macOS/other Python ABIs and ARM Python sanitizers unqualified|
| RC13 independent reproduction |PARTIAL: fresh actual external GitHub ARM execution now verified|Archive exact OS/compiler/dependency, source/package/JUnit/hash receipts for full independently repeatable evidence bundle|
| RC17 hosted CI evidence |PARTIAL: this exact-SHA native ARM run independently verified|Detailed logs/warnings/artifacts and older x86 CI evidence closure remain separate|
| RC16 security |BLOCKED|Provider/OpenSSL/CPython/Expat/vendor applicability and dependency qualification remain|
| RC21 distribution |BLOCKED|No release/distribution authorization inferred|
| RC23–25 observed data |BLOCKED|No full authenticated artifact/profile, valid complete initial L3 state or independent observed reference|
| RC27 production |OUT OF SCOPE|No crash durability/HA/live/exchange or operational certification|

Retaining the other Phase12 scoped decisions yields **19 scoped PASS, 5 BLOCKED,
2 PARTIAL, 1 OUT OF SCOPE**. Historical source-bound reports remain intact; this
is not a claim that all production source still equals the old ea2df475 baseline.
The arithmetic/sanitizer repairs and newer local/hosted evidence are explicit.

Private bounded synthetic research evaluation: **GO** on the qualified Linux
x86/ARM scopes. Native ARM milestone: **CLOSED**. Formal candidate closure:
**still blocked**. Retained-profile historical format compatibility is not a
validated full-market adapter. Real observed L3 reconstruction: **NO-GO** pending
its separate evidence/authorization. Production trading: **not established**.

## Next milestone and preservation

Recommend **independent reproduction and security evidence closure** before more
engine features: obtain signed-in exports for this existing run (no rerun needed),
archive exact toolchain/dependency/source/JUnit/hash/package identities, resolve
provider security applicability, and separately authorize the pinned checkout
maintenance update. Observed-data acquisition/initial-state/reference validation
must remain a later explicitly authorized milestone; no market data is acquired.

The source/test/workflow requirements and all eight digests are unchanged by this
documentation closure. No tests were rerun unnecessarily, main remains
12f3a53943dc245e36f2cbbc35b9910fb21c0718, and no workflow was launched/cancelled/rerun.
The docs-only commit uses `[skip ci]` to honor the no-additional-workflow instruction;
it does not skip or weaken any qualification test. Final documentation commit and
remote verification are reported after push, avoiding a self-referential hash.
