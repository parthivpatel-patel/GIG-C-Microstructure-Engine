# Phase 5 journal storage and equivalence contract

This is a private in-memory representation change, not a serialized journal schema
or persistent recovery migration. The public logical `JournalEntry`, all event
DTOs, replay canonical `gig.replay.v1`, payload indices, source accounting and run
lineage remain unchanged. Native clients must rebuild because ReplayEngine layout
changes; no stable binary ABI is promised. Python wheels rebuild the same sources.

## Representation and bounds

The private JournalRecord keeps the original owned MarketEvent and disposition,
with an optional integer reset-plan index. Only successful resets append a full
owned RestartPlan to a second PMR vector. No interning, pointers into caller data,
shared ownership, lossy metadata conversion or eviction is introduced. Stable
indices remain valid across vector reallocations and engine moves. The reset plan
count cannot exceed the accepted journal count or configured max_journal_records.
Both vector capacities are individually bounded by the unchanged1–100000 cap.
`journal_storage()` reports physical used/capacity/element sizes; the public DTO's
sizeof remains a logical-object measurement and is not the physical record size.

On measured Linux x86_64 GCC/Clang ABI: record12232 bytes versus old15944, plan3720.
A reset-only retained sequence costs15952 bytes per used pair (8 bytes more than
old); plan-vector spare capacity adds further workload-dependent overhead. Ordinary
records save3712 bytes each before vector slack. Metadata5576 and inline Snapshot
6624 remain; the optimization does not solve all scaling limits. Vector objects,
book/config, native allocation headers, fragmentation and exported snapshot/string
copies must be accounted separately.

## Commit ordering and failure contract

1. Validate event, source boundaries, all reset plans and next cursors.
2. Reserve journal slot, then optional reset-plan slot. Failure may change capacity
   and resource diagnostics, but never accepted book/cursors/journal/provenance.
3. Apply native event/reset/recovery using existing strong semantic atomicity.
4. For reset only, append the plan and its stable index. Append journal record,
   then commit cursor/order state. Reserved capacities and statically asserted
   nothrow stored-value construction prohibit a post-native allocation failure.

Ordinary apply and recovery require no reset archive allocation. Canonical export
resolves the optional index back to the exact original plan, preserving all fields,
ordering, provenance and existing token escaping. No compact serialized format is
introduced. Rebuilding from the trusted synthetic start uses the same logical input
and canonical state; no old in-memory object is imported or hot-migrated.

## Evidence gates

A frozen pre-change executable emitted128 canonical prefixes of an authored mix of
adds, observations with distinct provenance, seven resets and five complete native
recoveries. A separately authored map/count/sequence model checks each accepted
state; baseline prefix hashes are differential evidence, not an independent oracle
by themselves. Post-change output must match every frozen SHA256. A deliberately
wrong expected prefix is a negative control. Existing full ITCH wire/context/L3/
streaming/demo/HY/admin/auction oracle hashes remain required.

Real allocation injection covers journal growth, reset archive growth and native
reset allocations after0/1/2/3/4/8 reset prefixes. Every failure must leave complete
canonical state unchanged, allow exactly one successful retry, survive an engine
move, and release all tracked bytes/blocks. New tests reached16 injected reset
failure sites, versus11 pre-change; existing replay allocator tests additionally
exercise apply/recover/reset/canonical/depth. Finite injection tests and nothrow
proofs complement each other; neither claims exhaustive fault-model certification.

Memory probes use no resting orders so PMR byte changes isolate journal allocation;
independent integer formulas reconcile both vector capacities, not only sizeof.
Measure no-reset, reset-every64 and reset-every-event populations, including
non-power-of-two lengths. Keep old executable and raw measurements. Report live,
peak, allocations, RSS and timing distributions; do not infer heap fragmentation
from PMR or an exchange latency SLA from a shared-host benchmark. All-reset costs
must remain visible rather than being hidden by an ordinary-event average.
