# Alpaca paper-trading readiness: NO-GO

Candidate `5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9`. No account connection,
paper/live order,cancellation,credential inspection or provider call occurred.
**Integration readiness FAIL;personal paper operational readiness FAIL.**

This is an absent future subsystem,not a secretly enabled dangerous order path.
The repository deliberately implements read-only market research. It is safe to
keep execution disabled;it is not correct to call that a functioning paper broker.

## What exists

- `stocks/auth.py`:server-only ALPACA/APCA credential aliases with conflicting/
  incomplete-pair rejection and presence-only diagnostics. Credentials do not grant
  market-data or execution authorization. No real value was inspected in this audit.
- `stocks/alpaca_transport.py:6–35`:fixed HTTPS GET destinations;paper-api host is
  allowed **only `/v2/assets`** with approved asset query. Market quotes/trades/bars
  use IEX data endpoints,indicative options separately gated. No account/order client.
- `stocks/service.py:101–117`:ENABLED,PROTOCOL_REVIEWED,PRIVATE_DISPLAY_APPROVED,
  CLOUD_PROCESSING_APPROVED,NO_COST_CONFIRMED plus bounded permission reference;
  additional live/options/retention gates apply. None changed here.
- `stocks/live.py`:shared market-data connection,lifecycle/subscription/MessagePack
  validation;this is not a brokerage order stream or account reconciliation.
- Native `simulation::Simulator`:synthetic FIFO/latencies,partial fills,rejections,
  cancellation and reports. Native exposure/inventory scheduling bounds constrain
  a supplied simulation;they are not broker risk limits or account buying power.
- Market “Stop shared stream” stops market data. It is **not a trading kill switch**.

## Required execution controls and actual state

| Required control | Current state | Evidence / required acceptance |
|---|---|---|
| Paper-only verified account |ABSENT|No account lookup/verification;paper hostname in asset catalog is insufficient. Future test must reject live/misconfigured/unverified account.|
| Paper/live execution separation |ABSENT execution|Readonly destinations reject order/account/position URLs. Do not broaden data allowlist indiscriminately to implement execution.|
| Explicit paper-order authorization |ABSENT|Market-data flags are not order permission;future independent default-off gate required.|
| Pretrade validation and order-size/exposure limits |ABSENT broker controls|Future bounded price/quantity/notional,positions/open-order reservations,buying power and instrument/session validation.|
| Maximum daily loss |ABSENT|Future authoritative baseline,realized/unrealized loss definition and fail-closed unknown positions.|
| Idempotent IDs/duplicate prevention |ABSENT broker intent ledger|Native IDs do not prove exactly-once broker execution. Future persist-before-send and reconcile ambiguous acknowledgments before retry.|
| Kill switch/cancel-all |ABSENT trading|Future explicit stop admission,approved cancel request,reconcile outstanding orders;network failure cannot magically confirm cancellation.|
| Order/position/status reconciliation |ABSENT|Future deterministic transitions including partial,rejected,cancel-rejected/late fills and external/account changes.|
| Disconnection/restart recovery |ABSENT order recovery|Market-history recovery is not pending-order recovery. Future durable bounded intents/audit trail,reconcile before resuming.|
| Execution audit trail |ABSENT|No order-intent/status lifecycle archive;source-data receipts serve a different purpose.|
| Actual order routing |ABSENT|No HTTP order endpoint or client;do not place an order to “check.”|

The18 inventory rows group these needs under one new **P1 paper-readiness gap**,
not18 separate regressions or a P0 enabled-trading incident. Their prior exclusion
is acknowledged. Any implementation requires a separately approved paper-only plan.

## Executed mocks/negative tests versus unavailable tests

Two current independent negative checks pass:

1. Both paper and live host `/v2/orders`,`/v2/account`,`/v2/positions` destinations
   reject through the read-only validator without a fetch.
2. Candidate API has no `/api/v1/orders`,`/api/v1/paper/orders` or
   `/api/v1/trading/orders` submission routes;requests reject403/404/405 and an
   injected upstream sentinel is never called. Workspace environment stays empty.

These prove a read-only boundary,**not successful mock execution**. Broker paper
execution mocks are **NOT_RUN / no implementation exists**. Do not invent a mock
broker,pass arbitrary orders through it and report the missing production path as
qualified. Native simulation tests pass and remain separately SIMULATED.

## Future staged plan,not executed

Approve requirements and paper-only design first. Reuse C++ where exact scheduling
or arithmetic is useful,not as a reason to bypass Python/API permission boundaries.
Keep broker I/O in a narrow server-owned default-off service;use bounded local
durable intent state distinct from research snapshots and the unchanged C++ replay
journal. Test fake-clock/idempotency/partial-fill/restart/risk/unknown-ack paths before
allowing provider operations. Freeze candidate/evidence and validate the account
read-only under separate authorization. Only a later explicit owner-approved
bounded paper-order experiment may submit or cancel orders. Never fall back to live
money,paid data or an unverified account. Stop and require reconciliation on unknown
state;rollback by disabling the execution gate,not by erasing intent/audit history.

Current Basic personal research/IEX availability confirmation does not resolve the
specific private cloud/display/historical questions or authorize any order experiment.
No new keys or repeated general setup are requested.
