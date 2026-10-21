# GIG C++ Microstructure Engine

Standalone C++20 market-microstructure research project. Correctness precedes
performance. No live trading, broker connection or GIG Quant Terminal dependency.
The initial README and all Git history are preserved in repository history.

## Current status — Phase 3 in validation

IMPLEMENTED: strong types and validated event contracts, a deterministic single-owner
order-level book, strict multi-stream replay, explicit reset/recovery, owned accepted-
event provenance and canonical outputs. Historical reconstruction never matches orders.
The demo replays an entirely synthetic 11-record workflow; `--canonical` emits its
canonical result. Book-state exact analytics are implemented; no matching, execution simulation or Python integration yet.

See [book semantics](docs/PHASE_2_BOOK.md), [replay contracts](docs/PHASE_2_REPLAY.md),
[benchmark methodology](docs/PHASE_2_BENCHMARKS.md) and [limitations](docs/LIMITATIONS.md).
[Phase 2 completion report](docs/PHASE_2_REPORT.md) records evidence and acceptance.
Phase 1's [field contracts](docs/PHASE_1_CONTRACTS.md) still apply.

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
