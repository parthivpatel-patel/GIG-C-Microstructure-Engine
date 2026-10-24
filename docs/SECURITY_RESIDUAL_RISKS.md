# Security closure and residual risk register

October24,2026. **PARTIAL qualification. No owner risk acceptance inferred.**
Full machine-readable classifications: evidence/security_closure.json. Prior exact
versions/sources/licenses/advisories remain in evidence/dependency_inventory.json;
this is a closure overlay, not a rewrite of historical results.

- Verified vulnerability in deployed engine: none newly established by finite review.
- Confirmed non-applicable: CVE-2026-22184's specific contrib/untgz executable path
  is not deployed. It is not blanket zlib package clearance.
- Mitigated: Expat CVE-2026-93990's UTF16 path excluded for strictly UTF8/NUL/DTD/
  entity-rejected evidence. Other Expat issues/provider mapping remain unresolved.
- Mitigated: receipt verifier now preflights at most256 files/128MiB aggregate,
  retains64MiB/file and read-boundary budgets, before any hash processing. Two
  new controls fail before repair,10/10 pass after. Trusted immutable local evidence
  remains required; concurrent hostile filesystem races are not certified.
- Unresolved:13 named OpenSSL advisories from3.5.9 notes versus managed3.5.8,
  CPython3.12.14 versus3.12.15, Expat/vendor/host/toolchain patch identities and
  actual reachable crypto/provider features. No fabricated affected ranges/backports.
- Unresolved: full resolved bundled action dependency/SBOM security mapping and
  hosted execution of the updated checkout action. Official v6.1.0 immutable SHA
  d23441a48e516b6c34aea4fa41551a30e30af803 rechecked against upstream Git tag;
  retained official source/runtime/license receipts verified. Node24/read-only
  permissions/no persisted token controls remain; no workflow was launched.
- Accepted residual risks requiring owner approval: **none accepted in this program**.

Smallest owner actions: provider dated patch/feature evidence or supported qualified
runtime update; signed-in exports of the existing native run; separately authorize
current-HEAD hosted qualification after local gates. Do not send secrets or silently
replace managed TLS/interpreter/kernel. Empty feeds and sanitizers are not clearance.
