# Backend performance and memory evidence

These are bounded shared-cloud x86_64 synthetic measurements, not exchange latency,
native ARM64 results, capacity promises or complete allocator accounting. Safe exact
measurements, source identity and environment metadata are in backend_audit.json.

## Journal scaling

Existing GCC Release `gig_journal_memory_probe records reset_every` ran three repeats
each at(1,0),(1024,0),(8192,0),(8192,256). Independent fixture counts, byte accounting,
recovery state and post-destruction cleanup are asserted by the executable.

| Records/resets | Physical record bytes | Retained PMR bytes | Peak PMR bytes |
|---|---:|---:|---:|
|1/0|12232|12648|12648|
|1024/0|12232|12525984|18788768|
|8192/0|12232|100204960|150307232|
|8192/32|12232|100324000|150366752|

Logical JournalEntry remains15944 bytes; physical storage12232 plus separately stored
3720-byte restart plans. Vector growth temporarily retains old/new arrays. Native
default cap4096 and explicit maximum100000 remain (`src/replay/replay.cpp:49`).
At100000 fully allocated records, record storage alone extrapolates to1,223,200,000
bytes (~1.14GiB), excluding plans, growth, book, receipts and process memory. **This
task did not replay100000 records.** The PMR counter is not whole-process peak RSS.
No production memory guarantee or fragmentation conclusion follows from these probes.

## Reproducible stock microbenchmarks

`scripts/benchmark_stock_intelligence.py --repetitions 3 --iterations 30` measures
512 authored SEC facts,153-point option grid,128 authored research returns and native
L1 quote analytics. Five warmup calls precede each measured operation; input construction
is excluded. A separate untimed tracemalloc pass and whole-process peak RSS are recorded.
This run is tied to baseline HEAD plus the exact changed-file manifest; the benchmark
correctly reports a dirty worktree. SEC normalized output identities intentionally
change for additive v2 metadata, unrelated to the eight frozen native oracle hashes.
Actual timings live in the evidence JSON; they are not stable performance thresholds.

## Benchmark-gated journal improvement plan

1. Profile realistic bounded authored event mixes and reset density at fixed seeds;
   report allocations, live/peak/RSS, throughput and full logical replay identity.
2. Separate receipt/metadata/event/reset costs; prove byte/lifetime accounting, examine
   immutable shared metadata or compact typed records without losing source lineage.
3. Specify format/version migration and old→new materialization equivalence before
   changing physical storage. Preserve journal-limit failures and recovery diagnostics.
4. Differential-test every event, reset, checkpoint, cursor and allocation-failure point;
   preserve all frozen replay/canonical identities and independent reference outputs.
5. Accept only a measured improvement on equivalent workloads with no regression in
   failure atomicity, sanitizer safety or deterministic provenance. Otherwise keep the
   current baseline. Do not optimize simply to minimize sizeof.

No journal redesign, unsafe arena, mmap archive or unbounded retention was introduced.
