# Market model

APPROVED / MUST HAVE: one instrument/venue/session book, order-level FIFO,
integer ticks and lots with exact instrument metadata. No floating price keys.
Signed price storage permits instrument-specific ranges, including negative prices
only when explicitly supported. Zero/missing timestamps and sequence origins must
not be silently conflated. Checked arithmetic covers quantities, totals, products,
timestamps and counters. Rejected events leave state unchanged.

Adds, quantity/all cancels, replacements and identified executions have distinct
contracts. Print-only trades and quotes do not mutate order-level state. Book
resets and snapshots carry coverage and sequence boundaries. Unknown enums,
off-tick values, duplicate active IDs and ambiguous input are rejected in Phase 1+.
Phase 1 implements self-contained type/event checks; Phase 2 adds scoped active-ID
uniqueness, sequence continuity, FIFO and conservation checks. See PHASE_1_CONTRACTS.md,
PHASE_2_BOOK.md and PHASE_2_REPLAY.md. Every accepted event is a consistent boundary:
bid > ask is rejected, locked observations are allowed, and transient crossed bundles
are unsupported. Identified executions may name non-head orders without inferring
an aggressor; surviving FIFO order remains intact.

No auctions, hidden/iceberg/pro-rata/pegged priority, routing, venue certification,
self-trade-prevention model or live orders. A reconstructed book is not an
exchange-certified matching engine. The initial synthetic model uses positive
prices; this is not a universal market assertion.
