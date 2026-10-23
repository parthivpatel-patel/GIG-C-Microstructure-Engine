# Reproduce the private research build

Tested host: Linux Debian13 x86_64, GCC14.2, CMake3.31.6, Ninja1.11.1,
CPython3.12.14. Optional Clang19.1.7 uses the system GCC standard library.
No native ARM64 hardware was available: ARM64 is NOT TESTED, not cross-compiled.
Windows/macOS are not tested. No portability claim follows from C++20 alone.

Use the existing development branch and verify `git status --porcelain`,
`git rev-parse HEAD` and `git ls-remote origin refs/heads/feat/bootstrap-cpp20-engine`.
Never reset a dirty checkout or force-push. Clone restoration is not asserted merely
because an environment configuration was saved.

## Native core without Python bindings

```sh
python3 -m venv /workspace/gig-tools
/workspace/gig-tools/bin/pip install cmake==3.31.6 ninja==1.11.1.3
export PATH=/workspace/gig-tools/bin:$PATH
export CXX=g++
cmake --preset debug -DGIG_BUILD_PYTHON=OFF
cmake --build --preset debug
ctest --preset debug --output-junit build/debug/tests.xml
```

Repeat with release and asan-ubsan. With optional streaming and benchmarks enabled,
the P1I/P1J native suite has122 CTest outcomes; Python Debug/Release125 and
GCC Python sanitizer126. Historical P1F had85 native outcomes, including
independent Python arbitrary-precision reference programs; the native library does
not depend on a Python development module or pybind11. Reference scripts require
an interpreter. Explicit CXX avoids inherited SDK compiler settings. For Clang use
an independent binary directory and `-DCMAKE_CXX_COMPILER=/path/to/clang++` at its
first configure, never change compiler inside an existing cache.

Phase 9 used fresh `build/phase9-clean-{debug,release,asan-ubsan}` directories.
Clang was obtained without system installation: Debian trixie signed InRelease /
Packages metadata, installed Debian archive keyring, four matching SHA256 archives
(clang19, common19-dev, cpp19, rt19-dev), extracted under `/workspace/gig-clang/root`.
The compiler wrapper sets its private shared-library path. Package identities and
hashes are archived with final evidence. No unsigned repository or TLS bypass.
This optional workspace installation is not required when Clang is already present.

## Optional Python interface and private wheel

```sh
python -m pip install -r requirements-python.lock
cmake -S . -B build/python-release -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_COMPILER=g++ -DBUILD_TESTING=ON -DGIG_BUILD_BENCHMARKS=ON \
  -DGIG_BUILD_PYTHON=ON -DPython3_EXECUTABLE="$(command -v python)" \
  -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"
cmake --build build/python-release --parallel 2
ctest --test-dir build/python-release --output-on-failure
CXX=g++ python -m build --sdist --wheel --no-isolation --outdir build/private-dist
python -m venv build/private-consumer
build/private-consumer/bin/pip install --constraint requirements-python.lock build/private-dist/*.whl
build/private-consumer/bin/python tests/test_python.py
build/private-consumer/bin/python examples/python_research.py
```

No upload command is authorized. The lock is the tested CPython3.12 Linux toolchain;
other Python versions declared by package metadata need their own compatibility
validation and dependency resolution. Wheels include 14 schemas and third-party
notices. Verify installed module paths to exclude accidental build-tree imports.
Source-distribution build is checked separately. Same canonical semantic results
are required; byte-identical binary wheels are not promised (toolchain/build paths).
For Debug change build type and directory. For GCC Python sanitizer configurations,
add both GIG_ENABLE_ASAN and GIG_ENABLE_UBSAN; CTest invokes the live-interpreter
LSan harness and positive leak control described in PHASE_8_REPORT.md. Native core
checks retain normal exit-time leak detection. Do not apply the Python workaround
to the native tests or infer coverage of late CPython finalization.

## Reproduce evidence

```sh
python scripts/run_engine_baseline.py --build-dir build/phase9-clean-release \
  --output-dir build/reproduced-core
python scripts/benchmark_python.py --help
python scripts/review_dependencies.py --help
```

Run benchmarks sequentially after builds stop, from a clean verified code commit.
Each runner rejects overwrites and records exact source/build/workload hashes.
The core runner reruns the complete suite and numerical preflight. Compare
canonical artifact hashes first, then scoped raw distributions; shared-host timing
changes do not demonstrate optimization. See PHASE_7_METHODOLOGY.md and
PHASE_8_INTERFACE.md for workload, memory and provenance definitions.
Download locked wheels with `pip download --only-binary=:all: --no-deps -r
requirements-python.lock --dest build/review-wheels` before the read-only dependency
review. Its PyPI advisory response is a dated snapshot, not a universal CVE audit.


## Synthetic BinaryFile / ITCH wire foundation (P1E)

The independent `gig::itch` target does not enter the engine/Python runtime path.
P1E contributed nine outcomes when benchmarks are enabled.
At P1F, `ctest --test-dir build/debug -R '^itch\.' --output-on-failure` selected those
nine plus the eleven P1F context outcomes; later phases add further ITCH tests. At the P1E checkpoint the full native suite had 74 outcomes;
Python Debug/Release had 77 and GCC Python ASan/UBSan had 78, including its live-LSan
control. These are local Linux x86_64 results, not hosted CI or real-data evidence.

See [P1E_VALIDATION_REPORT.md](P1E_VALIDATION_REPORT.md) for exact interfaces,
commands, source policy, memory bounds, final matrix and limitations;
[P1E_MATRIX_COVERAGE.md](P1E_MATRIX_COVERAGE.md) accounts for all 62 proposed synthetic
rows and 8 observed gates. [P1E_EVIDENCE.json](P1E_EVIDENCE.json) retains the verified
implementation SHA, source/JUnit/package hashes and scoped synthetic measurements.
Raw run logs remain ignored under `build/p1e/evidence/`. Do not acquire market data
or infer valid L3 initialization from a successful wire parse.


## Synthetic source context and normalization (P1F)

Build with the existing presets. The standalone `gig::itch_context` target links
only to `gig::itch`; it does not enter engine or Python runtime paths.

```sh
ctest --test-dir build/debug -R '^itch.context' --output-on-failure
python scripts/check_itch_context_reference.py build/debug/gig_itch_context_reference_driver
python scripts/check_itch_context_reference.py build/debug/gig_itch_context_reference_driver --negative-control
python scripts/check_itch_context_benchmark.py build/release/benchmarks/gig_itch_context_benchmark
build/release/benchmarks/gig_itch_context_benchmark 512 7
```

Run the complete suite for each required compiler/configuration as well. At P1F,
native counts were85; GCC Python Debug/Release88 and ASan/UBSan89, including its
existing live-LSan control. The context oracle checks 515 sessions and 12,104
outcomes; prior P1E checks remain active. See
[P1F_VALIDATION_REPORT.md](P1F_VALIDATION_REPORT.md),
[P1F_CONTEXT_DESIGN.md](P1F_CONTEXT_DESIGN.md) and
[P1F_EVIDENCE.json](P1F_EVIDENCE.json) for exact policies, versioned normalization
provenance, hashes, local results, resource measurements and deferred integration.
No source-completion assertion grants L3 initialization eligibility.

## P1G synthetic L3 reconstruction checkpoint

P1G adds a separate `gig::itch_reconstruction` target; existing simulator/execution/
Python behavior is preserved. See [P1G_VALIDATION_REPORT.md](P1G_VALIDATION_REPORT.md)
for final executed evidence and limitations. At this checkpoint native CTest has103
outcomes per configuration, GCC Python Debug/Release106 and sanitizer107 (937 across
nine configurations). Historical P1E/P1F counts above describe their own checkpoints.

```sh
CXX=g++ cmake --preset release
cmake --build --preset release -j2
ctest --preset release --output-on-failure
python3 scripts/run_synthetic_l3_demo.py build/release/gig_itch_l3_reference_driver
python3 scripts/check_itch_l3_reference.py build/release/gig_itch_l3_reference_driver
python3 scripts/check_itch_reconstruction_benchmark.py build/release/benchmarks/gig_itch_reconstruction_benchmark
build/release/benchmarks/gig_itch_reconstruction_benchmark 128 7
```

Use the existing compiler/sanitizer and pinned offline Python package instructions
above for the corresponding matrices. The example uses independently authored
synthetic source bytes and an explicit empty start. It does not download data,
claim a valid historical start or expose a real-market trading interface. P1G has
no gzip/archive reader; P1H requires its own evidence. The native journal remains
15,944 bytes per entry on the measured ABI; bounded replay is not unlimited history.

## P1H bounded synthetic streaming checkpoint

The native debug/release/ASan+UBSan presets enable `GIG_BUILD_ITCH_STREAMING=ON` and
require system zlib development files>=1.3.1. Generic builds and ordinary wheel
builds default this optional feature OFF. The qualified local matrix explicitly
turns it ON in all nine configurations: native117 per row, Python Debug/Release120,
Python sanitizer121 (1,063 outcomes). See [P1H_VALIDATION_REPORT.md](P1H_VALIDATION_REPORT.md).

```sh
CXX=g++ cmake --preset release
cmake --build --preset release -j2
ctest --preset release --output-on-failure
python3 scripts/check_itch_streaming_reference.py build/release/gig_itch_streaming_reference_driver
python3 scripts/check_itch_streaming_benchmark.py build/release/benchmarks/gig_itch_streaming_benchmark
build/release/benchmarks/gig_itch_streaming_benchmark 128 7 17
```

All fixtures are authored synthetic data. The pipeline does not acquire archives,
certify observed initialization, seek into gzip or provide crash-safe hot recovery.
Full-source SHA/CRC/framing gates remain distinct from provisional accepted prefixes.
Stored-block benchmark throughput is not a real NASDAQ compression/workload rate.

## P1I synthetic end-to-end validation

Use the same qualified C++20/zlib environment above. This native demonstration
requires no market data and adds no Python extension API. With streaming enabled:

```sh
CXX=g++ cmake --preset release
cmake --build --preset release -j2
ctest --preset release --output-on-failure
python3 scripts/check_itch_validation_demo.py build/release/gig_itch_validation_demo --negative-controls
python3 scripts/check_itch_profile_probe.py build/release/benchmarks/gig_itch_profile_probe
```

For individual version1 JSON outputs, supply a separately measured lowercase
64-hex implementation/source-manifest digest as `IMPLEMENTATION_SHA256`:

```sh
build/release/gig_itch_validation_demo valid "$IMPLEMENTATION_SHA256"
build/release/gig_itch_validation_demo bounded "$IMPLEMENTATION_SHA256"
build/release/gig_itch_validation_demo restart "$IMPLEMENTATION_SHA256"
build/release/gig_itch_validation_demo corrupt "$IMPLEMENTATION_SHA256"
```

`corrupt` deliberately demonstrates integrity rejection inside a successfully
executed demonstration; inspect `publication_eligible=false`, not just process status.
Malformed CLI identities and failed output sinks return nonzero with no valid complete
result delivery. A bounded prefix must never be promoted to a full-source success.
Schema: [native validation output v1](schemas/itch_validation_output.schema.json).
The structural schema does not replace the independent semantic verifier. The supplied
implementation digest is caller-declared, not auto-authenticated Git provenance.

The offline evidence verifier requires the matching private raw logs/artifacts:

```sh
python3 scripts/check_validation_evidence.py docs/P1H_EVIDENCE.json --raw-root build/p1h/evidence --candidate-profile
python3 scripts/check_validation_evidence.py docs/P1I_EVIDENCE.json --raw-root build/p1i/evidence --candidate-profile
python3 tests/test_validation_evidence.py
```

Historical mode checks source blobs at the recorded implementation commit. Add
`--working-tree` only when exact recorded source bytes are expected in the checkout.
A missing private log/artifact is unavailable evidence and causes rejection; the tool
must not turn documentation assertions into a pass. The candidate-profile option
requires the nine configurations and reviewed P1E–H identities; P1I additionally records
and reviews its new E2E/query/profile test identities in its final matrix.

Clean source reproduction in P1I used an offline source archive containing all136
frozen validation files, enabled streaming/benchmarks/tests in a separate native
Release build, and ran the complete native suite. Direct and source-built wheels
were installed privately and checked from consumer environments. This establishes
same-host source/package restoration, not a fresh VM, ARM64, other Python version,
bit-identical binary build or hosted-CI qualification. See
[P1I validation](P1I_VALIDATION_REPORT.md) for actual evidence and limitations.

## P1J post-audit qualification

The same native demonstration/oracle/profile commands above apply. P1J changes only
the offline evidence verifier and its tests; no native/Python engine API changed.
Current verifier unit coverage is47 cases. With the matching private final artifacts:

```sh
python3 tests/test_validation_evidence.py
python3 scripts/check_validation_evidence.py docs/P1J_EVIDENCE.json --raw-root build/p1j-validation/evidence --candidate-profile
```

The source/measurement profile enforces a reviewed20-file protected minimum, not a
complete transitive build graph; all136 declared final source files are independently
checked at the recorded repair commit. Copied raw/report measurement, toolchain,
environment and package fields must agree type-exactly. No checksum or tool result
is a signature or proof of execution. Preserve the actual raw archives/logs privately
or regenerate them; a missing artifact is not a pass. Final native/package restoration
and nine-row test results are in [the P1J audit](P1J_INDEPENDENT_AUDIT_REPORT.md).
The audit's advisory, hosted, platform, fresh-machine and observed-data limitations
remain open regardless of successful local commands.


## Release-candidate evidence closure

See [RC_CANDIDATE_EVALUATION.md](RC_CANDIDATE_EVALUATION.md) for the independently
hashed source-archive path, fresh Ubuntu rootfs/toolchain reproduction, qualified
private zlib prefix, installed consumers and unchanged canonical identities.
An archive consumer test now requires explicit `GIG_TEST_SOURCE_COMMIT` supplied
from its verified source manifest; it fails if absent/malformed and rejects a
conflicting value in a Git checkout. Archive tests conservatively mark checkout
cleanliness as unknown/dirty, rather than inventing a clean Git state.
This changes test provenance handling only, not package/engine contracts.

Ubuntu24.04 distribution zlib reports1.3 and does not meet the optional streaming
minimum1.3.1. Use `bash scripts/build_ci_zlib.sh /absolute/new/private-prefix`
(optionally with the recorded official archive as a second argument), then supply
`-DZLIB_ROOT=/absolute/new/private-prefix`. The helper verifies the pinned digest
before extraction/build, refuses an existing prefix/work directory and verifies
header/runtime1.3.1. It requires curl,TLS CA trust,C/C++ compilers,CMake,Ninja,tar
and sha256sum. It does not replace system libraries or lower the minimum.

Fresh-container results do not certify a separate machine. RC13,RC16 andRC17
retain explicit evidence boundaries in [RC_EVIDENCE_CLOSURE_REPORT.md](RC_EVIDENCE_CLOSURE_REPORT.md).

## Offline H/Y status-observation extension

See [HY_HISTORICAL_COMPATIBILITY.md](HY_HISTORICAL_COMPATIBILITY.md) and
[ITCH_HISTORICAL_COMPATIBILITY_MATRIX.md](ITCH_HISTORICAL_COMPATIBILITY_MATRIX.md).
H/Y support is explicitly selected with `DecodeProfile::status_observations_v2`
and `ContextPolicy::decode_profile`;default v1 and its five canonical hashes stay
unchanged. This adds no Python H/Y API or observed-market initialization path.

With tests,benchmarks and optional streaming enabled,the H/Y checkpoint has131
native CTest outcomes,Python Debug/Release134,and GCC Python ASan+UBSan135.
The earlier122/125/126 counts above belong to P1I/P1J/closure checkpoints. Reproduce:

```sh
cmake --build build/phase9-clean-debug --parallel 2
ctest --test-dir build/phase9-clean-debug -R '^itch.hy_' --output-on-failure
python3 scripts/check_itch_hy_reference.py build/phase9-clean-debug/gig_itch_hy_tests
python3 scripts/check_itch_hy_reference.py build/phase9-clean-debug/gig_itch_hy_tests --negative-control
```

Configure the existing compiler/sanitizer/Python profiles before using a new build
directory;do not mix compilers inside a cache. Full actual results and artifact
identities are in HY_VALIDATION_EVIDENCE.json. No Nasdaq request is part of these
commands. A future approved prefix inspection must select v2 explicitly and use
correct complete-frame-versus-consumed accounting.

Source-distribution closure also runs the standalone packaging-only regressions:
`/workspace/gig-tools/bin/python tests/test_sdist_patterns.py` (three cases), then
`scripts/check_sdist_inventory.py ARCHIVE --source-root . --manifest MANIFEST`.
Use the exact source snapshot for byte comparison. Recursive force-includes are
intentionally absent so ignored build outputs and Python caches stay excluded.
