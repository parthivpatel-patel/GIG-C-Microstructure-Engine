# Supervised joint Kraken profile

`GIG_LIVE_KRAKEN_SESSION_PROFILE=NATIVE_JOINT_SESSION_V1` explicitly selects
the existing raw-frame coordinator inside `FeedSupervisor`. An absent setting
preserves the legacy subscription, adapter and recording behavior. Unknown
profiles fail before a worker or transport is created. All existing explicit
live enablement and protocol/private-display/cloud-processing permission gates
remain mandatory. No connection is made by selecting the profile alone.

The supervisor creates one process-local capture token for each connection
attempt and sends exactly its coordinator-generated book/trade subscriptions.
Request IDs and capture labels change after reconnect. Supplied raw frames are
admitted in their transport order against that exact token. The coordinator's
actual native aggregate owner supplies the existing book, metrics, flow and
research consumers. Both subscription acknowledgments, online system status and
a valid book snapshot are required before financial publication. A snapshot
received before the trade acknowledgment may become eligible after that
acknowledgment; research stays unavailable until a jointly eligible book snapshot
arrives, rather than assigning a synthetic receive time to the earlier snapshot.

`feed.joint_session` carries bounded coordinator diagnostics without another
copy of the financial book. `provenance.joint_source_receipts` carries separate
last status, book, trade and subscription frame hashes, receipt hashes, capture,
generation and source origin. Trade and heartbeat arrivals do not refresh the
book's receive timestamp or freshness deadline. The source hashes bind supplied
bytes and do not establish independent source authentication.

Non-online status, invalid frames/checksums, changed provider connection identity,
staleness, transport completion/failure and operator disconnect fence financial
publication. Invalidation precedes awaiting socket close. Reconnection starts a
fresh native book and requires fresh status, acknowledgments and snapshot.
Injected offline transports retain `HISTORICAL_SYNTHETIC` origin; the existing
terminal LIVE consumer suppresses their financial book, metrics, flow and research.

Legacy L2 recording remains incompatible with joint receipts. The recording route
now selects the separate `ORIGINAL_RAW_JOINT_SESSION_RECORDING_V1` writer before
allocation and verifies its profile again after restarting the source. The existing
joint opt-in, protocol/processing and separate retention gates remain required.
The version-aware playback consumer rederives all raw frames/native prefixes; no
joint data is admitted by the legacy reader. The bounded format and publication
uncertainty policy are specified in
`docs/qualification/development-continuation/KRAKEN_JOINT_RECORDING_V1.md`.

This bounded integration uses depth 10 and preserves the provisional status,
top-ten checksum scope and no-sequence/no-backfill/no-complete-history claims.
It does not establish real-provider qualification. Offline reproduction:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python -m unittest \
  terminal.providers.test_supervisor_joint \
  terminal.providers.test_supervisor terminal.providers.test_coinbase_supervisor \
  terminal.providers.test_transport terminal.providers.test_kraken_coordinator \
  terminal.providers.test_kraken_public_session terminal.providers.test_kraken_book_session \
  terminal.providers.test_kraken_depth_session terminal.test_l2_capture terminal.test_l2_recording -v
```
