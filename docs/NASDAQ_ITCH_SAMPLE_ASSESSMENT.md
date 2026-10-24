# Phase P1C — official NASDAQ ITCH sample assessment

Review date: October 21, 2026, America/New_York. Request timestamps below are UTC.
Repository: `parthivpatel-patel/GIG-C-Microstructure-Engine`.
Starting development commit: `2dbbd0878f2967cb7d89caf3d2833587f22c58d4`.
Branch: `feat/bootstrap-cpp20-engine`.

## Recommendation and evidence boundary

**CONDITIONAL GO to resume official directory/sample verification after environment
publication; NO-GO for sample acquisition, actual replay claims or adapter implementation
at this blocked checkpoint.** The user has supplied a new official-directory lead and
reports NASDAQ Data Client Success identified it as free sample data. This advances
beyond P1B's inability to locate a sample route. It does not establish that a particular
file is small, ITCH5, complete, or subject to unrestricted rights.

The exact supplied directory is
https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/ . Its HTTPS request failed at the configured
proxy before origin access. No directory listing, README, license, checksum file or
market archive was retrieved. No actual sample was selected, downloaded, decompressed
or parsed; no initial L3 state or defensible replay interval has been established.
This is a network-blocked assessment, not a completed empirical sample verification.

A concrete network-only draft now adds `emi.nasdaq.com` and preserves the existing
custom domains and preset. Save/read-back succeeded; the tool returned
`requires_publish: true`. User review/save/publication is required before claiming
activation. Do not bypass the proxy or repeatedly retry the unchanged blocked host.
No adapter, engine/storage change, main merge, paid resource or live connection was
performed. Existing audit, P1A/P1B and remediation documents are preserved unchanged.

## Repository and supported access verification

At entry, the working tree was clean. Local HEAD and exact remote development HEAD
both equaled the starting commit above. Main remained
`165c5038336887116d69160b0d8e5a1a5ef59d16`. No checkout/reset/rebase/history rewrite
was performed. This new assessment is the sole repository change in P1C.

Runtime status reported connected/current observations, restricted network-policy
state `unknown`, existing custom hosts `data.lobsterdata.com` and
`www.nasdaqtrader.com`, and no `emi.nasdaq.com` in effective hosts. The actual local
policy likewise lacked EMI and had VPN unconfigured. Unknown policy state does not
establish enforcement; the actual request establishes the observed denial.
LOBSTER was not retried.

### Actual access ledger

| Field | Observed value |
|---|---|
| URL | `https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/` |
| Recorded completion UTC | `2026-10-22T02:51:28.708778+00:00` (October21, 22:51:28 America/New_York) |
| curl exit | `56` |
| Error | `curl: (56) CONNECT tunnel failed, response 403` |
| Origin HTTP / downloaded body bytes | `000` / `0` |
| Directory response body | No file created |
| Interpretation | Proxy denial before origin access; not an EMI licensing refusal, missing-file response or proof of global unavailability |

The request used normal TLS verification, the inherited proxy, HTTPS-only redirects,
a25-second timeout and a3,000,000-byte cap. It requested the directory only, not a
market-data file or range. No alternate route, HTTP downgrade or mirror was attempted.

```sh
curl --proto '=https' --proto-redir '=https' --location \
  --max-time 25 --max-filesize 3000000 --silent --show-error \
  --dump-header /tmp/gig-p1c-evidence/directory.headers \
  --output /tmp/gig-p1c-evidence/directory.html \
  --write-out '%{http_code} %{size_download} %{url_effective}' \
  'https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/'
```

The mode0700 evidence directory is outside Git. Access-recorder JSON SHA256:
`b9b4fe7e3a691dce4bcdc68999d408f42e97c2101d390b6e6be8ecf9b54a0e25`.
Proxy-header SHA256:
`e67e0cd161a62a97f67b7d9d5c1f753a5c972eb2a44b1254f4708e2e3ec6e524`.
These identify local error evidence, not an official directory or sample. Temporary
files are not made available by this documentation commit.

### Saved supported configuration and required action

The configuration was read before updating: custom rules were exactly the two prior
hosts. A network-only update added EMI, preserving those rules and the selected
`package_managers` preset. Read-back confirmed draft revision4 and these three custom
hosts (order is immaterial):

```text
data.lobsterdata.com
emi.nasdaq.com
www.nasdaqtrader.com
```

Save response: `status: saved`, `requires_publish: true`. No installation/startup
scripts, repository membership, variables or secret requirements were changed.
No wildcard, unrestricted network or new VPN/TCP route was requested. Saving a draft
is not evidence that the current runtime can access EMI or a future restore succeeds.

**Required user action:** review/save the pending network draft in environment
settings and publish the environment. Then resume P1C, reverify development HEAD and
actual HTTPS access to the same official directory. Only retry after this meaningful
state change. This publication is environment configuration, not a GitHub release.

The runtime/configuration instructions read for this work explicitly required user
review: “Configuration changes require the environment configuration workflow and
its user review.” Independently, the supported tool returned `requires_publish: true`.
The blocker is applying this concrete saved change, not repeating P1C authorization.

## NASDAQ representative statement and licensing boundary

The user's P1C message reports NASDAQ Data Client Success supplied the exact directory
as an official free sample location and confirmed historical archives including
2019 ITCH5 files. Treat this as **user-supplied representative evidence**, not a new
independent directory observation. No original email, sender/date, verbatim terms or
attachment was provided in this session, so none is invented or authenticated here.
There is no need to repeat the earlier broad search as if no official lead existed.

“Free sample data” addresses sample availability/cost as reported; it does not by
itself establish every allowed use, retention period, cloud-storage condition or
raw/derived redistribution right. It is not treated as unrestricted/open licensing.
Before acquiring archive bytes, inspect any directory README/license/evaluation
notice and determine whether the reported permission covers this private evaluation.
If publicly stated terms resolve that use, proceed under them; do not invent an
additional mandatory agreement. If scope is unclear or terms conflict, obtain the
relevant representative wording/clarification before downloading. No account creation,
paid agreement, purchase, subscription or outreach is authorized/performed here.

The prior official website copyright wording and its limited personal/noncommercial
copying exception are documented in
[REAL_MARKET_DATA_ACCESS.md](REAL_MARKET_DATA_ACCESS.md). Do not assume those website
terms automatically govern or license all EMI archives. Applicability to EMI and
any sample-specific terms remain unresolved. Retention/deletion, permitted report
outputs, cloud storage and raw/derived redistribution conditions are not established.
No raw market data may be committed, packaged or redistributed. Keep any permitted
sample and row-bearing evidence in a private root outside the checkout.

## File inventory — reported leads versus verified measurements

| Item | Evidence available now | Size/date/format/checksum status |
|---|---|---|
| Official directory URL | Supplied by user as the NASDAQ representative's location; attempted directly | Listing unavailable in this runtime |
| 2019 ITCH5 historical archives | User reports their presence | Exact filenames, date intervals, compressed/uncompressed sizes, bytes and current availability not independently observed |
| `S010303-v2.zip` | Filename specifically mentioned by user | Not requested or inspected. Its name is a legacy-version clue, not proof of content; must not be labeled ITCH5 or selected solely because it is small |
| `tvagg.gz` | Filename specifically mentioned by user | Not requested or inspected. Content, granularity, wire schema and suitability are unknown; must not be assumed order-level ITCH5 |
| README/license and checksum files | Not observed | Existence, names, algorithm and coverage unknown; absence is not asserted |
| Acquired market archives / parsed messages | `0` / `0` | No sample SHA256, record histogram, timestamp range, session coverage or match rate measured |

No dates/sizes are inferred from a directory name or an illustrative access-guide
filename. The smallest **suitable** sample is not necessarily the smallest file.
When access works, inventory all actual candidate names, displayed lengths/date fields,
metadata provenance and checksum links before choosing; directory modification time
is not the trading date and Content-Length is not uncompressed size.

The three previously retrieved official specifications remain identified by SHA256
in P1B: access guide `77d0c9a5e86866951d99e58e5fda76b54ccf0316f19cbd7428492d459dee8177`,
ITCH5 specification `45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3`,
and BinaryFILE `a1f443400728b3ce44953e9ae263e4846fe6ad68420e7a635829872aefdfff60`.
They describe protocol expectations, not the format/integrity of either named small
file or a2019 archive. They were not redownloaded in this blocked phase.

## Bounded sample inspection design after access and rights gates

No parser or adapter is implemented by these proposed checks:

1. Retrieve only the listing and relevant small text/metadata/checksum documents
   first. Select a candidate with official evidence of ITCH5 order-level payloads
   and an acceptable total resource budget. Reject the “smallest extension wins” rule.
   If every suitable archive is multi-gigabyte, do not start a full download by default.
2. Establish permitted private evaluation and retention. Then record resolved URL,
   HTTP metadata, exact byte extent and an explicit acquisition cap outside Git.
   Respect verified redirect destinations; a new denied host needs a supported
   scoped configuration change, not a proxy workaround.
3. If bounded HTTP range or streaming inspection is practical and allowed, request a
   documented compressed prefix or stop at a byte/record budget. Verify206 and
   Content-Range if range semantics are relied on; a200 response may ignore Range.
   Enforce an actual read/write cap even if the server offers the entire archive.
   Record exact inspected prefix length/SHA256 and any incomplete final record.
4. A compressed prefix is not a complete gzip file: no full-archive SHA, trailer CRC,
   total uncompressed size or end-of-session assertion follows. Label deliberate
   acquisition cutoff separately from source truncation. A full permitted download
   can be compared to published checksums if present, and checked for gzip trailer/
   framing/EOF integrity. A publisher checksum over HTTP/TLS is useful integrity
   evidence but does not establish licensing or missing upstream-event completeness.
5. Validate BinaryFILE framing against the official protocol: two-byte big-endian
   payload lengths, complete variable payloads, external session identity and the
   terminal zero-length session marker where a full session is acquired. Distinguish
   raw historical file framing from MoldUDP64/SoupBinTCP; do not guess by file suffix.
6. Cross-check actual message lengths/types with the dated ITCH5 schema, unsigned
   big-endian fields, ASCII enums, six-byte nanosecond-since-midnight timestamps,
   Price(4) scaling, daily locates/order references and global control messages.
   Match2019 data against features applicable to2019, not every extension in the
   later specification (e.g.2023 direct-listing discovery). Pin the accepted schema.
7. Record raw message/type counts, first/last positions, time range/ties/regressions,
   source versus locally derived sequences, system markers, unknown fields/types,
   completeness gaps and decode failures. Archive naming or a terminal marker alone
   does not independently prove upstream exchange delivery completeness.

An exact dataset inventory is still an outstanding P1C deliverable; this checklist
is not substituted for measured sample results. No actual throughput or sample memory
usage is claimed.

## Initial L3 state, compatibility and valid interval requirements

The new source lead does not relax the inspected engine contracts:

- `src/replay/replay.cpp:38–49`: requires-snapshot by default; declared-empty needs
  evidence of an empty displayed book before all relevant adds, not just09:30,
  the first observed add or the presence of a start-of-market code.
- `src/book/order_book.cpp:233–267` and `include/gig/events/contracts.hpp:156–160`:
  recovery accepts complete order-level snapshots with real IDs/priorities, currently
  at most64 orders. Aggregated data cannot identify missing orders or FIFO. Multiple
  “complete” recoveries cannot be used to append chunks of one larger initial book.
- `src/book/order_book.cpp:162–181`: referenced orders must exist with matching
  resting side/price and sufficient quantity. Unknown orders cannot be synthesized
  from later cancellations, prints or reference levels.

An actually complete session beginning at a verified empty boundary may support a
prefix from that boundary. A short midday slice generally cannot establish its own
initial state without a complete identified initial snapshot and boundaries. A full
session stream filtered to one instrument still needs complete prior lifecycle and
deeper-order coverage for that instrument, plus retained global/session context and
an explicit mapping of filtering/local sequence ordinals. No sorting by timestamp or
silent removal of state-affecting records is allowed.

P1B's specification-level event compatibility remains: displayed A/E/X/D mutations
fit with exact units and prior state; F attribution and U replacement require retained
attributes/context and explicit priority assumptions. P is a print, not a displayed
execution or known aggressor. C's differing execution price/printability requires
more capability for full tape semantics; Q includes legitimate zero-share cases
unsupported as a current positive-quantity TradePrint. B has no current displayed-book
effect under the reviewed spec but requires tape/statistics correction support.
Session/auction detail, hidden queues and aggregate-only initialization are not fully
modeled. No actual candidate's compatibility histogram has been measured.

Do not apply these facts to `tvagg.gz` or legacy ZIP contents without identifying
their actual format. No claim that a candidate establishes a valid initial state,
order-level priority or replay interval can be made until its inspected content and
source contract meet these gates. No order IDs, executions or timestamps are invented.

## Journal limit and bounded-validation proposal

The existing maximum is100,000 retained journal records
(`src/replay/replay.cpp:45–49,109–115`); default4,096. Prior measured JournalEntry size
is15,944 bytes on the reviewed x86_64 ABI, not a portable or heap-inclusive guarantee.
No storage optimization, limit increase or new measurement was made in P1C.

| Allocated/retained entry count | Element bytes at the prior ABI size | Approximate MiB |
|---|---:|---:|
| 4,096 | 65,306,624 | 62.28125 |
| 10,000 | 159,440,000 | 152.05383 |
| 100,000 | 1,594,400,000 | 1,520.53833 |

Growth from65,536 to100,000 may temporarily hold old+new element arrays totaling
2,639,305,984 bytes, excluding live orders, allocator overhead, decoder/reference
buffers and canonical export. Streaming the compressed input does not bound this
retained native journal. Every required warm-up/history event also consumes capacity;
successful observations/filtered-instrument events passed to replay do too.

Proposed first validated interval: a source-supported prefix from the earliest verified
empty/complete-state boundary, stopping before a predetermined source-record/native
journal budget at a fully decoded message boundary. Start with a default-sized budget
if a useful interval fits, and report **bounded prefix validation**, not full-session
validation. Preserve exact inspected and unprocessed ranges, total count if known,
source-to-normalized record map and stop_reason. A deliberate inspection cutoff is
not a complete session or a sequence gap fabricated by the adapter.

If an initial snapshot is used instead, its complete contents must fit the actual
recovery contract, and all subsequent updates must be covered. If the minimum required
history exceeds the journal/budget, report resource-blocked feasibility; do not skip
it, restart empty per chunk, discard journals or bypass replay while claiming its
provenance. A filter can reduce retained target events only with explicit classification
and coverage evidence; it cannot erase an unknown target-book mutation. No interval
can be chosen after looking for favorable comparison matches.

A complete downloaded archive and a small validated prefix are distinct coverage
claims. An incomplete downloaded prefix cannot be advertised with the publisher's
whole-file checksum or session completeness. Full L3/FIFO correctness also cannot be
proven just by aggregate top-of-book agreement. Actual interval length/viability
remains unmeasured until directory and permitted sample inspection succeed.

## Completion checks and next action

Completed: latest branch/local/remote baseline verification, clean starting tree,
one EMI directory access attempt, current policy/draft inspection, narrowly scoped
saved/read-back network addition, user-statement provenance review, source-level
recovery/journal constraints, resource arithmetic, conditional compatibility and
bounded-inspection/validation design. Preserved five existing audit/design/remediation
files. Only this new report is committed/pushed; final SHA is in the completion response.

Blocked: independent directory inventory and smallest suitable file, actual checksum
listing, sample-specific terms/retention, archive acquisition and framing/integrity/
message/session inspection, actual initial L3 state and real-data comparison results.
No C++/Python tests or benchmarks were rerun because no implementation, build, schema
or package files changed. Documentation/evidence hashes, preservation and diff checks
are the checks performed; prior test results are not called new P1C results.

**Next:** publish the saved EMI allowlist addition, then resume P1C inspection under
this existing authorization. Stop before adapter implementation and request separate
authorization only after the actual sample feasibility results are available.
