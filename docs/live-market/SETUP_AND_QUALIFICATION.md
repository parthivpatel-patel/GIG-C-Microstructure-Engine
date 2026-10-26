# Private Codespaces update and bounded qualification

Keep port8787 **Private**. In the existing Codespace,stop the old server with Ctrl+C:

```bash
git switch feat/atlas-final-release
git pull --ff-only origin feat/atlas-final-release
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

Open the existing private forwarded HTTPS URL. Choose **Stock Intelligence → Live Market**.
Select at most the configured symbol limit,then **Apply authorized subscriptions** only
after server-side licensing/protocol/cloud/private-display/no-cost permission review.
Do not enable flags merely to make a button active. Credentials stay in Codespaces secrets,
not browser storage,Git,CLI arguments or screenshots. Existing ALPACA/APCA alias handling,
SEC private configuration and same-origin proofs remain in place.

No provider request was made for this checkpoint. Runtime reported no configured secrets;
Alpaca support381230/entitlement clarification remains an external dependency. After the
owner independently resolves that permission and has configured existing server gates,
a bounded existing tool can be run in that authorized environment:

```bash
python scripts/qualify_alpaca_live.py --execute --symbol AAPL --seconds 30
```

This uses one stock,at most60 configured seconds,no retries beyond the adapter's existing
bounded reconnect policy,and no raw observation output/recording. Review the report's
status,phase,source hashes and limitations. A pass is only bounded source observations,
not independent exchange accuracy,NBBO,full tape or production readiness. Do not run this
command here or before permission is established. Next qualify dynamic four-stock
replacement,reconnect,freshness and browser behavior against actual authorized observations.

## Offline reproduction (no source access)

With the existing validated Python/native package and frontend dependencies installed:

```bash
python terminal/tests/run_live_market_suite.py
npm --prefix terminal/web test
npm --prefix terminal/web run build
python terminal/tests/live_market_fixture_server.py
```

In a second shell:

```bash
node terminal/tests/live-market-validation.mjs
python terminal/tests/measure_live_market.py
```

The fixture listens only on127.0.0.1:18797. Its connector supplies independently authored
protocol frames,never uses a real provider endpoint,and labels every accepted observation
HISTORICAL_SYNTHETIC/SIMULATED. Do not expose fixture ports externally. Screenshots/metrics
are written under ignored `build/live-market`;do not treat them as live-market evidence.
The native application state still comes from the installed C++ engine. Tests and local
HTTP/TLS simulation do not verify Codespaces authentication outside this container.

## Next priorities

1. Obtain and record actual Alpaca permission/usage evidence without disclosing credentials.
2. Run bounded owner-authorized single/multi-symbol source qualification.
3. Dedicated proof-secured browser stock push with bounded backpressure and slow-client tests.
4. In-place provider subscribe/unsubscribe acknowledgements and gap accounting.
5. Independent scissored 3D cameras and synchronized/independent modes.
6. Sustained physical-GPU resource/FPS measurement and leak qualification.
7. Current verified market calendar/halts authority.
8. Broader current listings directory under reviewed no-cost terms.
9. Reconciled trade-correction tape before corrected volume claims.
10. Profile normal non-traced processing before scalability targets.
