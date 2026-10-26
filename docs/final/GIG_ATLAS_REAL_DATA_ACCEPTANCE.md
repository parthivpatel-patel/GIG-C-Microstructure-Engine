# Real-data acceptance ledger

|Gate|Status|Evidence and required owner action|
|---|---|---|
|Official Alpaca protocol source access|COMPLETE bounded source retrieval|Pinned public official alpaca-py3da132c6407792310bfbaca1b3114863c44d5bda;file hashes in evidence|
|Alpaca cloud/private-display permission381230|BLOCKED|No permission assumed;obtain applicable confirmation and review account entitlements|
|Alpaca historical observed acceptance|NOT VERIFIED|Existing gated REST/paging/storage tests use authored data;owner run bounded history CLI after rights|
|IEX live protocol implementation|PARTIAL|Quote/trade profile and lifecycle tested offline;corrections/cancels/other message families stop explicitly|
|IEX live provider observations|BLOCKED|No configured credentials/provider permission here;no provider connection attempted|
|SEC identifying configuration|BLOCKED here|GIG_SEC_USER_AGENT absent;never printed;Codespaces secrets not inherited|
|Official SEC reconciliation|NOT VERIFIED|No official request made;owner command below|
|Observed-market model studies|NOT VERIFIED|Authored numerical fixtures are not calibration/predictive evidence|
|Observed L3 reconstruction|BLOCKED|No licensed complete initialization/order-level reference obtained;LOBSTER not accessed|
|Exact-candidate ARM64/hosted run|NOT VERIFIED|No workflow launched;previous qualification does not transfer to changed Python/UI code|

Owner-only SEC reconciliation,after approved identifying User-Agent and existing policy
gates are configured;fixed official endpoints,conservative pacing,one bounded fetch:

```bash
.venv/bin/python scripts/qualify_sec_sources.py --symbol AAPL --as-of 2026-10-26 --fetch --output build/sec-owner-reconciliation.json
```

Authorized historical pilot,after retention/permission gates are reviewed:

```bash
.venv/bin/python scripts/qualify_alpaca_history.py --execute --symbol AAPL --start 2024-01-02 --end 2024-01-03 --max-pages 1
```

Live owner pilot ONLY after existing5 Alpaca flags,permission reference,credentials,
protocol review and additional GIG_ALPACA_LIVE_ENABLED are legitimately configured:

```bash
.venv/bin/python scripts/qualify_alpaca_live.py --execute --symbol AAPL --seconds 30
```

This tool never sets gates. Output contains counts/hashes/status,no raw rows or secrets.
PASS means bounded accepted quote+trade observations only,not independent exchange accuracy,
reconnect/quiet-session qualification,global completeness or production readiness. Run
browser quote/print/freshness/stop/reconnect acceptance separately through private port8787.
Unknown provider messages must be preserved as explicit failures and researched,not skipped.

Hosted qualification prerequisite:the preserved manual native-arm64 workflow's job guard
currently accepts only feat/bootstrap-cpp20-engine. Review and authorize a narrowly scoped
final-branch guard before a new free-usage-verified owner dispatch. No workflow changed or
launched here;an old-branch run cannot qualify this candidate by implication.
