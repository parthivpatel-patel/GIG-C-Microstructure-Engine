# P1D — Level 3 reconstruction requirements

Status: **PROPOSED VALIDATION REQUIREMENTS; NO ADAPTER IMPLEMENTATION**. Offline review
against `183ac12d0a4cc5e3587820ecbba19e5cbaf2d03d`, October 22, 2026 (America/New_York).
The S1–S3/C1–C4 references and their exact official document identities are defined in
[ITCH_50_VALIDATION_DESIGN.md](ITCH_50_VALIDATION_DESIGN.md). P denotes a proposed
harness policy; Q denotes unresolved market/source semantics. No new dataset evidence
or test pass follows from this design.

## Scope and reuse

[PHASE_2_BOOK.md](PHASE_2_BOOK.md) and [PHASE_2_REPLAY.md](PHASE_2_REPLAY.md) already
specify implemented ownership, mutation, sequencing and atomicity. This document
adds the evidence required to claim a real NASDAQ displayed-book reconstruction and
identifies adapter gaps. [REAL_MARKET_DATA_FEASIBILITY.md](REAL_MARKET_DATA_FEASIBILITY.md)
section G owns reference-depth comparison and coverage denominators; the P1D
[acceptance matrix](REAL_DATA_REPLAY_ACCEPTANCE_MATRIX.md) makes those ideas executable
as proposed tests. No matcher, synthetic liquidity, auction allocation or hidden-order
model is part of this reconstruction scope.

A displayed NASDAQ book is not NBBO, all trading in a listed instrument, the hidden
book, or an execution simulation. Validity must be reported separately for framing,
source coverage, displayed state, trade tape, session semantics and research outputs.
A valid book-only projection may intentionally exclude known non-book records while
retaining/counting them externally; it must not claim complete ITCH semantics.

## Initialization: evidence, not a convenient constructor flag

Current C4 initial_state defaults to requires_snapshot; apply and healthy depth are
blocked until recovery. Declared-empty is an input assertion, not a detector that a
historical source began empty (`src/replay/replay.cpp:38–49`).

Two admissible routes:

| Route | Evidence required | Current limitation |
|---|---|---|
| Empty boundary plus history | External session/date/venue identity, authoritative capture/start semantics establishing empty displayed state before all relevant orders, complete initialization/order spin and subsequent relevant history | S1's Start of Messages/Start of System Hours/Start of Market Hours codes are distinct, but their presence alone does not prove a selected file includes all required state; actual archive remains uninspected |
| Complete order-level state | Real live order IDs, side, remaining shares, prices, same-price FIFO priorities, complete coverage, included source boundaries for every configured native stream | C2 Snapshot max64 orders and8 boundaries; C3/C4 reject aggregate or bounded-depth recovery; larger genuine snapshots need a separate capability decision |

Pre-market and carried-order representation, historical archive start semantics and
date-specific clock are Q until source evidence is available. Do not assume every
2019 archive starts at a useful empty boundary. No inference from a favorable later
snapshot, no backfill from later cancels, no synthetic one-order-per-level bootstrap,
and no FIFO reconstruction from aggregated quantities. Multiple complete recoveries
replace state; they cannot append chunks of a larger initial snapshot (C3 recover).

If initial state is unknown, decoding/inventory can succeed but displayed-book
validity remains unavailable. Do not instantiate a declared-empty replay and label
its partial depth healthy. Known local empty synthetic fixtures are different: their
manifest explicitly establishes an authored initial state and never claims observation.

## Identity and FIFO invariants

S1 §1.3 describes day-unique order references. P: bind native identity to declared
venue/instrument/session/epoch with a verified daily reference namespace; retain
original uint64 references without hashing, truncation, sign conversion or fabricated
positive values. C3 rejects duplicate *live* IDs; it does not keep a day-long retired-ID
set. A future bounded adapter lifetime ledger is required to detect an illicit
same-day reused reference after deletion. Its capacity and commit semantics must be
explicit, not an unbounded leak. A new day's reference/locate reuse is distinct from
a duplicate within the same day. Do not silently start a new epoch to excuse reuse.

Source streams scope continuity, not order ownership (C4 and existing book contract).
An order on one configured stream can be referenced by another if the declared venue
namespace supports that. Raw channel-local IDs require a reviewed mapping; no such
namespace complication is assumed away or introduced for BinaryFile without evidence.

C3 per-price FIFO must preserve these observable invariants:

- Each active ID has exactly one list node and matching hash-index entry; each node
  belongs to one side/price level. Levels have no empty containers.
- Remaining sizes are positive and bounded; level quantities/order counts and total
  remaining quantity agree with nodes, without uint64 overflow.
- Local FIFO ranks strictly increase within a level; retained reductions preserve
  rank. New adds and priority-losing replacements append, with no priority wrap.
- Best prices/depth are sorted and internally consistent. Locked books are permitted;
  bid>ask is rejected at each native committed boundary, including recovery.
- Ledger reconciles checked credits and debits; revisions, IDs, cursor and journal
  position do not partially advance on a rejected mutation.

S1 identified executions need not be forced onto the FIFO head by the reconstructor.
C3 explicitly permits a known non-head fill while preserving surviving queue order
(`tests/test_book.cpp:54–64`). Preserving the represented FIFO is not independently
proving NASDAQ matching/hidden/reserve allocation rules. Same-price aggregate matches
can hide incorrect ID/priority histories, so an order-level oracle is required too.

## Source-to-core semantics and capability boundaries

| S1 source | Required displayed reconstruction behavior | Current support / future boundary |
|---|---|---|
| A/F displayed add (§1.3) | Require known registry/date context, unused reference, side, exact display price and shares; append once | Core AddOrder implemented; participant attribution and original fields stay in external envelope; daily historical uniqueness is adapter work |
| E execution (§1.4.1) | Resolve known resting ID/side/price; decrement executed shares, remove if zero | BookExecution implemented; match number is not native; never infer aggressor or execute unknown IDs |
| C execution with price (§1.4.2) | Decrement displayed shares while preserving actual execution price and printable Y/N externally | Core requires execution price=resting price. Full single-event semantics missing. A reviewed book-only projection can use resting price for decrement but must not present that as observed trade price or feed complete tape/TCA |
| X partial cancel (§1.4.3) | Subtract cancelled shares, not overwrite with new remainder | CancelOrder positive delta implemented; missing order/underflow rejects. P: an X cancelling all remaining shares is a semantic anomaly under the partial-cancel wording, recorded/stopped pending approved source policy; core itself permits an equal-sized reduction |
| D delete (§1.4.4) | Remove all known remaining shares once | CancelAll implemented. Unknown reference is invalid state, not a zero-sized successful deletion |
| U replace (§1.4.5) | Remove old remainder, adopt new reference/total quantity/price, inherit side/symbol/MPID | Atomic ReplaceOrder implemented. P: lose-priority projection until exchange priority eligibility is explicitly approved; S1 field semantics alone do not prove every NASDAQ priority rule. Retain-only-same-price-reduction mode must not be selected opportunistically |
| P non-cross non-displayed trade (§1.5.1) | No displayed-book change | TradePrint observation implemented. Modern reference0 and sideB are not displayed ID or aggressor evidence; keep aggressor missing |
| Q cross (§1.5.2) | Preserve cross identity/price/size; do not allocate visible fills or clear arbitrary orders | Positive print projection only; S1 allows zero-share Q, incompatible with current priced-quantity validator. External observation disposition needed for that case; auction semantics missing |
| B broken trade (§1.5.3) | No current displayed-book effect per S1 | External book-only disposition allowed if declared; no native match-ID correction/undo contract for tape/statistics. Never restore liquidity from a broken print |
| S lifecycle (§1.1) | Retain O/S/Q/M/E/C event codes separately; no implicit clear on market/end-system-hours marker | SessionEvent has only open/halt/resume/close. Raw codes/context remain external; source lifecycle is richer. Deletes/breaks may follow end-system-hours; End of Messages is distinct |
| H / h status (§§1.2.2,1.2.8) | Keep halt, pause, quotation-only, trading and venue-specific operational status separate | Core SessionEvent is a nonmutating observation, not a gate. H Q is not full trading resume; h for BX/PSX must not halt Nasdaq implicitly |
| Other administrative/imbalance/collar records | Preserve exact schema/fields and prove non-book disposition where excluded | Decode/context inventory may support them; no native allocation/auction/Reg-SHO/participant simulator. Unknown records are not proved nonmutating |

C3 crossing rejection can conflict with a legitimate source intermediate state that
requires multiple records before it becomes uncrossed. Such a segment is a capability
blocker, not permission to reorder, clamp prices, match orders away or hide records.
One source record must not become two native mutations without a reviewed atomic
compound-record design: C4 run commits prefixes, not an all-or-nothing group. No
compound execution/print repair is implemented in P1D.

A raw global control's locate0 cannot be turned into an exchange-assigned InstrumentId.
Current complete native metadata requires an instrument (C1). P: initially consume
such controls in a separate external session/context layer, preserving raw order and
classifications. If later fanned out to one target book, label that instrument binding
as a normalization context, not an observed source field. Do not fake a Quote or
SessionEvent merely to advance a cursor through an unsupported wire type.

## Source order, filtering and session integrity

S2 BinaryFile supplies order and external session identity, not exchange per-message
sequence numbers. S1 tracking number is internal tracking. P: retain immutable global
decoded ordinal and byte offset. If producing a selected native event stream, give
it a documented **derived contiguous sequence**, preserving a complete source-to-event
map; retain actual exchange sequence only when verified transport metadata supplies it.
Do not relabel a filtered gap as network loss or claim local contiguity proves no
upstream exchange events were absent.

C4 supports one target book plus up to8 additional configured instrument rules; it
is not a whole-market multi-book router. Passing every other symbol as a filtered
native event still consumes journal and requires configured instrument rules. A
future source classifier may exclude other instruments before core replay only
with a declared normalized-dataset scope, source coverage map and retained global
controls. That is different from asserting continuity of a raw exchange stream.
Reject conflicting or unknown target identity rather than guessing what to filter.
Never drop target mutations, deeper orders or unknown state-affecting messages.

Use capture-ordinal order, not timestamp sorting. Native capture ordinal is per
canonical event, strictly increasing; it is distinct from repeated packet/source
identity or subevent count. Event-unit native sequence requires index0/count1; message
subevents need a complete declared extent. Time ties/regressions remain observations.
Actual time conversion and source-date handling follow the clock rule in the wire
design; unknown receive times remain missing.

At file/session transitions require explicit old/new boundaries and reset/recovery
policy; do not concatenate days or rebase ordinals to hide a discontinuity. A native
reset consumes a valid old-scope boundary and complete restart plan; it cannot repair
a detected source gap by asserting empty state. Recovery needs real complete state,
not the last aggregate reference row. Unsupported large snapshots are a blocker.

## When state must be declared invalid or unavailable

| Trigger | Required result |
|---|---|
| Missing initial-state evidence | Displayed state unavailable from the start; parser-only outcomes permitted, no eligible reconstruction coverage |
| Missing target order, illegal ID reuse, duplicate/conflicting add, symbol/locate conflict | Stop strict application at first failure; displayed-state validity false after last good prefix |
| Target quantity underflow, unit/range/enum failure, crossed state, unsupported target mutation | Reject without committing; record exact reason; do not continue native healthy-depth comparisons |
| Native sequence/order/session fault | Existing replay sets needs_recovery; book/cursors/journal remain committed prefix, diagnostic state may change |
| Payload/allocator/capacity failure | Core often returns without setting needs_recovery; harness must nevertheless stop/mark current attempt incomplete, and must not mistake native flag=false for full-input validity |
| Unknown source type/profile, framing loss or source integrity contradiction | No verified continuation; raw inspection can preserve diagnostics but accepted reconstruction stops |
| Known non-book print/status unsupported in native projection | Explicit external disposition allowed only if justified; do not invalidate displayed state merely because tape/auction semantics are excluded, and do not label those domains complete |
| Declared budget cutoff at complete boundary | Valid bounded prefix may remain valid if its initial state was valid; full-session completeness false; no source-truncation accusation |
| Actual incomplete source EOF / decompression-integrity failure | Input/session integrity invalid. Preserve any previously observed prefix, but do not mark the run a verified complete artifact |

No invalidity is silently repaired by observation of a later matching reference.
Physical read position, raw decoded position, last native commit and last eligible
comparison are distinct report fields. Resource/transient retry may be tested at
the exact unconsumed logical position after diagnosis, without reapplying earlier
committed events. No automatic recovery or data correction is authorized here.

## Independent reference-model requirements

Use a simple separately maintained order list/dictionary plus per-price sorted
arrival ranks, arbitrary-precision aggregate/ledger calculations and explicit source
lifetime/status ledgers. Do not reuse C3 container operations, canonical serializer,
normalizer, wire decoder or fixed-width numeric helpers as the oracle. Existing
`tests/support/book_reference.hpp` and book/replay test groups are useful core
regressions; they do not replace an independent wire decoder and exchange-semantic
review. Future Python reference arithmetic is a test oracle, not a production runtime
dependency. Hand-audited byte vectors challenge shared specification misunderstandings.

After every eligible synthetic mutation compare exact IDs, sides, prices, remaining
sizes, FIFO order/rank relationships, best prices, depth, total remaining and ledger.
Check failure invariance separately. Source-provided reference depth, when permitted
and actually obtained, must be parsed independently and aligned by a predeclared
source boundary; do not choose an offset by maximizing matches. Compare exact prices
and quantities at the reference's available depth; unknown deeper liquidity is not
zero. Full source/native comparison requires an actual reference artifact, not an
expected book computed only by the same normalizer being tested.

### Proposed synthetic lifecycle oracle

Declared synthetic empty state/registry; buy-price quantum and quantities are exact:

| Step | Input semantic event | Expected orders and observable result |
|---|---|---|
| 1 | A101 buy10@100 | ID101 qty10, FIFO rank0, total10 |
| 2 | A102 buy20@100 | FIFO101 then102; total30; ID102 rank1 |
| 3 | E102 qty4 | Non-head fill accepted; quantities10/16; ranks unchanged; total26 |
| 4 | X101 qty3 | ID101 qty7; total23; FIFO unchanged |
| 5 | D101 | ID101 absent, ID102 qty16; total16 |
| 6 | U102->103 buy15@101, lose priority | Only ID103 qty15@101/rank2; total15; old102 absent |

Exact final ledger: added30, cancelled10, executed4, replacement_out16,
replacement_in15; total_in45, total_out30, remaining15. Interleave a print and halt:
orders/depth/quantities remain unchanged, while accepted observation revision/journal
can advance. A subsequent same-day Add101 is rejected by the proposed lifetime layer,
even though current core alone could accept a no-longer-live ID. End-of-session
reference reuse is a separate synthetic session test, not an implicit same-day reset.

## Remaining decisions before real replay

Rights/retention and applicable historical profile; actual initial state/completeness;
UTC interpretation; target normalization scope; exchange replacement priority policy;
C execution/tape contract; legitimate crossed intermediate handling; independently
available reference states; and required snapshot/journal capacity remain open.
[MEMORY_STREAMING_DESIGN.md](MEMORY_STREAMING_DESIGN.md) specifies resource stop rules.
No data acquisition or adapter implementation is needed to build the proposed
synthetic tests in a separately authorized next phase.
