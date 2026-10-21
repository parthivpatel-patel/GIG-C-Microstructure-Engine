# GIG C++ Microstructure Engine

A deterministic C++20 market microstructure research engine.

## Scope
- Event-driven market data replay and limit order book reconstruction
- Order flow imbalance, trade signing, liquidity and impact estimators
- Property tests, sanitizers and reproducible performance benchmarks
- Optional Python bindings after the C++ core is validated

This is a **research and engineering project**, not a live matching venue or trading system. Correctness precedes performance claims.

## Build
Requires CMake >= 3.20 and a C++20 compiler.

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
ctest --test-dir build --output-on-failure
./build/gig_engine_demo
```

## Initial milestone
The scaffold demonstrates integer-tick event accounting. The next milestone is a tested price-time-priority L3 book with explicit exchange-event semantics, deterministic replay and invariant checks.

## Design rules
- Integral price ticks and quantities; no floating-point price keys
- Deterministic processing and explicitly defined timestamps/sequence numbers
- No premature low-latency claims without repeatable benchmarks
- Separate research engine from broker execution and GIG Quant Terminal
