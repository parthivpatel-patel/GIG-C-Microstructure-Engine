# Private synthetic candidate evaluation

This is a private evaluation recipe, not a distribution or release grant. Formal
candidate closure is blocked as documented in `RC_EVIDENCE_CLOSURE_REPORT.md`.
Engine source remains at the previously validated P1E–P1J behavior. The closure
source export is commit `5349789` (full identity and hash in
`RC_CLOSURE_EVIDENCE.json`); subsequent workflow/docs changes are separately
recorded. A new source archive needs its own measured hash; never assume it equals
this frozen artifact.

## Frozen inputs and environment

The qualification used official `ubuntu:24.04`, digest
`sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac`,
a newly provisioned Ubuntu24.04.5 rootfs, GCC13.3,Clang18.1.3,glibc2.39,
CMake3.28.3,Ninja1.11.1,CPython3.12.3 with Ubuntu vendor backports. It has a3GiB
container limit,2CPUs and512-PID limit; kernel6.18.55 and daemon28.4.0 are shared.
Only source/recorded dependencies and an old private wheel were supplied readonly;
no host compiler/library/build directory was mounted. A public CA bundle was
mounted readonly to preserve configured proxy trust. No privileged/host-network
mode, proxy bypass, TLS-disable flag or paid resource was used.

A source archive was made with `git archive FULL_SHA`, SHA256 measured before
transfer, then extracted to a new directory with no`.git`. The manifest retains
all12 exact reviewed dependency-wheel SHA256 values. Before use, independently
compare archive/wheel bytes against that manifest; do not use an arbitrary
`GIG_TEST_SOURCE_COMMIT` as evidence that the source actually belongs to a commit.
The old Debian-built private0.1.1 wheel is explicitly distinguished from the new
Ubuntu source-built wheel; identical versions do not mean identical artifacts.

## Native and Python reproduction

In an authorized fresh Linux environment, preserve normal proxy/TLS settings and
install signed distro packages for GCC,Clang,`libclang-rt-18-dev` (Clang18 sanitizer runtimes),
CMake,Ninja,Python3.12 development/venv,
curl,CA certificates,Git and time. Retain actual package versions/changelogs.
Restore `requirements-python.lock` into a tooling venv from previously verified
wheels, e.g. `pip install --no-index --find-links=/private/wheels -r
requirements-python.lock`. The version lock is not a hash-enforced pip lock;
explicitly check every supplied wheel hash before installation.

```sh
bash scripts/build_ci_zlib.sh /private/new-zlib-prefix /private/zlib-1.3.1.tar.gz
export GIG_TEST_SOURCE_COMMIT=5349789edfc198f5bf74438cf412e403cef14fa9
```

The SHA above is the frozen qualification export. For another export, replace it
with exactly the full `source_commit` from its independently verified manifest
(or read that JSON with Python). No identity may be guessed from a filename. The helper's
official archive is1572744 bytes, SHA256
`17e88863f3600672ab49182f217281b6fc4d3c762bde361935e436a95214d05c`.
Omit its second argument only when authorized official network retrieval works.
Existing prefix/work directories are refused.

Configure independent new binary directories for GCC/Clang × Debug/Release/
ASan+UBSan. For each use `-G Ninja -DBUILD_TESTING=ON
-DGIG_BUILD_BENCHMARKS=ON -DGIG_BUILD_ITCH_STREAMING=ON
-DGIG_WARNINGS_AS_ERRORS=ON -DZLIB_ROOT=/private/new-zlib-prefix`, explicit
`CMAKE_CXX_COMPILER` and `Python3_EXECUTABLE`. Sanitizer rows enable both
`GIG_ENABLE_ASAN` and `GIG_ENABLE_UBSAN`, with Debug build type. GCC Release also
sets `GIG_BUILD_PYTHON=ON` and `pybind11_DIR` from the tooling venv. Build with
`cmake --build DIR --parallel 2`, then
`ctest --test-dir DIR --output-on-failure --output-junit /private/evidence/ROW.xml`.
Require122 cases per native row,125 for GCC Python Release, zero failures/skips/
disabled, and all five canonical hashes in `RC_CLOSURE_EVIDENCE.json`.
These six fresh rows supplement, not replace, P1J's prior nine-row1108 qualification.
The minimal Ubuntu image initially lacked Clang18 ASan runtime archives; install
the matching signed runtime package before configuring a new sanitizer build.
The failed linker log is retained separately from the repaired row.

The independent end-to-end test is reproducible directly:

```sh
python scripts/check_itch_validation_demo.py DIR/gig_itch_validation_demo --negative-controls
python scripts/check_itch_profile_probe.py DIR/benchmarks/gig_itch_profile_probe
python scripts/measure_benchmark_child.py DIR/benchmarks/gig_itch_profile_probe 128
```

Run resource probes sequentially after compilation stops; record RSS scope and
executable identity. The profile is two 128-live-order books,1024 journal entries/
book,one active price level/book and128MiB shared tracked PMR. It is not an
all-capacities memory guarantee. Ordinary wheels leave optional gzip streaming OFF;
Python consumers test existing research interfaces, not a new streaming Python API.

## Installed consumers and artifacts

Build a source distribution with `python -m build --sdist --no-isolation`; build
its wheel with `python -m pip wheel --no-index --no-deps --no-build-isolation
--wheel-dir /private/new-wheel SDIST`. The tooling venv must already contain the
verified exact build dependencies. Test the retained old wheel and new source-built
wheel in **separate new venvs**, installing dependencies from the verified wheelhouse
with lock constraints. With build-tree `PYTHONPATH` unset, run each installed
interpreter against `tests/test_python.py`, `tests/test_export_contracts.py`, and
`examples/python_research.py`. Require8 interface and6 export unit cases per
consumer (one additional harness regression versus P1J), installed module paths
under its own venv, and example SHA256
`c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9`.
Retain wheel/sdist/module/build identities. No bit-identical wheel/native ABI or
other Linux distro/Python compatibility is promised.

Raw commands, logs, JUnit, counts, SHA256 and actual outcomes are recorded in the
closure evidence. A successful helper, container build or manifest verification is
not hosted CI, full security clearance, observed-market validation, independent
physical-machine reproduction or permission to distribute any artifact.
