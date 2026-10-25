# Independent seeded-state validation

`check_seeded_reference.py` independently encodes the versioned seed hash and
initializes flat Python order/source-state dictionaries from authored manifest
values. It reuses the existing independent Python wire/transition oracle, not C++
factory/recovery/mutation code. Candidate uses real C++ seed import, incremental
BinaryFile framing (chunks1/257) and existing context/native transactions.

Compare initial and every subsequent event: active IDs/side/price/quantity/priority,
levels/best, ledgers/revisions/journal counts, context lifecycle, exact receipts,
source ordinals/native sequences, provenance and errors. Initial native recovered
ledger and sequence offsets are derived explicitly, not copied from candidate.
Identity-sorted seed imports are tested for input permutation invariance. Historical
matching/execution before the seed is not invented or compared.

Authored example is tests/fixtures/market_seed_manifest.json; scenarios include
partial execution/cancel, replacement/retirement/deletion, two-symbol isolation,
broken-print observation, closing lifecycle, over-execution/cancel, reused retired
IDs, duplicate match, unknown references/types and fixed-seed randomized tails.
Largest authored seed has128 active orders/32-bit maximum quantities. Generator
seed0x53454544. Three deliberately wrong reference expectations (quantity, FIFO
rank, source accounting) must be rejected by differential comparison.

Focused C++ tests also validate malformed directories, invalid side/price/quantity,
reference/rank collisions, digest/boundary/clock mismatch, observed-origin refusal,
65th-order snapshot cap, lifetime caps including retired IDs, journal exhaustion,
canonical journal replay, corrupt prefix, truncated prefix and actual allocation
failure sweep with zero live bytes on every return. No assertions/tests disabled.

Reproduce with configured CMake build:

```sh
cmake --build build/phase9-clean-debug --target gig_itch_l3_reference_driver gig_itch_reconstruction_tests
ctest --test-dir build/phase9-clean-debug -R '^itch.reconstruction_initialization$' --output-on-failure
python3 scripts/check_seeded_reference.py build/phase9-clean-debug/gig_itch_l3_reference_driver /tmp/authored-seed-evidence.json
```

The normal existing itch.l3_reference case also invokes this supplement, preserving
its frozen canonical identity. Supplement has a separately named digest. Counts,
actual measurements and nine-configuration compiler/sanitizer outcomes are recorded
in evidence/seeded_reconstruction_results.json. No native ARM run of new code was
launched. Same-session independent implementation is not third-party certification;
common specification misunderstandings remain possible. No observed validation.

Measurements distinguish factory initialization from end-to-end replay plus JSON
state serialization; PMR counts exclude Python/input vectors/OS allocator overhead.
No exchange-latency interpretation. Worst-case configured capacity is an admission
bound, not a measured full-market scalability result. Whole-process peak RSS is a
separate Linux getrusage measurement when available; all machine/runtime details
are retained with the experiment rather than inferred from old native ARM evidence.

## Executed exploratory measurements

Clang19.1.7 Release,x86_64;152 fresh candidate processes/330 source attempts,
76 authored cases with fragments1/257,zero warmups. Shared machine and JSON state
output included in replay time; these are correctness-run measurements, not a
controlled latency benchmark. Native journal physical record remains12232 bytes.

| Measurement | Minimum | Median | Maximum |
|---|---:|---:|---:|
|initialization_ns|211431|225907.0|683544|
|replay_ns|10168|76069.5|568599|
|pmr_peak_bytes|482217|541935.0|615415|
|pmr_allocations|49|55.0|470|
|journal_record_bytes|12232|12232.0|12232|

Linux child maximum RSS: 13952KiB across separately executed candidates; not simultaneous aggregate/parent RSS. Full run wall time: 0.588430s. Aggregate attempts/s including serialization/refusal paths: 26361.879. Two largest seed schedules contain128 active orders. No whole-market scaling claim.

Development evidence is retained: initially rejected directory decode used the wrong
synthetic decoder Location; an Error-return append condition was inverted; two
fixture declarations triggered -Werror indentation. All repaired before gates.
An existing GCC Debug benchmark object had Ninja deps0 and was linked with changed
public types: streaming creation failed with an empty result/error0. Preserved stale
object/log, rebuilt that single object, scanned all9 directories (no other deps0),
then reran GCC matrix. This is a local build-cache failure, not a suppressed engine
assertion or weakened source check. Final matrix supersedes failed attempt while
retaining its evidence. `/usr/bin/time` was unavailable; resource measurements use
Linux getrusage instead, with method/scope recorded rather than invented output.
