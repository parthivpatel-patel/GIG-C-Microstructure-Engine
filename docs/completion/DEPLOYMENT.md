# Private deployment and reproducibility

In the existing Codespace, stop the previous server with Ctrl+C, then:

```bash
git switch feat/atlas-final-release
git pull --ff-only origin feat/atlas-final-release
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

Keep port 8787 Private and use the existing authenticated HTTPS forwarded address. No new
URL, localhost allowlist entry, credential in frontend code, paid service or native rebuild
is required. Native WSS remains independent; stock push uses proof-authorized same-origin
HTTPS POST/SSE, avoiding WebSocket Origin rewriting. The launcher bounds graceful shutdown
to five seconds so long-lived HTTP streams cannot hold shutdown indefinitely. It does not
promise crash-safe market-tape recovery.

Do not turn on provider flags to clear warnings. Alpaca support381230/account permissions,
server credentials and actual source qualification remain separate external requirements.
No manual owner feature testing was required to develop or validate this checkpoint.
Actual provider qualification must occur only in an appropriately authorized environment;
the existing bounded script remains `python scripts/qualify_alpaca_live.py --execute
--symbol AAPL --seconds 30` after those requirements are legitimately satisfied.

## Optional session schedule

No calendar is bundled or inferred. If an authorized owner supplies independently verified
schedule evidence, store it privately under `.gig-session/` and set the server-only
`GIG_MARKET_SESSION_FILE` to that regular JSON file. Do not put credentials or private URLs
in source references. Authored test schema (not an exchange schedule):

```json
{"schema":"gig.session.schedule.v1","source":"AUTHORED_EXAMPLE_NOT_EXCHANGE_AUTHORITY","symbols":["AAPL"],"intervals":[{"start":"2024-01-02T14:30:00Z","end":"2024-01-02T21:00:00Z","state":"REGULAR"}]}
```

States are PRE/REGULAR/POST/CLOSED, intervals are half-open and must be sorted/nonoverlapping.
Uncovered periods remain UNKNOWN, not assumed closed. Restart to reload configuration.
This schema does not establish holiday/auction/real-time halt coverage or schedule accuracy.

## Offline qualification

Using the already validated native package/Python environment:

```bash
python terminal/tests/run_live_market_suite.py
python terminal/tests/run_native_suite.py --expected-tests 274
npm --prefix terminal/web test
npm --prefix terminal/web run build
python terminal/tests/live_market_fixture_server.py
```

In another local shell:

```bash
GIG_MARKET_EVIDENCE=build/completion node terminal/tests/live-market-validation.mjs
python terminal/tests/measure_live_market.py
```

The source fixture binds only127.0.0.1:18797, uses authored protocol bytes and an injected
connector, and never contacts Alpaca. Native state still comes from the C++ binding.
Do not expose fixture ports. Full seven-suite browser reproduction uses the existing four
loopback fixture servers and `python terminal/tests/run_atlas_browser_suite.py`; it builds
once and verifies asset immutability before/after each journey. Do not rebuild assets
concurrently with browser tests. Build/log/screenshot artifacts stay under ignored build/.

Next external gates: valid provider permission/credentials, bounded observed source/browser
qualification, independently sourced listings/calendar coverage, physical-device/GPU and
accessibility acceptance, then owner-authorized exact-commit ARM64/hosted verification.
These are not established by synthetic data or by past ARM64 runs on older commits.


## Acceptance repair:authored native diagnostics

Standard setup now invokes `bash scripts/setup_terminal_native.sh` to build the existing
ITCH and LOBSTER authored diagnostics at the terminal's configured native-build path.
The helper requires GCC,CMake and zlib>=1.3.1,keeps the existing strict minimum,and
never accesses private datasets or activates a source. The container requests
zlib1g-dev,but its exact image/package version has NOT been qualified here. A distro
package name is not evidence of the required version;setup must fail visibly if
CMake rejects the dependency. Do not weaken the minimum to clear the check.
Fresh local source/venv/npm/wheel tests are not a new ARM64 or actual Codespaces run.
See INDEPENDENT_ENGINEERING_VERIFICATION.md and FINAL_ACCEPTANCE_MATRIX.json.
