# Validation evidence

|Executed cohort|Pass|Fail|Skip|
|---|---:|---:|---:|
|GCC Debug / Release / ASan+UBSan native|155 each|0|0|
|Clang Debug / Release / ASan+UBSan native|155 each|0|0|
|Python terminal Release / Debug / sanitizer|274 each|0|0|
|Phase3+4+5 Release / Debug / sanitizer|51 each(13+18+20)|0|0|
|Frontend unit|13|0|0|
|Security / HTTPS-WSS|46 /8|0|0|
|Installed-wheel interface / exports|8 /6|0|0|
|Packaging pattern regressions|3|0|0|
|Existing seven browser cohorts / Phase4 / Phase5|91 /9 /6|0|0|
|Total counted checks|2095|0|0|

Counts are final outcomes,not every intermediate rerun. Eight canonical references are
compared in all six native XML outputs;those48 checks are inside930 native outcomes.
Native source/fixtures/build definitions unchanged;existing validated binaries exercised,
not newly compiled GCC/Clang toolchains. Installed wheel is the existing native wheel,
not a rebuilt extension. Both live-interpreter sanitizer leak checkpoints return0.

New20-case cohort covers multi-page/old-core compatibility,pagination/token encoding,
late-page rejection/no publication,disabled gates before fetch,backup/restart/corruption,
actual partial SQLite copy rollback,actual process exits before/after commit,completed
versus busy deadline handling,independent covariance/tails/shocks,missing/weight rejection,
training-only and walk-forward mutation controls,state-label invariance,normal Gaussian
tail constants,declared-calendar missingness,share units,raw accounting component identities,
HTTP429 no-retry/cooldown and explicit new endpoint proofs/unauthorized-origin denial.

Initial accounting fixture expected an equation to balance while supplying incompatible
literal components(targeted-expanded.log). Corrected authored inputs to1000=600+400;
production residual logic unchanged. A separate raw-fact fixture verifies1000=250+750,
100−40−60=0 and30−10−5+2−17=0 through the real parser. No observed statement was edited.
The backup deadline callback initially could report an already-completed copy as failed;
backup-done-before.log reproduces it. SQLITE_DONE is now distinguished from SQLITE_BUSY,
including zero remaining pages;pre-publication budget and rollback assertions retained.
An initial benchmark generator repeated one input modulo7;changed to modulo17 and asserted
8 unique revisions before recording final8-revision storage timings.

Browser assets are built first,then hashed throughout seven serial suites. New scenarios
exercise explicit ingestion,pinned30-record/2-page synthetic source,backup/delete/confirmed
restore,portfolio VaR.006,input invalidation,held-out/walk-forward identities and mobile
360/390 light/dark. Earlier90 all-workspace/theme/width combinations and NVDA→AAPL remain.
Headless Chromium/SwiftShader evidence is not physical Android/external Codespaces evidence.

Core reproduction:

```bash
python terminal/tests/run_native_suite.py --expected-tests 274
python -m unittest terminal.stocks.test_phase3 terminal.stocks.test_phase4 terminal.stocks.test_phase5 -v
npm --prefix terminal/web test
python terminal/tests/run_atlas_browser_suite.py
node terminal/tests/atlas4-validation.mjs
node terminal/tests/atlas5-validation.mjs
python scripts/benchmark_atlas_integration.py
```

Loopback fixture servers8787/18787/18788/18789 required by original driver;Phase4/5 use
18792/18793 via their named fixture-server scripts. Never forward fixture ports. Exact
commands,log hashes,screenshot hashes,source fingerprints and toolchain evidence are in
phase5_evidence.json. All figures are authored/research inputs,not market acceptance.

Final browser rerun initially timed out at backup/delete because a prior fixture process
retained an earlier private backup and revision. The no-overwrite backup policy correctly
returned422;deleting the new revision left the prior revision,contradicting the test's empty
list assumption. No production security/storage rule was relaxed. The browser test now
asserts empty private fixture storage before running;restart its dedicated fixture server
for each execution. A fresh server passed all6 scenarios with final built assets. Original
failure:phase5-browser-accepted-final.log;accepted rerun:phase5-browser-accepted-rerun.log.

Clean source archive built from the pushed implementation commit:673 intended members,
byte-identical inventory and required trees complete. Additional artifact acceptance,
not added as another CTest outcome to the2095 total. Screenshots inspected locally:
portfolio-dark.png and research-mobile-light.png;27 screenshot hashes retained.
