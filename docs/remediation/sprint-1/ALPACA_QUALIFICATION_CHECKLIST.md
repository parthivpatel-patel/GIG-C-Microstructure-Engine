# Pending Alpaca qualification — preparation only

Owner update received October 31, 2026 (America/New_York): Alpaca Support confirmed
retail Basic permits personal, noncommercial research and provides real-time IEX
equity data. This is an **owner-supplied support summary**, not an independently
retrieved permission letter or a live-provider qualification result. The original
support response bytes and hash were not supplied here.

The following specific follow-up questions remain pending:

1. Processing within the owner's private GitHub Codespace.
2. Display through the owner's private, authenticated browser forwarding boundary.
3. Historical IEX API access and its applicable account/request limits.

**Current decision: keep all authorization gates disabled.** Basic personal-use
confirmation does not silently resolve those deployment and historical-access
questions. No provider request, key inspection, streaming activation, order,
subscription purchase or observed-data retention occurred in this sprint.

## Future acceptance prerequisites

- Record the affirmative scope of the follow-up response and its provenance. Do
  not fabricate a permission reference or treat an unrelated feed as equivalent.
- Obtain explicit authorization for the bounded qualification experiment after
  the unresolved scopes are clarified. This document does not authorize execution.
- Use the already-configured credentials; do not request replacement keys or repeat
  successful setup. Never place credentials or personal contact in evidence.
- Verify the actual effective free connection and symbol allowance, including any
  other application sharing the account. The terminal's internal cap is four
  simultaneous symbols, not a claim of an additional account-wide allowance.
- Keep the Codespace and port private. No paid feed, SIP/OPRA fallback, trading,
  paper order or persistent observed-data storage may be enabled as a side effect.

## Proposed bounded checks, only after those prerequisites

| Check | Proposed bound and evidence | Required outcome |
|---|---|---|
| Asset discovery | One approved catalog import within existing byte/row/time budgets | Actual accepted/excluded counts, hash, receipt time and source coverage; not a complete-US claim |
| Historical AAPL | One explicit date interval; existing cap of four pages, 256 bars and 2 MiB; no automatic expansion | IEX feed, source timestamps, adjustment policy, truncation and provenance; no storage permission inferred |
| IEX authentication | One shared upstream connection, initially one AAPL symbol | Real acknowledgement and timestamps; sanitized errors; no secret output |
| Subscription lifecycle | Add a second symbol only within confirmed limits; bounded in-place changes | Correct generation/accounting and explicit handover gap; no invented exchange sequence |
| Quiet/reconnect | Short declared observation window, at most two minutes unless separately approved | Quiet is not fabricated activity; bounded recovery; stale state never relabeled current |
| Private browser | Exact approved HTTPS/WSS origin through private forwarding | Authentication, request proof, mutation and stream/reconnect succeed; arbitrary forwarded headers grant no authority |
| Evidence | Safe counts, source identity, hashes, timestamps and tested Git SHA | No raw market rows, tokens, cookies, credentials, public display or unapproved retention |

Zero trades and zero paid resources are mandatory. A blocked or quiet result must
be reported honestly. These proposed checks were **NOT EXECUTED**. Current-candidate
ARM64, deployment-runtime security and final private acceptance remain separate
qualification gates; source configuration readiness is not proof they passed.
