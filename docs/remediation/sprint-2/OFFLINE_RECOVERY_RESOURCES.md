# Bounded offline recovery and resource acceptance

Source: `62d8d50e2dd629db181114eaceb5845509a137b6`, clean at final measurement.
Only authored synthetic fixtures; no provider history, observed-data retention,
private dataset or journal redesign. Measurements are from one shared Linux x86_64
Codex environment, not exchange latency, capacity planning or sustained-session SLA.

## Interruption and failure acceptance

| Test / source | Executed result | Boundary of the claim |
|---|---|---|
| New `terminal/test_sprint2_recovery.py`: actual child exits73 during destination SQLite page-copy | Existing destination revision survives process restart; backup revision is absent until explicit successful restore; subsequent restore yields exact original revision. | Process interruption, not machine power loss, filesystem durability certification or cloud failover. |
| Same: child exits74 after backup DB publication but before manifest creation | Incomplete backup is rejected; next backup refuses overwrite; accepted store remains readable. | Incomplete backup is deliberately not auto-repaired. Owner may explicitly delete it after diagnosis. |
| Same: backup payload corrupted and outer manifest rehashed consistently | Internal revision validation still rejects; live accepted revision unchanged. | Hash integrity is not a signature against an adversary able to rewrite every semantic identity and trusted reference. |
| Existing `terminal/stocks/test_phase5.py` | Pre/post-SQLite-commit child exits, partial-copy exception rollback, deadline completion, denied observed restore and bounded backup checks pass. | SQLite transaction acceptance within tested process boundaries. |
| Existing `terminal/stocks/test_observation_store.py` | Abrupt uncommitted-frame exit, restart suffix/digest verification, corruption/tail deletion, expiry,10,000-record cap, byte cap and concurrent summary checks pass. | Retained historical suffix, not full provider-source loss recovery or current-live state. |
| New shutdown review plus existing `terminal/test_research_resources.py` | Cancelled waiters/close retain one physical worker until drain; repeated close and failed work accounted; new work denied after close. | Cancellation does not forcibly stop a Python/native thread. No preemptive CPU guarantee. |
| Existing browser push and stock reliability | 5,000-event burst, bounded dedup/history,8-client exhaustion, quiet heartbeat, real2s slow-send timeout, cleanup, generation, reconnect and subscription checks pass. | Bounded local snapshots, not provider backfill, measured live recovery time or transport-wide queue clearance. |

New recovery3 and ownership2 tests pass in all three native-binding consumer
configurations. Existing tests are included in the stock207 and Sprint1-25
cohorts; they were rerun, not counted as new independent implementations.

## Measured envelope

The existing `scripts/qualify_remediation_envelope.py` was reused unchanged. Final
clean-commit run: [envelope.json](evidence/envelope.json). An earlier dirty-baseline
measurement is separately labelled, not misrepresented as clean-source evidence.
Fixture:5,000 authored quotes;1 warmup and5×100 concentration calls over40 uint64-max
levels, with tracemalloc enabled. Clock, rate and RSS are actual observations:

| Measurement | Actual |
|---|---:|
| Accepted source receipts |5,000|
| Retained history / dedup keys |256 /256|
| Explicit evictions |4,744|
| Quote fixture processing elapsed |1.636149 s|
| Fixture processing rate |3,055.96 events/s|
| Python tracked current / peak |912,810 /944,758 bytes|
| Process peak RSS |36,948 KiB|
| Process user / system CPU |2.218497 /0.01549 s|
| Concentration mean ns/call per100-call sample |561746.11;553131.79;566435.62;570283.88;565253.36|

Accepted-count identity SHA256 is unchanged from Sprint1:
`6c9864f30b712520a232bf2c4bc69eea5ba35872c51d349c462a762d41eb01a6`.
No speedup is claimed; tracemalloc, startup and shared-host contention matter.

Enforced test-child limits:512MiB virtual address space,20/22s CPU soft/hard,
32MiB per output file,30s parent wall bound. Native probe processes have10s
watchdogs. These are **qualification process bounds**, not a new global service,
browser GPU, RSS or operating-system disk quota. Synthetic history/resource tests
use temporary directories; nothing enables actual observed persistence.

## Native journal scaling, unchanged implementation

Four independent native processes; all report zero live bytes after destruction.
See [journal-scaling.json](evidence/journal-scaling.json).

| Records | Reset cadence | Live PMR bytes | Peak PMR bytes | Allocations | Peak RSS KiB |
|---:|---:|---:|---:|---:|---:|
|128|none|1,566,112|2,348,960|9|13,192|
|1,024|none|12,525,984|18,788,768|12|13,968|
|4,096|none|50,102,688|75,153,824|14|50,736|
|1,024|128|12,555,744|18,803,648|24|13,976|

Physical record12,232 bytes; separately retained restart data3,720 bytes when
required; logical combined entry15,944 bytes. The initial15,944-byte finding is
not erased by the physical split. Capacity growth causes temporary peaks; linear
extrapolation of live records alone is not an RSS guarantee. A100,000-record archive
is roughly1.22GB of physical records before restart entries, native book/context,
capacity slack and other processes. It is not qualified by a4,096-case measurement.

Further optimization is deferred. A separate measured proposal must compare exact
journal/replay/snapshot equivalence, version/migration behavior, allocation failure,
restart semantics and all frozen identities before storage layout changes. No
failure here justified redesigning the journal during private-release qualification.

## Reproduction

On an authorized offline checkout with existing native builds and dependencies:

```bash
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_remediation_sprint2.py
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_live_market_suite.py
PYTHONPATH=build/python-release/python:. .venv/bin/python terminal/tests/run_remediation_sprint1.py
PYTHONPATH=build/python-release/python:. .venv/bin/python scripts/qualify_remediation_envelope.py --native-build build/python-release --output build/private-envelope-new
```

ASan/UBSan used the existing toolchain-matched preload and
`scripts/run_python_sanitized.py` recorded in evidence. No mandatory assertion,
budget, test or leak finding was suppressed. No RPO/RTO, long observed session,
cross-machine recovery or lossless provider replay is asserted.
