# Sprint 4 durable implementation progress

Baseline `4522948d94770ea94a6e152b68a695063d711fd4`.
Branch `feat/atlas-sprint-4-market-data-paper`,isolated worktree from that exact SHA.
Sprint3/release/main/audit worktrees and commits preserved.

## Historical core checkpoint

New `terminal/alpaca_wire.py` and `terminal/stocks/historical_v2.py` implement a default-disabled fixed-host transport boundary and explicit-feed exact-time historical client. Credentials are obtained only by a supplied future HTTP callback after authorization;no credential source was read or real HTTPWire invocation made during this task. FixtureWire is explicitly synthetic.

28 authored tests pass,0failures/skips. Coverage: exact timezone/nanosecond normalization,invalid timestamps,SIP900second boundary including1ns negative control,feed permissions,query bounds,redacted HTTP statuses,body/JSON budgets,pages,cursor loops,429bounded retry,ordered observations/identical-row dedup,conflicting identities,cancellation,cache expiry and permission rechecks. Initial test failures exposed an incorrectly authored fixture clock and bar-close `c` being mistaken for trade conditions;both corrected without weakening assertions. Source receipts retain physical counts;deduplicated records do not claim exactly-once tape completeness.

Limits:4pages×64records,512KiBwire/result,one active query,30second operation budget,16in-memory query results,60secondTTL,explicit deletion. No observed disk retention enabled. No automatic startup acquisition,no feed fallback,no session/calendar completeness claim. Official API profile references exist in the repository;no fresh official-doc retrieval or real-provider qualification is claimed.

Next exact action:implement paper-only adapter/normalization and durable-engine integration with deterministic broker fixtures;then historical/research API+browser workflows,streaming regressions,guides and complete affected validation. No Alpaca/provider/account/order operation is authorized.

## Paper protocol/engine checkpoint

Implemented `terminal/paper/alpaca.py`:fixed paper-host/path/order allowlist,default-disabled independently reviewed expiring session,account+session-bound journal,exact cent/whole-share account/order parsing,eligibility and fresh IEX reference requirements,stable double-collection with explicit non-atomic/exclusive-account-policy limitation,durable FILL-activity reconciliation rather than rounded average price,position/cash reconciliation,partial/terminal states,cancel uncertainty,kill/idempotent restart and safe finite errors. No credential reader or real provider was used by tests. The injectable HTTP boundary remains unauthorized by default.

Targeted combined cohort passes113tests(33new paper cases+52Sprint3+28historical),0failures/skips. New cases cover lost create acknowledgments,one-create behavior,actual POST429no-retry,exact partial fills with deliberately misleading rounded-average fields,duplicate/conflicting executions,cancel/fill race,pending cancel,unsupported replacements,unexplained cash/positions,unknown/stale references,blocked/wrong accounts,expiry,risk-profile binding,allocation rollback,restart and duplicate update hints. Tests use an independently authored integer provider ledger. Sprint3fake UI/API semantics preserved.

Real operation remains blocked:cloud/display/execution/audit-retention permissions,exclusive-account/coherence policy,actual source/account/order qualification and owner risk limits are not approved here. REST double-read is not claimed exchange-atomic. Fractional/subcent/unexplained-fee/cash profiles fail closed. No real provider UI is activated.

Next:connect historical adapter to source-bound research/API/UI and compatible bar-derived3D,add disabled provider-readiness API,then full regressions/browser/security/native checks and update existing guides.

## Historical research and disabled provider UI checkpoint

Recovered the interrupted integration without resetting or changing branches. Source-bound v2 historical APIs now support exact accepted revisions, trailing exact-return/SMA/drawdown and disclosed binary64 log-variation research, exact-endpoint multi-symbol comparison, separately gated exact-byte exports and explicit cache deletion. Historical bars have a separate bar-derived visualization input;no invented quotes/depth. Historical quotes can supply quote-compatible research;all paths preserve feed,adjustment,origin,exact source timestamps and receipt hashes.

Added independently gated paper-provider readiness/control APIs and UI alongside the unchanged fake sandbox. Construction does not access keys,accounts or HTTP. Starting a future qualified session requires independent execution/policy gates,explicit account/session/risk binding and all eight owner risk values. Added concentration admission checks. Browser controls do not grant permission. Default configuration remains disabled and creates no provider database.

Checkpoint verification:81 targeted Python tests(9newAPI+11research+28history+33paper),52Sprint3 tests,101frontend tests;all pass,zero failures/skips. TypeScript/production build passes. InitialJS242.59kB;new optional historical17kB and provider8.43kB chunks remain deferred. Existing514.41kBThree chunk warning is retained. No provider call,account access or paper order occurred;all broker operations used authored fixtures. Browser/full supported matrix verification follows;this checkpoint does not claim completed live qualification.

Next:focused transport/revocation tests,new historical/provider browser fixtures,existing browser/security/native regression checks,then update guides and evidence reports.

## Bounded transport and browser checkpoint

Added12no-socket tests of the actual HTTP reader via httpx.MockTransport:unknown/false/excessive lengths,compressed-response refusal,fragmented UTF8,redirect handling,credential boundary,history revocation during429wait,paper-session expiry during throttling,and default no-store behavior. The legacy v1 real historical route now requires the same independent cloud/display/IEX permission as v2;authored fixtures retain backward compatibility. This closes an alternate future authorization path without enabling any provider.

New ordinary-click Chromium workflow passes8checks:accepted historical IEX bars/trailing geometry,unsupported depth states,timeline/2D,exact-byte export,explicit historicalSIP quotes,symbol change isolation,fixture paper arm/idempotent submit/kill-cancel/native isolation,and light390px access. No page errors. Original test7/8 failure retained:incorrect test-only theme accessible-name selector (no product repair required);runner retry initially rejected TIME_WAIT bind,then adopted SO_REUSEADDR while retaining exclusive-port ownership checks. Repaired run passes8/8. Screenshots are authored fixture evidence only. Full supported regression matrix is running;remaining exact action:inspect its results,repair failures,finish broader browser/security/packaging evidence and existing guides.

## Readable comparison,accessibility and regression checkpoint

Historical multi-stock research now validates source revisions/symbols/exact endpoints before showing shared-scale percentage traces and readable exact-fraction tables. No nearest-neighbor price filling. New comparison parser regression raises the frontend cohort to102passing tests. Ordinary-click9check workflow passes,including AAPL/MSFT comparison and isolated paper fixture lifecycle. New table headers now declare scope explicitly:Chromium initially exposed unscoped header cells as generic cells;the original columnheader assertions now pass after the semantic repair. Original failed browser runs retained outsideGit. Screenshots remain authored-only;capture framing is being refined to show the new panels rather than the page header.

Full supported Python cohort passes823per configuration(Debug,Release,ASan/UBSan),2469outcomes total,zero final failures/skips. Native unchanged-source six-configuration rerun passes940CTest outcomes and48/48frozen hash comparisons. The initial older207stock cohort had1failure because the newly hardened legacy history gate correctly stopped a mocked-HTTP429test before transport;the test now declares specific authored history permission and still requires its original one-call429/cooldown assertions. All207then pass in each configuration. No provider was contacted.

Updated the nine existing operating/model/3D/interview guides for Sprint4,without replacing them or adding another audit. Remaining:finalized-asset browser/security/TLS/packaging and synthetic performance/source-evidence binding,then completion report. Default provider/retention/order gates remain off.

## Conservative paper-reference and final display checkpoint

Reproduced a new future-paper integration defect:the native server's reference callback accepted freshly received quotes with old/future source times,wrong feed or crossed/zero sides;it also replaced source age with receipt age. Two regression methods produced8failing assertions/subtests before repair. The callback now requires subscribed+authorizedIEX,exact source timestamp consistency,both source/receipt ages≤5seconds,ordered positive exact-cent best quotes,and conservative older source/receipt time. Both regression methods now pass. No provider action occurred. Strict Sprint4cohort is95;final supported matrix rerun is underway after this app change.

Visual inspection prompted bounded four-significant-digit headline formatting and explicit full-precision disclosure;exact calculations are unchanged. Historical comparison has explicit percent scale,symbol legend and shared-index axis description. Updated ordinary-click9check workflow passes on finalized assets. All102frontend tests pass. Added reproducible authored-only history/paper measurement tool:256historical rows and32create/cancel intents,virtual-time throttling,measured Python allocation/RSS and deterministic result hashes. Initial invalid benchmark timestamp fixture was rejected as intended and corrected;failure log retained. Final measurement will bind the committed source.

One broad browser run was correctly rejected by its asset-immutability guard after this developer rebuilt during that run. The complete final sequence now runs new then existing browser cohorts against finalized assets without recompilation. Do not count the rejected run as a final pass. Exact next action:collect finalmatrix/browser/TLS/packaging/performance results,bind safe evidence and finish final report. No provider qualification or current ARM64 claim.

## Configured schedule propagation checkpoint

Closed one remaining narrow integration gap:the default historical adapter now shares the already validated bounded session schedule used by LiveIEX,without another file read or provider acquisition. A configured authored schedule was previously ignored by history;the independent identity/state assertion failed before and passes after the one-line repair. Absent/out-of-coverage schedules remain UNKNOWN;no holiday/halt authority is invented. Sprint4strict cohort now96/96passes. Source is frozen for final regression/evidence closure;no additional features are planned in this assignment.
