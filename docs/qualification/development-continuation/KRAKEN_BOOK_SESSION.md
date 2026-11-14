# Opt-in bounded Kraken book-session negotiation

`KrakenBookAdapter(..., book_session_profile='BOOK_SESSION_V1',
book_request_id=100)` adds a local admission profile for the official book
subscription response. It does not change the legacy constructor defaults, the
existing ordered-update option, current supported depth ten, permissions or transport.
The adapter remains provisional and its profile_verified capability remains false.

Official source reviewed through documentation retrieval during this sprint:
https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/book
(response fields depth, snapshot, req_id, warnings, time_in and time_out).
The source documents separate acknowledgments per symbol and the echoed optional
client identifier. The local profile deliberately requires an explicit bounded
identifier and snapshot-enabled depth-ten negotiation. This is a narrower supported
contract, not a claim to implement every documented option or full protocol.

Call `connect()` to begin a local session, then `book_subscription_request()` to
construct its request without network or permission changes. A bounded u64 local
generation advances on every connect. The request id is the configured base plus
that generation; exhaustion rejects before replacing existing session state. The
first connect with base100 therefore constructs request101. The request builder is
pure; the caller remains responsible for any later independently authorized transport.
An acknowledgment must bind the active request, symbol, book channel, supported
depth and exact true snapshot option before any book snapshot can be admitted.
An acknowledgment alone never substitutes for a valid checksum-verified snapshot.

Warnings are preserved in the receipt, bounded to16 strings of256 printable
characters. Optional source time fields preserve exact nanoseconds and use the
existing bounded UTC timestamp grammar. Both fields may be absent; if both exist,
exit time cannot precede input time under this local admission policy. Unknown
book acknowledgment/result and book envelope fields reject explicitly. Trade
acknowledgment/status behavior remains the existing separate provisional profile.

Disconnect invalidates negotiation. Reconnect generates a new request identity;
an earlier acknowledgment cannot authorize the new session. A payload, checksum,
native-publication or receive-clock rejection invalidates the current negotiation
and requires explicit reconnect. Redundant valid acknowledgments and heartbeats
do not promote stale book data to LIVE or update its book freshness timestamp.
The previously accepted native book is not mutated merely by an acknowledgment,
a rejected candidate or session control event. Only a separately admitted snapshot
or final checksum-verified update commits native state.

Eleven new authored offline tests cover the pure request and exact receipts,
acknowledgment/snapshot separation, options/request types, bounded optional fields,
source and receive timing, reconnect generations/stale acknowledgments, stale-data
non-revival, checksum/native rollback, unsupported envelopes, strict configuration,
request exhaustion and legacy compatibility. Existing Kraken, ordered-update,
admin, recovery, differential and supervisor cohorts are also exercised.

This local request generation is not an exchange sequence, source capture identity,
lossless continuation/backfill proof or independent authentication of a response.
Full official depth/options, trade/status/session/usage reconciliation and actual
owner/provider/target qualification remain outstanding. No transport, provider,
application server, account, retention or trading action was invoked.
