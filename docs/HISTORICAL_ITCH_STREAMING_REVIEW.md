# Historical ITCH streaming and adversarial review

Scope: source-level and executable synthetic review during the administrative v3
extension. Independence means separate expected-value/reference algorithms and
negative controls; this is not a claim of an external human auditor, hosted runner
or independent-machine qualification. No additional market data was acquired.

## Reviewed boundaries and evidence

| Boundary /source | Mechanism checked | Reproduction or acceptance evidence | Remaining limitation |
|---|---|---|---|
| Decoder `src/itch/decoder.cpp` |Type→exact length before any field read; BE unsigned accumulation; no float; printable Alpha; finite enums; explicit profile |New oracle mutates every post-header byte of L/V/W/h/N through all256 octets, rejects all malformed lengths, independently checks10000 full-width V tuples; old-profile unsupported controls |Only selected retained-spec layouts; no newly observed historical fields |
| New profile `decoder.hpp`, `context.cpp` |v1/v2 values/variant indexes stable; v3 explicit, normalization3; owned typed fields |Prior six canonical identities retained; v3 independent oracle and malformed-profile tests |Rebuild C++ consumers; no stable ABI or Python administration API claimed |
| Context `context.cpp` |Prepare cannot mutate accepted vectors/cursor; global V/W locate0; mapped L/h/N stock; source/lifecycle/clock policy |Independent320-session16960-candidate model, per-rejection accepted-count/offset/directory checks, unknown/bad symbols/global locates; no order/match creation |No per-security regulatory/status-enforcement table, historical context assumptions explicit |
| Native integration `reconstruction.cpp` |Mutation set unchanged; new observations route or are global; receipt precedes no fallible post-native work |Two-book order/level/FIFO/revision/ledger/journal comparisons; global receipts have no fabricated book/sequence; 23-source streaming oracle accounting7native+16external |Synthetic initialization only, no observed factory/seed/metadata adapter |
| Gzip `gzip.cpp` |One-byte deterministic inflate policy, at most64KiB output buffer, checked compressed/header/output/ratio caps; callback allocation containment |Existing every-cut truncation, corrupt CRC/header, concatenated/trailing, expansion and allocation regressions rerun; new stream reaches33 injected sites |Conservative microstep performance; no archive seeking/concatenation support or current security-advisory clearance |
| BinaryFile `binary_file.cpp` |Two-byte BE framing, bounded owned buffer, record/byte/offset/ordinal bounds; residual vs complete-prefix distinction |Existing fragmentation/oversize/overflow/terminal tests plus new one-byte/four-size stream fragmentation; all accepted-record counts checked |A physical ordinal proves local adjacency, not exchange capture losslessness |
| Streaming `streaming.cpp` |Deferred physical gzip error retained across logical pause; accepted hash after joint commit; explicit incomplete EOF; full hashes/CRC/terminal gate |Existing deferred-CRC controls, source interruptions, unknown/bad events, budget exhaustion and deterministic restart rerun; new v3 profile-mismatch restart and incomplete-prefix rejection |Publication_eligible is synthetic source integrity, not authenticated exchange session; context.session_incomplete is separate |
| Recovery `restart.cpp`, native replay |Replay from authenticated start, source/config/code identities and exact logical checkpoint; pending/error states block checkpoint |Old deterministic L3/streaming oracles preserved; new profile identity negative and changed-fragmentation restart |Not crash-safe hot recovery or full ITCH-context restoration from native snapshot |
| Retained storage `replay.cpp`, context/receipts |Explicit capacity/PMR checks, no retired-reference eviction; journaling unchanged |Native source/journal limits and fault-injection gates rerun; measured profile and sizeof in engineering evidence |100000 journal cap can imply1.59GB element storage per book on measured ABI; no optimization |
| Packaging `pyproject.toml`, inventory checker |Pinned backend, root-anchored required files, no recursive force-includes, ignore rules intact |Three leak/cache negative-control unit cases, complete safe byte-identical sdist inventory, fresh direct/source wheel consumers |Local artifact snapshots, not public release or separate-machine reproduction |
| Evidence and CI |Actual per-row JUnit/log hashes; required counts and seven canonical identities; no hidden skips |Local CI summary native/Python positives plus deliberately wrong administrative hash negative controls |Hosted execution/status and security-provider/independent-machine gates remain unverified |

## Suspected issues and dispositions

1. **Potential full-session inference from synthetic publication flag:** reviewed
   `StreamingReconstructor::finish`, `SourceContext::finish` and their documented
   contracts. Physical source completion and `session_incomplete` are separate
   existing facts. No contradiction of the current synthetic source-integrity
   contract was reproduced. Explicitly block observed-session/L3 inference in
   OBSERVED_L3_READINESS_CONTRACT.md; do not broaden current factory semantics.
2. **Potential global-message misrouting:** V/W would fail the old non-S binding
   lookup if naively added only to the decoder. New v3 context enforces locate0;
   integration treats only validated V/W as global observations. Direct tests and
   streaming fixtures require accepted external receipts with no native sequence
   or book index. Old profiles reject them before routing, preserving behavior.
   This was an anticipated new-feature boundary, not an old supported-event defect.
3. **Potential precision/overflow narrowing:** a Price4 helper would reject/truncate
   64-bit Price(8). Use distinct Price8 uint64 raw fields, no native conversion,
   full uint64 boundaries and independent Python struct integers. No invented
   maximum/order relationship, quantization or floating-point calculation.
4. **Potential packaging contamination:** previous unanchored/recursive include
   fixes remain intact. New source archive is fully inventoried; deliberate
   ignored-build and root-cache controls remain effective. No leakage reproduced.

No new production streaming defect was reproduced; therefore no speculative
streaming/journal refactor or unrelated repair was made. This does not prove the
absence of all bugs or qualify observed-market reconstruction.

## Preliminary failures retained, not counted as final passes

- First build rejected an implicit signed-char conversion in the new test-only
  re-encoder under Werror. Added an explicit unsigned conversion; no flags changed.
- First focused run passed7/8 but its allocation test queried canonical state while
  the injected allocator was still armed. The source observations had allocated
  zero times; the subsequent canonical query legitimately needed allocation.
  Assert observation allocation count first, disable injection, then compare full
  book state. Failure log retained; final focused run8/8 and final matrix reported
  separately. No engine allocation error was suppressed or reclassified as success.

Final counts, compiler identities, artifact hashes, memory measurements and exact
source manifests are in HISTORICAL_ITCH_ENGINEERING_REPORT.md and its evidence.
