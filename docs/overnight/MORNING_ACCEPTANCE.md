# Morning acceptance — October 30, 2026

Use the existing private GitHub Codespace and existing secrets. This is the final
acceptance sequence,not a request to repeat setup. Keep port8787 **Private**. Stop
only the existing ATLAS server with Ctrl+C in its terminal before source probes;
this avoids background SEC refresh and competing account streaming connections.
Do not stop another project. Run one command at a time from this repository on
`feat/atlas-final-release`. Do not continue to acquisition if the pull fails.

## 1. Update

```bash
git pull --ff-only origin feat/atlas-final-release
```

No new dependency,SEC contact,key or native rebuild is required by this sprint.
Frontend source is unchanged;your existing successful frontend build remains usable.
The final SHA and source/test evidence are in `OVERNIGHT_COMPLETION_REPORT.md` and
the delivery response. Native wheel build identity can remain older because no
native source/ABI changed;it is not proof of ARM64 qualification of this new HEAD.

## 2. Verify the actual SEC repair

```bash
.venv/bin/python scripts/qualify_sec_sources.py --fetch --resolve-identity --symbol AAPL --as-of 2026-10-28
```

The fixed comparison date reproduces the original blocker;it does not mean this is
the latest filing snapshot. Expect exact official AAPL identity and
`AGREEMENT_WITHIN_SELECTED_RECORD_SCOPE` with positive matched records and zero
mismatches. That is selected-fact agreement,not complete statements or intraday PIT
certification. Failure exit2 includes a bounded stage/code/record diagnostic;preserve
it. Do not change keys/contact or broadly enable feeds to repair a source rejection.
No raw response,contact,cookies or credentials need to be pasted anywhere.

## 3. Qualify permitted catalog/history and optionally IEX

Run **one** of these alternatives,not both. They reuse existing settings,disable
observed retention for their own process,and never place orders.

If live permission or a free exclusive account stream slot remains unverified:

```bash
.venv/bin/python scripts/qualify_atlas.py --execute
```

Only if applicable existing private/cloud/display permission records and gates are
already verified,and other applications will not consume the shared free account
stream slot during the30-second qualification window,use this instead:

```bash
.venv/bin/python scripts/qualify_atlas.py --execute --exclusive-stream-window
```

Do not enable permission flags merely to obtain PASS. Missing applicable provider
evidence,including unresolved support381230 conditions,remains BLOCKED. No new
general account authorization or key setup is requested. The helper refuses an
active ATLAS gateway and has no automatic retries. It reports actual accepted
catalog counts,coverage,source-qualified bounded AAPL/MSFT IEX history and exact-time
comparison where permitted. The catalog is account/source-scoped,not a complete US
exchange master. SEC is qualified independently of Alpaca;the consolidated helper
performs additional bounded reconciliation reads intentionally.

IEX PASS requires actual fresh quote **and** trade observations. Quiet/off-hours,
empty,unauthorized or failed windows remain INCONCLUSIVE/BLOCKED,not a reason to
repeat connections. The helper is transient:its cache does not become the terminal's
live cache. Keep its output private;do not commit observed data or provider screenshots.

## 4. Start the actual terminal privately

```bash
GIG_ALPACA_STORE_ENABLED=0 GIG_HISTORY_STORE_ENABLED=0 bash scripts/start_terminal.sh
```

Leave this terminal running. Open the existing HTTPS address from the Codespaces
**Ports** tab for8787;its visibility must remain Private with GitHub authentication.
No new externally verified URL is supplied by this Codex session. Do not use your
phone's `127.0.0.1` address. If8787 is occupied,the launcher refuses to replace a process.

## 5. One browser acceptance pass

- Confirm connected transport and native engine health. Do not treat stale state as live.
- Search AAPL,APLD,CRWV;check source identity and exact or explicitly null CIK.
  Discovery success alone does not establish available financials or feed rights.
- Load allowed company data. Inspect periods,units,filing links,source timestamps and
  accepted/excluded directory counts. Selected reported facts are not full statements.
- Where authorized,inspect actual IEX quotes/trades and per-symbol freshness. Separate
  source observations from authored inputs,modeled outputs and native synthetic replay.
- Navigate all12 workspaces. Exercise replay,simulation,diagnostic fits and holdouts.
  A429 analytical busy response means another bounded job is still finishing;do not
  repeatedly click or interpret a canceled browser request as canceled computation.
- Exercise the13 applicable visualization modes,camera reset/rotate/zoom,2D fallback,
  light/dark themes and Android layout. Replay-only depth and toy VPIN remain labeled.
- Briefly reconnect only the browser network. Check current state resynchronization
  without opening another upstream connection or relabeling stale data LIVE.

Record exact Git HEAD,private-source report hash,source status and any reproducible
safe error in ignored private evidence. The existing template
`docs/milestones/FINAL_ACCEPTANCE_TEMPLATE.json` can be copied into private storage.
Owner acceptance,real-source verification,current-candidate ARM64/hosted qualification
and production readiness are separate. No workflow should be launched by the agent.
Do not merge,tag,publish,trade or enable observed retention as part of this sequence.
