# Phase4 replay, streaming, Python and adversarial review

Review scope: actual native source, retained specification, new synthetic fixtures,
existing independent replay/streaming oracles and Python/packaging contracts.
No observed L3 or external-human/machine audit is implied by algorithmic independence.
Final actual execution evidence is in PHASE4_HISTORICAL_ENGINEERING_REPORT.md.

| Finding | Classification /severity | Evidence, disposition and measurable gate |
|---|---|---|
| Observed L3 initialization/integration unavailable |Intentional scope gap /High for any observed certification |`SyntheticReconstructor::create` still requires authored-empty synthetic origin/seed/hash; `metadata` is generated-synthetic. Prefix directory admission is not initial order state. Machine readiness refuses all claims until observed adapter, complete context/native seed and independent observed book reference actually exist. |
| K binary price versus contradictory prose |Authoritative-document ambiguity /Medium |Retained §1.2.6 table says4-byte Price(4); general Data Types says unsigned BE integer fixed-point, while prose describes incompatible ASCII-like widths. Explicit retained2023 v4 uses normative type/table, never guesses two codecs. V1–v3 reject K unchanged; actual historical K remains unobserved/unverified. |
| Later auction fields are not2019 evidence |Evidence-backed applicability risk /Medium |O and NOII direction P introduced2023, NOII cross A2022 in AppendixA. V4 deliberately names retained2023. Near-time raw64 preserved with no invented time unit. Independent wire/context models verify local contract only. |
| Event ordering and recovery |Implemented, no new defect reproduced |`src/replay/replay.cpp::advance/order_check/reset/recover` validates dataset/venue/scope, exact sequence/subevent counts, capture or common-UTC/rank ordering, all-stream complete-order snapshot boundaries and recovery-required state. Existing duplicate/gap/order/invalid-snapshot/fault/reference tests rerun. Not an ITCH full-context seed or crash-safe persistence API. |
| Journal capacity and atomicity |Implemented bounded behavior; memory risk /Medium |`reserve_record` before native mutation, nothrow stored records, post-success cursor commit; cap100000. New forced1-entry/book schedule stops at9accepted/2native, with explicit error and no publication; no source record is silently treated as accepted.15,944-byte entry remains a scaling concern. No journal representation change. |
| Context normalization atomicity |Implemented |New K cancel contradictions, bad locates/stocks/fields reject before accepted cursor/state mutation; context prepared tokens/private native transaction unchanged. Three actual reserve fault sites, allocation-free observations,33 streaming fault sites; all owner cleanup checked. New observations change no native order/ledger/FIFO/sequence/journal state. |
| Fragmentation/error accounting |Implemented |Ten new fault variants across1/65536-byte schedules independently expect22/7,5/0,3/0,8/1 or9/2 accepted/native prefixes as appropriate; accepted=native+external, same accepted hash/error family across fragmentation; no publication. CRC and truncated trailers remain distinct from deliberate bounded prefix. |
| Unknown/unsupported events |Implemented |Unknown type is an explicit stop; v1/v2/v3 still stop on K/J/I/O, v4 accepts only the retained23 layouts. No skip-to-next accepted state after an error. Stateless inventory reports outcomes separately from context acceptance. |
| Status versus book state |Implemented |K/J/I/O typed external observations; raw prices/64-bit aggregates/time retained, no unit rounding or synthetic order/execution. K source locate stays0 while an exact symbol routes its receipt to a configured book. Direct tests cover both book bindings and source/provenance retention. |
| Streaming pointer lifetime |Implemented, reviewed |Gzip owned stable state/output buffer, framer copies partial payload, normalized/source records own fields; pending read-ahead span remains owned through moves. Existing move/pause/deferred-CRC/restart regressions rerun; ASan/UBSan evidence in final matrix. No speculative refactor. |
| Prefix accounting can be mistaken for session completion |Evidence-backed interpretation risk /Medium |Observed inspector's scope_complete flag means independent model coverage, not complete exchange source/session. Gzip member/CRC/terminal absent, initialization unknown. Source publication and local session flags remain distinct. Readiness checker emits BLOCKED/exit1; no inferred calendar state. |
| Python numeric/ownership boundary |Implemented, unchanged |`python/bindings/wire.hpp` strict canonical integer strings/from_chars, exact bools/enums, bounded list/string/record keys; module Replay/Simulation own PMR before model member and destroy model first, export copied dictionaries/strings. `api/mutate` convert ordinary wire/arithmetic/allocation errors; success response prepared before native mutation. Existing interface/export/Fraction/ownership/recovery regressions and fresh consumers rerun. Catastrophic Python OOM may prevent even constructing an error object; no process-survival guarantee. |
| Python provenance/export integrity |Implemented, unchanged |Existing schemas/references/dataset digest contradiction controls and installed package exports preserved. New native ITCH DTOs are not silently coerced into Python MarketEvent schemas or relabeled observed/synthetic. No new Python auction API is advertised. |
| JSON readiness tool |Implemented conservative audit |Bounded64KiB input, strict schema/keys/states, duplicate-key rejection, defensive output copy, synthetic/unknown-state and forged-positive negative controls. Declared claims are not attestations. Static unavailable-capability list must be updated only with future source/evidence review; current tool cannot certify observed L3. |
| Packaging contamination |Implemented gate |Pinned backend's root-anchored required files and ordinary ignore rules unchanged; source member inventory, three existing include/cache regressions and fresh checkout/source wheels required. No raw data, private environments, binary build outputs or unknown links may enter tracked artifacts. |
| Performance attribution |Evidence limitation /Medium |Pure decode timing includes two clock reads, no subtraction; batch context/reconstruction/gzip tools include their stated factory/allocation/validation/destruction costs. Counts/checksums/quantiles independently recalculated. No latency SLA, exchange claim, causal speedup or unjustified optimization. |
| Security/independent hosted evidence |External blockers /High for formal closure |Prior RC13 independent-machine, RC16 provider advisory/backport applicability and RC17 hosted CI remain unresolved. No secret/network/security-provider checks fabricated to close them. Trusted local artifact parsing only; process/resource caps do not certify dependencies. |

## Failure variants and independent reference expectations

1. CRC corruption: all22 source/7 native records can be a valid provisional prefix,
   but full input integrity/publication fails.
2. Truncated gzip trailer: same accepted prefix, incomplete source, no publication.
3. Complete gzip containing incomplete BinaryFile terminator: framing fails even
   though container CRC verifies; accepted22/native7, no complete publication.
4. Payload limit49 rejects I's50-byte record:5accepted/0native.
5. Invalid I direction enum:5accepted/0native.
6. Contradictory K cancellation fields:3accepted/0native.
7. Duplicated first add identity:8accepted/1native; no duplicate source commit.
8. Native journal limit1/book:9accepted/2native, explicit capacity boundary.
9. Source-record budget3:3accepted/0native; next framed record unaccepted explicitly.
10. Unknown message octet:3accepted/0native, explicit unsupported-source outcome.

These are authored source-level expectations, not copied production counts.
Existing broader suites still cover arithmetic boundaries, source/session metadata
contradictions, faulty snapshots, sequencing, clock policy, all-stream recovery and
allocation cleanup. New v4 oracle independently checks40129 wire cases and16960
context candidates, plus wrong expected wire/context negative controls.

No new production replay/journal/gzip/Python defect was reproduced in this review;
none was speculatively repaired. Absence of a reproduction does not prove the
absence of bugs. A future confirmed defect requires retained failing-before case,
minimal repair and independent regression before its evidence can be called PASS.

## Performance and memory disposition

Linear context vectors give bounded deterministic storage and linear directory/
order/match lookup; active-order summary recount scans retained order state. There
is no hash map to tune in this path. Reserve/grow journal copies and fixed inline
MarketEvent payloads dominate measured retained-byte risk; gzip's one-byte policy
is conservative for deterministic limit behavior. Any replacement needs an isolated
same-fixture profile and oracle/failure/restart equivalence, not intuition.

New NOII member ordering fits the previous largest wire alternative without packed
layout or alias tricks; static relative-size assertion and measured Message48/
DecodedRecord304 preserve prior receipt/context budgets. This is a layout design
constraint, not a claimed measured runtime optimization. No broad journal, hash-map,
allocation, cache or branch rewrite is justified solely by current batch timings.
The controlled benchmark/source measurements and residual stage-attribution limits
are recorded in the final report; optimization is deferred rather than invented.
