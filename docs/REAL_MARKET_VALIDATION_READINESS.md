# Real-market validation readiness — synthetic preparation only

October24,2026. **Synthetic preparation strengthened; observed-market integration
and correctness remain BLOCKED.** No dataset download, adapter implementation,
observed origin relabeling or market-date/initial-order fabrication in this phase.

## Source/spec audit

Official retained PDFs were rehashed offline: TotalView-ITCH5.0 (S1)
45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3;
BinaryFILE1.00 (S2) a1f443400728b3ce44953e9ae263e4846fe6ad68420e7a635829872aefdfff60.
Official URLs and dated-section catalog remain in ITCH_50_VALIDATION_DESIGN.md.
S1's retained revision includes2023 changes, not a separately authenticated2019
historical profile. K's typed Price4/prose conflict and later I/O semantics remain
explicit profile qualifications; do not infer complete2019 certification.

| Contract / official reference | Actual implementation / limitation |
|---|---|
|S2§§1.1–1.2: two-byte big-endian payload length, zero terminal marker, external session identity|src/itch/binary_file.cpp validates lengths/offsets/record and stream budgets, split reads and terminal policy; framing ordinals are derived, not exchange sequences.|
|S1 pp4–5 common fields and system events|src/itch/decoder.cpp preserves6-byte nanoseconds-since-midnight and exact locate/tracking. No trading date/timezone/sequence invented. Tracking numbers are not globally unique sequence keys.|
|S1 pp5–12 directory/status|Context maps daily stock locate/symbol, explicit session state. H/Y and later admin observations require matching opt-in profile; halt/system messages do not empty/reset native liquidity.|
|S1§1.3 pp12–14 A/F|Admissible global source reference enters bounded lifecycle state; exact Price4/share conversion; no synthetic aggressor or matching.|
|S1§§1.4.1–1.4.2 E/C pp14–15|Known displayed identity reduced, over-execution rejected. C's execution price/printability retained separately; book-only C integration is explicit opt-in, not a resting-price rewrite.|
|S1§§1.4.3–1.4.5 X/D/U pp15–16|Partial reduce/full retirement/new-reference replacement; exact quantity checks, retired identities, replacement priority preserved. Full cancel policy is explicit, no phantom unknown order.|
|S1 pp16–18 P/Q/B|Hidden print, cross and broken-trade observations retained separately. No displayed order invented; broken trades do not automatically restore liquidity.|
|S1 pp18–20 NOII/RPII/direct listing|Dated opt-in decoder observations, not auction matching or full historical compatibility. Unknown/unsupported input produces an explicit refusal.|

## Initial-state contracts and added checks

SyntheticReconstructor::create (src/itch/reconstruction.cpp:64 onward) already
requires authored_empty, complete_history, exact first frame boundary0/2/ordinal0,
consistent source/session/digest/seed and synthetic provenance. Unknown, complete
seed, incomplete history and observed origin cannot enter this factory. Current
complete native64-order recovery snapshots do not constitute a supported observed
context/native/FIFO seed. The factory validates caller assertions, not external
publisher authentication; the independent harness authenticates authored fixtures.

Expanded tests exercise **all255 non-authored encoded kind values** with fail-on-first
allocation, requiring metadata rejection before any allocation. Two more cases
shift both context and declared boundary identically (including UINT64_MAX ordinal):
matching arbitrary boundaries still cannot establish a valid start. Existing tests
cover missing history, wrong session/digest/seed, observed origin and unknown state.
No engine change was needed: the existing gate is correct for its declared scope.

Market open, system O, first file byte, top quotes and aggregate snapshots never
prove complete observed L3. A future observed adapter needs independently justified
empty-state boundary or complete order/FIFO/context seed plus session/capture
completeness; it must stop rather than mark missing-order state complete. Existing
scripts/check_observed_l3_readiness.py remains fail-closed even with every gate
claimed. This phase does not set its implementation capabilities true.

## Independent reconstruction extension

The existing Python flat-book/source-byte reference (check_itch_l3_reference.py)
is independent of production decoding/mutation. A new supplemental generator
check_itch_readiness_reference.py uses that independent model and byte packers,
never native results to generate expectations. It compares every accepted/rejected
prefix: order identity/side/price/quantity/priority, levels/best prices, ledgers,
context/receipts/native accounting and error class. Added67 sessions/476 prefixes,
three deliberately corrupted model controls; supplemental digest:
d0e09ee827dc2631bbc856fa2c64dc3ae0f63c383ec88e00d2b1e6a11ae6e66c.

Cases include two symbols/both sides,1/2/65535/UINT32_MAX quantities, execution,
partial cancellation, replacement and retirement, hidden/cross/broken observations,
full synthetic session, missing/duplicate references, invalid quantities/side,
strict timestamp regression, missing system/directory history, and all35 nonempty
truncations of an Add payload. BinaryFile fragmented/oversized/truncated/gzip/CRC,
resource exhaustion and interrupted/restart fixtures remain in the existing suite.

The supplement runs inside the existing itch.l3_reference case **after** the
unchanged qualified oracle/hash. It has its own digest, does not regenerate any
of the eight frozen identities, does not add/skip CTest cases, and bounds the
native child to120 seconds. Existing10032-session/65186-candidate reference and
its negative controls remain unchanged. See evidence/itch_validation_matrix.json
for executed matrix results and exact source references.

## Future ingestion/validation procedure (requires separate authorization)

1. Record written dataset private-use/storage/retention scope and official source;
   prior user-provided Nasdaq confirmation supports sample use, not redistribution.
   The3,524,013,057-byte archive is not downloaded here. Filename/date/range support
   does not establish decompressed size, whole integrity or valid initial L3.
2. Before acquisition, approve compressed/decompressed/disk/RAM/time/record limits
   and cleanup outside Git. Stream authenticated full artifact digests and gzip CRC/
   ISIZE/member completeness; a prefix cannot validate the unreceived suffix.
3. Preserve physical order, framing offsets and raw wire metadata; register exact
   dated profile and per-event disposition. Reject unknowns/gaps/contradictory state;
   never silently truncate a selected interval or invent earlier resting orders.
4. Establish session/initial-state evidence before applying observed book mutations.
   Unknown initial state may support decoder diagnostics, not certified L3 output.
5. Compare after each relevant source event to an independently implemented model
   and, separately, independently supplied observed book/queue reference. Expected
   snapshots must not initialize or repair the candidate during comparison.
6. Report total/accepted/rejected/unsupported/ambiguous records, comparison coverage,
   exact matches/mismatches/first minimal reproduction, input/reference/source hashes,
   restart boundaries, peak memory and scoped throughput; publish no raw data absent
   rights. Any incomplete source/state must block complete research publication.

Current synthetic default profile: two bounded books,128 live orders/1024 journal
records each,4096-source receipt limit in the profile. Factory hard source ceiling
100000 is not a memory guarantee:100000 ordinary12,232-byte records alone require
1,223,200,000 bytes before reserve coexistence, reset archive/context/references/
metadata. Replay from an authenticated start remains necessary; bounded intervals
cannot discard required earlier state. No journal redesign or full-day promise.

Exercise offline now via the existing synthetic gzip/streaming reference and
scripts/run_synthetic_l3_demo.py against gig_itch_l3_reference_driver, plus the new
readiness supplement. Those fixtures are explicitly synthetic, authenticated by
local expected bytes/digests, not marketed as observed exchange evidence.
