# Codespaces rewritten WebSocket Origin — secure handshake proof

## Facts and attribution limits

Owner supplied backend handshake:Origin http://localhost:8787,Host localhost:8787,
X-Forwarded-Host equal the private forwarded hostname,X-Forwarded-Proto https,
ASGI wss. Configured/expected Origin was the correct private HTTPS origin.
The existing rejection was correct for an untrusted Origin. Forwarded headers
alone cannot safely justify allowing localhost.

Frontend code constructs the WS URL solely from location.protocol/location.host;
WebSocket's browser API does not let that code set an Origin header. A real local
Chrome CDP capture confirms the outgoing handshake Origin equals document Origin
and the URL uses that document host. This is local browser evidence,not a remote
edge capture. The owner diagnostic alone does not prove which proxy/client sent
it:Codespaces edge,VSCode tunnel,another trusted local component or another client
cannot be distinguished without correlation. No assertion that a particular
Microsoft component rewrites every Codespaces connection is made.

## Repair without trusting forwarding headers

The updated browser obtains a one-use stream proof via POST/api/v1/stream-ticket.
That request remains subject to exact configured HTTP Origin,CORS,Host,body/rate
limits and GitHub private-port authentication. Browser reports its own origin,
intended exact WS URL and public attempt UUID;server requires them to match the
validated HTTP Origin. No request-derived host is learned as a trusted origin.

Proof:256bits of secrets randomness,30s expiry,32pending maximum,hashed in memory,
consumed once before any await. It is sent through a WS subprotocol,never a URL,
DOM/local storage or diagnostics. Server echoes only the public gig-stream-v1
protocol. Do not share full ticket responses or Sec-WebSocket-Protocol dumps.
Private-port GitHub authentication remains mandatory and unchanged;this proof
is a CSRF/connection binding,not a replacement login system.

Normal exact WS Origins remain valid. The specific reported localhost pair is
accepted only with an independent proof minted for the server-configured HTTPS
Codespaces origin,in server-owned Codespaces context,with exact local Origin/Host.
A bare local Origin is still rejected. Missing/foreign Origins,other hosts/ports,
wrong-context/guessed/expired/reused proofs and contradictory metadata fail closed.
X-Forwarded-Host/Proto/ASGI scheme are never authorization inputs. A forged header
cannot mint a proof or substitute for it. Valid proofs with foreign raw Origins
are rejected. The8-client cap is reserved before awaiting upgrade to preserve it
under concurrent handshakes. No wildcard CORS,Origin-check removal or public port.

This is an explicit bounded authorization protocol for a rewriting path,not a
claim that localhost became a trusted browser Origin. Both issuer and WS verifier
must agree on the configured origin independently of the forwarding headers.
If HTTP Origin is also rewritten,the issuer refuses rather than bypassing checks.

## Diagnosis after deployment

/api/v1/connection now has policy_version codespaces-stream-proof-v3 and:

- last_browser_bootstrap:actual HTTP Origin,browser-reported origin/WS URL,public
  attempt_id and issuance decision;no proof credential.
- last_authenticated_websocket:latest successfully proof-bound handshake with
  matching attempt_id,raw Origin/Host,authorization and101status.
- last_websocket:also includes uncredentialed probes/rejections. A later local
  probe does not overwrite the separate authenticated-browser record.
- has_application_protocol/has_stream_proof booleans,never protocol secret values.

If bootstrap HTTP Origin and browser origin equal the private HTTPS URL,and the
same authenticated attempt arrives with localhost Origin,that establishes a
change on that browser connection's downstream path. It does not name the exact
proxy hop. Uncorrelated bare localhost probes may be a different client. A missing
bootstrap usually means stale JS or failed strict HTTP Origin;refresh after build.
A bootstrap with no proof at WS can indicate stripped subprotocols or another
client;do not guess or weaken policy. Only sanitized diagnostic JSON should be shared.

## Update the existing Codespace

1. Stop the old GIG process using Ctrl+C. Preserve unrelated local changes.
2. From the repository:

```sh
git switch feat/bootstrap-cpp20-engine
git pull --ff-only origin feat/bootstrap-cpp20-engine
npm --prefix terminal/web run build
export GIG_TERMINAL_ALLOWED_ORIGINS="https://${CODESPACE_NAME}-8787.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
bash scripts/start_terminal.sh
```

Build only the browser assets because the browser now requests a handshake proof.
No native C++/wheel/pip/container rebuild or new dependencies are required. The
origin string is HTTPS without a final slash;never use wss in that allowlist.
Keep8787Private/internalHTTP. Use the actual Ports forwarded address in a top-level
Chrome tab,sign into the same account,and refresh so it loads the new JS bundle.
Step should advance the native position;transport should become CONNECTED.
Refresh/reopen the tab to verify a fresh proof/reconnection. If unresolved,read
/api/v1/connection after an attempt and share only its sanitized output.

## Executed evidence and remaining uncertainty

Exact rewrite tested with native HTTP replay and two WSS101 reconnects behind a
local TLS-verified proxy that deliberately rewrites Origin/Host to the reported
pair while preserving browser HTTP Origin. The test CA is explicitly trusted;
TLS verification is not disabled. Tests include negative forgery and one-use /
expiry/budget/host/Origin checks. Existing native-backed terminal and actual local
Chrome/3D/replay/reconnect tests execute with the new frontend. CDP evidence records
only document Origin,outgoing URL/Origin and successful correlation,no credentials.
Exact counts/receipt hashes:docs/evidence/codespaces_stream_proof.json.

Native C++/canonical fixtures unchanged. No market data,paid services,main or
workflow changes. Owner's authenticated Codespaces session cannot be reached from
this task;actual post-update success and rewriting-component attribution require
the correlated owner diagnostics. No unverified external success is claimed.
