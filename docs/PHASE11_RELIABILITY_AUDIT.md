# Phase 11 reliability and performance audit — October24,2026

Scope: frozen source ea2df47597fecb446013c902d2a74be4644ffdc0, later documentation
changes only. No production defect reproduced; no speculative patch or optimizer.
Prior source-level audit/remediation reports remain preserved. Algorithmic oracle
independence and a different target ISA are not an independent human or machine.

## Reliability and portability evidence

| Risk /actual source | Findings and evidence | Remaining limitation |
|---|---|---|
| Journal commit/ownership, replay.hpp and replay.cpp |Private index/archive reserves before native mutation; both post-success appends nothrow. Phase6 real reset failures16 sites, logical record/plan equality,32 lifecycle cycles/4128 events with balanced35552 allocations; new ARM tests pass unchanged. |Capacity may grow on rejection; metadata/snapshot storage remains large. No serialized journal loader/crash durability. |
| Recovery/session/ordering, replay.cpp and restart.cpp |Complete all-stream native snapshot boundaries, source version/scope and exact sequences; independent L3/original128-prefix comparisons retained. ARM independent L3 oracle10032 sessions/65186 candidates matches canonical. |Native snapshot lacks full ITCH context; trusted-start replay, not hot recovery. |
| Streaming integrity, gzip.cpp/binary_file.cpp/streaming.cpp |CRC/trailer/header/length/unknown/invalid/context/budget/allocation/restart suites retained. Phase6 independent699-prefix ×3 fragments passes on AArch64 too; every incomplete source refuses publication. |Exhaustive interruption applies to one stored-block fixture; no arbitrary real archive or all gzip coding proof. |
| Integer/alignment/lifetime, numeric.hpp/exact.hpp/decoder.cpp |Checked widths, explicit BE reads, no raw object serialization. AArch64 GCC13 strict Release compilation and154 distinct emulated tests pass. Actual char signedness/long-double precision differs but all8 canonical identities agree. |GNU/Clang128-bit extensions; native ARM/Python/sanitizers untested. Floating display/ABI need separate platform contract, not identical binaries. |
| Python wire and owning wrappers |Existing Fraction/range/enum/exception/ownership/installed-consumer and schema evidence from unchanged Phase6 source reused. Native models destroyed before owning PMR resource. |Catastrophic interpreter OOM need not construct a structured error; no ARM Python execution claim. |
| Provenance/publication |Source manifests and accepted receipt/hash boundaries remain pinned; synthetic never relabeled observed. Cross qualified source tree explicitly authenticated; no raw data request. |No observed initial seed, complete historical capture or independent observed-book reference. |
| Security /external platform |Phase10 current sources identify provider patch gaps; bounded trusted input scope preserved. Owner CI reports preserved without exact-SHA fabrication. |Security/independent-runner/hosted artifact gates remain blocked. |

AArch64 initial L3 timeout180s was a qualification execution limit, not a hidden
pass. Its unchanged900s retry succeeded578.83s. No warnings/assertions were disabled.
The initial zlib harness lacked make; existing CMake/Ninja built it instead. These
harness issues are documented separately from nonexistent engine repairs.

## Controlled native measurements

Twelve sequential x86 Release runs: each GCC14.2/Clang19 executes20,000-call pure
decode,32768-record framing/decode,256-order context,128 and192-order two-book
reconstruction, and192-order streaming/chunk31. Exact count/checksum/quantile/rate
formulas independently checked; all tracked bytes released. Two warmups and7
repetitions for batch tools; pure decode includes clock reads/no subtraction.
Six additional process runs (three/compiler) measure6144 journal records/reset17,
with independent capacity byte ledgers. Raw commands, seeds, fixture/binary hashes,
RSS, allocations and distributions: build/extended/evidence/phase11-measurements.json
and journal-{gcc,clang}-journal6144.json.

One QEMU L3 qualification job was concurrently active; native measurements are not
CPU-isolated. Reported timing is descriptive, not a causal optimization comparison
or exchange SLA. The equivalent128 reconstruction anchor exactly matches Phase5
fixture hash, receipt identity, checksum and peak PMR. New counts interpolate/
extend prior evidence; do not compare different event counts as a speedup. Phase5
before/after and Phase6 scaling remain historical measurements, not relabeled runs.

No new journal layout, arena, interning, hash structure or bulk decoder was justified
by these finite measurements. QEMU speed is emulator evidence, never native ARM
performance or a reason to optimize production code. The final report contains
actual measured values and clearly separates reusable x86 validation from new
cross/emulated execution.
