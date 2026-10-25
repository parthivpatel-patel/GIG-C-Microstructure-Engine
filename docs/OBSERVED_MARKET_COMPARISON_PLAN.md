# Bounded observed-market comparison readiness

## Implemented offline path and evidence levels

The current executable comparison path is **authored synthetic only**:
initialization manifest -> bounded raw BinaryFile input -> independent framing /
reference expectations -> C++ BinarySourceAdapter -> source context -> native L3 ->
per-event comparison / deterministic refusal / first-divergence reproduction.

1. Authored synthetic fixture agreement tests explicit known input/initial state.
2. Independent Python flat-book reconstruction agreement tests an algorithm distinct
   from production C++ transitions, including seeded state and receipts.
3. Independent observed-market agreement requires actual authorized observations,
   authenticated complete initialization and an independently aligned reference.
   **Level3 is blocked and is not implied by levels1/2.** Same-session independent
   implementation is not third-party verification or exchange certification.

C++ BinarySourceAdapter::create_seeded is additive and requires typed SeedState plus
separately retained trusted fixture digest, authored_synthetic_seed claim, matching
source/context config and synthetic origin. No borrowed seed span is retained.
Observed-origin declarations remain context-only or explicitly refused; no actual
observed seed factory is implemented. Existing empty path and eight hashes remain.

## Working bounded CLI and demonstration

```sh
python3 scripts/demo_bounded_comparison.py build/phase9-clean-release/gig_itch_l3_reference_driver /tmp/gig-authored-comparison-new
python3 tests/test_bounded_comparison.py build/phase9-clean-release/gig_itch_l3_reference_driver
```

Use a new output directory; existing demonstration directories are not overwritten.
The demo records exact commands and expected exit codes for complete/seeded state,
unknown state, corrupt seed, missing events, duplicate/unknown orders, unsupported
source, memory exhaustion, intentionally wrong reference and reproduction. It
creates only authored data and does not access any external dataset or network.

Direct CLI: run_bounded_comparison.py MANIFEST RAW --driver DRIVER
--trusted-source-sha256 HEX [--trusted-snapshot-sha256 HEX]. A manifest alone cannot
provide its own independent trust. Without supported positive initialization,
report initialization_blocked and do not read input or start candidate execution.
Observed origin never passes this fixture runner. Fixture symbols/native IDs and
provider are explicitly scoped to the two authored bindings; no silent remapping.
Missing seed timestamp/stage unsupported by this test-driver protocol is explicitly
refused rather than invented (the underlying typed engine supports optional time
where policy permits). No gzip/archive acquisition is added.

Limits are configurable within validated ceilings: input1MiB default/2MiB maximum,
records/events512 default/1024 maximum, candidate PMR4096..128MiB,120-second maximum
child deadline,32MiB combined child output,1MiB manifest/report,32768 reference
order-state cells and two instruments. Error count is explicitly stop-at-first1;
no continue/skip option. Candidate line/protocol input is additionally2MiB bounded.
CLI memory control is a PMR allocation governor, not process RSS or ASan virtual
address-space cap. Input/model/output sizes are separately bounded; sanitizer
shadow-memory requirements are not suppressed. Partial subprocess output is never
accepted as a completed result. A real sleeping-child deadline control kills/reaps
it. Resource errors produce explicit incomplete/unknown accepted-count diagnostics.

Integrity is checked before native execution. Complete independent BinaryFile
framing must consume every byte/terminal; no malformed/truncated frame is skipped.
Event-level context/native refusal stops at that record and reports examined,
accepted/rejected and unprocessed tail counts. Local ordinal adjacency cannot prove
upstream exchange sequence completeness; missing upstream sequence is null, not0.

## Comparison metrics and divergences

Report source count, accepted/rejected counts and reasons, unsupported count,
acceptance ratio, initialization scope, final-state agreement, first differing
field and book metrics. First divergent state compares order identities/quantities,
levels and best bid/ask; later differences are not exhaustively enumerated. When
state cannot be compared, metrics stay unknown/null. No observed accuracy statistic
is generated. Source gaps are detected only where independently supplied integrity /
boundary evidence establishes them; removing a record and rehashing a declared
capture does not magically establish exchange completeness.

`--inject-reference-error --report NEW.json` deliberately exits3/divergence.
The report contains dataset, original source hash, retained artifact hash, complete
initialization manifest, index/type, expected/actual state, first field and exact
reproduction argv. `--reproduce REPORT` reexecutes that command's authored fixture;
observed-origin payload export/replay is refused. A verified first-diverging prefix
is retained where it reproduces the same field, with original parent hash explicit;
it is a newly derived authored reproduction, not the unchanged original capture
or a globally delta-minimal fixture. Report writes are exclusive, not overwrite.
Absolute script path makes the stored command work outside the repository root.

## External observed-data gate

See REAL_DATA_ACCEPTANCE_CRITERIA.md. No actual data is acquired in this program.
Before empirical work, independently verify a complete source start or complete
order/context/FIFO seed, exchange-specific dated profile and independent observed
reference, plus licensing/private retention/resource authorization. The current
synthetic driver is not a general observed-data CLI; its fixture provider/dataset
namespace and authored seed boundaries must never be relabelled observed. Future
integration must explicitly implement and independently test observed evidence
verification/projection. Format-only historical prefix results do not clear it.
