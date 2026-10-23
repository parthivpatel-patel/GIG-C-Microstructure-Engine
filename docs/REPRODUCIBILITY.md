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

Repeat with release and asan-ubsan. Each current native suite has 85 outcomes (65 original outcomes, 9 P1E wire checks and 11 P1F context checks), including
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
`ctest --test-dir build/debug -R '^itch\.' --output-on-failure` now selects those
nine plus the eleven P1F context outcomes. At the P1E checkpoint the full native suite had 74 outcomes;
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

Run the complete suite for each required compiler/configuration as well. Current
native counts are 85; GCC Python Debug/Release 88 and ASan/UBSan 89, including its
existing live-LSan control. The current context oracle checks 515 sessions and 12,104
outcomes; prior P1E checks remain active. See
[P1F_VALIDATION_REPORT.md](P1F_VALIDATION_REPORT.md),
[P1F_CONTEXT_DESIGN.md](P1F_CONTEXT_DESIGN.md) and
[P1F_EVIDENCE.json](P1F_EVIDENCE.json) for exact policies, versioned normalization
provenance, hashes, local results, resource measurements and deferred integration.
No source-completion assertion grants L3 initialization eligibility.
