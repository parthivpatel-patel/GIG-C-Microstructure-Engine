# Reproducible event-level differential validation

Build the existing `gig_itch_l3_reference_driver` target with the project's CMake
configuration. Run from repository root:

```sh
python3 scripts/check_adapter_differential.py build/phase9-clean-release/gig_itch_l3_reference_driver
python3 tests/test_adapter_differential.py
ctest --test-dir build/phase9-clean-release -R '^itch.l3_reference$' --output-on-failure
```

The third command retains the original frozen oracle and additionally runs this
byte-adapter supplement and eight diagnostic controls. Test-count/hash assertions
are unchanged. Final executed matrices and private-log hashes are recorded in
`evidence/order_book_validation_results.json`. Raw output is retained under ignored
`build/readiness-program/phase4/`; no restricted data is present.

To prove mismatch detection, use a **new** report path (exclusive create; no overwrite):

```sh
python3 scripts/check_adapter_differential.py build/phase9-clean-release/gig_itch_l3_reference_driver --inject-reference-error --report /tmp/gig-authored-divergence.json
python3 scripts/check_adapter_differential.py build/phase9-clean-release/gig_itch_l3_reference_driver --reproduce /tmp/gig-authored-divergence.json
```

Both deliberately exit1. The independently corrupted expected quantity produces
first divergence at event3/typeA, `.books[0].orders[0][3]`; the four-record prefix is
re-executed and its first differing field confirmed. This is a negative control,
not an engine defect. Actual execution failures retain an unknown index/type and
bounded original fixture rather than inventing an event. Diagnostics identify the
dataset, seed, exact framed-fixture SHA256, expected/actual state, field, synthetic
origin and exact reproduction argv. Prefix reduction re-authenticates supplied
bytes; it is a verified first-diverging prefix, **not globally delta-minimal**.

Harness limits:2MiB fixture/report input,32MiB combined child output enforced at
read boundary,120-second child deadline; cleanup kills/reaps an unfinished child.
The driver adapter mode caps lines/decoded fixture bytes at2MiB, validates scales,
flags/digest, chunks1..65536 and uses a128MiB tracked PMR. Python interpreter/OS RSS
is not certified by that PMR budget. Reports reject duplicate JSON fields, excessive
sizes, inconsistent digest and observed-origin replay. This local synthetic test
utility is not an authenticated publisher or arbitrary-input network service.

Eight unit controls cover report roundtrip, contradictory digest, observed-origin
refusal, oversized/duplicate input, strict summary bool/int types, explicit candidate
execution failure, and no report overwrite. Preserved independent suites cover
resource caps, malformed source, allocation failures and deterministic restarts.

Current use: synthetic fixtures and decoded context inspection only. For future
observed comparisons require authorized privately held artifact, exact profile,
validated complete initial state, independent source accounting and an aligned
independent market reference. The current diagnostic loader refuses observed replay;
its structured format can inform that future work, but it is not yet an observed
harness. No empty book is inferred from timestamps/session messages/file boundary.
