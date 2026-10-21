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

Repeat with release and asan-ubsan. Each native suite has 61 outcomes, including
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
