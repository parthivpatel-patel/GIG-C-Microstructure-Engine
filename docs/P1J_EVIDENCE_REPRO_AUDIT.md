# P1J independent evidence, package and resource audit

Reviewed October 23, 2026 UTC against P1I implementation
`5ff7c8596f8705d92b7d97f55f860d0cb8d409fb` and evidence checkpoint
`5584ce34de5b839d2a78fabcd8e6603cec1185f3`. This reviewer inspected the actual
P1G/H/I JSON, historical source blobs, raw JUnit/logs, CMake caches/commands,
archive/wheels, installed consumers, validator and benchmark code. No full matrix
was rerun by this reviewer. The coordinating reviewer owns final frozen-source
matrix/package acceptance after the small verifier repairs below.

No critical/high defect was reproduced in this review's evidence/package/resource
scope. Two medium evidence-verifier defects were reproduced and repaired after
explicit coordinating-reviewer authorization. Neither defect establishes an engine
mutation defect, publisher authentication, remote execution or production readiness.

## Independent results

The independent parser/hash script and full outputs are privately retained under
`build/p1j/evidence/independent_evidence_audit.py` and
`independent-evidence-results.json`. It does not use the production validator for
source/raw/artifact hashes, JUnit case counting, archive checks or benchmark arithmetic.
The production validator is separately invoked as the subject of the tamper probes.

| Historical evidence | Actual JUnit cases by configuration | Total | Source/raw/artifact hash checks |
|---|---|---:|---:|
| P1G | Six native ×103; Python106/106/107 |937|105|
| P1H | Six native ×117; Python120/120/121 |1,063|129|
| P1I | Six native ×122; Python125/125/126 |1,108|231|

All checked hashes agree. The27 historical XML files contain zero failure/error,
skipped or disabled cases. JUnit/log identities were independently rehashed in
addition to the inventory checks. These are recorded test outcomes, not independent
execution attestation. P1I's source archive contains all136 frozen files with exact
matching bytes. The original P1I candidate-profile check passes with136 source files,
92 raw files and3 package artifacts. Historical H/I verification also passes after
repair; current-tree qualification must use the newly frozen source.

All nine inspected current CMake caches enable streaming and warnings-as-errors;
native/Python, Debug/Release and GCC/Clang selections agree with their names. Actual
sanitizer compile commands contain address+undefined sanitizers and
`-fno-sanitize-recover=all`. Python tests retain the explicit live leak-control and
`leak_check_at_exit=0` boundary; late interpreter-finalization leak coverage must not
be inferred. Current caches alone do not authenticate historical executions.

A new clean consumer virtual environment was created under
`build/p1j/evidence/restored-consumer`; the original direct wheel and dependencies
were installed with `--no-index` and local dependency wheels. From `/tmp` with
`PYTHONPATH` removed, actual installed interface7/7 and export6/6 cases pass. The
research example again hashes to
`c76ca0074818e18392753353bfe2cc5438e83c105325458e63a9db0360c3e1e9`.
Both module paths resolve inside this new environment's `site-packages`, recorded in
`restore-5.stdout`, rather than the source/build Python tree. Commands, statuses and
stdout hashes are in `independent-restoration.json`; complete streams are retained.
The original fresh consumer was also exercised independently with the same13 cases
and example result. This is same-host offline restoration, not another OS/VM.

Wheel metadata declares CPython>=3.9,<3.13 and runtime `jsonschema==4.23.0`;
only CPython3.12/Linux x86_64 is locally qualified. Exactly one native extension is
present. `readelf -d` shows libstdc++, libm, libgcc_s and libc, with no libz dependency.
CMake links `_native` only to `gig::microstructure`; streaming's private system-zlib
boundary is separate and the default option remains OFF. No Python streaming API or
stable native ABI qualification follows. Cache/metadata/linkage evidence is retained
in `cache-package-boundary.json`. Broader Python/platform distribution remains a
qualification/documentation gate, not a newly demonstrated defect.

## Resource and performance recalculation

The independently recalculated16 P1H raw benchmark records reproduce journal bytes,
median batch times and throughput within printed rounding. Their largest selected
PMR peak is41,685,328 bytes and largest recorded native RSS58,093,568 bytes;
`h-benchmark-recalculation.json` retains every calculation.

P1I journal arithmetic is15,944×1,024×2=32,653,312 bytes for the profile, and
15,944×512×2=16,326,656 bytes for the throughput fixture. Seven GCC elapsed samples
have median15,878,937ns, yielding15,386.566860ns/source record and64,991.756060
records/s; Clang median14,335,133ns yields13,890.632752ns/record and71,990.960949
records/s. These match the published rounded values. The benchmark builds fixtures
outside the timed `run`, then times create/feed/validate/destroy with two warmups;
these are batch measurements, not event-tail latency or real-archive throughput.

A fresh execution of the exact hash-identified GCC profile probe reproduces every
raw P1I profile field: first PMR peak42,722,343; original live34,559,015; coexisting
query live35,542,081; restart peak77,281,358; final live after destruction0. The
16MiB selected governor stops framed516/accepted515/native512 at peak12,109,863;
journal cap1023 stops framed2050/accepted2049/native2046 with `journal.records`.
The45 reached query-allocation faults are scenario counts, not unique global sites.
`actual-0.stdout` records executable SHA256
`9b08141f1f44615222ef9c713a56d9ebcbeb0b230b50ffb03b8fd506b13e7342` and
actual RSS76,058,624 bytes. No speedup claim is made from this rerun.

The actual retained `/tmp/gig-p1h-large-synthetic.gz` was independently hashed,
decompressed using Python gzip and framed using integer length parsing. It has
500,001 physical records,20,500,016 raw bytes and59,723 compressed bytes; both full
hashes match P1H. The1,024-record prefix is41,957 bytes with SHA256
`5d5be56e33cd25588be128086a356400e37ff2d0d26d8bee4a40436932c5764f`.
Frame1,025 ends at41,998;65,536 produced bytes minus that framing count leaves23,538
buffered bytes. `large-prefix-independent.json` retains these independent results.
The historical pipeline stopped after1,024 accepted external records; the authored
500,001-record inventory must not be relabeled accepted/replayed source history.

PMR excludes fixed objects, fixture/JSON allocations and allocator overhead; RSS is
single-child Linux high-water accounting with possible inherited pre-exec floor.
Retained journals/lifetime IDs/matches/receipts still grow; the measured finite caps
and selected one-level profile do not prove every maximum combination fits128MiB.

## Reproduced findings and disposition

**EA01 — Medium, fixed: contradictory duplicated measurement assertions passed.**
Original `scripts/check_validation_evidence.py:218` hashed raw files, then proceeded
to matrix checks without binding `report.measurements` to `measurements.json`.
A new independently created report replaced its measurement list with fabricated
1-byte PMR/10^12 records-per-second values while leaving the authentic raw file and
its hash untouched. `--candidate-profile` still returned PASS. The original report
itself was consistent; the defect affected the verifier's consistency guarantee.

Reproduce the original outcome with the preserved script
`build/p1j/evidence/verifier-before.py`, tamper report
`tamper-alter_measurements.json`, and `--raw-root build/p1i/evidence`.
The before result is in `independent-evidence-results.json`. New unit controls
failed before repair. Current code at `scripts/check_validation_evidence.py:244`
requires list measurements to have the raw record and binds measurements/environment/
toolchain duplicates; package comparison is also type exact. Canonical JSON equality
preserves bool/int/float distinctions. Acceptance: contradictory, missing and
false/zero or integer/float substitutions reject; original historical H/I pass.
Effort: small verifier/test change, no core/dependency change. Final candidate source
freeze and coordinator matrix/package rerun remain dependencies for candidate closure.

**EA02 — Medium, fixed to a scoped minimum: candidate source coverage could collapse.**
Original `scripts/check_validation_evidence.py:210` accepted any nonempty source map.
A new tamper report kept only `CMakeLists.txt`, recomputed its aggregate manifest hash,
and retained all genuine raw/package files: candidate mode still returned PASS with
`frozen_files=1`. The original P1I136-file freeze was complete for its declared
inventory; this was a missing candidate-policy guard, not a cryptographic forgery.

Reproduce with the preserved before script and `tamper-drop_source_coverage.json`.
Current `scripts/check_validation_evidence.py:34` defines20 explicit protected
P1E–H source/model/test paths shared by the historical H/I inventories;
`candidate_contract` rejects omission even when the aggregate is rehashed. Generic
consistency mode remains intentionally weaker. Acceptance: reduced candidate source
coverage rejects and actual H/I candidate reports pass. Effort: small, same source
freeze/rerun dependency as EA01. This minimum does not claim a complete transitive
build dependency graph or protect arbitrary future paths; exact reviewed manifest
and artifact identities remain required in the audit.

The original39 unit cases are preserved; eight additional cases yield47 passing
cases, including typed-comparison subcontrols. `regressions-before.stderr` retains
four failed regressions before repair; `regressions-final.stderr` retains47/47 after.
Final source hashes supplied to the coordinating reviewer:

- verifier: `9486d49fafec8dc6cfd4eca8d5ba40cfba11f2b8d5481b6252efcd4db8bd28b0`
- tests: `4cf6d8dbd89fb4b455775fd1082818c5f1b6c4607b1d7275f12d37c06388cf43`

No remote action, market acquisition, release, merge, journal redesign, or unrelated
core/build change was performed by this reviewer. Hosted CI, other architectures,
observed-data initialization/reference truth and operational trading readiness remain
outside these local synthetic results.

## Coordinating-review closure

The subsequent repair checkpoint `92567f15183074647e14af3dde4604ed5ba095c7`
was pushed and remotely verified. Its final47 verifier unit cases, all1,108 nine-row
CTest outcomes,122 clean source-archive native tests and both installed-wheel consumers
passed. The implementation review above remains the earlier independent record;
[P1J_INDEPENDENT_AUDIT_REPORT.md](P1J_INDEPENDENT_AUDIT_REPORT.md) and
[P1J_EVIDENCE.json](P1J_EVIDENCE.json) record final qualification and open RC gates.
The minimum protected-source profile is deliberately not full build-graph attestation.
