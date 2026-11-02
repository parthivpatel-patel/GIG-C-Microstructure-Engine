# Sprint 4 implementation and offline verification

Application baseline: `4522948d94770ea94a6e152b68a695063d711fd4` (Sprint3). Development branch: `feat/atlas-sprint-4-market-data-paper`. Final application checkpoint: `d40622ee201af9339326b14e810f2bfa56462be8`. The final evidence/report commit adds documentation only;its SHA is reported in delivery/Git history rather than self-embedded in a file.

## Outcome and scope

Implemented a bounded explicit-feed historical adapter,stock-specific trailing research and compatible visualization workflow,and separately gated paper-only broker adapter. All actual data/account/order interactions in this task were authored fixtures or local mock transports. No provider requests,credentials/account access,real paper orders,observed retention,public forwarding,paid resources,workflow dispatch,merges,tags or releases occurred. Existing SEC configuration and native C++ mathematical behavior were preserved.

This is an offline development candidate,not real-provider qualification,owner operational acceptance,complete historical reconstruction or production readiness. The owner-reported Sprint3 Codespaces acceptance and10,423SEC ticker mappings retain that attribution;this sprint did not remeasure a listed-stock universe.

| Package | Implemented interface / evidence | Status |
|---|---|---|
| Historical core | `terminal/alpaca_wire.py`,`terminal/stocks/historical_v2.py`;fixed HTTPS destinations,explicitIEX/SIP,bars/quotes/prints,exact RFC3339nanoseconds,pagination/dedup/source receipts,bounded429backoff and expiring memory cache | IMPLEMENTED / OFFLINE VERIFIED;provider disabled |
| Historical research | `historical_research.py`;exact returns/SMA/drawdown/volume/suppliedVWAP turnover,disclosed binary64 log variation,causal prefix tests,exact-endpoint comparisons and byte-bound export | IMPLEMENTED / OFFLINE VERIFIED;not predictive/empirical evidence |
| Native/API/UI integration | Additive bounded `/api/v2/market/{history,research,history/cache}`,readiness;`HistoricalResearch.tsx`,typed bar-derived input,quote-only inputs,source/freshness labels and exact-fraction tables | IMPLEMENTED / OFFLINE VERIFIED |
| Paper protocol | `terminal/paper/alpaca.py`;strict paper endpoint/order profile,independent expiring account/session/risk policy,exact activities,stable double collection,idempotency/unknown/cancel/restart handling | IMPLEMENTED / FIXTURE VERIFIED;no actual provider use |
| Paper qualification facade | `provider_workspace.py`,`PaperProvider.tsx`,v2paper status/control;no startup account/key/HTTP action,server-owned approvals and explicit limits;existing fake sandbox remains separate | IMPLEMENTED / DEFAULT DISABLED / NOT PROVIDER QUALIFIED |
| IEX readiness | Existing shared MessagePack upstream,SSE browser projection,bounded subscriptions/history/dedup,backoff/quiet-feed recovery,isolation and precise labels retained;strict source-aware paper references added | OFFLINE REGRESSIONS PASS;upstream disabled/unqualified |
| Session evidence | History reuses existing bounded configured schedule;missing/out-of-coverage evidence remains UNKNOWN | OFFLINE VERIFIED;not authoritative real-time holiday/halt service |
| UI/guides | Existing12workspaces and15modes retained;readable historical comparisons,explicit localAPI label,accessible headers,full-precision disclosure;all nine existing operating/interview guides updated | TESTED PATHS VERIFIED;not complete WCAG/physical-device certification |

## Exact contracts and resource limits

Historical requests require eight exact fields:symbol,kind,feed,start,end,timeframe,adjustment,max_pages. End is exclusive. Bars allow daily/hour/minute bounded windows;quotes/prints at most2days. SIP end must be≥900seconds old,including a1ns negative-boundary test. Never switch feeds on entitlement failure. Query defaults do not authorize acquisition. Default construction opens no connection.

Limits:4pages×64physical rows,512KiBwire/result,one active query,30second operation,16in-memory results,logical60secondTTL and explicit delete. Accesses prune immediately;periodic cleanup runs every60seconds,so physical removal is not promised exactly at the TTL boundary. Identical normalized records collapse;page hashes and physical counts remain. Conflicting bars/trade identities,out-of-order unique rows,loops and incomplete progress reject before cache publication. Raw record hashes cover normalized supported fields;physical page SHA covers supplied response bytes. This is not complete/corrected tape evidence.

Exact rational close returns,SMA and close-drawdown never use floating-point price rounding. Logs/square roots are declared binary64 approximations. Rolling variation is sqrt(sum of declared trailing log-return squares),not annualized. Caller-declared elapsed gaps can break return pairs;SMA uses supplied closes without calendar imputation. Notional requires supplied barVWAP;close×volume is not substituted. Comparison uses only exact shared source endpoints,with identical feed,origin,adjustment,window and query scope. The bar-derived dome is a modeled display of trailing variation,not invented quotes,depth or implied volatility. Actual historical best quotes can supply ribbon/quote variation;depth/event/signed-flow inputs remain absent. Existing15visualizations are preserved.

Historical exports require a separate observed export/retention approval. The response supplies exact sorted UTF8 payload text plus SHA256;the browser verifies those bytes before download. This is separate from the unchanged JavaScript-authored-fixture export contract. No observed export/storage permission is activated.

Paper is limit/day/whole-share/exact-cent,long-held-share only. Live-money/dynamic hosts,market orders,extended-hours,fractional/subcent profiles are rejected. Gates include independent execution/owner/risk review,eight specific policy approvals,account UUID,≤15minute declared session,all eight explicit owner risk values and their digest. General market-data permission never authorizes execution. Missing/wrong/stale/blocked account state fails closed. Source and receipt quote ages both must be≤5seconds;wrong feed,contradictory/future source timestamp,crossed/zero sides fail. Unsynchronized clocks can prevent admission;this is not a network-latency measurement.

SQLite persist-before-send and deterministic client IDs precede every create. Ambiguous create is never blindly resent. Reconciled exact FILL activities determine quantity/notional;rounded average prices are not a cash ledger. Duplicate activities are idempotent;conflicts reject. Cancellation204 is not proof of terminal cancellation. Restarts kill admission and preserve reservations until reconciliation. Separate provider store is account/session-bound and ignored byGit. Bounds:128intents,2048audit entries,512fill records,32symbols,16MiBSQLite,256KiBserialized intent state;bounded REST open-order/activity collection rejects ambiguous capacity or incomplete pages rather than pruning evidence.

The reviewed exclusive-account policy is essential:two equal REST collections are not exchange-atomic. Fractional/subcent fills,unexplained fees/cash,external orders,unsupported states and incomplete activity histories block the narrow profile. Real broker position availability/settlement,API profile behavior,coherent snapshots and recovery must be qualified independently. This is not general broker accounting or hot recovery certification. Example risk defaults are not owner-approved account limits.

## Reproduced defects and corrections

1. Bar-close numeric `c` collided with trade-condition `c`. Conditions now apply only to quotes/prints;valid bars remain numeric. Historical regression retained.
2. Legacy real v1 history could use only broad provider permission. It now requires the independent cloud/display/IEX history scope,including recheck before later pages. Its old HTTP429test initially stopped before transport;the mocked-HTTP fixture now declares specific authored permission while preserving the original one-call/cooldown assertions.
3. New comparison header cells appeared as generic cells in Chromium. Explicit column/row scope restored the intended accessibility semantics;original columnheader assertions pass.
4. Paper mark callback used receipt age as source freshness and did not validate feed or best-quote ordering. Two independent regression methods produced8failing assertions/subtests before repair,then passed. Both clocks and exact source timestamps are now checked;the conservative older timestamp is preserved.
5. Configured session evidence was not passed from LiveIEX to the default historical client. A failing configured-schedule identity/state test now passes after sharing the existing validated object;no extra provider/file read.

Other development failures are preserved in the evidence ledger:incorrect authored fixture clock/timestamps,obsolete test-only theme selector,a whitespace-sensitive test expectation,and a benchmark fixture beginning before the declared interval. They do not establish provider defects. One broad browser attempt was correctly rejected after this developer rebuilt assets during it. It is excluded from final results;the final runners use built-once immutable assets. No assertion,warning or resource guard was weakened.

## Executed verification

See `evidence/SPRINT4_EVIDENCE.json` and `evidence/SOURCE_AND_FILES.json` for exact counts,commands,log hashes,source bytes,assets and measurements. Final results replace no historical failures;initial logs remain locally archived with bound digests.

| Executed cohort | Passed | Failed | Skipped | Scope |
|---|---:|---:|---:|---|
| GCC Debug native CTest |158|0|0|Existing exact-source build,8hash checks |
| GCC Release native CTest |158|0|0|Same |
| GCC ASan/UBSan native CTest |159|0|0|Same,actual sanitizers |
| Clang Debug / Release / ASan-UBSan |155each|0|0|465total,24hash checks |
| Python Debug / Release / ASan-UBSan |826each|0|0|2478outcomes;96Sprint4+52Sprint3+30Sprint2+25Sprint1+142SEC/source+207stock/live+274terminal per configuration |
| Frontend Node tests |102|0|0|Response budgets,numerics,geometry,source/period/projection/history/comparison |
| Existing browser programs |12/12programs|0|0|Native21,stock10,loading10,Atlas21,Atlas2 11,advanced23,workspace120,Sprint3 7;plus contrast/performance/SOP/handshake programs |
| New historical/provider browser |9|0|0|Ordinary clicks,source/units/geometry,timeline/2D,export,multi-symbol,exact paper lifecycle,dark/light390px |
| Local HTTPS/WSS proxy programs |20checks across3|0|0|Trusted test CA,Origin/proof/rewrite/reconnect negatives;not real owner authentication |
| Additional security/diagnostic unit cohort |28|0|0|Overlaps broader terminal regression;not unique additional coverage |
| Independent native dictionary/Fraction oracle |241states /17143assertions|0|0|Authored inputs;not empirical book evidence |
| Installed unchanged-source0.1.1wheel |8interface+6export|0|0|Installed consumer;no fresh wheel compilation |
| Source packaging patterns |3|0|0|Including2negative controls |
| Rebuilt source archive |1087members|0|0|Safe,intended,byte-identical at application checkpoint;no private/build/cache/link payload |

All8frozen identities agree in all6native configurations(48/48). Existing authored3D geometry identity remains `222811765f4d91b5ac85af367c28cbbd2a01664d58c99dd1e77322e58365eaaa` (actual Node projection measurement). No empirical accuracy or provider qualification is inferred from these outcomes.


Native checks reuse existing exact-source builds because no `include/`,`src/`,`python/`,native tests,CMake or native build definition changed from the verified baseline. They are actual reruns,not a claim of new compilation. GCC14.2.0/Clang19.1.7,x86_64,Python3.12.14,Node24.19.0,Chromium154 are the local toolchain. Python ASan uses the existing sanitizer launcher with a live LSan checkpoint;`leak_check_at_exit=0` is disclosed,not shutdown leak certification. Native ASan/UBSan configurations also ran. No ARM64 or hosted run was launched for this candidate.

Warnings remain visible:deferred514.41kBThree chunk,Vite's standard chunk advisory,Starlette TestClient/httpx deprecation,pip cache ownership notice. `pip check` found no broken requirements. No dependency was added. No fresh external vulnerability-advisory clearance is claimed.

## Measured performance and visual evidence

Final source-bound authored measurement (`terminal/tests/measure_sprint4.py`):x86_64,Python3.12.14,5logical CPUs,one warmup then5historical repetitions/3paper repetitions.256rows/4pages:median1377.36rows/s with tracemalloc enabled,peak traced Python1,136,892bytes.32create/cancel intents per repetition:median8.224intents/s,680fixture requests,peak traced Python451,548bytes,SQLite143360bytes. Process peakRSS24060KiB. Canonical source/result hashes are identical across repeats. Initial/final exact-source measurement logs are retained;shared-host noise is expected.

These timings include parsing,exact calculations and/orSQLite plus tracemalloc. Broker pacing uses virtual time;they are not provider/network latency,exchange performance or an equivalent-baseline optimization claim. Allocation byte peaks are measured;total allocation counts and fragmentation were not instrumented.

Final initialJS242,590bytes /75.86kBgzip,versus241.38kB atSprint3;CSS59,995bytes. HistoricalResearch21.54kB /7.17gzip andPaperProvider8.43kB /3.14gzip remain deferred;Three514.41kB /127.55gzip unchanged. Added functionality increased the entry byabout1.21kB;no entry-size improvement is claimed. Browser measurements:1warmup/3repetitions,median initial navigation+networkidle761.3ms,company route134.6ms;initial scripts excludeThree/research scene/quote cloud/paper sandbox. Sampled JS heap range4,333,124–4,385,784bytes. These local fixture timings are not mobile or owner-cloud performance qualification.


All browser screenshots are independently authored fixture output,not observed market data or genuine account balances. `visual/` contains representative historical research/comparison and paper dark/light/mobile panels,each hashed in the evidence manifest. Software SwiftShader/headless Chromium was used;no physical Android/Safari/GPU qualification is claimed. Existing dark/light workspace checks cover360,390,768,1280and1920px. Contrast sampling/token checks and keyboard controls do not establish complete WCAG conformance.

## Durable commits

- `e18ed4cc24c4241d21c99050c6c5d225c8f9de68`:historical core28tests.
- `9622dc9ecc6334e7cb05023f8335c52b58344ccb`:paper protocol and durable engine33newtests;113combined with old52/history28.
- `b4d297dd12aa95b2ad4ec3c5f724b52f1aec15be`:source-bound research,APIs and disabled provider UI.
- `00f0eb5855072f3e5af5ddef04d586079f161ac1`:transport boundaries,legacy permission repair and fixture browser infrastructure.
- `f7d231046a4b013fb62549cc72bf7192b54c42c0`:readable exact-endpoint comparison,accessible headers and updated guides.
- `2bdbca1bb16d7bd5a720240e01a282ea4b0b2113`:source-fresh paper references,readable metrics and deterministic measurement tooling.
- `d40622ee201af9339326b14e810f2bfa56462be8`:configured schedule propagation and96-test final cohort.

Each checkpoint was pushed non-forcibly and its exact remote branch SHA checked. Final report/evidence commit follows separately. Protected main/release/Sprint3/Sprint2/audit refs remain unchanged;the evidence manifest records their observed SHAs. No new development branch was created during continuation.

## Safe owner handoff

This is a handoff procedure,not a request for intermediate manual testing. Preserve local changes first;never reset/clean an owner Codespace. When ready for acceptance:

```bash
git fetch origin feat/atlas-sprint-4-market-data-paper:refs/remotes/origin/feat/atlas-sprint-4-market-data-paper
```
```bash
git switch feat/atlas-sprint-4-market-data-paper
```
```bash
git pull --ff-only origin feat/atlas-sprint-4-market-data-paper
```
```bash
npm --prefix terminal/web ci && npm --prefix terminal/web run build
```
Stop the prior server with Ctrl+C in its own terminal,then keep all Alpaca/paper gates off:
```bash
GIG_ALPACA_ENABLED=0 GIG_ALPACA_LIVE_ENABLED=0 GIG_ALPACA_HISTORY_ENABLED=0 GIG_PAPER_EXECUTION_ENABLED=0 bash scripts/start_terminal.sh
```
Keep8787Private;use Codespaces' authenticated HTTPS Open-in-Browser URL,not phone localhost. Existing SEC private configuration is unchanged. No new keys or contact setup is requested. Do not enable paper/data flags based on a browser checkbox or this handoff. New qualification requires the specific permissions and approved plan in `REMAINING_GATES.md`.

Reproduce offline tests with the existing native package: `.venv/bin/python terminal/tests/run_sprint4.py`,`.venv/bin/python terminal/tests/run_sprint3.py`,`npm --prefix terminal/web test`. For isolated browser qualification,build first and stop compilation;run `run_sprint4_browser.py --output build/sprint4-browser --node-modules terminal/tests/node_modules`,then the existing `run_sprint3_browser.py --skip-build`. Both refuse occupied ports and block external Python sockets. These are fixture runners,not operator acquisition services. Benchmark: `.venv/bin/python terminal/tests/measure_sprint4.py --output build/sprint4-measurements.json` under the same offline guard.

## Readiness decision

The bounded Sprint4 implementation is available and offline verified within the explicit profile. Real-provider historicalIEX/SIP/liveIEX,private-cloud display,actual paper account/source/order/cancel/recovery,owner risk policy,current ARM64 and owner-target authentication/physical-device acceptance remain independently gated. Do not describe this as production trading readiness,empirical market validation or completeUS-equity coverage. No further speculative models or infrastructure are proposed.
