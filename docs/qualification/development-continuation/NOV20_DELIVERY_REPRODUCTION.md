# November 20 offline developer reproduction

Tested source: `9be1c0d8293444e517af67fe2a57fd1be599277c`.
Evidence: NOV20_DELIVERY_EVIDENCE.json and `nov20-delivery-evidence/`.
Do not launch GIG, application servers, live providers, deployment or owner acceptance.
Use a fresh isolated checkout/archive; preserve an existing worktree and never reset
it to reproduce this checkpoint. Dependencies/toolchains were already available at
$0. Commands below ran from the repository root unless another working directory is
explicitly stated. Current Python is 3.12.14; fresh wheel compiler is GCC 14.2;
Node is 24.19.0. Native build inputs did not change.

## Verify retained receipts and current runtime files

This read-only check works from the final evidence commit. Runtime files must match
the tested source; documentation is deliberately outside that runtime hash list.

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib,json,subprocess
base=Path('docs/qualification/development-continuation')
e=json.loads((base/'NOV20_DELIVERY_EVIDENCE.json').read_text())
for row in e['retained_receipts']+e['source_files']:
 p=Path(row['path']);data=p.read_bytes()
 assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],p
for row in e['source_files']:
 data=subprocess.check_output(['git','show',e['tested_source']+':'+row['path']])
 assert hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
print('All retained receipts and runtime inputs verified')
PY
```

## Python, frontend and existing contracts

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/run_no_launch_suite.py
npm --prefix terminal/web test
npm --prefix terminal/web run build
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_xbrl_statement_contract.py
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_xbrl_accuracy_contract.py
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_xbrl_vintage_contract.py
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_xbrl_calculation_report_contract.py
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_offline_import_contract.py
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_statement_set_contract.py
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_accounting_statements_contract.py
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_itch_product_contract.py
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_trade_contract.py
work/venv/bin/python tests/test_offline_sbom.py
work/venv/bin/python tests/test_sdist_patterns.py
work/venv/bin/python -m pip check
```

Expected current selected counts: 967 guarded Python; 345 frontend; 13 SBOM; three
source-package-pattern tests. All must pass with zero skips. The no-launch harness
checks its exact cohort before execution and forbids sockets/application creation.
The nine cross-language scripts emit their actual counts as final JSON lines.

The three newly registered frontend modules are sourceAccounting.test.ts (24),
sourceAccountingChecks.test.ts (32) and financialSourceContract.test.ts (92). They
invoke actual original-byte Python fixture exports under socket guards. No React
application/browser is started; rendering uses React server-side static markup.
Observed-origin metadata in authored permission fixtures is not real provider
qualification. Independent browser XML/issuer authentication is explicitly absent.

## Native compiler/sanitizer and frozen identities

```sh
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release --output-on-failure -R '^(itch\.(source_hot_recovery|durable_checkpoint|hot_context_checkpoint|reconstruction_checkpoint|reconstruction_recovery_boundary)|replay\.hot_checkpoint)$'
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release -V -R '^itch\.(validation_demo_reference|independent_reference|l3_reference|streaming_reference|context_reference|auction_reference|admin_reference|hy_reference)$'
/workspace/gig-tools/bin/ctest --test-dir build/master-gcc-debug --output-on-failure -R '^itch\.(source_hot_recovery|durable_checkpoint)$'
/workspace/gig-tools/bin/ctest --test-dir build/master-clang-debug --output-on-failure -R '^itch\.(source_hot_recovery|durable_checkpoint)$'
/workspace/gig-tools/bin/ctest --test-dir build/master-clang-release --output-on-failure -R '^itch\.(source_hot_recovery|durable_checkpoint)$'
/workspace/gig-tools/bin/ctest --test-dir build/accelerated-sanitizer --output-on-failure -R '^itch\.(source_hot_recovery|durable_checkpoint)$'
```

Expected 6 + 2 + 2 + 2 + 2 focused checks and eight frozen references. Match every
canonical SHA-256 against `native.frozen_hashes` in the evidence; do not merely count
test names. These runs reused existing byte-equivalent builds; the sanitizer scope
is native ASan+UBSan, not Python instrumentation or fresh full-compiler qualification.
Build-tree SDK consumer command was a socket-guarded unittest run of
tests/test_python.py using PYTHONPATH=build/recovery-release/python (eight tests).

## Clean-source packaging

Use a new work directory. Retained package-source.py/check-sdist.py show the exact
executed source archival and member verification procedure; they assert the tested
SHA/clean tree and intentionally refuse being rerun blindly at a different HEAD.
Create a separate detached worktree at the tested SHA when reproducing those helpers;
choose new output directories instead of overwriting existing evidence.

1. Git-archive the tested SHA. Reject absolute/parent paths, duplicate members and
   non-regular/non-directory types; extract using tarfile `filter='data'`.
2. Build the sdist from that clean archived source using the installed build tools:
   `work/venv/bin/python -m build --sdist --no-isolation --outdir <new-packages> <archived-source>`.
3. Compare every sdist regular member against `git ls-tree -r` and `git show` at the
   exact tested SHA, allowing only generated PKG-INFO. Expected 1,685 tracked files /
   1,686 members. Validate all archive paths/types/duplicates before safe extraction.
4. Build the fresh wheel from the verified extracted source, using absolute output
   paths and these already installed tools:

```sh
PATH=/workspace/gig-tools/bin:$PATH CXX=/usr/bin/g++ CC=/usr/bin/gcc CMAKE_ARGS=-DCMAKE_MAKE_PROGRAM=/workspace/gig-tools/bin/ninja work/venv/bin/python -m build --wheel --no-isolation --outdir /workspace/gig-development/work/nov20-delivery/packages work/nov20-delivery/extracted/gig_microstructure-0.1.1
work/venv/bin/python -m pip install --no-deps --no-index --target work/nov20-delivery/installed work/nov20-delivery/packages/gig_microstructure-0.1.1-cp312-cp312-linux_x86_64.whl
```

These are the actual run paths; substitute fresh work paths when reproducing. No
release/upload or package-registry access was used. Hashes bind this actual build;
a later build may differ in packaging metadata. Two-build bit identity is unclaimed.
Later evidence-only documentation is not part of the tested source archive.

## Isolated installed consumers and source/UI contracts

Run consumers from the extracted source root with absolute PYTHONPATH pointing to
the fresh installed SDK and GIG_TEST_SOURCE_COMMIT set to the exact tested SHA.
Assert SDK loading from that isolated directory. tests/test_python.py must pass all
eight consumers under socket guards.

The retained packaging-verification.json lists the exact 49 selected source modules,
709 cases and six installed cross-language scripts. The portable helper
nov20-delivery-evidence/reproduce-installed-source.py reads that receipt instead of
depending on an old workspace's test list. With the extracted source as cwd, set:

```sh
GIG_DELIVERY_PACKAGE_RECEIPT=/workspace/gig-development/docs/qualification/development-continuation/nov20-delivery-evidence/packaging-verification.json GIG_DELIVERY_INSTALLED=/workspace/gig-development/work/nov20-delivery/installed PYTHONPATH=/workspace/gig-development/work/nov20-delivery/installed /workspace/gig-development/work/venv/bin/python /workspace/gig-development/docs/qualification/development-continuation/nov20-delivery-evidence/reproduce-installed-source.py
```

It prohibits both sockets and application construction, asserts exactly 709 tests
and rejects skips. No old untracked runner file is required. Installed contracts are
check_xbrl_accuracy_contract.py, check_xbrl_vintage_contract.py,
check_xbrl_calculation_report_contract.py, check_offline_import_contract.py,
check_statement_set_contract.py and check_accounting_statements_contract.py, all
from the extracted tree with that same installed SDK path.

Only after archive byte verification, the existing locked terminal/web/node_modules
was linked into the extracted frontend for offline dependency resolution. From the
extracted terminal/web directory, the three source-accounting test modules ran via
Node --experimental-strip-types --test, with GIG_TEST_PYTHON set to the absolute venv
Python and PYTHONPATH set to the isolated SDK plus extracted source. All 148 passed;
actual Python generators resolved inside the extracted tree. No JS reinstall,
browser/app/server or current-worktree backend substitution occurred.

The sixteen generated exports are retained as installed-source-accounting-fixtures.json
with a hash receipt. They are authored offline examples, not financial observations.

## Source-lock inventory and boundaries

```sh
work/venv/bin/python scripts/build_offline_sbom.py --source-commit 9be1c0d8293444e517af67fe2a57fd1be599277c --output <new-private-output>.cdx.json
```

Expected 85 source-lock components and seven exact input hashes. The source SHA is
an explicitly supplied label; input hashes identify actual bytes. This inventory,
pip check and package tests do not establish fresh advisory/target OS/native/edge
security clearance. Existing advisory snapshots retain their earlier dates/scope.

No application, browser/device, provider, ARM64 workflow, paid resource, deployment,
trading or owner acceptance is part of these procedures. All seven blocked rows and
the eight stronger partial criteria remain unresolved as documented in the matrix.
