# Native ARM64 run #2 — sanitizer linkage and runtime repair

October 24, 2026 (America/New_York). Starting development HEAD:
`86b6ce96aaa60e0d97dec4b70f6b9f7f997f699b`.

## Hosted evidence and limits

Owner-verified run **40119114285** tested that SHA. GCC/Clang Debug and Release
passed. Clang ASan+UBSan failed linking gig_flow_tests at
`src/analytics/flow_metrics.cpp:126`, undefined `__muloti4`. GCC ASan+UBSan passed
153/154 cases; the bounded allocation-profile child exceeded 180 seconds and
CTest total was **3508.83 seconds**. These exact run outcomes/timings are owner
provided, not independently downloaded. One `gh run view 40119114285 --log`
request returned exit 1 / Forbidden from api.github.com. No blocked retries,
workflow dispatch/rerun/cancel, configuration change or market-data request.

The current GitHub API remains outside the effective allowlist; runtime policy
state is unknown. Exact hosted tool versions, per-test durations, CPU scheduling,
RSS, sanitizer settings and unfinished child phases remain unavailable. Do not
infer actual native qualification from local tests or the following QEMU checks.

## 1. Confirmed remaining runtime-symbol cause

The first repair was incomplete: it removed the explicit signed 128-bit overflow
builtin, but missed raw signed-wide multiplication that UBSan can lower to the
same unavailable checked-multiply runtime helper. Before this repair, compiling
the actual flow_metrics.cpp using AArch64 Clang 18.1.3 at -O0 with UBSan leaves
`U __muloti4`. Linking the test with the target default GCC runtime reproduces:

```
/work/arm-repair/flow-before.cpp:126:(.text+0x3c00):
undefined reference to `__muloti4'
collect2: error: ld returned 1 exit status
```

The native hosted compiler version is not inferred from the local cross compiler.
This is a compiler/runtime integration failure, not proof of an overflowing market
input. In this specific midpoint path the validated price is signed-64-bit and
its reduced midpoint denominator is 1 or 2, so the product is within 65 bits.
Nevertheless, generic signed-wide UBSan lowering introduces the missing helper.

All primitive signed-wide products found in production source are now routed
through the existing portable `exact::checked_mul`:

| Site | Bound / preserved interpretation |
|---|---|
| Flow trade and quote count × 1e9 | At most 4096 observations per input; exact intensity numerator |
| Trade price × midpoint denominator | Denominator 1 or 2; exact comparison, including half ticks near INT64_MAX |
| Schedule interval × bin index | Nonnegative signed-64-bit time interval; at most 4096 bins; exact integer division follows |

No suppression, custom `__muloti4`, runtime substitution in the product, float
conversion or unchecked overflow was introduced. The helper performs an unsigned
magnitude bound check before multiplication; its symmetric signed-127-magnitude
capacity and rejection behavior are unchanged. The flow arithmetic-capacity handler remains in place; the validated schedule
product is bounded below 2^75 and cannot reach the helper's rejection boundary.

Audit: __int128 aliases occur only in exact.hpp; all Wide/Unsigned uses in source
and headers were inspected. Remaining primitive wide multiplication in the helper
and schedule allocation/participation is unsigned. Two uint64_t operands fit in
unsigned 128 bits; signed Fraction products use checked_mul. Wide additions,
subtractions and comparisons do not require this multiply helper. The relevant
input-count, price, time and sampling bounds were reviewed rather than assuming
arbitrary signed-wide operations safe.

After repair, both affected translation units compile with Clang AArch64 UBSan
at -O0, -O1 and -O3 with no undefined __muloti4. Targeted tests compile with Clang
UBSan at -O1 and link using target GCC's compatible UBSan runtime for this private
cross experiment; the remaining engine archive is the retained unsanitized GCC
AArch64 archive. Under QEMU, flow contracts and all four execution groups pass,
plus 2000 independent Fraction flow cases and 5129 execution/integer references.
This is **targeted mixed-toolchain cross/emulated evidence**, not whole-engine
ARM sanitization or a native hosted pass.

Regressions add half-tick trade signing/effective-spread cases near INT64_MAX and
a three-bin schedule spanning 0 to INT64_MAX, with independently calculated exact
decision times. Existing signed-wide boundary/overflow tests remain enabled.

## 2. Profile instrumentation and measured remaining work

`GIG_PROFILE_TRACE=1` enables stderr phase diagnostics in the probe. Each line
reports phase, elapsed microseconds, deterministic work count, PMR allocation
attempts, live bytes and peak bytes. The verifier validates exact phase ordering
and syntax; unexpected diagnostics are rejected. Timeout and nonzero child errors
now forward captured phase/sanitizer evidence before rethrowing. Four independent
unit controls prove timeout/child diagnostics survive and unexpected output is
rejected. Against the old verifier, two of those four controls fail; all four
pass after repair.

The bounded mode still executes the entire authored full-capacity profile:
2056 source records, 2048 native mutations, 128 live orders and 1024 journal records
per book, two full replay passes, checkpoint authentication, all final ledger/FIFO
and source-accounting checks, 16 MiB exhaustion, journal-cap rejection, zero-budget
failure, first/last full-size checkpoint failure, full-size depth failure, and
all 31 reached query failures on the eight-order exhaustive fault fixture. The
34 combined query failure checks and five independent negative controls remain.
There is no additional workload reduction or dropped mandatory check in this fix.

The old bounded fault sweep is no longer the dominant local component. Full feed,
restart/re-export/hash verification and the full journal-cap replay dominate the
instrumented -O0 workload. The following are per-phase medians from three local
GCC14 combined-ASan/UBSan processes per mode, same fixture and work counts:

| Phase | -O0 ms | -O1 ms |
|---|---:|---:|
| Full feed / invariant checks |819.699|195.723|
| Full canonical/depth exports |121.546|44.491|
| Full fault boundaries |368.678|122.360|
| Small exhaustive fault sweep |190.709|54.337|
| Checkpoint |239.949|66.640|
| Full restart and verification |1316.455|252.705|
| PMR-cap replay |257.635|51.996|
| Journal-cap replay / zero-budget |1051.594|194.138|

Median end-to-end checker walltime: **4.551 s -O0 versus 1.137 s -O1**. These local
samples overlap other qualification work and are not CPU-isolated or native ARM
measurements. Phase medians need not sum to median walltime. Work fields are
counts of records, export bytes or injected failures according to phase, not
uniform units. Both modes retain the same canonical fixture and 34 fault outcomes.

The measured source work is finite and makes progress locally; no local hang was
reproduced. The exact hosted slowdown cannot be established without actual phase
logs. In particular, it is not defensible to assert that hosted scheduling, a
specific sanitizer implementation, or a particular function caused all 3508.83 s.
The new logs make the next failure diagnosable rather than discarding partial
child stderr again.

## 3. Qualification configuration and scheduling

Only the feature-branch ARM workflow changes: ASan+UBSan jobs configure Debug
with `CMAKE_CXX_FLAGS_DEBUG="-g -O1"`. Assertions remain enabled (no NDEBUG), full
ASan+UBSan and fatal-on-error flags remain, frame pointers/debug information
remain, and strict warnings/-Werror remain. There is no no_sanitize attribute,
blacklist, disabled instrumentation or missing test. Fresh optimized sanitizer
builds run the full same suite and compare all eight canonical hashes. Four
intentional signed-overflow/use-after-free controls verify both sanitizer classes
still detect faults under combined instrumentation in GCC and Clang -O1 builds.
The initial control attempted an out-of-bounds write, which UBSan correctly caught
before ASan; it was changed to use-after-free to verify ASan distinctly.

All local existing -O0 sanitizer configurations are also rebuilt/tested, preserving
unoptimized coverage. The ordinary x86 six-job CI and default presets are unchanged.
No switch to Release/NDEBUG or larger runner. The hosted per-test child timeout
stays **180 seconds** and job ceiling stays **60 minutes**.

The workflow enables phase diagnostics and increases only retained CTest output
limits (16 KiB passed / 64 KiB failed). Default 1 KiB JUnit truncation otherwise
cut off the final phases and verifier summary. This does not increase execution
budgets or relax result checks. Diagnostic unit controls run before CTest. The
existing required CTest counts, zero-failure/skip assertions, all eight exact hash
checks and Python/package steps are unchanged.

Scheduling remains sequential within a job. Local per-case evidence identifies
L3 reference, book reference, fragmentation and repeated independent adversarial
checks as other material -O0 costs. Their fixtures/negative controls test distinct
properties and were not silently removed as performance repetitions. No newly
qualified shared-file/concurrent allocation-test schedule exists; adding -j merely
to fit the deadline could create interference and complicate memory attribution.
The scoped optimization instead retains all cases and processes at lower measured
instrumented cost. No hosted runtime guarantee is made; further optimization or
splitting requires actual phase/per-case evidence from owner-approved run #3.

## 4. Validation, delivery and remaining gates

Executed outcomes, compiler/configuration commands, all eight hashes, phase samples,
negative controls, package inventories and raw evidence hashes are in
`NATIVE_ARM64_RUN2_EVIDENCE.json`; raw logs remain privately under
`build/arm64-run2-repair/evidence`. Old reports/evidence are preserved.

Files modified: src/analytics/flow_metrics.cpp, src/execution/execution.cpp,
tests/test_execution.cpp, tests/test_flow_metrics.cpp,
benchmarks/itch_profile_probe.cpp, scripts/check_itch_profile_probe.py,
.github/workflows/native-arm64.yml. Added tests/test_profile_probe_diagnostics.py,
this report and its JSON evidence. No main, existing x86 workflow, exact arithmetic
API, journal storage, replay format, canonical fixtures, market-data or Terminal
change. No paid resource, merge, release or Actions dispatch/cancel/rerun.

**Readiness: locally validated candidate for owner-approved native run #3; native
qualification still NOT PASSED.** Confirm the feature ref/new SHA and free-runner
eligibility before owner dispatch. Require all six actual hosted jobs to pass,
all eight hashes/count checks, Python/package checks and inspect recorded phases
and total sanitizer walltime. RC13/RC17 remain unclosed and RC18 partial pending
reviewed actual hosted evidence; no empirical market L3 claim.
