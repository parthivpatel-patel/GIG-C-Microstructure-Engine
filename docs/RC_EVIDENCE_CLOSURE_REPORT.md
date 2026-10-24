# Private synthetic candidate: evidence closure assessment

Reviewed **October 23, 2026 (America/New_York)**. Start:
`9171f4ecdaf638e2a1ff3b5bf1645be33f277b67`, clean, local/remote equal on
`feat/bootstrap-cpp20-engine`. Main remained
`165c5038336887116d69160b0d8e5a1a5ef59d16`.

**Decision: GO for bounded private synthetic evaluation; formal candidate closure
BLOCKED.** RC13, RC16, RC17 all have stronger evidence, but none is converted to PASS.
No new engine functionality, market data, live connection, main merge, tag,
distribution or release was introduced. Source/hash evidence does not certify
exchange reconstruction, production operations or research efficacy.

## Prioritized gate results

| Gate | Result | Verified improvement / unresolved evidence |
|---|---|---|
| RC17 hosted CI | **BLOCKED** | Actual Ubuntu zlib/header minimum mismatch reproduced and repaired with an executed official checksum-pinned private prefix. Workflow now requires exact per-row test counts and canonical identities. API fails at proxy CONNECT403, before GitHub; no run ID, job conclusion or hosted log available. Auth/settings/execution remain unknown. |
| RC16 security | **BLOCKED** | Dated actual runtime/component inventory, official CPython/Expat/zlib fixes, source hashes, Ubuntu vendor backports and path-specific applicability recorded. Newer upstream fixes and open/nonpublic Expat reports exist; comprehensive platform/provider/backport mapping remains unknown. No empty-feed clearance or unnecessary upgrade. |
| RC13 fresh reproduction | **BLOCKED under existing independent-machine definition** | Fresh official Ubuntu24.04 rootfs/toolchain/source export passed six configurations, installed consumers, independent synthetic oracle/demos and measured memory. Separate PID/mount namespaces; host compiler/build/library directories not supplied. Kernel/daemon remain shared. No independent VM/hardware/hosted-run attestation exists. |

The full reconciled [RC01–RC27 matrix](P1J_RELEASE_CANDIDATE_MATRIX.md) remains
**18 PASS,6 BLOCKED,2 NOT RUN,1 OUT OF SCOPE,zero retained candidate-scope FAIL**.
RC21 distribution,RC24 observed initialization andRC25 observed reference remain
blocked;RC18 platforms andRC23 observed artifact remain not run;RC27 production
operations is excluded. No gate definition was silently relaxed.

## Confirmed repair and qualification history

1. **Runner dependency mismatch.** `CMakeLists.txt:103–108` requires optional
   zlib>=1.3.1; freshly installed Ubuntu24.04 `zlib1g-dev` reports header/runtime1.3.
   Baseline `cmake --preset release` fails (exit1), before any engine test. The
   previous workflow's distro-only recipe cannot meet this verified minimum.
   Commit `108b423d1576ebae28d7a81598ee2ef1dbfe3a4a` adds
   `scripts/build_ci_zlib.sh` and workflow wiring. It retrieves official1.3.1,
   verifies SHA256 before extraction/build, installs into a new private prefix,
   refuses overwrite, and checks header/runtime1.3.1. Both online/offline builds
   and subsequent engine configure succeeded. Missing/relative/device input,
   existing-prefix and wrong-checksum controls reject. An initial private draft
   assumed Make in a Ninja-only image; explicit Ninja repaired it before commit.
   No system library replacement or lower minimum.
2. **Archive test provenance assumption.** Preliminary fresh GCC Release ran
   **124/125 pass,1 fail**, at `InterfaceTests.test_manifest_export_integrity_and_failure`.
   Baseline `tests/test_python.py:145` invokes `git rev-parse HEAD` although the
   verified clean source archive intentionally has no`.git` (Git exit128).
   Commit `5349789edfc198f5bf74438cf412e403cef14fa9` changes only the test harness:
   checkout provenance still uses actual Git; archive tests require explicit
   `GIG_TEST_SOURCE_COMMIT` from an independently verified source manifest, validate
   full lowercase40-hex, reject disagreement with a checkout, hash source bytes,
   and conservatively label archive checkout cleanliness dirty/unknown. No fake
   commit default or skip. New regression covers missing/malformed/conflicting
   identities and independent expected source digest. Both focused checkout
   controls and all8 archive interface tests pass. Production export/schema
   behavior is unchanged. Callers must authenticate the archive separately; an
   environment string is not authentication.
3. **Fresh minimal Clang runtime dependency.** Five rows passed; the initial sixth
   configured but failed linking missing `libclang_rt.asan*` archives, before CTest.
   Installed signed distro `libclang-rt-18-dev`1:18.1.3-1ubuntu1. A new sanitizer
   binary directory then passed122/122. Preserve failed link logs; this is a
   bootstrap prerequisite, not an engine or sanitizer defect. No flag suppression
   or source change was needed, and successful prior rows were not repeated.
4. **CI execution evidence checks.** Commit
   `9f9f488048df3a5f81aac0671e171cc4f3a5c4b3` strengthens summary checks to require122 native/125 GCC Python Release
   outcomes and all three Python case names, not merely a lower bound. Positive
   native/Python JUnit controls pass; missing-Python/wrong-canonical controls reject.
   These are executed local summary tests, **not a hosted success claim**.

No confirmed new critical/high synthetic engine defect remains from this closure
work. Preserved institutional audit and remediation history were not rewritten.

## Actual final validation

Fresh qualification source archive is
`5349789edfc198f5bf74438cf412e403cef14fa9`, SHA256
`5045243c2cb32b4b490f23f5d207a1d9a0da6e71907637805befab4a6974ed35`.
The subsequent CI count check is separately exercised against final JUnit; later
changes are documentation/evidence only. No bit-identical build claim is made.

| New fresh configuration | Executed CTest result |
|---|---|
| GCC13.3 Debug |122/122 PASS |
| GCC13.3 Release,PythonON |125/125 PASS |
| GCC13.3 ASan+UBSan |122/122 PASS |
| Clang18.1.3 Debug |122/122 PASS |
| Clang18.1.3 Release |122/122 PASS |
| Clang18.1.3 ASan+UBSan after runtime restoration |122/122 PASS |
| **Total** |**735/735; zero failed/skipped/disabled** |

All five P1E–P1I independent canonical hashes match the original evidence in every
new row. Each CTest case may contain many assertions/oracle checks;735 is the
CTest outcome count, not an assertion count. Existing replay, atomicity,
allocation-failure, streaming corruption/resource and numeric controls execute
inside this suite. New source/archive test unit counts increase interface7→8;
export remains6.

Additional actual checks, counted separately:

- Focused checkout `python.research_interface` passes1/1 in each existing Python
  Debug,Release,ASan+UBSan configuration (8 unit cases within each). No native
  rebuild or original nine-row rerun was necessary for a Python test-only repair.
- Retained Debian/GCC14 wheel installed in a new Ubuntu venv:8 interface+6 export
  cases, example and installed-path checks pass.
- New source distribution→Ubuntu/GCC13 wheel, separately installed new venv:
  same8+6 cases, example and installed-path checks pass. **28 installed unit cases
  total**, not folded into735. No build-tree Python import.
- Both examples retain SHA256
  `c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9`.
- Historical P1I and P1J evidence reverified against recorded Git blobs and raw
  files. Each original1108-outcome record remains intact; those full matrices were
  **not** newly executed.63 protected include/src/python/schema/CMake files match
  starting9171 bytes; protected manifestSHA
  `7a99d9372e9155ebd96cc9a656eae59d33e5cd16729eed01e9c78c6f39d71f8b`.
- Four direct fresh demo artifacts retained: valid18 accepted/7native/11external
  with publication eligible; bounded8 accepted and explicitly incomplete;
  restart reproduces full accepted-prefix digest; corrupt source denies publication
  despite a provisional accepted18-record semantic prefix. All are synthetic.

## Fresh-environment and memory evidence

Official Ubuntu image digest:
`sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac`.
Ubuntu24.04.5,CPython3.12.3-1ubuntu0.17,CMake3.28.3,Ninja1.11.1,
GCC13.3.0-6ubuntu2~24.04.1,Clang18.1.3-1ubuntu1,
libstdc++14.2.0-4ubuntu2~24.04.1,glibc2.39-0ubuntu8.9.
Exact versions, commands, image/container identities, source/wheel hashes,
log/JUnit SHA256 and sanitizer/runtime dependency restoration are retained in
[RC_CLOSURE_EVIDENCE.json](RC_CLOSURE_EVIDENCE.json).

Container budget:3GiB,2CPUs,512PIDs; default bridge,not privileged. Source archives/verified inputs were mounted readonly; extracted source and new
build directories are writable inside the rootfs, with results separately mounted
writable. The public CA bundle was mounted readonly.
Compiler/runtime libraries came from signed Ubuntu packages and verified official
zlib source, not host builds. Different PID/mount namespaces were observed, but
kernel6.18.55/daemon28.4.0 are shared with the original environment. This is stronger
than a second build directory, weaker than the existing independent-machine gate.

Sequential probes after compilation/package work stopped:

| Quantity | GCC fresh | Clang fresh |
|---|---:|---:|
| Peak externally wait-accounted process RSS,bytes |78,487,552 |78,630,912 |
| Peak tracked PMR,bytes |77,281,358 |77,281,358 |
| Query allocation failures reached and validated |45 |45 |
| Live tracked bytes after destruction |0 |0 |

Profile:two 128-live-order books,one active price level/book,1024 retained journal
entries/book,128MiB shared PMR. Restart original+replayed state coexistence is
included. Allocation count2757; journal entry remains15,944 bytes, element storage
32,653,312 bytes for2048 entries. Reduced16MiB PMR stops at515 accepted/516framed,
native512;1023-entry cap stops at2049accepted/2050framed,native2046 with
`journal.records`, without silent eviction. No journal redesign occurred.

RSS includes runtime/allocator overhead and may include inherited pre-exec floor;
PMR excludes fixed objects,fixture/output buffers and other allocations. No
all-maxima/many-price-level or whole-market guarantee follows. The container-wide
peak reached its3,221,225,472-byte cgroup cap during compilation/package/cache
activity,with2401 `max` events and **zero OOM/kill events**. Do not confuse that
bootstrap/test-process/cache pressure with the~78.6MB engine probe or claim that
an entire build needs only the probe RSS. After qualification,free disk was26,165,731,328 bytes (~26.2GB).
No new throughput optimization/performance SLA was claimed; historical qualified
batch measurements remain scoped to their original fixture/host.

## Private manifest and instructions

[PRIVATE_SYNTHETIC_CANDIDATE_MANIFEST.json](PRIVATE_SYNTHETIC_CANDIDATE_MANIFEST.json)
records supported exact environments, source/old-wheel/new-wheel identities,
protected implementation digest, qualified outputs and limitations. New artifacts
are private under`build/rc-closure/artifacts/`; official dependency/raw logs remain
ignored under`build/rc-closure/`,not committed or redistributed.
[RC_CANDIDATE_EVALUATION.md](RC_CANDIDATE_EVALUATION.md) gives reproduction steps.
Manifest/byte consistency is not execution attestation or a publisher signature.

## Bounded NASDAQ next experiment

No market URL was requested or raw bytes downloaded. The existing
[NASDAQ pilot plan](NASDAQ_REAL_DATA_PILOT_PLAN.md) is reviewed with a smaller
explicit first experiment:separately authorized4KiB compressed prefix from byte0 of
`https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/12302019.NASDAQ_ITCH50.gz`.
Prior reported full length3,524,013,057 bytes is not reverified here. Any later
expansion requires declared authorization,maximum1MiB cumulative compressed,
32MiB decompressed,4096frames,64KiB buffers,128MiB PMR/256MiB proposed native RSS,
64MiB private free-disk preflight and30s wall time. Capture extents/validators/SHA256,
format inventory/partial bytes/stops; incomplete gzip cannot pass full CRC/identity.
Rights,private cloud retention and output handling need explicit owner disposition;
raw redistribution is not inferred. No observed initializer or empirical reference
exists. Licensing support does not authorize acquisition in this assignment.

## Delivery and owner actions

Code/test checkpoints above are logical commits on the feature branch; the final
closure evidence/documentation commit and exact remote SHA are reported on delivery.
No reset,rebase,force-push,main merge,tag or release occurred.
[RC_OWNER_ACTIONS.md](RC_OWNER_ACTIONS.md) specifies:

1. Publish supported `api.github.com` access or supply authorized exact-SHA Actions
   run/job/JUnit artifacts; then resolve any remaining Actions-read permissions.
2. Obtain provider/vendor security applicability/patch mapping or explicit scoped
   disposition for unresolved runtime/platform components.
3. Supply authorized independent machine/runner bootstrap evidence; a hosted run
   can contribute only if its actual restoration evidence meets RC13.
4. Separately decide distribution and any bounded market acquisition; neither is
   granted by this private manifest.

November5 is13 calendar days away;November12 is20. Synthetic implementation is
available now for scoped private inspection. Formal closure depends on external
access/provider/independent-runner turnaround,so the date is **conditional,not a
verified commitment**. No new engine phase is needed merely to close these gates;
observed-market and publication requirements remain separate.

## Complete changed-file inventory for this closure

- `.github/workflows/ci.yml`:private zlib prefix,exact counts/case/hash evidence checks.
- `scripts/build_ci_zlib.sh`:bounded official checksum-pinned dependency recipe.
- `tests/test_python.py`:explicit archive test provenance and regression.
- `docs/RC_EVIDENCE_CLOSURE_REPORT.md`:this assessment,tests,failure history,bounds.
- `docs/RC_CLOSURE_EVIDENCE.json`:actual outcomes,versions,commands,raw identities.
- `docs/RC_SECURITY_APPLICABILITY.md`:dated component/advisory applicability.
- `docs/RC_OWNER_ACTIONS.md`:precise external closure actions.
- `docs/RC_CANDIDATE_EVALUATION.md`:private reproducible evaluation instructions.
- `docs/PRIVATE_SYNTHETIC_CANDIDATE_MANIFEST.json`:scoped private artifact manifest.
- `docs/P1J_RELEASE_CANDIDATE_MATRIX.md`:updated evidence,unchanged strict decisions.
- `docs/P1J_SECURITY_DEPENDENCY_REVIEW.md`:historical review preserved,later addendum.
- `docs/REPRODUCIBILITY.md`:historical/current count corrections,archive/zlib guidance.
- `docs/NASDAQ_REAL_DATA_PILOT_PLAN.md`:reviewed bounded proposal,no acquisition.
- `docs/OVERNIGHT_ENGINEERING_PROGRESS.md`:durable closure checkpoint,next owner action.
