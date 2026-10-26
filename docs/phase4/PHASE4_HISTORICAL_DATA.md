# Private historical storage

New history_store.py persists already accepted normalized single-page snapshots,not raw
provider responses or complete market archives. Original HistorySource/UTC nanoseconds,
feed/coverage/adjustment/origin/digests remain. Rebuild/revalidation precedes publication.
Snapshot revision is SHA256 of the canonical core including its provenance receipt;
identical content is idempotent,changed content gets a distinct revision. Existing
corrupt content at the same revision fails rather than claiming idempotent success.

Limits:32 revisions,256 bars/snapshot,512KiB payload/snapshot,4096-byte SQLite pages,
8192-page32MiB main-database cap. SQLite synchronous FULL,DELETE journal,secure_delete ON;
connection/transaction scopes close explicitly. A transient rollback journal and filesystem
allocation are additional to the main-file cap;not a full disk-quota guarantee.
Linux/owner UID,private0700 directory,0600 regular single-link database,non-symlink path,
application ID/schema version and file size are checked. Unknown databases are refused.
Default is disabled and no data is written merely by loading a stock.

Configuration(optional,server-only,no provider activation):

```bash
mkdir -m 700 .gig-history
export GIG_HISTORY_STORE_ENABLED=1
export GIG_HISTORY_STORE_DIRECTORY="$PWD/.gig-history"
```

Existing directories must already be private;the service does not silently chmod them.
Do not enable GIG_HISTORY_OBSERVED_RETENTION_APPROVED unless actual source retention and
cloud-processing rights are independently approved. Observed retention is denied by
default on both save and read,including after restart/approval removal. Revisions are
not silently destroyed on approval removal;owner can delete them explicitly.
Private directory/SQLite extensions are Git-ignored. Keep all storage out of source archives.

Access expires seven days after explicit save. Startup and writes purge expired rows;
there is no continuous deletion daemon or secure physical-erasure guarantee. Owners
requiring strict wall-clock physical deletion must arrange a qualified cleanup policy
before using observed data. No hardseven-day deletion SLA is claimed. Delete removes a
revision explicitly;backups/filesystem snapshots remain the owner's responsibility.

GET lists bounded revision metadata or returns a verified snapshot with the original
v2 JSON Schema intact;storage revision/completeness stay in the outer wrapper. POST
accepts only current accepted symbol save or exact SHA256 deletion,no client file paths.
SQLite transactions protect publication/capacity checks. Tests cover restart,idempotence,
multisymbol/timeframe records,expiry,tampering,wrong schema,permissions,symbolic links,
capacity,origin controls,read-gate revocation and schema compatibility. Process kill during
fsync,disk-full/power-loss campaigns,backup restore,encryption and concurrent deployment
migration are not qualified. No crash-safe native-engine recovery is implied.

Current limitation:single-page bounded snapshots only;generic Phase3 normalization
supports up to4 pages,but persistent ingestion rejects multipage snapshots explicitly.
No upstream paging,exchange holiday calendar,corporate-action acquisition or automatic
native replay from stored prices is implemented.
