# Offline developer reproduction

Source under test: `1ab1e17e1cfadc0e3d702bb18f9e65eb15057633`.
Receipts: NOV15_FINAL_SPRINT_EVIDENCE.json and nov15-final-evidence/.
These are developer checks; do not run application servers, provider commands or
owner-acceptance workflows. Dependencies/toolchains were already available locally.
Use a separate checkout/archive when reproducing; do not reset an existing worktree.

The current environment uses `work/venv/bin/python`, Node24.19.0, GCC14.2 and
Clang19.1.7. The existing source-enabled SDK is in build/recovery-release/python.
From the repository root:

```sh
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/run_no_launch_suite.py
npm --prefix terminal/web test
npm --prefix terminal/web run build
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_xbrl_statement_contract.py
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_xbrl_accuracy_contract.py
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_xbrl_vintage_contract.py
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_xbrl_calculation_report_contract.py
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_offline_import_contract.py
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_statement_set_contract.py
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_accounting_statements_contract.py
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_itch_product_contract.py
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release --output-on-failure -R '^(itch\.(source_hot_recovery|durable_checkpoint|hot_context_checkpoint|reconstruction_checkpoint|reconstruction_recovery_boundary)|replay\.hot_checkpoint)$'
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release -V -R '^itch\.(validation_demo_reference|independent_reference|l3_reference|streaming_reference|context_reference|auction_reference|admin_reference|hy_reference)$'
work/venv/bin/python tests/test_sdist_patterns.py
work/venv/bin/python tests/test_offline_sbom.py
work/venv/bin/python -m pip check
```

Repeat the two-test pattern `^itch\.(source_hot_recovery|durable_checkpoint)$` in
build/master-gcc-debug, build/master-clang-debug, build/master-clang-release and
build/accelerated-sanitizer. These current runs reused existing byte-equivalent
native builds. They are not full fresh compiler matrices. The GCC ASan+UBSan run
covers native tests, not Python instrumentation. All eight canonical hashes must
match the evidence JSON exactly.

Fresh packaging used `git archive` of the tested source into
work/nov15/package-source, followed by:

```sh
work/venv/bin/python -m build --sdist --no-isolation --outdir work/nov15/packages work/nov15/package-source
```

Before extraction, every regular archive member was compared byte-for-byte against
`git ls-tree -r` of the tested commit and its archived source copy. Absolute/parent
paths, duplicate members and unexpected file types were rejected; Python tarfile's
`filter='data'` was used. Inventory: 1,624 tracked files plus one generated PKG-INFO.
The receipt stores the compressed archive SHA256; this run does not claim two-build
bit-for-bit reproducibility. Extraction target was a new local work directory.
The fresh wheel command, from repository root, was:

```sh
PATH=/workspace/gig-tools/bin:$PATH CXX=/usr/bin/g++ CC=/usr/bin/gcc CMAKE_ARGS=-DCMAKE_MAKE_PROGRAM=/workspace/gig-tools/bin/ninja work/venv/bin/python -m build --wheel --no-isolation --outdir /workspace/gig-development/work/nov15/packages work/nov15/extracted/gig_microstructure-0.1.1
work/venv/bin/python -m pip install --no-deps --no-index --target work/nov15/installed work/nov15/packages/gig_microstructure-0.1.1-cp312-cp312-linux_x86_64.whl
```

Installed consumer checks run from the extracted source, with the absolute installed
SDK directory on PYTHONPATH and `GIG_TEST_SOURCE_COMMIT` set to the tested full SHA:
`tests/test_python.py` (8 tests). The installed source cohort uses the selected_names
in the no-launch receipt filtered for test_xbrl_, test_inline_, test_sec_filing_ingest,
test_sec_ingest_store, test_sec_ingest_cli, test_sec_multidoc, test_sec_source_expansion,
test_sec_transform_profile,test_kraken_book_session,test_python_json_ingress,
test_history_json_ingress or test_statement_set_source_acceptance (650 tests). It asserts SDK
loading from the isolated target and forbids socket bind/connect. No skips accepted.
The six installed cross-language scripts are check_xbrl_accuracy_contract.py,
check_xbrl_vintage_contract.py,check_xbrl_calculation_report_contract.py,
check_offline_import_contract.py,check_statement_set_contract.py and
check_accounting_statements_contract.py.
Source-lock SBOM was generated with build_offline_sbom.py --source-commit set to the
same SHA and a fresh --output path. Its inventory is not an advisory/target clearance.

Source hashes, all package hashes and 42 retained log/SBOM receipts are independently
checkable via SHA256 in NOV15_FINAL_SPRINT_EVIDENCE.json. Initial failure logs have their
original bytes; final successful logs are separately named. Full application/browser,
provider, physical-device, ARM64 and owner qualification remain outside this profile.

Current expected counts:908guarded Python,197frontend,9strict importer unit tests.
Focused new Python modules: test_xbrl_statement_set,test_xbrl_negative_dimensions,
test_xbrl_dimensional_calculation,test_python_json_ingress,test_history_json_ingress,
test_xbrl_dts_source_audit,test_statement_set_source_acceptance. They are explicitly
listed in run_no_launch_suite.py. It must report0failures/errors/skips and prohibit
both app construction and network sockets. Private ingress returns6exports/23negative
admissions;source statement consumer returns5sets/4cutoffs/23v2packets/1018assertions/
7re-signed rejections. No test harness wrapper is a new public schema.

Reconstruct source archive from the tested Git SHA in a new workdirectory only.
Check all tracked regular files byte-for-byte, plus generated PKG-INFO,before safe
extraction;the current archive has1625members. Do not reuse the interrupted older
d24175e source-directory or overwrite its partial package/logs. A clean tree is
required before archiving;preserve any pending work and choose a separate checkout
if needed. Later reports/evidence are excluded from the tested package by design.

November15new guarded modules:test_xbrl_negative_only_dimensions,
test_inline_dts_source_audit,test_xbrl_accounting_relationships and
test_xbrl_accounting_statements. New accounting contract consumes7actual exported
packets and verifies224assertions/7tamper rejections. Root actual invalid abstract/
period equality reproduction and fixture correction are retained separately.
Native/core/SDK/build inputs were byte-checked unchanged;fresh default SDK compiled
from this source,then all installed source regressions and6contracts passed.
The previous interrupted packages/logs remain untouched in their work directories.
The eight-partial-criteria review and later evidence-only docs are not in these
source archives. Do not replace actual provider/target/owner acceptance with these
fixture results. No app/server/provider/deployment/trading/paid action is part of
this reproduction profile.
