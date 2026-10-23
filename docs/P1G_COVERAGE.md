# P1G synthetic reconstruction acceptance coverage

Baseline: `1855a2f7a4d4ef472b61ffa5fd3b6b1a76acf282`, feature branch
`feat/bootstrap-cpp20-engine`. This is an implementation-to-requirement map, not
independent evidence that every registered test has executed. The final frozen-source
compiler, sanitizer, packaging and benchmark results belong in
`P1G_VALIDATION_REPORT.md`. Earlier P1E/P1F evidence remains separate.

At this document's initial preparation, focused native development evidence contains
12 passing CTest outcomes in `build/p1g/evidence/focused-native.xml`. The additional
checkpoint development run reports 32 reached allocation failpoints and the separate
Python `hashlib` comparison reports 1,268 cases in
`build/p1g/evidence/restart-focused.json`. These are focused results, not the final
GCC/Clang or Python matrix. The independent L3 campaign and final configuration matrix
must be recorded from their actual executed outputs before the P1G gate is closed.

## Requirement map

CTest names below refer to registrations in `CMakeLists.txt`. Native reconstruction
groups are implemented in `tests/test_itch_reconstruction.cpp` unless another file is
named. The Python model in `scripts/check_itch_l3_reference.py` derives expected
source/context/book states from independently decoded bytes, uses `Fraction`, and
compares full semantic fields through `tests/itch_l3_reference_driver.cpp`.

| Gate | Implemented assertions and independent expectation | Evidence state and limits |
|---|---|---|
| G01 initialization blockers | `itch.reconstruction_initialization`: unknown, incomplete, invalid and complete-seed kinds, absent complete-history declaration, arbitrary boundary, contradictory scope, observed origin and unknown context initialization all reject creation. `itch.reconstruction_recovery_boundary` rejects aggregate/bounded native recovery. | Focused assertions passed. S/O is an observation and cannot replace authored initialization evidence. Inspection without reconstruction remains available through P1E/P1F, not an eligible native book. |
| G02 authored empty boundary | `initialization` accepts only the explicit synthetic source/session/hash/seed/boundary contract; `multisymbol` and the L3 oracle compare declared routing and native sequences. | Caller-authored evidence must be independently verified by the fixture runner. The C++ factory validates consistency; it does not certify origin or prove a caller's generator assertion. |
| G03 64/65 seed boundary | `initialization` and `recovery_boundary` construct 64 literal orders/ranks and assert exact native recovery; the 65th append and forged count65 reject atomically. Aggregate/bounded recovery rejects; complete-seed adapter creation rejects. | Native64 support is tested; adapter complete-context seeding remains deliberately unsupported. Sequential snapshots are not an append mechanism. |
| G04 literal six-step ledger | `golden`; framing `prefix_truth`; Python oracle literal fixture. Expected final10315@101, added30/cancelled10/executed4/replacement_in15/replacement_out16/total_in45/total_out30 are authored arithmetic. | Focused native assertions passed. Independent campaign execution/hash must be taken from its actual final run. |
| G05 attributed lifecycle | `golden` F→U→full E checks inherited MPID, exact new/retired references and no remaining native/context orders. Oracle attributed fixtures compare context state. | Implemented and focused native assertions passed; no interpretation of MPID as an executing counterparty. |
| G06 partial/full reductions | `golden` checks surviving tickets and non-head quantities; full E retires both representations. Oracle tests partial/full E/X/D and zero/over-reduction; existing context policies test equal-X selection. | Native and context behavior preserve selected explicit equality policy. No automatic repair of rejected source input. |
| G07 replacement priority | `golden`, `atomicity`, and oracle replacement fixtures compare new tickets and retired identities; same-price U uses lose priority. | No claim of historical priority certification. Source ID reuse remains forbidden by the selected session policy. |
| G08 identified non-head execution | `golden` executes102 while101 remains head; framing literal prefix and independent flat-book model check both orders. Oracle negative control deliberately redirects the reduction to the head. | Implemented; this is reconstruction rather than simulated aggressive matching. |
| G09 C semantics | `observations` rejects default-disabled C before context/native commit; explicit opt-in checks native resting price100 against retained actual price123/printableN. Oracle includes differing price and printable controls. | Book-only route is explicit. No native tape/TCA equivalence, second print, or execution-price substitution is claimed. |
| G10 P/Q/B observations | `observations` checks unchanged displayed state and journal, zero-size Q, and B's broken-match flag without liquidity restoration; oracle compares match and receipt state. | Typed source observations are retained; no resting order or allocation is inferred. |
| G11 reference errors | `golden`, `multisymbol`, `observations`, old context identity/provenance cases, and oracle directed/adversarial candidates cover missing, retired, duplicate, wrong-locate and Q-origin references. | Explicit rejection/unsupported classification; rejected records cannot be silently skipped. |
| G12 two-symbol isolation | `multisymbol` checks independently remaining7/16, counts2/2, sequences1/1 and global capture ordinals5/6. Oracle compares both books after every source candidate. | Maximum two configured books; no all-market routing claim. |
| G13 global identity namespace | `multisymbol` rejects a source ID reused on the second symbol while preserving both books. Oracle has an explicit duplicate-across-symbol fixture. | This is the declared P1F global session namespace, not a claim about every historical feed profile. |
| G14 unknown/unsupported scope | `multisymbol` rejects undeclared locate3 before directory commit; oracle exercises H/unknown types. Existing decoder regressions distinguish unsupported and unknown wire types. | The minimal adapter has no declared other-scope filter: all non-S records must belong to a configured binding. Unconfigured symbols stop rather than being discarded. |
| G15 native metadata and provenance | `initialization` checks contradictory source hash/seed/origin/scope, missing seed, configuration errors and nonprintable bindings; `numeric` tests an overlong derived source-record identity. Oracle compares native dataset/version/policy/hash/seed/lineage/parent and missing timestamps. | Required immutable manifest tokens are construction-time fields; missing required fields cannot form a valid config. Policy is an internal synthetic-fixture policy, not a NASDAQ license. |
| G16 clock semantics | `multisymbol` asserts unavailable native event/receive time. Oracle exercises raw48-bit maximum, regressing timestamps and explicit monotonic policy; existing context numeric/policy tests preserve raw bounds. | No date, UTC clock, receive time or exchange sequence is invented. |
| G17 exact units | `numeric`: rational conversions, off-unit rejection, zero-preserving helpers, invalid scales, UINT64_MAX ID/lot boundaries, UINT32_MAX shares, Price(4) maximum and multiplication overflow. Python oracle independently uses `Fraction`. | Helpers do not apply instrument min/max rules; projection validates actual native events before commitment. Profiles also require the P1F integer hints to agree with full instrument rules. |
| G18 source/native sequences | `multisymbol`, `observations`, framing prefix truth and oracle receipts compare source ordinals/locations versus per-book contiguous sequence and journal count. | External observations consume no native journal entry or native sequence. Tracking numbers remain raw observations. |
| G19 locked/crossed book | `atomicity` accepts locked bid=ask and rejects crossed A and U with unchanged context/book/journal/receipt prefix. | Crossing remains a native incompatibility; no matching, reordering or synthetic corrective event is introduced. |
| G20 prepared transaction guard | `itch.context_prepare` checks read-only prepare, owned source bytes, wrong-owner/stale/consumed/moved token rejection, context movement/finish, same-address object lifetime reuse and discard rollback. `atomicity` uses an allocator callback to test process/finish reentrancy rejection. | Move-only fixed deltas and private friend-only finalization prevent a public unsafe commit bypass. Moving/destroying an object during its active member call remains a caller lifetime violation. |
| G21 native allocation atomicity | `allocation` sweeps direct native first-add5, adapter add6 and adapter U5 reached allocation requests. Each rejected adapter attempt preserves accepted book/journal/context summary/receipts/counts and the exact native replay cursor; exact-record retry commits once. | These are actual allocator failures. Tests found the pre-existing first-insert hash-bucket defect; the new direct regression fails against baseline source and passes with staged reserve. Capacity retention is not semantic state. |
| G22 initial storage/receipt bounds | `allocation` sweeps6 factory allocation requests with zero retained live bytes after failure; `budgets` checks receipt byte preflight and hard PMR rejection. Full receipt storage is reserved before any native event. | Source-receipt capacity cannot fail after successful native application. Config bindings are fixed-size owned values, not a dynamically growing registry. |
| G23 exact retry | Every adapter add/U injected resource failure is followed by the same-byte/same-position successful retry; receipt/context accepted counts advance exactly once. `atomicity` rejects a changed record while the failed source record is held. | Resource failures are pending; semantic failures are rejected. Both preserve held identity until restart or the exact admissible retry. |
| G24 postcommit query failure | `allocation` arms the PMR resource after successful native/context/receipt commits, observes canonical-query failure and confirms unchanged accepted state after disabling failure for inspection. | Failed query returns an error instead of a complete artifact. There is no filesystem publication or artifact writer in this adapter; output retry must query/export, not reapply source. |
| G25 checkpoint/restart | `itch.reconstruction_checkpoint`, `tests/test_itch_restart.cpp`: prefix capture independently rebuilds from byte0, compares full context/receipts and native canonical hashes; restart rejects changed source/config/implementation and five corrupted descriptor fields, then compares suffix replay without duplication. Rebuild fault sweep covers32 reached allocation requests. | Trusted in-memory descriptor with integrity hashes, not a MAC, origin authentication, hot snapshot restore, gzip seek or crash-safe recovery. Nonuniform raw provenance is explicitly unsupported. |
| G26 recovery diagnostics | Existing `replay.continuity`, `replay.gaps`, `replay.reset`, `replay.recovery` and book recovery regressions remain unchanged. The adapter exposes no reset/clear-diagnostics operation; native recovery-required state is never automatically cleared. | Adapter-owned derived sequences prevent manufacturing a replay gap through normal input. Existing native tests are the direct diagnostic oracle; final regression execution remains required. |
| G27 overflow/exhaustion | `numeric`, existing `itch.context_numeric` and native `replay.gaps` test exact numeric/byte/ordinal/sequence boundaries. Adapter considered count is factory-capped at100,000 and native counts/tickets cannot exceed considered source records. | Adapter UINT64 counter/ticket exhaustion is unreachable through the supported bounded factory; do not describe it as an executed UINT64_MAX adapter run. No unchecked increment is justified by an unbounded input stream. |
| G28 all resource caps | `budgets`: source cap+1, unconsidered-tail completion, receipt preflight, lifetime retention after D, native active-order cap, journal cap, adapter match and native level cap/cap+1, and tiny shared PMR. Match/level stops compare the exact accepted context/native prefix and disjoint accounting. | Adapter match/level gaps found during review were closed with explicit integration fixtures before source freeze. Final executed matrix remains authoritative. Hard128MiB is a caller resource policy demonstrated by drivers, not an implicit cap on default PMR. |
| G29 all cuts/fragments | `itch.reconstruction_framing`, `tests/test_itch_reconstruction_framing.cpp`: literal507-byte/18-record trace,2,027 fragment/cut schedules and one trailing-byte control. Each complete frame checks literal prefix state, order membership, FIFO, quantities and journal counts. | Bounded cutoff and malformed EOF are distinct; partial frames never enter reconstruction. Focused XML records the actual schedule count. |
| G30 adversarial campaign | L3 oracle source contains1,000 seeded grammar sessions with invalid tails plus9,000 independently malformed/context-invalid tails; requires at least10,000 actual rejected candidates and compares all emitted semantic fields. Six deliberately incorrect model expectations exercise the comparator. | Registered as `itch.l3_reference` and `itch.l3_oracle_negative_control`. Final executed counts, seed and canonical digest must be recorded; fixture code alone is not a passed campaign. |
| G31 full toolchain/regression gate | Nine supported build configurations, existing C++/Python tests, source-built and installed-wheel checks, P1E/P1F/L3 deterministic outputs. | Final matrix not executed at initial preparation. Record every actual failure/skip/disabled count and source freeze in the final validation report; do not infer this gate from focused tests. |
| G32 memory/failure measurement | Native tests release all tracked storage on destruction, factory/mutation/restart failures and fragmented replay; hard PMR caps produce controlled rejection; canonical query failure preserves accepted state. | Peak/shared-resource/RSS and retained-category measurements are separate benchmark evidence. Caller-owned resources must outlive every object. RSS is not the same measure as logical reserved bytes. |
| G33 performance baseline | `benchmarks/itch_reconstruction_benchmark.cpp` and `scripts/check_itch_reconstruction_benchmark.py` provide a deterministic correctness-checked fixture and timing harness. | Measurements unrun at initial preparation; require actual Release repetitions, fixture/compiler/source identities, allocation counts, journal growth and process RSS before reporting results. No institutional SLA or exchange-performance inference. |
| G34 observed data exclusion | Synthetic fixture/source declarations, explicit unsupported complete-seed/historical profile and separate NASDAQ readiness ledger. | No market data acquired or empirical snapshot comparison performed. Licensing, historical profile, actual source integrity, initialization and independent observed reference remain separate real-market gates. |

## Failure-atomicity boundary

Preparation is a const operation producing owned fixed-size deltas. Existing source
context vectors are completely reserved at construction and element copy/move
operations have nonthrowing assertions. The adapter privately owns its context,
checks token ownership/generation before native application, blocks processing and
finish reentrancy, and pre-reserves all source receipts. Native application is the
sole fallible mutation after preparation. Its success is followed by private context
commit, fixed receipt append and bounded counter updates; no validation, serialization
or new allocation follows.

The allocation campaign additionally exposed a native first-add defect: an empty
`unordered_map` can report a sentinel bucket while still needing its first real bucket
allocation. The previous condition skipped reserve at that boundary, allowing the
final index-node insertion to throw after FIFO/level transfer. Staging that reserve
before transfer closes the defect. The direct first-add regression checks no residual
order, level, quantity, revision or ledger change after each failure, then retries the
same native event once. This is a correctness repair, not a journal optimization.

## Explicit limitations

- Synthetic authored-empty start only; no valid observed initialization claim or
  positive complete-context seed implementation.
- At most two configured books. No automatic other-scope filtering, halt adaptation,
  auctions, hidden-order reconstruction, tape correction replay or cross clearing.
- Context lookup/retirement and match histories remain bounded linear storage; the
  existing15,944-byte journal-entry baseline is preserved.
- Restart reconstructs an isolated fresh instance from an integrity-checked framed
  prefix. The caller supplies that prefix and trusted descriptor; this is not yet
  bounded gzip streaming or persistence/crash recovery.
- A full compiler/sanitizer/package matrix, independent campaign and measured baseline
  must be attached to the actual implementation commit before closing P1G. Hosted CI,
  ARM64 and observed-market validation remain unverified unless separately executed.
