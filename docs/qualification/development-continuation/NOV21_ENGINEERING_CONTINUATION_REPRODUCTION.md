# November 21 implementation continuation reproduction

Exact tested source: `3cbe7b32089c86a3899b3808b6fdebbad9e817d0` on
`development/gig-ui-redesign`. Final enclosing checkpoint changes documentation and
retained evidence only. Protected baseline remains an ancestor; no reset, discard,
force push, application/server launch, provider access or paid resource was used.

From a source checkout, with existing offline build dependencies and native SDK:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/run_no_launch_suite.py
GIG_TEST_PYTHON="$PWD/work/venv/bin/python" PYTHONPATH="$PWD/build/recovery-release/python" npm --prefix terminal/web test
npm --prefix terminal/web run build
/workspace/gig-tools/bin/cmake --build build/recovery-release -j 2
/workspace/gig-tools/bin/ctest --test-dir build/recovery-release --output-on-failure -j 2
```

The exact guarded Python cohort fixes 1,212 tests and rejects sockets/application
factories. Frontend fixes 416 registered tests; 43 new comparison cases generate 19
real authored Python export variants and verify actual React output and strict
admission. These are offline developer checks, not browser/device/AT acceptance.
Other native configurations use the existing master-gcc-debug, master-clang-debug,
master-clang-release and accelerated-sanitizer build directories. Preserve their
recorded CMake configurations; sanitizer selection/flags are in the retained
native receipt. Native test binaries/SDK checks are developer verification, not
application launch. The sanitizer profile is targeted and is not the full native
cohort. Exact compiler versions, counts and commands are evidence-bound.

Nine current cross-language checks are `terminal/tests/check_{xbrl_statement,
xbrl_accuracy,xbrl_vintage,xbrl_calculation_report,offline_import,statement_set,
accounting_statements,itch_product,trade}_contract.py`. Security checks are the
local/ELF inventory tests, offline SBOM and sdist-pattern tests and pip check.
Inventories are passive and explicitly do not claim advisory or target clearance.

The new V9 profile and its adversarial fixtures are documented in
EFFECTIVE_CROSS_ROLE_CLOSED_EXPLICIT_V9.md. The supervised Kraken consumer's explicit
opt-in/recording limitations are in the root KRAKEN_SUPERVISED_JOINT_PROFILE.md.
The comparison consumer contract is in SOURCE_STATEMENT_VINTAGE_COMPARISON.md.

Fresh packaging uses a clean exact-commit Git archive, verifies every sdist member
against tracked source bytes, then builds fresh default and streaming wheels with
no-index dependencies. Installed SDK path checks prevent source-tree fallback.
SDK/source/recovery consumers, generated comparison exports, TypeScript/React tests
and the production build run from the extracted clean sdist. Retained helper scripts,
configuration, logs, source/archive/wheel hashes and final manifests accompany the
evidence receipt. No two-build bit-reproducibility claim is made. Earlier protected
receipts retain their original source/configuration and are not current reruns.
