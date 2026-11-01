# Fake-only paper execution infrastructure

This implementation is an offline architecture and lifecycle demonstration, not an Alpaca integration qualification. No credential access, HTTP broker client, account authentication, real paper order, or live-money order exists in this package. Even all independent execution flags set to `1` cannot construct a network transport: `PaperEngine._transport` fails closed for anything except the injected `FakeBroker`. Existing market-data permissions cannot authorize execution. Pure request builders accept only the fixed HTTPS paper host and explicit paths; they do not make requests.

## Contracts and controls

`terminal/paper/contracts.py`: canonical six-field intents, uppercase supported symbol syntax, exact positive cent prices, integer shares, buy/sell, limit/day only. Python bounded integers and decimal-string conversion avoid binary64 rounding. Client IDs bind the fake profile, request identity and canonical intent. Repeated identical request identity returns its durable state without another create; conflicting content rejects.

Example defaults (not owner-approved broker risk limits): order $100, per-symbol exposure $500, gross exposure $1,000, loss from authored opening equity $50, at most 8 open orders, coherent snapshot age at most 5 seconds, limit distance at most 500 bps from an eligible authored mark. All positions must have marks; no shorting, arbitrary symbols, unknown account state, unverified session, uncertain intent, stale/reversed clock or snapshot revision is admitted. Buy reservations count against exposure and buying power; sell reservations cannot exceed held shares. Every new fill increment, not merely average fill price, must respect its limit. Revision means local fake consistency metadata, not an exchange sequence.

`store.py`: private owner-only directory/file, no symlink path, SQLite FULL synchronous transactions, explicit4KiB SQLite pages and16MiB database limit, at most 128 lifetime intents, 256 KiB canonical state, 2,048 chained audit entries. Audit reads have a 2,049-row detection bound. Hashes detect corruption; they are not signatures against an owner who rewrites the whole database. SQLite rollback sidecars can require another 16 MiB. Capacity exhaustion fails closed rather than deleting history. This small demonstration needs a separately designed archival policy before long-running broker use. It is separate from the native C++ journal, which is unchanged.

## Failure and restart boundaries

An intent/reservation commits before fake transmission. Acknowledgment loss preserves SUBMITTED/UNKNOWN and blocks new admission until reconciliation. There is no blind retry of an ambiguous create. Reconciliation checks immutable identity, monotonic fill quantity/notional, terminal state, marks, positions, orders and buying power; unknown external orders reject. Missing active remote orders remain UNKNOWN. A late successful create plus a failed local commit cannot be called atomic or exactly-once; the durable uncertain record is the safety boundary.

Kill closes new admission before cancellation attempts. CANCEL_REJECTED and UNKNOWN remain explicit outstanding states. Successful cancellation is never assumed after a timeout. Process interruption before SQLite commit rolls back. Restart opens the durable fake account and local intents, kills admission and requires fresh reconciliation and acknowledgment. Backup tests use SQLite's backup API, not a copy of a database during writes. Tests do not establish power-loss durability, distributed reconciliation or genuine broker RPO/RTO.

The fake broker has authored cash, marks, eligibility, opening equity, session, orders and explicitly authored fills. No automatic market fill is fabricated. AAPL $100, MSFT $200 and NVDA $150 are fixture constants, not current prices. Under the default $100 order cap, a whole-share MSFT/NVDA buy correctly rejects. The loss guard uses the fixed authored opening equity; it is not an exchange-calendar daily-account implementation.

## Integration and verification

GET `/api/v1/paper/status` is disabled with no account and creates no storage. POST `/api/v1/paper/control` uses the existing exact Origin/Host and endpoint-bound proof boundary, 4 KiB request cap, aggregate rate bound and one workspace action at a time. Default fake state is ignored `.gig-paper-demo/`; opening the explicit sandbox is the only operation that creates it. Provider observation retention is unaffected.

The Execution Simulator contains a separately labeled fake panel with explicit arming, limit-intent creation, one-share authored fills, cancel, reconcile and kill. Request identity is retained for safe retry; “New fake intent identity” denotes a new order. Native simulation remains unchanged. Account, positions, order lifecycle, example limits and chained receipts are inspectable. External execution is always shown disabled.

Strict cohort: `PYTHONPATH=. .venv/bin/python terminal/tests/run_sprint3.py` with the installed native package. 52 tests cover contracts, exact numeric references, security/proof boundaries, lifecycle and incremental fill prices, risk rejection/reservations, ambiguous create/cancel, cancellation, injected commit/allocation failures, actual child-process termination, backup/restart, corrupt files, unsupported SQLite page size, private permissions, and capacity. Run this only in a separate provider-disabled test environment, never against an operator's active collection server.

## External work intentionally blocked

A real Alpaca transport, independently verified coherent account snapshot, actual broker lifecycle/profile differences, owner-approved execution and risk limits, permission evidence, clock/session authority, account authentication, paper-submit/cancel qualification, external reconciliation, retention and operational recovery require separate authorization. They are not implemented or certified by the fake tests. No live execution host is allowed.
