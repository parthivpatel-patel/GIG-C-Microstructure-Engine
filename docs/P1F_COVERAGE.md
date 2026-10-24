# P1F coverage ledger

This ledger describes executed synthetic P1F coverage at implementation commit
`e4aeb76d98087441a7ed33c491173a633e8d7e37`. Results and artifact hashes are in
[P1F_VALIDATION_REPORT.md](P1F_VALIDATION_REPORT.md) and
[P1F_EVIDENCE.json](P1F_EVIDENCE.json). It supplements the historical
[P1E matrix](P1E_MATRIX_COVERAGE.md); it does not mark all 62 P1D rows complete.

| Executed CTest group | Direct requirements and representative assertions |
|---|---|
| `itch.context_lifecycle` | A/E/X/D/U transitions; non-head identified reduction; full execution retirement; retained reference uniqueness; source arrival annotation |
| `itch.context_identity` | F attribution and U inheritance; duplicate, zero, unknown and retired references; over-reduction and equal-X rejection; multi-symbol locate ownership; idempotent/conflicting/blank directory; explicit new session |
| `itch.context_observations` | C observed versus resting price; P/Q nonmutation; Q zero shares; B correction without restoration; missing/duplicate/Q-origin break; duplicate match; explicit unknown/unsupported outcomes |
| `itch.context_policies` | O/S/Q/M/E/C observations without reset; deletes after end-system-hours; timestamp ties/regressions/day boundary/full48 preservation; permissive incomplete-history observation; bounded/complete local session flags; malformed side |
| `itch.context_limits` | Directory/lifetime cap stop without retirement eviction; storage budget rejection; size-arithmetic overflow |
| `itch.context_allocation` | Real failure at each of three creation allocation sites; rollback/deallocation; zero incremental allocation under armed failure; moved-from rejection |
| `itch.context_numeric` | Maximum references/matches/shares/price; exact reduction; off-unit hints without rounding; policy/version ownership; invalid finish; independent byte/ordinal exhaustion; no L3 eligibility |
| `itch.context_provenance` | Owned raw and manifest provenance; seed/source/digest conflicts; honest missing values; physical gap; explicit full-X policy; match-capacity rejection before decrement |
| `itch.context_reference` | Independent dictionaries and byte packing; 515 sessions, 12,104 full-output/state comparisons, 10,000 randomized semantic mutations; all supported families; finish and rejection atomicity |
| `itch.context_oracle_negative_control` | Four bad expected models detected: wrong remaining quantity, retired reuse, liquidity restoration, event alignment |
| `itch.context_benchmark_correctness` | Independent A/X/U/E byte fixture, counts, checksum, fingerprint and reservation accounting |

All 11 groups pass in all nine configurations. The 74 pre-P1F native outcomes
(including all nine P1E outcomes) remain active and pass. Python Debug/Release add
three existing groups; the Python sanitizer build adds its existing live-LSan
control. These are CTest outcomes, distinct from internal unittest/oracle case counts.

## Relationship to P1D requirements

P1F adds direct context evidence for D07–D11, I01–I02 annotation boundaries, S02–S05
identity/quantity implications, Q02–Q04 source-order/disposition boundaries, Q07
lifecycle observation, and A/R/T component-level failure, resource and determinism
requirements. These are **partial broader-row coverage**, not ITCH-to-native or L3
acceptance. In particular:

- D07/D08 cover bounded declared-scope mapping and explicit new-context identity;
  actual trading-day certification and history remain unresolved.
- D09 preserves unsupported control semantics rather than decoding V/W/K.
- S01–S07 do not receive a new native FIFO/depth/ledger oracle in P1F.
- Q01/Q05/Q06 do not receive source-to-native sequence, compound commit or recovery integration.
- A01–A04 prove context-local atomicity, not joint context/native/I/O transaction atomicity.
- R01/R02/R04 cover context reservations and failure safety, not a complete decompressor,
  engine, output collector or process-tree resource budget.
- T03 does not yet contain an independent ITCH-driven flat L3 book model.
- P01 receives scoped measurements, not full event-tail/service distributions or a speedup claim.

Gzip Z01–Z05, native integration, initialization eligibility and all eight observed-data
gates remain deferred. P1E's exact historical coverage classifications are preserved
in its report rather than rewritten as if P1F had existed then. No unexecuted test,
zero-reference coverage or external-market gate is labeled passed here.
