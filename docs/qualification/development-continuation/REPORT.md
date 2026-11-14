# GIG interrupted-work recovery and continued engineering

November 13, 2026 (America/New_York). Branch `development/gig-ui-redesign`.
Starting remote checkpoint: `c7d6a023ba54910cca0c0909fb1ac59abc8ce8d1`.
Final tested runtime: **efabe0f26504e5f418f5929e5ae19a4554b8ec60**.
The enclosing evidence-only Git commit identifies delivery; runtime and native
inputs do not change in that commit. Earlier reports remain in Git at their source
checkpoints. Current retained logs and hashes: CONTINUATION_EVIDENCE.json.

## Recovery and published packages

Recovery inspected staged/unstaged status, recent commits and interrupted
work/accelerated/multidoc-baseline.log. No staged change existed. The manifest
module and ingestion modifications were already applied; the patch script was not
rerun. Its 48 baseline tests passed but did not exercise multi-document acquisition.
All existing work was preserved, reviewed and completed. No reset/discard/force push.

| Verified implementation SHA | Package |
|---|---|
|3233222fb00cf11b17989b8da898378f7ffec9c8|Bounded manifest acquisition, per-original identities, complete inline-set reference union, continuation resolution and immutable version3 recovery.|
|349f1293d852ec3892a4d53d089de94dc9e856a6|Explicit NUMERIC_WHITESPACE_V3 schema corroboration; legacy profile refusal retained.|
|efabe0f26504e5f418f5929e5ae19a4554b8ec60|Official-documentation-backed opt-in repeated-price Kraken updates; provisional status retained.|

Contracts: MULTIDOCUMENT_ACQUISITION.md, NUMERIC_WHITESPACE.md and
KRAKEN_ORDERED_UPDATES.md. Each implementation was targeted-tested, committed and
pushed before proceeding. Final broader evidence covers their combined runtime.

## Manifest ordering, identity and recovery

The caller manifest's authored document order is now preserved, rather than sorted
by the interrupted normalizer. It participates in immutable intent identity.
The existing supplied-set parser keeps its documented URI-sorted canonical storage;
actual text interleaving and explicit continuedAt traversal remain authored. Tests
prove that a URI-earlier secondary document cannot reverse continuation text, that
reordered manifests yield equal parsed values, and that replacing accepted intent
with a reordered manifest rejects without changing accepted state.

One to eight local XHTML originals require exact advertised file type/size and
lowercase SHA256. The primary must equal the metadata primary. Each original retains
its actual URI, bytes, SHA, receipt and node/continuation lineage. The primary is read
once; all existing source/total/request/time/node/chain limits remain. The manifest
is caller intent, not an invented official SEC assertion or hyperlink permission.
The set's real schema-reference union drives bounded DTS discovery. Version3 restores
manifest/hash/key/primary/directory bindings and reparses the entire set offline,
paused. Existing version1/version2 behavior remains supported. Private immutable
publication is reused with disk failure and no-socket child-process recovery checks.
Shared-lock restore refusal, cancellation and unchanged accepted state are exercised.

Company-v2/Stock Intelligence consumes explicit installed collections through its
existing contract. An actual multi-document Python-to-TypeScript case verifies
source state and installed collection matching. No startup hook, HTTP upload route,
transport permission or raw retention was added or activated.

## Further semantic and provider work

The new numeric profile admits only explicit collapse whitespace facets on supported
numeric derivations. W3C XML Schema Datatypes section4.3.6 was reviewed through its
official specification. Outer XML whitespace is normalized; internal whitespace does
not join separated digits. Facet/source proof and inherited numeric bounds remain.
Legacy profiles reject the newly supported facet explicitly; nonnumeric bases and
unsupported facet/boolean variants reject. It does not claim schema validity or
accounting equivalence. Existing offline batch/inspection APIs share the profile
registry. No numeric values, GAAP aliases or source-backed equivalence are invented.

Official Kraken book/checksum pages became readable through the web documentation
tool, independently of the executor's historical host-access failure. They permit
ordered updates to the same price. An opt-in strict boolean enables this bounded
behavior: final checksum verification precedes one native diff publication; failed
checksum rolls back all intermediate writes. Snapshot duplicates and legacy defaults
still reject. This is partial book-contract reconciliation; depth/options/trade/
status/session/usage and observed qualification remain open. No market endpoint or
account was contacted. Kraken remains provisional.

## Verification and failures

| Final developer cohort | Result |
|---|---|
| Guarded Python/no-application/no-socket, GCC Release source-enabled binding | 554 passed, 0 failures/errors/skips |
| New integration regressions | 12 multi-document, 6 schema, 5 ordered-update |
| First multi-document package broad run | 543 passed |
| Numeric package broad run | 549 passed |
| Focused numeric schema checks | 27 passed |
| Focused Kraken/differential checks | 26 passed |
| Frontend | 186 passed, TypeScript/Vite build passed |
| Actual Company-v2 Python→TypeScript | 13 cases, 79 assertions |
| Existing v1 Python→TypeScript | 8 cases, 58 assertions |
| GCC Release native recovery | 6 passed |
| Eight frozen native references | 8 passed; exact identities unchanged |
| Fresh GCC Debug ASan+UBSan source/durable recovery | 2 passed |
| Fresh installed default SDK consumer | 8 passed |
| Final extracted-source selected ingestion/schema/provider checks, installed wheel | 113 passed |
| Installed-wheel Company-v2 contract | 13 cases, 79 assertions |

The first cancellation fixture failed its busy-lock assertion because an authored
zero-length response was rejected at content-length admission before suspending.
The fixture now supplies nonempty pending bytes; the lock assertion was retained.
The failing and passing logs are included. No runtime assertion or source/security
boundary was weakened. Intermediate repeated counts are not distinct new tests.
Final selected tests had no failures/skips. Existing Vite optional-chunk warning,
Starlette TestClient import deprecation and instrumented asyncio slow-task diagnostics
remain; no application/client was started. Native inputs are unchanged from c7d6a02.
Native evidence is one Release profile plus two focused fresh sanitizer tests, not
six-profile or ARM64 clearance; Python is not sanitizer-instrumented.

## Clean-source packaging

The final sdist was made from a clean Git archive of efabe0f; all tracked members
were compared byte-for-byte, and extraction used data-only safe rules. Its source
inventory and SHA are in CONTINUATION_EVIDENCE.json. No work/build/private source
storage or symlink was admitted. The new default SDK wheel was built from the
byte-checked349f129sdist. Its SDK/native/build inputs are identical at efabe0f;
installed consumers and final-source integration exercised that real wheel.
The last provider-only package did not require a native wheel rebuild. No prior
session wheel was substituted. The later evidence-only report/matrix is not claimed
as contained in the archive. PACKAGE_CURRENT.json identifies exact origins/hashes.

## Individual review of all eight partial requirements

No row status changed: **34 COMPLETE / 8 PARTIAL / 7 BLOCKED / 1 NOT APPLICABLE**.
No whole requirement is newly closed. Bounded acceptance added in SEC02, REL02 and
MD07 must not be represented as acceptance of their stronger full requirements.

| Partial row | Current engineering or independent qualification gap |
|---|---|
|DATA02|Existing authoritative importers remain implemented. Complete current listings still need an authorized actual import/reconciliation; no issuer/listing data invented.|
|SEC02|Manifest acquisition is now implemented. Broader transformations, general schema/DRS, full calculation/duplicate conformance, source-backed accounting equivalence, complete statements and observed vintage corpus remain engineering/qualification work.|
|MD06|Existing IEX reference correction ledger remains tested. Observed cancellation/error mapping and lossless exchange-wide sequence/backfill authority remain unspecified; no guessed C/E mapping.|
|MD07|Official book/checksum subset reviewed and ordered updates implemented opt-in. Remaining protocol/options/trade/status/session/usage reconciliation and later observed qualification remain; provisional status stays.|
|REL02|Multi-document SEC recovery now verified. Native partial/terminal/arbitrary compressed positions and unknown schema migration remain unsupported; hardware/observed continuity guarantees require actual target evidence. Existing SDK/product continuation was not rebuilt.|
|SECURITY03|Exact package/dependency pins preserved. Target OS/deployed/transitive artifacts and private-edge security clearance remain outstanding; offline package success is not vulnerability clearance.|
|UX02|Existing semantic tables/keyboard alternatives remain tested. Actual device/screen-reader/browser/WCAG acceptance remains outside the no-launch authorization.|
|SCOPE02|Original A18/A19 estimator/baseline evidence remains unknown. Prospective estimator substitution cannot retroactively close the requirement.|

## Exact continuation

Resume from the pushed evidence commit, inspect Git status, CONTINUATION_EVIDENCE.json
and the three contracts above. Preserve all three implementation commits and the
existing no-launch guards. Next feasible milestones are precise broader transform/
DRS/calculation contracts and source-evidenced accounting equivalence/statement-vintage
fixtures, plus remaining official Kraken protocol reconciliation. Do not reimplement
the completed manifest or native product-source continuation. Do not weaken legacy
profiles to admit new semantics. Multi-document HTML repair/named targets/tuples and
arbitrary external document discovery remain explicitly unsupported.

Work stayed $0 and GIG-only, separate from GIG Quant Terminal. No application/server,
provider/account connection, deployment, trade, or final owner acceptance occurred.
Documentation retrieval and dependency/Git access were development-only operations.
