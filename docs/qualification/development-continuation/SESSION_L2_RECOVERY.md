# Authored product-session and L2 worker recovery

No application,listener,provider/account call or trading action was performed. All inputs are authored fixtures. Kraken's provisional protocol status and permission/recording gates are unchanged;current official documentation remains unverified in this environment. No blocked-host probe was repeated.

## Product-native session

`NativeSession.checkpoint/restore_checkpoint` now connect the actual product's native replay owner to versioned checkpoint infrastructure. Restore bypasses the20-event default startup replay,imports native state directly,restores source position/speed,and resumes paused with fresh client/feed/simulation handles. The default constructor/startup behavior remains compatible. This explicit opt-in profile supports only the authored native dataset and rejects observed/provider-shaped/recorded sessions and LIVE/SIMULATION modes.

`terminal/session_recovery.py` binds fixture,implementation,binary identity,position,canonical native state and bounded migration lineage. Unknown schema versions and binary changes fail closed. Explicit migration re-admits the complete image with the new native reader/rules/configuration and verifies its unchanged canonical state before rebinding metadata. It does not prove equivalence of arbitrary historical code semantics;the owner must retain independently trusted input SHA/implementation identity and qualify any actual code-version change. No migration occurs at startup.

Private checkpoint revisions are immutable:exclusive atomic link publication follows complete write and file fsync;the parent directory is fsynced. New revisions never overwrite rollback input. Before-publication failure leaves no target;after-publication uncertainty requires reopen/verification. A real subprocess exit79 after publication leaves complete admissible bytes. An extra private temp hardlink after process exit is tolerated only through private-file ownership/permissions and independently expected content hash. This does not establish arbitrary hardware/power-loss durability.

Limits:8MiB payload,existing20,000-node/depth24 admission,native32MiB resource ceiling,current authored fixture boundary and4migration lineage records. Caller supplies private path and independently retained SHA;there is no new HTTP path/file-upload endpoint or automatic provider retention. This is native product-session support,not serialization of the new typed full ITCH context image,zlib state or every browser workspace.

## Provisional L2 reliability repairs

A deterministic concurrent-start regression reproduced2physical workers instead of1. Commands now serialize. Synchronous cancellation retains the retiring worker;new admission waits at most a bounded shutdown interval and remains fenced if that worker suppresses cancellation. Old generations cannot change new-owner failure state. Retry exhaustion now stops8consecutive failures;one valid snapshot does not erase repeated corruption. Backoff resets only after30seconds of stable valid depth delivery. Injected jitter must be finite and within its declared range;maximum base30seconds with20%jitter remains36seconds. No performance SLA is implied.

Another regression reproduced rejection of a valid finite JSON numeric quantity `1e-8`. Decimal tuple bounds now precede exact plain-decimal expansion;CRC and native lots retain full precision without context rounding or giant exponent allocation. String-field grammar remains strict. This repairs exact numeric ingestion in the candidate profile;it is not independent verification of Kraken's current official protocol or rights.

Existing L2 source views continue to publish aggregate levels and crypto provenance through the native product state,Order Book/Depth and compatible visualizations. Fixture transport remains HISTORICAL_SYNTHETIC;stale/disconnected/corrupt state publishes no trusted book. Nothing converts IEX L1 into depth or enables a new connection.

Focused run:71passing cases =62provider/worker/precision/differential cases +9real-native product-session cases. Includes a10,000-candidate independent aggregate/CRC oracle. Original worker/precision failures are retained in local evidence logs. Broader guarded regressions and compiler outcomes are recorded in the continuation evidence manifest. No actual Codespaces,live-provider,ARM64 or browser acceptance is claimed.
