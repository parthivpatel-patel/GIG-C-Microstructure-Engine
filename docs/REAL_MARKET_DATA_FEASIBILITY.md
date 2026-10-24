# Phase P1A — real market data feasibility and validation design

Review date: 2026-10-21 UTC. Repository: parthivpatel-patel/GIG-C-Microstructure-Engine.
Reviewed baseline: `38c91c38eebe945d5c9f9f9a86bbdfbfc2393cd5`.
Branch: `feat/bootstrap-cpp20-engine`.

## Decision and evidence boundary

**Conditional feasibility, with acquisition and initial-state blockers.** The engine
can reconstruct a bounded, ordered stream of displayed order additions, reductions,
deletions, replacements and identified executions when all referenced orders and
state boundaries are known. It is not yet a validated NASDAQ adapter. A LOBSTER
aggregated-depth file cannot supply missing order identities or FIFO history. A
nonempty intraday sample cannot truthfully be declared empty just to make replay run.

Both official URLs supplied for this review were attempted directly with TLS
verification and the configured proxy. Both failed before origin access with
CONNECT 403. Consequently, **current official availability, sample inventory,
specific terms of use and the contents/revision of the supplied PDF could not be
independently verified in this environment**. No market dataset was downloaded,
parsed, reconstructed or compared. There are no real-data matches, throughput
measurements or sample hashes to report. These are unavailable measurements, not
zero-event successes. Public accessibility elsewhere is not disproved by this
network restriction.

The report is complete as an evidence-qualified feasibility/design review. The
external format matrices below are explicitly **provisional design hypotheses**
based on conventional LOBSTER and ITCH 5.0 layouts, not findings from downloaded
files or an accessible current specification. They must be checked against the
actual licensed artifacts and date-specific official specifications before code is
written against them. In particular, this review does not assert a legal right to
download or redistribute either dataset, or claim every current ITCH extension is
covered by the conventional message list.

Recommendation: authorize a narrow acquisition/schema/initial-state investigation
first, after official access and usage rights are resolved. Authorize the minimal
adapter only if its state and coverage gates below can be met. Do not implement an
L2-to-L3 bootstrap, infer initial queue identities, or optimize the journal in P1A.

## A. Repository, access and evidence verification

### Repository observations

At entry, `git status --short` was empty. Local HEAD and the exact remote development
branch both returned the reviewed baseline. Main remained
`165c5038336887116d69160b0d8e5a1a5ef59d16`. No reset, checkout, rebase or history rewrite
was performed. The only repository change authorized in this phase is this new report.
Implementation, tests, package, institutional audit and remediation evidence remain
unchanged. Source references below refer to the reviewed baseline, not a future adapter.

Preservation checks compared SHA256 before and after this review:

| Existing document | Unchanged SHA256 |
|---|---|
| `docs/INSTITUTIONAL_ENGINEERING_AUDIT.md` | `25045c0c3820ca1ad17852be62ffece5b84a1261900301fb9f4dce681d0d7ef3` |
| `docs/CORRECTNESS_REMEDIATION.md` | `becc51cdd5f420814bbf32ca1b9dd0cfc10f9fc2add32c462860fc44bc5c85a6` |
| `docs/baselines/remediation-validation.json` | `8279682b837bd444613ec2e787c26cb13022d6aad4c50157b2bdd6bab993dce4` |

These identify the complete baseline documents, including the audit's existing
remediation addenda; the original pre-remediation audit preservation evidence remains
in the unchanged remediation report.

### Official-source access ledger

| Source | Exact supplied URL | Observation at 2026-10-21 22:24:39 UTC | What is established |
|---|---|---|---|
| Official LOBSTER sample index | https://data.lobsterdata.com/info/DataSamples.php | curl exit 56; CONNECT tunnel failed, response 403; final origin HTTP code `000`; downloaded body bytes `0` | This environment could not reach the index. No sample link, archive size, sample date or terms were verified. |
| NASDAQ historical ITCH document | https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/ITCHFTP.pdf | Same proxy denial, exit 56, origin HTTP `000`, body bytes `0` | The PDF was not retrieved. Its title, contents, revision, historical access instructions and wire-format coverage were not verified. |

The proxy emitted `HTTP/1.1 403 Forbidden` with `server: envoy`; this was not a NASDAQ
or LOBSTER origin response. The runtime reported a connected environment with a
restricted destination list lacking these hosts and network-policy state `unknown`.
Actual request failures are the access evidence. No proxy bypass, mirror retrieval,
credential change, subscription, account creation or paid resource was attempted.

Commands used (response headers outside the checkout):

```sh
mkdir -p /tmp/gig-p1a-evidence
curl --max-time 25 --location --silent --show-error \
  --dump-header /tmp/gig-p1a-evidence/lobster.headers \
  --output /tmp/gig-p1a-evidence/lobster-samples.html \
  --write-out 'LOBSTER HTTP %{http_code} bytes %{size_download}\n' \
  https://data.lobsterdata.com/info/DataSamples.php
curl --max-time 25 --location --silent --show-error \
  --dump-header /tmp/gig-p1a-evidence/itch.headers \
  --output /tmp/gig-p1a-evidence/ITCHFTP.pdf \
  --write-out 'NASDAQ HTTP %{http_code} bytes %{size_download}\n' \
  https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/ITCHFTP.pdf
```

The two proxy header files have SHA256
`b15b15bbbc091897c2c80b9faa06ae66e2429d01d0c2423667516ec84df28645`.
This hashes an error response, **not a sample, specification or licensing artifact**.
Raw evidence is temporary and is not made available by cloning this report.

To resolve access, use the supported environment network configuration workflow to
allow `data.lobsterdata.com` and `www.nasdaqtrader.com`; inspect any official redirects
before requesting additional destinations. Re-read the actual pages/specifications
and linked legal terms after access succeeds. Do not use a third-party sample or
mirrored specification as proof of official permission or byte identity.

### Inspected engine evidence

| Contract / code at baseline | Actual behavior and relevance |
|---|---|
| `include/gig/core/numeric.hpp:13–44,117–230` | Distinct checked IDs, signed 64-bit price/time, unsigned 64-bit quantities; IDs start at 1; exact decimal/rational conversion. Source share units and price units need explicit rules. |
| `include/gig/events/contracts.hpp:56–115` | Missing-value reasons; clock, stream/session/epoch, sequence, source record, capture ordinal; observed/synthetic origin; dataset/version/license/digest and bounded lineage/parents. No dedicated native raw-exchange attribute bag. |
| `include/gig/events/contracts.hpp:118–167` | Add, cancel, replace, print versus identified execution, quote, reset, bounded order/aggregate snapshot, session and unsupported variants. No native match ID, participant attribution, auction kind, execution-price override or trade-break payload. |
| `src/events/validation.cpp:34–57,69–106,185–207,209–250` | Missing timestamps can remain missing; a supplied timestamp requires supported clock/precision. Complete validation requires instrument/venue/scope/sequence/source record and dataset/version/license/origin/source/lineage. Derived transformations require parents. Unsupported payload rejects. |
| `src/book/order_book.cpp:12–20,35–110` | Ordered price maps, per-price FIFO lists, hash ID index; staged allocations before commit; duplicate live IDs and crossed additions rejected. Equal bid/ask is allowed. No exchange matching is performed. |
| `src/book/order_book.cpp:144–231` | Cancels and executions require an existing order. Execution side and price must equal the resting order; quantity cannot exceed remaining. Print-only trades do not mutate. Session/quote observations do not mutate orders. |
| `src/book/order_book.cpp:233–267`; `include/gig/events/contracts.hpp:156–160` | Explicit recovery accepts only a complete order-level snapshot, with at most 64 orders and explicit priorities/boundaries. Aggregated or bounded-depth recovery is unsupported. |
| `include/gig/replay/replay.hpp:6–34`; `src/replay/replay.cpp:38–60,71–143` | Initial state requires snapshot by default; declared-empty is an explicit assertion. Contiguous stream sequences and strict capture ordinal (or supported common-UTC time ordering) are enforced. Journal default 4,096, configured ceiling 100,000 records. |
| `src/replay/replay.cpp:145–148,150–220` | `run` commits an accepted prefix, not an atomic whole batch. Explicit reset/recovery require coherent stream boundaries. Sequence/order faults block continuity; many ordinary book/validation errors return without setting the replay recovery flag. The adapter must stop/mark invalid on those too. |
| `src/book/order_book.cpp:302–311`; `include/gig/replay/replay.hpp:36–38` | Aggregated depth export has sorted prices, quantities, order counts and truncation flags; replay snapshot identifies run/journal prefix. Suitable comparator output, not proof that missing history was recovered. |
| `schemas/gig.event-v1.schema.json`, `schemas/instrument_rules-v1.schema.json`, `schemas/replay_config-v1.schema.json`, `schemas/gig.run_manifest-v1.schema.json` | Existing wire types encode integers as decimal strings and explicit missing metadata. Keep their meanings; local normalization IDs do not become exchange IDs because a schema accepts them. |
| `python/gig_microstructure/__init__.py:300–358,360–384,435–475` | Export consistency checks require retained input references and matching known digests. Documents have a 32 MiB limit and export/verification a 128 MiB aggregate bound. This is not a streaming full-day raw-data archive API. |

Tests checked include `tests/test_book.cpp:54–64,90–100` (identified non-head
execution, print nonmutation, missing orders, aggregate-recovery rejection) and
`tests/test_replay.cpp:25–28,38–72,86–101` (initial snapshot, gaps, ordering, boundaries,
aggregate-recovery rejection). A non-head execution is permitted: this book preserves
FIFO order but does not independently establish that the exchange must execute only
the head. NASDAQ-specific allocation behavior and hidden/reserve priority are not
validated by that test.

### Local checks actually run in P1A

`ctest --test-dir build/phase9-clean-release --output-on-failure --no-tests=error
--output-junit /tmp/gig-p1a-evidence/release-tests.xml` returned:

```text
65/65 Test #65: benchmark.book_smoke ............... Passed
100% tests passed, 0 tests failed out of 65
Total Test time (real) = 3.23 sec
```

JUnit: 65 tests, 0 failures/errors/skips/disabled. JUnit SHA256:
`067aae8650e30cf4d78824c50f0e94cbdb3b5536a262ce7fde6ebded652ffea5`.
Test-log SHA256:
`1f7a25f3591f11c13a996c747587c46766c78e5076b8cfbecf23b3409c55279a`.
This re-executed the existing Release binaries whose source is unchanged since the
remediation. It is not a new compiler/sanitizer/package matrix or real-market test.
Prior remediation results remain in [the unchanged evidence](baselines/remediation-validation.json).
Hosted CI, native ARM64 and real-market validation were not established in P1A.

## B. Licensing, provenance and redistribution

**Permission status for both sources: unresolved.** No current official terms,
click-through agreement, entitlement or redistribution clause was accessible.
Neither “sample,” a public URL, an exchange specification, nor the user's research
intent establishes an open-data license. The format document is not a market-data
license. No particular commercial/noncommercial grant, attribution requirement,
retention period, fee or redistribution exception is asserted here.

Before download, record separately for LOBSTER and NASDAQ:

1. Official sample/data landing URL, resolved archive URL, retrieval time and access
   prerequisites; whether the selected artifact is explicitly offered for evaluation.
2. Applicable terms/license URL, document version/date and cryptographic hash where
   lawful to retain, plus the relevant clauses permitting the intended private use.
3. Restrictions on raw redistribution, derived data, displayed quotes, screenshots,
   public reports, model outputs, storage location, user counts and retention.
4. Any required NASDAQ agreement or vendor entitlement and whether sample permission
   differs from purchased historical access. Do not subscribe or accept paid terms
   under this authorization.
5. A scope decision: only the permitted private local evaluation proceeds. Resolve
   unclear permissions before downloading; seek rights clarification when necessary.

Keep raw archives, extracted CSV/binary files and row-bearing mismatch evidence in
an external private data root (for example `/tmp/gig-market-data/<artifact-hash>/` for
an ephemeral run, or a separately authorized persistent directory). Never store them
under this Git checkout, even in an ignored `build/` directory. Do not commit raw or
normalized market rows, excerpts, screenshots or redistributable package fixtures.
Use synthetic tests in Git. Even data-derived public summary reports require a rights
check; hashes/metadata are provenance, not a substitute for permission. Existing
complete research exports copy input bytes: do not feed licensed inputs to an export
that will be published or committed. A private external archive/manifest strategy
must be designed separately within the existing export contracts.

LOBSTER data, if verified, are a vendor reconstruction/selection of exchange data,
not a new independent exchange capture. A comparison to its order-book output tests
agreement with that vendor's reconstruction. It does not independently validate the
underlying exchange feed or vendor transformations. NASDAQ archive provenance must
identify venue/feed/date/file generation and whether the archive includes transport
headers/sequences; do not call an unsequenced historical file a packet capture.

## C. Sample selection and inventory

Downloaded market-data archives: **none**. Message/reference files inspected: **none**.
Symbol/date/row counts/depth/size/timestamp range/event histogram/data hashes:
**not measured**. Neither the ZIP CRC nor a URL is a SHA256 identity or origin proof.

Preferred first artifact: one smallest practical **official LOBSTER sample pair**
with a message CSV and corresponding reference-book CSV for one NASDAQ instrument,
one trading date and a declared time interval. Prefer a small depth (e.g. 1–10 levels)
for streaming inspection, while retaining enough surrounding history to establish
state. The exact archive is deliberately not invented: index access is required to
select and cite it. Smaller depth is a comparison choice, not evidence of a complete
L3 initial state. If no officially offered sample supports a valid initial state,
finish a parser/inventory feasibility test and report that L3 validation is blocked;
do not replace the official sample with an unverified repository copy.

The future external inventory must include:

| Area | Required fields |
|---|---|
| Acquisition | Original/resolved URL, retrieval UTC, HTTP result, access/terms evidence ID, declared publisher, content type, response size; publisher checksum/signature if available |
| Exact identities | SHA256 and byte count of archive and each decompressed member, member names, extraction policy, decompressor/version; never rewrite the original bytes |
| Sample scope | Symbol and venue, date, filename interval versus actual interval, timezone convention, requested/available depth, exchange/vendor format version, completeness declaration |
| Message inspection | Physical/data/blank/malformed line counts, columns, row count, raw decimal time precision histogram, min/max time, ties/regressions, event-code histogram, ID lifetime/reuse findings |
| Reference inspection | Rows, columns and depth, paired-row alignment semantics, missing-level sentinels, sortedness, duplicate prices, zero/negative sizes, crossed/locked rows |
| State/continuity | Earliest complete state evidence, unobserved prior orders, source sequences if present, filtered events, breaks, halts, auctions, unsupported codes, file truncation/EOF checks |
| Software | Source commit, compiler/build identity, configuration/rule hash, parser/spec revision, normalized artifact hash, exact comparison policy, run ID and external evidence paths |

A local SHA proves byte identity between runs, not authenticity or completeness.
Download only after permission resolution; enforce a bounded compressed/uncompressed
size, member count and line length, and safe extraction (no absolute/traversal paths,
symlinks or external executables). Inspect archive metadata before extraction. These
are adapter requirements, not newly added infrastructure.

## D. Source format hypotheses and event compatibility

Classification definitions used below:

- **Exactly representable (E):** the stated displayed-book mutation fits the current
  payload after validated unit conversion and with a valid prior state. This does
  not mean every raw exchange field is natively modeled; preserve those externally.
- **Representable with documented assumptions (A):** a useful projection fits, but
  omitted attributes, side interpretation or context must be explicit and retained.
- **Unsupported (U):** deliberately excluded from the minimal reconstruction scope;
  preserve/count externally, never silently turn it into another event.
- **Requires additional engine capability (C):** faithful requested semantics cannot
  be achieved by current payload/recovery behavior. This is a design dependency,
  not authorization to extend the engine.

All source-side meanings in this section need official verification. Conditional E
is a statement about inspected engine capability; it is not an empirical claim that
a row in an unavailable sample met those conditions. Any unrecognized future type
uses the unknown-code policy, not the nearest familiar event.

### LOBSTER provisional structures

Conventional message CSV: six fields
`Time, EventType, OrderID, Size, Price, Direction`, with decimal seconds since local
midnight, shares, integer prices in units of USD 1/10,000, and direction conventionally
`+1` for buy and `-1` for sell. Do not assume a header, date, sequence number, exchange
match number, receive time or participant identity is present. Verify actual column
count and meanings; reject an unrecognized variant instead of discarding columns.

Conventional reference CSV: for each level, groups
`ask_price, ask_size, bid_price, bid_size`, giving `4 * depth` columns and one state
associated with each message row. The working expectation is **state after that
message**; verify this explicitly with official documentation and actual adjacent
rows. Do not choose a row shift by maximizing matches. Missing-level dummy prices
and sizes must be decoded only after confirming official sentinel rules. A dummy
price is not an extreme valid order. An aggregated size says nothing about order
count, identities or intra-level priority.

| Conventional source event | Classification | Engine projection and required handling |
|---|---|---|
| 1 — submission of a displayed limit order | E, conditional on complete state | `AddOrder(id, side, price, quantity)`. Validate positive ID/size, scale, live-ID uniqueness, and source domain. A duplicate is an error, not an implicit replace. |
| 2 — partial cancellation | E for mutation | `CancelOrder(id, QuantityLots(size))`. Require the known remaining quantity; compare redundant source price/side to the resting order before applying because CancelOrder does not carry them. Underflow or unknown ID invalidates the segment. |
| 3 — deletion of an order | E for mutation | `CancelOrder(id, CancelAll)`. If Size denotes the full remainder under the confirmed format, require exact equality before deleting; do not hide a size mismatch by using CancelAll. Verify price/side as above. |
| 4 — execution of a visible order | E for mutation | `Trade{BookExecution(id, resting_side, resting_price, size)}` only after checking ID, side, remaining and price. Direction describes the resting side if confirmed; it is not automatically aggressor side. Preserve any source trade attributes externally. |
| 5 — hidden execution | A for print; C for hidden order/queue reconstruction | `Trade{TradePrint(price, size, aggressor=missing)}` is nonmutating. A source field named OrderID need not refer to a displayed live order. No invented hidden AddOrder/BookExecution. Infer opposite aggressor only if official semantics explicitly justify it, with lineage; initial scope leaves it missing. |
| 6 — cross trade / auction print | A for print; C for auction semantics | Preserve cross classification externally; optionally expose a print-only projection with missing aggressor. Do not decrement arbitrary visible orders, create two executions, or run the synthetic matcher. Auction-clearing mechanics and special-price/size cases are not modeled. |
| 7 — trading-halt indicator / state transitions | A for a reduced session observation; C for full quote-only/trading state machine | Decode only verified special field values into `SessionEvent(halt/resume, reason)` where meaningful. Not a priced order or trade. Quotation resumption and trading resumption are distinct; retain raw substate externally and gate the harness. Never clear the book on halt/resume without source evidence. |
| Unknown, extension, correction or malformed event | U by default; C if later required | Record raw code/offset/error and stop the eligible segment if it may affect state. The native UnsupportedEvent is an explicit rejection, not a skip/sequence-advance mechanism. No successful completion with an unclassified event. |
| Reference-book row, regardless of depth | A as independent aggregate reference; C as L3 initialization/recovery | Parse directly in the external comparator. Do not manufacture SnapshotOrder IDs/FIFO from quantities. Existing aggregate Snapshot validation does not imply recover support. |

Determine whether the selected message stream contains all displayed order lifecycle
updates or only updates selected by requested depth/time/vendor processing. A depth
limit on the reference file does not prove the message file is complete or incomplete:
inspect the actual contract. An order newly entering visible top-L after deeper
liquidity is removed can require earlier state absent from a filtered sample. Even
perfect top-L matches do not establish full-book or hidden-liquidity correctness.

### Historical TotalView-ITCH 5.0 provisional structure

Conventional ITCH is typed binary messages with network-byte-order integer fields,
ASCII enum/symbol fields, a stock-locate/tracking header and a 6-byte nanosecond count
since midnight. Common price fields use four implied decimals, shares are integer
units and order-reference numbers are 64-bit. These are working expectations, not
verified byte offsets for the unavailable archive. Historical framing/compression
must be established separately: a length-prefixed file is not automatically
MoldUDP64/SoupBinTCP, and an ITCH tracking number is not a contiguous transport
sequence. The supplied `ITCHFTP.pdf` must first be read to establish what it covers;
obtain the official date-appropriate wire specification if that PDF is only access
instructions. Pin exact per-type lengths/field offsets before parsing. Do not infer
message boundaries by searching for ASCII type letters.

The following conventional message families form the initial checklist; compare it
to the retrieved dated specification, including any additions, before calling it
complete:

| Message family / conventional type | Classification | Existing-engine fit and limitation |
|---|---|---|
| Add order `A` | E for displayed mutation | AddOrder with exact reference number, side, shares and price. Resolve stock locate through the verified directory/context. |
| Add with MPID attribution `F` | A | Same displayed mutation; participant attribution has no native field. Preserve it externally; do not claim participant-level queue analysis. |
| Order executed `E` | E for decrement; A for complete record | BookExecution uses side/price from the known resting order; execution shares exact. Match number/tracking attributes need external retention. No execution of unknown orders. |
| Order executed with price `C` | C for full semantics; A only for a declared displayed-book projection | Execution price can differ from resting price; the book requires resting-price equality. A BookExecution at the resting price captures the decrement but cannot represent the actual execution price/printable flag. Preserve both externally and exclude this projection from trade-price/TCA validation. Do not substitute execution price into BookExecution. A later compound execution/print design needs an atomicity and double-counting contract. |
| Order cancel `X` | E for mutation | Partial CancelOrder after resolving and checking known state. Source's cancelled shares are a reduction, not new remainder. |
| Order delete `D` | E for mutation | CancelAll on an existing reference. No synthetic quantity when remaining is unknown. |
| Order replace `U` | A | ReplaceOrder(old,new,old side,new price,new remaining shares,lose priority), once official priority semantics are confirmed. Use the native atomic replacement; not a separate cancel/add. Side and stock context inherited only from verified live state. Preserve reference history. |
| Non-cross trade `P` | A for print | TradePrint only, subject to official displayed/non-displayed semantics. Source buy/sell indicator is not automatically the aggressor; leave unknown if not justified. Retain match number and other flags externally. Do not decrement visible orders twice. |
| Cross trade `Q` | A for print; C for full auction/cross model | Print projection only for valid ordinary price/size; preserve cross type/match identity externally. No auction allocation or inferred visible-order effects. |
| Broken trade `B` | C | No trade-break/match-ID correction contract or retrospective analytics undo. Do not reverse a book execution or restore liquidity without a verified exchange rule. Stop/flag trade-dependent analysis; assess displayed-state validity separately from trade-ledger validity. |
| System event `S` | A for selected lifecycle observations | Map only verified start/end meanings to appropriate SessionEvent; retain all codes. System/session scope is not an instrument field. Any fan-out to a target instrument is an explicit normalization context, not a source instrument assertion. Opening a session is not proof of an empty book at 09:30. |
| Stock directory `R` | A as adapter configuration | Build date-scoped locate-to-symbol/instrument/rules registry externally; do not miscast directory attributes as AddOrder or Quote. Retain all attributes and unknown rule fields. |
| Stock trading action `H`; operational halt `h` | A for reduced halt/resume observation; C for complete status semantics | Verify reason/status meanings; session observation alone does not enforce quote-only states or trading eligibility. Retain separate status dimensions. |
| Reg SHO restriction `Y` | U for initial book scope | External status record; no short-sale-rule simulator is proposed. Not a cancel/reset. |
| Market participant position `L` | U for initial scope | External attribute/status. No participant model in the current book. |
| Market-wide circuit-breaker levels `V`; status `W` | U as thresholds; A for a verified reduced status projection | Preserve threshold/status dimensions; do not turn thresholds into prices/orders. Do not treat a market-wide status as a per-symbol book reset. |
| IPO quoting period update `K` | U for initial continuous-book scope; C for full IPO workflow | Retain auction/IPO timing and qualification fields; not an initial L3 snapshot. |
| LULD auction collar `J` | U for initial scope | Retain collar metadata, not displayed depth or an executable quote. |
| Net order imbalance indicator `I` | U for initial scope; C for auction analysis | Imbalance/paired shares are not resting orders. No fake additions to make depth agree. |
| Retail price improvement indicator `N` | U for initial scope | Not a displayed order or top-of-book quantity; retain externally. |
| Direct-listing/capital-raise discovery `O`, if present in the selected revision | U for initial scope; C for its auction semantics | Verify actual existence/layout for that date. Never assume every ITCH5 file shares an identical extension inventory. |
| Unknown type, reserved value, bad length, truncation | U | Preserve offset/type/length, reject malformed framing, and fail closed if state relevance cannot be proved absent. Unknown is not a harmless observation by default. |

These classifications concern a single venue's displayed reconstruction. NASDAQ
TotalView is not an NBBO or consolidated multi-venue feed. Full raw-record fidelity
requires a lossless external record layer even for types marked E. The current engine
alone cannot encode every ITCH header/attribute or reconstruct hidden reserve queues.

## E. State, ordering and numerical decisions

### Initial state and depth

There are only two valid entry routes for the current engine:

1. A source-supported empty displayed book **before all relevant orders**, followed
   by a complete update history. A file beginning at regular trading hours, the
   first observed add, or a system/open message alone does not establish that fact.
   Pre-market and overnight/session rules must be checked for the particular archive.
2. A complete order-level snapshot with real order IDs, remaining sizes, FIFO ranks,
   source coverage and exact sequence boundaries. Current recovery additionally
   limits this to 64 orders; a larger valid snapshot needs separately authorized
   engine work. Splitting a full snapshot into several “complete” recoveries loses
   previous chunks and is invalid.

An aggregated LOBSTER opening row supports neither route by itself, even at full
price depth: many order/queue histories yield the same levels. A bounded-depth row
has additional unknown liquidity outside its boundary. Use `requires_snapshot` until
valid evidence exists; do not use `declared_empty` as an adapter convenience. Do not
seed one fake order per price, assign synthetic IDs, infer age from row order,
backfill unknown orders from later cancels, or treat a later match as proof that the
initial state was correct. Future data must not influence an as-of state.

If the sample lacks full initial state, report **initial state unavailable**, parse
and inspect it without claiming an eligible engine replay, and identify the missing
source artifact. A partial diagnostic model could be a later separate experiment,
clearly incomplete and without engine healthy-depth claims. Do not weaken recovery
contracts merely to obtain a green comparison.

A valid complete engine book may be compared to a bounded reference at the reference's
available depths only. Extra engine levels beyond that depth are neither mismatches
nor validated. Missing deeper levels are unknown, not zero. Aggregate prices/sizes
cannot verify order count, exact FIFO, hidden inventory or match allocation. IDs and
FIFO need complete lifecycle evidence plus an independent order-level oracle.

### Identity and lifecycle

Use a date/session/feed identity namespace. Preserve a valid nonzero exchange order
reference directly in OrderId when the official scope allows; never hash/truncate to
fit. The book indexes live IDs and rejects duplicate live IDs, but it does not enforce
a never-reuse historical rule. Maintain an external lifetime ledger to distinguish
legitimate post-deletion reuse from duplicate messages, stale cancels and session
mixups. Verify NASDAQ's actual reference uniqueness/reuse guarantees and LOBSTER's
transformation rules before choosing a policy. Treat zero/sentinel IDs on prints or
control rows as non-order values, not generated positive orders.

InstrumentId/VenueId/StreamId are local positive registry keys, with explicit mapping
to publisher venue, symbol, locate, date and feed. They are not exchange-issued numbers
unless sourced as such. Persist/hash the mapping. Locate codes and order references
must not be reused across files/days without the appropriate scope. Do not equate
NASDAQ feed attribution with all trading in the listed symbol.

### Sequence, timestamps and gaps

Preserve **original file/record order**. Do not sort by timestamp; equal timestamps
are normal and time regressions must be counted/investigated without reordering.
Use capture-ordinal ordering for the initial single-source adapter. This engine's
common-UTC timestamp ordering is not appropriate for unspecified venue-local time.

LOBSTER normally has no exchange sequence in the conventional six fields. Label a
row ordinal and a contiguous normalized replay sequence as **derived local ordering**,
not a fabricated exchange sequence. Keep exchange sequence unavailable in the
external source envelope; the native required SequenceNumber belongs to a named
normalized stream (`SequenceUnit::event` for one accepted event per row). Hash/persist
the source-to-normalized position map. Physical line number, CSV data row number and
normalized event ordinal are separate fields. Byte offsets aid reproduction; they
are not timestamp or exchange-sequence evidence.

For ITCH, distinguish any transport/session sequence actually retained by the
historical archive from local decoded-message ordinal and the ITCH tracking number.
Stock filtering produces expected gaps in global positions, not necessarily feed
loss. Validate global continuity before filtering when possible. If no transport
sequence exists, contiguous local rows prove only local processing continuity; a
hash cannot prove no upstream exchange messages were missing.

Do not pass all raw positions as native contiguous sequence numbers after skipping
records. Either retain an explicitly derived normalized stream with a complete
classification map, or design a future source-consumption contract. Skip only
proved non-book observations in the declared book-only projection, count/retain them,
and do not claim complete trade/status semantics. An unsupported book-affecting or
unknown record stops the eligible segment; continuing with renumbered events would
hide a hole. UnsupportedEvent cannot advance the native cursor successfully.

If later one source record produces multiple events, declare message-unit subevents
and the count before delivery, retain a shared parent ID, and compare only after all
subevents. Current ReplayEngine.run is prefix-committing, so a logical compound
record is not automatically atomic. The minimal adapter should avoid compound
mutations; faithful execution-price/correction support requires a separately reviewed
atomic contract. Do not patch partial failures by pretending the remaining subevents
were received.

Parse decimal time as integer/rational text, never floating point. Convert exactly to
nanoseconds only when divisible at the supplied precision; reject sub-nanosecond
values rather than round. Preserve the original decimal text externally. Resolve
LOBSTER local-date/timezone and NASDAQ midnight convention from official documentation
and date-specific DST rules. A nanosecond encoding is precision, not proof of clock
accuracy, synchronization, capture latency or causal ordering across feeds.

Native EventTimestamp can preserve a venue-local nanosecond count with
`venue_utc_unsynchronized` and an honest clock identity (e.g. a documented local-day
clock); do not label it UTC epoch time. If exact UTC conversion is justified, record
the date, timezone database/rules and transformation. If clock/precision cannot be
established, leave event_time missing rather than invent it; preserve raw time for
inspection. Missing receive timestamps stay unavailable, not copies of event time
and not the current download time. Do not estimate feed latency from such data.

### Price, share and control-field conversion

If official confirmation establishes price units of USD 1/10,000, use
`tick_size={1,10000}` for a **source price quantum**, or require exact divisibility
before conversion to a separately justified trading tick. Do not equate encoding
quantum with an exchange rule that every symbol/date has a one-cent tick. Preserve
raw integer prices and reject overflow, sentinels and invalid session prices.
A value of 1,234,567 source units would be exactly USD 123.4567; this is an arithmetic
illustration, not an observed sample row. The rules must not silently discard
sub-cent prices.

Use one share per QuantityLots (`lot_size={1,1}`) for conventional equity shares;
“lots” is the engine type name, not a claim of 100-share round lots. Verify source
share units and any fractional-unit exception. Reject zero mutation sizes, negative
sizes, inexact conversions and quantities above declared limits. The numeric type
permits zero, but event validation rejects it for ordinary priced quantities.
Control rows can have zero/special values: interpret only after classifying type,
never force them through AddOrder/Trade validation.

Independently test conversion boundaries with arbitrary-precision integer/Fraction
arithmetic, including UINT64_MAX, INT64 limits, maximum daily time, maximum date
conversion, off-tick values and overflow. Range limits must be sourced or explicitly
named local safety limits, never inferred from a familiar sample maximum and claimed
as exchange limits.

### Sessions, corrections and state validity

A halt does not necessarily cancel resting orders. SessionEvent does not implement
an eligibility state machine or clear the book. Preserve quoting/trading/resumption
substates externally; a post-halt update is not silently discarded. A session reset
needs actual boundary evidence and an explicit new epoch/restart plan. A timeout,
failed parse, mismatch or file boundary is not exchange evidence of an empty book.

The book permits locked prices and rejects crossed prices. Observe/count any crossed
source state; distinguish genuine phase/auction semantics from bad parsing or missing
history. Do not clamp, reorder, match orders away or use the synthetic simulator to
resolve a crossed reference. If legitimate source behavior requires a crossed
intermediate state, current core policy is a capability blocker for that segment.

Broken/corrected trades and printable flags require distinct displayed-book and
trade-ledger validity. Do not assume a broken print restores displayed liquidity.
Auction/cross observations likewise do not authorize arbitrary book clearing.
Maintain per-domain validity (displayed state, trade tape, session status, analytics)
and reasons; do not produce a complete TCA or causal-analytics claim from a book-only
projection with unsupported trade semantics. No execution simulation is calibrated
or validated by depth agreement alone.

## F. Proposed minimal adapter architecture — design only

A small, single-threaded offline program should compose the existing library, not
embed a new matcher, dashboard, database, broker connector or distributed pipeline.
Suggested logical components (names describe future work, not added files/APIs):

1. **External acquisition manifest and immutable input.** Validate permission and
   paths first. Hash original archive/member bytes, pin format/spec/terms references,
   and retain all source data outside Git. Separate data from the manifest distributed
   with code. Date/symbol/venue mapping and exact units are reviewed configuration.
2. **Bounded streaming decoder.** Source-specific CSV decoder first, ITCH binary
   decoder later. Produce a lossless source envelope containing code, original
   attributes, row/byte position, raw time, source identities and availability flags.
   No book mutation, reference lookup or floating-point conversion here. Validate
   framing, column counts, ranges and EOF. No adapter implementation is authorized now.
3. **Classifier/normalizer.** Apply the matrices and explicit scope policy, exact
   numeric rules and honest metadata. Produce at most one current core event per
   accepted mutation in the first version. Retain all raw attributes and disposition
   externally; classifying a print must not invent order state or an aggressor.
4. **State prerequisite and application boundary.** Require proven initial state,
   verify referenced orders through book.find, validate redundant source fields,
   then apply. Stage any adapter registry/lifecycle changes and commit them only
   after native success. On any failure keep the last committed prefix, stop eligible
   comparison, preserve error/input positions and mark invalid. Native needs_recovery
   alone is insufficient because a missing-order book error need not set it.
5. **Existing ReplayEngine/OrderBook.** Keep deterministic single-threaded semantics,
   existing atomic mutations, explicit initial state and configured limits. Do not
   increase limits or change event schemas as an incidental adapter patch. Stop
   cleanly at budget, journal cap or unsupported capability.
6. **Independent comparator and audit sink.** Consume source reference rows directly,
   compare eligible snapshots only, and write counters/hashes/failure evidence outside
   Git. It must not feed reference prices, sizes or missing orders into normalization
   or engine state. Publication of any data-bearing artifact needs a separate rights
   check. Synthetic comparator fixtures may later be committed under authorization.

For LOBSTER provenance, use observed origin/public_dataset source, an observed source
lineage step followed by versioned normalization, missing generator seed and parents
referencing exact source artifacts. For official raw ITCH use observed/exchange when
verified. Registry mappings and inferred side/context are derived metadata, not new
exchange observations. If a separate synthetic diagnostic is used, keep it a distinct
run/artifact; never relabel observed data as synthetic to obtain a seed, or insert
synthetic orders into an observed run.

The native dataset identity/digest must refer to the **same exact-byte artifact** as
the retained manifest input. For example, a decompressed message CSV's digest cannot
be replaced with the enclosing ZIP digest. Give archive, message CSV, reference CSV,
normalization configuration and optional parent manifests distinct identities and
hashes; preserve their relationships externally. The vendor's unavailable version
must remain unavailable in the raw envelope. If replay requires a known version,
use an explicitly identified local immutable normalized-dataset revision, not an
invented vendor version. Record the verified license evidence reference; an arbitrary
nonempty token does not establish permission even if the validator accepts it.

Respect 128-character identity limits, eight native lineage/parent slots and eight
stream slots. Use a small stable artifact ID and external manifest instead of
truncating paths or silently dropping parents. Preserve exact digests and external
lookups. The reference snapshot artifact is a validation parent, not a replay input
that can influence the reconstructed state. Any timestamp conversion or reference
alignment decision must be frozen before scoring.

## G. Independent validation methodology and reporting contract

### Separate what is being validated

Use three layers, each with its own status:

1. **Decoder/normalizer validity:** all raw records classified, exact conversions,
   correct field semantics, no invented state, deterministic source-to-event map.
2. **Displayed-book reconstruction validity:** complete initial state and lifecycle,
   successful accepted mutations, invariants and independent order-lifecycle checks.
3. **Reference agreement:** exact level prices and quantities at the source's
   stated depth after the correctly aligned source record. This does not validate
   hidden book, FIFO, execution quality, profitability or causal inference.

LOBSTER's reference states provide an independent comparison input to this engine,
but originate from the same vendor transformation as its messages. Add a separate
simple oracle for lifecycle/aggregation implemented without the engine's maps,
canonical serialization, normalizer or numeric conversion helper; use Python integer
and Fraction calculations. Manually check selected synthetic add/reduce/delete/
execute/replace examples against the official field definitions. Differential
agreement alone does not prove both decoders avoided the same misunderstanding.

### Comparison procedure

1. Freeze selected artifacts/hashes, row alignment, units, state evidence, relevant
   session/depth interval, supported-event policy and comparison rules before results.
   A train/test split is unnecessary for deterministic reconstruction; any later
   calibration or model selection needs chronological held-out data and causal design.
2. Stream message/reference files in verified alignment, preserving all physical and
   data row numbers. Detect unequal row counts, unexpected headers, blank rows,
   malformed values, compression truncation and trailing data. A malformed row is
   not removed and followed by a row-number shift.
3. Decode the reference using an independently reviewed parser, validate ordered
   distinct levels and sentinel semantics, and use arbitrary-precision totals.
   Do not regenerate the expected snapshot with the engine under test.
4. After the entire source record's successful normalized effect, call replay.depth(L)
   only if continuity/initial state and phase coverage are valid. Compare each
   available side/rank's price and aggregated quantity **exactly**, without float
   epsilon, rounding or approximate matching. Test presence/absence separately.
   Do not compare engine order_count to a field that the source does not provide.
5. For a hidden/cross print projection, assert no displayed quantity changes and
   compare its unchanged reference row where available. For session controls, apply
   the declared nonmutating status policy and compare only when the reference row
   represents a comparable book. Count outside-scope rows with reasons; do not let
   their removal make coverage appear complete.
6. Record row-wide equality (all comparable cells) and per-side/rank/field equality.
   Beyond-reference-depth levels are excluded. A sentinel-confirmed absent level is
   a testable absence; an unknown/missing reference field is not. Compare the common
   declared scope without pretending absent deep history is validated.
7. On first mismatch, record original artifact hashes, source row/byte offset, native
   event index/subevent, local/source ordering identities, exact expected/actual
   fields, status/depth policy, engine error/invariants and last valid prefix. Freeze
   an external reproduction manifest and state fingerprint. Include prior records
   back to a valid initial state: a tiny suffix without state is not a reproduction.
   Data-bearing evidence stays external and rights-restricted. Hash the reproduction
   and include a command template, code/config/toolchain identity and exit status.
8. Strict acceptance stops at a state-affecting failure. An optional diagnostic pass
   may collect later discrepancies but must mark them tainted and exclude them from
   valid coverage. Never reset from each reference row, delete mismatches, search for
   favorable alignment, or silently restart an empty book to improve a match rate.

A content hash over the normalized event sequence and canonical states checks
repeatability. Repeat the fixed eligible run with GCC and Clang (Debug/Release and
sanitizers for correctness); compare all non-timing counters and canonical identities.
Hash only stable semantic outputs; runtime wall time, platform paths and compiler
banners belong to separate run metadata. No optimization or market-data latency
requirement is inferred from the earlier synthetic benchmark.

### Required counters and conservation identities

Maintain disjoint **source-record terminal dispositions**, independent of the number
of emitted native events:

```text
N_total = N_accepted + N_rejected + N_unsupported + N_deferred
```

- `total_source_records`: decoded record candidates in the declared full input;
  physical lines/blank lines, framing faults and unread/unprocessed tail counts are
  separate. If early failure prevents a full count, total is explicitly unknown or
  comes from a prior independent inventory pass. Never call processed prefix total.
- `accepted_records`: classified supported records whose declared projection is
  fully handled, including explicitly supported nonmutating observations; separately
  count core-applied events and supported external-only observations. A disposition
  does not imply a complete raw-wire semantic model.
- `rejected_records`: malformed fields/framing, invalid IDs/ranges, state conflicts,
  native errors and resource errors; partition reasons and first locations. A record
  is counted once at source level even if several validation predicates fail.
- `unsupported_records`: recognized but deliberately unimplemented semantics or
  unknown types; include raw code and book/trade/status relevance. Known harmless
  external-only records must be distinguished from state-affecting unsupported ones.
- `deferred_records`: syntactically valid but unavailable/ambiguous initial state,
  unresolved semantics, missing prior order, or not processed after a stop. Assign
  one primary disposition and retain overlapping reason flags. If missing-order is
  classified as a state rejection instead, freeze that policy before scoring.

Do not classify one source row as both unsupported and rejected to balance totals.
If the unread tail is not classified, state that the equation covers only the
inventoried portion and report unprocessed count separately; do not assert a complete
run. Report per-type counts, emitted normalized events, applied mutations, external
observations, first/last processed positions and stop_reason. One accepted source
record can emit zero/one/multiple events in future versions; those totals are not
the same denominator.

For snapshot comparison, define and publish:

```text
N_reference_rows = N_eligible_rows + N_ineligible_rows
N_eligible_rows = N_compared_rows + N_comparison_failures
N_compared_rows = N_exact_rows + N_mismatch_rows
coverage = N_compared_rows / N_reference_rows
eligible_coverage = N_compared_rows / N_eligible_rows
```

Report zero denominators as **not applicable**, never 100%. Missing reference,
initial state unknown, ambiguous alignment, source phase exclusion, engine failure,
unsupported mutation, depth uncertainty and unprocessed tail all get explicit
coverage reasons. State-affecting records can taint many subsequent rows: report
both source-event exclusions and dependent snapshot exclusions. Count reference parse
failures explicitly, not as missing price/quantity zeros. Include exact/mismatching
cells and per-side/depth breakdown, first mismatch and reproduction identity, and
whether comparison is price-and-size, size-only, or unavailable. Do not average away
a single mismatch with many unchanged rows.

A future external machine-readable summary should contain source and spec/license
hashes, chosen scope, engine/config/adapter/oracle identities, inventory counts,
terminal dispositions, validity-domain flags, comparison denominators, first failure,
normalized/canonical hashes, resources and exit status. It is not implemented by this
report. `complete=true` must mean the **declared** input and comparison scope was
fully processed with no unresolved state-affecting error; “complete displayed-book
projection” is not “complete ITCH semantics.” Known exclusions remain in the summary.
A parser-only result must never be labeled successful market-book validation.

### Memory and throughput measurement design

Measure an unsanitized Release run only after correctness passes. Separate decoder,
normalizer, replay mutation, snapshot comparison and end-to-end wall/CPU timings.
Report source records/s, native events/s and comparable snapshots/s with their exact
counts, bytes/s and peak resource usage. Include decompression/read/parse/hash/output
costs in the end-to-end figure; name exclusions in component figures. Use monotonic
wall time, process CPU time, selected PMR live/peak/allocation counts and whole-process
RSS/high-water. PMR is not total process memory. Keep reference-oracle memory separate
or include it transparently. Use bounded record buffers rather than preloading all
MarketEvents. Record host/compiler/flags/affinity, repetition count, cold/warm-cache
policy and filesystem/output behavior. Repeat identical artifact hashes serially;
report variation, not a single fastest run. Service-time percentiles are not exchange
or network latency; there is no receive timestamp or arrival process to validate that.
Do not extrapolate synthetic timings to a real-data SLA.

## H. Resource feasibility and journal scaling

Actual size-probe output rerun against the unchanged remediation build:

```text
MarketEvent=12208 JournalEntry=15944 RestartPlan=3720 ReplayConfig=4824
```

Probe source is the existing noncommitted
`build/institutional-audit/sizes.cpp`; the remediation-built executable was rerun,
not an engine modification. Output SHA256:
`6174197e3359f3d553c2eff581a3c3db0030af052b4bcdd8aa820c569500f9ec`.
These are GCC x86_64 ABI sizes, not portable C++ guarantees or heap-inclusive counts.
JournalEntry embeds MarketEvent plus optional restart-plan storage; an empty optional
does not eliminate its inline space. Each successful replay record (including
observations/filtered instruments) is retained. Streaming the CSV alone does not
bound the native retained journal.

| Retained entries / capacity | Element-storage bytes at 15,944 bytes | MiB | Current feasibility |
|---|---:|---:|---|
| 4,096 | 65,306,624 | 62.28125 | Default maximum; excludes all other memory |
| 10,000 | 159,440,000 | 152.05383 | Configurable, subject to memory budget |
| 65,536 | 1,044,905,984 | 996.5 | Near 1 GiB just for allocated elements |
| 100,000 | 1,594,400,000 | 1,520.53833 | Current configured record ceiling |
| 1,000,000 | 15,944,000,000 | 15,205.38330 | Arithmetic extrapolation only; current ReplayEngine rejects this configured limit |

`reserve_record` doubles capacity up to the configured limit
(`src/replay/replay.cpp:109–115`). For the default growth from 2,048 to 4,096 entries,
old-plus-new element storage may coexist: 97,959,936 bytes (93.421875 MiB). With
max_journal_records=100,000, growth from 65,536 to 100,000 can temporarily require
2,639,305,984 bytes (about 2.458 GiB) before allocator overhead and other state.
Allocator retention can further affect RSS. Capacity can exceed live entry count;
report both. Full canonical export builds another large string and must be measured
separately, not assumed free or streamed.

Order-book memory additionally grows with live orders and levels (map/list/hash
nodes and buckets); input parsing, decompression, raw envelopes, reference buffers,
configuration and oracle have separate costs. Depth extraction allocates O(L) output
per comparison; crossing checks and native invariant checking also affect runtime.
Do not confuse simulation's full-state staging costs with ordinary replay's local
staged book mutation. Recovery constructs a replacement book, so old/new state can
coexist there as well. Hash indexes are average-case lookup, not a hard constant-time
latency guarantee. Exact whole-process memory and throughput for either real source
are **unmeasured**.

Select a first eligible run small enough to remain within the measured budget and
all caps. Declare that record interval **before** scoring and only truncate from a
valid initial state, not arbitrarily into midday. A reference file might be small
while the necessary state-building history is large. A warm-up replay contributes
journal entries too; it cannot be ignored in capacity planning. A full day or whole
market may exceed 100,000 records; no actual sample count is available here to decide.

Do not recreate a fresh replay per chunk with an empty book, bypass the journal by
calling OrderBook while claiming full ReplayEngine provenance, or discard history
silently. If a legitimate sample cannot fit, report resource-blocked feasibility and
request a distinct storage/recovery phase. Later benchmark-gated work may investigate
compact journal payload ownership and bounded durable archival/checkpoints, but must
preserve atomicity, deterministic lineage and recovery semantics. No such storage
optimization or infrastructure is implemented or authorized by P1A.

## I. Risks, blockers and limits

| Priority | Blocker/risk | Evidence and consequence | Resolution before a claim |
|---|---|---|---|
| P0 | Official access/usage rights unresolved | Both origin requests blocked; no terms read | Enable official access; record permitted private use and redistribution restrictions before acquisition |
| P0 | Missing initial L3 state | Aggregates cannot identify orders/FIFO; recovery enforces complete order snapshot | Prove true-empty plus full history, or obtain complete L3 state within native capacity; otherwise report no eligible reconstruction |
| P0 | Source message/depth selection unknown | No sample or official documentation inspected | Establish whether all state-affecting history is retained, including deeper orders and pre-market history |
| P0 | Journal cap/memory may exclude useful interval | 15,944-byte entries; max 100,000 | Inventory required records and measure budget; select a valid small run or separately authorize storage work |
| P1 | Execution-price/correction/auction mismatch | Current execution requires resting price; no match-ID break/undo model | Restrict and label book-only scope, or request explicit capability design before trade/TCA claims |
| P1 | Session/crossed-state semantics | Halts nonmutating; crossed adds rejected | Verify source phases and keep invalid/out-of-scope intervals explicit; do not repair market observations |
| P1 | No exchange loss detector in a row-ordered CSV | Derived ordinals enforce local processing only | Report continuity evidence level; never claim transport completeness without actual sequence evidence |
| P1 | Common-source reference / circular validation | Vendor messages and book share reconstruction ancestry | Independent oracle/parser; never seed/reconcile engine from scored rows; qualify agreement |
| P1 | Time/price/size interpretation and leakage | Source clocks/rules not fetched; initial-state backfilling uses future data | Exact conversions, date-scoped rules and frozen causal boundary; leave unavailable fields missing |
| P1 | Licensed raw inputs accidentally bundled by exports | Complete export retains input bytes | Keep all raw/normalized artifacts external, rights-restricted and outside Git; review derived-output permissions |
| P2 | Parser safety and malformed compression | New external input boundary not implemented | Bounded extraction/framing, overflow/adversarial tests and sanitizers in the authorized adapter phase |
| P2 | Overclaiming aggregate agreement | Top-L snapshots cannot prove FIFO/hidden behavior | Separate decoder, displayed-depth, order-level and trade-research claims |

No real-market adapter, empirical calibration, full NASDAQ matching/priority model,
corporate-action adjustment, consolidated feed, real-time gap recovery or operational
system is delivered. The terminal is untouched. NASDAQ-specific behavior is an
observable contract to verify, not knowledge of any trading firm's proprietary system.

## J. Dependency-aware plan and precise acceptance criteria

These are proposed future checkpoints. **P1A does not authorize their implementation.**

| Checkpoint | Dependencies | Deliverable / measurable exit gate |
|---|---|---|
| 1. Official source/rights re-verification | Official host access | Retrieve and identify the supplied pages/PDF and dated format/terms; record actual rights, exact URLs and hashes. No unresolved permission for selected private use. No data download until this gate. |
| 2. One LOBSTER sample inventory | Checkpoint 1 | Choose/cite one official small archive; retain it externally; hash archive/members; report all rows/types/precision/depth/IDs and paired reference structure. Counts unknown in P1A become measured, not guessed. |
| 3. State/coverage feasibility decision | Checkpoint 2 and official semantics | Identify an eligible interval with complete initial state and all state-affecting updates. Initial boundary and reference alignment documented before scoring. If impossible, deliver a blocked parser-only assessment; do not claim L3 validation. |
| 4. Minimal CSV decoder/normalizer | Explicit user authorization, checkpoints 1–3 | Lossless external source envelope, exact conversions, deterministic local registry/sequence map, synthetic tests for every classified type and failure. No full ITCH decoder or engine schema expansion folded into this step. |
| 5. Native replay and independent comparator | Checkpoint 4, memory/cap gate | Run the declared bounded interval; exact integer price/quantity comparison at available depths; complete accounting and first-error reproduction. No input-derived fabricated state or reference-to-engine feedback. |
| 6. Repeatability/resource report | Checkpoint 5 correctness passes | GCC/Clang semantic/canonical equality; required Debug/Release/sanitizer regressions; serial Release memory/throughput with raw counts and qualified timings. Publish only permitted non-data evidence. |
| 7. Raw ITCH feasibility/decoder | Official historical archive rights/spec/framing and successful earlier gate, or a documented separate initial-state route | Select one bounded date/instrument input with full framing/transport provenance; enumerate actual message revision/extensions. Reassess C execution, match IDs, corrections, session/auction and resource needs before implementation. |
| Separate capability/storage work | Evidence that checkpoints 3/5/7 are blocked; separate approval | Complete-L3 initialization beyond 64 orders, compound execution-price semantics, or compact/bounded archival journal, each with independent correctness and benchmark gates. Not a silent dependency shortcut. |

### Minimal adapter acceptance contract

A later implementation may be accepted only when all applicable gates have evidence:

1. **Rights and integrity:** official selected source and permitted-use evidence;
   no raw market data in Git; archive and member SHA256/bytes fixed and checked before
   and after runs. A fresh permitted retrieval or private immutable artifact can
   reproduce identity; no claim that a digest proves publisher authenticity.
2. **Source coverage:** 100% of inventoried source records have a terminal disposition
   and documented type semantics. Physical lines, source rows and normalized events
   reconcile separately. Unknown/unhandled state-affecting events are zero within an
   accepted reconstruction interval. All exclusions and unprocessed tail remain visible.
3. **Initial state:** complete source-supported boundary, no fabricated orders or
   priority, no inference from scored/future references, no arbitrary empty restart.
   Required snapshot fits current contracts or the run is explicitly blocked.
4. **Numerics and identity:** exact price/time/share conversions; zero silent
   roundings/overflows/truncations; registry/reuse and duplicate policies tested;
   original time text and unavailable exchange/receive metadata retained honestly.
5. **Failures:** malformed inputs, invalid sides/enums/IDs, missing orders, inconsistent
   source size/price/side, file truncation, unsupported types, gaps, capacity and
   allocation errors have structured external error positions and deterministic
   dispositions. No partially committed logical record reported accepted; book/cursor/
   adapter metadata stay at the last valid prefix, with continuity validity explicitly
   false when required. Existing strong guarantees remain intact.
6. **Reference comparison:** every eligible paired row in the declared interval is
   attempted; eligible_coverage=100%, comparison_failures=0 and exact price/quantity
   matches=100% for the supported available scope. Any mismatch fails that scope's
   acceptance and has a reproducible first counterexample. Overall full-file coverage
   is separately stated and need not be 100% if declared exclusions are justified;
   no mismatch-driven selection or hidden exclusion. Zero eligible rows cannot pass.
7. **Independent evidence:** reference parser/oracle does not call engine conversion
   or mutation helpers to compute expected values; negative synthetic cases detect
   intentional price, size, alignment and missing-history errors. Aggregate agreement
   is labeled aggregate agreement, not proof of FIFO/hidden-market correctness.
8. **Determinism and regressions:** same licensed artifact/config gives equal normalized
   event identities, semantic counters and canonical hashes under GCC and Clang.
   Existing replay/numeric/atomicity tests remain green; new adapter tests cover all
   actual source types, boundaries, ties, repeats, malformed/truncated input and
   adversarial resource paths in Debug/Release/ASan+UBSan. Optional Python paths, if
   changed, require their existing package/consumer gates. No ARM64/CI claim without
   actual runs.
9. **Resource disclosure:** report retained journal size/capacity, selected PMR and
   process memory, peak growth and canonical-export overhead; no limit exceedance
   within the declared local budget. Include exact source/event/snapshot denominators
   and end-to-end/component timing methodology. No invented latency target or speedup.
10. **Scope and provenance:** observed, inferred and synthetic facts remain distinct;
    raw headers/flags/match attributes stay externally recoverable; compiler/source/
    dataset/spec/license/config/reference hashes and first-failure artifacts are
    traceable. Do not mark trade/TCA/session semantics complete when only displayed
    depth was validated. No main merge, release, terminal integration or live connection.

### P1A disposition and stop

Completed: baseline/remote/clean-tree verification, source-level engine inspection,
actual official-access attempts and their limitations, no-data inventory, provisional
event compatibility matrices, state/depth analysis, independent validation design,
measured journal-size review, resource arithmetic, risks, dependencies and explicit
implementation gates. Existing Release tests passed 65/65. This report is the sole
committed file for P1A; its own commit SHA is reported in the completion response.

Blocked/unverified: current official dataset availability and usage terms, any actual
sample structure/content/hash, complete initial-state evidence and all empirical
real-market comparison/performance outcomes. Those are prerequisites, not waived
acceptance criteria. No dataset or full adapter was created in this phase.

**Stop here. Request explicit authorization for the next source-access/inventory
checkpoint and, only after its feasibility gates pass, the minimal real-data adapter.
Do not start implementing the adapter or storage roadmap from this design report.**
