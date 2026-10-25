# Private L2 recording and interactive replay

Current source checkpoint5b8b7e5. See RECORDED_L2_IMPLEMENTATION.md for the earlier
checkpoint and CONTINUOUS_ENGINEERING_REPORT.md for final evidence and remaining gates.

## Working authored path

In the private browser choose Historical Replay, Save authored L2 recording, select
that session, then Load L2 session. Step, Seek, Play/Pause, speed and Restart operate
native-validated recorded prefixes. Selecting another Replay source returns to the
existing authored L3 scenario. Authored recordings always remain HISTORICAL_SYNTHETIC.
No private dataset, actual exchange response or L3 identities are fabricated.

CLI demonstration: `.venv/bin/python scripts/replay_terminal_l2.py --position 2`.
This creates/removes a temporary authored log, invokes native replay and prints hashes.
No network or restricted archive is accessed. The older CLI's v1 logs remain supported.

## Observed capture: separately gated, not live-qualified here

Start permitted recording requires LIVE_VERIFIED production transport, reviewed
protocol/private-display/cloud-processing settings, GIG_LIVE_RECORDING_ENABLED=1 and
GIG_LIVE_RECORDING_RETENTION_APPROVED=1. These must reflect an actual applicable rights
review. No flags were enabled in this task. No genuine market frames were received.
Starting capture reconnects for a real fresh source snapshot; existing aggregate depth
is never fabricated into observed source messages. Stop drains the accepted queue.

Version2 logs include raw source frames, accepted native-event receipts, exact source
metadata, optional actual Unix receive time, monotonic receive order, venue, instrument,
profile, integrity hash and interval-end reason. File completion is not market-session
completeness. Unknown initialization/session declarations are rejected. Hashes detect
corruption, not malicious coordinated edits or authenticated exchange authorship.

Bounds:512 records,2MiB/log,eight sessions,four queued records,8MiB encoded prefix cache,
64KiB source JSON and64KiB normalized receipt. Python heap is not equal to encoded size;
actual measurements are in the evidence. One writer and one trusted local operator.
No arbitrary URL, input path, upload, credentials or permission attestation from browser.

## Durability, retention and failure behavior

A durable pending deadline precedes raw writes. Retention begins when the writer is
created, not after collection finishes. Accepted finalization fsyncs files/staged directory,
atomically renames on the same filesystem and fsyncs the parent. Pending state is not
selectable. A failed parent fsync can leave a complete but unacknowledged directory;
caller reports error instead of claiming durability. Physical power-loss testing and
hostile concurrent filesystem mutation are not qualified.

Queue overflow, source interruption, disk/allocation failure or invalid source aborts
unpublished capture. Record-budget completion explicitly ends a bounded interval without
claiming a full source/session. No crash-safe hot continuation or silent omitted events.

Configured retention is1..86400s through trusted writer configuration (the browser
capture uses the conservative default24h). Expired loads are refused; expired cached
frames are cleared. The running service sweeps expired owned logs every60s, excluding
an active writer. Interrupted pending logs retain their deadline; legacy pending state
without one has a24h fallback. Cleanup failures are diagnosed. No cleanup process can
run while the environment is stopped; filesystem backups, remanence and client copies
are outside application enforcement. Deletion is not a secure physical wipe promise.

A selected session is fully revalidated with real native C++ before publication and
compiled into an owned bounded prefix cache. Interactive playback is cache selection
of native results, not mock financial state. Observed sessions are HISTORICAL_OBSERVED,
never LIVE_VERIFIED, and remain blocked unless processing permission is configured.
Observed exports stay disabled pending a separate rights decision.
