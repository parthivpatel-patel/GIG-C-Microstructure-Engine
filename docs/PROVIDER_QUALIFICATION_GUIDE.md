# Provider qualification and owner handoff

## Evidence boundary

Status at this checkpoint: terminal integrations TESTED_WITH_FIXTURES; actual provider
protocol conformance and permitted cloud processing BLOCKED. No exchange subscription,
market-data collection, account access, recording or restricted historical processing
was performed in this execution. Current official Kraken/Coinbase schemas and usage terms
were not retrieved in this managed environment. Existing cloud restrictions are not
bypassed or repeatedly retried. Coinbase Exchange-shaped support remains provisional.

OWNER_SUPPLIED evidence, not independently rerun here: Codespaces metadata HEAD returned
Kraken documentation308, legal200, ordinary HTTPS to the WebSocket host404, without
CONNECT403. HTTP404 is not evidence of a failed WebSocket upgrade. The owner also
confirmed connected browser transport, saved/loaded authored recorded L2, BTC/USD book,
3D rendering, history and preserved synthetic classification. No provider observations
or usage permission follow from either statement.

## Update the private Codespace

Stop the existing server with Ctrl+C. Keep port8787 Private and retain exact Codespaces
Origin configuration. On the existing feature branch:

```bash
git pull --ff-only origin feat/bootstrap-cpp20-engine
bash scripts/start_terminal.sh
```

Select Coinbase or Kraken explicitly in Live provider. With default gates, Connect
reports unavailable data and publishes no authored replay book as live. Coinbase cannot
start the Kraken-specific observed recorder. Do not enable flags merely to remove a warning.

## Handshake-only check

Run separately, without enabling terminal live mode:

```bash
timeout 20s .venv/bin/python scripts/diagnose_websocket_access.py --provider kraken
```

`--provider coinbase` uses its separately fixed endpoint. One connection, zero retries,
zero redirects, zero application sends/subscriptions. Strict certificate/hostname
verification and inherited proxy trust remain enabled. Async overall12s, open5s,
passive receive at most two4096-byte frames, close2s; outer20s bounds process startup.
There is no payload retention or raw message output. Unsolicited application frames
are discarded and stop inspection. TLS/WebSocket and passive-control observations
are separate from full protocol conformance or usage authorization. Under a configured
proxy DNS is explicitly not observed locally; the script does not bypass it to obtain
DNS evidence. Share only the resulting sanitized JSON, never proxy URLs or credentials.

Existing lightweight metadata diagnostic remains:

```bash
timeout 20s .venv/bin/python scripts/diagnose_provider_access.py --provider kraken
```

It sends HEAD, never follows redirects or consumes documentation bodies. A canonical
same-host HTTPS redirect may be printed after sanitization; it is not automatically
requested. Protocol/terms review requires actually obtaining the current official text
through an authorized browser. Supply official links/version/relevant wording and check:
Kraken book/trade schema, decimal CRC representation, snapshot depth/truncation,
multiple updates to the same price, online/status semantics, trade side and timestamp;
Coinbase Exchange versus Advanced Trade endpoint, authentication/channel entitlement,
snapshot/update units, ordering/sequence scope, match/last_match side and heartbeat.
Private display, cloud processing, attribution, retention and redistribution must be
reviewed separately. A successful handshake alone authorizes none of these.

## Separate live permission namespaces

Kraken uses `GIG_LIVE_`; Coinbase uses `GIG_COINBASE_`. Each requires ENABLED=1,
PROTOCOL_REVIEWED=1, PRIVATE_DISPLAY_APPROVED=1, CLOUD_PROCESSING_APPROVED=1 and a
bounded PERMISSION_REFERENCE documenting actual review. Existing Kraken attestations
cannot enable Coinbase. Do not set these until justified and an owner-authorized market
subscription test is approved. RECORDING_RETENTION_APPROVED is a separate permission;
Coinbase recording remains unsupported regardless. No live test was run here.

Coinbase maintains at most256 native levels per side, exposes top10, and rejects an
oversized snapshot rather than dropping deeper liquidity. This may block real full-depth
snapshots. Native depth metrics cover all admitted levels; rolling Python research uses
the declared top10 projection. Match side is an unverified maker-role candidate, never
fabricated aggressor direction. Hidden order identities, FIFO, exchange gap proof and
checksum are not inferred. Disconnect/update-before-snapshot requires fresh state.

## Fixture regression commands

```bash
.venv/bin/python terminal/tests/run_native_suite.py --expected-tests 176
npm --prefix terminal/web run build
npm --prefix terminal/web test
```

The CLI isolates authored localhost policy and disables both live flags. Browser harnesses
first require health.fixture_tests_safe=true, refusing an enabled/active feed, observed
replay or recording. Never run fixture browser tests against a working live terminal.
Use a separate private fixture instance. All fixture source values remain synthetic.

## Owner-controlled ARM64 qualification

The separate Native ARM64 workflow is still workflow_dispatch only, guarded to
feat/bootstrap-cpp20-engine and free_usage_verified=false by default, with the original
six configurations. New GCC Release wheel-consumer step runs all176 terminal fixtures
with both provider flags0, a temporary recording directory, and the freshly built native
replay binary path. Existing155/158 CTest counts and all eight frozen hashes remain
mandatory. Policy tests pass locally; no full YAML/actionlint or hosted execution claim.

After owner confirmation of current free public-runner eligibility/quota, select the
latest feature branch in Actions, Native ARM64, Run workflow and deliberately enable
free_usage_verified. This execution does not dispatch it. A successful run must record
exact SHA, runID, aarch64 architecture, six conclusions, eight hashes and176 terminal
outcomes (zero fail/error/skip). This adds GCC Release terminal binding qualification;
it does not claim ARM browser or every Python sanitizer combination. Previous ARM64
success remains tied to its tested SHA, not this checkpoint. Formal release, independent
machine/browser, observed-data calibration and production readiness remain separate gates.
