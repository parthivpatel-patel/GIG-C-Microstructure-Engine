# Phase 8 exact Python research and versioned interchange

IMPLEMENTED / MUST HAVE: optional pinned pybind11 interface, validated event input,
deterministic replay/reset/recovery, owned snapshots, book/flow analytics, separate
offline simulation, TWAP/VWAP/POV/TCA, structured errors, exact values, provenance and
local verified exports. No Terminal source/build dependency, broker or live API.

## Build/package

Native C++ presets remain independent and need no Python binding library. Optional
bindings require Linux 64-bit, GCC/Clang 128-bit support, CPython3.9..3.12 headers
(current local tests use3.12), pybind11==2.13.6 and scikit-build-core==0.11.6. Runtime
jsonschema==4.23.0 validates versioned records offline. Explicit pins in pyproject;
no FetchContent/download occurs at CMake configure. NO_EXTRAS prevents implicit IPO.
Static core uses PIC only in Python-enabled build trees. See THIRD_PARTY_NOTICES.md.

```sh
export PATH=/workspace/gig-tools/bin:$PATH
python -m pip install pybind11==2.13.6 scikit-build-core==0.11.6 build==1.2.2.post1 jsonschema==4.23.0
cmake -S . -B build/python-debug -G Ninja -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTING=ON -DGIG_BUILD_BENCHMARKS=ON -DGIG_WARNINGS_AS_ERRORS=ON -DGIG_BUILD_PYTHON=ON -Dpybind11_DIR="$(python -m pybind11 --cmakedir)" -DPython3_EXECUTABLE="$(command -v python)"
cmake --build build/python-debug --parallel 1
ctest --test-dir build/python-debug --output-on-failure --no-tests=error
CXX=g++ python -m build --wheel --no-isolation --outdir build/wheels
```

Use a separate Release tree for binding validation. Installed wheel consumers need
no checkout/Terminal, compiler or pybind11 headers, only compatible CPython/native
runtime and declared Python dependencies. No wheel/release is uploaded or published.
No stable C++ ABI or manylinux/macOS/Windows/free-threaded/subinterpreter claim.

## Wire version 1.0 and exactness

Every interchange document has EXACT keys schema/version/data. Known schema names:
gig.event, gig.book_snapshot, gig.metric_result, gig.simulation_output,
gig.execution_schedule, gig.run_manifest. Version exactly1.0; unknown major/minor
reject pending an explicit compatibility implementation. Static Draft2020-12 assets
in schemas/ are generated from native record descriptors and tested for drift.
No untrusted/remote schema loading or network resolution. Stable wire does not imply
a stable native memory layout. Schema changes must undergo version/compatibility review.

All integer values INCLUDING enum codes, IDs, quantities, times, sequence numbers,
counts and seeds are canonical decimal STRINGS. No JSON number/float/bool coercion,
scientific notation, plus signs, leading zeros or negative zero for integer fields.
Signed/unsigned ranges and strong factories validate. Standard schema annotations
x-integer-minimum/maximum express string-integer bounds; the package validator enforces
them with Python arbitrary integers. Other consumers MUST implement these checks too;
plain JSON Schema treats custom annotations as nonbinding. Native APIs additionally
validate cross-field/domain/session/sequence/quantity contracts. Structural schema
success is not proof of financial input correctness or authenticity.

Fractions: {numerator: decimal_string, denominator: positive_decimal_string}, reduced
by native exact arithmetic; no silent price/lot rounding. Ratios may exceed64-bit but
obey the symmetric signed127-magnitude intermediate contract. as_fraction(metric)
returns Python fractions.Fraction or None; absence keeps its unavailable code.
Approximate volatility is a finite decimal long-double STRING with explicit schema
annotation, not an exact rational or portable-last-bit claim. Consumers may opt into
float/Decimal views; the engine never silently substitutes them for identity-bearing data.

Enums are stable explicit decimal codes in this schema version (current C++ values
are deliberately mapped): Side buy0/sell1; MissingReason known0/not_reported1/
unavailable2/not_applicable3; SequenceUnit message0/event1; ClockDomain UTC0/
venue_unsynchronized1/monotonic2/simulation3. Available always has reason AND value:
known reason0 requires non-null typed value; other reasons require null.

Event payload is {tag,value}: Add0, Cancel1, Replace2, Trade3, Quote4, Reset5,
Snapshot6, Session7, Unsupported8. Cancel amount variant all0 value{} or quantity1
value lots string. Trade details print0 or identified book execution1. All required
fields are explicit, including complete metadata, timestamps/precision/missingness,
dataset/version/license/hash availability, origin/source, real generator seeds,
transformation lineage and parent artifacts. Codec descriptor tables mirror every
native field; no reduced metadata shortcut. Native Unsupported8 returns unsupported
rather than being applied. Full mapping and field lists live in schema assets and
PHASE_1_CONTRACTS.md. event(..., inspect_incomplete=True) preserves supported missing
metadata states; Replay always requires complete validation.

Snapshot metadata includes run/journal prefix, rules/session/revision, requested depth,
truncation and owned levels. Snapshot validation/analytics enforce sorted positive
levels, aggregates, noncrossing and capacity. Adapter input/query depth <=4096; larger
requests/limits explicitly reject, never truncate or infer order FIFO. Other bounded
operational arrays follow <=4096 inputs, while structural output schemas accommodate
native configured limits up to100000. A snapshot schema is not an order-level recovery
snapshot and is not silently imported into a book.

## Native ownership, errors and causality

Replay(rules, config, limits=..., resource_budget_bytes='134217728') owns a stable
TrackedResource BEFORE its ReplayEngine; Simulation similarly owns its resource.
No Python pointers/views or borrowed native containers are returned. ResearchDocument
stores immutable canonical JSON; nested lookups/to_dict return independent copies,
safe after owner deletion or mutation. ExecutionResult is frozen and retains both
plan and simulated output, including hindsight-oracle label. No GIL release/parallel
mutation; same call order/configuration gives identical native outputs. No support
for concurrent C++ access, free-threaded Python or subinterpreters is claimed.

Native operational boundaries return structured code/field/optional index; public
facade raises EngineError with those attributes and code_name. SchemaError distinguishes
wire/JSON failure. Replay.run stops on first failure and attaches accepted and
failed_input_index; no hidden continuation. Native mutations allocate the Python
success envelope BEFORE any possible commit, parse inputs first, then call staged
native operations. Rejection/overflow/native bad_alloc preserves committed logical
state (continuity diagnostics may mark recovery as already documented). Query/export
failure cannot roll back an already committed mutation. Fundamental Python allocator
failure can still raise MemoryError; no claim of allocation-free Python runtime.

Client reports include ONLY delivered simulator reports. exchange_fills in diagnostic
simulation output can include unreported model truth and MUST NOT drive causal client
decisions. Origin is unconditionally synthetic and transformation simulated; a caller
cannot relabel these outputs as observed. execute/analytics assumptions remain those
of Phases3–6. Exact parsing does not certify exchange mechanics or synchronized clocks.

## Provenance, manifests and durable local export

run_manifest(data) requires code commit/dirty/source-tree digest, build/compiler/
flags/dependencies/platform, input IDs/hashes/licenses/origin/source/transformation,
parent run IDs + manifest hashes, schema versions, instrument units, clock/order/
sequence/recovery/precision policies, parameters, seeds, coverage with explicit missing
times, errors and completeness. Dirty is explicit, not an attestation. A source-tree
digest must describe the actual code/build input table/archive; retain that artifact
when outside a verified Git commit. No code SHA/license/source value is invented.
Metadata validation/hashes do not authenticate external source/clock/calibration.

export_run(directory, manifest, artifacts, input_artifacts=...) creates a NEW local
directory only. It requires actual bytes for every declared input, verifies all
hashes, caps files/documents32MiB and run input+output128MiB, retains inputs under
safe indexed names, validates output versions/run refs and explicit oracle labels,
writes checksummed JSON artifacts, then publishes manifest.json with an atomic
no-overwrite link. A manifest.incomplete.json marker exists until all files finalize;
I/O errors are durably marked when possible and propagate. No failed/incomplete run
is returned as complete. No external publication/release/network write occurs.

verify_export is read-only: rejects incomplete markers, unsafe/symlink paths, missing
retained inputs, oversized files and hash/schema mismatches. Full replay canonical
journal or complete simulated command archive should be retained as input parents,
not latest_metadata alone. Cost benchmarks and parent manifests must be retained by
identity/hash; run refs resolve to own run or declared hashed parent manifest. Export
validates representations/integrity, not completeness/authenticity of external
provenance graph. Caller must supply proper original artifact versions/licenses.
Logical finalization/file fsync is not a cross-filesystem crash-durability guarantee.

## Complexity, validation and interview rationale

Binding conversion O(record/array size), owned Python/JSON copies add memory and
validation cost beyond C++ baselines. JSON schema checks/domain checks and immutable
copy lookups are research conveniences, not a high-frequency interface. Bounded
inputs/depth, byte-budget native owners and document limits prevent silent oversized
coercion. Python/parser/formatting memory is outside selected PMR resource accounting.

Tests cover every event family/nested variant, full missing metadata/provenance,
64-bit extrema/127-bit fractions, duplicate JSON keys/unknown versions/enums, invalid
fields, replay atomicity/gaps/reset/recovery, low budgets, owner lifetime/copy isolation,
simulation reports, schedules/TCA/flow, independently computed Fraction values,
schema drift and complete/incomplete/no-overwrite/hash-tamper export behavior. Optional
builds add Python interface/schema checks to the entire native regression suite.
Debug/Release, installed wheel, sanitizers and actual results appear in PHASE_8_REPORT.md.
Interview defense: typed descriptor-driven codecs prevent dropping lineage fields;
string integers protect JS consumers; publication staging preserves mutation semantics;
owned immutable documents decouple Python lifetimes from stable single-owner C++ state.

## Sanitizer interpreter isolation

GNU/Linux Python ASan tests preload libasan AND libstdc++ so exception interception
is initialized before a C++ extension loads. Core C++ ASan/UBSan tests keep ordinary
exit leak checks. The stock CPython control (`python -c pass`, no engine imported)
reported52710 shutdown bytes in1019 allocations in this environment; this is recorded
as interpreter evidence, not hidden as an engine pass/failure.

Python tests keep detect_leaks=1 and perform a live-interpreter recoverable LSan
checkpoint after native owners/tests and GC, with active CPython evaluation frame
materialized as a legitimate conservative root and GIL held. Automatic interpreter-
shutdown leak checking is isolated with leak_check_at_exit=0, not a suppression file
or disabled leak detector. A mandatory negative control verifies actual detection,
exit1 and intended report for a deliberate12345-byte unreachable malloc. No unrelated
crash/sanitizer failure counts as that control passing. Python late-finalization leaks
are NOT claimed verified; native owner/resource and live leak checks are. Address/
undefined checks still run normally and abort findings. See actual phase report counts.

The standalone example `examples/python_research.py` imports only the installed package,
asserts exact201/2 midpoint and403/4 microprice, and demonstrates simulated reports
remaining unavailable until their configured delivery time. No fixture/test repository
imports or live market inputs are required by that consumer example.

Reproduce the interface baseline only from a clean code checkpoint with an existing
unsanitized Release Python tree: `python scripts/benchmark_python.py --build-dir
build/python-release --output-dir build/python-baseline`. It rebuilds/runs the full
suite before importing that exact extension, validates256 synthetic adds/reference
remaining512 lots and repeated canonical hashes, then retains seven bulk repetitions,
1792 separate service samples, native-owner PMR and whole-Python VmHWM with flags/CPU/
code/input/binary hashes. Schema/immutable/native conversion overhead is INCLUDED;
fixtures/setup/export excluded. It is a research-interface rate, not C++ core speed.
Descriptor tables must be updated when native contracts change; C++20 has no automatic
field reflection. CI tests schema drift and complete current-field round trips.
