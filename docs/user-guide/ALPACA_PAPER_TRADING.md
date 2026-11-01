# Paper execution: fake sandbox only

Actual Alpaca paper account access and order routing are **not enabled**. There is no network broker transport in this sprint. Market-data permission is independent of execution permission. All live-money hosts are rejected by the pure request-construction policy. Trading remains off even if someone sets all execution flags; real transport/account/risk qualification is still missing.

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

Real account authentication, provider/cloud/order permissions, genuine coherent account/position/open-order/balance snapshots, owner-approved risk limits, retention policy, real transport and approved paper submit/cancel/recovery tests are prerequisites to future paper use. No live-money operation is in scope. See `docs/sprints/sprint-3/PAPER_SANDBOX_CONTRACT.md` for source-level contracts and tests.
