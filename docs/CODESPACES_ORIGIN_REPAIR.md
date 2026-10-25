# Private Codespaces Origin/HTTPS/WebSocket repair

## Evidence and root-cause boundary

Owner reports a standard private forwarded HTTPS URL and startup via
bash scripts/start_terminal.sh. These are the intended access path. That report
alone does not reveal the browser's transmitted headers or which Python process
owns8787. Owner's authenticated Codespace cannot be inspected from this task;
one unauthenticated HEAD was blocked by proxy CONNECT403 before origin,no retries
or credentials. No claim of externally verified owner-session repair.

Reproduced defect:the app factory derived allowed origins only from an explicit
variable/default localhost list;Codespaces auto-configuration lived exclusively
in __main__. Direct uvicorn/other ASGI imports bypassed it. With valid server-owned
Codespaces metadata and a TLS proxy rewriting Host to127.0.0.1,a native GET loaded
while POST returned the exact reported ORIGIN_DENIED and WS was rejected. Two
failing-before tests against immutable bcec6f9 source preserve that evidence.

The reported shell launcher should normally configure the origin. A stale process,
missing environment metadata/flag,or explicit stale origin list remains possible
in the owner's specific session,not proven from the screenshot. Fresh restart and
the credential-free runtime diagnostics below identify those cases without guessing.

## Repair and security

Shared server/config.py resolves the same exact environment policy in the launcher
and create_app,including direct ASGI startup. A server-owned CODESPACE_NAME can
supply exact origin even if a process manager omitted CODESPACES;without the flag
it stays loopback-bound. Explicit contradictory allowlists fail startup. No browser
Origin/Host/X-Forwarded-* header is used to learn or expand trusted origins.

Existing strict Origin,Host,CORS,CSP and client/resource limits remain. HTTPS is
required in the browser Origin;WSS is the WebSocket URL scheme,not an Origin entry.
Forwarded HTTPS does not require the internal backend itself to speakTLS. No
forwarded_allow_ips wildcard,no wildcard CORS,no GitHub authentication/visibility
changes,no cookie/token handling or public tunneling. Frontend already derives
HTTPS/WSS from location;it was not rebuilt or replaced. Native C++ unchanged.

Start script now refuses an occupied8787 with explicit instructions to stop the
old process. It never kills/replaces arbitrary processes or silently picks another
port. Pulling files or refreshing Chrome does not reload a running Python server.

## Update your existing Codespace — no rebuild

1. In the terminal running the old GIG server,press **Ctrl+C**. If that terminal is
   missing,identify the listener using `lsof -nP -iTCP:8787 -sTCP:LISTEN` and stop
   only your GIG Python/uvicorn process. Do not kill all Python processes.
2. From the repository directory:

   ```sh
   git status --short
   git switch feat/bootstrap-cpp20-engine
   git pull --ff-only origin feat/bootstrap-cpp20-engine
   export GIG_TERMINAL_ALLOWED_ORIGINS="https://${CODESPACE_NAME}-8787.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
   bash scripts/start_terminal.sh
   ```

   If Git refuses due to unrelated changes,preserve them;do not reset/discard. The
   exported string must equal the Chrome forwarded address's Origin exactly:HTTPS,
   no trailing slash/path and no wss scheme. If metadata is missing,use your exact
   owner-approved private HTTPS Origin explicitly instead of inventing a hostname.
   The launcher prints expected origin;contradictions fail closed.
3. Keep8787 **Private**,internal protocol **HTTP**. Use **Ports → Open in Browser**
   as a top-level Chrome tab,not an embedded VSCode webview. Sign into the same GitHub
   account. Refresh once after restart. No setup/pip/cmake/npm rebuild is needed.
4. In Historical Replay,click Step:position/book should change. Transport should
   read CONNECTED. Refresh/reopen that same private URL to check reconnection.

## Safe actual-header diagnosis

After trying Step and waiting for a WS attempt,open the same forwarded address plus
**/api/v1/connection** in Chrome. Expected policy_version:codespaces-origin-v2.
If404,the running server is outdated or the wrong checkout/process is serving8787.
Response contains:

- configured_origins and expected_codespaces_origin (server-owned authority);
- request Origin/Host,X-Forwarded-Host/Proto/Port and ASGI scheme;
- latest mutation decision and WS decision/upgrade status,with corresponding headers;
- connected-client count and limit8.

It retains only two bounded request summaries;no arbitrary headers,Cookie,
Authorization,client IP,query strings,source payloads or secrets. It is read-only
under the same existing private-port authentication;do not make the port public.
A GET may have no Origin;use last_mutation/last_websocket to see browser Origin.

Interpretation:

- Origin should match the exact HTTPS forwarded origin,no slash. Host may legitimately
  be127.0.0.1/internal while X-Forwarded-Proto ishttps;that is TLS termination,not a
  reason to disable strict Origin checks. ASGI may showhttp orhttps depending on proxy
  trust handling;authorization still uses server configuration.
- rejected_origin identifies an actual application policy mismatch;spoofed forwarded
  headers cannot authorize it. expected_codespaces_origin null indicates absent
  metadata;explicit exact configuration still works.
- WS accepted/101 followed by native messages proves application upgrade acceptance.
  rejected_capacity means close extra tabs and retry;do not remove limits.
- No WS record while browser is disconnected means it may not reach the app (GitHub
  auth/proxy/CSP/browser layer). Check top-level private login and Chrome Network/WS
  status. Do not share cookies,tokens or full DevTools header dumps.

If it persists,share only this sanitized JSON and the startup origin message. It
provides actual-session evidence without pretending local tests inspect the owner.

## Executed validation

22 unit/forwarding checks,56 existing native-backed terminal tests;10 new repair
checks under ASan/UBSan/liveLSan0. Local real TLS-terminating proxy -> native ASGI
passed6 end-to-end checks,including exact proxy-header capture,HTTPS Step,foreign
Origin denial,two verified WSS101 upgrades and accepted-prefix preservation. The
client uses CERT_REQUIRED/hostname verification with an ephemeral dedicated testCA;
TLS verification is never disabled. Actual Chromium browser21 checks include
replay,3D,mobile and interruption/reconnect. Exact results/receipt hashes in
[evidence/codespaces_origin_repair.json](evidence/codespaces_origin_repair.json).

These are local verified proxy/browser checks,not a real owner Codespace/private
GitHub authentication round trip. Existing native sources/canonical identities
are unchanged;no native rebuild/full1405 matrix rerun was necessary. No market data,
paid services,main change or GitHub workflow was involved.
