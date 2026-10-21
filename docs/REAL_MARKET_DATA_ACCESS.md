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
