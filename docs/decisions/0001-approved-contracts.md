# ADR 0001 — Approved core contracts and Phase 0 refinements

Status: APPROVED design; these engine contracts are PROPOSED, NOT IMPLEMENTED.
Phase 0B implements validation infrastructure only. User approval adds the four
requirements below. The complete Phase 0 design remains the feature roadmap.

## 1. Strong exception safety and atomic mutation (MUST HAVE)

For each accepted canonical book event, readers observe either the complete
previous state or the complete next state. Rejection, overflow, capacity failure,
or allocation failure leaves orders, FIFO links, index, level totals, sequence
cursor and committed journal position unchanged. Multi-order matching caused by
one simulated action has the same all-or-nothing boundary.

Validate and calculate checked deltas first; stage all allocating resources and
output capacity before mutation. Commit uses only nonthrowing operations over
prevalidated/staged objects. If that cannot be guaranteed, use a rollback guard
with allocation-free, nonthrowing rollback. Never declare noexcept around code
that can allocate merely to suppress exceptions. No callbacks, logging I/O,
serialization or external publication occur inside the commit section.

Sequence acceptance and state mutation commit together. A rejected event is
recorded separately and strict replay stops; the committed sequence cursor does
not advance. Snapshot replacement validates/builds a complete temporary state
then swaps it atomically. Resource exhaustion does not permit partial recovery.

Owned deltas/snapshots become visible only after commit. Publication failures are
separate from mutation failures: a committed result is not rolled back because an
export fails. Export uses a manifest-marked incomplete run until all checksummed
artifacts are durably finalized; retries use deterministic output identities.
This is logical single-owner atomicity, not crash durability or a transaction
across external systems. Fault-injection tests at every allocating/staging point
must compare pre/post canonical state and sequence cursors in Phase 2.

Alternative: mutate then repair; rejected because rollback can itself allocate or
fail. Interview explanation: staging makes failure behavior part of the contract,
not a side effect of container choices.

## 2. Multi-stream ordering and sequence boundaries (MUST HAVE)

Sequence scope is (dataset, venue, stream/channel, session/epoch), not instrument.
A stream can interleave several instruments. Adapters declare whether sequence
increments per message or event; one message with multiple events retains a
message sequence and explicit zero-based subevent index. Stream continuity is
checked before filtering instruments. First expected sequence comes from an
explicit capture boundary or validated snapshot; never infer missing history.

The canonical journal stores a global replay ordinal. Prefer a documented capture
merge order when supplied; do not invent a cross-venue causal order from unrelated
sequence numbers or clocks. Otherwise an offline merger uses a declared key:
(selected timestamp, configured stream rank, message sequence, subevent index).
Missing/nonmonotonic selected timestamps make that policy invalid; reject rather
than silently sorting away errors. A capture-ordinal policy can handle timestamp
regressions without changing stream order. Policy, clock and stream ranks are
manifest inputs. A deterministic total order is not evidence of market causality.

Sequence gaps/regressions/duplicates stop strict replay before applying the event.
No wraparound. Session reset requires an explicit epoch transition and recovery
policy. Snapshots specify per-stream included sequence/subevent boundary and
coverage; resume strictly after those boundaries. Aggregated snapshots cannot
restore order-level FIFO. Independent books may replay separately, but aggregated
research must retain the declared merge policy. Streaming watermarks/reorder
buffers are LATER / EXPERIMENTAL; no undeclared buffering in the baseline.

Phase 2 tests must cover equal timestamps, clock regressions, instrument filtering,
message subevents, gaps, overlapping sessions and snapshot resume boundaries.

## 3. End-to-end research provenance (MUST HAVE)

Every exported snapshot, metric, fill, cost estimate and benchmark references an
immutable run manifest. Required lineage: input artifact IDs and SHA-256 hashes,
license/source references, origin/source/transformation labels, adapter/schema
versions, instrument/tick/lot metadata, ordering and sequence/recovery policies,
configuration, code SHA and dirty state, build/toolchain, seeds, model versions,
parameter values, sample/time coverage and parent run/artifact IDs.

Use independent origin (synthetic/real), source (exchange/broker/SIP/public/etc.)
and transformation (observed/normalized/reconstructed/simulated) dimensions.
Derived results inherit lineage and add transformations; they never erase their
parents. SIMULATED_FILL != BROKER_FILL and simulated latency != observed latency.
Unknown provenance is explicit and fails claims requiring authenticated lineage.
Export manifests record completeness, errors, artifact hashes and validity flags.
A failed/incomplete run cannot masquerade as a valid research result. Hashes give
integrity, not proof of source authenticity. No credentials or restricted datasets
belong in Git. Phase 0B benchmark manifests implement the applicable subset only;
full research schemas and propagation tests are later phases.

## 4. Correctness-validated performance baseline (MUST HAVE)

Before optimizing a component: validate its workload against an independent oracle,
run invariant/replay/boundary checks and relevant sanitizers, then record a Release
baseline with exact commit, workload hash/seed, environment, flags, warmup,
repetitions and result checks. Compare candidates on identical workloads and retain
correctness equivalence. Changing semantics is not an optimization.

Phase 0B measures only existing AddOrder scaffold validation. It is not a LOB,
replay, matching or analytics baseline. Phase 2 must establish the first genuine
book/replay baseline before book optimization. No performance target or speedup is
assumed. Shared-cloud timings are noisy; sanitizers are correctness runs only.
