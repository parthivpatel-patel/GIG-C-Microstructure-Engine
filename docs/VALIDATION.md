# Validation and acceptance gates

## Bootstrap commands

Requires CMake >=3.20, Ninja and GCC or Clang with C++20. No network downloads occur
at configure/build time. From the repository root:

```sh
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
cmake --preset release
cmake --build --preset release
ctest --preset release
cmake --preset asan-ubsan
cmake --build --preset asan-ubsan
ctest --preset asan-ubsan
```

Eleven named runtime type cases exercise the existing validator, plus one demo
smoke and one deliberately failing harness case marked WILL_FAIL. Runtime checks
remain active with NDEBUG; an unknown case fails. The expected-failure test proves
failure exits are observable in Debug and Release, not domain correctness.
No zero-test success is accepted. Tests do not validate future event semantics.

Warnings are private to project executables. ASan/UBSan abort on findings and use
frame pointers; no suppressions. TSan has a separate configuration switch but is
not a Phase 0B acceptance target because no concurrent code exists. Sanitizer
support is gated to GCC/Clang; actual runtime/platform support still needs testing.

## Future phase gates (not implemented)

Phase 1: strong types, exact conversion, malformed events, checked arithmetic.
Phase 2: FIFO/conservation/index invariants, independent reference book, randomized
seeded streams, canonical replay, sequence recovery and allocation fault injection.
Phase 3: independent basic-metric numeric references and invalid states.
Phase 4: OFI/classification assumptions, causal horizons and sampling.
Phase 5: separate matching/reconstruction, cancellation races and seeded latency.
Phase 6: schedule constraints, inventory/cost reconciliation, no look-ahead.
Phase 7: correctness-validated before/after benchmarks; concurrency needs TSan.
Phase 8: exact schema/Python round trips, ownership and standalone compatibility.
Phase 9: native ARM64 and x86_64 reproducibility, complete portfolio documentation.

Every coherent checkpoint: inspect diff, test, review, commit, push designated
private development branch, compare remote SHA exactly; only then continue.
Never force-push, rewrite published history or merge main without approval.
