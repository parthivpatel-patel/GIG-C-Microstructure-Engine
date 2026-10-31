# Exact-candidate private acceptance runbook

This is the **final qualification procedure**, not a request to perform repetitive
intermediate development checks. Sprint2 engineering source is
`62d8d50e2dd629db181114eaceb5845509a137b6`; the final delivery tip also contains
documentation/evidence only. Use the full final SHA reported at delivery as
`<FINAL_SHA>`. Do not substitute a newer untested tip or derive the expected SHA
only from the same unchecked directory. No merge/release/paid runner is authorized.

## 1. Preserve and select the candidate

Run each command separately. Do not discard a dirty checkout or overwrite a
private configuration. If `git status` is dirty, stop candidate switching and
preserve the work; create another checkout through normal owner-controlled means.

```bash
git status --short
```

```bash
git fetch origin fix/atlas-private-qualification-2
```

```bash
git switch --detach <FINAL_SHA>
```

```bash
git rev-parse HEAD
```

The last value must equal the independently recorded full delivery SHA. Detached
inspection changes no branch tip and merges nothing. The existing `.venv` and
private SEC configuration are not committed or recreated. Do not re-enter keys.
If dependencies/assets are already at this version, do not reinstall unnecessarily.
If missing, follow the existing `scripts/setup_terminal.sh` after reviewing its
locked install steps; a network install is not part of the offline qualifier.

With already installed dependencies:

```bash
.venv/bin/python -m pip check
```

```bash
npm --prefix terminal/web run build
```

```bash
.venv/bin/python scripts/qualify_private_deployment.py --expected-sha <FINAL_SHA> --output build/private-deployment-before-new.json
```

PASS means offline checks only. Missing/old assets, wrong SHA, dirty tracked source,
unexpected runtime files or mismatched runtime pins are blockers. Do not ignore a
nonzero exit or delete a prior result to make it green. Use new output filenames.
Inventory/advisory clearance and hardware qualification remain separate gates.

## 2. Start the private native-backed application

Stop only the existing GIG process in its own terminal using Ctrl+C. Do not kill
unidentified processes or clear owner caches. Then:

```bash
bash scripts/start_terminal.sh
```

In a second terminal, compare the running startup receipt:

```bash
.venv/bin/python scripts/qualify_private_deployment.py --expected-sha <FINAL_SHA> --check-local-server --output build/private-deployment-running-new.json
```

This verifies a fixed loopback native server receipt, **not external authentication**.
If the old process remains, stop it normally and restart the candidate. Do not add
localhost to the external Origin allowlist to repair a failed forwarded request.

## 3. Private GitHub HTTPS/WSS gate — actual target required

- In Codespaces Ports,8787 must remain **Private**. Use its actual forwarded HTTPS
  URL while logged in to the intended GitHub account. Never publish the URL with
  cookies/tokens/proofs or alter visibility to public.
- In a fresh unauthenticated/incognito session, opening the forwarded application
  must require GitHub sign-in/authorization and must not expose terminal state.
  Local proxy fixtures cannot prove this boundary.
- In the authenticated session, verify native state, step/restart controls, actual
  WSS upgrade and connected transport. Capture only sanitized `/api/v1/connection`
  decisions and startup receipt, not DevTools full headers or storage.
- Temporarily disconnect/reconnect browser networking, then reload if necessary.
  State must disclose staleness during loss and recover without duplicate control
  application or Origin/Host bypass. Source freshness is distinct from connectivity.
- Use actual desktop Chrome plus Android Chrome if available. Record OS/browser,
  device versus viewport emulation, candidate SHA and per-flow pass/failure. Keyboard,
  touch, zoom, reduced motion and focus must remain usable. No physical-device or
  WCAG certification is prefilled by this runbook.

## 4. All12 workspaces

Use ordinary clicks; overlapping/inaccessible controls are failures. Record the
selected source, timestamp/absence, mode and candidate SHA rather than raw observed
market rows. Test both themes and360/390 mobile plus768/1280/1920 desktop widths.

| Workspace | Required acceptance |
|---|---|
| Command Center | Navigation, global search, watchlist persistence, unavailable/provider indicators; no fabricated live summary. |
| Securities Universe | Search AAPL/APLD/CRWV, exact identity and coverage disclosure; SEC registrants are not the complete exchange-listed universe. |
| Stock Intelligence | Company switching, selected financial periods, backend ratios/units/quality, missing facts, source-linked filings, pagination/filter, theoretical options labels. Do not interpret selected facts as complete statements. |
| Live Markets | Disabled entitlement state is correct while blocked; authorized future observations must retain exact provider/feed/time/freshness. |
| Multi-Stock Comparison | Watchlist/search, per-symbol unavailable/freshness, independent display pause, shared-scale labels and configured simultaneous-subscription cap. No fake fallback quotes. |
| Order Book | Native authored orders/levels, exact scales and source label, readonly proposed HHI formula/coverage disclosure. |
| Market Depth | Exact native/replay depth, no L2/L3 invention from L1, optional landscape controls and2D alternative. |
| Order Flow | Event source/order and unavailable trade-direction information remain explicit. |
| Historical Replay | Step/play/pause/seek/speed/restart, deterministic same-prefix state, dataset identity and synthetic/observed distinction. |
| Execution Simulator | Schedules/fills/costs are clearly simulated, input failures explicit, no external order routes. |
| Research & Validation | Units, declared inputs, theoretical versus observed models, bounded job errors, missing-data outputs and research limits. |
| Operations | Health/startup SHA, safe sanitized connection diagnostics, source status, no secrets/private contact; retain unresolved readiness gates. |

## 5. All13 visualization modes

The thirteen-mode denominator is four L1 projections + eight advanced research
modes + the declared GARCH response surface. The older native landscape is also
checked in Market Depth; it is not used to inflate this denominator.

| Mode | Required evidence/source boundary |
|---|---|
| L1 quote price | Actual best bid/ask observations only, or clearly authored fixture; no inferred depth. |
| L1 comparison | Retained valid-mid baseline and basis-point axis, symbol isolation; no fabricated history. |
| L1 realized variation | Enough retained valid mids;8 squared log-mid changes, not annualized or forecast accuracy. |
| L1 trades | Actual print size/price or explicitly synthetic input; log-size geometry label. |
| Order-book height map | Supplied native/replay depth, axes and exact tooltip, coverage disclosed. |
| V-canyon | Same discrete depth, no continuous unobserved-liquidity claim. |
| Event voxels/point cloud | Actual explicit add/cancel/delete/execute event source where available; absence is unavailable, not guessed from snapshots. |
| VWAP corridor | Declared supplied depth/price-weighting assumptions; no observed execution guarantee. |
| Flow streamlines/VPIN | Requires explicit admissible events/direction; distinguish toy proxy and unavailable classical VPIN inputs. |
| Cylindrical depth wheel | Discrete supplied levels with meaningful scale/side legend. |
| Volatility dome | Declared retained-mid variation/window, no calibrated forecast claim. |
| Bid-ask ribbon | Exact L1/replay bid/ask source and spread, no deeper levels invented. |
| GARCH surface | Declared one-step conditional-variance grid, parameter validation, not observed implied volatility or fitted prediction. |

For each applicable mode: rotate/zoom/pan; independent controls/camera reset/presets;
symbol/time/filter selection; pause/resume; accurate tooltip/axes/legend; fullscreen
where supported; reduced motion; WebGL/context failure and2D fallback. Sparse or
unavailable data is a valid unavailable outcome, not automatic rendering PASS.
Record actual frame responsiveness/resource behavior; this sprint's local browser
cohorts do not constitute target GPU or physical Android qualification.

## 6. Existing SEC evidence, ARM64 and remaining gates

- Bind the existing authorized SEC result using [SEC_EVIDENCE_BINDING.md](SEC_EVIDENCE_BINDING.md).
  Do not refetch, repeat contact setup or fabricate historical code/time metadata.
  10,429 identities and1,772 selected matches remain owner-reported until exact
  supplied bytes are bound. File hash binding still is not independent provider execution.
- Current-candidate native ARM64 remains **UNVERIFIED**. Existing
  `.github/workflows/atlas-native-arm64.yml` is manual-only, owner/free-usage gated,
  and accepts **only `feat/atlas-final-release`**. It therefore will **not qualify
  this isolated Sprint2 branch**. Do not dispatch it here or merge for convenience.
  A separately authorized, narrowly guarded candidate qualification path must check
  out this exact candidate on genuine native ARM64 and preserve six configurations,
  strict counts, eight hashes, Python/package gates and free-runner eligibility.
  Record actual run ID, SHA, architecture and conclusions; old runs do not transfer.
- Clear target runtime/transitive/system/browser/Action advisory questions with
  exact version/backport evidence. Offline pin matching is not security clearance.
- Obtain scope decisions A18/A19 as described in [REMAINING_BLOCKERS.md](REMAINING_BLOCKERS.md).

## 7. Future Alpaca qualification — not executed or enabled

Keep gates disabled. Basic personal noncommercial research and IEX availability
are owner-confirmed; private Codespace processing, authenticated display and
historical IEX scope/limits remain specifically pending. Follow
[Sprint1's prepared checklist](../sprint-1/ALPACA_QUALIFICATION_CHECKLIST.md) only
after those decisions and separate bounded qualification authorization. Use existing
keys; no repeated setup, paid feed, orders, extra subscription or observed retention.
Record actual catalog count/coverage, bounded AAPL history and shared-connection
stream/reconnect/source-time results if later authorized. Fixtures do not qualify
those feeds. Data absence while a gate is disabled must remain honestly unavailable.

Final acceptance is a signed-off set of source-bound per-flow results and explicit
exclusions, not a single green badge or a production/observed-L3/alpha claim.
