# Offline developer reproduction

Source under test: `1434ad4cca0cffa31bb7d5986ee27a75ae081aa5`.
Receipts: REPORT_BINDING_EVIDENCE.json and report-binding-evidence/.
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
PYTHONPATH=build/recovery-release/python work/venv/bin/python terminal/tests/check_itch_product_contract.py
ctest --test-dir build/recovery-release --output-on-failure -R '^(itch\.(source_hot_recovery|durable_checkpoint|hot_context_checkpoint|reconstruction_checkpoint|reconstruction_recovery_boundary)|replay\.hot_checkpoint)$'
ctest --test-dir build/recovery-release -V -R '^itch\.(validation_demo_reference|independent_reference|l3_reference|streaming_reference|context_reference|auction_reference|admin_reference|hy_reference)$'
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
work/report-binding/package-source, followed by:

```sh
work/venv/bin/python -m build --sdist --no-isolation --outdir work/report-binding/packages work/report-binding/package-source
```

Before extraction, every regular archive member was compared byte-for-byte against
`git ls-tree -r` of the tested commit and its archived source copy. Absolute/parent
paths, duplicate members and unexpected file types were rejected; Python tarfile's
`filter='data'` was used. Inventory: 1,494 tracked files plus one generated PKG-INFO.
The receipt stores the compressed archive SHA256; this run does not claim two-build
bit-for-bit reproducibility. Extraction target was a new local work directory.
The fresh wheel command, from repository root, was:

```sh
PATH=/workspace/gig-tools/bin:$PATH CXX=/usr/bin/g++ CC=/usr/bin/gcc CMAKE_ARGS=-DCMAKE_MAKE_PROGRAM=/workspace/gig-tools/bin/ninja work/venv/bin/python -m build --wheel --no-isolation --outdir /workspace/gig-development/work/report-binding/packages work/report-binding/extracted/gig_microstructure-0.1.1
work/venv/bin/python -m pip install --no-deps --no-index --target work/report-binding/installed work/report-binding/packages/gig_microstructure-0.1.1-cp312-cp312-linux_x86_64.whl
```

Installed consumer checks run from the extracted source, with the absolute installed
SDK directory on PYTHONPATH and `GIG_TEST_SOURCE_COMMIT` set to the tested full SHA:
`tests/test_python.py` (8 tests). The installed source cohort uses the selected_names
in the no-launch receipt filtered for test_xbrl_, test_inline_, test_sec_filing_ingest,
test_sec_ingest_store, test_sec_ingest_cli, test_sec_multidoc, test_sec_source_expansion,
test_sec_transform_profile or test_kraken_book_session (466 tests). It asserts SDK
loading from the isolated target and forbids socket bind/connect. No skips accepted.
The three installed cross-language scripts are check_xbrl_accuracy_contract.py,
check_xbrl_vintage_contract.py and check_xbrl_calculation_report_contract.py.
Source-lock SBOM was generated with build_offline_sbom.py --source-commit set to the
same SHA and a fresh --output path. Its inventory is not an advisory/target clearance.

Source hashes, all package hashes and 39 retained log/SBOM receipts are independently
checkable via SHA256 in REPORT_BINDING_EVIDENCE.json. Initial failure logs have their
original bytes; final successful logs are separately named. Full application/browser,
provider, physical-device, ARM64 and owner qualification remain outside this profile.
