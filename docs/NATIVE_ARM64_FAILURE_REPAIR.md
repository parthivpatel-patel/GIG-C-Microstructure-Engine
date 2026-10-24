# First native ARM64 run — arithmetic runtime and sanitizer workload repair

October 24, 2026 (America/New_York). Development branch only. Starting SHA:
`e0ab30f5674bfd3dfb57ccbee0f4213e588b9e5b`.

## Hosted evidence boundary

Owner-supplied run ID: **40113269297**, tested commit above. Owner verified GCC
Debug/Release passed; GCC ASan+UBSan reached 153/154 tests with the profile probe
exceeding its 180-second subprocess timeout; all three Clang jobs failed to link
`gig_execution_tests` with undefined `__muloti4`.

One authorized `gh run view 40113269297 --log` attempt returned exit 1:
`failed to get run: Get "https://api.github.com/repos/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/runs/40113269297?exclude_pull_requests=true": Forbidden`.
Full hosted logs, exact installed compiler versions, stage timings, allocator/RSS
and runner load could not be independently recovered. No retry/bypass, dispatch,
rerun or cancellation was attempted. This report does not claim hosted success.

## A. Confirmed arithmetic/runtime incompatibility

`include/gig/analytics/exact.hpp` used signed `__builtin_mul_overflow` on `__int128`.
A minimal variable-input reproduction with Ubuntu Clang 18.1.3 targeting AArch64
emits an undefined `__muloti4` in its object. Default driver linkage selects
`-lgcc_s -lgcc`; the installed AArch64 GCC 13 libgcc archive does not define that
symbol. The actual linker diagnostic is:

```
/usr/bin/aarch64-linux-gnu-ld: ... in function multiply(__int128, __int128):
undefined reference to `__muloti4'
clang++: error: linker command failed with exit code 1
```

This reproduces the reported runtime-symbol dependency independently, using a
cross compiler. It does not establish the unavailable hosted Clang version.
Clang compiler-rt can supply runtime builtins in appropriate installations, but
switching global runtime selection or installing a target-specific runtime is
unnecessary here and can complicate sanitizer portability.

The repair checks unsigned magnitudes against `(2^127-1)/other` before multiplying.
Unsigned modular negation obtains the magnitude even for signed minimum without
signed overflow. Zero operands return zero, including minimum times zero, as
before. Nonzero products outside the symmetric magnitude range throw the same
`ArithmeticFailure{overflow}`. Only a proven representable unsigned product is
converted to signed, then optionally negated. No floating arithmetic, truncation,
rounding, unchecked signed multiplication or overflow-check weakening.

AArch64 Clang `-O0` and `-O3` links both succeed with default libgcc; QEMU execution
checks success, overflow and minimum-times-zero. `nm` shows no `__muloti4` (ordinary
`__udivti3` remains supplied by libgcc). Actual production execution.cpp and the
execution tests also compile/link using Clang for AArch64 and run successfully
under QEMU. This is cross/emulated repair evidence, not native qualification.

Existing execution reference protocol now includes test-only limb/sign operands
for direct checked-multiply comparisons. Python arbitrary-precision integers
independently determine exact products and overflow. Signed minimum, both signs,
zero, maximum, near-boundary factors, 64-bit limbs and seeded adversarial values
are covered alongside existing Fraction-based schedule/TCA checks: **5,129 total
reference comparisons**, all passing in the cross/emulated run. Existing CTest
case identities/counts are unchanged.

## B. Sanitizer timeout: bounded work, retained correctness gates

The unchanged full probe completes locally: Release 0.381 seconds and GCC
ASan/UBSan 6.914 seconds, with 45 reached query-allocation failures. Temporary,
noncommitted stage instrumentation measured:

| Full-size sanitizer stage | Local seconds |
|---|---:|
| Initial feed and exports |1.109|
| Exhaustive checkpoint allocation sweep |3.823|
| Restart/replay/completion |1.179|
| Resource-cap checks |1.038|

The sweep retries checkpoint construction for every reached allocation site;
later failures repeatedly export/hash the complete two-book, 2,048-native-event
journal. It is bounded at 256 attempts, requires eventual success, and verifies
state/storage equality after each failure. This repeated diagnostic work explains
most local probe time. Local termination and independent checks show no local
hang or state defect. **The precise cause of the hosted elapsed time is not
proven:** architecture/compiler instrumentation cost, scheduling/runner load or
other host conditions require actual hosted logs/timings. No engine performance
regression or hang is asserted or ruled out on the inaccessible runner.

For ASan or UBSan builds only, CMake now requests
`--sanitizer-allocation-profile`. This retains:

- The same 128 active orders and 1,024 journal records per book, source bytes and
  independent fixture digest; full two-symbol replay and FIFO/ledger checks.
- Full canonical/depth queries, pause/checkpoint, two coexisting full reconstructions,
  fragmented restart equivalence, publication/accounting and zero-leak assertions.
- The same reduced-PMR stop, exact journal-cap failure prefix and zero-budget check.
- First and last reached checkpoint allocation failures at full capacity, plus a
  full-capacity depth-allocation failure, with exact state/live-storage rollback.
- An exhaustive until-success checkpoint allocation sweep and depth failure on a
  separate authored eight-order-per-symbol fixture. Every reached failure in this
  smaller fixture must still preserve state and release storage.

The small fixture is not a substitute for full-capacity replay. Non-sanitizer
configurations retain the original exhaustive full-size sweep. Sanitizers no
longer sweep every intermediate allocation index of the full-size checkpoint;
that explicit coverage tradeoff is offset by the smaller exhaustive sweep,
full-size boundary injections, and unchanged full-size unsanitized sweeps. All
existing P1G/P1H allocation/adversarial tests remain enabled.

The Python verifier still independently reconstructs the original full fixture,
validates all prior outputs and five negative controls, rejects invalid numeric
profile arguments, and now reports which allocation workload was selected.
In bounded mode the reached-failure total includes the separate fault fixture;
existing PMR/allocations fields describe the main profile resource, not combined
process RSS. Both resources are bounded and independently checked for zero live
storage on destruction. Default native output schema and eight engine canonical identities are unchanged.
Only the checker summary gains an `allocation_profile` field. The 180-second
subprocess timeout is **unchanged**; no tests/assertions were removed or warnings
suppressed. Before repair, the old executable explicitly rejects the new option;
after repair both modes must satisfy the same main-profile independent checks.

Local timing comparisons are diagnostic samples, not native ARM throughput or a
causal benchmark under isolated CPUs. Final measurements and all raw commands,
versions, outcomes and hashes are bound by the companion JSON evidence.

## Job timeout and workflow safety

The existing ARM workflow remains byte-identical, manual-only, default-false
owner-gated and feature-ref restricted. The 60-minute job timeout remains unchanged:
it is a safety ceiling for fresh dependency builds, six separate configurations
and packaging, not a test-performance target. The reported isolated 180-second
probe failure does not justify expanding the overall ceiling. A future owner-run
qualification must review total build/test/package walltime, per-test durations
and `/usr/bin/time -v` data. If runtime remains excessive, retain diagnostics and
investigate; do not silently raise budgets or reduce core replay.

## Validation and delivery

Executed local results (x86_64, GCC 14.2 / Clang 19.1.7):

| Configuration | Passed / total | Failed / skipped |
|---|---:|---:|
| GCC Debug |154/154|0/0|
| GCC Release |154/154|0/0|
| GCC ASan+UBSan |154/154|0/0|
| Clang Debug |154/154|0/0|
| Clang Release |154/154|0/0|
| Clang ASan+UBSan |154/154|0/0|
| Python Debug |157/157|0/0|
| Python Release |157/157|0/0|
| Python ASan+UBSan |158/158|0/0|

Total: **1,396 executed CTest outcomes**, no failures/skips; all eight hashes match
in every configuration. Nine additional final-source profile rebuild/checks passed
(one per configuration). Both fresh installed consumers pass eight interface plus
six export tests each (**28 checks**); both research examples retain SHA256
`c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9`.
Three packaging pattern regressions pass; source archive inventory has 322 safe,
intended, byte-identical members at validation time. Packages were built from the
modified working tree before final documentation commit; source provenance is
not relabeled as the later commit. No new native ARM or hosted pass is claimed.

Three final local GCC sanitizer repetitions per mode measured median **5.730 s**
full sweep (range 5.671–8.018) versus **3.482 s** bounded sweep (3.440–3.815), with
Python sanitizer tests concurrently active. The full fixture digest remains
`9180c359dd0a21ef72f3c28638d2d9e304de106295115f0154077998d1b489eb`,
main-profile peak PMR 60,176,462 bytes. Full mode reaches 45 query faults; bounded
mode reaches 34 across its smaller exhaustive sweep and full-capacity boundaries.
These are finite local samples, not a guarantee of the next hosted duration.

See `NATIVE_ARM64_REPAIR_EVIDENCE.json` for executed configuration counts, all eight
canonical hashes, cross-toolchain reproduction, final profile timings, package
checks and raw artifact digests. Test/build artifacts remain private under
`build/arm64-repair/evidence`; no market data was acquired or committed.

Changed source/test files:

- `include/gig/analytics/exact.hpp`: portable checked multiplication.
- `tests/test_execution.cpp`: test-only direct wide-multiply reference protocol.
- `scripts/check_execution_reference.py`: independent Python integer boundaries.
- `benchmarks/itch_profile_probe.cpp`: bounded sanitizer allocation workload.
- `scripts/check_itch_profile_probe.py`: explicit mode forwarding/reporting.
- `benchmarks/CMakeLists.txt`: select bounded sweep only when ASan/UBSan enabled.

Documentation additions: this report and `NATIVE_ARM64_REPAIR_EVIDENCE.json`.
No workflow, main, matcher, journal, replay schema, raw fixture, broker or Terminal
change. No merge/tag/release/paid resource. Exact final commit is supplied after
push, avoiding a recursive self-hash in this document.

A new owner-approved native run is required before qualification can pass.
Owner should export actual run metadata, complete logs/JUnit, compiler versions,
all eight digests, Python/package output and sanitizer durations. RC13/RC17 remain
unclosed and RC18 remains partial; synthetic/cross evidence cannot close them.
