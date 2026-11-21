# November 21 recovered sprint reproduction

Tested integrated source: `ec255121d070f80e7e92d958f223bf0701baa806`.
Protected November20 baseline: `7cd99d4afd98f58330732ecfc0fd0b3303c49a3b`.
Receipts: NOV21_SPRINT_RECOVERY_EVIDENCE.json and `nov21-sprint-recovery-evidence/`.
These are offline developer checks. No application/server/browser, provider, workflow,
deployment, trading, paid resource or owner acceptance is part of this procedure.
Use fresh output/checkouts and preserve all existing work; never reset a worktree.

## Independently verify the retained evidence

From repository root at the final evidence commit:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib,json,subprocess
b=Path('docs/qualification/development-continuation')
e=json.loads((b/'NOV21_SPRINT_RECOVERY_EVIDENCE.json').read_text())
for r in e['retained_receipts']+e['runtime_files']:
 p=Path(r['path']);data=p.read_bytes()
 assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],p
for r in e['runtime_files']:
 data=subprocess.check_output(['git','show',e['tested_integrated_source']+':'+r['path']])
 assert hashlib.sha256(data).hexdigest()==r['sha256'],r['path']
print('All81receipts and27runtime inputs verified')
PY
```

Raw log whitespace is retained to preserve hashes. Initial typing/invalid-proof
reproductions remain separately labelled and are not final passing qualification.

## Guarded Python, frontend and tooling

With the source-enabled SDK in build/recovery-release/python:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/run_no_launch_suite.py
npm --prefix terminal/web test
npm --prefix terminal/web run build
work/venv/bin/python -m unittest discover -s tests -p test_elf_dependency_inventory.py -v
work/venv/bin/python -m unittest discover -s tests -p test_local_artifact_inventory.py -v
work/venv/bin/python tests/test_offline_sbom.py
work/venv/bin/python tests/test_sdist_patterns.py
work/venv/bin/python -m pip check
```

Expected:1,153 guarded Python;373 frontend;35 ELF;35 retained local inventory;13 SBOM;
three source-package-pattern cases. No failures/errors/skips accepted. The harness
checks its exact named cohort, forbids sockets/application construction and asserts
application absence. TypeScript/Vite must pass without starting a server. Vite size
and Starlette/httpx deprecation warnings remain visible.

The four newly registered Python modules add111 cases to the preceding1,042 cohort:
inherited cross-role DRS40,statement comparison28,Kraken coordinator32,capsule11.
The new registered frontend file accessibilityNavigation.test.ts adds28 cases to345.
It uses actual React leaf SSR and actual helpers wired into App, including controlled
late promises and stale rendered selections; it does not mount an application or
qualify a real DOM/AT device.

Run the nine existing terminal/tests/check_*_contract.py scripts for xbrl_statement,
xbrl_accuracy,xbrl_vintage,xbrl_calculation_report,offline_import,statement_set,
accounting_statements,itch_product andtrade under the same source SDK path. Each
emits exact JSON case/assertion/rejection receipts. These cohorts overlap.

## Native and compiler/sanitizer scope

```sh
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release --output-on-failure
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release -V -R '^itch\.(validation_demo_reference|independent_reference|l3_reference|streaming_reference|context_reference|auction_reference|admin_reference|hy_reference)$'
```

Expected Release CTest:153 native/SDK/contract targets. Map each verbose reference's
actual canonical SHA-256 to its test name and compare with `native.frozen_hashes`;
an unordered count alone is insufficient.

For master-gcc-debug,master-clang-debug,master-clang-release andaccelerated-sanitizer,
rebuild gig_itch_completion_capsule_tests andgig_itch_source_recovery_tests, then run
`ctest --test-dir <build> --output-on-failure -R '^itch\.(completed_source_capsule|source_hot_recovery)$'`.
Expected two tests per configuration. Current native/build/SDK inputs are byte-equal
to verified406f88f; unchanged compatible builds are reused where no compile is needed.
This is not a new full historical five-way matrix or Python sanitizer instrumentation.

The native capsule target reports535 assertions and actual PMR failure positions
plain restore57/encode58,gzip restore61/encode62. The earlier source coordinator
retains331 assertions. The SDK capsule/completion/product cohort has33 tests, with
actual child-process restoration. Active-v1 formats and the eight identities stay
unchanged. No opaque-state migration or arbitrary compressed offset is inferred.

## Passive ELF and actual source-vintage evidence

ELF_DEPENDENCY_BINDINGS.md defines the exact supplied manifest and passive parser.
Retained `elf-actual-manifest.json` and `elf-actual-closure.json` bind8 named original
files and19 explicit edges with0 unresolved. The result's internal canonical digest
and every file hash are independently checkable. The commit is a caller label;
NEEDED/SONAME/header matches are not actual loader choice, symbol-version/dlopen
qualification, publisher/build attestation or advisory clearance. No ldd/binary
execution/default search occurs. Sensitive root components reject before reads.

`statement-original-comparison.json` is an actual221,305-byte authored two-envelope
output of the new callable API, with its receipt. Original lexical values, row states,
source/period/unit/relationship checks, calculations and ancestry remain intact.
It is not observed provider data, a restatement oracle or an automatically accepted
old-format UI import. General original acceptance still needs its sources/criteria.

## Clean-source default and streaming packages

The retained package helpers/configuration/manifests document the actual runs. Only
the exact clean tested source was Git-archived. Before extraction, all sdist regular
members matched Git blobs at that SHA and the complete tracked inventory, allowing
only generated PKG-INFO. Expected1,856 tracked files /1,857 members. Absolute/parent
paths, duplicates, links and unexpected types reject; tarfile's data filter is used.
Do not blindly rerun helpers at a different HEAD or overwrite old work directories.
Use a fresh detached checkout/archive at the tested SHA.

Build offline from that source with installed tools: `python -m build --sdist
--no-isolation`; build wheels from the byte-verified extracted sdist, using separate
default/streaming output directories and PIP_NO_INDEX=1. Actual build variables:

```sh
PATH=/workspace/gig-tools/bin:$PATH CC=/usr/bin/gcc CXX=/usr/bin/g++ CMAKE_ARGS=-DCMAKE_MAKE_PROGRAM=/workspace/gig-tools/bin/ninja
```

Streaming additionally sets `-DGIG_BUILD_ITCH_STREAMING=ON`. Installed local zlib
satisfies that optional profile; no dependency download/upgrade occurs. Install each
wheel separately with `pip install --no-index --no-deps --target <new-target>`.
The filenames match but their profile hashes differ; never overwrite or mix profiles.

The portable installed-checks.py reads the retained package-configuration.json through
GIG_RECOVERY_CONFIG; the isolated target is GIG_RECOVERY_INSTALLED.
It asserts loading from the explicit isolated target and runs from extracted source.
Use the recorded SDK-path environment variable, GIG_TEST_SOURCE_COMMIT and absolute
venv Python. Default selected source count873 andSDK8; streaming capsule/completion/
product count33 andSDK8. Both socket/application-factory guards stay active. The
explicit hashed native fixture executable supplies authored input only, never an
alternate SDK. Six default cross-language scripts also run from extracted source.

After archive byte verification only, existing locked node_modules was linked for
local resolution. Extracted-source sourceAccounting/sourceAccountingChecks/
financialSourceContract/accessibilityNavigation tests ran with actual extracted
Python generators and isolated SDK:176 cases (148+28). No fresh JS install or browser
launch. All source/backend imports resolve from extracted files, not current root.

Exact installed-check commands, with the extracted source as cwd (substitute fresh
output paths when reproducing):

```sh
GIG_RECOVERY_CONFIG=/workspace/gig-development/docs/qualification/development-continuation/nov21-sprint-recovery-evidence/package-configuration.json GIG_RECOVERY_INSTALLED=/workspace/gig-development/work/nov21-recovery-packaging/installed-default PYTHONPATH=/workspace/gig-development/work/nov21-recovery-packaging/installed-default GIG_TEST_SOURCE_COMMIT=ec255121d070f80e7e92d958f223bf0701baa806 /workspace/gig-development/work/venv/bin/python /workspace/gig-development/docs/qualification/development-continuation/nov21-sprint-recovery-evidence/package-installed-checks.py source
GIG_RECOVERY_CONFIG=/workspace/gig-development/docs/qualification/development-continuation/nov21-sprint-recovery-evidence/package-configuration.json GIG_RECOVERY_INSTALLED=/workspace/gig-development/work/nov21-recovery-packaging/installed-streaming PYTHONPATH=/workspace/gig-development/work/nov21-recovery-packaging/installed-streaming GIG_TEST_SOURCE_COMMIT=ec255121d070f80e7e92d958f223bf0701baa806 GIG_ITCH_FIXTURE=/workspace/gig-development/build/recovery-release/gig_itch_durable_checkpoint_tests /workspace/gig-development/work/venv/bin/python /workspace/gig-development/docs/qualification/development-continuation/nov21-sprint-recovery-evidence/package-installed-checks.py streaming
```

Use mode `sdk` with each profile's same isolated environment for eight consumers.

Actual source/default/streaming artifact hashes are in the evidence. These identify
this build, not two-build bit-identical reproducibility or a fresh full compiler-wheel
matrix. Later evidence-only documentation is outside tested package bytes.

Source-lock SBOM generation uses build_offline_sbom.py with the tested SHA label and
a fresh exclusive output path. Expected85 components/seven hashed inputs. This and
pip check do not establish current vulnerability/backport or target security clearance.

All seven external blockers and eight partial criteria retain their exact authority,
source,physical hardware and authorization dependencies. No fixtures, emulation,
documentation or passive metadata replace those actual acceptance observations.
