# Proposed next implementation sprint — approval required

Audit candidate `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`.
**Do not execute this plan during the audit.** No application/test repair,provider
activation,paper order or owner Codespace deployment is authorized by these notes.
Zero-additional-cost,same repository,native correctness and honest source labels
remain mandatory. No unrelated project code,microservices,Kafka/Kubernetes or paid
data infrastructure is proposed.

## Findings reconciliation

Original19 findings remain3 resolved +16 open/partial/deferred:
**0P0/3P1/12P2/1P3** outstanding. A04/A15/A16 retain Sprint1 resolution;
A18 original requirements and A19 estimator acceptance remain open. All62 Sprint2
receipts were rehashed;no historical finding was silently closed. Owner's private
port/sign-in/receipt/visibleSEC observations are positive new owner evidence for
A03/A10/A12/A14,but not independently authenticated full closure.

New grouped entries:

| ID | Priority / status | Exact evidence | Required action and measurable acceptance |
|---|---|---|---|
| S3-BUDGET |P2,confirmed application resource defect|`terminal/web/src/api.ts:2`;3MiB chunked response fully becomes text before2MiB check;`response-budget.json`.|Incremental byte-bounded read/cancel across generic API paths. Test absent/malformed/large length,chunked limits,multibyte,abort and structured errors;actual read/accumulation bounded,not merely final exception.|
| S3-TEST |P2,confirmed qualification regression|`terminal/tests/stock-intelligence-validation.mjs:15` fails old raw-string expectation;raw price reference passes.|Update test to assert intended four-significant-digit summary plus independent raw API and full-precision disclosure. Full committed program must pass without changing correct pricing or weakening reference assertions.|
| S3-PAPER |P1,future-goal readiness gap;not prior read-only regression|No account/order/position route/client;routing validator rejects them;negative mocks pass.|Separately approve paper-only design and all missing risk/idempotency/reconciliation tests before enabling any provider/order experiment. Simulation alone cannot close it.|

Combined outstanding priorities: **0P0/4P1/14P2/1P3**,19 entries across22 total
including3 resolved. No enabled money-trading,credential leak,unauthorized provider
connection or synthetic-as-live incident was reproduced. Candidate-model omissions
(cointegration,factors,optimizer) are scope decisions,not invented mandatory P1 bugs.

## Dependency-ordered packages

| Package | Scope / affected interfaces | Independent acceptance | Dependencies / risks / relative effort |
|---|---|---|---|
| R01 Response read boundary |Reuse bounded reader in `web/src/api.ts`;review optional-source error states.|Independent streaming fixture consumed-byte/cancellation checks;small/error/UTF8/timeout contracts;all frontend/security/native hashes retained.|Unblocked engineering after approval;small. Do not alter Origin/proof or financial calculation semantics.|
| R02 Browser evidence repair |Only stale display assertion and raw/full-precision reference in committed stock browser;stable build/test ordering retained.|Current original browser program completes all intended checks,raw BS known value and accessible full precision remain tested;no forced clicks.|Unblocked;small. Do not mark old failed run passed retroactively.|
| R03 Bind existing SEC evidence |Use existing report binder,not a fresh fetch or setup cycle;identify original code/time/scope.|Exact supplied report/source hashes and counts;unknown metadata incomplete. No promotion from fixtures;visible facts must retain input provenance/period/missingness.|Owner original sanitized artifact/time/SHA;small engineering,external duration unknown.|
| R04 Freeze personal research acceptance |Resolve A18 recoverable scope/A19 supplied-depth HHI decision;explicit required versus optional models.|Versioned acceptance cases/denominators with source and expected outputs;keep unknown historical scope separate.|Owner scope decision;small/medium. Do not add speculative models to inflate completeness.|
| R05 Lawful IEX read-only qualification |Existing `LiveIEX`,REST/history/catalog and owner qualification scripts;no unauthorized activation.|After separate authorization:source/receipt time,age,unit,symbol isolation,quiet/closed/UNKNOWN session,stale/reconnect,shared allowance,no synthetic fallback/depth/orders/retention. Exact SHA and safe evidence.|Specific cloud/display/historical scope and free account window;external block. Existing30s qualifier's quote+trade requirement can be inconclusive in quiet markets;never fabricate events to satisfy it.|
| R06 Data-source/3D workflow completion |Use actual accepted L1 for four existing projections/ribbon/dome;depth/event models keep unavailable states. Individually exercise CSV's unverified controls.|Known changed values transform actual scene/input tables,cameras unaffected;disconnect/stale/recovery and2D on real authorized source;no inferred depth or fictitious timestamps.|R05 for real source;fixture engineering unblocked after approval. No new decorative model suite required. Medium.|
| R07 Bounded historical research qualification |Existing raw history,immutable revisions/PIT views;declare adjustments,calendar,coverage and survivor-selection limits.|Independent interval/time/source matching,no look-ahead,source hashes,missing/amendment negative controls;observed historical results only with permitted inputs.|R03/R05 and genuine source evidence. Medium;do not relabel current raw closes as action-adjusted/full history.|
| R08 Paper safety design and fake-broker tests |New narrowly bounded server-owned paper execution boundary distinct from read-only data and unchanged C++ research journal;durable intent state only if approved.|Paper/live account negative cases,pretrade exposure/buying power/loss,reservations,idempotent IDs,unknown acknowledgments,partial/rejected/late fill,kill/cancel/restart reconciliation and audit trail under injected clocks/failures.|Explicit implementation approval for future paper subsystem;medium/large. Current data permission flags do not authorize orders. No provider connection needed for fake-broker engineering.|
| R09 Paper account read-only qualification |Only after approved R08 and separate provider/account authorization;fixed paper endpoint.|Actual account identity/paper verification and limits,reconciliation snapshots,permissions and no costs;zero order submissions.|External permission/account gate;not authorized by this audit. No requests to owner for new keys.|
| R10 Bounded owner-approved paper experiment |Only after R08/R09 and explicit order-specific approval.|Exact small experiment limits,pre/post positions,order/idempotency/status/fill/cancel evidence,loss and kill checks,no unknown open order state.|Separate authorization;NO-GO now. Never live-money fallback or retry ambiguous order creation blindly.|
| R11 Target security/portability/device acceptance |Current-SHA guarded free native ARM64 path;runtime/transitive/system/browser advisory review;actual private forwarding and desktop/Android flow.|Six actual hosted configurations,all8hashes;target login denial/authorized HTTPS/WSS;ordinary clicks/key/touch/resource scope;record run/commit/device evidence.|Owner free-runner/target authorization. Existing workflow accepts release branch only;do not merge or change guard merely to evade it.|

## Stop,rollback and durability

- Freeze and review coherent checkpoints;no main merge,force-push or deployment
  is implied. Each implementation change requires its own relevant tests and full
  source/canonical evidence. Do not “fix” expected mathematical values to get green.
- Stop source activation on missing scope/credential readiness/limits/integrity;
  keep previously accepted data labelled historical/stale and unavailable inputs
  honest. Do not fabricate history,session state,order IDs or fills.
- Roll back a UI/reader regression by deploying the prior approved exact candidate
  through an owner-controlled process,not resetting branches or deleting private work.
  Preserve raw failure logs and source receipts. No automatic owner deployment here.
- Future paper ambiguity triggers fail-closed admission and explicit reconciliation;
  disabling new submissions does not prove outstanding orders cancelled. Preserve
  durable intents/audit history;never erase evidence as a rollback mechanism.
- No new observed retention until provider rights and explicit owner approval.
  No broker orders until separately approved experiment. Real-money trading remains
  excluded. C++ is appropriate for existing exact/native hot paths;bounded256-sample
  Python diagnostics do not justify an unrelated native rewrite.

## Exact owner decisions/evidence still needed

1. Approve a **future** narrow repair sprint R01/R02;this audit does not implement it.
2. Supply already-existing sanitized SEC receipt/hash/tested SHA/time if available;
   no contact re-entry or repeated network setup required.
3. Resolve only the pending Alpaca private cloud/display/historical scope questions
   and authorize a bounded IEX qualification window later;Basic personal research
   availability is already acknowledged.
4. Decide original scope/A19 estimator and whether future paper engineering R08
   is desired;then define risk limits and order-specific approval separately.
5. Authorize a valid current-candidate free ARM64 qualification path and final
   private target/device/advisory review when appropriate. No workflow was launched.
