# P1G synthetic reconstruction validation report

Status: **correctness, toolchain and package gates passed; measurements and remote
checkpoint pending. P1H not started**.
Starting feature HEAD: `1855a2f7a4d4ef472b61ffa5fd3b6b1a76acf282`.
Main: `165c5038336887116d69160b0d8e5a1a5ef59d16`. Initial tree was clean.
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
