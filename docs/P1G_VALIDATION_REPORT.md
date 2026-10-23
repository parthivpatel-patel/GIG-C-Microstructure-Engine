# P1G synthetic reconstruction validation report

Status: **P1G complete, committed, pushed and remotely verified** at
`c3c3d8caef8f5b60aa4ce29f0f0875dc3bdd91c4`. The subsequent P1H gate also
completed at `cafcdb986afac5298c95bcf3418acb7cf3e6aafe`; see its validation report.
Starting feature HEAD: `1855a2f7a4d4ef472b61ffa5fd3b6b1a76acf282`.
Main: `165c5038336887116d69160b0d8e5a1a5ef59d16`. Initial tree was clean.
Verified implementation checkpoint: `997007f32cf94af1968b48a31504302de40085a0`.
Final evidence is a subsequent documentation commit; exact remote SHA is recorded
in the delivery/checkpoint response, avoiding a self-referential commit hash.
No market bytes were downloaded. This phase establishes synthetic-only behavior,
not exchange-equivalent reconstruction, empirical NASDAQ validation or production
trading readiness.

## Implemented scope

See [implementation contracts](P1G_IMPLEMENTATION_NOTES.md),
[34-row coverage ledger](P1G_COVERAGE.md), and
[reproduced native defect](P1G_DISCOVERED_DEFECTS.md).

The standalone library supplies authored-empty eligibility, a prepared source-context
transaction, exact unit/metadata projection, two independent native books, explicit
external observations, held-record identity and disjoint accounting, and verified
fresh-prefix restart. Native matching/execution/TCA/journal and Python contracts are
preserved. Complete-context seeded start remains explicitly unsupported.

The independent Python model derives expected values from source bytes and declared
fixture truth, using flat orders/FIFO tickets, arbitrary-precision integers and
Fraction arithmetic. It compares context lifecycle/retirement/matches, all native
orders/levels/ledgers/journals, full metadata/provenance, source receipts/sequences,
accounting, eligibility and incomplete-state flags after every candidate.

## Development evidence and corrected findings

- Independent campaign:10,032 sessions,65,186 candidates,10,025 explicit rejections;
  seed5255495. Six deliberately wrong expected models are detected.
- Full L3 semantic SHA256:
  `bb16d4ba9e400ee8f2bc40707de5aa89d0b0955819b4f1f45ca2cdf82cac7991`.
- Existing P1F SHA256 must remain
  `58d6a2f6fd574bc8041676964307ac606422dcebba780bc10166b3019b99476e`;
  P1E must remain
  `142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e`.
- Real allocation injection:5 direct-native first-add sites,6 adapter-creation,
  6 adapter-add,5 adapter-U and32 isolated-restart sites; zero retained tracked bytes.
  An armed allocator also proves no requests in accepted E/X/external final commits.
- Fragmentation:2,027 schedules/cuts over507 bytes/18 source records, plus trailing
  bytes; literal every-prefix order/FIFO/ledger truth. Native64/65-order snapshot
  boundary tested without claiming positive adapter seed support.
- The new fault sweep reproduced a pre-existing first-add hash-bucket allocation
  after partial transfer. The smallest staging repair is independently reproduced
  before/after and documented separately. Existing journal representation is intact.
- Invalid test BookLimits in early budget/benchmark fixtures were corrected without
  weakening native checks. The first complete matrix passed937 CTest outcomes.
- A resource run then found the oracle retained all generated grammar expectations:
  maximum child RSS224,624,640 bytes exceeded the proposed128MiB oracle profile.
  Incremental fixture generation reduced the measured high-water to65,748,992 bytes
  (62.7MiB), below128MiB, preserving both canonical hashes. Batch sizes64 and128
  produce identical full-campaign hashes. All nine configurations and both package
  consumers were then revalidated on the final fixture script. Prior logs remain under
  `build/p1g/evidence/development/pre-streamed-oracle/`.

## Final matrix and package gate

Linux x86_64; GCC14.2.0, Clang19.1.7 (system GCC standard library), CMake3.31.6,
CPython3.12.14. Warnings are errors; ASan/UBSan use nonrecovering checks.

| Configuration | Passed | Failed / skipped / disabled |
|---|---:|---:|
| GCC Debug |103/103|0 /0 /0|
| GCC Release |103/103|0 /0 /0|
| GCC ASan/UBSan |103/103|0 /0 /0|
| Clang Debug |103/103|0 /0 /0|
| Clang Release |103/103|0 /0 /0|
| Clang ASan/UBSan |103/103|0 /0 /0|
| GCC Python Debug |106/106|0 /0 /0|
| GCC Python Release |106/106|0 /0 /0|
| GCC Python ASan/UBSan |107/107|0 /0 /0|

**937 final CTest outcomes**, zero failures, skips, disabled tests or observed sanitizer
findings. Each configuration preserves all85 P1F-era native outcomes and adds18 P1G
outcomes. Every final JUnit independently contains the unchanged P1E/P1F hashes and
the exact L3 canonical hash above. No assertion, warning or sanitizer suppression
was weakened. Earlier development and pre-memory-fix logs remain separate.

The final source archive contains all36 frozen validation files byte-for-byte. Both
the direct wheel and an offline source-archive-built wheel pass7 interface and6 export
contract unittest cases each; installed module paths identify the consumer venv.
Both examples are identical, and byte-identical to the prior P1F example SHA256
`c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9`.
No Python API/schema/package-version change or publication occurred.

Local raw logs/JUnit/package hashes are retained under `build/p1g/evidence/`;
[P1G_EVIDENCE.json](P1G_EVIDENCE.json) retains the source/JUnit/package hashes and
actual counts. Hosted CI is unverified; no local result is presented as hosted success.

## Measurements and reproducible demonstration

Sequential unsanitized Release runs from clean implementation commit997007f, after
all correctness/package gates. CPU: Intel Xeon Platinum8573C, five exposed logical
CPUs; shared virtualized host. Two warmups and seven actual measured repetitions.
Fixture generation is outside timing; create/decode/context/native journal/receipts,
validation and destruction are inside. These are batch averages, not event-service
or tail-latency distributions. No production/exchange throughput claim is made.

| Orders per symbol | Source records | GCC median ns/record | Clang median ns/record | Peak selected PMR bytes |
|---:|---:|---:|---:|---:|
|8|67|11042.6|9463.67|1303504|
|32|259|12007.4|11354.6|5207280|
|128|1027|12155.6|11169.1|20822320|
|256|2051|14812.7|13530.0|41642160|

All eight measured fixtures receive independent Python packing/SHA/count/checksum/
source-to-native mapping checks. Raw repetitions, compiler strings, fixture hashes,
CPU time and executable hashes are retained in the evidence JSON. Selected PMR peak
stays below128MiB; each run releases all tracked bytes. The largest measured native
process high-water is64,323,584 bytes, below the proposed256MiB unsanitized ceiling.
Wait-accounted RSS includes process/allocator and possibly inherited pre-exec floors;
it is not engine-only memory or a sum of concurrent process-tree high-waters.
The separate default-profile independent oracle peaks at65,748,992 bytes (<128MiB).

Both compilers measure SourceContext808, PreparedContext1496, SourceReceipt344,
SyntheticReconstructor98264 and JournalEntry15944 bytes. Default4096 receipt slots
reserve1,409,024 element bytes. The n256 workload has1024 journal entries per book:
32,653,312 retained journal element bytes; one growth with the other journal full
can coexist at40,816,640 journal bytes before other state. Actual peak41,642,160
includes tracked context/receipts/books. No journal optimization was performed.

Equivalent standalone context checks (same P1F fixture, seven repetitions) now measure
GCC599.064/1001.17 ns per record at n128/512 and Clang254.895/632.751. Prior P1F
measurements were465.556/842.051 and210.321/593.165 respectively. The new prepared
ownership path adds work, and these shared-host observations are slower; this is not
a controlled causal estimate or speedup claim. Full L3 timings have a different scope
and must not be compared directly to standalone context throughput.

Reproduce offline with the existing toolchains/presets:

```sh
CXX=g++ cmake --preset release
cmake --build --preset release -j2
ctest --preset release --output-on-failure
python3 scripts/run_synthetic_l3_demo.py build/release/gig_itch_l3_reference_driver
python3 scripts/check_itch_l3_reference.py build/release/gig_itch_l3_reference_driver
build/release/benchmarks/gig_itch_reconstruction_benchmark 128 7
```

The documented release preset uses `build/release`; the validation host reused `build/phase9-clean-release`. The actual demonstration yields13 source
records:7 native commits and6 external observations. Book1 has ID103,15lots@101,
FIFO ticket2, six journal/revisions, ledger45in/30out; book2 has ID201,20lots@200,
one journal/revision. Every step is compared independently. The source/session is
an incomplete synthetic prefix, with no market reference or clock/date inference.
`build/p1g/evidence/synthetic-demo.txt` retains actual output.

## Acceptance and next phase

All mandatory P1G synthetic gates have local evidence in the34-row coverage ledger,
including justified unsupported complete-context seeding and observed-data exclusions.
After the documentation commit is pushed and remote HEAD verified, P1H may begin.
Its gzip/container/streaming gates are not implied by P1G and have not run here.
The NASDAQ rights quotation and separately authorized pilot plan are recorded in
[NASDAQ_REAL_DATA_PILOT_PLAN.md](NASDAQ_REAL_DATA_PILOT_PLAN.md); no acquisition occurs.

## Limitations

128MiB PMR is supplied/enforced by validation drivers, not a hidden default governor
inside the general API. Explicit count/receipt caps remain mandatory. Context and
lifetime/match lookups are bounded linear scans. Native journal entries remain large
and history is retained; no whole-day memory promise is made. Restart trusts a
caller-retained descriptor/source/code identity, supports uniform raw provenance,
and rebuilds from byte zero; mixed overrides are explicitly unsupported. It is not
a MAC, origin authentication, durable crash recovery or gzip seek index.

C is opt-in book-only; P/Q/B are external observations. Halts/unknown/historical
extensions stop; no cross clearing, hidden-order reconstruction, tape correction
or exchange-priority certification is claimed. Time-of-day is not UTC. Two configured
symbols do not establish a whole-market router. Observed initial state, dated2019
schema compatibility and an independent observed reference are still unverified.
Hosted CI, ARM64, other OS/stdlib/Python combinations remain unverified. Clang uses
the system GCC standard library. The existing Python live-LSan harness retains its
late-interpreter-finalization limitation; native sanitizer leak checks stay enabled.
