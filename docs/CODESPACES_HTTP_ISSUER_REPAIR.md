# Codespaces rewritten HTTP Origin: issuer repair

Baseline: 02fa56225eaf900dd27f768d3e271cd19ad9a74f. Date: October 25, 2026 (America/New_York).

The owner's sanitized diagnostics establish the failed policy condition before any
repair: POST /api/v1/stream-ticket arrives with Origin http://localhost:8787 and
Host localhost:8787, although configured/expected Origin is the private HTTPS
Codespaces origin. Forwarded host/proto are consistent with that external address.
The POST boundary rejects `request.headers.get('origin') not in origins` before
entering the issuer. `last_browser_bootstrap:null` confirms its body was not checked.
The previous WebSocket-only proof therefore cannot bootstrap. This evidence does
not identify which proxy/tunnel component rewrites HTTP Origin. No unsupported
claim about the browser or a specific Microsoft component is made.

## Security boundary and smallest repair

A same-origin GET /api/v1/request-proof breaks the circular dependency. It requires
three non-simple X-GIG headers declaring a fixed bootstrap marker, an exactly
configured browser Origin, and one of five explicit POST paths. Sec-Fetch-Site,
when present, must be same-origin. Raw foreign read Origins are rejected; the
specific observed localhost rewrite is recognized only with server-owned expected
HTTPS Codespaces configuration. Normal same-origin GET without Origin is supported.

This is a same-origin read CSRF capability, not authentication by a claimed header.
Browser SOP, unchanged CORS, and private Codespaces authentication protect issuance.
CORS deliberately permits only Content-Type: cross-origin browsers cannot pass
preflight for X-GIG headers; no-cors strips them. The response is no-store,
CORP same-origin, and nosniff. Authenticated raw HTTP clients can forge browser
headers, just as they could forge exact Origin before this change; this mechanism
is browser CSRF protection, not a replacement for private-port authentication.

The random 256-bit proof is hashed in RAM, capped at 32 pending entries, expires
in 30 seconds, and is consumed once. It binds the configured Origin and exact POST
path. Every frontend POST obtains a fresh proof. The POST gate accepts either the
existing exact configured Origin, or the observed exact localhost Origin/Host pair
with a valid independent endpoint-bound proof in configured Codespaces context.
Provided invalid proofs fail even for otherwise approved Origins. Foreign/missing
POST Origins, wrong Host, wrong endpoint, expired/reused proof, and forwarding
headers alone cannot authorize the compatibility path. Localhost was not added to
the Origin allowlist. TrustedHost and strict CORS remain enabled and unchanged.

The ticket body must match the independently authorized browser Origin and its WSS
URL. Existing one-use WebSocket proofs, native isolation, limits and private-port
authentication remain intact. Forwarded headers never confer authority. The policy
version is codespaces-request-proof-v4; bounded diagnostics add explicit failure
conditions and proof-bootstrap context, without logging capabilities or credentials.

## Executed validation

- 46/46 security/origin/access tests, including 11 new exact-failure regressions.
- 56/56 existing native-backed terminal regressions.
- 11/11 new tests with prebuilt ASan/UBSan native extension; LIVE_LSAN_CHECK=0.
- 3/3 frontend unit tests; TypeScript and Vite production build passed.
- 21/21 actual Chromium application checks, including replay, 3D rendering and reconnect.
- Actual Chromium cross-origin negative control: credentialed custom-header fetch
  blocked at preflight without reaching issuer; no-cors strips headers and cannot
  read a proof. A legitimate same-origin-context read succeeds.
- Browser CDP confirms outgoing WebSocket Origin equals document Origin and the
  bootstrap/socket attempt is correlated; no credentials captured.
- 8/8 loopback HTTPS/WSS integration checks with verified ephemeral CA: proxy
  rewrites both HTTP and WS Origin/Host exactly as observed, bare ticket POST fails,
  proof-authorized native step succeeds, two WSS101 reconnects retain that prefix,
  foreign Origin and non-simple cross-origin preflight fail.

All tests above ran locally. The TLS proxy uses actual native-backed ASGI, not a
mock engine. It does not establish success in the owner's private Codespace; that
post-deployment check remains required. Browser testing uses headless Chromium,
not a physical Android device. Existing Starlette/httpx deprecation warnings remain.
No native implementation, canonical fixture or replay identity was changed; the
full native/compiler matrix was not unnecessarily repeated. No hosted workflow
was launched and no market data was accessed.

## Apply to the existing Codespace

Stop the running server with Ctrl+C, keep the already correct Origin environment,
then run on feat/bootstrap-cpp20-engine:

```bash
git pull --ff-only origin feat/bootstrap-cpp20-engine
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

Keep port 8787 Private and refresh the existing HTTPS forwarded page. No native
rebuild, pip reinstall or Codespace rebuild is needed. Expected diagnostics:
policy v4; last_mutation authorization codespaces_rewrite_request_proof;
last_browser_bootstrap decision issued with matching browser/authorized Origins;
last_websocket upgrade_status101 and accepted_codespaces_rewrite_ticket. If this
still fails, capture sanitized connection diagnostics, not cookies or proof headers.
