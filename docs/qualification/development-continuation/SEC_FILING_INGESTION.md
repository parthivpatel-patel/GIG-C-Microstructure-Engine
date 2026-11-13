# Bounded read-only SEC filing/DTS ingestion and immutable source recovery

This is engineering with authored HTTP fixtures,not real-provider qualification.
There is no default transport,startup task,HTTP acquisition route or permission
activation. FilingIngestor requires explicit enabled=true,injected transport and
existing SEC identifying/fair-access permission. Observed processing requires a
separate explicit source permission/reference. No Alpaca/account/trading capability
is involved. SECReadWire implements fixed-host GET only;MockTransport exercises it
offline. The owner's actual credentials/configuration were not accessed.

## Supported acquisition transaction

An explicit accession is matched against normalized current submissions using the
existing SEC parser. The exact filing directory index must match issuer/accession.
The primary document or explicitly selected filename must be advertised as a file
with matching bytes. No filename similarity guesses an extracted instance. The
initial supported instance format is plain XBRL XML. HTML/inline primary documents
are explicitly unsupported here,even though supplied-inline parsers exist.
Unadvertised history shards/documents are not fetched automatically.

A safe instance drives bounded DTS dependency discovery. Current-filing relative
resources must be advertised with consistent sizes. External taxonomy resources
require exact operator-approved HTTPS URLs on the fixed official taxonomy hosts;
no arbitrary host,port,query,redirect,encoded path or cross-accession fallback is
allowed. Missing import locations,ambiguous US-GAAP versions or unsupported closure
fail before publication. Supplied namespace declarations determine the supported
selected-concept profile;no extension accounting aliases are inferred.

Source bytes,SHA/URL and original local receipt completion times are retained in
bounded memory. Receipt is not filing acceptance. Acceptance/filed/amendment identity
comes from bound supplied metadata;amendment predecessor is never inferred.
Already admitted source URLs and filing metadata cannot silently change. Cache TTL
is600seconds;cached receipts are not restamped. Explicit fresh requests can reveal
immutable conflicts. Failed/cancelled/over-budget transactions preserve all prior
accepted collections and source records. Directory/submissions responses,instance
and dependency hashes are bound separately. Complete history/source authenticity
is never inferred from self-consistent hashes.

Limits:2MiB/document,8MiB total consumed source bytes/retained source set,32source
records,8filings,16taxonomy documents,24HTTP attempts and30seconds/transaction.
At most one retry after429/503/timeout uses existing bounded equal jitter and a
validated Retry-After floor. Each request is spaced at least1.01seconds with an
8second transport/read timeout. The workspace factory shares its existing SEC
lock/rate timestamp with other source operations. Different independent processes
still require operator-wide fair-access coordination. Unknown-length bodies at
the exact ceiling are refused without probing beyond it. The wire may prefetch
one64KiB chunk;the coordinator's bounded read contract limits materialized source
bytes. These are application resource limits,not a TCP-byte/RAM/latency SLA.

## Explicit product integration

StockWorkspace.create_sec_filing_ingestor registers at most8coordinators and keeps
execution disabled unless explicitly requested. It preserves existing configuration
and refuses unknown CIKs/replacement registration. install_sec_filing_result admits
only an accepted or paused-restored collection through the existing issuer-bound
product admission. There is no automatic HTTP mutation or provider gate change.
The separate company XBRL contract can expose sanitized source-ingestion status:
state,counts,last HTTP status/fixed error and lifetime counters;never headers,
contact values,credentials or raw body. This is not live-stream qualification.

## Optional immutable source storage

FilingCheckpointStore requires both enabled and retention_approved. Read permission
alone never enables raw-source retention. The dedicated directory must already be
private/owner-controlled;the suggested .gig-sec-xbrl directory is ignored by Git.
Source images include exact bodies/receipts,plans and collection identity,not
User-Agent,request headers or raw permission-reference values. Observed restore
requires the same explicit processing scope/reference hash. Source retention must
be independently permitted before using it with actual responses.

The store reuses the existing immutable native/source file publisher:private temp,
file fsync,exclusive link,then directory fsync. It does not redesign the C++ journal.
A nonblocking private lock and16revision/64MiB quotas include orphan temps. Existing
revisions are verified,idempotent and never overwritten. Interrupted pre-publication
writes leave no revision;post-link uncertainty requires explicit reopen. No automatic
pruning occurs. Files are0600 and directories0700;symlinks/nonregular files reject.

Checkpoint schema1 is bounded to12MiB. Restore checks the externally supplied SHA,
exact schema/scope,source bodies/hashes/URLs,metadata binding,closure and collection
identity,then reparses all sources before one state replacement. Unknown schema or
changed parser-derived collection identity rejects;there is no silent migration.
Restored state is PAUSED_RESTORED,cache expired,no auto network connection. No RPO,
RTO,full-session provider recovery or hardware durability guarantee is claimed.

## Current qualification and limitations

21ingestion tests plus8storage/product tests cover offline wire calls,rate/retry/
source boundaries,immutable metadata,failed refresh,allocation and disk failures,
cancellation,permissions,corruption,publication uncertainty and cross-process restore.
A test initially assumed mkdir(0755) bypassed umask;the fixture now chmods the
negative-case directory explicitly. Assertions were preserved. A diagnostic-order
refinement restored the precise source-change error;failures remain in evidence.

Actual public SEC source schemas/host behavior,large issuer responses,inline filing
acquisition,older submissions shard scheduling,full taxonomy/schema/DRS semantics,
broad amortized/multi-process resource behavior and target Codespaces/provider
acceptance remain unqualified. No source/financial/accounting completeness is claimed.
