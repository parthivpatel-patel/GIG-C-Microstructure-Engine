# Security,private deployment and resources

Audited SHA: `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`.
No owner target/configuration was changed. This is a bounded same-environment code
and fixture assessment,not a penetration test or independent-machine attestation.

## Verified boundaries

55 policy tests and three **certificate-verified local** HTTP/WSS proxy cohorts
(6+8+6 checks) pass. Sources: `server/config.py`, `request_proofs.py`,
`stream_tickets.py`, `connection.py`, `app.py`. Exact forwarded external Origin
comes from server-owned Codespaces metadata,not arbitraryX-Forwarded headers.
Origin/Host rewrite compatibility requires the existing bounded endpoint-bound
request proof or one-use stream proof,withsame-origin/non-simple-header bootstrap
and applicable Fetch Metadata checks. Wildcard CORS was not enabled. Localhost was
not added to external allowed Origins. Proofs are bounded,expiring,one-use,not URL
credentials. Diagnostics whitelist bounded values and exclude tickets,cookies,
keys,contact information,client IP and arbitrary headers.

Provider URLs are fixed server-owned allowlists;permissions remain default-off.
REST does not follow redirects or expand compressed bodies. Read-only Alpaca
destinations reject account/order/position endpoints. Source errors use sanitized
categories. Private SEC/history/evidence files have permission/size/symlink checks;
existing output is not silently overwritten. No source was upgraded blindly.

`AnalysisGate` admits one physical analytical worker and retains ownership despite
request/shutdown cancellation. SSE uses bounded clients/latest-state coalescing,
payload cap/in-flight counters and a real2s send timeout. Native transaction,
allocation-failure,recovery and hash tests pass. These are component-level bounds,
not a global service CPU/RSS quota or provider-loss recovery guarantee.

## Confirmed P2: generic response budget is post-read

**S3-BUDGET**, `terminal/web/src/api.ts:2`, `decoded()`:

1. Declared Content-Length>2MiB rejects before read.
2. Without that header,it executes `await r.text()` on the entire body.
3. Only afterwards it checks `text.length>2*1024*1024`,a character count rather
   than incrementally enforcing a byte budget.

Independent bounded reproduction ran the unmodified built frontend/native app
against a deliberately substituted **local authored** catalog endpoint with48×64KiB
streamed whitespace chunks,no Content-Length. Browser timing reported3,145,728
decoded bytes and the instrumented original `Response.text()` returned3,145,728
characters—exceeding the stated2,097,152-byte limit before rejection. App.tsx's
optional catalog catch discards the error;no Data boundary alert is expected there.
See [response-budget.json](evidence/response-budget.json). The temporary fixture
changed no repository application code and accessed no provider or sensitive data.

Impact: the generic client budget does not bound allocation/read work for a
chunked/unexpectedly large response. Existing backend byte caps reduce normal
exposure;no credential leak,unrestricted foreign fetch or production exploit was
demonstrated. Medium severity is proportionate to the claimed resource-bound
invariant. Some versioned financial readers already use bounded streaming;do not
mistakenly assume their implementation covers every generic `request()` call.

Next authorized sprint:reuse a bounded incremental byte reader,abort/cancel on the
first over-budget chunk,handle malformed Content-Length/UTF8 safely and retain
structured errors. Test announced/unknown/chunked bodies just below/at/above the
budget,multibyte text and cancellation. Assert actual consumed bytes/cancellation,
not only that a final error eventually appears. Browser/network prefetch is a
separate layer;report managed accumulation/cancellation separately from actual
network transfer rather than promising a universal transport byte quota. No repair
was made in this audit.

Initial audit probe expected a visible alert and timed out;source inspection showed
the optional caller swallowed it. The revised **audit instrumentation**,not app,
measured body consumption directly. The initial log remains preserved. A transient
TIME_WAIT bind failure was handled with a normal SO_REUSEADDR free-port probe;
no running process or owner service was killed.

## Private Codespaces: owner evidence versus independent tests

Owner reports port8787 Private and an unauthenticated Incognito redirect to GitHub
sign-in,plus exact-source running receipt MATCH. Preserve these as positive
owner-target observations. They are not contradicted by the qualifier retaining
`private_target_acceptance:UNVERIFIED`,which correctly refuses to infer external
authentication from a loopback GET. This audit did not log in to that target.

An owned loopback native server with empty provider environment was started and
stopped. Its frozen startup receipt matched the exact candidate and built assets.
No forwarded owner URL,cookie,secret or target authentication was inspected.
An authenticated private GitHub edge is an external dependency,not reproduced by
a local test CA/reverse proxy. Do not make the port Public or weaken Origin checks
to improve a test result.

## Runtime and dependencies

Current offline inventory:pinned17 runtime distributions match;19 installed
distributions inventoried;`pip check` finds no broken requirements. CPython3.12.14,
OpenSSL3.5.8,Expat2.8.3,SQLite3.53.1,Node24.19.0,npm11.9.0,GCC14.2.0 and available
Clang19.1.7. Exact receipts include lockfile hashes/transitive names. No online
advisory query was issued;pin equality is not vulnerability/backport/system image,
browser or GitHub Action clearance. Prior npm advisory receipts are historical.

Private file helpers are owner-controlled tools,not privileged sandboxes against
hostile ancestor-directory renames. Exclusive/fsynced evidence writes do not claim
crash-atomic multi-file publication or signatures. Code SHA/digest binding is not
independent execution attestation. Current-candidate ARM64 remains unverified;
existing manual workflow is release-branch-only and was not dispatched/modified.

## Actual bounded performance

- Owned warm-filesystem launch to first successful native health:.355480s,
  25ms polling resolution;SIGTERM-to-exit:.213942s. One local launch,not RTO or
  external startup/browser latency.
-5,000 authored quote processing:1.587859s,3,148.90 events/s;RSS36,984KiB;
  Python tracked peak945,808 bytes;history/dedup256,4,744 evictions. No exchange-speed claim.
-50,002 **authored** directory identities:parse/index .334000s,RSS82,312KiB.
  Exact lookup median .004883ms,prefix .024614ms,broad50,000-match substring
 18.855389ms (one warmup,5 repetitions,declared inner query counts). Not real stock coverage.
- Native journal4 cases retain12,232-byte physical records plus3,720-byte restart
  data as applicable,15,944 logical combined bytes. All four processes return zero
  live allocator bytes after destruction. No journal redesign or full100k-session claim.
-3D/software renderer/projection measurements are in THREED_MODEL_AUDIT. These
  are bounded samples,not60FPS,physical-device,tail-latency or sustained-session proofs.

No credential exposure,enabled real-money execution,unauthorized provider connection
or synthetic-as-live publication was reproduced. That is a scoped result,not
universal absence of vulnerabilities. Runtime,owner-target,device,endurance and
independent-machine acceptance remain open.
