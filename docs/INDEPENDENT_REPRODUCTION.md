# Clean-checkout reproduction and evidence archive

October24,2026 (America/New_York). Source883d91c32f428396f9ee412d07f14a13d14e36c3,
implementationf02363e0e09b9767b4dc6748737206254e5e4c6a. A fresh detached Git
worktree at /workspace/gig-fourphase-clean was configured and built from scratch.
No precompiled engine/library/build cache was copied. This is a new clean checkout
on the existing Codex host, not a new independent physical machine or human audit.
Native external ARM qualification remains separately closed by run40126420107.

## Dependencies and exact procedure

Actual host: Debian13 x86_64, GCC14.2.0-19, CMake3.31.6, Ninja1.11.1,
CPython3.12.14 with development headers; system zlib header/runtime1.3.1. A C++20
compiler and128-bit integer support are required. Optional Python bindings need
all12 exact requirements-python.lock entries, including pybind11/scikit-build-core,
jsonschema and its transitive packages. Build frontend cmake==3.31.6 and
ninja==1.11.1.3 are separate tested tool distributions. Exact installed versions,
Python-linked OpenSSL/Expat and compiler output are manifest metadata, not security
clearance. Clang is optional and not used for this fresh GCC Release reproduction.

Example from a clean checkout of the source SHA (use your own empty destination):

```sh
python3 -m venv /tmp/gig-repro-tools
/tmp/gig-repro-tools/bin/python -m pip install cmake==3.31.6 ninja==1.11.1.3
/tmp/gig-repro-tools/bin/python -m pip install -r requirements-python.lock
export PATH=/tmp/gig-repro-tools/bin:$PATH
cmake -S . -B build/reproduction -G Ninja -DCMAKE_CXX_COMPILER=g++ \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DGIG_WARNINGS_AS_ERRORS=ON \
  -DGIG_BUILD_BENCHMARKS=ON -DGIG_BUILD_ITCH_STREAMING=ON -DGIG_BUILD_PYTHON=ON \
  -DPython3_EXECUTABLE="$(command -v python)" \
  -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"
cmake --build build/reproduction --parallel 2
ctest --test-dir build/reproduction --output-on-failure \
  --output-junit "$PWD/build/reproduction/tests.xml"
python -m build --sdist --wheel --no-isolation --outdir build/dist
python -m pip wheel --no-deps --no-build-isolation build/dist/*.tar.gz --wheel-dir build/source-dist
python -m venv build/consumer
build/consumer/bin/python -m pip install --constraint requirements-python.lock build/dist/*.whl
build/consumer/bin/python tests/test_python.py
build/consumer/bin/python tests/test_export_contracts.py
build/consumer/bin/python examples/python_research.py
```

Repeat consumer checks with the wheel built from source archive. Do not mix build
trees/compiler caches. If system zlib is older than1.3.1, follow
scripts/build_ci_zlib.sh's official-source/SHA-qualified private-prefix procedure
and supply ZLIB_ROOT; no TLS bypass or unqualified mirror. This reproduction used
system1.3.1, recorded by package identity, rather than a hidden local engine artifact.

Actual pinned tools were already installed at /workspace/gig-tools, not reinstalled
without cause. Installed consumers were fresh virtual environments. Their only
external inputs were explicitly retained PyPI dependency wheels from
build/phase9-dependency-wheels; names/sizes/SHA256 appear in dependency-wheels.json.
For a new machine obtain exact-lock wheels using pip download --only-binary=:all:
--no-deps -r requirements-python.lock, and verify source registry digests. Offline
installation used --no-index/--find-links pointing at that documented cache.

## Executed results

Fresh configure and119-step build succeeded. **157/157 CTest outcomes**, zero
failures/skips/disabled; all eight canonical SHA256 identities equal qualification.
This includes ten benchmark correctness/contract cases, deterministic replay,
independent references, failure injection, journal and restart checks. Their actual
names and output digests are in the manifest, not invented performance results.
Fresh checkout/source-archive wheels passed8 interface+6 export tests each:
**28 installed checks**, both research examples retain SHA256
c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9.
No native ARM matrix was rerun, and these are local x86 results.

## Manifest and verification

[evidence/reproduction_manifest.json](evidence/reproduction_manifest.json) separates
reproducible source/profile/count/hash requirements from environment-dependent
compiler/OS/dependency metadata. Private artifacts are under build/four-phase/phase1;
all file receipts use relative paths and SHA256. To verify that archive after
copying it intact:

```sh
python scripts/verify_reproduction.py docs/evidence/reproduction_manifest.json \
  --artifacts build/four-phase/phase1
python tests/test_reproduction_verifier.py
```

The verifier fixes the eight-identity policy and allowed profile counts, rejects
path escapes/symlinks, digest mismatch, duplicate JSON fields, oversized files,
DTD/entity/NUL/non-UTF8 JUnit and missing/duplicate/failed/skipped testcases. Six
independent controls cover valid evidence plus hash/path/count/canonical/DTD
corruption. It checks receipts against supplied trusted files; it does not certify
remote publisher authenticity or recreate missing artifacts. Another engineer can
repeat the commands and compare semantic identities; timings/binary wheel bytes
are environment-dependent, not promised identical.

## Native archive boundary

NATIVE_ARM64_QUALIFICATION_EVIDENCE.json preserves independently obtained official
summary and six job/step records, full source SHA, job IDs/durations, expected hash
policy and public source links for run40126420107. Raw logs/JUnit/compiler output
remain inaccessible via existing authenticated access (API Forbidden, no configured
outbound identity). No repeated blocked request, login, secret discovery or bypass.
This is the explicitly permitted metadata-only archival fallback, not full raw
artifact archival. Owner export of the existing run remains the smallest action.
