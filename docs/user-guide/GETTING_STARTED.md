# Start GIG ATLAS

GIG ATLAS is a private research application. The C++ engine runs deterministic order-book, replay and simulation calculations. A Python service exposes bounded APIs. The browser displays results and their source labels. Provider execution stays disabled by default;the native simulator and authored paper sandbox do not place broker orders.

## Existing Codespace

Preserve any local changes before switching branches; do not reset or clean the worktree. These commands select the isolated Sprint 4 candidate and leave protected branches unchanged:

```bash
git fetch origin feat/atlas-sprint-4-market-data-paper:refs/remotes/origin/feat/atlas-sprint-4-market-data-paper
```

```bash
git switch feat/atlas-sprint-4-market-data-paper
```

```bash
git pull --ff-only origin feat/atlas-sprint-4-market-data-paper
```

For an existing working environment, install the locked frontend dependencies and compile finalized assets:

```bash
npm --prefix terminal/web ci && npm --prefix terminal/web run build
```

Stop the old terminal with Ctrl+C in its own terminal. Then:

```bash
bash scripts/start_terminal.sh
```

If this is a new environment, first read and run `scripts/setup_terminal.sh`; it installs the server dependencies/native package and builds frontend assets. Existing private SEC/provider configuration must stay private. Never paste its contents into a report. Do not set provider or paper permission flags to make an empty screen disappear.

Keep port 8787 **Private** in Codespaces' Ports panel. Use its HTTPS **Open in Browser** address on a browser signed into the owner GitHub account, including Chrome on Android. `127.0.0.1:8787` on a phone points to the phone. This sprint's loopback/TLS fixtures do not establish external Codespaces authentication or physical-device acceptance.

## First offline journey

1. Command Center → search AAPL, MSFT or NVDA → Stock Intelligence. Identity discovery is independent of SEC availability and feed rights.
2. Read source and missing-data badges. Unavailable means no accepted observation, not a zero price or zero revenue.
3. Choose **Open Level 1 research**. This saves an identifier for research; it does not subscribe or start Alpaca. With no permitted input, the model explicitly has no eligible observations.
4. Order Flow → **Open advanced research** → **Authored two-symbol depth / event fixture v1**. Inspect models, rotate/pan/zoom, choose symbol/time and compare the 2D/table alternatives. These are synthetic examples.
5. Execution Simulator → run a native authored simulation. Separately, open the explicitly authored **Paper execution sandbox** to exercise fake intents and risk controls. See [paper guide](ALPACA_PAPER_TRADING.md).
6. Operations shows source and browser transport diagnostics. Configuration readiness, a connected browser and a genuine upstream provider feed are different states.

Dark/light theme persists in this browser. Tab reaches named controls and canvases; focus is visible. Reduced-motion settings disable unnecessary motion. Tables scroll inside their containers. On a narrow screen the workspace navigation scrolls horizontally; the compact-navigation button remains available.

## Reproduce offline checks

Use a separate provider-disabled local test environment, not an active acquisition server. With the native package installed:

```bash
.venv/bin/python terminal/tests/run_sprint3.py
npm --prefix terminal/web test
```

The strict fake Sprint3 backend cohort expects 52 tests;the additional Sprint4 cohort below expects 93. Browser fixture scripts require their named loopback fixture servers, Playwright/Chromium and a completed frontend build. Never rebuild assets during browser tests. See `docs/sprints/sprint-3/IMPLEMENTATION_REPORT.md` for exact executed evidence and environment limitations. Native builds and sanitizers follow `CMakePresets.json` and `docs/REPRODUCIBILITY.md`.

For developer browser qualification in a separate stopped/provider-disabled instance,install `terminal/tests` dependencies and Chromium in the development environment first. Then run:

```bash
.venv/bin/python terminal/tests/run_sprint3_browser.py
```

This runner builds once,owns its loopback fixture servers,refuses occupied ports and blocks external Python socket connections. It writes authored-only evidence under `build/sprint3-qualification/`;it does not change Codespaces port visibility. Do not point fixture programs at an active operator acquisition server. Its headless test browser uses software rendering and container test flags,not the owner Chrome runtime. The optional `--skip-build` requires independently verified finalized assets;the default performs the build before any browser test.

## Sprint 4 research and qualification boundaries

Stock Intelligence → Overview → **Exact-time historical research / explicit IEX or delayed SIP** provides explicit feed,UTC interval,adjustment and trailing-window controls. On a default server the acquisition button is disabled and explains the missing permission. This is intentional. Securities discovery and SEC availability do not grant historical-data rights. No provider request occurs at startup.

After separately documented future approval,accepted bars can drive descriptive research and the bar-derived volatility dome;actual historical best quotes can drive compatible quote displays. Histories remain historical,even if fetched just now. Multi-Stock Comparison uses exact shared source endpoints and refuses interpolation. See [model guide](QUANT_MODELS_EXPLAINED.md) and [data guide](MARKET_DATA_AND_LIMITATIONS.md).

Execution Simulator keeps three distinct boundaries:native simulation,authored fake sandbox,and the **Alpaca paper provider boundary**. The last is implemented but default-disabled and not provider-qualified. Do not turn flags on to make it display a balance. Never use the fixture server as an owner acquisition server.

Safe offline developer check,with a native package already installed:

```bash
.venv/bin/python terminal/tests/run_sprint4.py
```

The network-disabled fixture/browser procedure is documented in `docs/sprints/sprint-4/IMPLEMENTATION_REPORT.md`. There are no owner instructions to enter credentials or activate provider/order gates in this sprint. Stop the application with Ctrl+C in its owning terminal;provider enablement is not part of stopping or restarting.
