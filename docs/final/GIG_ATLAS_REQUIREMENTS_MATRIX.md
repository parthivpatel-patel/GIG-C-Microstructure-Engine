# Requirement-level acceptance matrix

Statuses apply to the stated bounded contract,not a claim that unit tests alone establish
product completion. Numerical,integration,statistical,observed and operational evidence
are distinct. See final_evidence.json for exact counts/hashes/commands/source scope.

|Requirement|Implementation|Local evidence|Real-data evidence|Limitations|Severity|Owner action|
|---|---|---|---|---|---|---|
|Historical REST/pagination|PARTIAL|Prior51+new18 consumers;browser ingestion|NOT VERIFIED|Raw bounded pages,no automatic acquisition/session completeness|High|Review rights/retention;bounded owner pilot|
|Persistent immutable revisions|COMPLETE bounded contract|Recovery/hash/old-core regressions|NOT VERIFIED observed|32 snapshots/schema1/access expiry;not exchange archive|Medium|Configure private directory only if needed|
|Source receipts/provenance|PARTIAL|Revision/frame/analysis fingerprints|NOT VERIFIED|No invented exchange sequence;page partition/resume incomplete|Medium|Review per-page evidence design|
|Multi-symbol dataset alignment|COMPLETE bounded contract|Independent1/99;start/end alignment;unit conflict;browser|NOT VERIFIED|20–64 exact shared intervals,raw only;no inferred FX/calendar|High|Qualify actual authorized source revisions|
|Exchange sessions/corporate actions|NOT IMPLEMENTED|Explicit non-authority assertions|NOT VERIFIED|Raw prices;no missing exchange-bar or adjusted-price claims|High|Obtain authoritative calendar/actions inputs|
|Backup/restore/restart|PARTIAL|Existing process-exit/partial-copy/CRC tests|NOT VERIFIED operational|Explicit restore;no cross-process/power-loss HA guarantee|Medium|Disk/restore contention qualification|
|IEX quote/trade transport|PARTIAL|Official SDK references;18-case cohort/fake async transport|BLOCKED|Binary32KiB/128 rows;unknown/correction types stop|High|Permissions381230,credentials,current protocol review|
|Stream auth/subscription/reconnect|COMPLETE bounded offline contract|Handshake/reorder/duplicate/backoff/stop regressions|NOT VERIFIED|Fixed endpoint;5 failures;actual provider/proxy unqualified|High|Owner-run bounded live pilot|
|Live browser observation/freshness|PARTIAL|Blocked-start browser;monitor tests|BLOCKED|5s browser poll;30s stale labels;no feed enabled|High|Private browser source/reconnect acceptance|
|Trade corrections/cancels/other feeds|NOT IMPLEMENTED|Unknown-type rejection tests|NOT VERIFIED|No silent skip or liquidity restoration|High|Verify authoritative schemas before extension|
|SEC selected financial descriptors|COMPLETE bounded contract|Existing exact financial/source tests|NOT VERIFIED official|12 descriptors;missing/period/unit metadata preserved|High|Owner official reconciliation|
|Full XBRL statements/dimensions|NOT IMPLEMENTED|Explicit selected-fact UI disclosures|NOT VERIFIED|No presentation/context/dimension tree ingestion|High|Separate scoped XBRL implementation/oracle|
|Retained filing-date vintages|PARTIAL|Known-cache cutoff/empty-old/future rejection|NOT VERIFIED|Truncated historical cache;date-level,not intraday PIT|High|Full filing-history/context evidence|
|Official SEC reconciliation|BLOCKED|User-Agent absent;no official request|NOT VERIFIED|Owner configuration not inherited here|High|Run existing gated official CLI|
|HMM Baum-Welch/filtering|COMPLETE bounded contract|Existing oracle/state/likelihood tests|NOT VERIFIED statistical|Two-state local Gaussian fit;label ambiguity/in-sample caveats|Medium|Observed OOS/calibration study|
|HMM missing emissions|COMPLETE fixed-parameter inference|Independent transition/label-permutation checks|NOT VERIFIED|No imputation;not missing-data parameter estimation|Medium|Missing-data EM if justified|
|GARCH conditional search|COMPLETE bounded conditional method|Independent recursion/grid baseline/constrained tests;browser|NOT VERIFIED statistical|Fixed mean/initial variance;finite local search,no globalMLE/CI|Medium|Observed OOS comparison/uncertainty|
|Kalman prediction/update|COMPLETE bounded existing contract|Existing independent numerical/Joseph tests|NOT VERIFIED empirical|Fixed process/measurement variances|Low|Calibrate only with independent evidence|
|Chronological/walk-forward evaluation|PARTIAL|Training-only/future-mutation tests preserved|NOT VERIFIED statistical|Caller order not authenticated PIT;new optimizer not silently used|High|Official vintages/calendar/OOS study|
|Portfolio covariance/tails/scenarios|COMPLETE bounded mathematics|Independent exact covariance/tails/weights tests|NOT VERIFIED calibration|Explicit weights,no inferred holdings/FX/liquidity guarantee|Medium|Observed calendar/position/tail evidence|
|Native L3/matching/replay/TCA|COMPLETE synthetic contract|6×155;8 hashes each|NOT VERIFIED observed L3|No licensed complete initialization/reference|High|Separate licensed observedL3 gate|
|Native journal memory optimization|NOT IMPLEMENTED new candidate|Existing measured baseline/recovery/allocation suite|NOT APPLICABLE|12232-byte record;no speculative compaction|Medium|Benchmark-gated migration/equivalence package|
|Python/native packaging|COMPLETE local interface contract|Wheel8+6;sdist3 and clean inventory|NOT APPLICABLE|Existing native wheel tested,no new compiler build|Medium|Fresh independent-machine candidate build|
|All9 workspaces/navigation|COMPLETE local fixture journeys|91 original browser+90 viewport/theme combinations|NOT VERIFIED external|Risk integrated in Stock Intelligence,not separate route|Medium|Private Codespaces owner acceptance|
|Pinned dataset→risk→export journey|COMPLETE authored workflow|New5 browser journeys;export content checked|NOT VERIFIED observed|Authored export only;observed export disabled|Medium|Review redistribution rights before changing gate|
|Responsive/accessibility|PARTIAL|360/390 new;5 widths original;keyboard/reduced motion|NOT VERIFIED devices|No full WCAG/screen-reader/physical Android audit|Medium|Manual accessibility/device review|
|Frontend/API/model performance|COMPLETE local measurement|1 warmup/3 runs;raw timings/source hashes|NOT VERIFIED production|No tail SLO,exchange latency or long-run growth claim|Low|Independent sustained/target-device qualification|
|Origin/Host/request proofs|COMPLETE tested boundary|46 security+8TLS+new forged-header tests|NOT VERIFIED external auth|Private Codespaces boundary remains owner/platform-managed|High|Owner external HTTPS/WSS acceptance|
|Secrets/provider permissions|COMPLETE preserved controls|Preconnector rejection;safe reason fields|NOT VERIFIED entitlements|No secrets configured/copied;no wildcard/paid activation|High|Obtain legitimate permission;server-only secrets|
|Private storage/retention operations|PARTIAL|Hash/expiry/private-file/recovery tests|NOT VERIFIED physical|No hard globalquota/continuous physical erase/encrypted backup|Medium|Operational retention/security policy|
|Exact candidate ARM64/hosted qualification|NOT VERIFIED|No workflow launched|NOT VERIFIED|Prior qualifications do not transfer to this implementation|High|Owner-authorized manual free-runner qualification|
|Reproducible source candidate|COMPLETE local artifact gate|Clean source inventory plus manifest|NOT APPLICABLE|Not a published/tagged v1.0 release|Medium|Independent checkout/build/review|
|Production trading readiness|NOT APPLICABLE|Research-only boundaries;no broker execution added|NOT VERIFIED|Not an operational trading platform|Critical|Do not deploy for trading|

Recommendation:CONDITIONAL GO for private,disabled-provider research evaluation.
NO-GO for complete live/observed v1.0 or production trading claims.
