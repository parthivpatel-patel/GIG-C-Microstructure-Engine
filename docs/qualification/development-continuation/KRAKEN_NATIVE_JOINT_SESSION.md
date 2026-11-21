# Opt-in joint Kraken session and native L2 eligibility

`terminal.providers.kraken_coordinator.KrakenSessionCoordinator` adds the explicit
`NATIVE_JOINT_SESSION_V1` profile. It composes the existing reviewed book negotiation
profiles and `TRADE_STATUS_SESSION_V1` with an **owned actual NativeAggregateDepth**.
There is no transport, source activation, permission change, order action, default
adapter replacement or provider qualification. Existing Kraken adapter defaults and
all native artifact formats remain unchanged. MD07 remains PARTIAL.

## Authority and local policy

The wire contracts remain those in [KRAKEN_BOOK_SESSION.md](KRAKEN_BOOK_SESSION.md),
[KRAKEN_DEPTH_SESSION.md](KRAKEN_DEPTH_SESSION.md) and
[KRAKEN_TRADE_STATUS_SESSION.md](KRAKEN_TRADE_STATUS_SESSION.md), with their official
Kraken source references. The new joint eligibility/fencing policy is a conservative
GIG contract, not an exchange guarantee or additional Kraken wire specification.

A caller explicitly creates the coordinator with `profile=NATIVE_JOINT_SESSION_V1`.
Only the existing BTC/USD or ETH/USD scales/origin choices and book V1 depth ten or
book V2 depth ten/25/100 are admitted. Both subscriptions must be acknowledged on the
current supplied connection; a requested trade snapshot must also arrive before the
native book is eligible. Book snapshots and executed-trade observations remain
separate. Trades never mutate the native L2 book or become L3 order evidence.

## Supplied connection binding

`connect(capture_label)` returns a frozen, process-local `KrakenSessionToken` and
advances both parser generations together. Every `feed` requires that exact token
object. Copied, fabricated, foreign-coordinator and old-generation tokens reject
and fence financial eligibility. Capture labels are bounded caller declarations,
not issuer authentication. Generations are local to one coordinator instance and
are never exchange sequences, globally unique capture identities or durable tokens.

The initial raw status frame binds the connection ID supplied by the caller's
transport. A changed ID requires reconnect. Book/trade acknowledgments bind distinct,
nonwrapping request IDs, exact symbol and selected options. Status, both parsers and
native receipts are associated with the same current capture and generation. An
arbitrary caller can still supply arbitrary raw bytes; this offline API cannot
independently attest which real socket produced a frame. The transport-to-token
association and actual observed qualification remain external evidence.

`subscription_requests(token)` returns owned book/trade request dictionaries only.
`trade_unsubscription_request(token)` records local unsubscribe intent and withdraws
joint book eligibility immediately. Its matching acknowledgment ends the joint
session and requires reconnect. Book unsubscribe is explicitly unsupported in this
profile. No request builder transmits anything.

## Raw admission and complete receipt coverage

The only frame entry point accepts a bounded original UTF-8 string; receipt objects,
parsed mappings and caller-supplied digest assertions are not accepted. The existing
strict decoder rejects duplicate keys and preserves numeric tokens as Decimal.
Public receipts must come from the raw-frame parser with `HASHED_RAW_FRAME` authority,
the same digest, generation and connection ID. A lower-level
`CALLER_SUPPLIED_DIGEST` receipt cannot bridge this admission boundary.

Each owned receipt includes the raw frame SHA-256/byte length, exact receive clock,
capture/generation/connection, selected profiles, separately owned source receipt,
actual native event (if any), native revision/checkpoint digest and the raw source
hash of the last native mutation. Public/status/heartbeat/duplicate frames retain
the last book mutation's source hash instead of claiming to replace it. A receipt
hash binds its exact contents; it is not a signature or independent authentication.

Book callbacks are staged and compared field-for-field with the parser's native
receipt before any native mutation is published. The coordinator restores a native
candidate from its **internally retained private aggregate image**, applies the
validated event through C++, captures the resulting image/revision and allocates the
outer receipt. Only then does it swap owned native/parser state. It does not accept
an imported native checkpoint or silently rebuild a revision from level arrays.

A bad CRC, late malformed/conflicting trade, stale token, native capacity/arena
failure or receipt-allocation failure cannot publish the candidate. The prior native
financial image remains private for rollback inspection; its view is unavailable
once fenced. Returned requests, receipts and native view dictionaries do not alias
owned source or native state. No native/core code or frozen identity changes are
required for this composition.

## Eligibility, staleness and unavailable states

Non-online engine status, changed connection, malformed/rejected frames, invalid
receive clocks and stale book freshness fence the entire joint session. Later online
status or a replayed acknowledgment cannot reinstate eligibility. Reconnect clears
the native owner and requires fresh status, acknowledgments and a book snapshot.

Freshness uses the native book frame's receive deadline. Trades, status, heartbeats
and duplicate frames never refresh it. `view(now_ns)` returns `book:null` with an
explicit reason for normal stale/unavailable states; invalid clock inputs reject.
It never exposes retained stale levels or metrics as an eligible current book.
Native view-allocation failure also fences eligibility.

Source-order detection is explicitly limited to the caller's supplied wire order,
monotonic receive clock, process-local generation and book receive deadline. Without
an authenticated sequenced source this cannot identify every delayed/replayed
internally valid frame from the same supplied connection. Trade IDs do not become
book sequence numbers. No exchange-wide gap detection, full history, backfill or
lossless recovery is claimed.

Subscribed depth is always disclosed separately from the **top-ten-per-side CRC**.
Depth-25/100 observations beyond those levels are not promoted into checksum-covered
continuity. All views/receipts disclose L2, distinct executed trades, source origin,
no independent source authentication and unqualified full protocol status.

## Bounds

Raw frames retain the 65,536-byte bound and the underlying parser limits. Capture
labels are at most 128 restricted characters. Source price/quantity scales and stale
deadlines retain existing bounds. Native capacity is explicitly one through 256
levels and each PMR arena one byte through 64 MiB; a too-small capacity/budget fails
closed. Atomic candidate preparation can temporarily own two native arenas (prior
and candidate), plus bounded parser state. There is no unbounded frame journal or
source-history accumulation. A native owner is dropped on disconnect/reconnect.

## Developer verification

`terminal/providers/test_kraken_coordinator.py` uses authored original frame strings
and the actual installed native binding. Its 32 focused tests cover:

- Same-capture negotiation, both acknowledgment/snapshot gates, exact hashes and
  callback/native receipt coverage, native revision preservation and owned views.
- Non-online/connection changes, stale/copied/foreign tokens, reconnect, clock and
  book freshness, explicit unsubscribe and absence of stale native eligibility.
- Real C++ capacity/one-byte-arena rejection, atomic 200 changes per side at depth
  100, ordered repeated-price updates and unchanged financial state on failures.
- Invalid CRC/late malformed members, exact large/fractional numeric tokens,
  raw-versus-caller digest rejection and receipt/view allocation failures.

The guarded combined provider/native cohort contains 141 tests and forbids socket
bind/connect and application creation. Focused and combined cohorts overlap.
Commands from repository root:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python -m unittest terminal.providers.test_kraken_coordinator -v
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python work/nov21-kraken-coordinator/run-regressions.py
```

Logs: `work/nov21-kraken-coordinator/focused.log` and `regressions.log`. Exact source
SHA and integrated evidence belong to the enclosing sprint report. Authored fixtures
are not real Kraken observations. Application/product transport wiring, actual
provider/usage qualification, remaining protocol coverage and external acceptance
remain separate milestones; none is inferred from these tests.
