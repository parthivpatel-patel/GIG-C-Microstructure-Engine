# Phase 5 baseline and optimization decision

Entry: `f0373aa3e662d416fe6260210a7f3158d8fecea7`, clean `feat/bootstrap-cpp20-engine`; remote matches. Main `165c5038336887116d69160b0d8e5a1a5ef59d16` preserved. Phase 4 executed 1,360 CTest outcomes, 28 installed consumers and three packaging regressions; these remain historical results, not newly executed Phase 5 results.

## Ownership and data flow

BinaryFile framer owns a bounded payload; typed decoder owns exact wire fields. SourceContext owns bounded PMR directory/order/match histories and prepares nonmutating one-shot deltas. SyntheticReconstructor owns two ReplayEngines and source receipts; native success precedes infallible prepared-context commit. Each ReplayEngine owns its OrderBook, config, cursors, journal and PMR allocator association. The resource must outlive the engine. Snapshots/research results are owned copies; replay canonicalization resolves provenance through the retained journal. ITCH checkpoint restart replays from an authenticated synthetic start, not crash-safe hot restoration. Analytics consume accepted native state/events; no observed initialization exists.

## Measured x86_64 GCC ABI decomposition

| Object | Bytes |
|---|---:|
| Metadata | 5,576 |
| EventPayload | 6,632 |
| Snapshot | 6,624 |
| MarketEvent | 12,208 |
| RestartPlan | 3,720 |
| optional RestartPlan | 3,728 |
| JournalEntry | 15,944 |
| ReplayEngine | 14,776 |

The journal stores every event by value. Snapshot dominates the variant even for adds; metadata owns bounded provenance arrays even when mostly empty. RestartPlan reserves eight full stream starts in every entry although only reset records use it. Vector geometric growth temporarily coexists with its old allocation; capacity and used element count differ. Snapshot results/canonical strings allocate separately and are not included in sizeof. Heap allocator headers/fragmentation and RSS are not inferred from logical PMR bytes.

A standalone controlled probe compiled against the unmodified Release library tests 128/512/1001/1024/4096 observations with no resets, one reset per64 events or all resets; each has one process warmup and three measured repetitions. It independently reconciles live PMR bytes with actual vector policy and checks cleanup. At1,024 no-reset events:16,327,072 live PMR bytes and24,490,400 peak bytes, with416 initial book bytes. Reset-all also uses12 journal/book base allocations plus1,024 native reset allocations. Raw before measurements and compiler/binary identity are retained under build/phase5/evidence.

## Bounded proposed repair and acceptance

Separate only reset plans into a PMR archival vector; ordinary records store an optional stable index. Keep public logical JournalEntry and canonical v1 bytes unchanged. Do not compress metadata, move snapshot payloads, intern identities or change journal limits. Both vector reserves occur before native reset mutation; both post-success appends must be statically nonthrowing. No externally visible accepted cursor/journal/book may change on failure (reserved capacity may grow).

Acceptance: measured reduction for ordinary-event retained/peak PMR; transparent reset-heavy cost accounting; every prior canonical hash and frozen before/after native replay trace unchanged; independent state model; complete allocation-failure cleanup and retry; full applicable regression/package matrix. Reject the change if those gates fail. This representation is private in-memory storage, not a new persistence format or migration.

## Initial platform evidence

Linux x86_64 is the current actual host. No native ARM64 executor, aarch64 compiler, qemu-aarch64 or registered binfmt handler was found. GitHub Actions API request through the inherited proxy returned Forbidden (gh exit1); no run ID, SHA or conclusion obtained. Git access succeeds separately. No configuration change or market-data request was made. Hosted CI and ARM64 remain unverified, not successful by inference.
