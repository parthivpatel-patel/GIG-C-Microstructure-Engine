# P1G-to-release backlog and critical path (planning only)

Planning date: October 22, 2026, America/New_York. P1F is remotely verified at
`d0b45b4003d0edbb0477de165e5db7e8cdb648c0`; its implementation is
`e4aeb76d98087441a7ed33c491173a633e8d7e37`. All dates below are conditional planning
windows, not completed work or guarantees. November 5 is 14 calendar days away;
November 12 is 21. Neither date overrides evidence, licensing or authorization gates.

**Immediate gate:** P1G production implementation has not been authorized. These
packages can proceed technically without NASDAQ licensing or LOBSTER access, but
implementation still requires explicit authorization. No data purchase, release,
deployment, broker integration or GIG Quant Terminal change is included.

Effort is relative engineering complexity: S=localized addition, M=several coordinated
interfaces/tests, L=cross-layer lifecycle/failure work, XL=uncertain research or broad
capability. These are not promises of calendar duration. Proposed file names and
package IDs are planning artifacts, not an assertion those files/APIs exist today.

## A. Synthetic work without external market-data blockers

| Priority / package | Files and interfaces affected | Required implementation | Independent oracle and acceptance | Dependencies / explicit blockers | Memory/performance risks | Effort |
|---|---|---|---|---|---|---|
| P0 A01 initialization/contracts | Proposed `include/gig/itch/reconstruction.hpp`; `docs/P1G_ARCHITECTURE_PLAN.md`; fixture manifests | Typed eligibility, scope/rules/fixture evidence, dispositions and bounded config; unknown start cannot expose healthy book | Literal manifest truth; G01–G03; zero eligible output for O-only/aggregate/missing history | P1G authorization; no external data needed | Oversized binding/manifest/snapshot representations; avoid fake hot restore | M |
| P0 A02 independent L3 truth | Proposed `scripts/check_itch_l3_reference.py`, reference driver and `fixtures/itch/*` | Independent byte/context/Fraction/flat-book/priority/ledger model; hand traces before production projection | Exact every-step membership/FIFO/ledger/metadata; bad oracle controls fail; G04–G18,G30 | A01 contracts; can run in parallel with A03; requires genuinely separate calculations | Oracle expected-output/history growth must be capped; not production container reuse | L |
| P0 A03 context preparation | `include/gig/itch/context.hpp`, `src/itch/context.cpp`; proposed `tests/test_itch_context_prepare.cpp` | Add owned prepared delta/owner-generation guard and adapter-private nofail commit; existing apply delegates same contract | Preserve P1F/P1E hashes and old outcomes; real allocation/stale/move tests G20–G23 | A01, independent test review; no current prepare API exists | Token lifetime, hidden reallocations and copy overhead; no full-context/book clone per event | L |
| P0 A04 metadata/exact units | Proposed reconstruction.cpp/helpers and tests; existing numeric APIs reused | Truthful native metadata, generated fixture policy reference/seed/parents, checked rational tick/lot and strong domain types; raw TOD stays external | Python Fraction and independent metadata expectations; G15–G18; off-unit/overflow blocks before commit | A01/A02; declared synthetic fixture/rule manifest; no NASDAQ license assumption | Token/lineage bounds, overflow intermediates; no float shortcut | M |
| P0 A05 one-book projection | Proposed reconstruction.hpp/cpp, `tests/test_itch_reconstruction.cpp`, CMake new target | A/F/E/X/D/U route, explicit C book-only option, all observation dispositions; coordinated source/native receipt commit | G04–G11,G19–G24; zero state divergence and zero duplicate application after failures | A02–A04; proof of nofail final commit mandatory | Journal reservation and book staging peaks; context/native split-commit hazard | L |
| P0 A06 two-symbol isolation | Proposed adapter bounded registry/receipts and multisymbol fixtures | Separate preconfigured ReplayEngine per book; one context namespace; per-book derived sequences; explicit other scope | G12–G14,G18; every unrelated book unchanged; global duplicate reference rejected | A05; no all-market router or global atomic fan-out needed | Two journals multiply retained history; avoid journaling every external observation into both | M |
| P0 A07 restart/accounting | Proposed checkpoint descriptor/driver, source receipt trace and tests | Authenticated restart from authored beginning; disjoint source accounting; pending versus committed positions; output-incomplete reporting | G23–G29; exact replayed prefixes/state hashes; reject changed source/config and false snapshot restore | A05/A06; complete-seed/hot restore explicitly deferred | Receipt retention/I/O errors; export may allocate after state commit; no blind reapply | M |
| P0 A08 adversarial/fault matrix | New reconstruction tests/oracle cases; existing TrackedResource; CMake/CTest | Exhaustive reached-allocation failure sweeps, cap/cap+1, malformed sources, crossing, replay recovery diagnostics and 10k bounded candidates | G19–G32 plus unchanged775 baseline outcomes; final actual counts generated, no skips | A02–A07; sanitizer/toolchain availability; preserve all old assertions | Deterministic memory stops vs kills; resource diagnostics not semantic rollback | L |
| P1 A09 correctness-first baseline | Proposed reconstruction benchmark/checker; existing measurement worker and build metadata | Fixed seed/manifest, two warmups and raw batch/service scope, retained-state/journal growth and CPU/RSS | G33; independent checksum/fixture plus full correctness before timing; no fixed institutional throughput target | A08 passing; clean verified implementation commit | Linear context scans and15,944-byte journal entries; no journal optimization in this package | M |
| P1 A10 reproducible candidate | Existing CMake/CI/packaging paths; proposed P1G reports/demo manifest | Full matrix, clean source-archive/wheel consumer, deterministic standalone synthetic demo, exact file/commit inventory | Same non-timing output across builds and restored source package; all required local gates green | A08/A09; hosted CI access unresolved and explicitly recorded, not silently passed | ABI/toolchain drift, stale incremental builds, package omissions | M |
| P1 A11 candidate review/security | Proposed release-readiness record; dependency lock/notices; artifact verifier | Source/data boundary audit, dependency/toolchain inventory, input-limit review, private artifact hashes and known limitations | Read-only source/artifact review; secrets/raw-data absence; actual advisory/toolchain evidence only | A10; publication/license/version policy requires owner decision; no release publication authorized | Advisory access may be unavailable; pinned versions are not a universal security guarantee | S–M |
| P2 A12 synthetic container hardening | Proposed bounded byte/gzip reader and tests; selected vetted dependency; docs | After separate scope authorization, gzip framing/CRC/truncation/expansion/member-policy tests on synthetic data only | Independent compression/decompression tools and Z01–Z05 cases; no archive acquisition | Outside P1G minimum; dependency/RFC review first; not blocked by market licensing | Decompression bombs, optional-field buffering, new dependency surface | L |
| P2 A13 optional research interface | Proposed new separately versioned Python facade/export schemas, not Terminal | Only if justified after C++ candidate: expose immutable synthetic reconstruction evidence with complete provenance | Independent installed-consumer schema/export tests, no implied execution interface | A10; separate API/version review; omit from deadline critical path | Copy/ABI/packaging cost and accidentally exposing partial/ineligible state | M–L |

No package may optimize the existing journal incidentally. A later storage/index
optimization needs a separate correctness-equivalent benchmark proposal, explicit
scope authorization and retained baseline. Likewise native snapshot expansion,
crash recovery, ARM64 qualification and native time-domain expansion are separate
capability decisions, not ways to hide a failed minimum integration.

## B. Real-market work gated on external evidence

| Priority / package | Files and interfaces affected | Required work | Independent oracle and acceptance | Dependencies / explicit blockers | Memory/performance risks | Effort |
|---|---|---|---|---|---|---|
| B01 rights/access ledger | Existing `docs/REAL_MARKET_DATA_ACCESS.md`, sample assessment; no engine code | Obtain written private evaluation/cloud/retention/publication scope; verify exact official artifact and access | Official correspondence/terms and source hashes; clear GO/NO-GO conditions | NASDAQ response pending; acquisition separately authorized only after rights; LOBSTER support independent | Retention/redistribution restrictions and large files; no purchase | External / uncertain |
| B02 dated profile and inventory | Proposed dated schema/context profile and private inventory manifest | After B01, bounded official sample inspection, true format/types/date/namespace/order completeness/initial boundary | Official spec revision plus independently parsed bytes/hashes; no inferred empty book | Rights and actual allowed access; EMI prior accessibility is not rights; no new bytes in this planning phase | Multi-GB gzip prefix may not reach orders or valid start; capped scan can be inconclusive | M–XL |
| B03 observed initial-state evidence | Proposed initialization evidence record; possible separate complete-context seed capability | Establish full empty boundary+complete history or genuine complete L3 state including required context | Independent membership/priority/history proof; reject aggregate/bounded snapshots or absent retired/match context | B02; initial state may simply be unavailable; >64 native snapshot orders is a capability blocker | Full-day identity state and snapshot size; cannot append 64-order recoveries | XL / uncertain |
| B04 independent source reference | Proposed private reference parser/alignment manifest; validation report | Identify legally usable source-provided reference, freeze timing/row alignment, exact eligible-depth comparison | Nonzero eligible coverage, every attempted row accounted, exact mismatch reproduction; internal model agreement is not external reference success | B01–B03; independently supplied snapshots may not exist | Reference storage/precision/depth mismatch; deeper unknown liquidity is not zero | L / uncertain |
| B05 permitted bounded pilot | Proposed offline acquisition/streaming harness using A12, adapter and private report | Only after separate authorization, run exact declared source/context/native caps and dispositions | Zero independent eligible mismatches, authenticated artifacts and complete stop/tail accounting; honest incomplete scope | A10/A12, B01–B04; historical semantics unresolved block unsupported segments | Journal/lifetime caps can stop before useful market coverage; do not silently drop depth/events | L |
| B06 empirical research/calibration | Later research notebooks/reports and model interfaces | Assess observed-data coverage, clocks, trade interpretation, statistical leakage and queue/latency assumptions | Independent references, preregistered held-out checks/sensitivity; no synthetic simulation mistaken for observed execution | B05, suitable datasets/permissions; no production-trading authorization | Look-ahead selection, selection bias, nonidentifiable hidden liquidity | XL / uncertain |

LOBSTER CONNECT403 / Support Case #17931099 is not a dependency for any A package
or an officially reachable NASDAQ path. Conversely, resolving that support case does
not grant NASDAQ use rights or establish a valid L3 start. No multi-gigabyte download,
mirror workaround or paid service is proposed as an unblocker.

## C. Definition of candidate versus release

A **private synthetic research candidate** can be technically ready after A01–A11:
faithful scoped semantics, independent stepwise evidence, bounded resource/failure
behavior, reproducible package/demo and explicit limitations. It is not production
trading readiness or empirical NASDAQ validation. Candidate readiness does not
require B01–B06 to be relabeled passed.

A **real-data research validation milestone** additionally needs the applicable B
rights/source/initial-state/reference/pilot gates. If an independent reference is
unavailable, report model/differential validation only and keep that gate unverified.

Any actual release publication needs explicit owner authorization, version/license/
distribution and artifact decisions plus the relevant validated scope. No merger,
release command, signing purchase or deployment is authorized by this backlog.
Production/operational trading qualification is a separate program and cannot be
inferred from a research candidate or a firm-name comparison.

## D. Critical path against November 5 and November 12

Dates use America/New_York. Assumptions: prompt P1G authorization, usable current
Linux toolchains/resources, an independent oracle maintained alongside implementation,
and no newly reproduced engine defect requiring a separate correctness repair. This
is a capacity-sensitive plan, not a verified effort forecast. Reassess after the
prepare/commit proof and first end-to-end golden pass; those are the highest-risk
unknowns. Do not add real-data dependencies to the synthetic critical path.

| Conditional window | Exit evidence / work |
|---|---|
| Oct 22 | P1F pushed/verified; P1G source-level design, validation matrix and backlog completed; implementation not begun |
| Oct 23–26 | A01 contracts/initialization and A02 oracle in parallel with A03 prepare/commit; A04 complete metadata and exact-unit boundary; demonstrate failure-atomic golden before widening scope |
| Oct 27–29 | A05 one-book integration then A06 two-symbol routing; explicit C/P/Q/B boundaries, provenance receipts and no-change regressions |
| Oct 30–Nov 2 | A07 restart/accounting plus A08 adversarial/failure/cap matrix; resolve all first divergences and freeze synthetic semantics |
| Nov 3–5 | A09 baseline, A10 clean matrix/package/demo, A11 independent readiness review; target a scoped private synthetic candidate if every gate passes |
| Nov 6–12 contingency | Repair discovered correctness/packaging/toolchain failures, rerun affected/final gates and finalize evidence. Defer optional A12/A13 and unneeded optimizations rather than weakening gates |

**Current critical path:** implementation authorization -> prepared-context commit
proof + independent oracle -> exact metadata/projection -> multisymbol/fault/restart
acceptance -> final compiler/package evidence -> candidate review. External B packages
may progress administratively in parallel, but their completion date is unknown.

If authorization/resources or proof-of-atomicity slips, revise scope/date openly.
The November 12 planning ceiling cannot make unavailable licensing, initial state,
reference data, hosted CI or ARM64 evidence appear complete. A valid outcome is a
verified synthetic candidate plus a clearly blocked empirical milestone. Do not
promise a full real-market or production release by either date on current evidence.
