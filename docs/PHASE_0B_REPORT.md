# Phase 0B checkpoint evidence

## Checkpoint 1: build, tests and architecture

Base: f57b3560870d40b8c6384ce6600a3752d409e35e on
feat/bootstrap-cpp20-engine. Main remains unchanged. No core header/demo changes.

Observed locally: Debian 13.6 Linux x86_64, GCC 14.2.0, CMake 3.31.6,
Ninja 1.11.1, Python 3.12.14. Tools installed in /workspace/gig-tools, outside Git.

Debug: 13/13 CTest outcomes passed. Release: 13/13. ASan+UBSan: 13/13,
no reported sanitizer findings. Each suite comprises 11 domain-scaffold cases,
1 demo smoke and 1 expected-failure harness check; these are not 13 domain tests.
The deliberate failure was also invoked directly in Debug and Release: exit 1.
Incompatible TSan+ASan configure rejected as intended. BUILD_TESTING=OFF builds.
Warnings-as-errors enabled in all three tested presets. No Phase 1 functionality.

CI matrix configured for GCC/Clang x Debug/Release/ASan+UBSan on Ubuntu 24.04.
Remote CI execution NOT VERIFIED: GitHub API request returned Forbidden in this
runtime. Git fetch works; API access is distinct. Repository privacy follows user
configuration but could not be independently confirmed through that denied API.
Clang/native ARM64/TSan runtime validation not performed locally.

Review: git diff --check passed; no credentials, datasets or generated build
outputs included. Approved mutation, ordering, provenance and pre-optimization
correctness gates are design contracts, not implemented engine behavior.

## Next checkpoint

Minimal validator-only benchmark with independent oracle, bounded input options,
reproducible workload, raw repetition samples and checksummed environment manifest.
No engine timing or economic claim.

## Checkpoint 2: correctness-validated scaffold harness

Checkpoint 1 remote SHA verified:
c61ecba556619914780a5aa9ee2211c4637e1955.

Final suites have 16 CTest outcomes each: 11 scaffold domain cases, 1 demo,
1 benchmark oracle check and 3 explicitly expected-failure checks. Negative checks
require exit 1 and the intended diagnostic; sanitizer errors/crashes cannot pass.
The harness uses an independent construction oracle, separate compiled timed
batch, bounded options and consumed result counts. A temporary deliberately broken
always-true validator was rejected with oracle mismatch. Repeated seed 42 produced
the same workload fingerprint/count; seed 43 changed the fingerprint. Runner
rejected Debug evidence and overwrite attempts. Smoke manifest emitted successfully.
Full clean-commit timing evidence is captured only after committing the harness.
No optimization or Phase 1 core changes were made.
