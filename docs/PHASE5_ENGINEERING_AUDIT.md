# Phase 5 adversarial engineering review

Scope: this phase's private journal representation, tests, measurement and readiness
changes. Algorithmically independent controls are not a separate human review or
independent machine. This report does not replace earlier institutional audits.
Final executed counts and artifacts are in PHASE5_ENGINEERING_REPORT.md and its
structured evidence.

| Area / source | Finding and classification | Validation / residual boundary |
|---|---|---|
| Ownership / `include/gig/replay/replay.hpp:55–66` | Owned MarketEvent unchanged; reset archive owns values, records use stable integer indices. No borrowed payload or deduplication lifetime risk. | Move-after-reset, canonical differential prefixes, sanitizers and cleanup. Allocator must still outlive engine; moved-from engine is only destroyed. |
| Bounds / `src/replay/replay.cpp:109–130` | Both geometrically grown vectors are capped by configured1–100000 entries; size/capacity arithmetic stays bounded. | Independent used/capacity byte ledger, non-power-of-two counts, cap/fault regressions. Per-entry remaining12KB footprint remains a scaling risk, not an unbounded container. |
| Atomic reset / `src/replay/replay.cpp:192–199` | Both reserves precede native mutation. Nothrow JournalRecord/RestartPlan construction plus reserved append capacity prevents post-native allocation failure. |16 new real injected reset failures, exact canonical equality after failure, single retry and move; existing replay32 fault sites cover additional operations. Capacity/statistics may change on rejection; accepted semantic state does not. |
| Archive integrity / `src/replay/replay.cpp:259–265` | Only private reset path creates an index; canonical export dereferences the corresponding owned plan in acceptance order. No load-from-untrusted-index API. |128 frozen canonical prefixes and existing independent oracles; no schema/hash change. This does not add cryptographic persistence or crash-safe journal recovery. |
| Recovery snapshots / `src/replay/replay.cpp:201–240` | Existing complete-order/all-stream boundaries, no rewind or partial message contradiction, native recovery then append. New archive unused for recovery. | Prior malformed/missing boundary/FIFO/allocation tests rerun. Native seed remains distinct from complete ITCH context; observed hot recovery unsupported. |
| Replay failure classification / `src/replay/replay.cpp:138–165` | Continuity/order errors deliberately set recovery-required diagnostic; invalid payload/capacity failures do not consume the event. | Existing independent sequencing/restart/reference suites plus new retry tests. Diagnostic state changes on continuity failure are intentional, not a broken strong semantic guarantee. |
| Provenance / native replay and `src/itch/context.cpp` | Full accepted metadata retained and canonicalized. ITCH source context checks pinned manifest/envelope conflicts; native stream contract checks venue/dataset identity/version/scope. | Existing source-seed/hash conflicts and export contradictory-digest tests retained. Native replay is not an archive authentication service; a retained digest claim is not independently verified source integrity. No observed certification allowed. |
| L3 initialization / readiness checker | Current gate always refuses observed certification, including all-positive claims.120 contradictory cases and2048 seeded adversarial documents add refusal coverage. | No fabricated seed/order/time/date; no new adapter or observed L3 instance. Missing capability remains an intentional scope blocker, not fixed by metadata claims. |
| Storage diagnostics / benchmark accounting | Logical JournalEntry remains15944; physical record12232. Updated ITCH benchmarks use physical storage accessor; book benchmark keeps logical metric and adds explicitly named physical metric. | Independent formulas, exact PMR allocation ledger, baseline binary retained. Logical DTO sizeof must not be advertised as current physical journal footprint. |
| Reset-heavy cost / archive capacities | All-reset used pairs cost8 extra bytes/event on this ABI; extra vector reserve sites and spare capacity are real costs. | Explicit no-reset/1-in64/all-reset measurements; no universal speed or memory reduction claim. Worst-case configured archive remains bounded. |
| Snapshot/provenance compaction | Not implemented: inline snapshot6624 and metadata5576 bytes dominate remaining size. | Further compaction would require a separate representation/atomicity plan and independent measurements. No speculative interning, arenas or persistence schema introduced. |
| Performance interpretation | Deterministic PMR improvement established; sequential shared-host timing and finite samples cannot isolate all causal effects. | Raw sizes, RSS, allocations and elapsed distributions retained; timing includes declared fixture/factory/reset checks/destruction. No tail-latency or exchange throughput promise. |
| Packaging / ABI | Python API/schema unchanged; ReplayEngine C++ object layout changes, so clients and wheels rebuild. | Source inventory, backend contamination controls and installed consumers required. No stable C++ binary ABI, manylinux, other CPython or ARM claim. |
| Platform / security | Current host x86_64; hosted API Forbidden; ARM execution tools/runner unavailable. Dependency advisory/backport applicability remains external. | No bypass, paid machine, silent dependency upgrade or green-CI inference. Prior RC13/16/17 blockers stay open. |

No new production correctness defect was reproduced in the audited paths. The
confirmed storage inefficiency was measured and repaired without changing logical
journal behavior. Local development-harness issues (initial test field spelling,
missing /usr/bin/time and PATH selection) were corrected before qualification;
these were not production engine defects and are not represented as engine fixes.
No failed mandatory regression was hidden or disabled. Absence of a reproduction
is not proof of absence of defects.
