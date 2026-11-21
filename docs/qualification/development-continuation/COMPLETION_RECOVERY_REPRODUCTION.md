# Recovered completion engineering — offline reproduction

Protected baseline: `7cd99d4afd98f58330732ecfc0fd0b3303c49a3b`.
Tested integrated source: `9e6218e5387cd8baaf5e5c950718ee48ab266753`.
No application/server, provider connection, deployment, trading or paid resource is
part of these procedures. Use fresh work/output directories and preserve existing
changes. Current dependencies/toolchains were already installed. Source packages
exclude later evidence-only documentation by design.

## Current source verification

From the repository root:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/run_no_launch_suite.py
npm --prefix terminal/web test
npm --prefix terminal/web run build
work/venv/bin/python -m unittest discover -s tests -p test_local_artifact_inventory.py -v
work/venv/bin/python tests/test_offline_sbom.py
work/venv/bin/python tests/test_sdist_patterns.py
work/venv/bin/python -m pip check
```

Expected: 1,042 guarded Python, 345 frontend, 35 inventory, 13 SBOM and three source-
package-pattern checks, with zero failures/errors/skips. The Python cohort forbids
socket bind/connect/connect_ex and application creation, checks its exact count and
asserts that no application exists. Frontend uses static React rendering and pure
contracts; it does not launch a browser/server. TypeScript and Vite build must pass.
Vite chunk-size and Starlette/httpx deprecation warnings remain visible.

Focused new modules: terminal.providers.test_kraken_public_session (29),
terminal.test_itch_source_completion (11), terminal.stocks.test_xbrl_cross_role (35).
They account for 75 new guarded checks; counts measure cohorts, not whole acceptance.
Source package tests overlap with focused/native checks and must not be summed.

Nine existing actual cross-language scripts, each under
PYTHONPATH=build/recovery-release/python:., also pass:
check_xbrl_statement_contract.py, check_xbrl_accuracy_contract.py,
check_xbrl_vintage_contract.py, check_xbrl_calculation_report_contract.py,
check_offline_import_contract.py, check_statement_set_contract.py,
check_accounting_statements_contract.py, check_itch_product_contract.py and
check_trade_contract.py, all under terminal/tests/. Their final JSON lines retain
case/assertion/rejection counts and explicit no-launch/provider scope.

## Native source completion and frozen identities

The recovery implementation and test were freshly rebuilt in five existing build
configurations, retaining their compiler/sanitizer flags. Example:

```sh
/workspace/gig-tools/bin/cmake --build build/recovery-release --target _native gig_itch_source_recovery_tests gig_itch_durable_checkpoint_tests -j 2
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release -V -R '^itch.source_hot_recovery$'
/workspace/gig-tools/bin/cmake --build build/recovery-release -j 2
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release --output-on-failure
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release -V -R '^itch\.(validation_demo_reference|independent_reference|l3_reference|streaming_reference|context_reference|auction_reference|admin_reference|hy_reference)$'
```

Expected full Release CTest:152, including native, SDK and contract targets. The source
recovery target reports331 assertions, 67 legacy PMR positions and66 new completion
PMR positions. Rebuild and run the same source-recovery target in master-gcc-debug,
master-clang-debug, master-clang-release and accelerated-sanitizer. All five pass.
This is focused fresh compilation on those configurations, not a new full five-way
historical matrix or Python sanitizer instrumentation.

Match the eight actual `canonical_sha256` values against protected baseline evidence.
No value can be inferred from a passing test count. Plain/single-gzip terminator/EOF,
trailer/CRC, seeded boundaries, immutable inputs, write refusal and PMR cleanup are
native tests. The SDK suite adds actual child-process completion and no fallback.
Serialized finished v1 images, partial frames and arbitrary compressed seeks remain
unsupported; do not manufacture migration/observed-source guarantees.

## Actual local inventory and acceptance authority

LOCAL_ARTIFACT_INVENTORY.md documents the passive command and its exact bounded
scope. Actual retained snapshot:24 distributions, 2,151 RECORD artifacts, two named
native ELFs and1,437 installed-ok dpkg records. The source commit is a caller label;
RECORD and ELF hashes are not publisher/build attestations. No advisory matching,
private-edge clearance, kernel/ELF dependency closure or OS package-file integrity
is established. Receipt file bytes and its internal canonical digest are checkable.

ORIGINAL_ACCEPTANCE_AUTHORITY.md covers all16 non-COMPLETE rows. Read-only audit
commit67ad42d08daf45d8c523c733587cdbd88852b81d was recovered; its176 normalized rows
and source catalog explicitly are not a universal original master. Raw H01–H07
attachments and H08 master remain absent. No original estimator/oracle was invented.
FREE_QUALIFICATION_OPTIONS.md records official free paths and their exact owner/use/
allowance gates. No workflow or provider acquisition is authorized by this procedure.

## Safe source packages and isolated SDK profiles

The retained packaging helper/configuration and manifests describe the actual run.
Only a clean exact tested HEAD was Git-archived. Every regular sdist member must
match `git show <tested-source>:<path>` and the tracked tree; PKG-INFO is the sole
allowed generated member. Reject absolute/parent paths, duplicates, links and
unexpected types before tarfile extraction with `filter='data'`. The actual archive
has1,755 tracked files plus PKG-INFO. Never rerun archival helpers blindly against
an evidence-only later HEAD or overwrite retained work directories.

The sdist is built offline with `python -m build --sdist --no-isolation`. Both GCC
wheels are built from that verified extracted source into separate directories;
set PIP_NO_INDEX=1 and retain the already installed build tools. Actual variables:

```sh
PATH=/workspace/gig-tools/bin:$PATH CC=/usr/bin/gcc CXX=/usr/bin/g++ CMAKE_ARGS=-DCMAKE_MAKE_PROGRAM=/workspace/gig-tools/bin/ninja
```

The streaming profile additionally sets `-DGIG_BUILD_ITCH_STREAMING=ON`; its zlib is
already available locally. No dependency installation/upgrade or registry fetch is
needed. Install each profile separately with `pip install --no-index --no-deps
--target <new-isolated-target> <corresponding-wheel>`. Default and streaming wheels
share the public wheel filename but have separate hashes/configuration scopes;
never overwrite one with the other or claim one profile's evidence for both.

With extracted source as cwd, installed-checks.py reads the retained configuration,
asserts exact SDK loading from GIG_COMPLETION_INSTALLED, forbids sockets/application
factory and checks expected counts. The default profile runs773 selected source
checks, eight SDK consumers, six existing contracts and148 actual extracted-source
Python-to-TypeScript-to-React checks. Existing locked node_modules is linked only
after archive byte validation; no fresh JS dependency install/browser launch occurs.

The streaming profile runs eight SDK consumers plus22 source-completion/product
checks. GIG_ITCH_FIXTURE explicitly names the existing native durable-checkpoint
fixture generator; its actual bytes/hash are retained. It supplies authored input
only, not an alternate SDK. The isolated compiled streaming SDK performs recovery;
source package/backend imports resolve from the extracted tree. A test fixture is
not actual observed initialization, terminal-image migration or independent provider
reference. No SDK fallback or live source transport is permitted.

The manifest retains actual archive/default-wheel/streaming-wheel bytes and hashes.
Two-build byte-identical reproducibility is not claimed; these hashes identify the
actual verified builds. Read current source/receipt hashes from
COMPLETION_RECOVERY_EVIDENCE.json and preserve earlier receipts with original scope.
