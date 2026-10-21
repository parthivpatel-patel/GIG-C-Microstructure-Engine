# Market model

PROPOSED / MUST HAVE: one instrument/venue/session book, order-level FIFO,
integer ticks and lots with exact instrument metadata. No floating price keys.
Signed price storage permits instrument-specific ranges, including negative prices
only when explicitly supported. Zero/missing timestamps and sequence origins must
not be silently conflated. Checked arithmetic covers quantities, totals, products,
timestamps and counters. Rejected events leave state unchanged.

Adds, quantity/all cancels, replacements and identified executions have distinct
contracts. Print-only trades and quotes do not mutate order-level state. Book
resets and snapshots carry coverage and sequence boundaries. Unknown enums,
off-tick values, duplicate active IDs and ambiguous input are rejected in Phase 1+.
The bootstrap validator does NOT yet enforce all of these rules.

No auctions, hidden/iceberg/pro-rata/pegged priority, routing, venue certification,
self-trade-prevention model or live orders. A reconstructed book is not an
exchange-certified matching engine. The initial synthetic model uses positive
prices; this is not a universal market assertion.
