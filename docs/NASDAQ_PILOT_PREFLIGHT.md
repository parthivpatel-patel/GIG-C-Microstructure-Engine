# NASDAQ format-only pilot: resource and access preflight

**2026-10-23, America/New_York. PREFLIGHT ONLY: no market-data body bytes
requested or downloaded. CONDITIONAL GO for a separately approved 4 KiB format
inspection; NO-GO for acquisition now or real-data L3 reconstruction.**

## Repository and preserved scope

Repository `parthivpatel-patel/GIG-C-Microstructure-Engine`, branch
`feat/bootstrap-cpp20-engine`. Entry local/remote HEAD both
`98e76bf6fbf8eb4fb0ab6586e3629625492d1e0c`, clean. Main remote
`165c5038336887116d69160b0d8e5a1a5ef59d16` unchanged.
Reviewed `NASDAQ_REAL_DATA_PILOT_PLAN.md`, `REAL_MARKET_DATA_ACCESS.md`,
`RC_EVIDENCE_CLOSURE_REPORT.md` and `RC_OWNER_ACTIONS.md`. No validated engine,
Python implementation, tests, journal, network configuration or dependencies changed.
No synthetic suite rerun is warranted for these documentation-only observations.
RC13/16/17 evidence blockers remain as previously reported.

The cloud-environment runtime skill and networking reference were followed.
Current runtime observations were fresh and connected/running, with EMI in the
configured restricted allowlist, but enforcement state `unknown`. Actual responses
below establish this request's reachability, not blanket network readiness. Normal
inherited proxy, CA trust and TLS verification were preserved. No LOBSTER request,
proxy bypass, paid resource, broker connection or release operation occurred.

## Official artifact and actual HEAD evidence

Official directory: <https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/>.
Exact previously selected artifact:
<https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/12302019.NASDAQ_ITCH50.gz>.
No new directory GET or archive GET was issued.

| Observation | Result |
|---|---|
| HEAD with `Range: bytes=0-4095`, 17:30:55 EDT | curl0, CONNECT200, origin HTTP416; body bytes0 |
| HEAD without Range, 17:31:07 EDT | curl0, CONNECT200, origin HTTP200; body bytes0 |
| Content-Length, both responses | **3,524,013,057 bytes**, approximately3.282 GiB |
| Content-Type | `application/x-gzip` |
| Accept-Ranges | `bytes` |
| Last-Modified | `Tue, 31 Dec 2019 05:13:48 GMT` |
| ETag | `"64b3281599bfd51:0"`; opaque validator, not a cryptographic digest |
| Range-bearing HEAD anomaly | `Content-Range: bytes */0` contradicts the advertised full length |

The first response was not a proxy authorization failure: NASDAQ-facing HTTP
metadata was returned after CONNECT200. One plain HEAD clarified accessibility;
network testing then stopped. A Range field on HEAD is not a valid replacement
for demonstrating a GET206 body. RFC9110 §14.2 specifies Range processing for GET:
<https://www.rfc-editor.org/rfc/rfc9110.html#section-14.2> (reference, not fetched).
Thus **byte-range support is advertised and was historically reported, but current
GET Range behavior remains unverified**. Do not infer that the artifact is empty,
that ordinary GET is broken, or that a 4 KiB response has been obtained.

Sanitized ordinary command (the first added `--header 'Range: bytes=0-4095'`):

```sh
curl --head --proto '=https' --tlsv1.2 --connect-timeout 5 --max-time 15 \
  --max-redirs 0 --retry 0 --silent --show-error \
  --header 'Accept-Encoding: identity' \
  --write-out '\nPREFLIGHT_STATUS %{http_code} %{http_connect} %{size_download} %{time_total}\n' \
  'https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/12302019.NASDAQ_ITCH50.gz'
```

Exact commands, sanitized headers, timings and raw-metadata hashes:
[NASDAQ_PILOT_PREFLIGHT_EVIDENCE.json](NASDAQ_PILOT_PREFLIGHT_EVIDENCE.json).
Private originals are outside Git at `/workspace/nasdaq-pilot-preflight/`.
There is no sample/prefix SHA256, gzip integrity result or observed event inventory.
Content-Length and MIME are server claims, not verified format or integrity.
The filename is not authenticated trading-date/session evidence.

## Actual resources, 17:30:43 EDT

| Resource | Observed value / limit |
|---|---|
| `/workspace` free | **26,165,575,680 bytes**, about24.37 GiB; overlay filesystem |
| `/tmp` free | **17,823,784,960 bytes**, about16.60 GiB; **tmpfs**, consumes RAM when used |
| Host-reported RAM total / available |35,743,760,384 / 34,595,491,840 bytes |
| Visible cgroup RAM cap / current usage |34,359,738,368 / 6,699,360,256 bytes (32 GiB cap) |
| Visible cgroup unused allowance at observation |27,660,378,112 bytes, about25.76 GiB; not reserved |
| Swap |Host reports zero swap; do not rely on swapping despite cgroup swap limit `max` |
| CPU |Intel Xeon Platinum8573C;5 visible/affinity logical CPUs, quota400000/100000 = **4 CPU equivalents** |
| Process CPU/address-space/file-size limits |Reported unlimited (`-1`); not permission to run without explicit caps |
| File descriptors |Soft/hard16384 |
| Platform execution deadline |Not exposed; session/usage interruption remains possible |
| Local watchdog |`/usr/bin/timeout` available; use monotonic deadlines and finite socket waits |

These are visible resource snapshots, not host reservations or an independent
machine qualification. `/tmp` is a different device and is memory-backed; do not
add its capacity to workspace disk or RAM. Use a private directory on `/workspace`
outside the repository for any future approved bytes. No acquisition directory or
prefix file has been populated; the preflight directory contains metadata only.
The old 3 GiB fresh-container qualification cap is not this outer executor's32 GiB
visible cap. Existing engine profile RSS~78.6 MB/PMR~77.3 MB is historical synthetic
measurement, not observed-market inspection/reconstruction consumption.

## Proposed first experiment — approval required

This supersedes only the first-attempt envelope, not the larger staged proposal
in `NASDAQ_REAL_DATA_PILOT_PLAN.md`. No automatic growth or retries.

| Bound | Proposed hard limit / behavior |
|---|---|
| Requested archive extent |One GET `Range: bytes=0-4095`, starting at compressed byte0 |
| Application-read/retained compressed body |**4,096 bytes total**, including all gzip headers; never read a cap-plus-one sentinel |
| Response headers |64 KiB aggregate parser/input cap; reject excessive metadata |
| Decompressed output |**32 MiB cumulative**, processed incrementally, not retained as a full dump |
| Expansion guard |Stop if produced bytes exceed `128 × consumed compressed bytes + 64 KiB`; absolute32 MiB cap also applies. Proposed inspection setting, not a previously measured real-data bound |
| Input/output buffers |At most64 KiB each; output calls limited by remaining absolute/ratio allowance |
| Considered frames |At most4,096 complete BinaryFile messages; residual bytes separately counted |
| Gzip policy |One member; optional header work stays within the4 KiB compressed cap; report/reject observed trailing/member data explicitly |
| RAM |**256 MiB managed process envelope**: one no-child network/decode worker with192 MiB hard virtual-address cap and supervisor with64 MiB cap; watch process-tree RSS, abort at256 MiB. No whole-host/kernel/page-cache guarantee |
| Temporary/private disk |**8 MiB total retained output**, including prefix, headers, manifests, diagnostics and logs; require64 MiB free at start. Cap output sinks, no row dumps/core dumps |
| Time |**30 seconds total wall time**, including network and inspection; connect5s, individual blocking wait<=5s, network overall<=15s, all bounded by shared monotonic deadline |
| Retries/redirects/expansion |Zero automatic retries, redirects or increased ranges; failure/inconclusive results return for review |

The 4 KiB entity-body cap excludes HTTP/TLS overhead. If a server ignores Range,
close before application body reads; TLS/kernel buffers may already contain some
unsolicited traffic. Do not promise a literal wire-byte ceiling or count that as
an authorized full download. No API that eagerly buffers a response body is allowed.
The process caps require testing with synthetic local fixtures before the approved
network run; `RLIMIT_AS` limits virtual memory, not just RSS. Apply both process
limits and a watchdog rather than assuming an RSS poll alone is a hard bound.
A future implementation may stop early if runtime mappings exceed these limits;
that is a resource failure, not grounds to raise the cap silently.

### Short proposed acquisition procedure

1. Obtain explicit approval for this exact one-request budget and private retention
   policy. Suggested policy for approval: delete received prefix and row-bearing
   diagnostics after the private inventory is reviewed, within7 days unless the
   owner expressly extends it. This is a proposed project policy, not a Nasdaq term.
   User-supplied Nasdaq sample-use confirmation supports private investigation but
   does not grant unrestricted redistribution or define retention.
2. Recheck Git, free space, RAM and current metadata. Keep raw output outside Git
   in a new mode0700 directory; files0600. Fail if a destination already exists.
   Validate the no-child worker, output/read limits and watchdog on synthetic
   ignored-Range/oversize/slow/truncated/expansion cases **before any GET**.
3. Request the exact official URL with normal proxy/TLS, `Accept-Encoding: identity`,
   Range0–4095, and representation conditioning using the saved ETag if it is still
   applicable. Do not transparently HTTP-decompress the `.gz` body. Inspect headers
   before opening/reading the body. Require HTTP206, exact
   `Content-Range: bytes 0-4095/TOTAL` consistent with the current artifact metadata,
   Content-Length4096, absent/identity Content-Encoding, and a consistent validator.
   Reject chunked/unknown-length transport for this deliberately strict first pilot.
   ETag changes require review; no stitching changing representations. Require the
   frozen reported total if using this preflight snapshot, or stop for reapproval.
4. On admissible headers, read at most the remaining4096 bytes, hash and retain
   exactly that extent, then close without draining or connection reuse. Record
   requested/returned extent, validators, actual count, UTC time, origin and
   unsupported/partial status. SHA256 authenticates only these received bytes.
5. Incrementally inspect gzip and BinaryFile/ITCH wire structure under the caps,
   using standalone format checks, **not the synthetic L3 factory**. No source
   context acceptance, order-book mutation, missing-order invention or trading-date
   inference. Report message type/length counts and raw timestamp ranges only for
   complete observed messages, with residual compressed/decompressed/framer bytes.
6. Write bounded private JSON inventory: prefix digest, exact byte/count accounting,
   format evidence, known/unknown types, error/stop reason, decoder/profile identity,
   measured RAM/time and coverage. No raw rows in Git. Stop even if identification
   is inconclusive; a larger prefix needs separate approval.

## Failure handling and partial-archive interpretation

| Condition | Safe disposition |
|---|---|
| Proxy denial, TLS failure, timeout, HTTP403/404/416, redirect |Stop, retain sanitized metadata only; no retries or alternate host |
| HTTP200 ignores Range, wrong/oversized/missing length, wrong Content-Range or validator |Reject before application body reads; close, no fallback full GET |
| Body shorter than declared4096 |Transport truncation; hash actual received extent, mark incomplete and do not pad/retry |
| Body reaches4096 |Close immediately; prefix cap reached, no extra-byte read to probe EOF; no full-source claim |
| Output/ratio/header/frame/RAM/disk/time cap exceeded |Stop deterministically, retain bounded partial accounting/error; no full-sized output allocation or automatic budget increase |
| zlib reports malformed data/header/complete trailer CRC error |Corrupt observed prefix/member; stop, no format-validation success |
| Gzip does not reach member EOF at planned4096-byte cutoff |Expected incomplete prefix, **whole-member CRC/trailer unverified**; not evidence the full archive is corrupt |
| Header incomplete, no complete record, ambiguous framing/type profile |INCONCLUSIVE within budget; never fabricate format, orders or history |

A partial gzip prefix can establish magic/method/flags when present, limited valid
Deflate decoding, observed complete BinaryFile lengths and individual ITCH wire
fields/types consistent with the pinned specification. Multiple aligned messages
provide stronger format evidence than MIME/one magic byte; any unexamined profile
version remains an assumption. Timestamps are source time-of-day fields, not dates,
UTC or receive times. A complete first member can pass its own trailer/CRC if it
happens to fit; that still does not prove the rest of the file or session complete.

A prefix generally cannot establish whole-archive SHA256/CRC/trailer, final expanded
size (ISIZE is modulo2^32), all member/type coverage, session/exchange completeness,
lossless capture, actual trading date, valid empty start, full L3/FIFO state or an
external-reference correctness result. A terminal marker in an observed segment
alone cannot supply those missing facts. The `.gz` extension and reported2019
Last-Modified do not establish historical ITCH profile compatibility.

## Acceptance checklist and decision

- [x] Starting branch/HEAD/clean tree and feature remote match expected baseline.
- [x] Required documents reviewed; validated engine unchanged.
- [x] Two bounded HEAD observations recorded; no GET/body download; no LOBSTER retry.
- [x] Actual disk/tmpfs/cgroup/CPU/process limits and unexposed session deadline recorded.
- [x] Artifact MIME/length/validators observed; Range anomaly and remaining uncertainty explicit.
- [x] Byte/decode/process/disk/time bounds and stop/inconclusive rules predeclared.
- [ ] Owner approves **one4 KiB GET+format-only inspection**, private retention policy
      and limits above. No approval exists yet.
- [ ] Future bounded inspector passes local synthetic safety controls before its first GET.
- [ ] Actual206 extent/body/hash/format inventory obtained under that future authorization.
- [ ] Whole-source integrity, observed initialization and real L3/reference validation:
      outside this experiment, not passed by a prefix.

**Resource feasibility: YES for the proposed tiny format-only pilot, conditional
on current resource recheck and the safety harness. Transport feasibility:
CONDITIONAL because current GET Range behavior is not established. Acquisition:
NOT STARTED.** Next requested authorization is precisely the unchecked4 KiB step;
no1 MiB escalation, full archive, engine integration or real-data reconstruction.
