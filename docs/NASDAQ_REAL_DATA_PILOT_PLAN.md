# NASDAQ real-data pilot — resource and validation plan

## Latest authorized prefix result — October 23, 2026, America/New_York

The single authorized GET returned206 with exact `bytes 0-4095/3524013057`,
4096 body bytes and a matching preflight validator. No second request occurred.
Observed gzip output14267 bytes contains350 complete S/R/H/Y BinaryFile frames
and10 residual bytes. Native decoding accepts346 S/R frames and explicitly
classifies4 H/Y frames unsupported. Format identification passes;complete
historical/engine compatibility remains INCONCLUSIVE. No L3 reconstruction.
The temporary supervisor's complete-boundary/total-consumption comparison defect
was reconciled offline using recorded aggregates and a synthetic partial-frame
control;the original blocked diagnostic remains preserved. Raw bytes existed only
in anonymous memory and are no longer retained. See
[NASDAQ_FIRST_PREFIX_INSPECTION.md](NASDAQ_FIRST_PREFIX_INSPECTION.md).
Earlier preflight and acquisition-rights observations below are historical;this
result does not authorize another request,larger range or integration work.

Latest resource/access assessment: [NASDAQ_PILOT_PREFLIGHT.md](NASDAQ_PILOT_PREFLIGHT.md),
October 23, 2026 (America/New_York). Metadata-only HEAD confirms reported size
and accessibility; current GET Range behavior remains unverified after a HEAD
Range anomaly. The concrete first request is limited to4 KiB, with no automatic
expansion. The broader staged limits below are historical/planning ceilings, not
authorization to acquire1 MiB. No market-data body was downloaded in preflight.

Prepared October 23, 2026 UTC (October 22, America/New_York), against planning
baseline `1855a2f7a4d4ef472b61ffa5fd3b6b1a76acf282`. **Planning only: no market
bytes acquired, no observed replay executed, no empirical acceptance claimed.**
P1G/P1H synthetic acceptance, when documented separately, cannot pass these gates.

## Source, permission and known artifact facts

Official directory: https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/ . Candidate direct URL:
https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/12302019.NASDAQ_ITCH50.gz . This exact filename,
prior reported compressed length **3,524,013,057 bytes** (3.282GiB), and prior Range
support are leads/evidence from P1C, not remeasured here. The name suggests a
December30,2019 NASDAQ ITCH5 artifact; the actual trading date, payload schema,
member count, uncompressed extent and session coverage remain unverified.

The [access ledger](REAL_MARKET_DATA_ACCESS.md) records the user-supplied written
Dan Vizconde sample download/use statement and its evidentiary limits. It supports
private sample investigation for this project. It is not independently authenticated
email evidence, an unrestricted redistribution license or a stated retention schedule.
Raw data, row-bearing diagnostics and correspondence remain private and outside Git;
publication of raw/derived data needs its own permissions assessment. A local SHA256
or successful HTTPS request does not create a license.

**Current instruction forbids NASDAQ/LOBSTER data downloads.** The steps below require
separate explicit acquisition authorization after resource verification. No LOBSTER
retry, proxy/network change, paid resource, mirror or external outreach is needed.

## Evidence catalog and historical profile

Reuse retained official documents rather than fetching market bytes:

| Reference | Recorded exact-byte SHA256 | Relevant contract |
|---|---|---|
| [TotalView-ITCH5](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf) | `45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3` | Wire fields, message lengths/types, source order/trade semantics |
| [BinaryFILE1.00](https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/binaryfile.pdf) | `a1f443400728b3ce44953e9ae263e4846fe6ad68420e7a635829872aefdfff60` | Big-endian two-byte payload length, zero terminal marker, external session identity |
| [Historical access guide](https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/ITCHFTP.pdf) | `77d0c9a5e86866951d99e58e5fda76b54ccf0316f19cbd7428492d459dee8177` | Account-based historical access and BinaryFile guidance; not proof this EMI artifact matches |

These document identities and source references are detailed in
[ITCH_50_VALIDATION_DESIGN.md](ITCH_50_VALIDATION_DESIGN.md). The retained ITCH PDF
has post-2019 revisions (including the2023 direct-listing update); it does not certify
every2019 enum/message profile. Before observed normalization, pin an explicitly
versioned historical profile and record every difference or unresolved field.
Do not infer a historical K price encoding from conflicting prose, accept later
extensions by assumption, or silently skip H/h/status/auction messages. P1E/P1F
supported families are S,R,A,F,E,C,X,D,U,P,Q,B; other recognized types need explicit
unsupported reporting or separately reviewed semantic support. Format inspection
can stop with an unsupported outcome without claiming a valid book.

## Staged acquisition proposal and resource envelope

Resource limits below are **proposed local safety choices**, not measurements,
NASDAQ requirements or promises that a useful interval exists. This is a versioned
pilot proposal, not an automatic increase of an implementation's configured limits.
Reconcile the final P1G/P1H measured profile before authorizing a run. The earlier
P1D profile in [MEMORY_STREAMING_DESIGN.md](MEMORY_STREAMING_DESIGN.md) remains its
own historical proposal; do not combine its larger order counts with this smaller
P1G-aligned count budget and call the result tested.

| Stage/resource | Proposed bound / gate |
|---|---|
| A: metadata-only preflight | After authorization, normal verified HTTPS with finite timeout; inspect listing/available checksum/README and response validators; no multi-GB GET |
| B: format-only prefix | First4KiB compressed from byte0, with an actual byte/read cap; expand only by a declared next attempt, at most1MiB compressed in this initial pilot |
| Input/output chunk | At most64KiB each; bounded gzip/framer buffers and one pending owned record, no entire-file buffer |
| Cumulative decompressed output | At most32MiB including all prelude and other-symbol records; absolute cap dominates ratio policy |
| Expansion protection | Use the independently validated P1H ratio/slack and member policies, record their exact values; never replace the absolute output cap with ratio alone |
| Considered source records | At most4,096 complete frames, including controls and other symbols; residual partial frame bytes counted separately |
| Source context | At most8 directory entries,1,024 lifetime IDs including retired entries,1,024 match references; early exhaustion is an explicit stop, not eviction |
| Native books | At most2 configured symbols,128 live orders and128 levels per book, query depth16,1,024 retained journal entries per book |
| Selected PMR / receipts |128MiB shared hard PMR cap plus2MiB explicit adapter/receipt budget; report ownership to avoid double counting; caps may stop before count limits |
| Native peak RSS | Proposed unsanitized256MiB acceptance ceiling, measured externally; failure requires profile review, not silent limit inflation |
| Independent oracle | Separate proposed128MiB RSS ceiling; if concurrent report combined process-tree peak as well |
| Disk for bounded pilot | Require at least64MiB free in a private external evidence root; retain at most1MiB compressed prefix plus bounded metadata/results, never a32MiB decompressed dump by default |
| Wall time | Proposed30seconds per bounded acquisition/inspection attempt, monotonic checks and finite blocking-read timeout; report time-budget stop distinctly |

Directory/order caps can be exhausted during the full-market prelude before either
target produces useful data. A source-aware scope policy must classify every record;
it cannot discard target liquidity or unknown state transitions. If caps cannot reach
a valid interval, this pilot is resource-blocked. Redesigning the journal, forgetting
retired references or restarting empty per chunk is not an authorized workaround.

Runtime/throughput for this archive is unknown. Forecast only after synthetic P1H
measurements and a permitted prefix inventory, reporting machine/build, compressed
and decoded denominators and shared-host variance. Never extrapolate a measured
prefix rate into a promised full-day completion time without qualifications.

A later **full compressed acquisition is a separate decision**, not part of this
pilot. At the prior length, one final compressed copy needs3,524,013,057 bytes;
a two-copy staging/publication scheme alone needs7,048,026,114 bytes. A proposed8GiB
free-space preflight leaves additional headroom but is not an uncompressed-size
estimate or guarantee. Streaming avoids an uncompressed-file requirement only if
output/artifact retention remains bounded. No full download is authorized now.

## Transport and integrity procedure

1. Save a private acquisition manifest: exact official/final URL, acquisition time,
   permission reference, request range, response status, Content-Range/Length,
   validator/Last-Modified when present, TLS/proxy outcome, software versions and
   declared caps. Preserve normal TLS verification and approved proxy behavior.
2. Require206 and exact requested Content-Range when relying on Range. A200 response
   can ignore the range; stop at the actual configured byte cap and report that
   range semantics were not established. Do not buffer an unsolicited full body.
   Bind successive pieces to the same representation using available validators
   and final content checks; reject inconsistent lengths/validators, never stitch
   changing versions. ETag is not automatically a cryptographic digest.
3. Compute SHA256 of exactly the acquired compressed extent and record its byte
   interval. A prefix hash must never be labeled a whole-archive hash. If a publisher
   checksum exists, record algorithm/file/coverage and verify only after obtaining
   its complete covered artifact; checksum availability is presently unknown.
4. Start gzip decoding at byte0. Deflate is not randomly message-seekable merely
   because HTTP Range works. Use validated P1H CRC/header/trailer/member/expansion
   handling. A deliberately bounded member prefix has **unverified complete-member
   CRC/trailer integrity**. Actual premature EOF is corrupt/truncated input; a
   declared acquisition cutoff is incomplete coverage, not fabricated EOF success.
   Gzip ISIZE is modulo2^32, so it is not the full uncompressed size of a large file.
5. Validate BinaryFile lengths and complete payloads, supported type lengths/enums,
   timestamps as raw time-of-day, exact integer Price(4)/share conversions and source
   positions. Record unknown/unsupported/malformed messages without silently skipping.
   A terminal marker plus CRC does not prove no upstream exchange messages were lost.
6. Record compressed read position, decoded position, last complete source record,
   last context commit and native per-book sequences separately. Reader lookahead
   and a pending record do not count as committed events. Retain first mismatch/error
   reproduction privately by source offset/config hash, not public raw rows.

No command in this design was executed against a market-data URL. Full gzip integrity,
framing compliance and source completeness remain distinct future findings.

## Valid initialization and semantic gates

The filename, early timestamp, S/O/S/Q observation, first add, terminal marker,
top-of-book agreement or aggregate snapshot cannot establish an empty L3 book.
Require authoritative source start semantics plus complete displayed initialization
and subsequent relevant history, bound to external session/date/venue and exact
artifact extent; or a genuinely complete identified L3 state including priorities
and source-context history. Do not infer a trading date/UTC clock from the filename.

Current P1G planning admits authored synthetic empty history, **not observed empty
evidence**. An observed initializer requires separately reviewed evidence/contracts.
Native complete snapshots hold at most64 orders and do not seed the P1F retired-ID,
directory, match or session lifecycle ledgers. Splitting a larger state into multiple
recoveries replaces rather than appends the book. A missing complete-context seed is
a capability blocker, not permission to fabricate IDs or queue ranks.

Retain daily identity namespaces and replacement chains; do not reuse retired IDs
just because a native live-order map is empty. Tracking numbers are raw fields, not
globally unique sequence counters. BinaryFile capture ordinals and native sequences
must be labeled locally derived. Actual exchange-loss detection requires capture
evidence beyond local contiguous ordinals. Preserve source ordering and reject
unknown order references; never synthesize earlier adds from later executions.

For a declared book-only run, displayed E/C reductions remain separate from prints,
crosses and broken-trade corrections. C's actual execution price/printability stays
external when native execution uses resting price; B never automatically restores
liquidity. Hidden prints and auctions do not create resting orders. Crossed-intermediate
books rejected by the native engine remain an observed-compatibility question, not
a reason to reorder or auto-match source data. Unsupported status/auction semantics
must block the affected validity claim even when bytes are decodable.

## Independent observed-market validation gates

| Gate | Required evidence / measurable pass condition |
|---|---|
| Rights/resources | Explicit acquisition authorization, recorded permission basis, declared private retention/output handling and successful free disk/memory/timeout preflight |
| Artifact identity | Exact acquired extents and SHA256; no contradictory dataset digests; full-archive integrity only if genuinely verified |
| Dated profile | Every encountered type/enum classified against pinned historical rules; zero silently omitted unknown target mutation |
| Initial state | Independently supported empty boundary+complete history or complete context/order seed; otherwise inspection-only, zero eligible L3 validation claims |
| Source accounting | Every complete considered frame in exactly one disposition: committed native, external observation, explicit other scope, rejected/unsupported or pending; partial bytes separately reported; unknown tail counts remain unknown |
| Independent reconstruction | Separate parser/context/flat-book calculation, after-each-relevant-event IDs/side/price/qty/FIFO/ledger consistency; negative controls must fail. Internal differential agreement alone is not a publisher-reference pass |
| External reference | Legally usable independently supplied depth/order snapshots with frozen event alignment and documented depth coverage. No source reference currently identified; zero eligible comparisons cannot pass |
| Comparison | Report total/eligible/attempted/exact/mismatch/unavailable rows and exact first mismatch reproduction; require zero unexplained mismatches in the declared eligible interval, never align post hoc to maximize matches |
| Resource behavior | All configured byte/count/PMR caps respected, no silent truncation/eviction, measured RSS within declared envelope, explicit incomplete-prefix outcome on planned stop |
| Reproducibility | Identical non-timing output hashes across supported toolchains/restarts from the authenticated start, checked provenance and complete report/export identities |
| Research claim scope | State displayed-book/tape/session/reference validity separately; no hidden-book, NBBO, causal execution-quality or production-trading equivalence claim |

An external aggregate reference can test eligible depth but cannot independently
prove every queue identity or FIFO priority. If no publisher/reference source exists,
report model/differential validation only and leave that empirical gate unverified.
Predeclare symbols, interval, budgets, price/lot rules and alignment before comparing
outcomes; do not select a favorable interval after seeing mismatches.

## Dependency-ordered real-data backlog

| Package | Required work and independent acceptance | Dependency / blocker |
|---|---|---|
| R01 permission/artifact record | Preserve supplied correspondence privately; reconcile any applicable restrictions; record exact official artifact/metadata without claiming fresh verification | Separate acquisition authorization; raw/derived publication rights unresolved |
| R02 synthetic transport acceptance | Complete P1G/P1H independent oracle, atomicity/fault/restart, compiler/sanitizer/package and bounded streaming gates | Authorized synthetic phases; no market-data dependency |
| R03 bounded private inventory | Implement/run the authorized capped byte0 inspection, true framing/profile/type/time inventory and exact hashes | R01/R02 plus explicit resource-verified acquisition approval; may be inconclusive within caps |
| R04 observed initialization | Establish actual complete start/history or design separately reviewed complete-context seed; reject unknown state | R03 and authoritative boundary evidence; unavailable state is a valid NO-GO outcome |
| R05 historical semantic gaps | Review unsupported encountered families, crossed states, units and correction/auction limits against dated source rules; independent fixtures before changes | R03; separately authorized observed integration work, no opportunistic semantic weakening |
| R06 independent reference | Obtain permitted independently supplied snapshots/coverage and freeze alignment; maintain separate source-byte reference model | Data/reference availability and permitted use; currently unresolved |
| R07 bounded observed pilot | Run only declared eligible prefix with exact accounting, zero unexplained eligible mismatches and full resource/provenance report | R04–R06; stops or zero eligible coverage cannot pass |
| R08 later empirical studies | Held-out intervals, sensitivity/calibration/leakage review and publication assessment | R07 plus suitable data/rights; outside synthetic candidate readiness |

**Recommendation: CONDITIONAL GO for a later private bounded inspection, after
explicit acquisition authorization and resource verification. NO-GO for observed
L3/research-validation claims today.** The smallest safe next action is completing
synthetic P1G/P1H gates and presenting a measured, fixed pilot profile for approval;
do not use the newly supplied permission as authorization to download in this task.
NASDAQ initial state/reference evidence and LOBSTER Support Case #17931099 are
independent. Neither the November5 target nor November12 contingency can substitute
for missing observed evidence or authorize unrestricted redistribution.


## P1I/P1J readiness update — October23,2026 America/New_York

P1I was pushed and verified at `5584ce34de5b839d2a78fabcd8e6603cec1185f3`;
P1J independently reviews that checkpoint and any subsequent scoped evidence-tool
repairs. The bounded synthetic pipeline now exists and its two-book/default-journal
selected profile has measured restart coexistence below the128MiB PMR proposal.
This replaces only the earlier plan's pending synthetic prerequisite, not its
observed-source gates. No market bytes were downloaded or inventoried.

The current reconstructor factory still requires synthetic authored-empty evidence.
Unknown symbol bindings and unsupported historical administrative/auction/status
messages stop explicitly. A full-market prelude can exhaust directory/lifetime/match/
source budgets before a useful target interval. Native snapshot capacity64 does not
supply a complete source-context/FIFO seed. Single-member gzip policy must be checked
against the actual artifact member structure rather than relaxed silently.

**Smallest next step:** separately authorize a format-only byte0 prefix inspector,
using standalone bounded gzip/framer/decoder APIs, not the synthetic L3 factory with
an observed artifact relabeled synthetic. Recheck private disk/free-space, memory,
monotonic time and actual byte limits immediately before the run. Start at the
existing4KiB proposal, no automatic growth past its separately reviewed1MiB maximum;
32MiB raw output and4,096 considered frames remain independent caps. A prefix may
end before useful metadata and must be reported inconclusive, not session-complete.
Resource observations from this host do not reserve storage or guarantee throughput.
No full3,524,013,057-byte archive is authorized by this update.

Record expected and observed transport extents, validators, SHA256, framing/message
histogram, unsupported records, residual/truncated state and exact cutoff. A bounded
compressed prefix cannot establish whole-gzip CRC/integrity or exchange completeness.
Only after actual inventory/profile review should a separately authorized source-
scope/observed-provenance/initialization adapter be designed. Independent observed
snapshot/order reference and predeclared alignment are required for externally
referenced L3 correctness; model agreement alone is differential validation.

The user-provided Nasdaq statement supports download/use of official samples; it
does not establish unrestricted redistribution/publication or an explicit retention
schedule. Keep raw prefixes, row-bearing diagnostics and correspondence outside Git
and private. LOBSTER support case17931099 is separate; no retry or network change
was performed. Real-market validation remains NO-GO today; a later resource-bounded
format-only pilot is CONDITIONAL GO after its explicit authorization and preflight.


## Release-candidate closure review — October23,2026

No source request or market bytes were acquired. The smallest recommended next
experiment remains the **separately authorized format-only4KiB compressed prefix
from byte0** of the exact official artifact above. It is not an L3 replay or an
archive-integrity test. An owner-authorized later attempt may increase the cumulative
compressed allowance up to1MiB; there is no automatic escalation in the first run.

Predeclare the existing32MiB decompressed/4096-frame limits,64KiB buffers,128MiB
PMR/256MiB native RSS ceilings,64MiB private free-disk preflight and30s wall time.
RSS/PMR values are proposed pilot gates, not measured observed-market requirements.
Actual prefix output can stop much earlier due to full-market directory/ID budgets.
Stop on byte/time/resource exhaustion, ignored/contradictory Range, changing
validators, invalid framing/gzip, unknown profile or missing rights. Treat a normal
prefix gzip EOF/trailer absence as incomplete, never as full archive validation.
Retain exact offset/extents, timestamp of acquisition, SHA256 for received bytes,
compressed/decompressed counts, message-type/length inventory, first/last complete
source timestamps, partial-byte accounting and every error. Publish no raw rows.

Keep raw prefix/row diagnostics in a private directory outside Git; no compressed
archive, market row or correspondence belongs in the source repository. The
user-provided download/use statement establishes neither a specific retention period
nor unrestricted redistribution. Owner must declare retention/deletion policy and
private cloud handling before acquisition; no expiry is invented here.
A prefix digest authenticates only the locally received extent, not the full
3,524,013,057-byte archive. Observed trading date, initial L3 eligibility, external
reference and empirical agreement stay unverified even if the format probe passes.
