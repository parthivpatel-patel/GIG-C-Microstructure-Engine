# P1I end-to-end synthetic validation

Starting feature checkpoint: `f3869b2e3c5b0ad4003f974499b78e265d5f820e`,
`feat/bootstrap-cpp20-engine`; local/remote equality and initially clean tree verified.
Main remains `165c5038336887116d69160b0d8e5a1a5ef59d16`.

Status: final local correctness/package/source-restoration gates passed; sequential
Release measurements and evidence delivery pending. No P1J execution yet.
This report is completed only when actual final results and implementation identity
are recorded below. No NASDAQ/LOBSTER bytes were acquired; no observed initialization,
market-reference comparison, production readiness, release or main merge is claimed.

## I01–I07 implementation and boundaries

| Package | Concrete implementation and independent check |
|---|---|
| I01 | `scripts/check_validation_evidence.py`: bounded local source/log/JUnit/artifact verification; exact historical Git blobs or explicit current-tree mode; optional mandatory nine-configuration/P1E–H coverage profile. `tests/test_validation_evidence.py` contains39 adversarial unit cases. |
| I02 | `examples/itch_validation_demo.cpp`: four offline native scenarios, valid/bounded/restart/corrupt, through the actual gzip/framer/decoder/context/native L3 APIs. Independent Python byte/flat-map oracle in `scripts/check_itch_validation_demo.py`; no new ingestion framework. |
| I03 | Native-only version1 JSON output and `docs/schemas/itch_validation_output.schema.json`. Exact source identities, configured units/budgets, source/native receipts, active/retired lifecycle, native membership/FIFO/levels/ledger, missing metadata and separate integrity/completeness flags. No existing Python schema/API/version change. |
| I04 | [Boundary review](P1I_BOUNDARY_REVIEW.md), additional72 independent pause/late-CRC scenarios and maintained `tests/test_itch_query_failures.cpp`: every reached22 checkpoint/canonical and2 depth allocation sites; failed queries preserve accepted/native/context/receipt/hash state and exact retry. Existing transaction/fault suites retained. |
| I05 | `benchmarks/itch_profile_probe.cpp` and independent checker: declared128-live-order/two-book profile, retained1024 journals per book, coexisting queries and isolated restart, hard PMR/journal caps and reached query faults. No journal redesign or hidden cap enlargement. |
| I06 | Final compiler/Python matrix, offline direct/source-built wheels and clean source-archive native reproduction described below. This is same-host clean-source restoration, not a fresh VM or platform qualification. |
| I07 | Frozen-source manifest, raw evidence inventory, explicit limitations and reproducible handoff for the separately gated P1J audit. No unresolved critical/high correctness defect was identified in the declared synthetic scope by the P1I review; this is bounded evidence, not exhaustive proof. |

## Output and source identity contract

The authored fixture contains18 records,507 BinaryFile bytes and530 stored-block
gzip bytes. It intentionally includes two symbols, same-price priority, partial
execution/cancellation, delete/replace, hidden print, cross and correction observations,
and system observations. Expected values are independently computed with Python
struct/integer framing, CRC and flat maps; production output is never the golden oracle.

| Scenario | Accepted / native / external | Required output |
|---|---|---|
| valid |18 /7 /11| Actual EOF, gzip/raw/compressed identities and terminal framing agree; complete publication eligible. |
| bounded |8 /5 /3| Explicit accepted prefix, paused/bounded/incomplete; no full-source publication. |
| restart |18 /7 /11 after restart boundary8| Fresh byte0 replay under a different chunk schedule, exact checkpoint/prefix/native equivalence, then independently verified full completion. Original and restarted state coexist inside the declared shared governor. |
| corrupt |18 /7 /11 provisional| Altered CRC, fatal gzip corruption, no complete publication even though all logical records were accepted provisionally. |

The caller supplies an independently measured implementation digest; the output marks
it `caller_declared`. It is not an auto-authenticated Git identity, MAC or signature.
Final demonstration evidence supplies the frozen-source-manifest SHA256 and binds it
to the implementation commit. Semantic canonicalization excludes only allocator
measurements and caller code identity, not source identities, state or completeness.
Restart always replays byte0; no compressed seeking or durable hot recovery is claimed.

The output is assembled and size-checked before stdout, and a failed sink returns
nonzero. This does not make redirected files crash-atomic: downstream tools must check
exit status, parse/schema/semantic validation and integrity before publishing results.
Fixed objects, fixture generation and JSON buffers are outside the PMR governor and
are included only indirectly in process RSS; output size is capped128KiB.

## Reproduced defect and smallest repair

**Medium; fixed — new-demo invalid implementation digest.** `gig::Digest` is a
bounded generic printable token, not itself a64-hex validator. The original demo
accepted short/nonhex/uppercase input; printable quotes could produce malformed JSON
because the CLI value was inserted into a quoted field. This affected the new demo,
not existing engine validation. Both the independent reviewer and root reproduced it.

Before constructing state/output, the CLI now requires exactly64 lowercase hexadecimal
characters. Permanent oracle CLI controls failed against the original executable and
pass after repair; malformed identities produce empty stdout/nonzero status. The
`/dev/full` control returns exit3 for a failed sink. Before/after command results,
source/executable identities and regression logs are retained in the evidence inventory.
No unrelated core change or assertion/sanitizer suppression was used.

**Medium; fixed — evidence-verifier encoding bypass.** The initial verifier
searched raw ASCII XML bytes for DTD/entity declarations. Independently constructed
UTF-16 XML passed that filter and was parsed, contradicting the no-entity contract.
The new regression failed on all three UTF-16 encoding variants against the original
script. The minimal repair decodes UTF-8 first, rejects NUL-bearing/other encodings,
then checks declarations before parsing. UTF-16 and UTF-32 variants now reject;
all39 adversarial cases pass. CTest JUnit is UTF-8. This is input-boundary hardening,
not evidence of remote-code execution or a production engine defect. The source freeze
was invalidated and final validation/package reproduction was repeated for this repair.

Independent oracle development also corrected its own authored directory-byte,
side/receipt and derived-count expectations. Those were test-author errors resolved
from field widths and public contracts, not reported as engine defects or accepted
by replacing a golden hash with production output.

## Final executed evidence

Linux x86_64; GCC14.2.0, Clang19.1.7 with the system GCC standard library,
CMake3.31.6, CPython3.12.14 and system zlib1.3.1. The final136-file source manifest
is `79c2defcfa3c5c02c31d9cff314bc9246e34f16cc671d3bd66f96ba13074e4c6`.
All final rows explicitly enable streaming; warnings remain errors and sanitizers
are nonrecovering. The earlier pre-hardening runs are not the final qualification.

| Final configuration | Passed | Failures / skips / disabled |
|---|---:|---:|
| GCC Debug / Release / ASan+UBSan |122/122 each|0 /0 /0|
| Clang Debug / Release / ASan+UBSan |122/122 each|0 /0 /0|
| Python Debug / Release |125/125 each|0 /0 /0|
| Python ASan+UBSan |126/126|0 /0 /0|

**1,108 final CTest outcomes**, zero failures/skips/disabled outcomes and no observed
sanitizer findings. The evidence unit executable runs39 internal tests. New query
regression reaches22 checkpoint/canonical and2 depth allocation failures. New E2E
oracle runs four modes twice, rejects17 corrupted expected contracts and passes10
CLI/sink controls. Structural schema checks independently pass four outputs and
reject eight invalid structures. These different counting units are not summed as
if they were distinct CTest cases.

Every final configuration preserves P1E/P1F/P1G/P1H canonical identities from the
P1H report. P1I semantic SHA256:
`4ebdd734b5f11e368be1525f95a93070893ec14e9caafb161583807c88d23520`.

The offline source archive contains all136 frozen files byte-for-byte. A separate
native Release restoration without Git metadata passed **122/122** tests on this
same host. Direct/source-built0.1.1 wheel consumers each pass7 interface+6 export
cases; a fresh direct-wheel installation additionally verifies the installed module
paths, unchanged research-example SHA256
`c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9`, and no
libz dependency in the Python extension. Ordinary wheels leave optional streaming
OFF. The private artifacts were not published. Build artifacts were made from the
frozen indexed tree before its implementation commit; the manifest binds their exact
source bytes rather than asserting a clean Git build identity they did not possess.

### Measurements and handoff

Sequential final Release profile/throughput measurements and final implementation
commit are recorded in the subsequent evidence checkpoint. P1J remains gated until
all measurements, report, push and remote verification complete.
