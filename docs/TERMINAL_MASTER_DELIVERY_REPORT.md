# Institutional terminal: master execution and qualification report

Date: October25,2026 (America/New_York). Delivery target: November10,2026; budget$0.
This is a completed validated engineering checkpoint, **not full live-data acceptance**.
Provider access/legal/schema evidence blocks the critical live qualification gates.
No elapsed work is claimed after the task stops.

## Commits and scope

- Starting, owner-confirmed CONNECTED/Step baseline:
  34e3145467c0e47dcc76c9c9fcd3079990f7c3cc.
- Baseline/access checkpoint: c846dac (full SHA in Git history).
- Validated implementation: **80a6f30b2ea03d523931f84957c54e8c5a2f2639**,
  pushed and exact remote SHA verified before this report.
- This report/evidence is a separate documentation checkpoint; its final SHA is
  reported in delivery and Git history rather than a self-referential commit field.
- Authorized feature branch only. Main remains12f3a53943dc245e36f2cbbc35b9910fb21c0718.
  No force push, workflow launch, release, tag or paid service.

The implementation commit changes27 files. Complete file inventory, six canonical
matrices, source archive inventory and raw-log hashes are in
[evidence/terminal_master_execution.json](evidence/terminal_master_execution.json).
New documentation/evidence in this closing commit is additional to that inventory.

## Actual implementation

Reused existing C++20 AggregateDepth and Python native binding, native L3/replay,
exact rational metrics, replay/simulation/TCA, secured ASGI/WebSocket transport,
React/Three.js renderer and private Codespaces setup. No C++ or native binding
implementation was changed or replaced with a mock. No dependencies added.

Added a single-owner supervised Kraken candidate transport: fixed endpoint, redirect
rejection, explicit permission gates, two-symbol configuration, one active selected
symbol, snapshots/absolute updates/trades/heartbeats, CRC validation, reconnect/backoff
with bounded jitter, resubscription, fresh-snapshot resynchronization and shutdown.
Native L2 state is separate from synthetic L3 and there is no inferred order identity.

Added browser provider/instrument/depth/connect/disconnect controls, native feed state,
source/receive timestamps, depth age and reconnection diagnostics. Live mode shows no
substitute authored book when unavailable. Stale/invalid depth is hidden before socket
cleanup can await. Browser history resets across local capture segments and instruments;
visualization pause freezes history while native ingestion/current state continue.

Added bounded private L2 log writer/loader and fresh-native deterministic prefix replay,
record/disk/allocation/corruption/retention checks, authored CLI demo and benchmark.
This tooling is **not attached to live capture or browser recorded-L2 selection**.
Existing browser authored-L3 recording/replay remains working. Observed recording is
disabled, not silently granted by public endpoint availability.

## Compliance and implementation matrix

|Directive area|Delivered/evidence|Current classification|
|---|---|---|
|1 Baseline/gap audit|Repository/source/security/provider/native/3D/recording inspection and checkpoint|IMPLEMENTED|
|2 Free live connectivity|Supervised Kraken candidate, fixed endpoint, BTC/USD and ETH/USD; no Coinbase adapter|TESTED_WITH_FIXTURES; current schema/rights/live access BLOCKED|
|3 Integrity|CRC, snapshot gate, exact decimal conversions, bounded dedup, freshness, crossed rejection, resync, errors|TESTED_WITH_FIXTURES; provider has no invented sequence|
|4 Native C++ processing|Existing bounded AggregateDepth, native exact spread/mid/microprice/depth imbalance and totals reused|IMPLEMENTED and independent algorithmic checks; advanced flow PARTIAL|
|5 Live terminal|Protected controls, explicit state/provenance, no fabricated liquidity, one active symbol|IMPLEMENTED/TESTED_WITH_FIXTURES; production path not LIVE_VERIFIED here|
|6 3D/rendering|Existing interactive Three.js/2D, window/depth, inspection, camera/zoom; visualization pause; bounded history|Local browser TESTED; real-feed rendering BLOCKED; separate dedicated heatmap not implemented|
|7 Advanced analytics|Existing L3 flow and execution analytics preserved; core exact L2 metrics; no forced cancellation/queue inference|PARTIAL; causal trade/quote estimates and research statistics not added|
|8 Recording/history|Existing authored interactive replay; bounded L2 writer/loader/native prefix replay and corruption tests|PARTIAL; observed capture attachment, recording selection and interactive L2 playback missing|
|9 Free historical discovery|Existing Nasdaq/LOBSTER access ledger and restrictions retained; provider matrix updated|BLOCKED applicable rights; no additional datasets acquired|
|10 Optional equities|No free depth entitlement verified; no invented NBBO/L2/L3|BLOCKED/DEFERRED after primary feed|
|11 Security|Exact Origin/Host, v4 HTTP and WS proofs, CORS/CSP, resource limits preserved; fixed provider boundary|TESTED locally; private external identity remains owner-controlled|
|12 Efficiency|Bounded queues/cache/native/history/logs and reproducible authored benchmark|MEASURED locally; no production network/tail-latency claims|
|13 Tests|Six native configurations, three terminal-binding configs, security/browser/TLS/oracle/package tests|PASS executed scope; see counts below|
|14 Real live verification|Official docs CONNECT403; permission-gated smoke CLI blocks before socket|BLOCKED; zero actual provider snapshots/updates/trades|
|15 E2E acceptance|Private baseline owner-connected; local native replay/3D/security proven; fixture supervisor integrated|PARTIAL; genuine provider and observed recording gates remain open|
|16 Documentation|Operation/activation, L2 log/replay, security audit, evidence, README updates|IMPLEMENTED; this is a checkpoint report, not a release publication|
|17 Final audit|Failing-before defects and negative controls, repair and security review|COMPLETED local independent-style scope; not external certification|
|18 Deliverables|This report, guides, evidence, inventories, update commands and residual priorities|DELIVERED with explicit gaps|

No LIVE_VERIFIED result was produced during this task. That state is reserved in the
implementation for a production transport snapshot accepted by native C++ after
operator-attested review. Fixture injection remains HISTORICAL_SYNTHETIC and is hidden
in the terminal's LIVE view. Future runtime labels do not certify full exchange
compatibility, observed L3 or unrestricted data rights.

## Provider, terms and cost ledger

|Candidate|Source/access|Authentication/cost/rate/rights evidence|Outcome|
|---|---|---|---|
|Kraken|Official docs.kraken.com book URL: current HEAD request curl56/CONNECT403. Proposed fixed wss://ws.kraken.com/v2, no arbitrary endpoint|Current official public-auth/free-access/rate/geo/cloud/private-display/retention terms not independently verified in this task. No keys/payment requested. Prior legal request blocked.|Provisional fixtures only; no actual provider connection|
|Coinbase Exchange|Official docs.cdp.coinbase.com channels URL: current HEAD curl56/CONNECT403; prior provider-owned legacy SDK evidence retained|Legacy SDK is not current Exchange API or license proof. No current subscription/rights/rate guarantees verified.|No adapter or live qualification claimed|
|LOBSTER/Nasdaq|Existing restricted/private dataset and separately authorized historical evidence retained|No new cloud-processing/retention right inferred. No private attachment opened.|No processing or downloads|
|Equities|No eligible provider/plan reviewed|No paid trial, assumed NBBO, full depth or entitlement|Deferred/blocker|

Both current metadata requests used inherited proxy, normal TLS, timeout10s, retries0,
no destination response/body. Provider domains are absent from this managed environment's
configured destination list. No further denial retries, unapproved mirrors or bypass.
The owner's Codespace has independent networking and needs its own documented test.

## Numerical and independent evidence

The independent provider oracle uses its own level maps, bitwise CRC polynomial and
Python Fraction arithmetic against native state after10,000 deterministic authored
candidates across BTC/USD and ETH/USD.103 deliberately wrong CRCs must reject without
changing native state, followed by103 explicit authored reinitialization snapshots.
A deliberately wrong expected quantity is detected. Existing1,000-update native
map/Fraction reference and allocation/boundary tests also pass.

Exact decimal-to-integer conversion rejects nonintegral quantities/prices, overflow
and malformed inputs; no float-based book or CRC arithmetic. Price/quantity scale1e8
in the supervisor is an explicit representation choice, not a claimed venue rule.
Timestamp parsing preserves up to nanoseconds; absent exchange metadata remains null.

See [TERMINAL_MASTER_SECURITY_AUDIT.md](TERMINAL_MASTER_SECURITY_AUDIT.md) for root
causes, failing-before evidence and limits. Repairs include shared-clock depth
freshness, crossed candidates, receive-clock trust, late trade ack state, extreme
numeric parser failure, asynchronous close publication and invalid-mode side effects.
The browser pause test's completion race was corrected by waiting for its exact POST
response, keeping all prior pause/prefix assertions and adding response assertions.

## Executed validation matrix

|Configuration/check|Passed|Failed|Skipped|Notes|
|---|---:|---:|---:|---|
|GCC14.2 Debug native CTest|155|0|0|Existing current phase9-clean build|
|GCC14.2 Release native CTest|155|0|0|Same source, existing compiled native core|
|GCC14.2 ASan+UBSan native CTest|155|0|0|Failure/allocator/recovery/oracles included|
|Clang19.1.7 Debug native CTest|155|0|0|Existing current phase9-clang build|
|Clang19.1.7 Release native CTest|155|0|0|All eight canonical identities verified|
|Clang19.1.7 ASan+UBSan native CTest|155|0|0|All eight canonical identities verified|
|Terminal with installed Release binding|96|0|0|Final expanded native-backed cohort|
|Terminal with Debug binding|96|0|0|10,000-candidate oracle included|
|Terminal with ASan+UBSan binding|96|0|0|LIVE_LSAN_CHECK=0, no findings suppressed|
|Python interface/schema CTest Debug|3|0|0|Existing build-tree consumer|
|Python interface/schema CTest Release|3|0|0|Existing build-tree consumer|
|Python sanitizer CTest|4|0|0|Includes sanitizer control|
|Installed unchanged wheel interface/export unittests|14|0|0|8 interface+6 export; no new wheel rebuild claimed|
|Dedicated Origin/Host/proof/access tests|46|0|0|Current security boundary|
|Actual Chromium full application checks|21|0|0|Native replay,3D, camera, mobile emulation, refresh/reconnect|
|Additional live controls/pause checks|7|0|0|Disabled feed truthful; ETH selection; replay resumes; no fabricated live response|
|Verified loopback HTTPS/WSS integration|8|0|0|Both Origin rewrites; native step; two WSS101 upgrades|
|Frontend unit tests|3|0|0|TypeScript/Vite production build passed|
|Packaging pattern regressions|3|0|0|Negative controls retained|

Actual Chromium cross-origin credentialed fetch/no-cors negative controls also passed:
non-simple read preflight denied before issuer; stripped-header no-cors response cannot
provide a proof. No actual physical Android or external private Codespace connection
was tested. Existing Starlette/httpx deprecation and Vite bundle-size warnings remain;
no warning suppression, assertions removal or timeout increase.

The unchanged C++ source did not need rebuilding. Existing current native builds were
executed, not described as newly compiled. Initial accidental selection of obsolete
build/debug, release and asan-ubsan trees yielded stale binary/reference failures:
58/61,64/65,58/61 respectively. These old trees predate remediation and lack the155-case
current suite; current reference output contains fields absent in their binaries.
The correct current six build trees then all passed155/155. Earlier failed attempts
are retained in the evidence, not reported as passes or repaired by weakened tests.
An initial `ctest` command was also unavailable until using the installed tool path.

All eight frozen canonical identities match in **each** of the six current native
configurations. Their exact64-character values are in the evidence manifest. No
canonical fixture, C++ source, replay identity, test expectation or main file changed.
No new ARM64 qualification: prior owner/hosted evidence applies only to its exact
qualified commit, not80a6f30 or this report. Owner authorization/run is still required.

## Packaging and private-data review

Source archive rebuilt from clean implementation commit80a6f30;513 members. Inventory
verified required new code/tests, excluded build outputs, node_modules, caches, binaries,
ZIPs and private/recording directories. SHA256:
6929477cb41491590f179c86c68ad5f2b807611817825967a6fc567299068d13.
Artifact stays ignored under build/master-live/dist; no publication. Native wheel
itself is unchanged and its installed interface/export tests were rerun. No fresh
source-built-wheel or independent machine/ARM64 evidence is claimed.

No restricted raw rows, attachment, market archive, provider responses, tokens or
credentials were staged. Source fixtures are independently authored toy values.
Only source/tests/documentation and safe count/hash evidence are pushed.

## Performance and resource evidence

See the benchmark object in the evidence manifest for exact final measured values,
source commit, fixture/input/output hashes, CPU model, Python/native compiler/build,
three measured repetitions,100-event warmup and10,000 events/repetition.

Run:

```bash
git rev-parse HEAD
.venv/bin/python scripts/benchmark_terminal_feed.py --events 10000 --repetitions 3
```

The final clean-implementation run measured28,344 events/s median,19,456KiB process
peak RSS,1024-byte native PMR live state and2048-byte native PMR peak on an Intel
Xeon Platinum8573C (Linux x86_64, Python3.12.14, GCC14.2 Release). Total allocator
call counts and network/tail latency were not instrumented or claimed.

The workload alternates two authored one-level replacement snapshots; JSON, decimal,
CRC, native application and exact native metrics are included. It does not benchmark
socket throughput, arbitrary update mixtures, exchange latency or tail percentiles.
A separate untimed tracemalloc pass measures Python allocation footprint; RSS is the
whole Linux process high-water mark. Native PMR live1024bytes/peak2048bytes, no L2
journal growth. This is not a change to the existing L3 journal. No equivalent old
supervisor benchmark exists for a justified before/after speedup claim.

Bounded state: one source socket,4 queued frames,64KiB/frame, ten retained levels/side,
256 trade identities,32 native level capacity/side,1MiB native resource budget,
96 browser observations and1 latest-state browser output. L2 logs cap512 records,
2MiB,8 logs,24h maximum load eligibility. No global OS OOM/crash-safety claim.

## Reproduction and owner acceptance

[Provider operations](LIVE_PROVIDER_OPERATIONS.md) gives exact gated activation and
private Codespaces update instructions. [L2 log/replay guide](L2_RECORDING_REPLAY.md)
gives authored source-log replay. Existing C++ synthetic terminal and historical
CLI functionality are preserved. No private dataset is needed for these commands.

Owner update: Ctrl+C, `git pull --ff-only origin feat/bootstrap-cpp20-engine`,
`npm --prefix terminal/web run build`, `bash scripts/start_terminal.sh`; keep the
existing correct Origin and port8787 Private. No native wheel rebuild required.

Acceptance checklist:

- Confirm private forwarded browser CONNECTED and historical Step/restart still work.
- Confirm provider selection and ERROR/UNAVAILABLE default (no substitute liquidity).
- Verify current official provider protocol and applicable private cloud/display rights.
- Configure reviewed server permission only after that review; never set assertions
  merely to bypass the blocked status. Fixed endpoint must be reachable by policy.
- Run bounded smoke CLI, then verify actual ack/snapshot/update/trade/CRC/freshness,
  browser WSS/native metrics/3D, reconnect and source-label evidence separately.
- Obtain owner-authorized native ARM64 qualification of the new implementation SHA.
- Recording/redistribution remain disabled unless their separate rights are established.

## Residual work in dependency order

1. **Critical path:** official provider protocol/usage/access review; acquire no paid
   service or restricted dataset. Handle any documented status/admin/field differences
   with versioned authored regressions before a bounded permitted connection.
2. Actual provider/native/browser verification and outage/reconnect evidence. Preserve
   unsupported/gap states; no real-market completeness or empirical claims from fixtures.
3. Exact new-HEAD ARM64 owner qualification; no workflow was dispatched here.
4. Verified retention rights, bounded nonblocking capture integration and interactive
   recorded-L2 catalog/play/pause/seek/speed. Current offline log tools are a foundation.
5. Causally aligned native trade/quote analytics and independent references: relative
   spread, OFI, trade intensity/signed flow, realized volatility, impact/effective spread.
   Do not label L2 decreases as cancellations. Research lambda/VPIN/Lee–Ready need
   explicit methodologies, sampling/lag choices and observed validation, not UI claims.
6. Provider-specific second adapter, then optional authorized no-cost equities discovery;
   no invented consolidated NBBO or depth. Dedicated heatmap and rendering profiling
   follow actual feed qualification rather than fake motion.

The November10 target's critical path is external provider documentation/rights and
actual runtime verification, not the repaired browser connection. No delivery guarantee
is inferred from passing synthetic tests. Private synthetic evaluation is supported;
full live terminal acceptance and production trading readiness are **not closed**.
