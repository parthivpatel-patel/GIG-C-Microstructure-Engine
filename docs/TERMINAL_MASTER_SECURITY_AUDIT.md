# Terminal master execution security and correctness review

Scope: source review plus executed local independent-style checks, not an externally
commissioned audit, penetration test, exchange certification or production review.
No market/provider observations, restricted attachments or credentials accessed.

## Confirmed findings and repairs

|Finding|Evidence|Repair and residual scope|
|---|---|---|
|Heartbeats/trades kept unchanged depth fresh|Both authored regressions failed before repair; original shared last_receive_ns was updated by non-book traffic|Separate book receive clock; stale depth and metrics withheld|
|Crossed candidate reached callback|Authored crossed snapshot failed before repair by not raising|Cross check before CRC/native commit; locked books explicitly distinct|
|Receive clock regression preserved trust|Before regression observed LIVE after rejected clock|Explicit GAP_DETECTED, rejection accounting; no native callback|
|Late trade subscription acknowledgement invalidated active book|Source inspection and executed regression; no separate failing-before log captured|Only initial book ack transitions to SYNCHRONIZING; trade ack cannot downgrade snapshot|
|Extreme JSON exponent escaped structured error mapping|Before regression raised decimal.InvalidOperation|Map parser InvalidOperation to malformed_json; fail-closed context|
|Rejected source remained visible during awaited socket cleanup|New supervisor regression failed while authored generator blocked in aclose|Invalidate publication before await; view also requires adapter LIVE|
|Invalid mode disconnected feed before input rejection|New API regression failed with ERROR becoming DISCONNECTED after invalid mode|Synchronous native control validates before close; invalid request retains state|
|Browser test read state before pause POST completed|Real run:5 passes then playing=true assertion failure; click completion was not request completion|Await exact pause POST response, assert200 and playing=false, then retain all prior prefix/stability assertions;21 checks pass|

The last two supervisor/API findings were caught during review before committing
implementation. Failing-before logs are retained privately under build/master-live;
safe evidence records hashes. No assertions were removed, timeout raised, warning
suppressed or failed mandatory check disabled.

## Preserved boundaries

- Exact configured Origin or valid one-use endpoint-bound read proof; separate WS
  ticket; TrustedHost; strict CORS; CSP; private forwarded port. No wildcard, new
  localhost allowlist, public forwarding, raw forwarded-header authority or proxy bypass.
- Existing4KiB request/5s body limit,30 POSTs/s,8 sockets, bounded latest-state output.
  Provider selection uses the protected existing control endpoint; no new CSRF bypass.
- Fixed WSS endpoint and redirect rejection; max_size64KiB/max_queue4; provider frames
  cannot choose URLs, files, credentials, shell arguments, subscriptions beyond two
  allowed symbols/one active connection or depth10. Explicit server gates before socket.
- No provider exception text is returned: known error code or generic transport failure.
  No raw frames, stream proofs, cookies, permission references or tokens in diagnostics.
- Native L2 storage is separately bounded and never fabricates L3 orders. Accepted
  required updates are processed before sampled browser rendering; invalid/stale depth
  is hidden before asynchronous cleanup. Reconnection requires a new snapshot.
- Source and fixture origin are separate. Injected transport is always fixture-only;
  NativeSession refuses to publish fixture liquidity/trades in LIVE mode. Browser
  history resets across symbol/local capture segment to avoid false continuity.

## Tests and unresolved boundaries

The evidence manifest records exact final test counts and raw-log SHA256 identities.
Actual Chromium hostile-origin/custom-header/no-cors tests passed; verified local TLS
proxy reproduces rewritten HTTP/WS headers and reconnects with native replay. The
owner's private GitHub authentication is not emulated or bypassed; external post-update
acceptance remains an owner task. No new hosted/ARM64 execution was launched.

The new source-log writer uses authored allocation-failure and disk-failure injection;
these are not global OS malloc exhaustion. Existing native PMR/allocation/replay/failure
regressions pass in the complete CTest suites. Python+native view serialization is
not claimed to have a process-wide strong exception guarantee under arbitrary OOM;
the supervisor invalidates publication and rebuilds from a fresh source snapshot.

Filesystem assumes one trusted local operator. No adversarial same-user symlink-race
or crash-safe hot recovery proof. Integrity hashes do not authenticate an exchange or
prevent malicious coordinated manifest+payload edits. Expiry blocks load but does not
automatically delete files. Log replay trusts operator-approved source identity; no
arbitrary observed ingestion endpoint exists. Recorder integration is not enabled.

## Residual release gates

1. Current official provider schema, heartbeat, checksum and rate limits review; handle
   documented status/admin frames explicitly rather than silently skipping unknowns.
2. Applicable free-access/geo/cloud/private-display/retention terms; no verified license
   or entitlement is inferred from public API availability. No paid trials initiated.
3. Genuine snapshot/update/trade/ack/CRC/browser/reconnect evidence on bounded permitted
   production connection. No actual snapshot has been received in this task.
4. Native ARM64 qualification of the exact new source commit by owner-authorized run.
5. Verified retention basis, nonblocking bounded recorder attachment and interactive
   recorded-L2 replay controls. No completeness claims until these have evidence.
6. Independent observed references for analytics and reconstruction; no complete L3
   initialization from an aggregate feed. No queue, hidden-liquidity or alpha claims.

No new release, tag, main merge, workflow dispatch, paid infrastructure, broker action
or restricted dataset processing occurred. The application remains private research
software, not production trading infrastructure.
