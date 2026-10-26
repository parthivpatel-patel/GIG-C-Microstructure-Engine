# Phase4 validation evidence

## Final local matrix

|Cohort|Passed|Failed|Skipped|
|---|---:|---:|---:|
|GCC Debug / Release / ASan+UBSan native|155 each|0|0|
|Clang Debug / Release / ASan+UBSan native|155 each|0|0|
|Python terminal Release / Debug / sanitizer|274 each|0|0|
|Phase3+Phase4 Release / Debug / sanitizer|31 each(13+18)|0|0|
|Frontend unit|13|0|0|
|Origin/Host/proof security|46|0|0|
|HTTPS/WSS/proxy|8|0|0|
|Installed-wheel interface / export|8 /6|0|0|
|Packaging pattern regressions|3|0|0|
|Existing seven browser cohorts|91|0|0|
|New Phase4 browser journey|9|0|0|
|Total counted final checks|2029|0|0|

Eight native canonical identities matched all six native XML outputs;these are included
within930 native outcomes,not48 extra cases. Native C++ sources/toolchain definitions are
unchanged;tests execute existing validated native binaries,not newly compiled toolchains.
Installed wheel is the existing validated extension because its sources are unchanged.
Both Python sanitizer consumers report LIVE_LSAN_CHECK=0. New Python code is tested under
the actual sanitizer-bound engine but is not transformed into C++ sanitizer instrumentation.

Browser assets are built first and hashed before/after each original suite;no concurrent
asset compilation. All9 workspaces and90 viewport/theme combinations remain covered,
including NVDA→global AAPL. New browser uses a separate authored25-bar/missing-fact fixture,
ephemeral SQLite directory and no provider network. Screenshots/hashes are recorded.
New endpoint security tests include unauthorized origins,target mismatch,one-use proofs,
unknown targets and proof-authorized rewritten Codespaces headers. Actual external
Codespaces authentication and physical Android are owner gates.

## Reproduced development failures and repairs

|Evidence artifact under ignored build/atlas4|Finding|Repair|
|---|---|---|
|targeted.log|Private-directory negative test assumed mkdir0755 would override restrictive umask|Explicitly chmod the authored invalid directory0755;security assertion retained|
|hmm-tie-before.log|Equal extreme log likelihoods gave probability sums0.9999709/1.0000319|Max-shifted weights normalized by their own sum;equal-state/independent likelihood regressions|
|phase4-browser.log,phase4-server-before-proof.log,proof-target-before.log|New POSTs absent from explicit proof target allowlist;bootstrap403 before handler|Register exactly3 new paths;one-use,target/origin negative controls;browser save/model/scenario passes|
|phase4-browser-final.log|New browser expected missing item in fully populated fixture|Author an explicit missing2023 gross-profit fixture;retain missingness assertion,no expectation weakening|
|retention-gate-before.log|Observed-profile fixture stayed readable after retention approval removed|Recheck read gate after restart;preserve data for explicit owner deletion|
|stored-schema-before.log|Storage metadata inserted inside strict historical-v2 payload|Move storage metadata to outer wrapper;JSON Schema regression|
|log-return-before.log|Subtracting logs of nearly equal large closes lost a tiny return|Use log1p of exact simple return,with log-ratio fallback only near rounded−1;80-digit Decimal.ln reference|

These are defects/test-construction issues found in new Phase4 work,not claims of
reproduced old native-engine defects. Final tests preserve every original assertion and
canonical output. No timeout,warning or sanitizer check was suppressed. Corrupt existing
revision resave also fails explicitly rather than claiming idempotent success.

Late browser reproduction `risk-refresh-before.log` confirmed stale risk provenance
after an accepted price refresh. The response is now bound to symbol/receipt and
superseded reads are aborted;the new browser assertion checks the new canonical provenance.

Authored diagnostic/scenario results also remain bound to the exact inputs that produced
them;editing inputs hides superseded output until calculation matches the current inputs.

## Reproduction

Use the validated Python environments and existing CMake directories. Commands and log
hashes are in phase4_evidence.json. Core commands:

```bash
python terminal/tests/run_native_suite.py --expected-tests 274
python -m unittest terminal.stocks.test_phase3 terminal.stocks.test_phase4 -v
npm --prefix terminal/web test
python terminal/tests/run_atlas_browser_suite.py
node terminal/tests/atlas4-validation.mjs
python scripts/benchmark_atlas_models.py
```

The original driver requires loopback fixture servers8787/18787/18788/18789 as documented
in Phase2. The Phase4 journey additionally requires python terminal/tests/atlas4_fixture_server.py
on18792. These are authored test services,not deployment/provider services;never forward
them publicly. Keep global live-provider flags0. Sanitizer runner uses the existing
live-interpreter leak checkpoint and actual instrumented native bindings. Exact native
ctest commands and output counts are captured in the manifest.
