# Phase 12 private synthetic release-candidate assessment

October24,2026 — America/Los_Angeles. **Private bounded synthetic evaluation GO;
formal candidate closure BLOCKED.** Phases7–12 were pursued through all available
authorized work. New evidence includes an actual AArch64 cross build,154 distinct
emulated C++ test passes, eight cross-architecture canonical matches, current
dependency applicability sources and18 controlled native measurement processes.
No production defect was reproduced and no engine/API/schema/warning-policy patch
was needed. No release, merge, paid machine or market-data acquisition occurred.

## Source and phase completion

Frozen candidate: **ea2df47597fecb446013c902d2a74be4644ffdc0**. All production,
test, build, Python, fixture, schema and benchmark source equals Phase6's tested
195cb11431bda150e28a1232bc4c8c735769d81d; exact Git diff confirmed equivalence.
All commits in this extended session change documentation only. Main remains
165c5038336887116d69160b0d8e5a1a5ef59d16. Source export/ELF/wrapper/JUnit identity
and checks are in the structured companion evidence; raw files remain privately
under build/extended/evidence. No binaries/raw market bytes are committed.

| Phase | Completed work | Remaining boundary |
|---|---|---|
|7 hosted CI |Owner observations preserved, one bounded API attempt, exact artifact/PR-source/warning export instructions |Run IDs/SHAs/logs/6 warnings independently unavailable; RC17 BLOCKED|
|8 independent Linux |Availability investigated, exact fresh-source/compiler/Python/package/resource recipe |No genuinely independent executor; RC13 BLOCKED|
|9 ARM64 |Strict GCC13 AArch64 Release cross-build, actual QEMU execution, ABI/source/integrity checks,154 distinct cases and8 equal hashes |Native hardware, ARM Python, target sanitizers/Debug NOT RUN; RC18 PARTIAL|
|10 security |Actual versions,7 upstream/CNA sources,12 PyPI metadata endpoints, selected vendor backports/path applicability |Provider/OpenSSL/CPython/Expat and wider vendor mapping unresolved; RC16 BLOCKED|
|11 audit/performance |Journal/replay/streaming/C++/Python review,12 native workload runs+6 journal runs, independent formulas |Finite synthetic review, no newly reproduced defect or causal optimization claim|
|12 readiness |All27 gates assessed separately, source reproducibility procedure and owner actions |Formal/observed/production boundaries not closed by local evidence|

See PHASE7_HOSTED_CI_EVIDENCE.md, PHASE8_INDEPENDENT_REPRODUCTION.md,
PHASE9_ARM64_PORTABILITY.md, PHASE10_SECURITY_APPLICABILITY.md,
PHASE11_RELIABILITY_AUDIT.md and PHASE12_RELEASE_CANDIDATE_MATRIX.md.

## Hosted observations versus independently verified evidence

Owner reports #129 PR workflow success, six green jobs, ~4m29s and six warnings;
#128 commit workflow also success. These reports are retained as owner evidence.
They do not identify API run IDs or authenticate exact candidate/PR merge source.
One `gh api` request returned exit1/Forbidden. No blocked retry or bypass. Actual
compiler/image/dependency versions, CTest counts and warning annotations remain
unavailable from those runs. Local tests and successful pushes are not substituted.
PR head, base, merge and checkout-resolved SHA must be compared before closing RC17.

## New cross/emulated qualification

Official Ubuntu cross GCC13.3, target glibc2.39/libstdc++14.2 and QEMU8.2.2 were
installed only as tools in the existing x86_64 Ubuntu qualification container:
27 additions,0 package upgrades. Existing authenticated zlib1.3.1 source SHA256
17e88863f3600672ab49182f217281b6fc4d3c762bde361935e436a95214d05c was reused.
AArch64 zlib header/runtime both report1.3.1. All source files match the frozen
candidate Git archive. No binfmt registration, privileged guest, remote machine
or new candidate dependency.

The engine cross-build completed115 steps under -O3 -DNDEBUG -Werror. Machine183
ELFs are preserved and individually hashed; private wrappers invoke qemu-aarch64
with the target sysroot. Host Python independent oracles call those target programs;
this is **not ARM Python extension execution**.

Initial full run:153 passed, one L3 oracle timed out at a qualification-only180s.
A targeted unchanged900s retry passed in578.83s with10032 sessions/65186 source
candidates. Across those two runs all **154 distinct tests** pass; no assertions,
case counts or canonical requirements were reduced. The initial timeout remains
in evidence. Do not describe it as an initially clean154/154 run. No emulated
throughput is used as native ARM performance evidence.

ABI: pointer8,long8,long double16,journal record12232,DecodedRecord304 bytes on
both hosts. Plain char signedness differs (x86 signed, AArch64 unsigned), as does
long-double precision (64 versus113 bits). All eight integer/canonical contracts
still agree. Byte order is explicit and object padding is not serialized. Display
floating-point formats and binary files are not assumed identical across ISAs.

## Reused versus newly executed validation

| Evidence | Result / scope |
|---|---|
|Phase6 x86 GCC14/Clang19 Debug/Release/sanitizers; Python D/R/sanitizers |1396 outcomes retained; unchanged source/dependencies, not rerun or relabeled new|
|Prior GCC13 focus and repair |Preserved; no new full GCC13 x86 run claimed|
|New AArch64 GCC13 Release via QEMU |154 distinct passes;153 initial+1 targeted retry; no remaining failures/skips|
|New canonical agreement |All8 hashes match x86; full independent L3 oracle completes|
|Previous package/installed consumers |28 installed-wheel checks/3 packaging regressions remain source-equivalent evidence; no new ARM wheel|
|New native resource/performance profiles |12 workload runs+6 journal processes, independent numeric/quantile/count checks|
|Final source archive |Clean fixed-epoch duplicate sdist builds/inventory bound after final documentation push in local final-delivery.json|

No unchanged expensive native matrix was repeated merely to add counts. Source
packaging must be freshly inventoried for the new documentation; old sdist hashes
are not reused as identities of the final archive. No arbitrary third-party
archive/XML security clearance is inferred.

## Security applicability and restrictions

Fresh authoritative OpenSSL NEWS confirms3.5.9 Sep29 security fixes after managed
Python's3.5.8. Managed CPython3.12.14/Expat2.8.3 likewise precede recorded later
security fixes. Selected non-deployed DTLS/QUIC/CMP/UTF16/untrusted extraction paths
can be excluded only within stated scope; normal HTTPS/provider/crypto and wider
backports remain unresolved. No exploitable engine issue was reproduced and no
managed runtime was silently replaced. GCC security/Ubuntu notices access failed;
source unavailability is not security clearance. All12 version-specific PyPI
responses list zero advisories, a limited feed result only.

Native zlib CNA explicitly excludes core compression from contrib/untgz overflow;
engine does not deploy untgz/minizip or call Copy/combine APIs addressed by selected
later fixes. This scoped exclusion does not clear all dependencies. QEMU/cross
tools execute only authenticated local ELFs and synthetic inputs, not hostile
binaries. Provider patch identities or a supported patched/qualified runtime remain
required for formal security closure.

## Performance and memory observations

All new performance samples are native x86 Release. One QEMU L3 qualification job
was concurrently active; no CPU isolation, compiler ranking or causal speedup is
claimed. Raw distributions and warmup/repetition scopes are retained. Pure decode
includes clock reads; batch tools include declared create/process/validate/destroy
stages rather than isolated journal latency.

| Workload | GCC | Clang |
|---|---:|---:|
|Pure decode20k calls p50 /p99 ns |107 /150|77 /100|
|Framing/decode32768 median ns/record |99.6295|85.0884|
|Context256 median ns/record |764.079|362.433|
|Reconstruction128 records/s |92,757.2|105,195|
|Reconstruction192 records/s |82,952.6|96,047.3|
|Streaming192/chunk31 records/s |74,916.8|80,924.5|

The128 reconstruction anchor exactly matches Phase5 fixture/checksum/receipt and
16,070,960-byte peak PMR. New192 reconstruction/streaming peaks25,670,920 /
25,714,088 bytes in both compilers; all tracked storage released. These scales do
not imply a real-market capacity or exchange SLA.

Journal6144/reset17:361 resets, record capacity6144, plan capacity512, live PMR
77,058,464, peak126,208,416 and386 allocations, same both compilers. Three measured
processes/compiler follow a warmup. Median elapsed95,847,403ns GCC /105,484,923ns
Clang, with no claim that a compiler or implementation became faster. Current
physical record12232 versus logical DTO15944; metadata/snapshot overhead, geometric
reserve coexistence and resource caps remain substantial. Phase5/6 historical
before/after/scaling evidence is preserved. No new optimization justified changing
those verified contracts.

## Readiness, dates and exact next steps

Current27 gates:18 scoped PASS,7 BLOCKED,1 PARTIAL,1 OUT OF SCOPE. RC18 advances
only to cross/emulated partial evidence. Distinct conclusions:

1. Private synthetic evaluation: GO within tested Linux/profile/resource scope.
2. Formal candidate closure: BLOCKED by independently bound hosted/machine,
   security/provider and owner/distribution evidence.
3. Historical ITCH decoding: retained-profile synthetic support plus prior bounded
   S/R/H/Y observations, not complete2019 compatibility.
4. Observed L3: NO-GO without authenticated complete capture/initial state,
   observed integration and independent aligned book/queue reference.
5. Production trading: OUT OF SCOPE; no readiness claim.

November5 is12 calendar days from October24; November12 contingency19. Local
synthetic evaluation is defensible now. No guaranteed formal closure date can be
claimed while external turnaround remains unknown. PHASE12_OWNER_ACTIONS.md
prioritizes exact-SHA CI exports and warning triage, independent runner, provider
patch applicability and native ARM/Python qualification or explicit scoped deferral.
Any market-data acquisition or observed adapter phase needs new explicit scope;
no such work starts automatically after this report.

## Git inventory and preservation

Pushed checkpoints:
3471bde351a7630928a2a9e8f04c023c7a468e6b (phase7),
000c253c54b4f445a8ea95d2bfc15f697a327df9 (phase8),
a6664d21c363abc178513193b63eabc8e207bd27 (phase9 partial checkpoint),
931538e640654b472481edfa50ecd2fa13531883 (phase10),
426d9925d7193436dae078cda9d8e087c4cb1def (phase9 completed evidence/phase11).
Each milestone push and remote was verified; final documentation HEAD/clean tree/
unchanged main are bound after push in build/extended/evidence/final-delivery.json
and final response, avoiding a self-referential Git hash in this report.

Changed files are only docs/PHASE7_HOSTED_CI_EVIDENCE.md,
docs/PHASE8_INDEPENDENT_REPRODUCTION.md, docs/PHASE9_ARM64_PORTABILITY.md,
docs/PHASE10_SECURITY_APPLICABILITY.md, docs/PHASE11_RELIABILITY_AUDIT.md,
docs/PHASE12_RELEASE_CANDIDATE_REPORT.md, docs/PHASE12_RELEASE_CANDIDATE_MATRIX.md,
docs/PHASE12_OWNER_ACTIONS.md, docs/PHASE12_ENGINEERING_EVIDENCE.json and
docs/EXTENDED_ENGINEERING_PROGRESS.md. Prior audits/history preserved. No engine,
matcher/TCA, Python API, workflow, dependency lock or GIG Quant Terminal changes.
No merge/tag/release, data download, LOBSTER retry, broker/live or paid resource.

All available authorized phases are assessed. External/untested gates remain
explicitly blocked/partial. Resume from EXTENDED_ENGINEERING_PROGRESS.md and the
final delivery record; do not restart completed matrices or claim execution continues
after Codex stops.
