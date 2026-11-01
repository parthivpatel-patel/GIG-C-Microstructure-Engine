# Paper execution: simulator,authored sandbox and disabled provider adapter

Actual Alpaca paper account access and order routing are **not enabled**. A separate fixed-paper-host transport and adapter are implemented and fixture-tested in Sprint4;they were never used against Alpaca. Market-data permission is independent of execution permission. All live-money hosts are rejected by the pure request-construction policy. Default execution and provider gates are off. Configuration is not qualification;future explicit provider/account/risk/session qualification is still required. Do not enable gates under this guide.

## Try the offline infrastructure

Open **Execution Simulator**. Native schedules/fills/TCA are unchanged. Below them, **Paper execution sandbox** is separately labeled AUTHORED FAKE BROKER.

1. **Open authored fake sandbox**. This creates a private ignored `.gig-paper-demo/` SQLite store, not provider data. Fake equity, buying power, marks and positions are visible as authored constants.
2. Read **Example risk limits and audit receipt**. Check the authored-example acknowledgment, then **Arm fake admission only**.
3. Default AAPL buy: one whole share, limit $100, day. **Submit fake intent** commits the reservation before fake transmission. Retrying that same identity never creates another order.
4. **Author one-share fill** deliberately adds a fake event. There are no market-driven fills. Exact filled quantity/notional and held position are reconciled.
5. **New fake intent identity** is needed for a genuinely new order. Selling requires held, unreserved shares. Under the example $100 cap, MSFT/NVDA at their higher authored marks correctly reject.
6. **Cancel fake**, **Reconcile fake account**, **Kill new fake orders**, or **Kill and cancel fake orders**. A timeout/rejected cancellation does not mean outstanding orders disappeared.

On service restart, reopen the sandbox. Durable fake orders/account are retained, admission is killed and must be freshly acknowledged. No database is silently deleted or reset. Lifetime capacity is128 intents and2,048 audit entries; exhaustion rejects further mutation rather than discarding history. SQLite backup/restore and corruption tests are engineering evidence, not broker hot recovery or power-loss certification. Preserve a private backup using SQLite's backup API if needed; never copy a database mid-transaction or publish it.

## Risk and uncertainty

Only positive exact-cent limit/day integer-share buy/sell intents are supported. Checks include example notional, eligible instrument, reference-price distance, buying power, reserved positions, gross/per-position/open-order limits, stale/unknown snapshot/session, unknown order state and a loss guard relative to authored opening equity. Example limits are not owner-approved brokerage limits.

An ambiguous create remains UNKNOWN/SUBMITTED and blocks admission until reconciled; it is never blindly resent. Kill prevents new admission before attempting cancellations. UNKNOWN and CANCEL_REJECTED are explicit outstanding states. No exactly-once network guarantee is claimed. Hash chains detect accidental modification, not a malicious complete owner rewrite.

Real account authentication, provider/cloud/order permissions, genuine coherent account/position/open-order/balance snapshots, owner-approved risk limits, retention policy, real-transport qualification and separately approved paper submit/cancel/recovery tests are prerequisites to future paper use. No live-money operation is in scope. See `docs/sprints/sprint-3/PAPER_SANDBOX_CONTRACT.md` for source-level contracts and tests.

## Sprint 4 provider adapter: implemented,not activated

The separately labeled provider panel reads only safe readiness information on startup. It does not access account data,credentials or a network connection. The backend owns policy;checking a browser acknowledgment cannot grant permission. Live-money hosts,market orders,extended hours,fractional shares and subcent fills are outside the accepted profile.

Future qualification requires independent `GIG_PAPER_EXECUTION_ENABLED`,owner/risk review and permission reference;all eight provider/cloud/private-display/protocol/audit-retention/exclusive-account/reconciliation/no-cost policy flags;an exact account UUID;an expiring session of at most15minutes;and eight explicit owner risk values bound by SHA256. Do not copy authored example limits into a real session. `terminal/paper/provider_workspace.py` defines the exact names;this guide deliberately provides no enablement recipe.

A future session opens killed,reconciles,then allows separately acknowledged risk admission. Only fresh already-authorized IEX best quotes are accepted as references. Both source and receipt ages must be within5seconds;future timestamps,source-timestamp contradictions,wrong feed,zero-sided or crossed quotes fail closed. Unsynchronized clocks can block admission;they are not evidence of measured exchange latency. Buying power,positions,order reservations,gross exposure,concentration,daily loss,session,price distance and unknown-state checks fail closed. Same request identity means one durable intent,not a second order. Create timeouts remain unknown;there is no blind create retry. A cancel204 is not terminal cancellation proof.

Fill notional is summed from exact individual FILL activities,not a rounded average fill price. Duplicate activities are idempotent;contradictory ones reject. Unexplained cash/fees/positions,unknown external orders,incomplete activity pages or unsupported broker states block admission. The narrow reviewed exclusive-account policy is necessary:two equal REST collections are **not exchange-atomic** and cannot rule out an unseen concurrent actor. Real coherence/recovery remains unverified.

Provider state uses a separate private ignored `.gig-paper-provider/` store,account/session-bound;the authored sandbox remains `.gig-paper-demo/`. Limits include128intents,2048audit entries,512exactfill records,16MiBSQLite/256KiBserialized state,32held symbols and bounded account/activity pages. A newly opened process kills admission and reconciles durable state. Restarting into a different session/account does not silently rebind the old journal. Capacity failure preserves history and blocks operation;it does not prune accounting evidence. This is not a full-session broker accounting or crash-proof guarantee.

Offline protocol fixtures test delayed/lost acknowledgments,partial fills,cancel races,rate limits,expiry,restarts and durable rollback. They are not real Alpaca account observations,permission evidence or genuine order qualification. No real account/order operation occurred in Sprint4.
