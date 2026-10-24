# Phase 9 ARM64 portability — October 24, 2026

**Cross-compilation and all154 distinct Release C++ tests under QEMU passed. Native
ARM64 and ARM Python extension qualification remain NOT RUN.** This is not an
independent machine: x86_64 Ubuntu24.04 container shares the original host kernel.

Official signed Ubuntu packages installed only as qualification tools: GCC13.3
AArch64 cross compiler and qemu-user8.2.2 distribution1:8.2.2+ds-0ubuntu1.18,
target glibc2.39-0ubuntu8cross1/libstdc++14.2 cross runtime.27 packages added,0
upgraded; no candidate dependency or host kernel/network configuration changed.
No binfmt registration, privileged container or paid infrastructure.

Frozen source ea2df47597fecb446013c902d2a74be4644ffdc0 was exported to a fresh
/work/extended/source. Existing authenticated zlib1.3.1 source was cross-built
into /work/extended/arm-zlib. An initial configure/make harness found make absent;
qualification resumed with existing CMake/Ninja, preserving that log. Engine
Release cross-build115 steps completed with -O3 -DNDEBUG -Werror and streaming/
benchmarks/tests enabled, Python bindings disabled. No production patch required.

Executable ELF headers were checked for machine183/AArch64. Each original ELF
was preserved as .aarch64-elf; private shell wrappers invoke explicitly:
`/usr/bin/qemu-aarch64 -L /usr/aarch64-linux-gnu ELF "$@"`.
This lets host-Python independent reference scripts invoke target executables
without pretending host Python itself is ARM64. Wrappers are qualification-only,
not candidate source or distributed binaries. Actual scripts/logs/manifests are
under build/extended/evidence and /work/extended in the existing container.

Measured ABI: pointer8,long8,long double16, journal physical record12232 and
DecodedRecord304 bytes. x86 plain char is signed/long-double precision64 bits;
AArch64 plain char is unsigned/precision113 bits. Canonical contracts use explicit
integer widths/decimal fields, not raw object memory. Wire decoding is explicitly
big-endian; allocation headers preserve max_align_t. exact.hpp uses GNU/Clang
128-bit integers/checked builtins, supported by this target but not a universal
C++ compiler guarantee. No engine atomic/concurrent algorithm is introduced.
Display-level long-double differences must not be confused with exact rational
contracts; cross-architecture binary files are not required to be identical.

The initial full154-case CTest run passed153 and timed out only itch.l3_reference
at the qualification-only180s allowance. That failure is retained. A targeted retry
with900s allowance passed in578.83s, executing all10032 sessions/65186 candidates
with unchanged assertions. Across these two invocations,154 distinct tests passed,
zero remaining failures/skips, and all8 canonical hashes equal the x86 baseline.
This is not an initial single-run154/154 result or native performance evidence.
Other reference tests also have substantial QEMU cost. No engine/test assertion,
data or canonical contract was changed to pass. ARM Debug, sanitizers and Python
bindings remain NOT RUN. Final counts and ELF/wrapper/JUnit hashes are recorded in
build/extended/evidence/arm-results.json and the final structured candidate evidence.

Reproduce using recorded cross compiler, CMAKE_SYSTEM_NAME=Linux,
CMAKE_SYSTEM_PROCESSOR=aarch64, CMAKE_CXX_COMPILER=aarch64-linux-gnu-g++, explicit
ARM ZLIB_INCLUDE_DIR/ZLIB_LIBRARY_RELEASE, Python OFF and unchanged test presets.
Preserve ELF and wrapper hashes, full logs/JUnit and source identity. Native
hardware, ARM Python installation and target sanitizers require separate actual
execution; RC18 cannot become PASS from these cross/emulated observations alone.
