# P1J independent engineering audit

Reviewed October23,2026, America/New_York. P1I was completed, pushed and remotely
verified at `5584ce34de5b839d2a78fabcd8e6603cec1185f3` before this audit began.
Its implementation/measurement source is `5ff7c8596f8705d92b7d97f55f860d0cb8d409fb`.
Main remains `165c5038336887116d69160b0d8e5a1a5ef59d16`.

Status: **P1J audit and local post-repair qualification complete**. Verified repair
remote: `92567f15183074647e14af3dde4604ed5ba095c7`. Final documentation delivery
is recorded in the completion response. No release or observed-market claim.

## Executive decision and independence

The project supplies a substantive bounded synthetic research engine, not merely
scaffolding. P1I now demonstrates the complete authored gzip→framing→decode→context→
L3→versioned validation-output chain, including intentionally incomplete, restarted
and corrupt inputs. Exact types/rationals, prepared transactions, real allocator
faults, explicit unknown states, source accounting and independent wrong-model
controls are credible engineering evidence. No firm's proprietary architecture,
performance target, internal rubric or hiring guarantee is assumed.

Separate review agents inspected actual C++/protocol/memory paths, evidence/packages/
benchmarks, and dependencies/security; the integrating reviewer separately inspected
financial/causal paths and ran an independent numerical experiment. Reviewers share
the same machine/repository and tool substrate: this is algorithmic and review-pass
separation, not organizational independence or a clean-machine certification. Earlier
reports supplied context; their claims were checked against source and raw artifacts.

No new critical/high synthetic engine defect was reproduced. Two medium evidence-tool
issues were reproduced and repaired during P1J; the two P1I CLI/encoding issues had
already been repaired. Their severity, exact references and before/after acceptance
are in [the evidence audit](P1J_EVIDENCE_REPRO_AUDIT.md) and
[findings register](P1J_FINDINGS.md). Deliberately excluded observed/production
capabilities are not mislabeled current engine defects. Bounded testing is not proof
that no other defect exists.

**Decision:** scoped private synthetic evaluation is defensible. Formal release-
candidate closure remains conditional on independent restoration, native/platform
advisory applicability, hosted CI evidence and owner distribution decisions. Public
release, observed-market correctness and production trading remain NO-GO. See the
[complete RC01–RC27 matrix](P1J_RELEASE_CANDIDATE_MATRIX.md), including open gates.

## Source and independently executed evidence

- [C++/protocol audit](P1J_CPP_PROTOCOL_AUDIT.md): actual decoder/lifecycle/FIFO,
  identity/units, prepared→native→nofail commit, zlib C ABI/lifetime, physical versus
  logical prefix, CRC/EOF/publication and restart code inspected. New24,000
  arbitrary-precision Fraction/native conversion cases:2,475 accepted and21,525
  rejected, zero mismatches. Reached allocation and lifetime tests independently
  traced, not accepted from prose alone.
- [Evidence/reproduction audit](P1J_EVIDENCE_REPRO_AUDIT.md): original G/H/I source
  blobs, raw files/artifacts/JUnit counts rehashed; source archive, wheel notice,
  actual import paths, new venv consumers, source/probe arithmetic and benchmark
  samples reviewed. Sparse source coverage and contradictory duplicated measurements
  accepted by the old tool were reproduced before minimal guarded repairs.
- [Security/dependency review](P1J_SECURITY_DEPENDENCY_REVIEW.md):12 actual current
  PyPI version/advisory responses, exact installed pins and cached wheel registry
  digests matched; no returned active advisories. Three official upstream GitHub
  advisory pages gave empty published-advisory lists. Those bounded feeds do not
  establish comprehensive security clearance; no upgrades or market requests occurred.
- Integrating review:1,000 newly authored two-quote/one-trade inputs, seed20261023,
  compared9 exact metrics each against Python integer/Fraction calculations via the
  public native flow interface. **9,000 comparisons, zero mismatches** for OFI,
  intensity, causal quote-based signs, simple-return variance, effective/realized
  spread and impact decomposition. Probe/output hashes retained in final evidence.
  This validates arithmetic under fixture assumptions, not true exchange aggressor
  side, treatment-effect identification, profitable alpha or empirical calibration.

`src/analytics/flow_metrics.cpp:15–22,65–145` requires ordered, clock/scoped/as-of
observations, strict prior source prefixes for trade quote inference and completed
horizons before realized metrics. Quote age/continuity/sampling flags are caller
contracts, not independently measured data quality. The final volatility square root
is approximate long double; underlying returns/variance/spread are exact rationals.
`src/execution/execution.cpp` preserves forecast availability/oracle distinction and
exact fill/TCA accounting; synthetic queue/latency/fee/impact assumptions remain
research models. Source/reference acquisition and statistical out-of-sample evaluation
are prerequisites to empirical claims. No terminal or broker interface was changed.

## Post-audit repair and final regression

Repair source/verified remote:
`92567f15183074647e14af3dde4604ed5ba095c7`. Final136-file source-manifest SHA256:
`ed8acdd4a67603820adff2755b13e4ba42f7b527652917af0f7ed48d3ab27cbe`.
Only the offline verifier and its regression tests changed after P1I; native engine,
matching/execution/TCA/journal/Python code, schemas and source contracts are unchanged.
Two medium repairs are covered by failing-before counterexamples and47 final verifier
unit cases, including typed numeric duplicate checks. No critical/high defect remained
reproduced within the declared synthetic scope.

| Post-repair final configuration | Passed | Failures / skips / disabled |
|---|---:|---:|
| GCC Debug / Release / ASan+UBSan |122/122 each|0 /0 /0|
| Clang Debug / Release / ASan+UBSan |122/122 each|0 /0 /0|
| Python Debug / Release |125/125 each|0 /0 /0|
| Python ASan+UBSan |126/126|0 /0 /0|

**1,108 actual final CTest outcomes**, zero failures/skips/disabled outcomes or
observed sanitizer findings. A new offline source archive, containing all136 frozen
files, independently configured/built in a separate same-host native tree and passed
**122/122**. New direct/source-built private wheels each pass7 interface+6 export
cases and the canonical research example. The independent reviewer also restored a
fresh installed consumer with PYTHONPATH unset and passed13 cases. Native leak checks
remain enabled; the preexisting Python live-LSan/late-finalization limitation remains
explicit. No stronger platform/ABI/security qualification is implied.

All five P1E/P1F/P1G/P1H/P1I semantic hashes agree across all final configurations.
The P1I semantic hash remains
`4ebdd734b5f11e368be1525f95a93070893ec14e9caafb161583807c88d23520`.
Final qualification records live under build/p1j-validation, preserving the original
P1I source/log/artifact evidence unchanged. The offline verifier passes136 source
blobs,50 qualification raw files,three package artifacts and all nine JUnit documents;
61 separately indexed review artifacts are independently hashed by the integrating
reviewer. See [P1J_EVIDENCE.json](P1J_EVIDENCE.json). Mutable installed venv/cache files
are excluded from the retained review manifest; actual install logs/paths and wheel
hashes remain. Hash consistency is not execution attestation or publisher identity.

P1I measurements remain applicable: all four measured native executables are
byte-identical after the Python-only verifier repairs. Source5ff7c85's original
sequential Release results are reused with that explicit equivalence evidence,
not presented as new timings: max PMR77,281,358 bytes, max selected native RSS
76,070,912 bytes; GCC/Clang medians15,386.6/13,890.6 ns per source record for the
n128 stored-block fixture, two warmups/seven samples. Query/journal/cap arithmetic
was independently reproduced. See P1I report for scope and all PMR/process exclusions.

## Readiness, remaining blockers and critical path

All27 RC gates are evaluated: **18 PASS,6 BLOCKED,2 NOT RUN,1 OUT OF SCOPE**.
No failing current scoped gate is concealed as unavailable. BLOCKED gates are
RC13 independent fresh-machine bootstrap, RC16 comprehensive native/platform advisory
applicability, RC17 hosted run evidence, RC21 distribution authorization, RC24 observed
initial state and RC25 observed reference. RC18 platform expansion and RC23 actual
historical inventory are NOT RUN; production operations RC27 are OUT OF SCOPE.

Hosted request for exact P1I candidate5584ce3 returned exit1 `Forbidden`, with no
usable Actions conclusion. This is not evidence of hosted success or failure, and no
HTTP status is invented from the CLI message. Actual Ubuntu zlib resolution still
needs runner evidence; local Debian success cannot establish it. No retry of LOBSTER,
cloud configuration change or circumvention occurred.

There are13 calendar days from October23 to November5 and20 to November12. Local
synthetic implementation/independent review is complete within this target window.
Formal release-candidate closure remains conditional, and no empirical or production
delivery date is defensible without the missing evidence. First close accessible CI,
current native advisory applicability and independent restoration gaps while retaining
private artifacts. A later **separately authorized format-only NASDAQ prefix pilot**
is the smallest observed-data step, not direct synthetic-factory L3 replay. The
[updated pilot plan](NASDAQ_REAL_DATA_PILOT_PLAN.md) preserves byte/time/disk/memory,
profile/initialization/reference/retention/redistribution gates. No sample was acquired.

Defer journal redesign, extra APIs/platform claims, dashboards and production ops
unless a separately scoped measured need exists. Do not add broker/live/Terminal
integration, purchases, main merge or publication to meet a date. The next owner
decision is review of this audit and authorization of a narrowly bounded follow-up;
this assignment stops after verified documentation delivery.

## Complete assignment changed-file inventory

Relative to the verified starting feature commit f3869b2; A=added, M=modified.
Private build/probe/package artifacts are separately indexed, not committed.

```text
M	CMakeLists.txt
M	benchmarks/CMakeLists.txt
A	benchmarks/itch_profile_probe.cpp
M	docs/NASDAQ_REAL_DATA_PILOT_PLAN.md
M	docs/OVERNIGHT_ENGINEERING_PROGRESS.md
A	docs/P1I_BOUNDARY_REVIEW.md
A	docs/P1I_EVIDENCE.json
A	docs/P1I_VALIDATION_REPORT.md
A	docs/P1J_CPP_PROTOCOL_AUDIT.md
A	docs/P1J_EVIDENCE.json
A	docs/P1J_EVIDENCE_REPRO_AUDIT.md
A	docs/P1J_FINDINGS.md
A	docs/P1J_INDEPENDENT_AUDIT_REPORT.md
A	docs/P1J_RELEASE_CANDIDATE_MATRIX.md
A	docs/P1J_SECURITY_DEPENDENCY_REVIEW.md
M	docs/REPRODUCIBILITY.md
A	docs/schemas/itch_validation_output.schema.json
A	examples/itch_validation_demo.cpp
A	scripts/check_itch_profile_probe.py
A	scripts/check_itch_validation_demo.py
A	scripts/check_validation_evidence.py
A	tests/test_itch_query_failures.cpp
A	tests/test_validation_evidence.py
```
