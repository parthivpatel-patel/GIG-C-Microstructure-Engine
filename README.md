# GIG C++ Microstructure Engine

Standalone C++20 market-microstructure research project. Correctness precedes
performance. No live trading, broker connection or GIG Quant Terminal dependency.
The initial README and all Git history are preserved in repository history.

## Current status — Phase 0B bootstrap

IMPLEMENTED: small AddOrder validation scaffold, demo, explicit runtime checks,
CMake Debug/Release and sanitizer configurations. Verification evidence is recorded
in docs/PHASE_0B_REPORT.md when available. Planned features are NOT implemented:
strong core contracts, LOB, replay, analytics, matching, execution and Python.
An optional reproducible validator-only benchmark is included. See [limitations](docs/LIMITATIONS.md); this is not a working market engine.

## Build and test

Requires C++20 GCC/Clang, CMake >=3.20 and Ninja. From this directory:

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
define the planned engine. [Benchmark methodology](docs/BENCHMARK_METHODOLOGY.md)
describes the limited scaffold baseline, not LOB performance. No performance or
production-readiness claim follows from using C++.

## Development

Use `feat/bootstrap-cpp20-engine` for approved Phase 0B work; never force-push or
merge main without approval. GitHub is the durable source of truth: verified
checkpoints must be pushed and their remote SHAs checked before substantial new
work. Phase 1 requires separate user approval.
