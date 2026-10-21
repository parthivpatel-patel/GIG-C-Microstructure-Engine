# GIG C++ Microstructure Engine

Standalone C++20 market-microstructure research project. Correctness precedes
performance. No live trading, broker connection or GIG Quant Terminal dependency.
The initial README and all Git history are preserved in repository history.

## Current status — Phase 1

IMPLEMENTED: eleven strong numeric types, checked arithmetic and exact unit
conversion, eight typed event families, explicit metadata/provenance and structured
allocation-free validation. [Phase 1 contracts](docs/PHASE_1_CONTRACTS.md) specify
required fields, missing states, limits and errors. The demo validates a synthetic
event; it does not replay a market. No LOB, matching, analytics, execution or Python
implementation exists. See [limitations](docs/LIMITATIONS.md).

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
define the planned engine. [Benchmark methodology](docs/BENCHMARK_METHODOLOGY.md)
describes the versioned payload baseline, not LOB performance. No performance or
production-readiness claim follows from using C++.

## Development

Use `feat/bootstrap-cpp20-engine` for approved development; never force-push or
merge main without approval. GitHub is the durable source of truth: verified
checkpoints must be pushed and their remote SHAs checked before substantial new
work. Phase 1 is authorized; Phase 2 requires separate user approval.
