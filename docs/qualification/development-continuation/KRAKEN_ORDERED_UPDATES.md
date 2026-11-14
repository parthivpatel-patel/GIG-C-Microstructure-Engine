# Provisional ordered-update reconciliation

Documentation retrieved November 13, 2026 (America/New_York), through the
web documentation tool, with no feed/account/provider request:

- https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/book
- https://docs.kraken.com/exchange/guides/websockets/book-checksum-v2

The book description permits repeated updates to a price within one message in
wire order. The guide describes zero-quantity deletion, depth truncation and
checksum validation over the final top ten levels with exact decimal text.

`KrakenBookAdapter(..., ordered_updates=True)` admits sequential repeated-price
updates in this bounded offline profile. The candidate cache receives every update;
only its final accepted diff reaches native after checksum validation. Defaults
retain duplicate-level rejection. Snapshots still reject duplicate price levels.
An invalid final checksum publishes none of the intermediate changes. The strict
boolean option does not enable transport, permissions, display or storage.

Five regressions cover ordered overwrite, deletion/reinsertion order, legacy and
snapshot refusal, checksum rollback and configuration admission. Existing independent
CRC/differential checks rerun. This is partial official book-contract reconciliation,
not verification of all depth/options/trade/status/session/usage contracts. Current
supported depth remains ten. No exchange sequence, backfill/losslessness or official
live adapter qualification is inferred. Kraken remains provisional.
