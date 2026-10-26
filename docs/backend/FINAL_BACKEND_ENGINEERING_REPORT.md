# Backend engineering assessment and delivery

## Executive result

Delivered a verified SEC integrity/financial-contract checkpoint, not completion of
every institutional backend capability. Two reproduced SEC defects are repaired,
malformed-container failures are explicit,12 exact period-aware financial descriptors
and read-only v2 company/filing interfaces are implemented, and an independent raw SEC
reconciler is ready. Existing native book/replay/simulation/TCA behavior is unchanged.
Actual official SEC source reconciliation remains **BLOCKED**, so acceptance requirement5
is not claimed. Owner-reported dashboard observations remain separate evidence.

Baseline: feature `f991c813749ad4c54e99943c51d7b1294f0cda20`, clean tree verified.
Main `12f3a53943dc245e36f2cbbc35b9910fb21c0718` is preserved. Exact delivered source
and evidence commit identities are recorded by Git and the final response; see the
safe evidence manifest for tested file hashes. Commits carry `[skip ci]`; no workflow
is launched, no merge/tag/release or market-data download occurs.

## Defects, changes and architecture

SEC_EDGAR_VALIDATION.md records failing-before cases, root causes and repairs. Numeric
magnitude used context-rounded Decimal abs; contradictory accession rows lacked checks.
Both are now rejected without accepting partial parsed state. A related option signed-
value boundary failure at low Decimal precision is also reproduced and repaired with
the same context-independent comparison. Receipt timestamps now
distinguish request start from completed validation. Fiscal FY/FP, actual durations,
issuer/source IDs and bounded revisions are preserved. Legacy fields/v1 endpoints stay.

BACKEND_ARCHITECTURE.md inventories routes and v2 contracts. New financial calculations
use exact Fraction arithmetic, explicit missingness and compatible actual periods;
no fiscal-quarter fabrication, debt-as-liabilities proxy, denominator fallback or
annualized return claim. Versioned schema validates populated and unavailable views.
Independent tooling compares original source records rather than copying production
normalization expectations. Current tests use independently authored source shapes.

## Fresh executed validation

| Configuration/check | Passed | Failed/skipped |
|---|---:|---:|
|GCC Debug|155/155|0/0|
|GCC Release|155/155|0/0|
|GCC ASan+UBSan|155/155|0/0|
|Clang Debug|155/155|0/0|
|Clang Release|155/155|0/0|
|Clang ASan+UBSan|155/155|0/0|
|Terminal installed Release native consumer|274/274|0/0|
|Terminal Debug native consumer|274/274|0/0|
|Terminal ASan+UBSan native consumer|274/274|0/0|
|New backend focused tests(included above)|21/21|0/0|
|Strict security regression|46/46|0/0|
|TLS/rewritten HTTP/WSS|8/8|0/0|
|Chromium application/native/3D|21/21|0/0|
|Stock unavailable browser|10/10|0/0|
|Configured authored stock browser|9/9|0/0|
|Recorded replay/research browser|9/9|0/0|
|Live-control authored browser|9/9|0/0|
|Frontend unit tests|4/4|0/0|
|Packaging patterns(build-tool interpreter)|3/3|0/0|
|Installed wheel interface/export contracts|8+6|0/0|

The new financial tests include2000 independent seeded margin candidates and reference
formulas for all12 metrics. Six fresh native suites total930 outcomes and preserve all
eight canonical hashes in every configuration(48 comparisons). Frozen native source,
bindings/root schema/fixtures were not changed. Historical six-defect rechecks are in
BACKEND_COMPLIANCE_MATRIX.md. Existing allocation-failure/recovery/adversarial oracles
are included in the native suites; no new C++ allocations were introduced.

Live-interpreter LSan checkpoint reports0; the deliberate12345-byte leak negative
control is detected with expected nonzero exit. This does not certify full CPython
interpreter-shutdown leak cleanliness. No suppressions/assertion weakening were added.

A first packaging invocation used the runtime-only wheel environment and failed to
import scikit_build_core. Re-execution in the installed build-tool environment passed
all3 checks; this was an environment-selection error, not a repaired package defect.
Two server launch attempts found already-running owned local test servers; those were
stopped and the changed source was restarted before browser qualification.

## Journal, performance, models and risk

PERFORMANCE_REPORT.md contains measured1/1024/8192-record scaling and separate restart
costs; physical record12232B,logical15944B,cap100000.8,192 records consumed roughly100MB
retained PMR/150MB peak. No100000-record or whole-process fragmentation claim is made.
No storage refactor occurred. Stock microbenchmarks record actual shared-host timings,
warmups/repetitions,fixture identities,source state and process/traced memory.

QUANT_MODEL_VALIDATION.md separates fixed HMM/GARCH/Kalman demonstrations, European
option scenarios, descriptive risk and causal microstructure statistics from fitting,
calibration and empirical prediction. Portfolio risk/exposure and production operations
are not represented as complete. SECURITY_AUDIT.md documents preserved source/origin/
host/proof/credential boundaries and unverified external security gates.

## Delivery and operations

Changed implementation: SEC normalizer, option signed-value parser, source service, new financial calculator,
backend contract/schema, two cache-only routes, independent qualification CLI and21
authored tests. Strict terminal cohort count increases253→274; the manual ARM64
workflow and its policy test use the new exact count without trigger/gate changes.
Nine required reports, a durable checkpoint and safe evidence are added. Full file
inventory/digests and archive validation results are recorded in the evidence manifest.

Codespaces update(start from a clean feature checkout):

```bash
git switch feat/bootstrap-cpp20-engine
git pull --ff-only
bash scripts/start_terminal.sh
```

Stop the prior terminal process before restarting. Keep8787 PRIVATE and use its
forwarded HTTPS address, not a remote device's localhost. Existing UI stays on v1;
new v2 company/filing views are available for the redesigned frontend. No native engine
rebuild is necessary for these Python/backend changes when the validated wheel exists.

## Remaining acceptance and next actions

1. Obtain supported SEC host access and truthful contact configuration, or run the
   owner-side independent qualifier against authorized official copies/cache. Retain
   source digests/cutoff and independently reconcile financial statements.
2. Execute private Codespaces/ATLAS v2 owner acceptance. Local Chromium/TLS tests do
   not prove external GitHub authentication behavior.
3. Owner-authorize exact-new-HEAD ARM64 qualification and obtain hosted CI evidence.
   Historical ARM runs qualify their tested SHAs only; no new hosted success is claimed.
4. Keep Alpaca authorization pending support381230; do not turn on IEX/options gates
   merely because fixtures or configuration checks pass. Do not process LOBSTER.
5. Follow the dependency-ordered top25 priorities in REMAINING_GAPS.md. No credible
   production-readiness or deadline promise is justified by this local checkpoint.

The code is suitable for continued private synthetic research and owner-gated SEC
reconciliation. It is not a complete institutional trading, empirical L3 or production
financial-data platform. This session stops after the verified checkpoint; work does
not continue in the background.
