# Continuous engineering: recorded native L2 checkpoint

Baseline54fa230; no native source or dependencies changed. Official provider/terms
access remains blocked under unchanged managed configuration. The new owner diagnostic
`scripts/diagnose_provider_access.py --provider kraken` makes exactly three bounded
HEAD requests to fixed official documentation/legal/feed hosts, reads no response body,
follows no redirects, opens no WebSocket and records no proxy credentials. Its unit
negative controls passed; it was not run again against known blocked destinations.
Owner Codespaces connectivity/rights are still unverified.

## Implemented

- Version2 private logs preserve exact raw provider frames, accepted normalized native
  L2 event receipts, source timestamps inside those receipts, monotonic receive time,
  optional actual Unix receive time, venue, instrument, profile, hashes and bounded
  interval end reason. Version1 remains readable. Missing metadata stays null.
- Files fsync, staged directory fsync, atomic same-filesystem directory rename and
  parent directory fsync precede successful finalization. Crash before rename leaves
  ignored pending state; after rename only complete hashed files are visible. A parent
  fsync failure can leave a valid but unacknowledged final directory: caller reports
  error, never confirmed durability. Hardware power-loss/filesystem guarantees remain
  assumptions; authored child-process interruption tests are not a physical crash test.
- One asynchronous recorder, four queued records, one thread-backed disk operation,
 512 records/2MiB/log/eight sessions. Overflow, malformed data, source interruption,
  write/finalization failure or allocation failure aborts unpublished capture. Stop
  drains accepted records and finalizes only with a source snapshot. A bounded log
  remains market_session_complete=false. Expiry rejects load; cleanup is explicit.
  No hard OS filesystem-hang deadline or adversarial shared-filesystem protection claimed.
- Protected recording API starts observed capture only with a verified production feed,
  existing protocol/cloud/private-display attestations and separate server settings
  GIG_LIVE_RECORDING_ENABLED=1 and GIG_LIVE_RECORDING_RETENTION_APPROVED=1. Those flags
  must reflect reviewed rights, never be set merely to bypass rejection. Capture restarts
  the source and requires an actual fresh provider snapshot, not an invented book seed.
  No observed connection or recording was started in this task.
- Private discovery, rejection diagnostics, deletion and selection accept only bounded
  recording identities, not paths/URLs/uploads/permissions. Observed processing remains
  separately gated. Captures are not redistributable by implication.
- Session loading replays every frame through the real C++ AggregateDepth and checks
  recorded normalization. It builds an immutable, owned native-validated prefix cache:
 512 source records, at most8MiB encoded cache. Python heap is structurally bounded,
  not guaranteed equal to encoded size. Native objects are created/destroyed in the
  compilation worker; only owned Python frames cross back to the event loop.
- Interactive Play/Pause/Step/Seek/Restart/speed uses that validated cache and source
  capture order. It is not fake book generation or crash-safe hot recovery. EOF stops
  on the last event without another timer tick. Complete L3/session claims are rejected.
- Browser controls save/select/load/delete authored L2 and operate recorded replay.
  Existing L3 authored replay, simulation and private Origin/Host/HTTP/WS proofs remain.

## Evidence and test repairs

The native-backed terminal cohort passed118/118 and its ASan/UBSan consumer passed
118/118 with LIVE_LSAN_CHECK=0 before the additional false-completeness negative control.
Final focused log/playback/capture tests cover that added rejection as well. Subsequent
consolidated evidence records the final expanded counts. Security46/46; authored recorded
browser8/8; async-polling negative controls3/3; TypeScript/Vite build passed.

New browser checks found the installed Playwright waitForFunction polling path treated
an async predicate's Promise as truthy, even when it later resolved false. `wait-state.mjs`
now explicitly awaits each HTTP state and predicate with a bounded deadline. Permanently
false async predicates must reject. Existing live-controls checks now use the same helper.
No product assertion was removed or changed to accept an incorrect state. Mutation
checks also wait for their exact successful POST response, not click completion.

Independent tests cover wrong normalized receipts despite recomputed hashes, corrupted
source/log counts, false initialization/session declarations, exact quantity prefixes,
owned cached views, prior timestamps, observed-load gates, paths/symlinks, queue overflow,
ENOSPC, MemoryError, finalization faults, subprocess exit before/after rename and deletion
of on-disk files without corrupting an already owned session. Full eight canonical
identities/native compiler evidence is unchanged from baseline; no new ARM64 run.
