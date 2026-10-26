# Native engine and journal

C++ source/build definitions/fixtures unchanged. Fresh six native configurations rerun
all155 cases,including book/matching,sequencing,allocation failure,journal/recovery,
pre-optimization replay equivalence and independent references. All eight canonical
identities remain unchanged. Existing validated binaries were exercised;no new compiler
build or exact-HEAD ARM64 qualification is claimed.

Measured journal baseline repeated at128/1024/8192 authored session records,reset intervals
0/128. Tracked memory returns to zero. Detailed bytes/allocations/timing in evidence.
JournalRecord(replay.hpp) retains MarketEvent plus disposition/restart index;MarketEvent's
large fixed metadata/payload drives record size12232 bytes. Logical JournalEntry15944
bytes remains the public value representation. Phase4's~150MB8192-record growth peak is
still material. Separate restart-plan vector already avoids storing every plan per record.
No new compaction or misleading memory/performance win is claimed.

## Measured implementation plan,not an untested redesign

1. Preserve current snapshots/errors/ledger/source accounting and frozen128-prefix trace.
2. Isolate known-interval capacity reservation candidate;measure transient peak/allocation
   savings and startup allocation costs before proposing a default.
3. Separately investigate compact event payload storage and immutable metadata interning;
   maintain public logical journal reconstruction and ownership/lifetime guarantees.
4. Require independent per-event equivalence,allocation-failure sweeps,restart/export
   compatibility and GCC/Clang sanitizer matrix for every candidate.
5. Test128..8192 then explicitly budget larger workloads;record RSS versus PMR and tail
   timing. No inferred exchange throughput or unmeasured100000-record performance claim.
6. Version any persisted representation/migration and preserve rejection atomicity.

Redesign risk exceeds this integration checkpoint's scope. Native changes deferred in
accordance with the directive rather than destabilizing verified replay before November10.
