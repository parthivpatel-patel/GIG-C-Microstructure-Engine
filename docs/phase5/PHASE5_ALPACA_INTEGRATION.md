# Alpaca status and owner acceptance

Historical REST adapter: **PARTIAL / OFFLINE TESTED / REAL SOURCE NOT VERIFIED**.
Actual live IEX wire client: **NOT IMPLEMENTED and BLOCKED** by outstanding cloud/display
review381230 and unavailable current authoritative protocol access. Existing REST quote/
trade/indicative profiles and server credential alias guards remain;no activation.
Free Basic account ownership does not resolve permitted cloud processing/display rights.
IEX is never SIP/NBBO/depth;indicative options are never OPRA.

One metadata-only official documentation probe:
curl -I --connect-timeout5 --max-time10 --retry0
https://docs.alpaca.markets/docs/real-time-stock-pricing-data
returned curl56,proxy CONNECT403. Origin documentation did not respond. No repeated probe,
TLS bypass,mirror or network configuration change. No market-data request was made.

Separate Quant Terminal:absent locally;metadata probe at the plausible owner path
parthivpatel-patel/GIG-Quant-Terminal returned Repository not found. This could mean name,
privacy or authorization mismatch,not proof the owner's project is absent. No connector
with authorized source-file access was available;no source/credentials copied or modified.
Owner may provide the correct approved source location later for read-only pattern reuse.

## Executable historical acceptance(after rights/configuration verified)

Keep all existing permission/protocol/private-display/cloud/no-cost gates and credential
selectors. Do not set approval flags merely to bypass rejection. Configure approved
owner-private storage/observed retention only when rights permit. Run one bounded attempt:

```bash
python scripts/qualify_alpaca_history.py --execute --symbol AAPL \
  --start YYYY-MM-DD --end YYYY-MM-DD --timeframe 1Day --max-pages 1
```

Use a permitted interval≤366 days;no concurrent source refreshes. Initial limit64 bars,
512KiB response,zero automatic retries. Success stores private normalized observations and
prints only counts,source hashes,revision and status. Do not commit raw data. Inspect the
revision in ATLAS;verify real response identity/timestamps/feed/coverage,has_more and errors.
Historical success does not qualify live WebSockets or consolidated observations.

## Live-IEX procedure: NOT EXECUTABLE YET

Before any live activation,obtain current official protocol/usage evidence and implement
the missing wire client/qualification runner. Required acceptance checks:

1. Authenticate server-side without credential echo.
2. Confirm IEX entitlement and refuse SIP/paid fallback.
3. Validate subscription acknowledgements and exact requested symbol set.
4. Receive actual observations,not merely a connected socket.
5. Validate source timestamps/receipt clocks and precision.
6. Verify IEX-only UI labels and no inferred Level2/3.
7. Exercise controlled disconnect/reconnect with new generation/state.
8. Verify stale data publication stops;heartbeats alone cannot refresh observations.
9. Verify private HTTPS/WSS browser/source provenance against the qualified runner.
10. Verify shutdown closes tasks/sockets and retains no unauthorized data.

Do not report fixture or historical REST success as passing these live checks. Existing
crypto supervisors/offline freshness monitor are useful patterns,not an Alpaca wire client.
