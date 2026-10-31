# GIG ATLAS functional reality audit — October 31, 2026

**Audited application:** `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`,
`fix/atlas-private-qualification-2`. **Audit branch:**
`audit/atlas-functional-reality-20261031`, isolated from that exact commit.
This is a documentation-only audit. Application, tests, configuration, workflows,
permissions and all protected branch tips are unchanged. No SEC, Alpaca, crypto or
market-data requests, credentials, private historical data, orders, deployment,
paid resources or workflow dispatches were used. New tests are temporary offline
audit harnesses, reproduced as documentation, not application implementation.

## What the terminal actually is

GIG ATLAS is a functioning **bounded offline research terminal and read-only data
integration framework**, with a native C++ book/replay/simulation core, exact
financial transformations, Python statistical laboratories and browser visualizations.
It is **not currently qualified as a connected daily market terminal or an Alpaca
paper-trading system**. Permission-disabled integrations are not functioning live
feeds. Synthetic simulator fills are not broker orders.

The default native book is `terminal-authored-v2`, instrument `SYNTH-USD`, with
20 initial authored events. Browser replay, state changes, native calculations and
simulation actually execute; they are not screenshots or mocked C++ integration.
Native tests independently preserve FIFO, checked arithmetic, recovery and eight
frozen identities. None establishes exchange-equivalent observed L3 reconstruction.

The statistical models calculate meaningful quantities on supplied inputs. HMM EM,
grid/conditional GARCH, scalar Kalman, exact portfolio risk and causal toy backtest
are implemented. They do not establish profitable signals, calibrated forecasts,
complete historical research or an execution strategy validated on actual data.

All13 advertised visualization modes respond mathematically to controlled inputs.
Two additional legacy scenes also change pixels following real native replay or
declared parameter changes. The15-mode inventory therefore exceeds the old13-mode
denominator without pretending two extra scenes are new work. Rendering, camera
interaction and data updates are separately tested. None is qualified against a
live provider here. Dome cross-sectional curvature is explicitly decorative; the
volatility statistic driving its height is meaningful but not calibrated volatility.

## Inventory and evidence accounting

[FEATURE_INVENTORY.csv](FEATURE_INVENTORY.csv) has **463 declaration/capability
rows**:306 static JSX controls/options,51 route/method contracts,12 workspaces,
15 visualization modes, and analytical/native/source/security/readiness capabilities.
This is not463 independent user journeys, a coverage percentage or the unknown
universal original requirements denominator. Dynamic runtime instances are grouped
at their source declaration. Unexercised controls remain explicitly unverified.

| Primary classification | Rows |
|---|---:|
| REAL_LIVE |0|
| REAL_DELAYED |0|
| REAL_HISTORICAL |0 independently verified in this audit|
| REAL_STATIC_REFERENCE |2 static reference capabilities;not fresh exchange authority|
| SIMULATED |126|
| VISUAL_ONLY |1 intentionally decorative dimension,not a whole-model verdict|
| DISCONNECTED |20 provider-dependent paths/workspaces|
| BROKEN |2:browser assertion and generic client response budget|
| UNVERIFIED |312,including individually unexercised controls and absent future capabilities|

**148 rows have current offline functional/contract evidence**; this count includes
working fail-closed behavior and static references. It does not mean148 genuine
provider features. Newly provider-verified functional rows:0. A UI control classified
UNVERIFIED is not automatically broken. A model classified SIMULATED may be
mathematically correct and useful on authored inputs.

## Reproduced failures

`terminal/tests/stock-intelligence-validation.mjs:15` expects the old long option
price substring `7.96556746`; current UI correctly formats it as `≈7.966`.
The committed browser program fails after four earlier checks. Independent raw
Black–Scholes reference gives7.965567455405804 and passes. This is a **P2 test-contract
drift**, not evidence of wrong option pricing. The test was not weakened, repaired
or silently omitted. Its original failure is retained. No product defect is
invented from this result, and no overall all-tests-PASS claim is made.

A second **P2 resource-boundary defect** is reproduced at `terminal/web/src/api.ts:2`: with no Content-Length,`decoded()` awaits all `r.text()` before its2MiB check. A bounded3MiB chunked local fixture was completely received and converted to text;the optional catalog caller swallowed the resulting error. This disproves enforcement at the read boundary. It is not an unauthorized provider call or credential leak. See SECURITY_AND_DEPLOYMENT and the preserved reproduction. No application repair was made.

New P1 **readiness gap**: broker paper-order routing, account/risk/reconciliation
and durable intent/idempotency controls are absent. That is deliberate current
read-only scope, not a regression or an enabled dangerous trading path. It blocks
the owner's newly stated future paper-trading goal.

## Separate readiness gates

| Gate | Decision | Exact boundary |
|---|---|---|
| A Offline research terminal |PASS|Bounded authored/native replay, calculations and tested UI flows;not every control or arbitrary research workflow. Failed legacy qualification assertion remains open.|
| B SEC fundamental research |UNVERIFIED|Owner sees genuine SEC facts;parser/PIT/ratio contracts verified offline. Exact original provider artifact and coverage cannot be independently established here.|
| C Genuine real-time market data |BLOCKED|Permissions remain disabled;no authorized provider session executed.|
| D Data-driven3D |PASS|15 tested synthetic/declared/replay mappings and actual render updates;not live-market qualification or physical-GPU certification.|
| E Genuine historical research/replay |UNVERIFIED|Authored replay passes;complete observed initialization, corporate actions, survivor-safe history and empirical validation are absent/unqualified.|
| F Quantitative signal reliability |UNVERIFIED|Numerical references pass;no empirical predictive significance or profitability.|
| G Alpaca paper integration |FAIL|No broker execution adapter or operational risk/reconciliation stack.|
| H Personal paper operations |FAIL|G plus permissions/account/operational acceptance outstanding.|
| I Real-money trading |FAIL|Intentionally unsupported/prohibited;do not build or activate as part of this plan.|
| J Institutional production |FAIL|Incomplete operational/security/source/market qualifications;no production claim.|

## Owner evidence preserved without promotion

The owner reports12 visible workspaces, successful build/startup, exact-source
local receipt MATCH, private8787 forwarding, an unauthenticated Incognito GitHub
sign-in redirect, visible SEC facts and rendered3D. These are positive owner-target
observations. This audit cannot independently inspect the owner's authenticated
Codespace. It does not downgrade them into “did not happen,” or upgrade them into
full penetration testing/provider/market/ARM64 acceptance. SEC10,429 identities and
1,772 selected matches remain owner-reported pending exact artifact binding.

## Delivery and next decision

The original16 open/partial/deferred findings retain0P0/3P1/12P2/1P3. Adding the
paper-readiness gap,test drift and response-budget defect gives **0P0/4P1/14P2/1P3**
open/partial/deferred entries across22 total findings including the3 earlier
resolved entries. No new finding establishes an enabled trading path or credential exploit.
A18/A19 historical requirements/estimator decisions remain open.

Proceed first with the bounded response-reader and browser-contract repairs,plus evidence binding,
then separately authorized IEX qualification after the specific permission questions
are answered. Do not add decorative models or pretend absent depth is available.
Paper execution needs an approved paper-only safety architecture and deterministic
failure tests before any provider/order activation. The precise dependency sequence,
rollback and stop gates are in [SPRINT_3_REMEDIATION_BACKLOG.md](SPRINT_3_REMEDIATION_BACKLOG.md).
No implementation is authorized by this audit's plan.
