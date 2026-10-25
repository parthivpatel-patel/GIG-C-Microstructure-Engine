# GIG C++ Microstructure Engine

Standalone C++20 market-microstructure research project. Correctness precedes
performance. No live trading, broker connection or GIG Quant Terminal dependency.
The initial README and all Git history are preserved in repository history.

## Current status — Phase 9

IMPLEMENTED: strong types and validated event contracts, a deterministic single-owner
order-level book, strict multi-stream replay, explicit reset/recovery, owned accepted-
event provenance and canonical outputs. Historical reconstruction never matches orders.
The demo replays an entirely synthetic 11-record workflow; `--canonical` emits its
canonical result. Exact book-state and causal windowed flow analytics are implemented; separate synthetic matching and latency simulation are implemented. Offline TWAP/VWAP/POV planning and exact TCA are implemented. Common-code baselines and scoped profiling are recorded; no speculative optimization. Pinned Python research bindings and exact version1.0 schemas are implemented; see [the interface guide](docs/PHASE_8_INTERFACE.md).

See [book semantics](docs/PHASE_2_BOOK.md), [replay contracts](docs/PHASE_2_REPLAY.md),
[benchmark methodology](docs/PHASE_2_BENCHMARKS.md) and [limitations](docs/LIMITATIONS.md).
[Phase 2 completion report](docs/PHASE_2_REPORT.md) records evidence and acceptance.
Phase 1's [field contracts](docs/PHASE_1_CONTRACTS.md) still apply.

Final validation, reproducibility and acceptance: [final report](docs/FINAL_REPORT.md),
[reproducibility guide](docs/REPRODUCIBILITY.md) and [security review](docs/SECURITY_AND_DEPENDENCIES.md).

Correctness follow-up: [remediation report](docs/CORRECTNESS_REMEDIATION.md) records
maker-report, TCA-boundary, export-consistency and compiler-metadata repairs.

## Build and test

Requires C++20 GCC/Clang, CMake >=3.20 and Ninja; tests additionally require
Python >=3.8 for independent arbitrary-precision numeric references. From this directory:

```sh
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
./build/debug/gig_engine_demo
```

Repeat with `release` and `asan-ubsan`; see [validation](docs/VALIDATION.md).
Optional local tools (outside the checkout):

```sh
python3 -m venv /workspace/gig-tools
/workspace/gig-tools/bin/pip install cmake==3.31.6 ninja==1.11.1.3
export PATH=/workspace/gig-tools/bin:$PATH
```

[Architecture](docs/ARCHITECTURE.md) and [approved contracts](docs/decisions/0001-approved-contracts.md)
define the engine boundaries. [Benchmark methodology](docs/BENCHMARK_METHODOLOGY.md)
describes the versioned payload baseline, not LOB performance. No performance or
production-readiness claim follows from using C++.

## Development

Use `feat/bootstrap-cpp20-engine` for approved development; never force-push or
merge main without approval. GitHub is the durable source of truth: verified
checkpoints must be pushed and their remote SHAs checked before substantial new
work. Phases 3–9 are authorized by [the autonomous mandate](docs/AUTONOMOUS_MANDATE.md).
Proceed sequentially through validated checkpoints; no merge to main or release publication.

## Optional institutional research terminal

The `terminal/` consumer now provides a local React/TypeScript/Three.js interface
backed by the native Python/C++ engine: authored deterministic replay, exact depth,
interactive3D, execution plans/simulation/TCA and permission-aware research controls.
It is separate from GIG Quant Terminal. Live mode remains unavailable pending
provider protocol/access/rights verification; no observed liquidity is fabricated.
The private LOBSTER sample remains blocked. No broker/order submission exists.
A fixture-tested supervised Kraken candidate now connects the bounded native L2
book to the existing terminal after explicit server-side protocol/usage review.
[Provider operation and activation gates](docs/LIVE_PROVIDER_OPERATIONS.md) explain
why this is not yet live-qualified. [Bounded L2 source-log replay](docs/L2_RECORDING_REPLAY.md)
now supports private session discovery and interactive recorded replay. Observed
capture controls require separate server-side retention approval; no observed data
was collected or qualified. [Continuous status](docs/CONTINUOUS_ENGINEERING_STATUS.md)
records the latest engineering checkpoint.
See [startup instructions](docs/TERMINAL_REPRODUCIBILITY.md),
[architecture](docs/INSTITUTIONAL_TERMINAL_ARCHITECTURE.md) and
[provider boundaries](docs/MARKET_DATA_PROVIDER_MATRIX.md). Existing Phase9/core
reports above retain their historical scope;new code needs fresh owner-gated ARM64.
