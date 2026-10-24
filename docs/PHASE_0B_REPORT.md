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

## Final baseline and acceptance evidence

Checkpoint 2 pushed and exact remote SHA verified:
6bdf4758e44ff4aa88dd806cfab10682474b7b57.

The Release baseline ran from that clean commit, after all 16 Release checks.
`baselines/phase0b-validator.json` contains the complete applicable provenance,
source/executable/result SHA-256 hashes, environment, compile commands, standard
library, workload seed/fingerprint, oracle counts and all seven raw samples.
Manifest SHA-256: 2a703a5e59e29cdf2394707f93bbf7a5434e075808dab1a06b7dca75c86df4e7.

262144 synthetic records x 64 batches = 16777216 validations per repetition;
2 warmups, 7 timed repetitions, seed 42, one thread. Median batch time:
41.698456 ms; observed batch range: 32.338653–59.957308 ms. Median batch-derived
throughput: 402346216.3682991 validations/second. These are existing field-validator
measurements ONLY, not per-event latency, orders/second, LOB, replay or analytics
performance. Large variation on shared cloud is visible; no optimization/speedup
or production claim is made. Each batch independently expects 98304 valid records.

Final local GCC suites: Debug 16/16, Release 16/16, ASan+UBSan 16/16. No skipped
checks or reported sanitizer findings. Thirteen positive checks and three verified
negative checks per suite; these are not 16 feature/domain tests. No TSan runtime,
Clang execution or native ARM64 validation. Checkpoint 2 was tested with warnings
as errors, then reviewed before commit/push. Original core header and demo source
remain byte-for-byte unchanged.

Hosted CI status: NOT VERIFIED. The specific check-runs API request after the
checkpoint push also returned Forbidden. The six-job GCC/Clang matrix and Release
benchmark smoke are committed, but local tests are not evidence of hosted success.
No main merge or force push. Final documentation/evidence is a separate checkpoint;
its SHA is reported in the completion message to avoid self-referential commits.

### Phase 0B acceptance criteria

- [x] Preserve history and existing development branch; main unchanged.
- [x] Record approved architecture and all four mandatory refinements.
- [x] Scoped CMake flags, reproducible presets and BUILD_TESTING support.
- [x] Debug/Release runtime checks remain active and failures are observable.
- [x] ASan/UBSan pass; incompatible TSan combinations rejected.
- [x] Oracle-validated deterministic scaffold baseline before any optimization.
- [x] Minimal bounded harness and complete applicable benchmark lineage.
- [x] CI matrix and benchmark smoke configured; dependencies are minimal.
- [x] Honest implementation/verification and metric limitations documented.
- [x] Implementation checkpoints pushed and exact remote SHAs verified.
- [ ] Hosted CI results: inaccessible from this runtime, NOT VERIFIED.
- [ ] Phase 1 approval: required; no Phase 1 implementation started.

### Remaining risks

Numeric aliases remain weak; invalid Side values are still accepted by the
scaffold. These are disclosed Phase 1 work, not fixed implicitly in bootstrap.
Atomic book mutations, multi-stream replay and full research lineage are specified
but cannot be runtime-validated until those components exist. The baseline has
no market-data realism, event-latency percentiles, allocation or peak-memory data.
Private repository visibility is user-declared; API metadata access was denied.

### All changed files relative to original bootstrap tip

- `.github/workflows/ci.yml`
- `CMakeLists.txt`
- `CMakePresets.json`
- `README.md`
- `benchmarks/CMakeLists.txt`
- `benchmarks/validator_batch.cpp`
- `benchmarks/validator_batch.hpp`
- `benchmarks/validator_benchmark.cpp`
- `cmake/ExpectFailure.cmake`
- `docs/ARCHITECTURE.md`
- `docs/BENCHMARK_METHODOLOGY.md`
- `docs/GIG_INTEGRATION.md`
- `docs/LIMITATIONS.md`
- `docs/MARKET_MODEL.md`
- `docs/MICROSTRUCTURE_METRICS.md`
- `docs/PHASE_0B_REPORT.md`
- `docs/VALIDATION.md`
- `docs/baselines/phase0b-validator.json`
- `docs/decisions/0001-approved-contracts.md`
- `scripts/run_benchmark.py`
- `tests/test_types.cpp`
