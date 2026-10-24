# Level3 initialization and completeness contract

InitialClaim preserves what the caller says; eligibility is independently restricted
by implemented capabilities. Neither a JSON claim nor a digest authenticates history.

| Input/evidence category | Implemented route | Native/full-L3 status |
|---|---|---|
|Verified session-start evidence from observed capture|Context-only inspection; evidence identity retained|BLOCKED until observed evidence verifier and factory/seed capability exist|
|Validated complete observed snapshot|Context-only inspection|BLOCKED: current native64-order snapshot is not a complete observed context/FIFO/match/retired seed|
|Unknown mid-session start|Context-only; default lifecycle/missing-reference rejection explicit|Never labelled full L3|
|Incomplete/corrupt capture|Explicit interruption/error, accepted prefix only|No complete publication|
|Authenticated authored synthetic empty boundary|Existing SyntheticReconstructor with matching SourceManifest/ContextPolicy/proof|May publish only after exact complete framed input, checksum, local session and no error/gaps|

The observed rows are architecture contracts plus explicit unsupported integration,
not claims that their external evidence has been supplied or verified. A session
O message, open timestamp, arbitrary file boundary, aggregate depth/top quote or
matching shifted offsets cannot establish complete observed resting orders/FIFO.
No phantom order identities, restored broken-trade liquidity or fabricated exchanges
are permitted. Unknown source order references stop; trading states do not reset.

Dataset contract fields: provider/dataset identity, acquisition reference, private-use
permission reference, redistribution restriction reference, instrument bindings (for
native synthetic projection), external session identity, optional session date,
capture byte boundaries, raw framed-artifact digest, initial-state evidence reference,
known gaps and explicit origin. Missing fields stay absent or cause config rejection;
permission references are not automatic legal/publisher attestations.

Observed inputs can establish framing/decoding/context observations only. Future
complete-L3 eligibility requires externally authenticated initial-state evidence,
qualified dated profile, gap-free source accounting and independent aligned observed
reference; declare exact supported scope and fail closed outside it. The current
observed readiness capability flags remain false. Do not change them merely because
new synthetic adapter tests pass.

Retain input manifest and all prefix errors/offsets. An interrupted adapter can be
restarted by replaying identical bytes from a verified boundary; no crash-safe hot
snapshot, filesystem durability or unknown-mid-session resume is claimed. Existing
typed observed/session-origin fields are never converted into synthetic origin.
