# Phase 8 independent Linux reproduction — October 24, 2026

**Strict independent-machine gate BLOCKED.** Runtime supplies no independent runner,
VM capability or outbound identity. Current Linux x86_64 and existing Ubuntu24.04
container share kernel6.18.55/daemon; neither is a new independent machine. Owner
CI observations are promising but cannot establish machine/source/test identity
without Phase7 artifacts. No paid resource or new remote service was provisioned.

## Exact reproduction contract for an authorized runner

Use frozen candidate ea2df47597fecb446013c902d2a74be4644ffdc0 (later documentation
commits must have their source delta compared). Fresh Git checkout that full SHA,
record `git rev-parse HEAD` and `git status --porcelain`, kernel, distro, CPU, runner
image/provider identity, compiler executables/versions, Python -VV and architecture.
A PR merge checkout is not silently substituted for this source.

Reuse CMakePresets.json and .github/workflows/ci.yml, not an invented parallel
build system. Reuse scripts/build_ci_zlib.sh in a new private prefix; retain official
source checksum, header/runtime1.3.1 and build log. Native streaming requires1.3.1;
Ubuntu system1.3 alone is insufficient. Install requirements-python.lock into a
fresh environment; archive exact wheel filenames/hashes, dependency inventory and
THIRD_PARTY_NOTICES.md. Keep normal proxy/TLS trust.

For each GCC/Clang compiler, run debug/release/asan-ubsan presets in separate clean
build directories or worktrees. Record configure/build commands and CMakeCache/
compile_commands, then CTest --output-junit. Require154 native outcomes, zero failed/
skipped/disabled, all8 hashes from PHASE6_OVERNIGHT_ENGINEERING_EVIDENCE.json and
128-prefix comparison. Enable Python on GCC Release as in CI:157 outcomes; record
extension build info. Optional full Python D/R/sanitizer counts157/157/158 remain
separate configurations, not claims about an unexecuted hosted matrix.

Build checkout wheel and sdist with pinned backend, inventory via
scripts/check_sdist_inventory.py, build a second wheel from that archive, install
each into fresh consumers and execute tests/test_python.py (8),
tests/test_export_contracts.py (6), examples/python_research.py. Confirm site-packages
paths and example SHA256 c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9.
Use only authenticated local source/dependency archives; no untrusted archive/XML
intake is cleared by this recipe. Rebuild sdists twice with fixed SOURCE_DATE_EPOCH
and compare bytes/member manifests; do not require wheels from different compilers
or architectures to be byte-identical.

Run journal_memory_probe at4097/8191/8192 with reset_every0/64/1, and qualified
ITCH profile128, reconstruction and streaming benchmarks. Record fixture identity,
seed, warmups/repetitions, PMR/RSS, raw samples, binary hashes and cleanup. Timings
on a different host are not automatic optimization evidence.

Archive full logs/JUnit, source/tree/artifact hashes, dependency identities and a
machine/source-bound manifest. Verify required outcomes against actual logs rather
than documentation claims. Previous shared-rootfs evidence remains useful but
cannot close RC13. This phase prepares an executable recipe; no new independently
hosted run is claimed.
