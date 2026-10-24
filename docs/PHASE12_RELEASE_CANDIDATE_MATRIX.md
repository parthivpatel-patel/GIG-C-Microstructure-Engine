# Phase 12 release-candidate matrix — October24,2026

> **October 24, 2026 closure update (America/New_York):** Native Linux ARM64
> qualification is CLOSED at f02363e0e09b9767b4dc6748737206254e5e4c6a.
> Run40126420107 and all six job successes are independently verified from official
> public GitHub pages. See [current qualification and readiness overlay](NATIVE_ARM64_QUALIFICATION.md)
> and its structured evidence. Current RC18 is PASS scoped; RC13 and RC17 are
> PARTIAL, RC16/security and observed-market gates remain blocked. Aggregate:
> 19 scoped PASS / 5 BLOCKED / 2 PARTIAL / 1 OUT OF SCOPE.
> The report below is preserved historical source-bound evidence; its ARM-not-run,
> API-only access blocker, old counts/source-equivalence and owner actions do not
> override the newer closure. No raw hosted log/JUnit export is claimed.


Candidate source: ea2df47597fecb446013c902d2a74be4644ffdc0. Production/test/build tree equals Phase6 tested195cb11431bda150e28a1232bc4c8c735769d81d; later commits modify documentation only. Exact source-equivalence checked by Git diff. All scoped passes refer to that source; blocked gates have no qualifying tested commit, as explained below.

| Gate | Status | Source-bound evidence / remaining requirement |
|---|---|---|
| RC01 source/history |PASS scoped|Candidate ea2df475; current commits documentation-only, exact remote checks; main unchanged.|
| RC02 correctness repairs |PASS scoped |No new reproduced unresolved production defect; no speculative repair. Prior remediation evidence preserved. |
| RC03 joint transaction |PASS scoped |Prepared context/native atomic contract retained; allocation failures and new observation isolation tests pass. |
| RC04 initialization/scope |PASS scoped |Authored synthetic-only factory unchanged; machine gate refuses observed claims, unknown/partial state never promoted. |
| RC05 numerics/semantics |PASS scoped |All prior independent numerics preserved; new exact Price4/uint64/time-field wire references and malformed boundaries. No new floating conversion. |
| RC06 unsupported/lifecycle |PASS scoped |V1–v3 unchanged; explicit retained2023 v4 types, contextual cancel/symbol/session rules; unknown types stop. Typed observation is not native auction execution. |
| RC07 streaming publication |PASS scoped|Retained1396-outcome x86 qualification plus154 distinct AArch64 emulated cases; interruption/CRC/source publication guards preserved.|
| RC08 source accounting |PASS scoped |New prefix reference counts native/external/receipts/journals independently; no accepted record omitted or duplicated across2097 schedules.|
| RC09 restart |PASS scoped |New profile-bound checkpoint/replay, fragmented input equivalence and prior independent restart regressions; no hot/crash-durable claim. |
| RC10 independent oracles |PASS scoped|All8 canonical identities equal across x86 and AArch64 emulation; independent L3 retry65186 candidates/10032 sessions. Not outside-human/machine attestation.|
| RC11 toolchain matrix |PASS scoped|Unchanged x86 source matches Phase6 tested195cb114;1396 retained outcomes,4 GCC13 focus; new AArch64 Release153 initial passes +1 unchanged retry pass.|
| RC12 Python boundary |PASS scoped|Existing qualified CPython3.12 x86 artifacts/APIs unchanged; no ARM Python binding or other ABI claim.|
| RC13 strict independent machine |BLOCKED|No genuinely independent machine supplied. Same-host Ubuntu and QEMU cannot close this gate; Phase8 recipe ready.|
| RC14 memory |PASS scoped|12232-byte physical record, Phase5/6 byte ledgers; new6144/reset17 rows and ARM ABI agree; no full-market capacity promise.|
| RC15 measured performance |PASS scoped|12 new native workload runs +6 journal processes; raw stats/independent count/quantile checks. Concurrent QEMU/no CPU isolation, no causal speedup or ARM performance claim.|
| RC16 security applicability |BLOCKED|Current security source/path review: managed OpenSSL3.5.8 versus3.5.9 fixes; CPython/Expat/provider/vendor mapping unresolved.12 PyPI feeds empty does not clear.|
| RC17 hosted CI |BLOCKED|Owner reports #128/#129 success and6 green jobs; API Forbidden, exact IDs/tested SHAs/logs/6 warnings not independently archived.|
| RC18 other platforms |PARTIAL|GCC13 AArch64 cross Release and154 distinct QEMU cases pass,8 matching hashes. Native ARM, target Python/sanitizers/Debug NOT RUN.|
| RC19 docs/evidence |PASS scoped|Source-bound manifests, timeout preserved, owner observations separated from verified artifacts; final source package/evidence checks.|
| RC20 repository/data hygiene |PASS scoped|No market-data request, no LOBSTER retry, no tracked binaries/secrets or Terminal/live changes. Tool installation limited to qualification container.|
| RC21 distribution |BLOCKED |No authorization to publish/distribute candidate or raw data; private Git engineering commits do not change rights. |
| RC22 private artifacts |PASS scoped|Previous source/wheel qualification preserved; final current documentation source inventory/hash recorded separately, no public distribution.|
| RC23 observed artifact/profile |BLOCKED, partial prefix evidence |1433 complete observed S/R/H/Y messages and local context agree; full artifact integrity/session/profile and unobserved types remain unverified. This replaces earlier NOT RUN only for the current overlay. |
| RC24 observed initial L3 |BLOCKED |No authenticated complete empty boundary/history or complete context/FIFO seed; machine refuses certification. |
| RC25 observed reference |BLOCKED |No aligned independent observed book/queue/snapshot reference or empirical reconstruction comparison. |
| RC26 research interpretation |PASS scoped |Synthetic software/exactness claims only; no calibrated queue/impact/alpha/causal/statistical generalization inferred from prefix decoding. |
| RC27 production operations |OUT OF SCOPE |No crash durability/HA/live broker/exchange/Terminal work or production readiness claim. |

Totals:18 scoped PASS,7 BLOCKED,1 PARTIAL,1 OUT OF SCOPE. RC18 improves from NOT RUN to partial cross/emulated evidence; it does not become native PASS. No other external gate is closed.

Readiness: private synthetic evaluation GO within tested scope; formal candidate closure BLOCKED; historical ITCH compatibility retained-profile only; observed L3 NO-GO; production trading OUT OF SCOPE.
