# P1J independent audit and release-candidate requirements

Documentation-only preparation against feature checkpoint
`cafcdb986afac5298c95bcf3418acb7cf3e6aafe`, branch
`feat/bootstrap-cpp20-engine`, inspected October23,2026 UTC. The qualified P1H
implementation/measurement commit is `e055f055a447baa6bf1f913c09f7c7dcd57a8878`;
its evidence commit does not change that source identity. Main's retained baseline is
`165c5038336887116d69160b0d8e5a1a5ef59d16`.

This document specifies a future independent audit and candidate gate. It does not
claim that P1I/P1J implementation, a fresh independent audit, release publication,
observed-data qualification or production trading qualification has occurred. No
source, tests, dependencies, network settings, market data or publication workflow
were changed to prepare it. A release, main merge and further production-code work
still require separate authorization. No firm's proprietary implementation or hiring
standard is assumed.

## Decision and qualification levels

**GO for continued private synthetic research evaluation** of the actually qualified
Linux x86_64 configurations and authored-empty, two-symbol scope. P1G/P1H provide
substantial independent algorithmic and fault evidence. That evidence supports scoped
research engineering claims, not a certificate that all source paths are correct.

**CONDITIONAL GO for a private release-candidate audit.** Close the required review,
evidence-restoration, dependency/advisory and documentation gates below, resolve every
reproduced candidate-scope correctness defect, and retain explicit limitations.
This is permission to assess readiness, not permission to publish an artifact.

**NO-GO for an observed-NASDAQ validation claim or production trading release.** No
historical archive has been inventoried/replayed, no observed complete initial L3
state established, and no source-provided independent market reference compared.
Operational, broker, latency, queue and statistical calibration requirements remain
separate. Do not fill those gaps with synthetic agreement.

| Qualification | Required evidence | Current disposition |
|---|---|---|
| Private synthetic research candidate | Authored initialization, scoped exact semantics, independent stepwise truth, failure/resource behavior, supported local builds, reproducible private artifacts and honest limitations | P1G/P1H locally qualified; independent RC review and remaining checklist closure pending |
| Observed-data research validation | Permitted acquired artifact, actual integrity/profile/session inventory, defensible initial state, complete scoped event accounting and independent observed reference coverage | Unrun; acquisition requires separate authorization after resource verification; reference/initialization may be unavailable |
| Production execution/trading system | Separately specified exchange/broker/operational contracts, resilience, deployment/security/monitoring, calibrated models, service-performance evidence and operational authorization | Outside the implemented and currently authorized scope; not inferred from the research candidate |

## Evidence inventory to audit

Inspect the files and raw evidence, not only these summaries. The durable JSON files
retain source/JUnit/artifact identities; ignored `build/` logs are local evidence and
must be privately retained or regenerated before another environment relies on them.
A SHA256 identifies bytes; it is not a signature, publisher-origin proof or licensing
grant. A reported successful command without its source/configuration identity is
insufficient for closing a gate.

| Evidence | Exact source and material verified scope |
|---|---|
| Historical audit and targeted remediation | [INSTITUTIONAL_ENGINEERING_AUDIT.md](INSTITUTIONAL_ENGINEERING_AUDIT.md), [CORRECTNESS_REMEDIATION.md](CORRECTNESS_REMEDIATION.md). Preserve the original audit/addendum and failing-before regressions. Maker reports, TCA quantity limits, retained profiles, digest consistency, compiler metadata and deterministic fixture repairs do not close every historical audit recommendation. |
| Wire/context foundations | [P1E_VALIDATION_REPORT.md](P1E_VALIDATION_REPORT.md), [P1F_VALIDATION_REPORT.md](P1F_VALIDATION_REPORT.md), their evidence/coverage records and independent scripts. Their historical counts describe their own commits. |
| Joint reconstruction | [P1G_IMPLEMENTATION_NOTES.md](P1G_IMPLEMENTATION_NOTES.md), [P1G_COVERAGE.md](P1G_COVERAGE.md), [P1G_DISCOVERED_DEFECTS.md](P1G_DISCOVERED_DEFECTS.md), [P1G_VALIDATION_REPORT.md](P1G_VALIDATION_REPORT.md), [P1G_EVIDENCE.json](P1G_EVIDENCE.json). Native first-add failure was reproduced before repair; prepared transactions, lifetime guards and isolated restart are additive. |
| Bounded streaming | [P1H_COMPRESSION_DEPENDENCY_REVIEW.md](P1H_COMPRESSION_DEPENDENCY_REVIEW.md), [P1H_COVERAGE.md](P1H_COVERAGE.md), [P1H_VALIDATION_REPORT.md](P1H_VALIDATION_REPORT.md), [P1H_EVIDENCE.json](P1H_EVIDENCE.json). CRC/read-ahead pause regression, strict member policy, source hashes and publication flags are part of the qualified source. |
| Final local matrix | `docs/P1H_EVIDENCE.json:matrix`, `build/p1h/evidence/matrix.json`, nine corresponding JUnit/log hashes. Six native configurations117/117 each; GCC Python Debug/Release120/120 each; Python sanitizer121/121: **1,063 outcomes**, zero recorded failures/skips/disabled tests. No new matrix was run merely to write this planning document. |
| Packaging | `docs/P1H_EVIDENCE.json:package` and local package logs: direct and offline source-built0.1.1 wheels each pass7 interface+6 export cases, **26 inner unittest cases** total. Source archive checks49 frozen validation files byte-for-byte. Installed module paths and absence of libz linkage were checked; no P1H Python API is implied. |
| Independent models | P1G:10,032 sessions/65,186 candidates/10,025 rejections. P1H:475 fixtures/3,993 framed/3,989 accepted records; six negative controls in each model suite. These are bounded synthetic campaigns, not exhaustive input verification or exchange certification. |
| Allocation and interruption | P1G:5 native first-add,6 creation,6 adapter-add,5 U and32 isolated restart reached allocation sites. P1H:4 reader sites,10 pipeline creation and23 pipeline feed sites; independent scenarios overlap code and must not be advertised as unique global sites. P1H has2,119 fragment/cut schedules plus owned-tail move and pause/CRC checks. |
| Performance/memory | `docs/P1H_EVIDENCE.json:measurements`, `memory_categories`, `large_synthetic_stop`, and16 raw Release benchmark records. Scope, warmups, repetitions, fixture/executable/compiler/source hashes and CPU/RSS accounting are retained. No tail-latency result is present. |
| Hosted access evidence | `build/p1h/evidence/hosted-ci-access.json`: the recorded `gh api .../actions/runs?...` request exits1 with `Forbidden`. This proves evidence access failed, not that hosted tests passed or failed. |

Canonical semantic identities required for unchanged qualified contracts:

| Model | SHA256 |
|---|---|
| P1E wire | `142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e` |
| P1F context | `58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e` |
| P1G L3 | `bb16d4ba9e400ee8f2bc40707de5aa89d0b0955819b4f1f45ca2cdf82cac7991` |
| P1H streaming | `be5d6f5a15fa1dc77560e0a815b8397a605eab369fa66f44df12e5ed9b04a4d5` |
| Installed Python research example | `c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9` |

A future intentional semantic change requires an explained, versioned contract and
independent expected-value review. Replacing the golden hash with the current output
is not a correctness review.

## Release-candidate acceptance matrix

Priorities: P0 blocks any claim contradicting the affected gate; P1 blocks closing
the scoped candidate review; P2 is deferred capability unless it is advertised.
Statuses below distinguish current evidence from work that this document proposes.
No gate authorizes implementation or an external action by itself.

| ID / priority | Gate and present status | Measurable acceptance and review evidence | Dependency / stop condition |
|---|---|---|---|
| RC01 P0 | Source/history identity — current feature checkpoint known | Identify exact implementation and evidence SHAs; verify repository/branch/remote HEAD; inventory dirty files; demonstrate main/history preserved; freeze actual source/config hashes before validation | Any unknown/unreviewed source delta invalidates reused results for affected paths; no reset/force-push |
| RC02 P0 | Current correctness regressions — locally verified | Preserve all old assertions and documented before/after reproductions; reproduce every new material defect, repair within authorized scope and rerun affected/final gates with zero unresolved candidate-scope correctness defects | A new reproducible atomicity, lifetime, numeric, accounting or provenance defect blocks candidate acceptance |
| RC03 P0 | Joint transaction proof — verified scoped tests; independent source review pending | Trace prepare→metadata/receipt preflight→one native apply→private nofail commit. Inspect move-only owner/lifetime/generation guards, reentrancy, reserved storage and nothrow assertions; reproduce reached allocation sweeps and exact retry | No fallible allocation/validation/callback may appear after successful native mutation; diagnostic/capacity changes must remain separate from accepted state |
| RC04 P0 | Initialization and scope truth — synthetic-only | Unknown/O-only/time/aggregate/bounded/partial history never produces eligible reconstruction. Inspect literal fixture proof and exact source/session/rules. Positive native64 recovery must not be relabeled a full context seed | Observed or seeded eligibility remains blocked without full context/FIFO/history evidence |
| RC05 P0 | Numeric/event semantics — locally verified profiles | Independently compare rational price/share conversion, domain bounds, IDs, FIFO, partial/full reductions, U lose priority and E/C resting-versus-execution price. Reject lossy/off-unit projection before commit | Native numeric capabilities exceed selected integer source-quantum profiles; unsupported configurations must reject, not round or widen silently |
| RC06 P0 | Unsupported source and identity lifecycle — explicit limits | Every enabled S/R/A/F/E/C/X/D/U/P/Q/B path has a typed outcome; H/unknown/Q-origin B/unknown bindings stop explicitly. Retired IDs and match/correction histories cannot be silently evicted or reused | Historical namespace, reuse and unsupported message semantics require separate dated-profile evidence |
| RC07 P0 | Streaming integrity/publication — locally verified | True EOF, gzip CRC/trailer, no trailing member/bytes, BinaryFile terminal and exact compressed/raw SHA must all agree before complete publication. Wrong hashes and corruption must block it | Member verification, prefix integrity, context session completeness and authored initialization remain independent facts |
| RC08 P0 | Source accounting and interruption — locally verified | For each fixture compare physical complete frames, considered/accepted/rejected/pending/unconsidered records, native/external counts, source/native sequences, residual framing and buffered output; no invented tail totals | Read-ahead cannot be mistaken for logical commitment or complete source inventory |
| RC09 P0 | Restart/recovery boundary — limited deterministic restart implemented | Rebuild a fresh instance from authenticated expected source identity and byte0; compare logical checkpoint under different chunk schedules; changed source/config/code/state rejects; fail isolated rebuild allocations without altering original | No claim of MAC/signature, hot restore, gzip seek, durable state publication or crash recovery |
| RC10 P0 | Independent oracle integrity — locally executed; fresh audit pending | Review algorithms and fixture generation separately from production containers; compare every relevant ID/price/quantity/priority/level/ledger/metadata/disposition; show negative controls fail and reproduce canonical hashes | Independent algorithmic calculation is not organizational reviewer independence; correlated specification errors remain possible |
| RC11 P1 | Compiler/sanitizer matrix —1,063 local outcomes | On the final frozen candidate, rerun affected supported configurations and retain all nine JUnit identities; zero failures/skips/disabled required cases and no suppressed sanitizer findings | No inference of MSVC/libc++/ARM64/other-OS success; Python late-finalization leak limitation remains explicit |
| RC12 P1 | Python package/API boundary — direct/source-built consumers verified | Restore both wheel consumer checks, installed paths, schemas, export graph/profile integrity and example identity. Inspect ordinary wheel dependencies and optional streaming OFF behavior | Only CPython3.12/Linux x86_64 exercised; metadata declares>=3.9,<3.13, so other versions require qualification or narrower advertised support before broader distribution |
| RC13 P1 | Fresh environment restoration — partial evidence | A reviewer independently restores the named source artifact/clean checkout with recorded tools and system zlib; executes documented offline demo and applicable tests, captures commands/artifact identities and confirms no build-tree imports | Prior source-wheel restoration is strong package evidence, not proof of a clean VM/other machine bootstrap |
| RC14 P1 | Memory budgets and retention — measured selected profiles | All published candidate examples declare finite buffer/count caps and caller-owned bounded PMR; verify cleanup at real failures and compare PMR/RSS separately. Reproduce selected profile and large controlled-stop results | Default PMR is not an implicit128MiB governor. Do not promise all maximum caps fit together or replace resource failures with data loss |
| RC15 P1 | Performance evidence — measured batch baseline | Reproduce checksum/fixture correctness before timing; retain two warmups/seven measured repetitions, compiler/config/CPU/source identity and allocations/RSS. Compare only equivalent workload scopes; disclose noise | No invented service/tail latency, institutional target, real-archive throughput or causal optimization claim |
| RC16 P0 | Dependency/security inventory — pinned/observed versions, current advisory clearance missing | Inventory source/build/runtime/system dependencies, exact artifacts and notices; obtain a dated advisory review with explicit unavailable sources and findings, then document disposition/revalidation of each applicable issue | Pinned versions and an old PyPI snapshot are not current security clearance; this remains unverified, not a discovered vulnerability |
| RC17 P1 | Hosted CI — unavailable evidence | Obtain actual Actions run ID, head SHA, conclusion and logs for the candidate's claimed hosted configurations; verify system zlib resolves to the required version and expected tests actually run | Recorded API `Forbidden` blocks verification. Workflow YAML/install commands alone cannot close the gate or prove hosted failure |
| RC18 P2 | Platform expansion — unverified | Qualify native ARM64 and any new OS/stdlib/Python claim with actual hardware/environment/compiler/test/package evidence | No ARM64 test or cross-compilation evidence exists; defer the claim rather than adding unnecessary platform work to the scoped Linux candidate |
| RC19 P1 | Documentation/evidence coherence — requires candidate review | Reconcile current source/options/counts and historical dated sections; every supported command succeeds under declared setup; links and fixture identities resolve; distinguish implementation/evidence commits and pending versus completed milestones | Preserve historical audits/reports rather than rewriting past results. P1G/P1H current headers now record verified checkpoints; preserve earlier counts as historical evidence |
| RC20 P0 | Repository/data/secret boundary — scoped synthetic policy, final audit pending | Inspect full candidate diff and tracked artifact inventory for credentials, restricted/raw market data, accidental binaries, generated caches and unrelated Terminal/live changes; retain explicit data provenance for every fixture | No real dataset may be included merely because public access/download/use was permitted |
| RC21 P0 | Licensing/distribution authorization — public release not granted | Owner chooses project distribution/license/version/scope and approves notices/artifact contents; determine actual zlib/native/Python redistributable obligations; obtain explicit release authorization | Private project currently has no new public redistribution license. NASDAQ access statement is not an unrestricted redistribution/publication grant |
| RC22 P1 | Release artifact provenance — private builds only | Manifest candidate source/config/toolchain/dependencies/schema/API versions and hashes; verify source/wheel contents and every referenced research artifact; define immutable candidate ID and retained evidence | Private0.1.1 wheel creation is not release publication, binary reproducibility or a stable C++ ABI promise |
| RC23 P0 observed | Actual historical source/profile — unrun | After separate acquisition authorization, inventory actual file bytes/hash/date/member/framing/types/namespace/session and supported versus unsupported records. Freeze a dated profile and resource plan before replay | No multi-GB download in these phases; artifact name/range support do not prove contents, integrity or trading date |
| RC24 P0 observed | Initial/full-source L3 evidence — missing | Demonstrate complete empty boundary plus all required history, or independently validated full context/FIFO/lifetime/match seed. Account every scoped source message without fabricating identities or truncating depth | Current native snapshot64 bound and missing complete-context seed contract remain real blockers; O/open time/quotes are insufficient |
| RC25 P0 observed | Independent observed reference — missing | Freeze reference provenance and row/event alignment before comparison; report eligible coverage/counts, exact prices/quantities, all attempted matches/mismatches and first reproducible mismatch | Internal Python/C++ agreement supports differential validation, not external ground truth. Missing external references blocks that stronger claim, not an honestly labeled format/model pilot. No zero-coverage success claim |
| RC26 P0 research claims | Financial/statistical interpretation — synthetic assumptions explicit | Audit data availability/clock scope, causal windows, sign/impact assumptions, forecast provenance, held-out evaluation and sensitivity for every advertised empirical result | Current queue/latency/fees/impact assumptions are not calibrated exchange observations; empirical conclusions remain unverified |
| RC27 P2 production | Persistence, operations and live safety — excluded | Only under separately approved requirements: define crash durability, state publication, availability, monitoring, incident/recovery, authentication and exchange/broker contracts with measurable tests | Do not build a production stack, broker connection or Terminal integration to close a synthetic research candidate |

## Independent review procedure and finding standard

The next reviewer should inspect actual code and evidence outside the original author
workflow. At minimum review `include/gig/itch/` and `src/itch/`, the native book/replay
mutation and recovery paths, exact numeric factories/validation, Python serialization
and export contracts, CMake/presets/workflow, package contents and benchmark scripts.
Read the original audit before deciding which findings are closed. Strong oracle
separation and a second agent's review are useful evidence, not a replacement for a
clearly identified independent candidate reviewer.

Each material finding must contain:

1. Severity and status, exact source commit/path/line range, and affected advertised
   contract. Separate a reproduced defect from excluded scope or missing evidence.
2. Sanitized reproduction commands/input identities, expected values from an
   independent calculation, actual output and smallest triggering boundary.
3. Root cause, accepted-state/diagnostic/resource consequences, proposed minimal
   repair and dependencies. Do not silently optimize the journal while repairing it.
4. Measurable acceptance and failing-before/passing-after evidence, including
   allocation, deterministic and supported regression effects where applicable.
5. Remaining risk/effort, review owner and disposition. An unavailable check remains
   unavailable; do not convert missing evidence to a successful checkmark.

Review all aggregation boundaries: one event, accepted prefix, gzip member, complete
artifact, exchange session and research export have different validity conditions.
A fully verified smaller boundary must not certify a larger unobserved boundary.

## Dependency and security checklist

- Compare `requirements-python.lock`, `pyproject.toml`, CMake feature flags and actual
  installed packages/wheel contents. Record direct and transitive runtime/build
  dependencies; pybind11/scikit-build-core/jsonschema are pinned, while compilers,
  standard library, Python and system zlib are separately qualified components.
- Preserve [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) and the inspected zlib
  package/header/runtime identities in the compression review. The optional native
  target uses zlib1.3.1 on this host; the Python fixture reference uses1.3.2. Those
  different implementations are explicit evidence, not interchangeable package hashes.
- Perform a current, dated advisory review. `scripts/review_dependencies.py` supports
  a limited Python wheel/PyPI snapshot; its successful historical result does not
  cover current zlib/compiler/CPython/kernel advisories or all vulnerability sources.
  Do not fetch/install/upgrade dependencies merely to make a checklist look complete.
- Verify hosted dependency resolution before certifying the workflow. It currently
  requests Ubuntu24.04 and installs the distribution's `zlib1g-dev`; CMake requires
  minimum1.3.1. Actual runner package/header/runtime versions must be observed. This
  is an unresolved compatibility check, not a reproduced runner failure.
- Inspect hostile-input boundaries: checked zlib allocation products/alignment,
  exception containment at the C ABI, fixed buffers, header/ratio/output limits,
  unknown types, integer exhaustion, sticky errors, borrowed-span lifetime and
  reentrancy. Confirm error reporting itself cannot create a late partial commit.
- Scan the proposed artifact inventory for secrets and restricted bytes without
  printing credential values. Keep private raw/evidence paths outside published
  artifacts; inspect dependency/build logs for accidental sensitive environment dumps.
- Do not claim signed artifacts, publisher authentication, SBOM completeness, current
  CVE clearance, OS sandbox resilience or supply-chain attestation without their
  actual independent evidence. A static inventory may be sufficient for a private
  candidate; no unnecessary infrastructure is requested here.

## Memory, performance and journal review criteria

The P1H largest measured selected PMR peak is41,685,328 bytes; largest measured native
wait-accounted high-water is58,093,568 bytes; independent streaming oracle high-water
is15,335,424 bytes. They pass the measured128MiB PMR/256MiB native-RSS/128MiB oracle
profile proposals, not all possible configurations or platforms. Resource owners,
fixed stack/object storage, driver/fixture allocations, allocator retention and
process-tree versus single-child accounting must remain explicit.

The500,001-record synthetic generator inventory describes a20,500,016-byte raw source
compressed to59,723 bytes. The pipeline probe accepted1,024 external observations,
stopped at frame1,025, read255 compressed bytes and produced65,536 raw bytes, with
598,567-byte peak selected PMR and no native journal entries. This demonstrates a
controlled resource stop and honest prefix accounting, not full-file validation.
A reviewer must reproduce the prefix hash and explicit unread/buffered tail rather
than advertise500,001 processed records.

Retained state still grows: lifetime references include retired orders, matches retain
correction history, receipts retain source records, and native journals retain full
large events. Selected ABI sizes are56/16/344/15,944 bytes per lifetime order/match/
receipt/journal element. These are not portable heap-inclusive sizes. At two journals
of1,024 entries, elements alone total32,653,312 bytes; a selected growth overlap can
reach40,816,640 journal bytes before other state. A generic100,000-entry journal can
therefore exhaust the chosen budget long before reaching its record cap.

No journal optimization is authorized by this document. A future proposal must first
freeze equivalent workload/contracts and compare old/new representations after every
event, full journal/canonical/provenance export, recovery and all reached allocation
failures. Specify version/migration and retained old evidence, then measure actual
allocations/peak/RSS/throughput on equivalent inputs. Approve only a correctness-
equivalent improvement supported by those measurements. Do not discard accepted
history, retired identities, source receipts or deeper liquidity to reduce memory.

Throughput evidence is batch-scope Release data with two warmups/seven repetitions,
not service/tail latency, a real-ITCH archive result or an exchange SLA. One-byte
inflater microsteps are intentionally conservative. Future batching changes require
corrupt-prefix, exact-limit, chunk-invariance and restart equivalence before timing.
Do not set an arbitrary institutional performance requirement or infer a speedup from
non-equivalent P1G/P1H scopes on a shared host.

## Public claims, licensing and observed-market blockers

The user supplied a NASDAQ representative's statement permitting download/use of the
public EMI samples. The ledger and [NASDAQ_REAL_DATA_PILOT_PLAN.md](NASDAQ_REAL_DATA_PILOT_PLAN.md)
keep that evidence separate from unrestricted redistribution/publication rights,
retention clarification and authorization to acquire a multi-gigabyte archive.
No new observed bytes were acquired during P1G/P1H or this document preparation.
Do not publish raw/row-bearing excerpts, identify a file as fully verified, or claim
real-data initial state because access or HTTP Range worked previously.

A final candidate README/report must state what is present: synthetic-only framing,
source context, bounded two-book reconstruction, bounded single-member streaming,
separate synthetic matching/execution research and the existing Python package.
It must also state what is absent: real-data calibration/reconstruction evidence,
all-market/complete-seed/hot recovery, stable native ABI qualification, hosted/ARM64
success evidence and production live execution. No GIG Quant Terminal change or
integration completion is implied by versioned consumer schemas.

## Prioritized disposition

1. Close any newly reproduced candidate-scope correctness defect first. Preserve the
   qualified source/evidence and verify repairs rather than suppressing failures.
2. Independently restore the scoped candidate and audit its source/evidence contracts;
   reconcile current documentation and obtain actual hosted run evidence when access
   permits. Record any unavailable external checks openly.
3. Complete current dependency/advisory and artifact/license/distribution review for
   any proposed release. Keep unpublished private artifacts private pending explicit
   owner decisions; do not create a release or merge main under this checklist.
4. Advance the separately authorized, resource-verified NASDAQ pilot only after actual
   acquisition/profile/initialization/reference prerequisites are met. If valid state
   or an independent reference is absent, report that blocker instead of fabricating
   a validation success.
5. Defer optional APIs, platform claims, journal redesign and operational infrastructure
   unless a measured need and separate scoped authorization justify them. Do not add
   live trading, broker connectivity or Terminal changes to meet a planning date.

A candidate can remain useful and credible with explicit empirical and platform
limits. Neither November5 nor November12 supplies missing evidence or changes these
truth boundaries. The remaining critical path and implementation authorization are
recorded separately in the progress/phase plans; this document closes no unexecuted
future gate.
