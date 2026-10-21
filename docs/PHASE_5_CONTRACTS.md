# Phase 5 separate offline synthetic matching and latency model

IMPLEMENTED / MUST HAVE: deterministic single-owner synthetic price/time matching,
seeded scheduler, exact queue positions, partial/full fills, cancellations/races,
marketable limit orders, GTC/IOC/FOK and explicit post-only GTC. These are simulated
outcomes, NOT observed venue/broker executions. No feed event dispatcher is accepted
by Simulator; historical OrderBook/ReplayEngine do not match and are unchanged.
No fees, routing, STP, auctions, hidden/iceberg/pro-rata, random fill probabilities,
market impact calibration, real orders or broker connectivity. Those claims need
separate models and validation. Market orders without a price cap, DAY/venue-specific
TIF and replace-in-place are unsupported; do not silently emulate them.

## Model, ordering and causality

SimConfig fixes run ID, instrument tick/lot rules, nonzero uint64 seed, resource
limits and four independent latency distributions: arrival, cancellation,
acknowledgment, execution reporting. Each is base + discrete uniform integer jitter
in [0,jitter], explicit nanoseconds, xorshift64 deterministic generator. One draw is
consumed even for zero jitter. This is an ASSUMED synthetic latency model, not measured
network/venue latency or a calibrated statistical claim. Times cannot overflow.
Scheduler key (simulation_time, monotonically allocated ordinal) breaks ties.
Arrival priority is assigned WHEN processed, not when submitted; stochastic arrival
ordering can change FIFO. No sequence/time/priority wrap. Fill price is maker price.

submit_at/cancel_at first process scheduled events <= decision time, then enqueue
the new request at decision time + sampled latency. Zero-delay requests run on the
next advance or command at that time. An explicit advance_to processes through its
target. Past decisions reject, never rewind. Same command sequence/config/seed gives
identical canonical output. Different advance calls are different journal inputs;
semantic book outcomes may agree but full command-history bytes need not.

Public exchange_orders/exchange_fills/exchange_queue_position expose MODEL TRUTH
for offline diagnostics; exchange_fills may exist before a client execution report.
They are not a latency-filtered strategy information set. client_reports exposes
ONLY records delivered by now; decision logic must consume this filtered channel.
An execution report may arrive before its acknowledgment when configured delays
permit it. Same-time report ties follow the scheduler ordinal, never implicit
future knowledge. Market-data latency is not modeled; public-book observation is
an explicit instantaneous synthetic assumption. No strategy or fill-probability
calibration is implemented in this phase.

Every accepted command and its decision time, seed/RNG state, scheduled event,
exchange order/priority, fill and delivered report is retained in canonical state.
Fills carry run ID/seed, maker/taker source command indices, maker/taker IDs, side,
price/quantity and match/report times. Reports reference run/order and fill index.
Retain this archive and code/build/parameter/input manifest for end-to-end lineage;
identities and hashes are not proof of real data authenticity. All origins here
are synthetic and transformations simulated, never observed/reconstructed fills.

## Mutation semantics and quantity conservation

GTC crosses eligible opposite limits in best-price/FIFO order, rests any residual at
its own limit with new arrival priority. Partial fills retain makers' priorities.
IOC crosses similarly then expires its residual; never rests. FOK prechecks available
eligible displayed quantity; insufficient liquidity rejects with NO fill. Post-only
GTC rejects if it would take any quantity. FOK success fills entirely. No self-trade
prevention model (agents are not represented); no assertion of venue certification.

Cancel arrival removes active residual quantity and reports it. A cancel before an
order reaches the exchange rejects as not_active; it does NOT cancel an in-flight
request. A cancel after a fill similarly rejects; partial-fill cancel removes only
remaining quantity. IDs cannot be reused anywhere in a run, even after rejection.
Invalid enums/zero quantity/out-of-rule prices/unsupported TIF combinations reject
before any command advancement. Valid exchange rejections are committed synthetic
reports, not malformed-input errors. Full/partial client status is derived from
accepted/expired/cancel/fill reports, not a look at unreported model fills.

    submitted = pending_arrival + resting + executed_sides + cancelled + expired + rejected

executed_sides counts both maker and taker lots (2 per fill). Every term and total
is checked uint64; submitted is a lifetime counter and can exhaust. Empty levels
are implicit in flat storage; no crossed/locked resting book can survive matching.
Invariant scanner checks valid positive resting GTC orders, unique IDs and priority,
arrival order, noncrossing, scheduled times/keys, source commands, reports/fills and
quantity conservation. Debug scans after commit; Release tests/preflight scan too.

## Ownership, atomicity, complexity and limits

Correctness baseline uses flat PMR vectors, explicit priority and linear best-price
selection. Every public command clones complete bounded State using the SAME PMR
resource, advances/stages all matching/scheduler/report effects there, then swaps a
nonthrowing owner pointer. Multi-maker matching is all-or-nothing; bad_alloc, time/
quantity overflow or any capacity failure preserves the previous canonical state,
clock, RNG, counters and pending queue. Canonical export failure also preserves state.
No callbacks/logging/I/O in mutation commit. This favors auditability over speed;
copy cost is explicitly benchmarked, not advertised as a high-throughput design.

The selected resource must outlive simulator and exported PMR strings. Views/spans
are read-only and invalidated by the next successful command or owner destruction;
bindings must return copies/owned schemas. No concurrent access. Defaults: 1024
pending+active orders, 16384 queued events/fills/commands, 32768 delivered reports;
all limits positive <=100000. Caller may enforce a byte-budget resource. Lifetime
journal/report limits can stop a run even when the active book is small.

With N resting orders, Q events, H history: full staging time/space O(N+Q+H). Each
fill scans O(N) for best eligible price/priority; vector erase/queue insertion is
linear. Processing K events adds these scan/move costs; Debug pairwise invariants
add O(N^2). Queue position O(N). This is intentionally a simple correctness baseline;
ordered maps/heaps or transaction staging without full cloning are future profiled
alternatives. Resource/time exhaustion is a structured failure, not a partial fill.

## Validation and benchmark

Independent Python sorted-list oracle compares every order, FIFO rank, fill and
conservation state after 1000 seeded submit/cancel actions (seeds 5/42/1729/2027).
Unit tests cover partial/full/multi-maker fills, FOK reject/success, IOC residual,
post-only rejection, invalid enums/ranges, duplicate lifetime IDs, queue position,
cancel-before-arrival/after-fill, delayed ack/report visibility, seeded reproducibility,
past decisions, near-time overflow, quantity/capacity boundaries. Actual PMR failure
sweeps exercise full staged multi-fill transitions and canonical query allocation,
checking rollback/live bytes and cleanup. No fabricated failure flags.

Release baseline: seed 1729, 32 eight-lot makers at 100+id%4, then 128 one-lot IOC
buys capped at 103; zero assumed latency. A timed operation includes submit_at AND
advance_to (two atomic State stages), final success/checksum, not setup/canonical
export. Two warmups, seven 128-operation bulk passes and 896 separate service samples;
all repeated canonical outputs must match and end with 128 fills and exact ledger.
Selected PMR allocation deltas exclude setup, lifetime peak includes setup/staging;
all bytes freed after owners. Manifest embeds canonical complete simulated run,
code/flags/CPU/seed/raw timings; finite shared-cloud samples, not production latency.
