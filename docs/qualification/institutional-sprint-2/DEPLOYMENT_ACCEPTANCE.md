# Exact-source upgrade, rollback and private deployment acceptance

This is an owner-run procedure, not a claim that the owner's machine was accessed. Runtime candidate `b91de9e0189a6a4ebbcb1c1cbcc583945495e297` contains the tested recovery implementation; the following closure commit adds only qualification documentation. Use the **full delivered SHA from the final delivery message** for deployment. Never substitute an unrecorded moving branch tip.

## Preconditions

Keep port 8787 **Private**, the existing Codespace owner-only and authenticated. Do not paste keys, cookies, SEC contact values or private files. Stop the existing server with Ctrl+C in its terminal before replacing assets. Do not kill unrelated processes. Keep all provider, observed retention/export, paper and live execution gates disabled for this deployment test.

Run one command at a time from the repository root. First:

```bash
git status --short --branch
```

Stop on any changes, detached/unexpected branch or owner work needing preservation. No reset/clean/stash/discard is prescribed. Record the currently deployed full SHA for rollback:

```bash
git rev-parse HEAD
```

If a permitted private store already exists, stop its writer and preserve a separate private, permission-preserving backup before upgrade. Copying private observations requires applicable retention rights; do not enable storage or duplicate a store where those rights are absent. Never commit/upload it. This sprint makes no database migration and does not qualify a filesystem/power-loss recovery guarantee. Preserve failed stores for diagnosis rather than reinitializing them.

## Upgrade to the exact delivered commit

Set this public source identifier to the full final SHA; it is not a credential:

```bash
GIG_QUALIFICATION_SHA=PASTE_FULL_DELIVERED_40_CHARACTER_SHA
```

```bash
git fetch origin development/gig-ui-redesign
```

```bash
git merge-base --is-ancestor "$GIG_QUALIFICATION_SHA" origin/development/gig-ui-redesign
```

```bash
git switch development/gig-ui-redesign
```

```bash
git merge --ff-only "$GIG_QUALIFICATION_SHA"
```

```bash
test "$(git rev-parse HEAD)" = "$GIG_QUALIFICATION_SHA"
```

Stop if any command fails. In particular, a local branch already newer than the candidate will not be rewound; the final equality check must pass. Do not merge into main/release or replace a newer branch. Branch/ref preservation is required even if the candidate cannot be installed.

Install the pinned server requirements in the owner's existing Python 3.12 environment, without printing configuration:

```bash
.venv/bin/python -m pip install -r terminal/server/requirements.txt
```

```bash
.venv/bin/python -m pip check
```

```bash
npm --prefix terminal/web ci --ignore-scripts
```

```bash
npm --prefix terminal/web run build
```

```bash
.venv/bin/python -c 'import gig_microstructure as g; assert hasattr(g._native,"AggregateDepth"); print(g.native_build_info())'
```

The native inputs are unchanged in Sprint 2. Preserve a valid installed module; if it is absent/incompatible use the existing `scripts/setup_terminal.sh`/native setup procedure and record that new build rather than claiming the old module qualifies the target. Do not remove an owner environment to force installation.

Offline receipt (the output path must not already exist):

```bash
.venv/bin/python scripts/qualify_private_deployment.py --expected-sha "$GIG_QUALIFICATION_SHA" --output build/sprint2-target-offline.json
```

`PASS_OFFLINE_CHECKS_ONLY` requires source/assets/pins; it does not establish CVE clearance or GitHub access control. Stop on mismatch and keep the sanitized report.

Start the existing actual native-backed terminal with **process-only** disabled gates; existing saved SEC/Alpaca settings are not rewritten:

```bash
GIG_SEC_ENABLED=0 GIG_ALPACA_ENABLED=0 GIG_ALPACA_IEX_STREAM_ENABLED=0 GIG_ALPACA_LIVE_ENABLED=0 GIG_PAPER_EXECUTION_ENABLED=0 GIG_LIVE_ENABLED=0 GIG_COINBASE_ENABLED=0 GIG_ALPACA_STORE_ENABLED=0 GIG_HISTORY_STORE_ENABLED=0 GIG_LIVE_RECORDING_ENABLED=0 bash scripts/start_terminal.sh
```

In another terminal, using the same full SHA:

```bash
.venv/bin/python scripts/qualify_private_deployment.py --expected-sha "$GIG_QUALIFICATION_SHA" --check-local-server --output build/sprint2-target-running.json
```

A local startup `MATCH` binds source/assets to the server receipt; it is not loaded-byte attestation, provider acceptance or external authentication. Keep the server in its owning terminal. A Codex process is not persistent hosting.

## Minimal target acceptance

1. Confirm the Ports panel shows 8787 **Private** and the forwarded HTTPS URL requires the owner GitHub account. Do not change visibility or copy authenticated URLs/cookies into reports.
2. Through that private URL, verify actual-native state, one authored replay step, stream reconnect after an ordinary page reload, and Operations diagnostics without an Origin warning. Record delivered SHA and sanitized outcome. Do not treat local proxy tests as this evidence.
3. Review all 12 preserved workspaces and eligible 15 visualization modes in dark/light desktop and mobile views. Missing market depth must remain unavailable; authored L3 replay is not live IEX. A phone viewport simulation is not physical-device acceptance.
4. Obtain target OS/transitive dependency/advisory and installed artifact clearance. Separately, an owner may authorize the existing free-eligible, manual-only ARM64 workflow against the exact candidate with all six configurations and eight identity checks. This sprint did not launch it.
5. Actual IEX/history acceptance is a separate owner-authorized private window under the existing read-only runbook. No credential entry, provider call, retention activation or trading action is part of this Sprint 2 deployment test.

## Non-destructive rollback

Stop the candidate server and require a clean working tree. Use the recorded previous full SHA; Sprint 1's known rollback source is `90ebb956df5143670702bcc512de81821cdfa23d`.

```bash
git switch --detach 90ebb956df5143670702bcc512de81821cdfa23d
```

This preserves `development/gig-ui-redesign` and remote history; it does not reset or force-push. Reinstall the prior pinned dependencies/rebuild prior assets, verify the native ABI, and repeat the offline/running receipts with that exact previous SHA before starting with the same disabled gates. Do not copy a newer frontend onto older backend source. Never overwrite a failed/current database with a backup automatically. Schema version remains 1, but malformed records deliberately rejected by this repair are not made trustworthy by downgrading.

After diagnosis, stop the server, require clean state and return with `git switch development/gig-ui-redesign`; verify the intended full SHA again. Private ignored configuration/store directories remain in the same checkout and must stay private. This is a source/asset rollback procedure, not an automated database downgrade or guaranteed RPO/RTO.

## Executed local evidence

A disposable local Git repository fetched the exact candidate and Sprint 1 parent from the existing repository, fast-forwarded to the candidate, detected an authored dirty-file stop condition, detached to the baseline, verified the candidate branch pointer was preserved, and returned to it cleanly: five checks passed. No network/protected ref/owner worktree was changed. The clean candidate offline receipt passes and its actual loopback native-backed server startup receipt matches; a Chromium capture correlates browser Origin and the ticket-authenticated WebSocket. These do not establish owner-target installation/authentication or database downgrade safety.
