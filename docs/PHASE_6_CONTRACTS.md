# Phase 6 offline execution planning and transaction-cost analysis

IMPLEMENTED / MUST HAVE: exact-lot TWAP, explicitly forecast/oracle VWAP, causal POV,
configurable schedules/limit/TIF/child size, hard parent inventory and participation
constraints, separate simulation integration, exact TCA and owned provenance.
No live broker, portfolio-margin engine, calibrated impact, adverse-selection model,
hidden liquidity, adaptive strategy, terminal dependency or real trading authority.

## Planning and units

PlanConfig fixes run/assumptions IDs, instrument rules, side, limit, target lots,
maximum directional inventory lots, max child lots, start/end simulation nanoseconds,
bins and first lifetime-unique child ID. Target>0 and <=inventory_limit. A parent may
exceed per-order maximum, but each child may not; max_child>0 and <=rule maximum.
1..4096 bins, end>start, at least one ns/bin; <=4096 emitted children. End is exclusive
for TWAP/VWAP bin start decisions, inclusive for available POV input observations.
Side/TIF enums and price bounds validate; post-only requires GTC. Defaults use IOC.
No implicit market order or future choice of price based on unrealized information.

TWAP uses equal bin weights. VWAP uses supplied nonnegative integer volume weights,
not future market observations by default. Sum weights must be positive. Allocate
exact target lots by largest remainder: floor(target*weight/sum), then assign leftover
lots to descending fractional remainder, tie earlier bin. TWAP thus divides integer
lots as evenly as possible. Every target lot is allocated without rounding price,
quantity conversion or floating-point loss. This is explicit integer-lot apportionment,
not an assertion of continuous fractional-lot execution. Products use exact unsigned
128-bit arithmetic (uint64*uint64 fits); summed <=4096 weights fit. Independent Python
Fraction verifies the algorithm even at uint64 extremes.

Decision grid is start+floor((end-start)*i/bins) integer ns. This explicit downward
nanosecond grid quantization is part of the model; it is not a hidden unit conversion.
If a bin exceeds max_child, split same-time children deterministically with increasing
IDs. Empty bins emit no zero-size orders. Total target and inventory cap are unchanged.
No arbitrary number of child allocations: >4096 chunks returns capacity error.

VWAP requires profile artifact ID and its availability time. ex_ante_forecast rejects
availability after start; oracle_hindsight is explicitly labeled oracle in Schedule
and ExecutionRun and permits hindsight profile availability. A label/identity cannot
authenticate a forecast artifact; researchers must retain original version/hash and
must not relabel realized volume as ex ante. No estimate of actual future volume is
invented. Oracle execution is a hindsight benchmark, not an achievable causal result.

POV consumes VolumePoints (available_at, lots, artifact, ordinal) in nondecreasing
time and strictly increasing source ordinal, all in [start,end]. The available_at
clock is the synthetic decision information time, not an unadjusted exchange time.
Given rate p/q with 0<=p<=q and q>0:

    allowed_cumulative_child_lots = min(target, floor(cumulative_visible_external_volume*p/q))

Emit only new positive budget at that observation time, split by max_child. Every
prefix respects participation and inventory, including with in-flight orders or
unreported fills. Budget counts SUBMITTED lots; IOC misses/cancellations do not
recycle it, so realized participation can undershoot. Own simulated fills must NOT
be counted again as independent external volume. The function can consume an offline
full tape but earlier outputs depend only on the available prefix (tested).

## Execution integration and ownership

simulate owns a NEW simulator, seeded initial synthetic liquidity and the complete
plan. It recomputes/compares the plan from its declared configuration/input profile
before execution, so a manually forged Schedule cannot bypass caps or timing. Run ID
and instrument rules must agree. Initial liquidity submits at time 0; child decisions
use their fixed schedule times; finish>=end. No strategy accesses future reports or
model fills to alter its schedule. Delay/report filtering follows Phase 5 contracts.
Finish may leave in-flight requests/reports if configured latency exceeds the horizon;
a completed planning run is not proof of completed inventory execution. Full fills
and delayed client information must be inspected separately.

Failure creates no externally mutated simulator/partial result: entire new ExecutionRun
is owned until success. Output plan preserves oracle label and volume/profile inputs;
exporting only its generic Simulator would omit strategy assumptions and is insufficient
as a research artifact. Retain both plan and simulator plus manifest. PMR resource must
outlive selected outputs, same as Phase 5; pure planner/output bad_alloc translates to
resource_exhausted. No callbacks or external order submission.

## TCA definitions, benchmarks and costs

CostConfig declares research/simulation run IDs, rules/side/target, arrival and terminal
midpoint benchmarks with artifact IDs/availability, and as_of. Each CostFill retains
the full simulated fill, selected maker/taker child, child decision time, causal decision
midpoint benchmark and fee in TICKS PER LOT (negative explicit rebates permitted).
Validate source run/seed consistency, distinct maker/taker/commands, price/rules,
positive quantity, duplicate fill identity, side attribution and total <=target.
The input must reference the actual source archive; validation is not authentication.

Benchmarks can retain half ticks but must remain within instrument price bounds.
Arrival/decision benchmarks are available by the decision; decision<=matched<=reported
<=as_of. Terminal benchmark is available by as_of and no earlier than arrival. Thus
passing an unreported internal simulation fill is rejected as future information.
Unordered fill inputs are allowed; output retains their explicit input order. Exact
capacity failures reject the result, never fabricate an approximate cost.

Let s=+1 buy/-1 sell, Q parent target, q_i filled lots, P_i fill ticks, D_i decision
midpoint ticks, A arrival midpoint, T terminal midpoint, f_i fee ticks per lot:

    execution VWAP = sum(P_i*q_i)/sum(q_i)       [ticks; unavailable with no fills]
    notional = sum(P_i*q_i)                    [tick-lots, signed price allowed]
    delay cost = sum(s*(D_i-A)*q_i)             [tick-lots]
    spread cost = sum(s*(P_i-D_i)*q_i)          [tick-lots]
    slippage = delay cost + spread cost        [s*sum((P_i-A)*q_i)]
    fees = sum(f_i*q_i)                        [tick-lots]
    unfilled opportunity cost = s*(T-A)*(Q-sum(q_i))
    implementation shortfall = slippage + fees + opportunity cost
    currency shortfall = shortfall * tick_size * lot_size

Fees are declared inputs, not guessed venue fees. Opportunity cost is a benchmark of
unfilled inventory, not an observed cash execution or calibrated market impact.
Negative costs indicate improvement/rebates under the convention. No annualization,
financing, tax, hidden liquidity, impact/adverse-selection calibration or double-counted
future drift is implied. Price/time coverage and benchmark artifact choice materially
change the interpretation. Arrival-midpoint IS is a stated research convention; it
is not all published IS definitions. CostFill parents and all benchmark assumptions
remain owned in the report and must enter its immutable run manifest.

All arithmetic is exact reduced rational, including money conversion; general checked
128-bit intermediate limits apply. Empty fills keep full opportunity cost but report
unavailable average execution price. Hand example: buy 20, fill 10 at 103, arrival100,
decision102, terminal104, fee1/10 per lot -> delay20, spread10, fee1, opportunity40,
shortfall71 tick-lots, 71/100 currency for tick1/100, lot1. Sell/rebate signs tested.

## Complexity, validation and alternatives

Weighted plan O(B log B+C) time, O(B+C) memory for bins/children; POV O(V+C), <=4096
observations/children. TCA O(F^2) duplicate comparison baseline, O(F) owned parents,
F<=4096. Integration inherits bounded full-State simulation costs. Alternatives:
continuous optimization/forecast calibration are unimplemented, not approximated by
these schedules. Interview defense: exact apportionment reconciles inventory, causal
availability prevents hindsight leakage, and additive cost terms reconcile algebraically.

Independent Python Fraction: 2600 deterministic weighted, POV and buy/sell fee/cost
cases (seed6011). Tests cover max integer products, grid/remainder ties, splits,
profile availability/oracle labels, causal prefix stability, invalid IDs/caps/volumes,
zero fills, future quotes/reports, duplicate costs, forged plans, run identity and
simulation integration. Actual PMR sweeps exercise schedule and integrated simulation
allocation/cleanup, plus TCA output failure. Full Debug/Release/ASan+UBSan gate applies.
Benchmark fixes the hand example using actual simulator fills, validates first, retains
complete parent canonical simulation plus declared plan/cost assumptions, then separately
measures planning+TCA wrappers (not matching, setup or export). Raw timing/selected PMR
counts are scoped, finite shared-cloud evidence; no optimality or production speed claim.
