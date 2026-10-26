# Phase8 local qualification and candidate closure

Executed final counted cohorts(no duplicate intermediate reruns):

|Cohort|Pass|Fail|Skip|
|---|---:|---:|---:|
|GCC Debug/Release/ASan+UBSan native|155 each|0|0|
|Clang Debug/Release/ASan+UBSan native|155 each|0|0|
|Terminal Release/Debug/sanitized native-binding consumers|274 each|0|0|
|Phase3+4+5+final consumers(13+18+20+18)|69 each|0|0|
|Frontend unit|13|0|0|
|Origin/proof/Codespaces/browser-access security|46|0|0|
|Verified TLS/WSS rewritten-Origin proxy|8|0|0|
|Installed-wheel interface/export contracts|8+6|0|0|
|Packaging include-pattern regressions|3|0|0|
|Browser original7/Phase4/Phase5/final|91+9+6+5|0|0|
|Total counted checks|2154|0|0|

48 hash comparisons(8×6) are inside930 native outcomes,not added to2154. All eight frozen
identities unchanged. Source engine/build/fixtures unchanged;existing compatible native
artifacts exercised,no stale changed-native-source build and no new compiler build claimed.
Python consumer sanitizer runs use existing ASan+UBSan native extension plus live LSan
checkpoint;both checkpoint results0. Python/third-party codec were not rebuilt with ASan.
No exact-HEAD ARM64,hosted workflow or independent physical machine claim.

## Reproduced defect and initial test failures

Final review added a regression proving explicitly incompatible price-unit revisions were
accepted. unit-mismatch-before.log fails1/1 on the original implementation. Minimal repair
adds source price_unit to the compatibility key;no rounding/FX or data reinterpretation.
Final69-case cohorts exercise this rejection and1/99 exact returns across all3 consumers.
A browser ingestion run also proved that a concurrent source load was rejected as generic
422. loader-busy-before.log reproduces expected409 versus old422. The endpoint now returns
HISTORY_INGEST_BUSY409 with an explicit wait/retry instruction;no queue,automatic retry or
partial revision is introduced. Browser sequencing waits for the actual load response AND
reported completion before ingestion. Both initial browser timeout logs are retained;
browser-final-finished.log passes5/5 on a fresh fixture server with final backend sources.
Other original failures were engineering/test invocation mistakes:app initialization
ordering corrected before initial10-case pass;wrong TestClient Host corrected without
relaxing Host rules;overlong authored horizon shortened to existing80-character limit;
nonexistent security-module and wrong packaging-interpreter commands corrected. Logs are
preserved,not counted as successful tests. No assertion/security control weakened.

## Reproduction

Use the existing validated terminal environment and native build configurations:

```bash
.venv/bin/python terminal/tests/run_native_suite.py --expected-tests 274
.venv/bin/python -m unittest terminal.stocks.test_phase3 terminal.stocks.test_phase4 terminal.stocks.test_phase5 terminal.stocks.test_final -v
npm --prefix terminal/web test
.venv/bin/python terminal/tests/run_atlas_browser_suite.py
node terminal/tests/atlas4-validation.mjs
node terminal/tests/atlas5-validation.mjs
node terminal/tests/atlas-final-validation.mjs
.venv/bin/python scripts/benchmark_atlas_final.py
```

Original driver builds first and checks asset identities across7 serial suites. Start
only authored loopback servers8787/18787/18788/18789/18792/18793/18794 using the respective
terminal/tests fixture-server scripts and actual native server. atlas5 and final browser
tests require fresh dedicated fixture processes/private stores every execution. Never
forward these fixture ports;they are test-only. Tests assert fixture identity before any
mutation. Source commands/log hashes,all screenshots,bundle/model/browser measurements,
canonical references and archive manifest are captured in final_evidence.json.

Artifact acceptance(source inventory) is separate from the2154 total. No publication,
tag,main merge,workflow dispatch or real-data acquisition. Requirement matrix retains
substantive incomplete/blocked capabilities;local green tests do not close observed gates.

Clean source artifact:698 intended byte-identical members fromdc3da0a37901d2a0604df241a2985cf0541a18c8;
required source trees complete;no databases/ZIPs/private outputs. Artifact acceptance is
separate from2154 test outcomes. Actual final branch ARM64 workflow requires owner review
of the preserved bootstrap-only branch guard before any separately authorized dispatch.
