# P1G — independent synthetic L3 validation design (proposed)

No test below has been implemented or executed by this planning phase. The verified
P1F baseline is85 native outcomes per configuration, 88 Python Debug/Release and 89
Python ASan/UBSan,775 total across nine builds. Preserve its two oracle hashes and
all existing tests. New counts must be generated from actual registrations/results,
not obtained by adding this table's rows to an old total.

## Independent oracle architecture

Proposed files: `scripts/check_itch_l3_reference.py`,
`tests/itch_reconstruction_reference_driver.cpp`, `tests/test_itch_reconstruction.cpp`,
`tests/test_itch_context_prepare.cpp`, and small synthetic-only golden fixtures under
`fixtures/itch/`. Production proposals are described in
[P1G_ARCHITECTURE_PLAN.md](P1G_ARCHITECTURE_PLAN.md). None of these proposed source
files exists as a result of this planning work.

The Python reference must independently implement source-byte decoding for the enabled
profile, context/retirement/match lifecycle, target routing, Fraction-based units,
flat active-order records, per-book insertion tickets and ledger arithmetic. Do not
consume production normalized output as the expected event. Do not share native
mutation helpers, generated decoder tables, serializers, quantity arithmetic or FIFO
containers. Existing P1E/P1F models and the flat C++ core reference remain separate
regressions and useful cross-checks, not the sole new integration oracle.

Before calling the native driver, compute literal/generator truth for each source
candidate and expected dispositions. After every candidate compare:

- Source identity, physical locations/ordinal, context commit prefix, full directory,
  lifetime and match state, normalization settings/version and eligibility evidence.
- Target instrument, native source-record linkage, derived sequence/capture ordinal,
  journal count, book revision and documented diagnostic state.
- Every active ID, side, exact price/quantity, within-level FIFO order, number of orders,
  depth, best prices, total remaining and each ledger category.
- External observations, unsupported/rejected records, pending state, comparison coverage
  and incomplete/complete flags. No zero-eligible run can claim 100% market validation.

Use oracle-known IDs with `OrderBook::find`, count equality and independently sorted
priority/order views to detect missing and extra IDs. Do not compare only best bid/ask
or trust `check_invariants` as independent proof. Export the driver's actual semantic
fields; production canonical hash equality alone is insufficient. Exact internal
priority tickets can be asserted for authored empty-start fixtures; contextual global
arrival ordinals are not numerically identical to per-book tickets.

A test mismatch must identify fixture/config hashes, seed, input index, frame/payload
offsets, source event and book, expected versus actual field and first divergent state.
Keep diagnostics bounded and synthetic. Validate the comparator with known wrong
models: endian/scale error, non-head execution forced to head, priority retained on U,
broken-trade liquidity restoration, wrong routing and a one-row alignment shift.

## Proposed acceptance matrix

Every row requires a deliberate assertion, independent expectation and recorded
pass/fail. Rows can contain multiple cases; none is an already passed P1G outcome.

| ID | Fixture/trigger | Independent oracle and measurable acceptance |
|---|---|---|
| G01 | Unknown start, only S/O, timestamp09:30, aggregate/bounded snapshot | Literal manifest truth: zero eligible L3 publications and explicit initialization blocker; inventory remains separate |
| G02 | Authored complete empty synthetic start with frozen source/config hashes | Manifest plus independently generated initial state: eligible only for declared symbols and exact boundary |
| G03 | Complete64-order seed,65 orders, missing retired/match context | Preserve existing core recovery regressions and add a hand-checked 64/65-order native boundary fixture; adapter positive seed remains explicitly unsupported until full context-seed API exists; reject65/aggregate/incomplete seed atomically |
| G04 | Literal A10110@100,A10220@100,E1024,X1013,D101,U102->10315@101 | Independent table: final10315@101; added30, cancelled10, executed4, replacement_out16, replacement_in15, total_in45,total_out30; compare every step and native FIFO |
| G05 | F then U and further E/X/D | Side/symbol/attribution inherited; old reference retired, new identity used; no source ID hashing/truncation |
| G06 | Same-price partial reductions and full reductions | Surviving order priority unchanged; full reduction removes ID and empty level; zero/over-reduction rejects |
| G07 | U same-price reduction, increase, different price and ID collisions | Declared lose policy always obtains a new per-book ticket; duplicate/new-retired reference fails before old order changes |
| G08 | E targets second order in same-price queue | Identified ID decremented, head preserved; independent flat list detects an erroneous simulated head fill |
| G09 | C actual price differs from resting, printableN/Y | Default-disabled book-only route explicitly blocks; enabled route decrements at native resting price, retains actual price/flag externally, no invented print/cancel or TCA/trade-tape output |
| G10 | P sideB/reference0; Q zero/positive size; known B | No book state/priority/native journal/sequence change; context match/correction state updates; B never restores quantity |
| G11 | Missing, duplicate, retired, cross-book or Q-origin correction references | Exact context/unsupported disposition; no native mutation or hidden record skip |
| G12 | Interleaved two symbols, opposite sides, repeated tracking/time ties | Independent books/depth/ledgers/sequences; source order retained; unrelated book unchanged on every step |
| G13 | Same raw ID reused in another symbol within declared global namespace | Global P1F lifetime rejection even though two independent core books could otherwise accept it |
| G14 | Known declared other scope versus unknown binding/type, H/h, later enum | Explicit disjoint accounting or blocked source; no fabricated instrument or silently filtered target mutation |
| G15 | Missing dataset/version/license-policy/seed/parent, long source token, contradictory digest | Complete metadata validation rejects before any commit; synthetic internal policy never presented as NASDAQ rights |
| G16 | Raw48-bit time, regression, missing clock/receive time | Preserve source; native time unavailable where clock not established; capture ordering unchanged; no UTC invention |
| G17 | Tick/lot Fraction boundaries, Price(4) max, uint64 ID high bit, overflow/off-unit | Exact integer domain values or precise rejection; no signed-ID loss, double or truncation; compare Fraction independently |
| G18 | Derived sequences with S/R/P/Q/B and other-book records between mutations | Per-book contiguous native sequences, source ordinal gaps allowed; complete source mapping and no exchange-sequence claim |
| G19 | Locked then deliberately crossed add/U | Locked allowed; cross rejected preserving context/native accepted state; no source reordering or simulated matching repair |
| G20 | Failure after prepare, stale/consumed/wrong-owner token, move/reentrancy attempt | Zero native calls for invalid tokens; no context mutation; post-success hook proven nofail/noalloc; no callable unsafe public bypass |
| G21 | Native journal/book allocation failure, capacity, quantity/ledger limit | Sweep every reached allocation site; accepted context/book/cursors/journal/receipt prefixes unchanged; documented diagnostic/capacity differences preserved |
| G22 | Receipt/outbox/binding allocation or cap failure | Stop before engine apply; no unrecorded native commit or late allocation in final commit section |
| G23 | Exact-position resource retry | One successful application only; no doubled execution, derived sequence or journal; source hash/location unchanged |
| G24 | Error after native commit while exporting/reporting | Artifacts incomplete, state remains committed; retry output only; no reapply disguised as export recovery |
| G25 | Deterministic checkpoint/restart from authored beginning | New adapter replays authenticated committed prefix; all context/book/cursor/receipt hashes equal; changed source/config invalidates descriptor |
| G26 | Native replay gap/duplicate and explicit reset/recovery diagnostics | Preserve old native tests; adapter cannot clear recovery by empty reset or claim global multi-book atomic recovery |
| G27 | Byte/ordinal/derived sequence/ticket/counter exhaustion | Checked stop at first prohibited step, no wrap or silent partial commit; independent integer calculation |
| G28 | Caps at cap/cap+1 for source, active/lifetime/match/levels/journal/receipts | No eviction/truncation; finite controlled stop and exact processed/pending/tail accounting; totals unavailable when not inventoried |
| G29 | Cut at every frame boundary/interior byte and all chunk splits of goldens | Identical complete-prefix semantics; actual truncation versus bounded cutoff distinct; no publication of incomplete frame |
| G30 | Seeded lifecycle grammar and corrupt/mutation campaign | At least10,000 bounded candidates; expected outcome and state after each, deterministic seed/first failure; zero crash/OOB/UB/unbounded growth |
| G31 | GCC/Clang Debug/Release/ASan+UBSan and replay reruns | Exact same non-timing semantic outputs; zero failure/error/disabled/skipped required outcomes; P1E/P1F hashes preserved |
| G32 | Memory destruction/recreation and query/export/restart peaks | Tracked live bytes return to baseline; hard PMR cap enforced; query/export allocation failure correctly classified; process RSS separately measured |
| G33 | Independent Release fixture baseline | Two warmups, at least 3 measured passes; actual counts and canonical hashes verified before timing; raw batch measurements, CPU/RSS and compiler/build/source identities retained; no invented SLA |
| G34 | Real sample, archive or external observed snapshot requested | Explicit unrun/blocked status; no license inference, network retry, acquisition or empirical-validation claim in synthetic P1G |

## Joint transaction failure proof

Enumerate preparation, metadata/conversion, receipt reservation, replay journal reserve,
book level/list/index allocation and rehash. Inject failure at every reached real
allocation request; disabling the failing resource is allowed for post-error inspection,
not to conceal a production retry. Compare semantic state and separately record retained
capacity/needs_recovery diagnostics. If a native failure marks continuity invalid,
stop and require the declared reconstruction restart path; do not reset diagnostics
just to retry successfully.

The final context/receipt commit after successful native apply must contain no
allocation, serialization, external call or new failing validation. Test an armed
allocator at that point. The private prepared-token invariant must mechanically
prevent a stale hook call, not merely rely on a comment. Use sanitizers plus explicit
nothrow type assertions. No deep-copying the full book per event as a shortcut.

## Determinism and end-to-end golden traces

Freeze input byte fixtures, manifests, scope/unit/priority policies and seeds. Generate
expected order membership and source/native disposition traces independently. Compare
all non-timing outputs across every build and repeated chunk schedule; hash both full
field output and fixture/config identity. Include the literal six-step ledger in G04,
a second symbol interleaved between each step, C differing execution price, P/Q/B
observations, and first-invalid records at each boundary. Do not choose alignment by
maximizing a later snapshot match or invent source snapshots from the production book.

Native canonical output is a useful exact checkpoint within the same version; the
oracle must additionally compare fields and explain harmless representation changes.
Preserve P1E context/wire golden hashes unless an independently justified versioned
contract change is separately reviewed. Oracle independence does not prove proprietary
exchange implementation equivalence or absence of all correlated spec misunderstandings.

## Validation execution and evidence

Extend existing CMake/CTest targets without editing old assertions or suppressions.
Run GCC/Clang Debug, Release and ASan/UBSan, plus the current GCC Python Debug/Release/
sanitizer configurations and installed source-built-wheel interface/export/example
checks. Native sanitizers retain normal leak detection; Python's existing live-LSan
control/late-finalization limitation remains explicit. ARM64/other OS/Python combinations
and hosted Actions are separate evidence, never inferred from local builds.

During implementation run focused new targets first. Freeze sources before the final
matrix to avoid stale incremental objects; after edits rebuild affected targets before
reusing results. Record each configuration's actual JUnit counts, code/source/config/
compiler hashes and oracle digest. Preserve failed development logs separately from
final passing evidence. Documentation-only planning does not need another85/88/89 rerun.

Before new performance measurement pass correctness/oracle gates, use unsanitized
Release without LTO shortcuts, and measure one workload at a time from a clean verified
code commit. Report state size, per-operation scope, allocations, retained-history and
journal growth, batch averages versus service samples and shared-host limitations.
No performance optimization is accepted without semantic identity and benchmark
comparison against this recorded baseline.
