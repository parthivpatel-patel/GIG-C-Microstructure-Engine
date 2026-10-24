# P1F — synthetic ITCH source-context design and limits

P1F adds a **synthetic-only semantic context layer**, separate from the existing
native book, replay engine and Python interface. This document records its design
and local admission policies; the P1F validation report owns actual test outcomes.
No observed NASDAQ archive, historical-profile certification, market-data license,
complete initial L3 state or native integration is established here.

## Contract basis and responsibility

The retained official document identities and hashes remain in
[ITCH_50_VALIDATION_DESIGN.md](ITCH_50_VALIDATION_DESIGN.md). In this document **S1**
means that retained TotalView-ITCH 5.0 specification (retrieved layout with April2023
revision log), not an independently certified2019 profile. **Policy** identifies a
local strict synthetic admission decision rather than an additional exchange wire
rule. [L3_RECONSTRUCTION_REQUIREMENTS.md](L3_RECONSTRUCTION_REQUIREMENTS.md) remains
the broader reconstruction contract; [P1E_MATRIX_COVERAGE.md](P1E_MATRIX_COVERAGE.md)
is the historical P1E coverage ledger, not a claim that its deferred rows passed.

The pipeline in scope is:

```text
synthetic BinaryFile framing -> validated owned wire decoding
                            -> bounded source/session context
                            -> owned normalized candidate or external observation
```

There is no arrow to native replay in P1F. The implementation contracts are
[context.hpp](../include/gig/itch/context.hpp) and
[context.cpp](../src/itch/context.cpp); wire behavior remains specified by
[the P1E report](P1E_VALIDATION_REPORT.md).

`SourceContext::apply` receives payload bytes plus immutable physical location and
optional provenance, and calls the wire decoder itself. Arbitrarily constructed
`DecodedRecord` objects cannot bypass that validation boundary. Wire errors are
reported separately from semantic context errors, unsupported source types,
resource admission failures and native-integration ineligibility. No silent skip,
resynchronization, session rollover or recovery path is provided. Rejection preserves
the expected logical position; the caller must stop or explicitly retry that same
position rather than advance past an unsupported record.

## Explicit identity, initialization and provenance

A `SourceManifest` requires owned source and session identity tokens and carries
optional provenance plus an initialization annotation. Unknown metadata stays
unknown: no exchange instrument, receive timestamp, UTC epoch, license identity,
source digest verification or seed is manufactured. Source record locations and
raw wire fields remain available in each owned `NormalizedRecord`. Each output also
owns its complete `ContextPolicy` and `normalization_version=1`, preserving the
selected price quantum, lot size, first source position, timestamp/lifecycle/equal-
cancel policies, ledger caps and logical memory budget. This identifies the applied
normalization settings without a borrowed configuration lifetime. The exact source
commit/hash belongs in run evidence; version1 is not a substitute for that code
identity, a certified historical schema profile or an exchange-policy version.

`Initialization::synthetic_history_declared` annotates the caller's assertion of
an authored synthetic history. It is **not** a proof of empty-start completeness,
a snapshot installation, or a native eligibility gate. Both that annotation and
`Initialization::unknown` retain `initialization_incomplete=true`. A successful
context observation must never be presented as valid reconstructed L3 depth.
This distinction applies even when all local lifecycle and order-reference checks
pass. Actual initial-state evidence and native publication eligibility require a
separately authorized phase.

One factory-created context owns one explicitly declared source/session scope.
New session/day processing requires a new context with an explicit new manifest;
S control codes do not clear directory, retired-order or match ledgers. This
prevents an implicit reset from disguising same-day reference reuse or missing
history. The caller must establish the relationship between declared session and
trading day before interpreting a context as a day-unique namespace.

Optional source/digest/origin/seed values are observations or caller assertions,
not independently verified artifact integrity. Contradictions must be rejected
rather than resolved by replacing one identity with another. Any accepted inherited
manifest provenance must remain distinguishable from unavailable per-record values.

## Source order, timestamps and lifecycle

BinaryFile contributes physical order, byte extents and local ordinal, not exchange
transport sequence numbers. Context uses exact declared first location and subsequent
frame adjacency/ordinal increment. Tracking number is preserved as Nasdaq internal
tracking; it is never a gap detector. A record cannot advance a logical committed
context position when its semantic admission fails. An actual physical reader may
already have advanced, so the caller must retain separate read/decoded/committed
positions and stop or retry the same logical record explicitly. A valid final
record at the maximum representable byte/ordinal boundary may commit; an explicit
exhausted-cursor state prevents computing a wrapped next position or admitting a
subsequent record.

Raw48-bit timestamps remain exact. Optional policy can require nondecreasing values
or an ordinary-day intraday bound. Those are selected context restrictions, not
new raw-wire width rules or claims of UTC/timezone/date conversion. Capture order
is never repaired by sorting timestamps. The default timestamp policy does not
invent missing clock evidence.

S1 §1.1 distinguishes O (start messages), S (system hours), Q (market hours), M
(end market hours), E (end system hours), C (end messages). Optional strict lifecycle
ordering observes those distinct stages; it does not equate them with the native
open/halt/resume/close enumeration. Observing the sequence never proves that all
required source history was acquired. S1 explicitly allows deletes and broken
trades after E, so earlier close markers must not clear state or act as EOF.
C and the BinaryFile terminator remain different contracts. Starting at a declared
bounded prefix must not silently invent missing earlier lifecycle observations.

Finish modes distinguish caller-declared source completion, bounded prefix and
unexpected EOF. A caller declaration cannot independently verify a missing container
terminator, gzip CRC, archive hash or completeness of the exchange feed. Source
completeness, local session-policy completeness and L3 initialization are separate
flags. `session_incomplete` becomes false only after the strict ordered O/S/Q/M/E/C
policy completes and the caller declares source completion; a permissive lifecycle
policy never establishes this flag. None of these flags establishes upstream
exchange completeness or L3 validity. Finalization seals this context rather than automatically starting a
new session. An invalid finish enum returns an explicit `finish_error` without
sealing. A moved-from context rejects admissions/finalization with an invalid-config
diagnostic rather than allocating through empty moved ledgers.

## Directory and order-lifetime policies

S1 §1.2.1 supplies daily locate/symbol directory information. The context retains
all decoded directory fields and exact eight-byte padded symbols; it does not trim,
case-fold, hash into a native ID or infer issuer continuity. An identical repeated
entry can be an idempotent observation; conflicting binding or payload is a context
conflict under this strict policy. Symbol-bearing A/F/P/Q records must agree with
the known locate binding. Unknown locate is missing context, not permission to
invent a directory or silently classify a record as another instrument.

S1 §1.3 calls displayed order references day-unique. The bounded lifetime ledger
retains inactive entries as well as active entries, so deletion/full execution does
not permit same-scope reuse. A replacement creates a new reference and retires the
old one. Replacing into any previously used reference, including the original
reference, is rejected. New session scope must be explicitly constructed; capacity
exhaustion cannot be repaired by evicting retired references.

P1E preserves unsigned zero references and quantities because native positivity is
not evidence of exchange wire invalidity. **Policy:** this synthetic semantic
layer can reject zero displayed-reference/positive-mutation requirements as
context-invalid or integration-ineligible; this must not retroactively label the
bytes structurally malformed. Non-displayed P reference0 is an observation, not a
displayed-order lookup. Q shares0 is explicitly supported by S1 §1.5.2.

The context order record contains reference, locate, stock, side, remaining shares,
resting Price(4), optional attribution, arrival ordinal and active state. It is a
lifetime/quantity ledger, not a price-level structure, FIFO/matching engine or a
proof that exchange priority was reconstructed.

| Source | Context behavior and boundary |
|---|---|
| A/F | Resolve directory/symbol, require unused displayed reference, retain exact side/price/size/attribution and arrival ordinal. |
| E | Resolve active reference/locate and reduce exact shares; retire at zero. E has no wire execution-price field: a resting-price-derived candidate must not be labeled observed price. Identified execution is not forced to the FIFO head. |
| C | Reduce displayed shares as E; separately preserve observed execution price and printable flag. A different execution price is not changed into an observed resting-price trade. Any future book-only projection remains explicitly classified. |
| X | Subtract cancelled shares from remaining size; reject underflow. Default policy rejects equality as `equal_cancel` because S1 §1.4.3 describes a partial cancellation; `allow_equal_cancel` is an explicit alternative policy, not silent repair. |
| D | Retire the known active order and remove its entire remainder; unknown/inactive reference is not a successful no-op. |
| U | Retire old reference, create unused new reference, use new total displayed size/price, inherit side/stock/attribution per S1 §1.4.5. No exchange priority-retention claim. |
| P | Preserve a non-displayed print; no displayed-order insertion, decrement or aggressor inference. |
| Q | Preserve bulk cross including zero shares; no auction allocation or clearing displayed orders. |
| B | Preserve correction identity/mark known eligible match broken; never restore displayed liquidity. |
| S/R | Session/directory observations only; no native event or synthetic order is invented. |

## Match ledger: observations, not trade accounting

S1 §§1.4.1–1.4.2 describe E/C match numbers as day-unique; §1.5.1 describes P's
number as session-unique; §1.5.2 describes Q's as day-unique. **Policy:** within the
explicitly declared synthetic scope, generation by E/C/P/Q occupies one bounded
match ledger entry, and a duplicate generation is a strict context conflict. This
is not a general claim that a local session identity proves an exchange day's
namespace or that every historical representation has been certified.

S1 §1.5.3 says B references a previously transmitted E/C/P match and that a break
is final. The strict profile requires an existing eligible unbroken match and
consistent locate; repeated breaks and unsupported origin kinds are rejected.
The specification's stated list does not establish Q break semantics: no liquidity
undo, auction rollback or inferred Q-to-C relation is implemented.

S1 warns that nonprintable C shares may appear in a later bulk print. Preserve
printable and match identities separately. Do not infer that C and Q have the same
match number, add their quantities into verified volume, or label this ledger a
complete corrected trade tape. The ledger does not calculate research returns,
TCA, volume conservation or cross-event allocation.

## Normalization and native capability boundary

`IntegrationClass` describes a potential representation route, not actual application
or eligibility. Exact candidates, book-only projections and external observations
retain their source record and manifest. Exact integer tick/lot conversions use
explicit `price_quantum` and `lot_size`; off-unit values must not round or truncate.
Those factors are caller-declared hypothetical normalization units, not inferred
instrument metadata. An ineligible native conversion may still be a valid committed
source-context observation; callers must inspect both disposition and commit status.
E/C hypothetical candidate price ticks derive from the context resting price, not
C's distinct observed execution price. C's actual price stays separately owned.
Q remains integration-unsupported even if its price/quantity units are exactly
representable; auction semantics are not a positive-size print conversion. Zero-share
Q remains an observation. B corrections are also integration-unsupported. P
candidates represent prints only, never displayed orders or inferred aggressors.

No native sequence, event timestamp, InstrumentId, order mutation, snapshot,
recovery state, matching result or journal entry is produced. Native book crossing
checks, FIFO assertions, initialization publication and independent state comparison
are future work. Current core/Python behavior remains outside this component.

## Bounded ownership, complexity and atomicity

Policy caps directory entries, lifetime orders and matches, including retired and
broken entries. Logical slot budgeting uses checked multiplication/addition before reservation,
then checks the vectors' actual capacities against the same logical-storage budget
after reservation. This is not an allocator-overhead or RSS limit, and the standard
permits capacity over-reservation before that second check. A caller-owned bounded
PMR resource is required for a hard allocation governor. The context reserves all
ledger capacity at creation and rejects an excess before publishing the context. No input length
or session duration authorizes an unbounded ledger. Resource lifetime must exceed
the context's lifetime. Fixed normalized records own their source/provenance values;
returned views into context vectors remain tied to context lifetime/mutation.

The chosen small bounded-vector design trades simple ownership and allocation-free
admission for linear lookup in the configured ledgers. It is not whole-market
scalability evidence or a performance optimization claim. Creation may allocate;
steady-state successful and rejected admissions should not allocate. A failed reserve
must release earlier reservations and return a structured resource error.

Strong semantic failure atomicity requires validating every needed directory/order/
match lookup, quantity operation, capacity admission, unit decision and next source
position before committing any ledger or cursor change. A duplicate match detected
after a tentative execution must not consume shares. A failed replacement must not
retire the old order or occupy a new reference. Rejection must preserve accepted
counts, last location/time, directories, orders, matches and lifecycle stage, except
explicitly documented finalization/stop diagnostics. Tests must distinguish a valid
context commit classified integration-ineligible from a rejected context mutation.

No journal optimization is included. The existing15,944-byte-per-entry finding and
100,000-record native journal cap remain unchanged; a bounded context does not make
native retained history bounded enough for a full archive.

## Required evidence and remaining decisions

Synthetic tests should cover exact source adjacency, directory identity/conflicts,
reference lifetime/reuse, every supported variant, non-head execution quantities,
C printable/price preservation, match origin/break policy, lifecycle and timestamp
profiles, missing provenance, conversion boundaries, each capacity and allocation
failure, invariant preservation on every reject, and fresh-context session reuse.
An independently implemented reference must compare every accepted/rejected result
and complete ledger state after each step; wire oracle agreement alone is insufficient.
Cross-compiler Debug/Release/sanitizer gates and owned-allocation accounting are
separate results to be reported, not implied by writing this design.

Outstanding decisions include actual historical schema/context profile, exchange
session/day namespace evidence, source permissions and complete initial-state
provenance, zero-value contextual certification, full-X anomaly policy for observed
input, exact match reuse/break scope for any historical exceptions, independent
observed reference data, gzip integrity/limits, native transaction mapping and
initialization eligibility. No real-market GO follows from P1F. The next phase
requires explicit authorization and must retain these boundaries.

All-space directory symbols are wire-observable but rejected as unavailable stock
identity under the local P1F admission policy (`stock_conflict/empty_stock`). This
does not certify the exchange character alphabet for other nonblank symbols.
