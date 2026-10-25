# Bounded L2 source log and native replay tooling

The existing terminal recording API remains authored-L3 only. New terminal/l2_recording.py
is offline infrastructure, not an enabled observed capture service or browser recording
catalog. The live supervisor does not currently attach a recorder. Observed retention,
recording integration and interactive recorded-L2 selection remain explicit gaps.

L2Writer requires enabled=True. LIVE_OBSERVED additionally requires reviewed Permission,
private-display/cloud-processing attestations and recording_approved=True. This is an
operator assertion, not an inferred license. No observed file was opened or created by
this assignment. All recording tests use independently authored provider-shaped strings.

Bounds:512 records,2MiB/log,8 directories,64KiB source JSON per frame, retention1..86400s.
Source strings and receive-monotonic timestamp order are preserved exactly. Log ordinal
is physical capture order, never fabricated exchange sequence. Profile/symbol/scales,
source SHA256, byte/record counts and completeness are in a versioned manifest. Unix
creation time supports retention. Expired files are rejected on load; expiry is not
automatic disk deletion. Explicit operator cleanup is required. No unlimited retention.

Private staging uses mode0700 directories,0600 files, fsync and one final directory
rename. Append, disk-full, allocation or finalization failure aborts the unpublished
log. An interrupted .pending-l2 directory is incomplete and not replayable. There is
no crash-safe hot recovery promise or durable cross-filesystem transaction. One trusted
local writer is required; checks are not a defense against a hostile same-user process
racing symlinks. No browser filesystem path input exists. Hashes detect accidental
corruption; they are not source authentication or a signature against deliberate edits.

Loader rejects duplicate JSON keys, invalid manifest identity, symlinks, count/digest/
clock contradictions, truncated rows, invalid record order and expired/future dates.
Replay reconstructs a fresh native AggregateDepth and revalidates source CRC/semantics
at each requested prefix. Seeking is bounded O(records), not indexed recovery. The
first valid subscribed L2 snapshot remains necessary; no L3 initialization is claimed.
Observed log replay is HISTORICAL_OBSERVED, never LIVE_VERIFIED; authored log replay
remains HISTORICAL_SYNTHETIC. Log loading is an explicit trusted offline operation,
not arbitrary user-upload ingestion or permission verification.

Run the self-contained authored demonstration (no network or private dataset):

```bash
.venv/bin/python scripts/replay_terminal_l2.py --position 5
.venv/bin/python scripts/replay_terminal_l2.py --position 2
```

The first prints a final one-bid/one-ask native view; the second prints the earlier
updated bid quantity. Source hash and canonical result hash are deterministic. The
TemporaryDirectory is removed on exit. It never accesses LOBSTER or Nasdaq attachments.

Next integration gate: explicit verified retention basis, bounded capture writer
attached without blocking/loss ambiguity, failure/stop receipts, selected recording
catalog and browser play/pause/seek/speed tests. Do not claim those are complete.
