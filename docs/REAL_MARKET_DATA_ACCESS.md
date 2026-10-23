# Phase P1B — official data access and sample inventory

## Subsequent observed-prefix verification — October 23, 2026

The separately authorized repeat4KiB inspection now passes all350 complete frames
under opt-in v2 (S1,R345,H2,Y2); default v1 retains346 decoded/4 unsupported.
Both observed H states are T with blank reason/reserved space; both Y actions are0.
Independent typed-field hashes and all4 directory associations agree. This does
not establish full historical compatibility, source completeness or initial L3 state.
No observed context/book reconstruction occurred. See
[NASDAQ_HY_PREFIX_VALIDATION.md](NASDAQ_HY_PREFIX_VALIDATION.md) and its evidence.
Statements below describe their original checkpoint unless explicitly updated.

## Offline H/Y support update — October 23, 2026

An explicitly selected status-observations_v2 profile now provides synthetic-tested
H/Y decoding and contextual observations,while default baseline_v1 preserves old
unsupported outcomes/hashes. See [HY_HISTORICAL_COMPATIBILITY.md](HY_HISTORICAL_COMPATIBILITY.md)
and [ITCH_HISTORICAL_COMPATIBILITY_MATRIX.md](ITCH_HISTORICAL_COMPATIBILITY_MATRIX.md).
No additional download or reinspection of the released real prefix occurred.
Actual historical H/Y values,full source completeness and valid initial L3 state
remain unverified. Another4KiB format-only request needs separate authorization;
no larger range or observed reconstruction is authorized by this offline study.

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

## Latest metadata-only preflight — October 23, 2026, America/New_York

At verified baseline `98e76bf6fbf8eb4fb0ab6586e3629625492d1e0c`, plain HEAD
to the exact EMI archive returned HTTP200, reported Content-Length3,524,013,057
and `Accept-Ranges: bytes`. HEAD with Range returned416 and contradictory
`Content-Range: bytes */0`; this does **not** verify present GET Range behavior.
Both transferred zero body bytes. Network testing stopped after those two HEAD
requests. No archive GET, sample/prefix download, LOBSTER retry or new licensing
claim occurred. See [NASDAQ_PILOT_PREFLIGHT.md](NASDAQ_PILOT_PREFLIGHT.md) for
actual resources, sanitized evidence, strict4 KiB proposal and approval checklist.
This supersedes only older access/size observations, not historical results or
rights/retention limits below. Acquisition remains unauthorized in this assignment.

## Current rights/access update — synthetic engineering assignment

Recorded October 23, 2026 UTC (October 22, America/New_York), from the user's
P1G/P1H authorization. This section supersedes acquisition-rights recommendations
in the historical investigations below; it does not replace their recorded HTTP
results or turn them into current observations.

The user supplies this written statement attributed to Nasdaq Client Support
representative **Dan Vizconde**:

> The EMI site you visited is publicly accessible, so you may download the sample
> data available on the site and use it as needed.

**Evidence class: user-provided correspondence quotation.** The original email,
headers, date and any attachments were not independently inspected/authenticated
in this update. No additional wording or conditions are inferred. The supplied
statement supports downloading and using the publicly available sample for this
project; the prior absence of a sample-use statement is no longer the same blocker.
It does **not independently establish unrestricted redistribution/publication rights**,
an open-data license, or an explicit retention/deletion schedule. Record any further
applicable terms before a broader use, and preserve the supplied correspondence
privately. Do not put raw data or correspondence containing private details in Git.

| Ledger item | Current evidence and consequence |
|---|---|
| Official directory | `https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/`, previously reached in P1C as reported in the subsequent conversation; no fresh request made here |
| Selected archive lead | `12302019.NASDAQ_ITCH50.gz`; direct official location is the directory plus this exact filename |
| Prior compressed length | **3,524,013,057 bytes** (about3.282GiB), prior reported observation; not remeasured in this update |
| Prior transport capability | HTTP Range support was reported verified; that does not establish content immutability, full archive integrity, actual session date or initial L3 completeness |
| Permission basis | User-supplied Dan Vizconde quotation above supports sample download/use; no paid account or purchase is proposed |
| Retention/cloud/publication | No explicit duration, deletion schedule, raw redistribution or derived-output publication grant is established by the quoted wording alone; no unrestricted grant is asserted |
| Current acquisition authorization | **Not authorized in this assignment.** The user expressly forbids real-market-data downloads; a separate resource-verified acquisition authorization is required |
| Current data inventory | No archive bytes downloaded or parsed in this update. No full/prefix sample SHA256, decompressed size, record count or empirical validation result is newly available |
| LOBSTER | Separate Support Case #17931099; no repeated diagnostics or acquisition, and no dependency for synthetic P1G/P1H work |

**Recommendation: GO for authorized synthetic engineering and offline acquisition
planning; CONDITIONAL GO for a later bounded private sample pilot after explicit
acquisition authorization and resource checks; NO-GO for claims of observed-market
validation now.** Valid initial L3 state, historical schema compatibility and independent
observed reference comparisons remain unverified regardless of download permission.
See [NASDAQ_REAL_DATA_PILOT_PLAN.md](NASDAQ_REAL_DATA_PILOT_PLAN.md) for the proposed
resource/integrity/initialization gates. This update changes documentation only and
performs no network request, agreement acceptance, dataset acquisition or publication.

## Latest investigation — official NASDAQ historical sample

Review date: 2026-10-21 UTC. Resumed baseline:
`8ab92dab20f9f66639b530a2b099788f7f66c0cc`.
Repository: `parthivpatel-patel/GIG-C-Microstructure-Engine`.
Branch: `feat/bootstrap-cpp20-engine`.

**Result: no suitable, permitted small NASDAQ historical ITCH 5.0 sample has been
verified in the official resources reached. NO-GO for market-data download or adapter
implementation at this checkpoint.** This is not a claim that NASDAQ has no sample
anywhere; the search is bounded by unavailable product pages and a blocked official
product host. The documentation supports an account-based historical-data route,
not an established free evaluation entitlement. No historical data file was requested,
no agreement accepted, no account created and no purchase or paid resource initiated.

LOBSTER was **not retried**. No proxy bypass, HTTP downgrade, certificate-verification
disablement, third-party mirror or unauthorized outreach was used. The C++ engine,
recovery rules and journal are unchanged. Earlier specification findings and access
attempts are preserved in the historical record below, not represented as fresh tests.

### Repository and network observations

The working tree was clean at entry. Local HEAD and the exact remote development HEAD
were both the resumed baseline above. Existing P1A, institutional audit and remediation
report/evidence were fingerprinted and remain unchanged. No branch switch or history
rewrite was performed. Only this access report is changed and normally committed/pushed.
Main is preserved.

The cloud runtime skill and networking reference were read. Runtime status reported
connected/current observations, both prior custom allowed hosts still listed, but
network-policy state `unknown` in this invocation. Do not replace the earlier recorded
`enforced` observation with a claim of currently verified enforcement. The actual
HTTPS responses below establish the reachability of the specific paths tested.
The local policy remains restricted with VPN unconfigured; no configuration update
was made. `www.nasdaq.com` is a different hostname from `www.nasdaqtrader.com`.

### Official discovery and source-access ledger

The NASDAQ Trader homepage was retrieved and its actual navigation/footer links were
inspected. The Historical ITCH, TotalView, global-data, data-agreement, copyright and
US Equity Tick History URLs below are taken from that official homepage. The initial
Historical ITCH query was a discovery probe and was subsequently confirmed to be a
homepage link; no guessed archive filename was requested. Times are UTC request
completion/recording times. Requests preserved the configured proxy and TLS validation.

| Official resource | Recorded UTC | Observed result |
|---|---|---|
| https://www.nasdaqtrader.com/ | 2026-10-21T22:53:44.109920+00:00 | curl0, HTTP200, 171,787-byte homepage; relevant official navigation links inspected |
| https://www.nasdaqtrader.com/Trader.aspx?id=ITCH | 2026-10-21T22:53:44.868324+00:00 | HTTP302 toward `http://www.nasdaqtrader.com/ErrorPage404.aspx?path=%2fTrader.aspx%3fid%3dITCH`; curl1 because HTTP redirect is disabled |
| https://www.nasdaqtrader.com/Trader.aspx?id=Totalview2 | 2026-10-21T22:54:02.656772+00:00 | HTTP302 toward the same ErrorPage404 path with its own encoded query; HTTP redirect not followed |
| https://www.nasdaqtrader.com/Trader.aspx?id=Global_Market_Data | 2026-10-21T22:54:03.072598+00:00 | Same HTTP302/ErrorPage404 behavior; HTTP redirect not followed |
| https://www.nasdaqtrader.com/Trader.aspx?id=AgreementsData | 2026-10-21T22:54:03.064093+00:00 | Same HTTP302/ErrorPage404 behavior; actual data-agreement terms not retrieved |
| https://www.nasdaq.com/solutions/US-Equity-Tick-History | 2026-10-21T22:54:01.994010+00:00 | curl56, proxy CONNECT403, origin HTTP000, zero downloaded body bytes |
| https://www.nasdaqtrader.com/Trader.aspx?id=CopyDisclaimMain | 2026-10-21T22:54:34.122775+00:00 | curl0, HTTP200, 89,748-byte copyright/trademarks/disclaimer page, relevant terms inspected |
| https://www.nasdaqtrader.com/robots.txt | 2026-10-21T22:54:34.045236+00:00 | Final HTTP200 at `https://www.nasdaqtrader.com/Trader.aspx?id=http404`, title “Page Not Available”; not a robots document |
| https://www.nasdaqtrader.com/sitemap.xml | 2026-10-21T22:54:33.889457+00:00 | Same final HTTP200 error page, 42,995 bytes; not a sample index or XML sitemap |

A 302 Location naming ErrorPage404 is not a measured HTTP404 response; the downgrade
was not followed. Likewise, HTTP200 HTML titled “Page Not Available” does not verify
that a sitemap exists. No missing/blocked page was treated as a successful sample or
license discovery. The `www.nasdaq.com` failure establishes a present access blocker
for that official product page, not that its data are unavailable or necessarily paid.
No LOBSTER request or repeated unchanged retry was issued.

Command shape, with exact arguments/return codes retained outside Git:

```sh
curl --proto '=https' --proto-redir '=https' --location \
  --max-time 25 --max-filesize 5000000 --silent --show-error \
  --output /tmp/gig-p1b-nasdaq-sample/<name>.html \
  --write-out '%{http_code} %{size_download} %{url_effective}' '<official URL>'
```

The final three policy/discovery probes used 20 seconds and a 3,000,000-byte limit.
The private evidence root is mode0700 and outside the repository. No JavaScript or
third-party tracking resources were executed. No market-data archives, byte ranges
or SFTP files were downloaded. Website HTML/metadata were inspected solely for
source discovery and terms; no website quote/statistic rows are reproduced here.

| Local evidence artifact | SHA256 |
|---|---|
| Exact homepage HTML | `ec90772938d3089172723a8fc37dfa2615c0aaf6f3668f4e1134e12a63c053a8` |
| Exact copyright-page HTML | `efb6ff02796530ed6b1ca5abe25f3f5086a5472ede7f34741a52fb7370688b5d` |
| Nine-request metadata ledger | `d293691090c0df35a6780c028f746381657c73c7bddbbd7b86c47c3be39b39d5` |

These are documentation/discovery identities, not market-data hashes. Raw pages,
error pages and request metadata remain external and are not distributed in Git.
The three prior official specification hashes remain recorded in the historical
section; those documents were reused, not redownloaded in this investigation.

### Six requested verification questions

| Question | Finding and evidence boundary |
|---|---|
| 1. Exact official sample download location | **Not established.** No verified direct URL to a small free/evaluation ITCH5 archive was found in the reached official resources. The prior access guide identifies `sftp://itchdata.nasdaq.com:22`, `ITCHFiles_v5`, and filename convention `SMMDDYY-v50.txt.gz`, but that is a documented account-based route, not an authenticated listing or a publicly licensed sample URL. The guide's illustrative filename/date is not a selected sample. |
| 2. Free access or agreement | **Unresolved for a sample.** The guide requires a Historical TotalView-ITCH account username/password; it does not identify a free anonymous evaluation entitlement. No account or entitlement was supplied/verified. Account-based does not by itself prove a fee; no fee amount or mandatory purchase is invented. The specific data-agreement link was unavailable as recorded above. |
| 3. Licensing and retention | **No sample-specific grant or retention conditions established.** Website copyright terms were read, as detailed below, but do not establish an ITCH historical sample entitlement or blanket research use. No assumption of perpetual retention, cloud permission or raw/derived redistribution is made. |
| 4. Size/date/format/sequence coverage | **No selected sample metadata available.** Compressed/uncompressed size, trading date, row/message counts, first/last record, source sequence extent, truncation and scope are unknown. The official wire/BinaryFile formats are documented; a sample's actual adherence/coverage has not been inspected. |
| 5. Defensible initial L3 state | **Not established.** There is no actual sample or initialized order-level state to examine. An account guide, date filename, first observed add or market-open flag is insufficient. A complete initial boundary plus all relevant displayed-order history, or a complete identified order snapshot with priorities/boundaries, is needed. |
| 6. Existing engine compatibility | **Conditional at specification level only.** Displayed adds, reductions/deletes and identified resting-price executions fit existing contracts given complete state. Execution-price overrides, printable flags, trade breaks, auction/status detail and large initial snapshots have the limitations described below and in P1A. No empirical compatibility or reconstruction pass is claimed. |

### Licensing facts actually observed

The official copyright page, headed “Copyright, Trademarks and Disclaimers,” says
website Content is owned by Nasdaq or affiliates unless otherwise stated. Its
Copyright section generally requires prior written consent for copying/storage/use,
subject to stated fair-use and limited-copy exceptions. It describes one temporary
copy in one computer's memory and one unaltered permanent copy for the viewer's
**personal and non-commercial use only**, with required permission notice and copyright
citation. It says other use may require prior written consent and a fee, except where
separate agreements permit it. The disclaimer also disclaims accuracy/completeness.

This is a scoped observation of the website wording, not legal advice or a conclusion
that this project's intended research qualifies under an exception. **Private is not
a synonym for personal/non-commercial.** The page does not identify a particular ITCH
sample, grant its data entitlement, establish its governing agreement, or specify a
historical-sample retention/deletion period. It cannot justify downloading unidentified
historical market data. It is not an open-data license. Any future acquisition needs
verified applicable sample/evaluation terms or written permission covering the actual
use. Do not distribute raw data, long specification excerpts or these HTML pages in
Git. Only source metadata, limited paraphrase and links are recorded here.

The previously read BinaryFILE phrase “Current Restrictions: None known” describes a
technical protocol document, not market-data licensing or unlimited retention.
The access guide's “most recent three months” directory descriptions concern stated
server availability, not a licensee's allowed retention period; even current server
availability has not been independently inspected. Do not conflate these meanings.

### Initial-state and engine fit gates for any future offered extract

A useful smallest evaluation extract would contain one named NASDAQ instrument,
one identified session/date, and a source-supported initial displayed state followed
by complete relevant order lifecycle updates. A small midday time slice without
initial state is not enough. A symbol filter needs explicit context/coverage and
must not omit deeper orders that can later enter the compared depth. A full-market
file may be much larger than a small sample and cannot be declared feasible before
its metadata and required history are known.

The current source still requires:

- Positive, nonfabricated IDs and exact price/share conversion. Reference IDs and
  stock locates must respect the verified daily scope. No invented order ID is
  introduced for a zero-reference non-displayed trade.
- `src/book/order_book.cpp:162–181`: known resting order, matching resting side/price,
  and sufficient remaining size for executions/cancels; no implicit state creation.
- `src/book/order_book.cpp:233–267` and
  `include/gig/events/contracts.hpp:156–160`: complete order-level recovery only,
  at most64 snapshot orders. Aggregate levels cannot initialize FIFO; splitting one
  full initial snapshot into multiple “complete” recoveries is invalid.
- `src/replay/replay.cpp:38–49,71–115`: proven initial state, scoped contiguous native
  ordering and explicit journal bounds. Default4,096 and maximum100,000 retained
  records remain in force. Prior measured JournalEntry size is15,944 bytes on the
  reviewed x86_64 ABI; no new performance/memory measurements or optimizations here.
- An actual BinaryFile session boundary and complete lifecycle/sequence coverage,
  not merely its terminal zero-length marker. That marker detects a missing terminal
  indication but does not independently prove no upstream exchange events were lost.
  Any local normalized sequence must be labeled derived, not an exchange sequence.

Specification-level classifications remain: A/E/X/D displayed mutations are E with
valid prior state and exact units; F and U are qualified projections with external
attribution/inherited context and explicit priority policy; P is nonmutating A with
missing aggressor (its modern side field is constantB); Q is A only for representable
positive-size print projection, with zero-share Q unsupported as current TradePrint.
C requires extra capability for faithful execution-price/printability semantics;
B can be externally classified as nonmutating for an expressly book-only replay but
needs correction support for tape/statistics. Full auctions/hidden queues and detailed
administrative semantics remain outside scope. These are code/spec facts, not a sample
histogram or an independently validated market run.

No recovered state, IDs, queues, source timestamps or executions will be fabricated
to make an eventual sample pass. No currently verified real-data interval exists.

### Smallest practical next step

**Ask NASDAQ Client Success for a no-cost, private evaluation extract and explicit
terms before attempting any data download.** The contact `Clientsuccess@nasdaq.com`
is verified in the official access guide; no email/message has been sent, since
outreach has not been authorized. The user can ask through that official channel:

> Is there a no-cost, officially distributed historical TotalView-ITCH5.0 evaluation
> file for offline private research validation? Please provide the exact official
> URL/access method and governing evaluation terms, including agreement/entitlement
> requirements, allowed cloud/local use, retention/deletion period, and restrictions
> on raw data, derived outputs and non-data validation reports. Prefer one instrument
> with documented session/date, framing, complete initial state and update coverage,
> plus compressed/uncompressed sizes, checksum, first/last source boundaries and any
> independently supplied reference depth states. No paid subscription is requested.

Prefer a complete low-activity instrument/session or a publisher-provided self-contained
extract whose full state-building history fits the current bounded journal. A few
thousand retained normalized records would keep the first experiment near the default
4,096-record budget; this is a project practicality preference, not a claim such a
sample exists, a mandatory NASDAQ distribution size or an institutional SLA. If a
larger complete history is necessary, reassess resources rather than clipping away
required orders or changing the engine under P1B. Request aggregate reference states
for comparison, while recognizing they are not a substitute for initial L3 identity.

Alternatively, a supported narrow allowlist addition for `www.nasdaq.com` would let
this environment inspect the homepage-linked US Equity Tick History product page.
That may reveal current evaluation terms/contact instructions, but is not known to
provide a small order-level ITCH5 sample and does not itself establish rights. No
network change was saved in this investigation: the smallest recommended step is the
specific official sample/terms inquiry, rather than broadening access or provisioning
an account without an identified permitted artifact. No LOBSTER action is required
for this NASDAQ-specific inquiry.

If NASDAQ confirms no suitable no-cost sample, stop acquisition and report that
confirmation. Do not substitute a licensed vendor file, unauthorized mirror, modern
trade/quote dataset or synthetic fixture and call it historical order-level validation.
Adapter implementation remains a separate authorization after rights, initial state,
metadata/resource feasibility and comparison coverage have been established.

### Checks and stop

Verified here: clean baseline and exact remote SHA; official navigation links;
request-level results and HTTPS-only handling; actual website copyright text;
prior document hashes and retained source/spec limitations; preserved prior report,
audit/remediation evidence; documentation-only diff and checks. No market-data file
or byte range was requested, no LOBSTER request was made, and no C++/Python tests or
benchmarks were rerun because implementation/build/schema/package files are unchanged.
No source acquisition, numerical reconstruction or performance success is claimed.

Only this report is committed and pushed to the existing development branch. The
completion response supplies the remotely verified final SHA. Stop after this
investigation; no adapter, engine change, main merge, release, live integration,
Terminal modification, subscription or paid resource is authorized or performed.

## Earlier P1B evidence — retained historical record

The sections below document earlier official-specification/access investigations.
They remain useful provenance but their references to a pending next action are
superseded by the NASDAQ-specific recommendation above. No destination was retried
merely to reproduce those historical results.

<details>
<summary>Earlier P1B access report and specification review</summary>

# Phase P1B — official data access and sample inventory

Current update: 2026-10-21 UTC, after the user published the two-domain network change.
Resumed baseline: `557f1237a3bd7d8598b0dcc6cd8d00aab8fff0ca`.
Repository: `parthivpatel-patel/GIG-C-Microstructure-Engine`.
Branch: `feat/bootstrap-cpp20-engine`.

## Current recommendation

**NO-GO for adapter implementation or claimed real-data validation at this checkpoint.**
Official NASDAQ documentation is now reachable and inspected. LOBSTER remains blocked
at the environment proxy, despite its domain being present in the enforced policy.
No market-data sample has been acquired, no LOBSTER usage terms or sample listing
has been read, and no actual initial L3 state or eligible validation interval has
been established. Do not equate successful specification retrieval with dataset
acquisition or permission to use historical data.

**GO for further official-document review; CONDITIONAL GO for resuming sample
acquisition** once LOBSTER access and actual evaluation rights are resolved. The user
already authorized that P1B investigation. No new blanket research authorization is
needed, but adapter implementation remains outside P1B and requires separate approval.
No engine or adapter changes have been made.

This current section supersedes the earlier pending-publication assessment, retained
below as historical evidence. The unchanged
[Phase P1A design](REAL_MARKET_DATA_FEASIBILITY.md) still governs initial-state and
validation requirements. Source facts newly verified here supersede its corresponding
NASDAQ format hypotheses; LOBSTER format hypotheses remain unverified.

## Repository and runtime verification after publication

- Starting working tree: clean. Local HEAD and exact remote development HEAD:
  `557f1237a3bd7d8598b0dcc6cd8d00aab8fff0ca`.
- Branch: `feat/bootstrap-cpp20-engine`. No checkout/reset/rebase was performed.
- Main remains `165c5038336887116d69160b0d8e5a1a5ef59d16`.
- Runtime status: `connectivity: connected`, `observations_current: true`,
  restricted network policy **`state: enforced`**, custom allowed hosts exactly
  `data.lobsterdata.com` and `www.nasdaqtrader.com`, both present in effective hosts.
- `/etc/codex/network-policy.json` independently contains both destination rules;
  `vpn_configured: false`. The policy file was read, not changed.
- A subsequent runtime-status check still reports the same enforced allowlist;
  `network_diagnostics: null`. The supported diagnostic metadata listing reports
  `history_status: not_found`, zero retained records and no legacy snapshot. No
  diagnostic logs or credentials were requested or disclosed.

The user's publication resolved the **saved-versus-active configuration** blocker.
It did not resolve every destination request. Publishing the same unchanged draft
again is not an evidence-based remedy for the remaining LOBSTER denial. No additional
network configuration, domain wildcard, proxy override, alternate route, certificate
bypass, mirror or paid resource was used in this resumed investigation.

## Current official-source access ledger

Times are UTC completion/recording times from the request recorder. Every request
used the inherited proxy and normal TLS verification. Redirects were HTTPS-only.

| Resource and exact URL | Recorded UTC | Result | Bytes / interpretation |
|---|---|---|---|
| LOBSTER sample index: https://data.lobsterdata.com/info/DataSamples.php | 2026-10-21T22:42:53.459874+00:00 | curl 56; CONNECT 403; origin HTTP `000` | 0 downloaded body bytes; no response-body file created |
| NASDAQ access guide: https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/ITCHFTP.pdf | 2026-10-21T22:42:55.235654+00:00 | curl 0; HTTP 200 | 133,895-byte PDF retrieved and read |
| Linked ITCH 5.0 specification: https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf | 2026-10-21T22:43:23.809605+00:00 | curl 0; HTTP 200 | 1,200,722-byte PDF retrieved and inspected |
| Linked BinaryFile specification: https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/binaryfile.pdf | 2026-10-21T22:43:24.719651+00:00 | curl 0; HTTP 200 | 84,384-byte PDF retrieved and read |

The two technical-specification links were extracted from annotations in the official
access guide; their `http` links were requested using HTTPS on the same approved
hostname. No guessed sample filename, mirror or new host was requested. No SFTP
connection was attempted. Nasdaq guide retrieval received `application/pdf`; PDF
structure and text were inspected locally with `pdfinfo`, `pdftotext` and PDF link
extraction. No cookie/authentication header values are included in this report.

Reproducible command shape (actual filenames differ by resource):

```sh
curl --proto '=https' --proto-redir '=https' --location \
  --max-time 40 --max-filesize 15000000 --silent --show-error \
  --dump-header /tmp/gig-p1b-resumed/<name>.headers \
  --output /tmp/gig-p1b-resumed/<name>.body \
  --write-out '%{http_code} %{size_download} %{url_effective}' '<official URL>'
pdftotext -layout /tmp/gig-p1b-resumed/nasdaq.body /tmp/gig-p1b-resumed/ITCHFTP.txt
```

The linked-specification requests used a 25-second timeout and the same size/TLS
restrictions. Recorder files separately retain return code, result, URL and UTC time.
All documents and temporary evidence are in mode-0700 `/tmp/gig-p1b-resumed`, outside
Git. The historical-data files themselves have **not** been downloaded.

### Document identities — not market-data sample hashes

| Retrieved official document | PDF pages | SHA256 of exact retrieved bytes |
|---|---:|---|
| ITCHFTP access guide | 5 | `77d0c9a5e86866951d99e58e5fda76b54ccf0316f19cbd7428492d459dee8177` |
| TotalView-ITCH 5.0 specification | 36 | `45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3` |
| BinaryFILE 1.00 specification | 2 | `a1f443400728b3ce44953e9ae263e4846fe6ad68420e7a635829872aefdfff60` |

The access guide's visible title is “Accessing NASDAQ Historical TotalView-ITCH Data
via SFTP”; its embedded metadata still says FTP. It has creation/modification metadata
January 12, 2024. The retrieved ITCH specification has metadata February 28, 2024,
while its newest listed revision-log entry is April 28, 2023. Metadata, HTTP
Last-Modified and semantic specification revision are different facts; none proves
a particular historical archive uses all features in this document. BinaryFILE
identifies version 1.00 with revision notes dated 2008/2010. These exact document
hashes pin what was reviewed, not a claim that each document is the latest revision
for every trading date.

LOBSTER's proxy header file SHA256 is
`18d753fd47b0d900fb245c70d205e2f8e380db074101939018f69da24db62bd1`.
It identifies a 403 error header, not official page content or a sample hash.
Temporary evidence is not distributed by this documentation commit.

## Verified NASDAQ findings and licensing boundary

**Access guide, pages 1 and 3–5:** historical access is described via
`sftp://itchdata.nasdaq.com`, port 22, with a NASDAQ Historical TotalView-ITCH account
username and password. The guide lists the `ITCHFiles_v5` directory, gzip filenames
such as the pattern `SMMDDYY-v50.txt.gz`, and instructs users to process ITCH 5.0 files
using BinaryFile. These are documentation statements, not an authenticated server
listing, current retention guarantee, entitlement verification or successful file
transfer. No account was created, credentials requested, purchase made or server
connection attempted. Existing environment access to public HTTPS specifications
does not establish permission/access to that separate SFTP service.

The guide names `Clientsuccess@nasdaq.com` for access problems. This is a verified
official contact, not an authorization to send outreach; no message was sent.

**No free historical sample or evaluation license is established by these three
PDFs.** The access guide describes account-based access but does not establish a
public anonymous market-data sample or a grant for the proposed private evaluation
and redistribution. BinaryFile's “Current Restrictions: None known” is a statement
inside a technical protocol document, **not a historical-data license**. Public
access to specifications is not a market-data use grant. Actual NASDAQ data-use,
redistribution and entitlement terms remain unresolved. No particular fee or purchase
requirement is inferred merely from the account-based workflow.

LOBSTER sample listings, format documentation and evaluation terms remain unread
because its official index is unreachable. Their existence, smallest sample, permitted
uses, redistribution clauses and actual download URLs are not guessed. Sample
acquisition is stopped until the applicable permission can be verified. No data
account or paid subscription is needed merely to continue inspecting the public
specifications already retrieved, but that does not resolve the sample objective.

## Source facts now verified from the official specifications

| Official source section | Observed specification statement | Consequence for the existing engine |
|---|---|---|
| ITCH, Data Types p.4 | Integers are big-endian, unsigned unless noted; alpha fields are space-padded ASCII; Price(4) has four implied decimals; timestamp is nanoseconds since midnight | Exact parsing and rational source quantum are appropriate; do not infer UTC, receive time or an exchange minimum trading tick from precision |
| ITCH, Architecture p.3 / System Event pp.4–5 | Delivery protocols normally provide sequencing; locate codes are assigned daily; non-stock messages use locate 0; tracking number is an internal tracking number | Preserve date/scope and source order; do not use tracking number as a transport sequence or assign symbol identity to global controls without explicit normalization |
| ITCH, Add Order pp.12–13 | New displayed orders have day-unique references; A includes side/shares/symbol/price, F adds attribution | Prior generic reuse ambiguity is narrowed for this NASDAQ specification: enforce day scope and preserve lifetimes; native AddOrder fits the displayed mutation, not MPID attribution |
| ITCH, Executed/Cancel/Delete pp.14–15 | Updates reference earlier adds; executions and partial cancellations reduce displayed shares; deletion removes all remaining shares | E/X/D fit current mutation contracts when prior order state exists; missing orders remain errors |
| ITCH, Executed With Price pp.14–15 | C executes at a different price from the initial display price and carries printable Y/N; non-printable executions should not be included again in tape/volume totals | Current BookExecution cannot faithfully encode both resting price and actual execution price/printability; a book-only decrement is a qualified projection, not complete trade/TCA validation |
| ITCH, Replace pp.15–16 | U removes the old remainder and supplies a new reference, total displayed quantity and price; side/symbol/MPID are inherited | Native atomic ReplaceOrder can project the mutation with explicit priority policy; raw attributes/lifecycle must remain recoverable. Do not claim this paragraph independently validates all exchange priority rules |
| ITCH, Non-Cross Trade pp.16–17 | P describes non-displayed executions, has no displayed-book effect; reference field is zero from December 6, 2010; side field is always B from July 14, 2014 regardless of resting side | Never turn P's reference into a positive displayed OrderId; never infer aggressor or resting side from that constant B. TradePrint with missing aggressor is a qualified projection |
| ITCH, Cross pp.17–18 | Q is a bulk cross print; shares may be zero when interest is insufficient; avoid double-counting non-printable executions | A legitimate zero-share Q cannot be forced through current positive-quantity TradePrint validation. Preserve as a source observation; full cross/tape semantics need explicit handling |
| ITCH, Broken Trade p.18 | B has no impact on the current book and may be ignored for book-only construction, but tape/statistics users must process it | This resolves P1A's open book-restoration question for the retrieved spec: do not restore liquidity. Native trade-break/statistics correction remains unsupported; an explicit book-only external disposition is defensible |
| ITCH, System Event p.5 | Deletes and broken trades can arrive after end-of-system-hours; end-of-messages is a distinct event | Do not stop at market close or clear state on halt/close without a proper boundary. This alone does not prove a selected archive starts from an empty complete book |
| ITCH, Direct Listing p.20 / revision log p.22 | O direct-listing capital-raise discovery is present; latest listed log entry April 28, 2023 | P1A's extension-existence hypothesis is confirmed for this document, not every historical date; no auction model is added |
| BinaryFILE §§1.1–1.2, p.1 | One session per file; session ID is external; messages have a 2-byte big-endian payload length; zero length ends session; missing zero marker indicates incompleteness | A future historical-file parser must validate framing/terminal marker and external session identity. This is not raw MoldUDP64 or proof of upstream packet completeness |

Classifications are **E** (exact displayed mutation with valid state), **A** (qualified
projection), **U** (unsupported in minimal scope), **C** (additional native capability
for full semantics). For NASDAQ, A/E/X/D mutation semantics above are now confirmed
at the specification level; F/U/P/Q/status records have explicit A limitations;
C execution-price fidelity and B tape correction remain C. Zero-share Q is U as a
current TradePrint even though it is a legitimate source observation. Hidden queues,
auction allocation and many administrative/imbalance attributes remain outside core
book scope. All raw headers/flags need external preservation. This classification
is not evidence of seeing any particular event in an actual data sample.

LOBSTER's conventional type mappings in P1A remain conditional E/A/U/C hypotheses;
they cannot be independently verified or counted until its official format and sample
are accessible. No vendor format should be inferred to equal raw ITCH merely because
its events have similar names. No adapter, source parser or normalization artifact
was created during this documentation investigation.

## Actual market-sample inventory and initial-state decision

| Requested measurement | Current result |
|---|---|
| Official market-data archives downloaded / message-book pairs extracted | 0 / 0 |
| Selected sample URL, filenames, symbol and trading date | Not established |
| Archive/member SHA256 and compressed/uncompressed sizes | Unavailable; the document hashes above are not sample hashes |
| Message/reference rows, timestamp range and event-type histogram | Not measured |
| LOBSTER schema, scaling, sentinel conventions, depth and row alignment | Not verified |
| ITCH schema | Official wire/framing documents inspected; no archive bytes parsed |
| Initial L3 IDs, quantities, FIFO priorities and completeness boundaries | No actual sample evidence |
| Eligible real-data validation interval | Not established |
| Exact matches/mismatches, real-data memory and throughput | Not run / not measured |

The preferred acquisition remains the smallest suitable officially offered LOBSTER
message/reference pair after terms verification. No market-data directory was populated
in this resumed phase. Public PDF documentation and all evidence remain outside Git;
no raw or normalized market rows are committed or redistributed.

The initial-state blockers from P1A remain. A complete day from a documented initial
boundary may be a route, but a sample starting at 09:30, an aggregate ladder or a system
open code is not sufficient evidence on its own. Current native recovery requires a
complete order-level snapshot and supports at most 64 snapshot orders; aggregated
depth cannot establish IDs or FIFO. All necessary history also counts toward the
100,000-record journal ceiling and its previously measured 15,944-byte entry cost.
No resource optimization, limit change, invented state or later-reference backfill
was performed. Thus **we cannot yet recommend adapter implementation as a validated
path for an actual selected sample**, even though more NASDAQ wire semantics are known.

## Remaining blocker and precise next action

The LOBSTER request at 2026-10-21 22:42:53 UTC failed with
`curl: (56) CONNECT tunnel failed, response 403`, before an origin HTTP response,
while the runtime reports both domains present and policy enforced. The response
header is from envoy. No supported retained diagnostic evidence explains the policy
mismatch. **The root cause beyond that observed proxy denial is unknown.** Do not
claim a vendor 403, a licensing refusal, global site outage or an unapplied draft.

Required user/platform action: have the cloud-environment administrator/support
investigate HTTPS egress to `data.lobsterdata.com:443` under this environment's
already-enforced custom allowlist, providing the exact URL, UTC timestamp, curl56 /
CONNECT403 outcome and the contrast with successful NASDAQ HTTPS requests. Enable a
supported working route to the same official hostname if policy permits. No new
wildcard or duplicate-domain publication is requested. After a meaningful access
change, resume P1B and recheck the official index and linked terms before acquisition.

Official resources for that follow-up:

- [LOBSTER samples](https://data.lobsterdata.com/info/DataSamples.php)
- [NASDAQ historical access guide](https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/ITCHFTP.pdf)
- [NASDAQ ITCH 5.0 specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf)
- [NASDAQ BinaryFile specification](https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/binaryfile.pdf)

If NASDAQ becomes the sample route instead, establish an already-permitted evaluation
artifact/entitlement and applicable terms first; the guide's account-based SFTP
workflow is not permission to purchase, create an account or request credentials in
chat. No account or transport access is requested merely to mask the blocked LOBSTER
sample investigation.

## Verification and scope of this update

Only `docs/REAL_MARKET_DATA_ACCESS.md` is modified. P1A, the institutional audit,
remediation report/evidence and engine implementation are checked unchanged. The
working tree and remote SHA are verified at completion; the documentation commit
hash is provided in the completion response. No C++/Python tests or benchmarks were
rerun: no implementation, build definition, schema or package changed. Document
identities, local PDF extraction, access results, preservation and diff checks are
the validation performed here. Prior test results are not represented as fresh runs.

**Stop here: no adapter implementation, main merge, release, Terminal work, live
connection, paid resource or market-data acquisition without verified rights.**

## Historical pre-publication record — superseded access status

The following retained record describes the earlier attempt from commit
`2b2c23a02c8d485d1aaab7d3db47079c4d3abc57` through
`557f1237a3bd7d8598b0dcc6cd8d00aab8fff0ca`. Its pending-publication instructions,
all-URLs-blocked result and statements that the PDFs were unread are historical and
are superseded by the current findings above. It is retained to preserve evidence;
do not use it as the current runtime or access recommendation.

<details>
<summary>Earlier P1B report, before the user's publication</summary>

# Phase P1B — official data access and sample inventory

Review date: 2026-10-21 UTC. Repository:
`parthivpatel-patel/GIG-C-Microstructure-Engine`.
Starting commit: `2b2c23a02c8d485d1aaab7d3db47079c4d3abc57`.
Development branch: `feat/bootstrap-cpp20-engine`.

## Recommendation

**NO-GO for acquisition and real-data validation in the current runtime.** A supported,
narrow network configuration change has been prepared and its persistence verified,
but it is not applied to this running environment. Fresh requests to both official
URLs still fail at the proxy with CONNECT 403. Official sample availability, terms,
formats and initial-state sufficiency therefore remain unverified. Acquisition has
stopped; no successful download or sample inspection is claimed.

**CONDITIONAL GO for resuming P1B** after the user reviews/saves the prepared network
change and publishes the environment, then actual official access and permitted use
are verified. This is not a GO for the adapter, which remains unauthorized. Resolving
network access alone will not establish licensing or valid initial L3 state.

This report is an evidence-qualified update to
[REAL_MARKET_DATA_FEASIBILITY.md](REAL_MARKET_DATA_FEASIBILITY.md), read before work.
That report's event matrices remain provisional. P1B adds a verified configuration
path and fresh access evidence; it does not promote prior format hypotheses to
observed sample facts. The P1A report itself is preserved unchanged.

## Repository and preservation verification

At entry:

```text
git branch --show-current
feat/bootstrap-cpp20-engine

git rev-parse HEAD
2b2c23a02c8d485d1aaab7d3db47079c4d3abc57

git status --short
<empty>
```

A read-only `git ls-remote origin` check returned the same development SHA. Main was
`165c5038336887116d69160b0d8e5a1a5ef59d16` and is not modified. No branch switch,
reset, history rewrite, force push, merge, release or deployment was performed.
The sole repository change for P1B is this new report. No engine, adapter, tests,
package, Terminal or raw-data files are changed or added.

Existing evidence files were fingerprinted before work and checked unchanged:

| Existing file | SHA256 |
|---|---|
| `docs/REAL_MARKET_DATA_FEASIBILITY.md` | `13fbc7dc83a34b8123151395329ed519715e5c70ce6d1cbaf88949e4cef749c8` |
| `docs/INSTITUTIONAL_ENGINEERING_AUDIT.md` | `25045c0c3820ca1ad17852be62ffece5b84a1261900301fb9f4dce681d0d7ef3` |
| `docs/CORRECTNESS_REMEDIATION.md` | `becc51cdd5f420814bbf32ca1b9dd0cfc10f9fc2add32c462860fc44bc5c85a6` |
| `docs/baselines/remediation-validation.json` | `8279682b837bd444613ec2e787c26cb13022d6aad4c50157b2bdd6bab993dce4` |

## Supported network configuration investigation

The cloud runtime and environment-onboarding skills were read, including their
networking/configuration references. The actual runtime policy at
`/etc/codex/network-policy.json` is restricted, with `vpn_configured: false` and neither
requested official host in its destination list. Runtime status reported connected,
current observations, restricted mode, network-policy state `unknown`, no custom
allowed hosts, and neither official host among effective allowed hosts. Connected
runtime status is not proof of access to either origin; the actual curl results below
are decisive.

The supported workflow was exercised:

1. Read the current environment configuration draft. Its revision was 2, custom
   network egress rules were empty, and the existing `package_managers` preset was
   selected. Existing setup/startup instructions and repository membership were read
   and preserved; they were not replaced as part of this request.
2. Saved a **network-only** draft update with these exact custom destinations:

   ```json
   {
     "config": {
       "network": {
         "allowed_domains": [
           "data.lobsterdata.com",
           "www.nasdaqtrader.com"
         ]
       }
     }
   }
   ```

3. The tool returned `status: "saved"` and **`requires_publish: true`**. Read-back
   confirmed revision 3 with precisely those two custom host rules and the existing
   preset still selected. Configuration persistence is verified; activation is not.
4. Re-read runtime status after saving. Both destinations remained absent from the
   running effective host list. Issued one fresh request per official URL after the
   saved draft; both still failed at CONNECT. There was no origin response body.

Saving a draft does not apply the policy, execute scripts, publish an environment or
prove future restored-runtime access. No tool available in this workflow was used to
publish; publication is a user action. No wildcard/unrestricted policy, TCP grant,
VPN, secret, credential, proxy change or mirror was introduced. TLS verification and
the inherited proxy path were retained. The policy file was inspected, not edited.
No scripts, variables, dependencies or repository-membership fields were changed in
the draft. No paid services or account registration were used.

The review requirement comes from the
[cloud-environment runtime skill](skill://plugin_connector_1p_c5b7d5df5d7081918f2c4be5a633ed5d/cloud-environment-runtime/SKILL.md):
“Configuration changes require the environment configuration workflow and its user
review.” The supported configuration tool additionally returned `requires_publish:
true`; the onboarding reference states that a saved draft does not apply changes to
the running environment. This is a concrete pending configuration change, not a
request to repeat the user's P1B authorization.

## Source-access ledger — actual P1B requests

Requests were made after draft persistence and runtime-status recheck. The time below
is the UTC request start. The proxy header date was 2026-10-21 22:34:27 GMT.

| Source / exact official URL | Attempted at UTC | curl exit | Origin HTTP / body bytes | Observation |
|---|---|---:|---|---|
| LOBSTER sample index: https://data.lobsterdata.com/info/DataSamples.php | 2026-10-21T22:34:27.176405+00:00 | 56 | `000` / `0` | `CONNECT tunnel failed, response 403`; no body file created |
| NASDAQ document: https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/ITCHFTP.pdf | 2026-10-21T22:34:27.197349+00:00 | 56 | `000` / `0` | Same proxy failure; no body file created |

The 403 headers identify `server: envoy`, not a LOBSTER/NASDAQ origin denial. Origin
HTTP `000` means no origin HTTP status was obtained. These observations establish a
current environment access blocker, not global dataset unavailability, an expired
sample, a paywall, a licensing refusal or a broken official server. No alternate
protocol, direct route, proxy bypass, disabled certificate checking or unauthorized
mirror was tried. No repeated unchanged-request loop was used.

Actual commands used by the temporary evidence recorder, once for each URL:

```sh
curl --proto '=https' --proto-redir '=https' \
  --max-time 25 --max-redirs 3 --location --silent --show-error \
  --dump-header /tmp/gig-p1b-evidence/<source>.headers \
  --output /tmp/gig-p1b-evidence/<source>.body \
  --write-out '%{http_code} %{size_download} %{url_effective}\n' \
  '<official URL from the ledger>'
```

The recorder captured each curl return code, stdout and stderr independently; a shell
continuing to the second URL was not treated as a successful first request. The
private temporary evidence directory is outside Git and mode 0700. It contains only
access/configuration-preservation evidence, not market data. Relevant identities:

| Evidence | SHA256 |
|---|---|
| `/tmp/gig-p1b-evidence/access-ledger.json` | `06eedbcff61d13676774ca3f2296df983ab0bd6a0a23f3b6619cc27a2750642d` |
| Each proxy response header file | `0c800248cc851b3da09c10c7032e50b35a4a538787f61f8fe016d0e8847839fa` |

These hashes identify local **failure evidence**, not a dataset, specification,
license or publisher-authenticated checksum. Temporary files are not distributed by
this Git commit. The ledger above preserves the meaningful observations in the report.

## Licensing and official availability evidence

| Question | LOBSTER | NASDAQ historical ITCH |
|---|---|---|
| Official landing resource retrieved? | No | No |
| Current sample listing or historical access instructions verified? | No | No |
| Smallest suitable official sample identified? | No; index inaccessible | Not selected; initial preference remains LOBSTER |
| Actual format specification retrieved/revision pinned? | No | No; the supplied PDF's contents and scope remain unread |
| Evaluation/private-use permission verified? | No | No |
| Applicable license/terms URL, version/hash or clause verified? | No | No |
| Raw/derived redistribution rights verified? | No | No |
| Login, entitlement, price or purchase requirement established? | Unknown; not inferred from proxy error | Unknown; not inferred from proxy error |
| Dataset download attempted? | No archive URL selected or requested | No historical data file selected or requested |

There is no positive licensing evidence yet. No terms were accepted and no grant is
invented. A public “sample” link, the user's research request or a format PDF does
not establish an open license or redistribution right. No commercial/noncommercial
license condition, retention rule, subscription fee or permission is asserted without
reading actual official terms. The PDF must be read before deciding whether it is
access guidance, a wire specification or both; an applicable dated wire specification
may need to be obtained through official links.

Acquisition remains stopped under task 12. Do not download a guessed archive, scrape
a mirror, substitute a third-party CSV, or describe a proxy error document as official
content. The next access attempt must follow an actual configuration change. If the
origin then works but rights remain unclear, stop again with the specific official
terms/reference or rights-holder clarification needed; do not purchase access.

## Sample inventory

**No market sample was obtained or inspected.** The inventory distinguishes absence
of acquisition from unmeasured data content:

| Requested item | Result |
|---|---|
| Acquired archives / extracted message-reference pairs | 0 / 0 |
| Selected official archive URL and filename | Not established |
| Dataset SHA256; compressed/uncompressed byte sizes | Unavailable, not an empty-file hash or zero-byte dataset |
| Member filenames | Unavailable |
| Instrument, venue as encoded by source, trading date | Unavailable |
| Message/reference row counts | Not measured |
| Timestamp range, timezone, precision and tied/regressing times | Not measured / not verified |
| Event-type histogram | Not measured |
| Price scaling, share unit, column layout and sentinel rules | Not verified against official source or sample |
| Reference depth coverage, row alignment and completeness | Not verified |
| Order-ID reuse, unknown initial orders and initial FIFO evidence | Not measured |
| Reconstructed snapshots / exact comparisons / mismatches | Not run; no success rate or empirical interval claimed |
| Real-data memory consumption and throughput | Not measured |

After rights verification, selection should compare the actual official listings and
choose the smallest suitable message/reference pair with a declared instrument/date,
interval and depth, considering uncompressed size and necessary initial history as
well as compressed size. No particular symbol, date, archive name or size is fabricated
here. All raw archives and extracted members must remain in a private directory
outside the repository. No data directory is populated in P1B.

## Initial L3 state and validation interval

No new source facts are available to resolve initial state. **A defensible actual
validation interval has not been established.** This is lack of evidence, not proof
that every official sample is unusable.

The engine prerequisites remain unchanged and were checked against the existing
source:

- `include/gig/events/contracts.hpp:156–160` bounds a snapshot to 64 orders; the
  snapshot type can describe aggregated levels, but recovery does not accept those
  as L3 orders.
- `src/book/order_book.cpp:233–267` requires a complete order-level recovery snapshot,
  including actual order identities and priorities. `src/replay/replay.cpp:184–220`
  requires appropriate stream boundaries. A price/size ladder cannot supply FIFO.
- `src/book/order_book.cpp:162–181` rejects missing referenced orders and execution
  side/price mismatch or excessive size; it does not create absent orders.
- `include/gig/replay/replay.hpp:6–20` offers requires-snapshot and declared-empty
  initial modes. Declared-empty needs source evidence of an empty state before all
  relevant orders, not an intraday timestamp or the first observed submission.
- `src/replay/replay.cpp:45–49` caps configured journal retention at 100,000 records.
  The prior verified x86_64 JournalEntry size remains 15,944 bytes; no new memory
  measurement or optimization was made. Required initial-history length is unknown.

Once a real sample is available, inspect its first reference row and full message
history, official start/capture/filtering semantics, deeper-order coverage, ID
lifetimes and any actual order-level initialization artifact. Determine whether a
true-empty start plus complete history exists, or complete L3 state is supplied.
A bounded aggregated opening ladder alone is insufficient even if the first few
updates subsequently agree. Do not manufacture order IDs, seed one order per price,
backfill from later records, clear the book until matching starts, or choose a
favorable interval using future reference states. A later matching top-of-book row
is not proof of complete state or FIFO identity.

If an official sample lacks valid initial L3 state, parser/inventory work can still
be reported as such after acquisition, but strict L3 reconstruction stays blocked.
Request the missing official history/state artifact or a separately authorized
capability design; do not weaken the engine to obtain a pass. No adapter is implemented
in this phase, even if a future sample proves feasible.

## Event compatibility status

There are **no observed source records** to classify in P1B. The following is a compact
carry-forward of P1A's conditional mappings, verified only on the engine side. It is
not a sample event histogram or official source-format verification. E means exact
stated displayed mutation with complete state and validated units, A means a qualified
projection, U means unsupported in the minimal scope, and C means more engine capability
is needed for faithful semantics.

| Provisional source category | Conditional class | Engine contract / unresolved requirement |
|---|---|---|
| Displayed submission; conventional LOBSTER 1 / ITCH A | E | AddOrder; verify actual source field definitions, units and live-ID scope first |
| Partial cancellation; conventional LOBSTER 2 / ITCH X | E | CancelOrder with reduction; source price/side, where supplied, must match known order |
| Deletion; conventional LOBSTER 3 / ITCH D | E | CancelAll; verify supplied remaining size if the source promises it |
| Identified displayed execution; conventional LOBSTER 4 / ITCH E | E for decrement; raw attributes may need retention | BookExecution requires existing ID, resting side/price and exact remaining quantity |
| Hidden execution/non-cross print; conventional LOBSTER 5 / ITCH P | A for print, C for hidden queues | TradePrint does not mutate; never infer a displayed order or aggressor without justified semantics |
| Cross/auction; conventional LOBSTER 6 / ITCH Q | A for print, C for full auction behavior | Preserve classification externally; no arbitrary visible-order depletion or synthetic matching |
| Halt/session control; conventional LOBSTER 7 / ITCH H, h or selected S | A / C for full status machine | SessionEvent is only an observation; quoting/trading substate and true resets require official rules |
| ITCH F attribution and U replacement | A | AddOrder or atomic ReplaceOrder projection; retain attribution, verify priority and inherited side/context |
| ITCH C explicit execution price | C for full semantics; A for declared book-only decrement | Resting-price decrement cannot encode separate actual execution price/printability; do not corrupt trade/TCA meaning |
| Broken trades/corrections, conventional ITCH B | C | No match-ID break/correction contract; do not restore liquidity without verified source semantics |
| Other directory/status/auction indicators, unknown types/extensions | U or explicit external configuration/observation | Classify against retrieved dated specification; never silently drop a potentially state-affecting event |
| Aggregated reference-book row | A as comparison input, C as L3 recovery | Cannot infer real order identities/queues from aggregate prices and quantities |

The full provisional event families and limitations remain in P1A sections D–G.
Unknown source sequence/receive time must remain unavailable; derived local row/event
ordinals must be labeled as local normalization, not exchange observations. Official
clock/price/quantity rules and reference-row alignment remain unresolved. No source
semantics are marked exactly verified because a similarly named engine type exists.

## Required user action and resumption gates

1. Open this cloud environment's **environment settings** and review the saved
   network-only draft. Confirm custom allowed domains are exactly
   `data.lobsterdata.com` and `www.nasdaqtrader.com`, with the existing presets retained.
   Review and save the changes, then **publish the environment**, as required by the
   tool's `requires_publish: true` result. This is environment configuration, not a
   GitHub release or deployment. Do not reset the repository or replace the branch.
2. Resume P1B after that configuration is active. Recheck runtime status and actual
   TLS requests before asserting access. Reverify local/remote development HEAD and
   preserve the existing checkout/history if publication reconnects the environment.
   A saved/published configuration is not itself evidence of successful restoration
   or origin access.
3. Verify official resources at these links:
   - [LOBSTER official samples](https://data.lobsterdata.com/info/DataSamples.php)
   - [NASDAQ supplied historical ITCH document](https://www.nasdaqtrader.com/content/technicalSupport/specifications/dataproducts/ITCHFTP.pdf)
4. Read the official linked sample/format/evaluation terms before any archive
   acquisition. No applicable terms URL was accessible, so none is guessed here.
   If those pages redirect or link to a different necessary official host, identify
   it from verified official content and request a narrowly scoped supported addition.
   Do not pre-authorize wildcards, mirrors, paid accounts or unspecified destinations.
5. Only when private use is permitted, select one small suitable official LOBSTER
   sample, retain it outside Git, hash/inventory it, and assess actual initial state
   and supported event coverage. If license terms require clarification, obtain it
   through the official rights-holder channel before download; no outreach was sent
   in this phase.

The user has already authorized P1B acquisition subject to these conditions; another
blanket permission to investigate is unnecessary. The current external prerequisite
is applying the saved environment change. Adapter implementation still requires
separate authorization after a source-supported feasibility decision.

## P1B checks, outcomes and stop

Verified in this phase: requested baseline, branch, clean starting tree and remote
SHA; existing report/evidence preservation; supported configuration read/update/read-back;
precisely two saved host additions with presets preserved; pending activation status;
two actual proxy-denied official requests; no dataset acquired; doc/source-reference
review and documentation-only Git diff checks. No C++ tests, package builds, benchmark
runs or new sanitizer matrix were necessary or executed for this documentation-only
access investigation. Earlier P1A/remediation results remain historical evidence,
not fresh real-data validation or P1B test claims.

The final commit SHA and exact remote verification are reported in the completion
response. Only this report is committed/pushed to the existing development branch;
engine, P1A report, audit and remediation evidence remain unchanged. No raw market
files are committed or redistributed. No adapter, Terminal change, live connection,
main merge, release, purchase or paid resource is created.

**Stop acquisition and adapter work here. NO-GO remains in force for current-runtime
acquisition and validated replay until the required access, rights and state evidence
are obtained. Continue only after the identified environment action; do not implement
the adapter under this P1B authorization.**

</details>

</details>
