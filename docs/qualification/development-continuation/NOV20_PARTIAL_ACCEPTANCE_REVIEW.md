# November 20 partial-requirement acceptance review

Read-only review of the fifty-row completion matrix, implementation source and
retained contracts. This document changes no status, acceptance criterion or source
code. The matrix still has **34 COMPLETE / 8 PARTIAL / 7 BLOCKED / 1 NOT APPLICABLE**;
all row statuses match the starting `f7813d7` checkpoint. New source packages close
bounded subcriteria, not the stronger whole requirements. Final runtime SHAs/test
counts belong to the enclosing source-bound sprint evidence. An in-progress guarded
run is not represented here as a passing result.

No provider, application/server, owner target, device, ARM64 workflow or advisory
service was accessed for this review. The evidence column identifies implemented
source/retained contracts, not fresh external acceptance. Recovered import/semantic admission defects were repaired and independently tested.
No external acceptance evidence was created by those repairs.

|Partial row and exact retained criterion|Implemented evidence and current disposition|Exact unfinished engineering versus external dependency|Minimum defensible next unit|
|---|---|---|---|
|DATA02 — Complete,current US-listed security universe|`directory.py` validates the two official directory file schemas, dates, duplicate symbols and bounded atomic replacement; `alpaca_reference.py` validates active/inactive provider IDs/status/flags; `discovery.py` preserves exact-identifier union and explicitly disclaims completeness. Directory receipts preserve source creation text with unspecified zone and actual receipt separately. **PARTIAL.**|No missing generic importer was established. Current complete listing coverage requires actual authorized authoritative source import/reconciliation and freshness evidence. Provider account assets, SEC registrants and a static symbol union cannot supply that claim. Delisted history and symbol-equivalence inference are outside the existing bounded import contract.|One source-bound complete-file reconciliation cycle with exact source counts, exclusions, timestamps and identity conflicts, after an authorized source/target is supplied. A separately specified historical symbol-change contract would be another engineering package; do not guess aliases.|
|SEC02 — Complete historical financial statements and point-in-time source history|The retained acquisition, inline-set, schema, DRS V1–V6, calculation/default, acceptance/vintage, source-statement and original-source audit contracts are bounded implemented subsets. V6 now admits direct closed mixed scalar-typed/explicit cubes from original DTS; private source-accounting/inline exports now reach existing Financial/Stock Intelligence imports through strict semantic validation. `xbrl_accounting_relationships.py` and `xbrl_accounting_statements.py` now require original-source essence/required-element evidence and independent statement selection; supplied role labels are not GAAP completeness. **PARTIAL.**|Broader schema/complex-typed/cross-role/effective DRS, complete inline/OIM/calculation semantics and independently justified full financial-statement/accounting acceptance remain distinct engineering milestones. Complete observed history/source authenticity also needs legitimate original source/corpus evidence. Source audits prove reconstruction of supplied bytes, not provider authentication.|One independently specified semantic/conformance slice plus adversarial original-source fixtures and existing product/SDK contracts. For whole-statement closure, first bind explicit completeness/mapping criteria to an authoritative taxonomy/issuer corpus; no fixed total estimate is defensible before that scope exists.|
|MD06 — Complete corrected exchange tape and lossless reconnect|`trade_tape.py` implements bounded exact-reference correction/retirement/deduplication with capture-session isolation. Cancellation is explicitly limited to `AUTHORED_CANCEL_C_V1`; `live.py` reports absent exchange sequence, bounded retained windows and subscription-handover gaps. **PARTIAL.**|Observed cancellation/error action interpretation remains unsupported without authoritative mapping. Exchange-wide completeness/losslessness requires actual sequence/initialization/backfill authority that the current IEX-only observation contract does not provide. These are not gaps to fill with guessed events.|One source-versioned observed-action mapping and deterministic correction/cancel/reconnect fault package once the authoritative contract is available. Losslessness requires an independently complete sequence/backfill source; without it that stronger promise is not an estimable coding task.|
|MD07 — Official-contract Kraken L2/native/product integration|`kraken.py` retains explicit provisional status, exact decimal/checksum candidate handling, native L2 projection, opt-in ordered repeated-price updates and `BOOK_SESSION_V1` depth10/snapshot/request-generation negotiation. `BOOK_SESSION_DEPTH_V2` adds opt-in depth25/100 with ordered updates and explicitly top-ten CRC scope;80 provider/native checks pass. `KRAKEN_ORDERED_UPDATES.md` and `KRAKEN_BOOK_SESSION.md` retain the reviewed subset. **PARTIAL.**|Remaining official depth500/1000/options/trade/status/full-session/usage reconciliation is engineering backed by exact documentation; later source/target qualification is external and prohibited here. Local acknowledgment generations are not exchange sequences, and CRC agreement is not backfill/losslessness or usage approval.|One bounded documentation-to-parser/native fixture reconciliation unit, such as a precisely specified trade/status transition profile or bounded larger-depth native admission, with byte/level/session limits and legacy refusal. Retain provisional status until all required contract and actual qualification evidence exists.|
|REL02 — Crash-safe hot live/L3 recovery and hardware durability guarantees|Native source recovery supports only its versioned bounded plain/single-gzip prefix contract; `source_recovery.hpp/.cpp` explicitly rejects partial frames, terminal positions and unsupported source/container/cursor states. Existing SDK/product paused continuation, immutable publication and source/capture/generation identities remain implemented. New source/JSON recovery checks do not widen native positions. **PARTIAL.**|Partial/terminal positions, arbitrary compressed seeking and unknown schema migration remain unsupported engineering contracts rather than implicit guarantees. Actual observed initialization/continuity and hardware durability remain external qualification. No obsolete claim of absent basic product wiring should be restored.|Specify exactly one additional replay/source boundary and state transition, then implement its versioned codec/cursor/continuation contract with compiler/sanitizer, corruption/failure and cross-process fixtures. Arbitrary compressed offsets or hardware guarantees cannot be inferred from that unit.|
|SECURITY03 — Runtime/dependency security clearance|Source-lock SBOM/inventory and private package/source/import/JSON bounds exist (`build_offline_sbom.py`, `artifacts.py`, `offlineJson.ts` and source-audit contracts). Existing package/version/hash receipts and bounded advisory snapshots keep their original source/date scope. **PARTIAL.**|Exact installed/deployed/transitive/native/OS/edge artifacts and advisory/reachability scope remain unavailable. A source-lock inventory, successful `pip check`, raw-source reconstruction or fixture-origin/Host result does not establish target security clearance. This review performs no fresh advisory scan.|One exact-target inventory plus source/version-bound advisory/reachability/remediation/retest cycle after actual artifacts and an authorized target scope exist. No blind dependency upgrade or universal vulnerability-absence claim.|
|UX02 — Full WCAG2.2AA and physical-device acceptance|Source inspection finds semantic navigation, focus-visible and reduced-motion rules, keyboard-scrollable exact-value tables with captions/scoped headings, named file controls and loading/error announcements (`Navigation.tsx`, `workstation.css`, `BarValues.tsx`, `AcceptanceFacts.tsx`, `SourceCalculations.tsx`). Offline SSR/unit contracts cover code-level behavior. The recovered source panel adds two accessible file controls, exact-value source tables and asynchronous issuer guards;345 frontend tests pass. **PARTIAL.**|Actual browser/device/screen-reader interaction and exhaustive WCAG2.2AA/current-candidate acceptance remain unperformed. This source review does not certify contrast, focus behavior or assistive output across every state/device. No additional concrete static defect was demonstrated here.|One separately authorized target/browser/assistive-technology acceptance session, followed by findings-specific code repairs and retest. Confirmed static issues can be fixed offline when identified; unknown future failures cannot be given a defensible fixed implementation estimate.|
|SCOPE02 — Historical A18/A19 requirement and concentration acceptance|`REMAINING_BLOCKERS.md` preserves the missing-original-criteria decision and prospective alternatives. Existing exact supplied-depth HHI/concentration code remains intact. **PARTIAL.**|The original estimator/baseline/acceptance evidence was not recovered from the inspected retained repository decision records. This is a missing historical contract, not authorization to substitute a new concentration metric or retrospectively accept HHI.|Recover the exact original requirements/evidence or obtain an explicit prospective owner contract. Implementation effort cannot be scoped before that criterion exists; any prospective baseline must be labeled separately from historical acceptance.|

## Seven blocked rows and unchanged excluded scope

The status identities were checked against `f7813d7`; all seven remain **BLOCKED**.
Existing offline prerequisite tools are retained in
`BLOCKERS_AND_REMAINING_ENGINEERING.md`; this review did not reproduce a new missing
engineering prerequisite or establish that no future source-specific repair can be
needed.

|Blocked row|Exact independent evidence still required|
|---|---|
|CORE05|Legitimately usable observed L3, independently complete initialization/order reference, bound hashes and actual source/reference comparisons.|
|VIS04|Current-candidate sustained physical GPU/mobile/independent-browser interaction and resource results on actual targets; requires authorized application/device testing.|
|SEC03|Authorized actual official SEC reconciliation with exact candidate/source identities, date/count/cutoff and source receipts.|
|MD05|Authorized private IEX entitlement, live/historical source-clock/freshness/venue receipts with observation-only use.|
|RES03|Legitimate versioned observed data, an independently specified causal/out-of-sample protocol and actual statistical evaluation; fixtures are not forecast quality/alpha.|
|OPS02|Exact-candidate owner-authenticated private HTTPS/WSS/Origin/Host and source/assets acceptance on the real private edge.|
|OPS03|Genuine current-candidate native ARM64 run IDs/SHA, required compiler-profile conclusions/counts and all eight reference identities; not cross-compilation or an older run.|

**SCOPE01 remains NOT APPLICABLE:** real/paper execution, paid feeds, public deployment
and redistribution were not authorized by this sprint. No criterion was removed or
silently narrowed to raise a status. November20 is the engineering delivery target and the date of this checkpoint;
remaining semantic milestones and externally dependent acceptance are explicit,
with no implied background execution, new deadline or production-readiness claim.

## Current developer receipts and remaining effort

Tested source: `9be1c0d8293444e517af67fe2a57fd1be599277c`. Exact current counts,
package provenance and hashes: NOV20_DELIVERY_EVIDENCE.json. The eight partial
criteria were assessed individually above. Closed subcriteria are bounded typed
corroboration, additional Kraken depth admission, and the private Python-to-TS-to-UI
source-accounting/inline evidence path. None satisfies its stronger entire row.

Remaining semantic work needs multiple independently specified implementation and
verification units. The minimum next unit for SEC02 is one cross-role/effective or
complex-typed/OIM conformance slice, or issuer-corpus-bound statement completeness;
its exact effort depends on the source contract and fixtures. MD07 needs one more
protocol/native reconciliation package before any authorized provider qualification.
REL02 needs one precise source-position/schema admission contract and native failure
matrix; basic source/product wiring is already present. DATA02, MD06, SECURITY03,
UX02 and SCOPE02 retain the exact source/target/authority dependencies listed above.
No defensible fixed effort to whole-project acceptance exists without those inputs.
Deferral leaves bounded functionality usable but bars complete statements/history,
exchange-wide losslessness, target security, WCAG/device or production claims.
The delivery target is not silently extended; engineering remains incomplete today.
