# GIG November14 resumed engineering checkpoint

November14,2026 (America/New_York). Engineering target:November20,2026.
Branch:`development/gig-ui-redesign`. Starting remote:
`a0ca1964175cae01c329510d651224b898a6fb77`.
Tested integrated source:**3ac8e8eb46ed70310cae2a9fd8d1f34f21a57a29**.
The enclosing evidence-only commit is the delivery checkpoint;runtime inputs do not
change in that commit. Earlier reports/evidence remain source-bound in Git.
Current receipts:NOV14_SPRINT_EVIDENCE.json.

## Recovery and implementation checkpoints

The attached executor became ready and executed commands. Runtime status was running,
with no failure. The worktree was clean;fetch and ls-remote matched the requested
checkpoint. Ledger,evidence,matrix and remaining-contract documents were read before
editing. No reset/discard,force push,protected-branch change,project restart or
reimplementation of the previous five packages occurred. The cloud runtime skill
was used;safe independent agents implemented DRS,calculation math and book-session
scopes. Root implemented schema constraints,wired/reviewed integration and reran
focused acceptance before each published package.

|Package|Verified implementation SHA|Focused evidence|
|---|---|---|
|Numeric restriction constraintsV5|a4cd92bbd5467f91f4a2b86b62c1304bdc82b32b|53schema tests;12new|
|Direct explicit open/closed hypercubeDRSV2|c42f35bae54ca01d3dc90b53faee010e038083b2|41focused/76related;16new;legacy identity comparisons|
|Exact calculation rounding/truncation intervalsV2|a4182a5f37eecd41999c896d24935549b6f5346a|62focused;19new|
|Kraken book session negotiationV1|9951eccbf36555f4ca19eb679ca2b716b4360ae7|60focused;11new|

All four were committed,pushed and independently remote-SHA-checked before proceeding.
Integrated developer-suite checkpoint:3ac8e8e. Full hashes/commands/logs/source-file
receipts are retained with the evidence. Contracts:NUMERIC_RESTRICTION_CONSTRAINTS.md,
OPEN_EXPLICIT_DRS.md,CALCULATION_INTERVALS_V2.md,KRAKEN_BOOK_SESSION.md.

## Supported behavior and limits

Numeric constraints are an explicit opt-in extension. Fixed total/fraction digit
facets,inherited non-widening digit limits,integer fractionDigits=0,local bound
consistency and bound/base lexical validity are checked before nil/fact admission.
Equal closed bounds are supported;empty exclusive intervals and fixed range facets
remain explicitly unsupported. Original declaration/source proof remains;legacy
profiles retain their previous supported behavior and reject the new fixed facets.
This is not general schema restriction/derivation validation.

Direct open hypercubes now admit additional explicit axes only with usable supplied
declarations/domains and valid nondefault members. Required/defaulted axes remain
validated. The legacy closed profile stays unchanged. Version2 derived artifacts
carry exact-profile,closed/extra-axis proof;malformed/forged scope flags reject.
Selected financials still exclude dimensioned/default-dependent data rather than
consolidating it. The existing graph/role/axis/domain/depth/output limits apply.
Typed,negative,inherited,multiple/cross-role assignments and general XDT remain
unsupported. No context,fact,metric or accounting equivalence is synthesized.

New additive calculation helpers support explicit round-to-nearest and sign-sensitive
half-open truncation,including zero. Exact Fraction math preserves open endpoints
through duplicate intersections,signed finite-decimal weights,sums and residuals.
Every reported value/source identity is retained;selected_reported_value stays null.
Excess digits,disjoint duplicates,nil/missing accuracy and unsupported precision
remain visible. Mixed modes,duplicate identities,contradictory proof status,
malformed intervals and unsupported grids reject. Existing closed-accuracy product
APIs and displayed conflict policies are unchanged. These are arithmetic helpers
for pre-bound compatible data points:OIM/context/entity/period/unit/network binding
remains the caller's responsibility. Full Calc1.1/report conformance and automatic
product calculation selection are not claimed.

The Kraken opt-in session profile provides a pure subscription-request builder and
requires current-generation request/depth10/snapshot acknowledgment before book
admission. Optional warnings/timestamps and envelopes are bounded and checked.
Reconnect/rejection invalidates negotiation;stale acknowledgments cannot revive a
session or refresh book timestamps. Only a separate checksum-verified book candidate
publishes native changes. Legacy defaults and ordered-update behavior remain
compatible. No transport,permission,retention or trading action is enabled. Local
request generations are not exchange sequences/backfill authority. Broader protocol,
trade/status/depth/usage and observed qualification remain open;Kraken is provisional.

## Current verification

|Cohort|Actual result|
|---|---|
|Guarded no-application/no-socket Python,GCC Release source-enabled binding|659passed;0failures/errors/skips|
|New regressions across4packages|58distinct:12schema,16DRS,19intervals,11session|
|Frontend unit/TSC/Vite|186passed;build passed|
|Company-v2 Python→TypeScript|15cases/93assertions|
|Existing v1 Python→TypeScript|8cases/58assertions|
|Vintage Python→TypeScript|3entries/6adversarial rejections|
|Actual native→TypeScript|35assertions,5states,1source-recovery state|
|GCC Release focused native recovery|6passed|
|Eight frozen native references,GCC Release|8passed;all8exact hashes unchanged|
|GCC Debug,Clang Debug,Clang Release focused source/durable recovery|2passed each|
|GCC ASan+UBSan focused source/durable recovery|2passed|
|Packaging patterns/offline SBOM|3passed/13passed;85components/7source inputs regenerated|
|Installed fresh SDK consumer|8passed|
|Extracted-source XBRL/source/book-session checks with real installed binding|401passed;0failures/errors/skips|
|Installed-wheel v2/vintage contracts|15cases/93assertions;3entries/6rejections|
|Dependency consistency|pip check passed|

Native/SDK/build inputs are byte-identical to the starting checkpoint. Existing
byte-equivalent native builds were reused for current focused tests;this is not a
new full compiler/CTest/Python/sanitizer matrix. Fresh default wheel build is separate.
GCC14.2,Clang19.1.7,CPython3.12.14,Node24.19.0,x86_64Linux. Pure Python is not
sanitizer-instrumented. No genuine ARM64,application/browser/device/GPU,provider or
owner acceptance is inferred from these tests.

Two initial DRS integration errors showed the new profile/schema had not yet been
wired into collection/selection. Root added exact version/profile/record validation;
the initial and final logs are retained. Assertions were not weakened. Two legacy
derived artifacts were compared exactly with the prior implementation. Root review
also added negative calculation proof-status/source-identity checks. All final
cohorts pass. Existing Starlette import deprecation,Vite optional large-chunk warning,
pip cache permissions and asyncio instrumentation diagnostics remain. No application
factory or network socket was allowed in the guarded cohort. Repeat configurations
are repeat outcomes,not new independent tests or a performance-improvement claim.

## Packaging and security scope

Clean Git archive3ac8e8e produced a fresh sdist:1,444regular members containing all
1,443tracked files,byte-compared before safe data-only extraction. Duplicate/unsafe
members reject. No scratch/build/private store/symlink was admitted. A fresh default
SDK wheel was built from that extracted source,installed offline without dependencies
into an isolated target,and actually exercised by the consumers and401source tests.
Source/archive/wheel hashes and sizes are retained inNOV14_SPRINT_EVIDENCE.json and
PACKAGE_CURRENT.json. Later evidence-only docs are not represented as packaged.

Dependency pins did not change. Current offline consistency/SBOM results do not
claim vulnerability clearance. Prior npm/PyPI advisory snapshots keep their original
November13/source scope;they were not relabeled as fresh November14 scans. Actual
OS/deployed/native/full installed graph/edge security remains unqualified.

## Completion status and precise resume

Matrix remains **34 COMPLETE / 8 PARTIAL / 7 BLOCKED / 1 NOT APPLICABLE**,50rows.
No whole requirement was newly closed. SEC02 andMD07 now record the demonstrated
bounded acceptance and remove obsolete missing-direct-open/negotiation claims.
All previous five packages,API defaults,native identities and twelve workspaces are
preserved. The seven external blockers remain CORE05,VIS04,SEC03,MD05,RES03,OPS02,
OPS03;their exact independent evidence requirements remain in
BLOCKERS_AND_REMAINING_ENGINEERING.md. No unavailable source/target was replaced by
synthetic acceptance. OriginalA18/A19requirements remain unknown.

Remaining engineering includes typed/inherited/negative/multi-role DRS,general schema
constraints,report-level calculation/aspect/network integration,source-evidenced
accounting equivalence and complete statements,remaining independently specified
Kraken/IEX contracts,and additional native recovery positions only with precise
contracts. No complete historical statements,exchange-wide tape/backfill or arbitrary
compressed-source recovery is inferred. Full acceptance still needs independent
conformance/observed corpora and target evidence. November20remains the target;
full completion is not established and the deadline has not been silently extended.

Resume from the enclosing pushed evidence commit. Read actual status,SPRINT_LEDGER.md,
NOV14_SPRINT_EVIDENCE.json,the matrix and four new contracts. Preserve all published
packages;do not rerun patch scripts,rebuild completed architecture or widen defaults
without explicit versioning. Next source milestones should bind the new math to
precisely compatible report aspects and expand typed/inherited DRS using authoritative
fixtures. Do not claim accounting aliases from names,display order or approximate
values. No background work continues after this active session.

Strict$0,GIG-only,private observation-only,separate fromGIG Quant Terminal. No GIG
launch,server,liveSEC/market/account connection,deployment,trading/paper trading or
final owner acceptance occurred. Documentation,dependency/Git development access
only;N/A scope remains unchanged.
