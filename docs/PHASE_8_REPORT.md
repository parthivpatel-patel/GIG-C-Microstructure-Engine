# Phase 8 completion report

Objective: pinned standalone Python research, exact versioned interchange, structured
errors, safe ownership and integrity/provenance exports without Terminal changes.
Verified clean start: `874bd59f72aa69d8a37591896ecfda6650b8a63b`.
End implementation: `ce44faa6d53abe40c928d7d4bfb07ece94c70fd2`, normally pushed
and exact remote SHA verified. Subsequent evidence/report commit is this document's
containing Git commit; Phase 9 records the full boundary SHA.

Implemented: optional pybind11==2.13.6/scikit-build-core==0.11.6 build, version0.1.0
private local wheel, runtime jsonschema==4.23.0, full event/metadata/provenance codec,
strict replay/reset/recovery, snapshots/book/flow analytics, offline matching/latency,
TWAP/VWAP/POV/TCA, structured errors and owned immutable ResearchDocument/ExecutionResult.
14 generated/checked schema assets include wire1.0 event/snapshot/metric/simulation/
run-manifest/execution-schedule and configuration/input definitions. Integer/enum/
64-bit quantities/timestamps/IDs/seeds use decimal strings; ratios remain exact.
Domain validation stays native; schema custom string-bound annotations are enforced
by the companion Python validator. No float/bool coercion, duplicate keys, unknown
versions, dropped provenance fields or automatic recovery/FIFO inference.

Contracts/units/ownership/capacities/complexity/alternatives/assumptions/interview
rationale: PHASE_8_INTERFACE.md and GIG_INTEGRATION.md. Native resources precede
owners in lifetime; returned values never borrow C++ containers. Mutation success
publication is allocated before commit. Export requires actual input bytes/hashes,
retains inputs, checks run/parent/schema/oracle/seed/benchmark references, stages an
incomplete marker and finalizes no-overwrite manifest only after file checksums.
Read-only verification detects incomplete/tampered/unsafe exports. No crash-durability
or source-authentication claim; external provenance graph authenticity remains caller work.

Actual local results on GCC14.2/CPython3.12.14/Linux x86_64:

| Configuration | Executed | Failed/errors/skips |
|---|---:|---:|
| Python-enabled Debug | 63/63 (4.19s final run) | 0/0/0 |
| Python-enabled Release | 63/63 (2.47s full run; baseline reran63) | 0/0/0 |
| Python-enabled ASan+UBSan | 64/64 (18.86s final run) | 0/0/0 |
| Installed private wheel consumer | 7/7 Python groups (0.649s) | 0/0/0 |

The 63 comprise all61 native checks plus Python interface/schema drift. Python groups
exercise all eight event families/nested variants, unsupported states, full provenance/
missingness, int64/uint64 extremes,127-bit ratios, invalid enum/range/version/duplicate
input, gaps/reset/recovery, atomic low-budget failure, immutable copy/lifetime safety,
client report latency, schedules/flow/TCA, integrity/no-overwrite/incomplete exports.
300 independent Python Fraction cases (seed8033), exact hand metrics/costs and ALL
previous independent native/Python reference cases remain enabled. No assertion
weakening, omitted core regression or hidden expected failures.

Sanitizer qualification: stock CPython (`python -c pass`, no engine) reported52710
shutdown bytes/1019 allocations. ASan also required libstdc++ preload before extension
C++ exception interception. The live LSan harness keeps detect_leaks=1, holds the GIL
and materializes the active optimized CPython frame as a legitimate conservative root
(avoiding an interpreter-frame200-byte false leak). Native owners/tests/GC complete
before the recoverable checkpoint; both interface/schema checks report LIVE_LSAN_CHECK=0.
The64th test verifies detection of an intentional12345-byte unreachable allocation,
exit1 and intended LSan report. No suppression file; no blanket disabled leak detector.
Automatic CPython shutdown leak check alone is isolated (leak_check_at_exit=0).
Native C++ tests retain ordinary exit leak checks and aborting ASan/UBSan. No unexpected
sanitizer findings remain; Python late-finalization leaks are explicitly NOT verified.

Private local wheel: gig_microstructure-0.1.0-cp312-cp312-linux_x86_64.whl,
SHA-256 `dad962e5015d792449cefef10b5b1e5eedbde99657c409a8844f1d5bc4a85bbf`.
Zip inspection confirmed14 schemas, notices and exact current Python source bytes.
Installed into a new noneditable consumer venv with constrained runtime dependencies;
import path verified under that venv, all seven groups and standalone example passed.
Example output SHA-256 matches Release build tree:
`287f373a245dff61c40c8a08e47aace216573f4d9240533e5a7656491f97efcf`.
No wheel/binary is committed, uploaded or released. Initial wheel tooling inherited
an unavailable SDK clang++ setting; explicit CXX=g++ selects the verified compiler
and is in reproduction instructions. Full licenses/notices and tested lock retained.

Clean-code interface baseline: baselines/phase8-python-interface.json. Runner rebuilds
and reruns63 tests BEFORE importing the exact selected unsanitized Release extension.
256 synthetic adds/run, expected512 resting lots, seed0 fixed fixtures, two warmups,
seven bulk repetitions and1792 separate service samples; every canonical replay hash
matches `6503413a860da1800ab06e846f504a338d73ebd8078c33dac7346448a0df0fda`.
Input SHA-256 `f1288cc88c4da2539f7f1c7e28b310f71c4ad07cb81cdb32338eb42849cba1c1`.
Observed median 719.72 events/s,
p50/p95/p99/worst observed 1208328/2013844/2935411/12881071 ns.
This INCLUDES schema/immutable/Python/native conversion/validation/book/journaling;
not comparable to bare C++ throughput. Each bulk owner's selected PMR status:787
allocations,268 deallocations,4109064 live/6137608 peak requested bytes, including
owner setup but excluding parser/Python heaps. Whole Python VmHWM34435072 bytes
includes interpreter/schema/fixtures/driver/native/export. Raw values/flags/build/
CPU/code/module/input hashes retained. Shared scheduling, no production speed claim.

Hosted CI UNVERIFIED: fresh checks API probe for preceding checkpoint failed proxy
CONNECT403 (curl56). Workflow keeps existing GCC/Clang three-preset matrix; GCC Release
additionally installs pinned deps, tests bindings/schemas and local wheel/example,
with NO publication. Equivalent local checks above pass. No local engine Clang/native
ARM validation yet; Python being compiler-built by Clang is NOT engine compatibility
validation. Only CPython3.12 and Linux x86_64 currently verified;3.9–3.11, other OS/
interpreters, free-threaded/subinterpreters/manylinux/C++ABI remain unverified/unsupported
as documented. PMR budgets exclude Python/parser heaps; bound annotations require
consumer enforcement; descriptor tables need review when native contracts change.

Acceptance: required implementation, mathematical/engineering/consumer contracts,
unit/reference/regression, Debug/Release/qualified sanitizer+active leak control,
installed wheel ownership/schema smoke, full provenance/export validation, relevant
clean benchmark, diff review, normal push/exact remote verification PASSED. Hosted
success unavailable/disclosed. No Terminal/source changes, main merge, force push,
live/broker integration, paid cloud resource or external release/publication.
Phase 8 complete; automatically continue Phase 9 fresh-build/package/reproducibility,
platform/security/license/dependency/documentation review and final acceptance.

Changed paths:

- `.github/workflows/ci.yml`
- `.gitignore`
- `CMakeLists.txt`
- `README.md`
- `THIRD_PARTY_NOTICES.md`
- `docs/GIG_INTEGRATION.md`
- `docs/PHASE_8_INTERFACE.md`
- `docs/PHASE_8_REPORT.md`
- `docs/baselines/phase8-python-interface.json`
- `examples/python_research.py`
- `pyproject.toml`
- `python/bindings/build_info.hpp.in`
- `python/bindings/module.cpp`
- `python/bindings/results.hpp`
- `python/bindings/schemas.cpp`
- `python/bindings/wire.cpp`
- `python/bindings/wire.hpp`
- `python/gig_microstructure/__init__.py`
- `python/gig_microstructure/manifest_schema.py`
- `requirements-python.lock`
- `schemas/cost_config-v1.schema.json`
- `schemas/flow_config-v1.schema.json`
- `schemas/flow_quote-v1.schema.json`
- `schemas/flow_trade-v1.schema.json`
- `schemas/gig.book_snapshot-v1.schema.json`
- `schemas/gig.event-v1.schema.json`
- `schemas/gig.execution_schedule-v1.schema.json`
- `schemas/gig.metric_result-v1.schema.json`
- `schemas/gig.run_manifest-v1.schema.json`
- `schemas/gig.simulation_output-v1.schema.json`
- `schemas/instrument_rules-v1.schema.json`
- `schemas/plan_config-v1.schema.json`
- `schemas/replay_config-v1.schema.json`
- `schemas/simulation_config-v1.schema.json`
- `scripts/benchmark_python.py`
- `scripts/check_python_lsan_control.py`
- `scripts/generate_schemas.py`
- `scripts/run_python_sanitized.py`
- `tests/python_fixtures.py`
- `tests/test_python.py`
