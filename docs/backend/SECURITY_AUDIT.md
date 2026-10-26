# Backend security review

Scope: source review and authored negative/regression tests, not an external penetration
test. No credentials, private market data or provider payloads are included in evidence.

## Preserved boundaries

* `server/config.py`, `request_proofs.py`, `stream_tickets.py`, `connection.py`: exact
  configured Origin/Host and bounded endpoint/session proofs. Forwarded headers never
  independently authorize a request. Rewritten localhost Origin is not added globally.
* `stocks/service.py` and `auth.py`: fixed official destinations; credential alias
  consistency; redirects/retries disabled; SEC fair-access/contact gate and Alpaca
  entitlement/private-display/cloud-processing/no-cost gates remain enforced.
* SEC and financial endpoints accept curated symbols, bounded numeric/file identifiers,
  exact JSON values and safe official filing paths. New v2 GETs read cache only and do
  not carry provider credentials or authorize another mutation.
* Existing recording paths/retention/size limits and private-data git exclusions remain.
  No LOBSTER dataset, full NASDAQ archive or live trading path was accessed.

## Executed evidence

46 strict origin/host/proof tests pass.8 local HTTPS/WSS rewritten-proxy checks pass
with certificate verification, plus Chromium native/reconnection flows. New v2 tests
verify bounded query rejection, schema/null states and native-book isolation. Expanded
terminal cohorts pass under ASan/UBSan and the live LSan checkpoint; the deliberate
12345-byte leak negative control exits as expected. Full CPython interpreter shutdown
is still outside that live-checkpoint claim. No sanitizer suppression was added. The indicative-option signed-value range parser
also uses a context-independent magnitude comparison after an authored precision8
over-limit reproduction; negative and positive boundary cases remain rejected.

## Findings and limits

| Severity/status | Finding | Action/acceptance |
|---|---|---|
| High/repaired | SEC contradictory filing identities/numeric boundary | Regression failures reproduced and repaired; keep independent raw-source negative controls |
| High/blocked | Actual source/entitlement qualification missing | Do not enable Alpaca or claim independently reconciled SEC data until evidence exists |
| Medium/partial | Stock cache process-local and per-result bounded, not persistent warehouse | Document restart loss and total-memory budget; measure worst-case multi-symbol retention before enlarging limits |
| Medium/unverified | External Codespaces authentication/reconnection on this HEAD | Owner keep8787 PRIVATE and exercise actual forwarded URL; local proxy tests do not authenticate GitHub's service |
| Medium/partial | Dependency pins are not a vulnerability attestation | terminal/server/requirements.txt pins versions; separate current advisory/SBOM review remains required |
| Medium/unverified | No crash-safe financial persistence/backup restore | Keep process-lifetime limitation; require corruption/recovery tests before adding persistence |
| Low/partial | Monolithic ASGI app and concise parser code complicate review | Extract only when boundary tests preserve exact semantics; no broad refactor in this repair |

No authentication tokens, arbitrary request headers or private response bodies are
logged by new qualification tooling. Financial source receipt URLs are fixed public
endpoints. SHA256 is an identity/integrity check, not a license or authenticity proof
for an owner-supplied file. No paid resources, workflow dispatch or public-port changes.
