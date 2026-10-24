# Phase 9 ARM64 portability — October 24, 2026

**Cross-compilation succeeded; QEMU user-mode qualification in progress. Native
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

The full154-case CTest run uses the same assertions and fixtures. Its initial
qualification-only180s timeout was too short for itch.l3_reference under emulation;
that timeout is preserved, not counted passed. Other reference tests demonstrate
substantial emulation cost (auction reference ~145s). Only the timed-out oracle
is rerun with900s allowance; original project assertions/data are unchanged and
project CMake sets no such timeout. Final actual counts/hashes will be bound in
PHASE12_RELEASE_CANDIDATE_REPORT.md and the structured evidence. No completed
ARM matrix or native performance is claimed while execution is pending.

Reproduce using recorded cross compiler, CMAKE_SYSTEM_NAME=Linux,
CMAKE_SYSTEM_PROCESSOR=aarch64, CMAKE_CXX_COMPILER=aarch64-linux-gnu-g++, explicit
ARM ZLIB_INCLUDE_DIR/ZLIB_LIBRARY_RELEASE, Python OFF and unchanged test presets.
Preserve ELF and wrapper hashes, full logs/JUnit and source identity. Native
hardware, ARM Python installation and target sanitizers require separate actual
execution; RC18 cannot become PASS from these cross/emulated observations alone.
