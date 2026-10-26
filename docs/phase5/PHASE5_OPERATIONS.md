# Storage operations and security

**COMPLETE bounded tests:**immutable revisions,multi-page aggregate validation,known-version
schema checks,private paths/modes,quota/capacity rejection,explicit expiry/delete,source
permission rechecks,backup corruption rejection and restart behavior. Existing schema1
DDL retained;old single-page revisions remain readable. No DDL migration was necessary;
unknown versions fail closed. Future schema migration framework remains PARTIAL.

Backup uses SQLite online backup under a reentrant store lock,validates copied records,
and creates one fixed owner-private backup plus SHA256 manifest with atomic no-overwrite
linking. Existing backup must be explicitly deleted before creating another. No caller
paths. Restore validates hash/schema/index metadata/record caps/source permissions,stages
and purges expired rows,then publishes using SQLite's destination write transaction,
not replacement of a live file inode. UI requires explicit restore confirmation.

Tests interrupt actual SQLite destination copying and verify rollback. A child process
exits abruptly before and after a real SQLite commit;reopening recovers the expected
accepted state. These are not power-loss/fsync qualification. Deadline handling distinguishes
SQLITE_DONE from zero-page SQLITE_BUSY;completed copies do not produce false deadline
failure and busy copies retain the five-second bound. Failures/partial backup artifacts
are quarantined,not silently overwritten;operators inspect/delete failed backup artifacts.

32MiB main database,32 revisions,512KiB per payload. Backup/stage files separately≤32MiB,
plus SQLite rollback journals;128MiB free-space precondition for maintenance. This is not
an OS-enforced global disk quota. Multiple processes writing during restore and hard
power-loss/backup media/encryption qualification remain NOT VERIFIED. Same-instance
operations serialize;SQLite supplies interconnection transaction locking. No HA claim.

Access TTL stays7 days from original save;startup/write purge,not continuous physical
erasure. Backup files need explicit owner deletion/retention policy. Restores preserve
original retention timestamps and exclude expired rows. No source licensing authority
is inferred from a backup or an approval flag. Observed-data gates remain mandatory.

Origin/Host/private8787/proof controls preserved. New exact proof targets are history-ingest,
portfolio,evaluation. No wildcard CORS,arbitrary forwarded trust,credential transfer or
broker execution. Errors are bounded/sanitized. Keep fixture ports loopback-only;all are
stopped at delivery. No paid infrastructure or dependency added.
