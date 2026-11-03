# Observation recovery admission

Baseline: `90ebb956df5143670702bcc512de81821cdfa23d`. This closes Sprint 1 R06 within the private, opt-in observation ledger; it does not change the native journal or authorize observed-data storage.

## Reproduced defects and repairs

- Recovery fetched all payload rows before checking count/bytes. Admission now caps the SQL count at 10,001, rejects more than 10,000 rows, and checks aggregate payload bytes (16 MiB), individual bytes (65,536) and BLOB types **before returning payload rows to Python**.
- Capture/digest/parent columns could be oversized or wrongly typed even when payloads were small. SQL validates their lengths and types, integer receipts and numeric clock types before row delivery. Metadata is limited to four bounded, uniquely keyed fields. Invalid or duplicate metadata is rejected.
- The old JSON reader admitted duplicate fields and insufficiently validated retention/origin metadata. The existing strict bounded decoder now checks the exact envelope, policy, finite clocks, capture/receipt correspondence, known origin and observed-retention authorization. Extreme integer clock input produces a structured rejection rather than a float-conversion `OverflowError`.
- Missing metadata or a missing table could be recreated by constructor initialization. Only a new zero-byte store is initialized; existing version-1 stores must pass recovery without repairing missing evidence.
- Preflight and validation previously used separate read views. An explicit read transaction now covers admission, bounded streamed rows and final chain/receipt checks. An independent connection writing concurrently cannot change that accepted read snapshot.

Rejected appends leave the accepted database/cache unchanged. Hashes, capture transitions, contiguous receipts within each retained capture and final tail metadata must agree. Expired rows are validated before pruning. No corrupt row is silently skipped. Append trimming permits one bounded 128-event transient batch, then restores the existing retained budgets.

## Compatibility and boundaries

There is no schema migration or new schema version. Valid existing version-1 envelopes, private-file modes, original per-record TTL, prefix eviction, pruned suffixes and restart behavior remain supported. Minimal valid legacy events need not acquire fields retroactively. Old malformed records that happened to pass weaker validation intentionally fail closed. A default-disabled store stays disabled; observed recovery requires current permission and an admissible stored permission policy. All returned records remain `RETAINED_HISTORICAL_NOT_CURRENT`.

An empty file is indistinguishable from a newly provisioned store; this does not restore a wholly lost database. Hash-chain consistency is not source authentication, exchange completeness, or protection against a privileged owner rewriting the entire ledger. The caller's private directory remains part of the trust boundary. SQL preflights bound delivered bytes/rows, not a literal Python heap or kernel I/O deadline. A decoded result can consume more memory than its serialized payload.

## Independent fault evidence

The original 11-method cohort produced seven assertion failures and three errors; the corrupt SQLite header case already rejected. Later failing-before runs preserved two constructor failures, ten subtest failures across three scalar/metadata methods, and one extreme-integer error. Logs and hashes are bound in EVIDENCE.json. Fixtures author SQL/JSON and recompute chain hashes independently to demonstrate that a matching digest alone is insufficient.

The final 26 admission methods plus seven workload methods form a strict 33-test cohort. Coverage includes legacy restart, expired/pruned suffixes, row/byte/type limits, duplicate JSON/metadata, unknown origin, invalid policy, nonfinite/extreme clocks, missing metadata/tables, receipt discontinuity, corrupt database bytes, nonmutation on rejection, concurrent read/write snapshots, and actual `SQLITE_FULL` using a fixed page ceiling. The latter proves rollback and valid restart; the sustained workload separately injects ENOSPC before commit. Neither is a hardware power-cut qualification.

Reproduce offline from the repository root with the installed native module and runtime dependencies:

```bash
.venv/bin/python terminal/tests/run_institutional_sprint2.py
```

The cohort requires exactly 33 executed tests, zero failures/errors/skips. It disables provider/execution gates; its injected connector cannot contact a provider. The manual-only owner-gated ARM64 workflow includes the cohort but was not dispatched in this sprint.

Additional legacy qualification loads the **actual committed Sprint 1 writer** from `git show 90ebb956df5143670702bcc512de81821cdfa23d:terminal/stocks/observation_store.py` into a private temporary module. It authors four independent SQLite databases: empty, two captures (12 retained events), a pruned suffix (3 retained events) and expired history (0 eligible events). Current recovery equals the old writer's expected recovery exactly in all four cases. The old writer source hash, database hashes and expected/actual result hashes are recorded in EVIDENCE.json. This is compatibility with genuine baseline-produced version-1 artifacts, not just current encoder round-tripping or processing an owner's database.
