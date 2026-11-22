# Bounded Kraken joint recording/replay V1

Explicit profile `ORIGINAL_RAW_JOINT_SESSION_RECORDING_V1` uses schema
`gig.terminal.kraken_joint_log.v1`. It is separate from legacy L2 logs V1/V2;
legacy writer, receipt and replay defaults remain unchanged. The supervisor's
existing joint-profile setting selects the joint writer through the existing
recording control. Existing live/protocol/private-display/cloud-processing and
separate retention permission gates still apply. This code does not activate a
provider or claim genuine observed qualification.

The bounded contract is one fresh transport generation, depth10, fixed scales of
100,000,000, book session V1, no trade snapshot and coordinator request bases100/200.
The manifest retains exact generated subscriptions and capture identity. It admits
at most512 records,2 MiB raw metadata and8 MiB encoded native prefix cache, with
at most24 hours retention. Each canonical JSONL envelope retains the original raw
provider string, exact monotonic/wall-clock receipts and complete coordinated
normalization. Duplicate fields, inexact numeric metadata, invalid ordinals/clocks,
unknown manifest keys, incompatible source/configuration and truncated rows reject.
Canonical envelope serialization does not alter the raw string or authored update
array order. Manifest/source hashes establish internal byte consistency only.

Finalization fsyncs source bytes, then reconstructs every raw frame through a fresh
coordinator and real native aggregate owner before publishing a complete manifest.
Status, both acknowledgments and a valid snapshot must jointly establish final L2
eligibility. Missing receipts, altered normalized claims, CRC/status faults and
changed captures/generations reject. A source interruption aborts asynchronous
capture. The private recording namespace is owned and serialized by the gateway;
its inherited directory precheck/rename is not an atomic no-replace guarantee
against a hostile concurrent namespace actor. Existing targets are refused under
that ownership assumption. Post-publication directory-fsync failure reports
`recording_joint_publication_uncertain`; the valid artifact is preserved, and
Capture reports ERROR rather than falsely claiming confirmed durability. This is
syscall-level evidence, not physical power-loss or hardware durability qualification.

`open_recorded_session` dispatches the new schema into actual `NativeSession`
playback while the legacy `RecordedSession` refuses it. Source frames, receipts,
exact native metrics, research, flow and per-channel source hashes are independently
rederived into owned prefix caches. Seeking and fresh-process restoration preserve
source order; source trades do not refresh the book's receive wall clock. Expiry
or regressed wall clocks hide and clear cached financial data. The observed-source
processing grant is checked before payload reads. Historical observed origin remains
distinct from live; synthetic fixtures remain visibly synthetic. Complete market
initialization, exchange sequencing/backfill, complete tape/L3 history, independent
source authentication and full protocol qualification remain false/unavailable.

The explicit `save_joint_l2_fixture` diagnostic creates authored historical data;
existing record/load controls use the version-aware writer/reader. No application
or server is needed for offline reproduction:

```sh
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python -m unittest \
 terminal.test_kraken_joint_recording terminal.providers.test_supervisor_joint \
 terminal.test_l2_capture terminal.test_l2_recording terminal.test_l2_playback.Playback -v
```

Forty new tests exercise actual supervisor/capture/native consumers, all nine
native-to-TypeScript/ladder prefixes, fresh processes, strict metadata, tampering,
fencing, source clocks, budgets, symlinks, expiry and publication uncertainty.
A wider196-test cohort also covers prior provider and legacy recording contracts;
its socket/application-factory-guarded log is
`work/engineering-next/kraken-joint-recording-guarded.log`. Initial test setup errors
used nonexistent consumer method/control names and omitted NativeSession restart;
fixtures were corrected to the real production flow without weakening assertions.
MD07 remains PARTIAL.
