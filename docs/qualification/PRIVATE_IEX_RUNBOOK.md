# Private, read-only IEX acceptance

This procedure targets `development/gig-ui-redesign`. It does not enable paper/live order execution, options, SIP, asset-account queries, observed exports or disk capture. Existing SEC configuration and credentials are not rewritten. The owner must keep Codespaces port 8787 **Private**, control the Codespace exclusively and use the authenticated forwarded HTTPS URL. Runtime metadata cannot independently prove that private-edge configuration.

## Update the existing Codespace

Preserve local work before switching; never reset, clean, force-push or overwrite local edits. Run one command at a time:

```bash
git fetch origin
```

```bash
git switch development/gig-ui-redesign
```

```bash
git pull --ff-only origin development/gig-ui-redesign
```

Use the existing Python environment and locked server dependencies:

```bash
.venv/bin/python -m pip install -r terminal/server/requirements.txt
```

```bash
npm --prefix terminal/web ci --ignore-scripts && npm --prefix terminal/web run build
```

Confirm the actual native module without rebuilding it unnecessarily:

```bash
.venv/bin/python -c 'import gig_microstructure as g; assert hasattr(g._native,"AggregateDepth"); print(g.native_build_info())'
```

Check configuration without network access or disclosure of credential values:

```bash
.venv/bin/python scripts/private_iex.py --check
```

`ready` means credential-alias/shape, Codespaces-origin and protocol-dependency readiness only. It is not provider authentication, native/asset qualification, billing verification or private-port proof. If existing credentials are absent from this process, use the owner's existing secure Codespaces secret configuration; do not paste values into chat, a browser form or a command transcript. No new keys are requested by this procedure.

## One bounded provider qualification

Stop the existing terminal with Ctrl+C in its owning terminal. Confirm there is no other client using this account's limited stream connection. Do not run the standalone probe alongside the gateway.

```bash
.venv/bin/python scripts/private_iex.py --qualify --confirm-private-single-user --exclusive-stream-window
```

The confirmation asserts the actual private, single-user, personal noncommercial deployment boundary. The permission profile derives from the owner's reported support confirmation #384778; it does not infer new rights from credentials.

The command reads one AAPL historical page each for bars, quotes and trades, then opens at most one 30-second IEX stream. It does not query an account or submit/cancel orders. Historical requests use a five-minute UTC interval on the previous weekday, at most 64 physical rows each. Weekday selection is not an exchange holiday/calendar assertion. An optional exact interval can be supplied with both `--start-time` and `--end-time` in RFC3339 UTC; `--seconds` allows 5–60 seconds.

Budgets: a cooperative 120-second acquisition timeout, at most nine historical HTTP attempts (three 429-bounded attempts per kind), 192 historical physical rows, one stream connection with no reconnect, 32KiB stream frames and 256 retained in-memory events. HTTP responses remain byte-bounded by the existing 512KiB transport. No raw records, prices, credentials, cursors or SEC contact values are printed; reports contain counts, source receipts and hashes. WebSocket cleanup uses the existing three-second close timeout after acquisition; this is not a measured or OS kill-enforced total process deadline. Process exit discards the accepted in-memory observations.

Interpretation:

- `PASS_BOUNDED_PROVIDER_READS_ONLY`: nonempty accepted historical observations plus fresh quote and trade observations in the stream window. This does not establish complete tape/depth, independent exchange agreement, private-edge authentication or product acceptance.
- `INCOMPLETE_OR_BLOCKED`: inspect stage categories. HTTP 401 is authentication, 403 entitlement, 404 range/resource, 429 rate limit. Authentication/entitlement rejection stops further admission attempts. Do not enable a paid fallback.
- Empty histories or quiet/off-session streaming are inconclusive; do not fabricate observations. Repeat only during an appropriate owner-chosen market window or with a justified available historical interval.
- `BLOCKED_OR_REJECTED`: private confirmation, current process configuration, active gateway, dependencies, interval or a sanitized integration failure prevented completion. Nothing changes saved credentials or permissions.

## Start the private terminal

After the standalone probe exits, start the existing backend/frontend/native application through the new fixed launcher:

```bash
.venv/bin/python scripts/private_iex.py --start --confirm-private-single-user
```

This invokes the existing `scripts/start_terminal.sh`; it does not create another server or bypass its port/dependency/asset checks. Its process-only profile sets `GIG_ALPACA_IEX_STREAM_ENABLED=1`, while keeping **`GIG_ALPACA_LIVE_ENABLED=0` and `GIG_PAPER_EXECUTION_ENABLED=0`**. Read-only IEX and specific IEX history flags carry the documented permission reference. Disk capture, exports, options and SIP remain off. No provider stream is opened until the operator explicitly starts it in Live Markets. Existing independently configured SEC discovery may still run under its own unchanged SEC permissions.

Keep 8787 Private. Open the existing Codespaces authenticated HTTPS address and hard-refresh Chrome. Use Live Markets to choose up to the configured 1–4 symbols and start quotes/trades; stop this shared stream before another standalone probe. Subscription updates are in place, but the unsubscribe/subscribe handover has a disclosed observation gap.

Inspect source, receipt timestamps, stale/quiet status and provenance. IEX is partial venue coverage, not consolidated NBBO or a complete market tape. Level 1 quotes cannot supply native order identities or Level 2/3 depth. Historical research displays accepted observations; native L3 replay remains independently authored/validated and is not relabeled observed IEX.

The eight advanced depth/event models require eligible source inputs. Unavailable depth stays unavailable. Camera orbit does not generate observations or advance replay. The native execution simulator and fake paper sandbox remain separate from default-disabled broker execution.

## Exact-source/private-edge acceptance

With a clean checkout and the server running, bind a local receipt:

```bash
.venv/bin/python scripts/qualify_private_deployment.py --expected-sha "$(git rev-parse HEAD)" --check-local-server --output build/private-deployment-acceptance.json
```

This checks local source/assets/runtime/health, not GitHub authentication. Independently verify the forwarded URL requires the owner account, then check HTTPS state, replay mutation, WSS reconnect, all 12 workspaces and 15 eligible visualization modes in desktop/mobile themes. Do not publish screenshots containing observed market data. Owner browser/device review and the current native ARM64 run remain outstanding acceptance gates.

## Owner-gated ARM64

The existing `Native ARM64 qualification (owner-gated)` workflow is still manual-only with `free_usage_verified` defaulting false. It now permits this exact development branch as well as the two previously approved branches. No workflow was dispatched by this sprint.

After verifying current free eligibility/usage, an owner may separately authorize a run against the delivered redesign SHA. Preserve all six native compiler/configuration jobs and eight hash checks; the GCC Release job additionally runs the new offline qualification cohort. Record exact run ID, SHA, architecture and conclusions. An earlier ARM64-qualified commit does not qualify this candidate. No main/release workflow registration was changed here.
