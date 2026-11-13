# Bounded primary filing and historical scheduling extension

The coordinator now accepts advertised `.xml`, `.htm`, `.html` and `.xhtml`
originals. XML remains the existing instance contract. XHTML uses the existing
explicit inline document-set profile with exactly one acquired original: ordered
passive text, the two supported numeric transformations, local continuations,
exact scale/sign and original document provenance. This does not repair HTML,
follow document hyperlinks, acquire arbitrary multi-document sets, or implement
additional transformation/target semantics. Unsupported input rejects publication.
DTS closure, exact directory sizes, host/path restrictions and transaction limits
remain enforced. No source permission, transport or retention is enabled by default.

`await coordinator.discover_filings(start=..., end=..., max_shards=2,
max_filings=8)` explicitly scans current submissions plus at most four advertised
older shards. At most 128 advertisements and 10,000 input rows per response are
admitted; existing normalization retains at most 1,024 eligible rows per response
and reports truncation. At most eight filings are returned, ordered by filing date
and accession descending. The date range concerns filing dates, not acceptance-time
selection. Each entry retains its metadata response URL, SHA and original receipt.
Contradictory duplicate accessions reject. Deferred shards and output truncation
are explicit; complete_history remains false. This is a finite plan without a
background worker, polling, application startup or automatic filing execution.

`await coordinator.ingest(accession, metadata_shard=advertised_name)` explicitly
executes an older-shard candidate. It revalidates the current issuer index,
advertisement, row count, date envelope, normalized accession and overlapping
current rows before fetching the filing. The current index and historical shard
are retained together with the filing directory and original DTS bodies. Discovery
results are not trusted as authority for a later transaction. Both operations share
the existing source lock, rate limits, independent permission checks, 30-second
transaction ceiling, 24-attempt budget and 8 MiB response-byte ceiling.

Existing no-shard checkpoints continue to emit version 1. Collections containing
historical metadata emit explicit version 2 with a history_key per historical plan.
Restore accepts both versions, checks the version/plan relationship, revalidates
all source bindings, reparses originals and remains PAUSED_RESTORED without I/O.
Older implementations reject version 2 rather than silently losing its binding.
Every filing-local DTS dependency is checked against the retained directory during
restore as well as initial acquisition. Private revision store format and native
checkpoint formats are unchanged.

The existing explicit workspace installation and Company-v2/Stock Intelligence
contract accept the resulting collection. The cross-language contract now includes
an acquired inline primary and checks installed collection matching. Missing
presentation/statement structure remains unavailable; no accounting equivalence,
GAAP alias, full schema/DRS validation or complete financial statement is inferred.

Seventeen new offline integration regressions cover inline exact values/provenance,
restart/immutability, unsupported semantics/HTML, bounded schedules, permissions and
shared locks, hostile names, count/date/duplicate conflicts, historical execution,
dependency revalidation and rejection of shard URLs supplied as DTS references.
No live SEC, market, account, application, deployment or owner acceptance was used.
