# SEC integration repair — root-cause record

Baseline ee945723a01c589bbe975f23dba06d05e9f686ca on feat/atlas-final-release;
October26,2026 America/New_York. Clean starting worktree;remote baseline verified.

Inspection before implementation confirms:
1. StockWorkspace.permission and configuration compare SEC booleans to literal'1'.
   Owner-provided'true' therefore disables access and is reported missing.
2. start_terminal.sh execs the Python server inheriting only exported process variables.
   Assignments in another terminal/unexported shell or an older process do not propagate.
   No persistent SEC configuration mechanism was loaded on startup.
3. User-Agent validation was printable8–160 characters containing'@',and diagnostics
   listed the variable as missing only when absent,not when present but invalid.
4. Existing data pipeline already uses AAPL CIK0000320193,fixed official submissions and
   companyfacts URLs,bounded bodies,timeouts,one-request/second pacing,no automatic retry,
   and separate partial-component acceptance. Exact selected financials retain units,
   periods,filing identity and source hashes. Cache is process-local,not persistent SEC
   storage. Existing annual/quarter/YTD filters must not be weakened or relabelled TTM.

Planned narrow repair:shared SEC boolean/identity validation;private bounded JSON settings
with exported environment precedence;safe setup/check helper;startup/readiness parity;
explicit refresh cache/cooldown and error disclosures;fixture/browser validation. No
Alpaca gate,execution/risk control or native source change. Live SEC requests require
valid owner configuration;none is configured in this Codex runtime at inspection.

## Repairs and additional findings

The true-flag failure was independently reproduced from the baseline source:ready:false
with both flag names missing;shared parsing now returns ready:true for valid authored
identity. Missing User-Agent remains blocked deliberately;no contact was invented.
Private configuration loads for both normal startup and direct ASGI construction. Exported
values win;malformed private settings disable SEC only. Startup prints sanitized readiness.
Helper/template/docs provide reproducible restart configuration without shell sourcing.

Readiness and missing-key diagnostics now validate format,not just presence;the header
must contain an application identity and contact email,with printable bounded characters
and no header injection. No full contact/headers are exposed by configuration diagnostics.
The health fixture-safety boundary also used literal1;shared SEC parsing now refuses
fixture tests on an observed source enabled with true/yes/on BEFORE collection begins.
fixture-boundary-before.log reproduces the old unsafe safe:true result;regression added.

HTTP/browser refresh reuses successful SEC cache for60seconds,after policy checks. Direct
internal refresh retains its existing forced-refresh default;no Alpaca semantics change.
Existing pacing,timeout,body limits and HTTP429/503 cooldown remain. Partial Company Facts
failure previously erased accepted financials if filings succeeded;partial-cache-before.log
reproduces it. The repair retains the entire accepted SEC packet and reports a sanitized
error rather than mixing new filings with old financial provenance. All-component failure
keeps its prior diagnostic behavior. The original274-test regression caught a diagnostic
precedence error in the first repair;it was corrected without changing assertions.

A cancelled refresh previously left the new status marker RUNNING;cancellation-before.log
reproduces this. It now reports CANCELLED,propagates cancellation and publishes no data.
The UI reads cached status after a failed refresh(NO acquisition retry),shows retained
reported facts with the actual error,and fences stale responses during company switching.

New SEC status panel distinguishes blocked/loading/reported/partial/stale/unavailable/error;
derived ratios remain separately labelled with backend formula/source metadata. No numeric
financial calculation or annual/quarter/YTD normalization was rewritten. No values fabricated.

## Validation scope

17 new focused cases,within86 combined consumer cases per Release/Debug/sanitizer. Existing
274 terminal cases per configuration preserved. Frontend14 tests;security46;verifiedTLS8;
installed-wheel8+6;packaging3;eight Release canonical references;original browser91 plus6
SEC browser scenarios. Exact final counts/hashes and file inventory are in SEC_EVIDENCE.json.
No native source/build/workflow change,no new dependency,no main merge or workflow launch.
No new hosted/ARM64 qualification is claimed. Both Python sanitizer live leak checkpoints0.

Initial SEC browser fixture failures exposed an inconsistent authored expiry/rate clock
and cross-scenario cooldown carryover. Fixtures now advance one coherent clock across
expiry/scenario boundaries;production pacing/cooldown checks were NOT disabled. Dedicated
fresh fixture server and exact status-badge checks pass. All original failure logs retained.

Live verification:NOT ATTEMPTED. This runtime lacks approved SEC identifying configuration;
Codespaces configuration is not inherited. No public SEC or other market-data request was
made. See SEC_SETUP.md for the owner-run check,private configuration and bounded acceptance.

## Final counted outcomes

|Cohort|Pass|Fail|Skip|
|---|---:|---:|---:|
|Terminal Release/Debug/sanitized native-binding consumers|274 each|0|0|
|Combined research+SEC consumers(includes17 new SEC cases)|86 each|0|0|
|Frontend formatting/period/source/state unit tests|14|0|0|
|Origin/proof/Codespaces security|46|0|0|
|Verified TLS/WSS rewritten-proxy integration|8|0|0|
|Installed native wheel interface/export contracts|8+6|0|0|
|Packaging pattern regressions|3|0|0|
|Release native frozen reference identities|8|0|0|
|Original browser journeys/SEC-specific browser journeys|91+6|0|0|
|Total counted configuration/test outcomes|1270|0|0|

Counts exclude initial failures/reruns and do not add17 SEC cases again(they are inside86).
Native C++ source and build definitions are unchanged;existing native binaries/wheel were
exercised,no fresh compiler build or six-configuration native rebuild claimed. Eight
canonical hashes were actually compared in the Release reference run. Prior full native
qualification is historical evidence,not a new hosted/ARM64 result for this change.
Three SEC screenshots are authored fixtures;reported-aapl.png and failed-refresh-cache-
preserved.png verify actual native-backed browser rendering,not real SEC reconciliation.
Screenshots/logs remain ignored;safe fingerprints and results are committed in the manifest.
Five owned fixture servers were stopped after browser evidence capture.
