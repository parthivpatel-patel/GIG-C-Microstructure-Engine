# P1F — synthetic source context and event normalization evidence

P1F implements a standalone deterministic source-context and normalization layer.
It does not initialize or mutate a native book, integrate with replay, reconstruct
L3 depth, decompress archives, acquire market data or certify historical exchange
behavior. All tests and measurements use authored synthetic bytes. Existing matcher,
execution, TCA, journal and Python behavior remain unchanged.

## Baseline, interfaces and file inventory

Local and remote feature HEAD initially matched
`1f997e775ea803f5ee54ce71b63cf263fbe769fd`, with a clean working tree on
`feat/bootstrap-cpp20-engine`. Main remained at
`165c5038336887116d69160b0d8e5a1a5ef59d16`.

The verified implementation checkpoint is
`e4aeb76d98087441a7ed33c491173a633e8d7e37`. This report, coverage ledger, machine evidence and the
reproduction-note update form a subsequent documentation commit. Exact final and
remote SHAs are included in the delivery response; no history rewrite or main merge
is authorized or performed.

| File | Added/modified and purpose |
|---|---|
| `include/gig/itch/context.hpp` | New owned context, policy, lifetime/match state, normalized record and structured result APIs |
| `src/itch/context.cpp` | New wire-validated semantic admission, staged atomic commit and explicit completion |
| `CMakeLists.txt` | Separate `gig::itch_context` static target; eight native groups and two reference/control groups |
| `tests/test_itch_context.cpp` | New lifecycle, identity, observation, policy, limits, allocation, numeric and provenance regressions |
| `tests/itch_context_reference_driver.cpp` | New test-only canonical typed output and complete ledger observation |
| `scripts/check_itch_context_reference.py` | Independent Python lifecycle/context/normalization model and negative controls |
| `benchmarks/itch_context_benchmark.cpp` | Correctness-first bounded synthetic lifecycle workload |
| `scripts/check_itch_context_benchmark.py` | Independently packed fixture, fingerprint, count and checksum preflight |
| `benchmarks/CMakeLists.txt` | New standalone benchmark and its correctness test |
| `docs/P1F_CONTEXT_DESIGN.md` | Explicit architecture, source evidence, selected policies and limitations |
| `docs/P1F_VALIDATION_REPORT.md` | This completion report |
| `docs/P1F_COVERAGE.md` | Executed-group coverage and remaining P1D boundaries |
| `docs/P1F_EVIDENCE.json` | Durable source/JUnit/package hashes and actual measurements |
| `docs/REPRODUCIBILITY.md` | Current counts and P1F reproduction commands |

No existing C++/Python implementation or existing test was edited. The P1D designs,
P1E evidence, institutional audit and remediation reports match their starting Git
blobs exactly. New code links to `gig::itch`, not the existing engine library or
Python extension; existing CI discovers its CTest registrations automatically.

## Implemented semantics and classifications

The architecture and official-document hashes are detailed in
[P1F_CONTEXT_DESIGN.md](P1F_CONTEXT_DESIGN.md) and the retained
[P1D source ledger](ITCH_50_VALIDATION_DESIGN.md). The selected ITCH layout is the
retrieved 5.0 document with April 2023 revision history, not a certified 2019 profile.

`SourceContext::create(manifest, policy, resource)` requires explicit source/session
identity and reserves bounded ledgers. `apply(payload, location, provenance)` calls
the validated wire decoder internally, then validates context and emits an owned
`NormalizedRecord`. Forged public `DecodedRecord` values cannot bypass wire validation.
The output preserves raw typed fields, exact padding, header/location/provenance,
source/session manifest, semantic kind, before/after lifetime state, price/printability
observations, integration classification, normalization version **1**, and the
complete selected policy. Missing raw metadata remains missing even when the separate
manifest contains caller assertions. Contradictory source/digest/origin/seed values
reject rather than replacing one identity with another.

| Family | Context and normalization behavior |
|---|---|
| S | Distinct O/S/Q/M/E/C observations; optional strict ordered lifecycle; no implicit reset, market-state coercion or L3 eligibility |
| R | Exact locate/directory identity; identical repeat is an observation; conflicting binding or unavailable blank symbol rejects |
| A/F | Known matching directory; unused eligible displayed reference; positive mutation quantity under the declared local policy; exact side, price, attribution and arrival ordinal retained |
| E | Resolve active identity and reduce exact shares; full execution retires it. Resting-price-derived candidate stays distinct from an observed wire price, which E does not supply |
| C | Reduce displayed remainder, retain actual execution price and Y/N printability; candidate book-decrement units use the resting price. Different observed price explicitly requires a book-only projection |
| X | Subtract positive cancellation delta; underflow rejects. Default rejects full-size X as a partial-cancel anomaly; explicit alternate policy allows it and retires the identity |
| D | Retire known active identity and all its remainder; unknown/inactive identity is not a successful no-op |
| U | Retire old identity, create unused new identity and total quantity/price, inherit stock/side/attribution; new arrival ordinal annotates the source transition without certifying exchange FIFO priority |
| P | Non-displayed print only; no resting order or aggressor inferred from raw reference/side |
| Q | Cross observation, including zero size; no resting orders, auction allocation or book clearing; native integration remains unsupported |
| B | Known eligible E/C/P correction reference; mark broken once, never restore liquidity; unknown, repeated or unsupported Q-origin break rejects explicitly |

Lifetime references include active and retired orders. Reusing a retired reference
within the same declared namespace rejects, including replacement into any previously
used reference. New scope requires an explicit new context/manifest, not an S marker
or eviction of old identities. Replacement chains are retained as source U records
plus typed before/after transitions; there is no persistent chain archive beyond the
bounded lifetime state and caller-retained normalized outputs.

E/C/P/Q generations share a strict bounded match-identity ledger under the selected
synthetic session/day policy. B is a reference/correction, not a new match generation.
This is not a complete corrected trade tape: nonprintable C and later cross quantities
are not aggregated into allegedly verified volume, and historical match exceptions
remain uncertified.

Statuses distinguish accepted source context, source-invalid, context-invalid,
unsupported source, integration-ineligible and resource-limit outcomes. **A valid
context commit can be integration-ineligible**; use `committed()` separately from
integration status. Such outputs retain the full source event rather than forcing
a lossy native conversion. Hypothetical integer tick/lot hints require exact positive
integer divisibility under explicitly selected factors; off-unit values never round.
They are not constructed native domain values or full InstrumentRules validation.

H/h and other message families unsupported by P1E remain explicit unsupported
outcomes, not silently accepted trading-state semantics. There is no skip, implicit
session rollover or automatic recovery API. A caller must stop or explicitly retry
the same logical record after rejection; the synthetic retry tests do not authorize
editing observed source bytes or bypassing missing history.

## Source order, session and initialization limits

Physical frame offsets and local capture ordinals must be exactly adjacent under
the configured first location. No exchange sequence number is invented. Tracking
numbers are preserved per record and may repeat; they are not a continuity oracle.
Raw 48-bit timestamps remain exact. Optional nondecreasing/ordinary-day restrictions
are explicit configuration, not UTC conversion or a universal exchange clock claim.
Ties and regressions are not repaired by sorting.

`finish` distinguishes bounded prefix, unexpected EOF and caller-declared source
completion. `source_complete` is an external container assertion, not independent
verification of a terminator, CRC, artifact hash or upstream exchange completeness.
Only strict ordered O/S/Q/M/E/C plus declared source completion clears
`session_incomplete`; permissive context never certifies that local lifecycle flag.
Callers must not claim declared completion after an unresolved source rejection.
**`initialization_incomplete` always remains true**, including complete local sessions
and manifests annotated `synthetic_history_declared`. No initialization eligibility
algorithm, snapshot installation, healthy-depth publication or observed-data gate
was implemented. Invalid finish enums do not seal the context; valid finish is
idempotent. Moved-from instances reject safely.

## Failure atomicity and independent validation

All directory/order/match lookups, quantity bounds, identity rules, capacity admission
and cursor checks precede the nonallocating commit. Unsigned subtraction occurs only
after comparing the delta against remaining quantity. A failed U cannot retire its
old order; a duplicate/capacity-failed match cannot consume shares. Rejected events
leave accepted state, ledgers and cursors unchanged. Valid integration-ineligible
observations are explicitly committed and are not counted as failed mutations.

Native tests cover both byte-offset and ordinal exhaustion independently, including
valid final records near UINT64_MAX and refusal to wrap. They also cover UINT64_MAX
references/matches, UINT32_MAX shares, Price(4) boundaries, off-unit conversions,
full/partial execution and cancellation, retired reuse, multi-symbol interleaving,
unknown/conflicting locate, inherited attribution, system boundaries, missing and
contradictory provenance, unsupported input, malformed source, invalid finish,
moved-from safety and explicit incomplete history.

The independent model uses Python dictionaries, explicitly packed bytes and
arbitrary-precision integers. It does not import production parsing, containers,
canonical serialization or native book code. A hand-calculated 17-candidate golden
checks reference remainders, retirement, correction state and counts before any
production output is consulted. Every candidate then compares exact reconstructed
wire fields, provenance, all normalization settings/version, normalized values,
complete directory/order/match ledgers and semantic summary after acceptance or
rejection. ABI-dependent reserved bytes are checked separately by native allocation
and benchmark accounting, not copied into a supposed independent semantic oracle.

Per configuration the context oracle executes **515 sessions / 12,104 comparisons**:
12,092 source candidates and 12 finish checks, including **10,000 deterministic
randomized semantic mutations**, seed `0x503146`. They are grammar/lifecycle
mutations, not 10,000 arbitrary corrupt byte strings. Existing P1E adversarial wire
coverage remains active. Four negative controls deliberately use wrong remaining
quantity, retired reuse, liquidity restoration and event alignment expectations;
all four are detected by the real comparator.

All nine configurations produce context canonical SHA256:
`58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e`.
The unchanged P1E 10,000-case oracle still produces:
`142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e`.

Review and testing corrected unsafe next-offset arithmetic, moved-from admission,
E inferred-price labeling, C candidate-price distinction, incomplete-session flags
and missing policy/version provenance. The independent benchmark preflight also
caught a directory-fixture field mismatch; the C++ fixture was corrected to match
independently packed fields. One Python Release incremental object remained stale
while source was being finalized; the new context source was forcibly rebuilt in
all nine configurations and the complete final matrix rerun. No warning suppression,
sanitizer workaround, expectation relaxation or existing-test removal was introduced.

## Final toolchain and package results

Linux x86_64, GCC 14.2, Clang 19.1.7, CMake 3.31.6 and CPython 3.12.14; warnings
are errors. Sanitizer configurations enable ASan and UBSan with nonrecovering checks.

| Configuration | Passed | Failed | Skipped/disabled |
|---|---:|---:|---:|
| GCC Debug | 85/85 | 0 | 0 |
| GCC Release | 85/85 | 0 | 0 |
| GCC ASan/UBSan | 85/85 | 0 | 0 |
| Clang Debug | 85/85 | 0 | 0 |
| Clang Release | 85/85 | 0 | 0 |
| Clang ASan/UBSan | 85/85 | 0 | 0 |
| GCC Python Debug | 88/88 | 0 | 0 |
| GCC Python Release | 88/88 | 0 | 0 |
| GCC Python ASan/UBSan | 89/89 | 0 | 0 |

**775 CTest outcomes**, zero final failures, skips or sanitizer findings. Each native
row preserves 65 original outcomes and all 9 P1E outcomes, adding 11 P1F outcomes.
Existing replay determinism, recovery/atomicity, book, numeric, analytics, matching,
execution/TCA and benchmark fixture/compiler-metadata checks remain active.

Python uses the existing interface/export/schema tests and established live-LSan
harness/control. Its existing late-CPython-finalization limitation remains; no native
leak detection was disabled. Clang Python builds were not run.

A final source archive containing all 10 implementation-checkpoint files exactly
was rebuilt offline into a private 0.1.1 wheel. Installed interface tests pass **7/7**,
export contracts **6/6**, and the research example passes with output byte-identical
to the P1E example. Installed paths identify the separate consumer venv. No Python
API, package version or schema changed, and normalization is not exposed in Python.
No artifact was published.

Hosted Actions remains **unverified**: a current `gh api` request returned
`Forbidden`. Existing workflow registration is not a verified hosted success.
ARM64, Windows/macOS, other Python versions and real-market data remain untested.
Raw final JUnit, logs, package and measurement artifacts remain ignored under
`build/p1f/evidence/`; [P1F_EVIDENCE.json](P1F_EVIDENCE.json) retains durable hashes,
source identity and selected actual measurements.

## Memory and representative synthetic measurements

Exactly three selected PMR vector reservations occur when all ledger caps are
nonzero. Real fail-after injection sweeps each of those allocation sites, verifies
rollback releases earlier allocations, and verifies destruction returns tracked
live bytes to zero. Armed allocation failure after successful creation does not
trigger during valid or rejected admissions: incremental PMR allocation count is
**zero**. Source and decoded/normalized outputs own fixed fields, not borrowed
payload/configuration storage.

Measured ABI sizes agree between GCC and Clang:

| Representation | Bytes |
|---|---:|
| SourceContext object | 800 |
| ContextPolicy | 72 |
| SourceManifest | 488 |
| NormalizedRecord | 1,064 |
| Lifetime OrderState, active or retired | 56 |
| MatchState, including broken entries | 16 |
| DirectoryState | 40 |

Default caps are 64 directories, 4,096 lifetime order references and 4,096 matches;
measured default reservation is **297,472 bytes**. These are ABI measurements, not
portable size guarantees. The 4 MiB configured budget covers logical vector storage,
not object size, allocator metadata, transient over-reservation or process RSS.
Requested size arithmetic is checked before allocation and actual capacities checked
after reserve. A caller-owned bounded PMR supplies a hard allocator governor.

Active and retired references occupy the same bounded lifetime ledger. Retired
references are never evicted to admit new orders; reaching a cap stops before mutation.
An indefinitely long session therefore cannot be processed with this fixed profile.
Any future compact lifetime index or external checkpoint must preserve uniqueness
and source identity and receive separate correctness/benchmark gates.

The following measurements ran sequentially on the shared host from the clean
implementation commit after builds stopped. Each workload uses S/R, then n A,
n X, n U and n E records, two warmups and seven measured repetitions. All orders
finish retired, all match identities remain known, and the independently checked
remainder checksum is 25*n. Timed passes include create/reserve, wire decoding,
normalization, ledger scans, validation and context destruction; fixture generation
is outside. The benchmark records per-pass-average median/minimum, not event-level
service distributions, tail latency or a market-data transport rate.

| Authored orders n | Source records | Reserved ledger bytes | GCC median ns/record | Clang median ns/record |
|---:|---:|---:|---:|---:|
| 32 | 130 | 4,136 | 336.562 | 126.092 |
| 128 | 514 | 16,424 | 465.556 | 210.321 |
| 512 | 2050 | 65,576 | 842.051 | 593.165 |
| 2048 | 8194 | 262,184 | 2434.27 | 2156.3 |

Every run independently verifies its payload fingerprint, record count, checksum and
retired/match counts. Physical reservation stays constant during each run; logical
occupied lifetime state grows to 2*n and match state to n. Canonical fixture identities
and executable/compiler hashes appear in machine evidence. There is no speedup or
institutional throughput/SLA claim. Linear directory/order/match scans and active-count
recalculation make large-profile per-record time grow with retained state; this is a
measured limitation, not a hidden constant-time claim. Whole-child CPU and wait-accounted
RSS are recorded; RSS can include an inherited pre-exec worker floor and is not engine-
only RAM. The process-local ledger proof is separate from full pipeline resource limits.

The existing **15,944-byte journal entry and 100,000-record native journal cap** are
unchanged. No native history is created in these measurements. Context memory bounds
do not solve replay-journal growth or establish feasible full-archive replay.

## Acceptance and recommended P1G gates

P1F acceptance is satisfied for standalone synthetic scope: all 12 families have
explicit normalization/disposition; context identity, lifecycle and bounds are
explicit; mutations are atomic; independent state and negative-control checks pass;
P1E/core regressions remain green; final-source packaging and cross-compiler checks
pass; no protected implementation or market data was changed/acquired.

The original 62-row P1D program is not declared complete. P1F adds context evidence,
but gzip, initialization eligibility, native source-to-event mapping, joint transaction
semantics and observed-data gates remain open. Historical 2019 profiles, real clock/day
namespace, zero/full-X edge policies, match exceptions, licensing/cloud/retention
permissions and independent source-reference availability require further evidence.

Recommended P1G is a separately authorized synthetic initialization-and-projection
phase, with these gates before any observed-input claim:

1. Version an explicit initialization manifest and prove unknown/aggregate/incomplete
   starts cannot publish healthy L3 state; do not treat S/O or local context completeness
   as an empty-book proof.
2. Specify source-context versus native commit positions, rejection accounting and a
   prepare/commit or explicit prefix-stop contract. Current `context.apply` commits
   source state: simply chaining it with a fallible native apply is not a joint atomic
   transaction and cannot be described as one.
3. Map only lossless supported native mutations under explicit InstrumentRules and
   exact rational units; keep C/P/Q/B full semantics external where unsupported.
4. Compare every synthetic step to an independent flat-order/FIFO reference model,
   including identity, remaining size, priority, quantities and first divergence.
5. Inject native/context/resource failure at every reached boundary; require no
   duplicate application, hidden skips, partial replacement or fabricated recovery.
6. Repeat required compiler/sanitizer/Python gates, preserve current oracle hashes,
   and predeclare joint context/book/journal resource caps before scale testing.

Rights and source completeness remain prerequisites for actual market acquisition.
Do not add gzip ingestion, journal optimization, broker connectivity, production
trading or a new dashboard as an incidental P1G task. P1G has not begun.
