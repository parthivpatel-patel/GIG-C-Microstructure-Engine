# P1H bounded synthetic streaming coverage

P1G baseline: `c3c3d8caef8f5b60aa4ce29f0f0875dc3bdd91c4`. This document maps the
P1H requirements to actual implementation and test assertions. It does not replace
the final frozen-source validation matrix or measured benchmark report. No NASDAQ or
LOBSTER data is part of these fixtures, and no observed-market validation is claimed.

The integration test is `tests/test_itch_streaming.cpp`; its seven groups are
`basic`, `fragments`, `corruption`, `semantics`, `budgets`, `allocation`, and `restart`.
The lower-level gzip tests in `tests/test_itch_gzip.cpp` independently exercise
`valid`, `errors`, `limits`, and `allocation`. The separately implemented Python
reference is `scripts/check_itch_streaming_reference.py`, driven through
`tests/itch_streaming_reference_driver.cpp`; it uses the independent P1G flat-book
model, bytewise wrapper observations and Python `hashlib` identities.

## Independent authored fixture and focused evidence

`tests/support/itch_gzip_fixture.hpp` writes gzip fixtures without calling a
compression library: an explicit gzip header, RFC1951 stored blocks, an independent
bitwise CRC32 and little-endian CRC/ISIZE trailer. Its literal source trace contains
18 records and507 BinaryFile bytes, including the terminal. Python `gzip.decompress`
independently confirmed the resulting530-byte member. Recorded Python `hashlib`
references are asserted by the native test:

| Artifact | SHA256 |
|---|---|
| Complete507-byte BinaryFile | `b0a3dfbda8636f10743ba71b082267aeaf52709a221e653e5d33d8d23feed2e5` |
| Complete530-byte stored-block gzip | `73d9117e5adc97c2b506e2c129c02a7953bf2f7c3431f59371010248c07d8e20` |
|505-byte accepted frame prefix, excluding terminal | `8f6c0f588e049f6fe1ff443e44935621c93adedafd0904390dcd979ff3435991` |

Expected book state is literal arithmetic, not another production run's canonical
output: native book0 ends with10315@101 and ledger added30/cancelled10/executed4/
replacement_in15/replacement_out16/total_in45/total_out30; book1 retains20120@200,
sell side. The complete trace has7 native mutations and11 external observations.
Every interrupted/faulted run compares its accepted record count against the literal
per-event identities, quantities, prices, FIFO tickets, context lifetime/match state,
native revisions, journals and source accounting.

Focused standalone GCC Werror development execution passed the seven integration
groups, with2,119 fragmentation/cut schedules and actual allocator failures at10
factory requests plus23 feed requests. This is focused development evidence, not the
final GCC/Clang/Python matrix. The additional corrupt-CRC/read-ahead checkpoint
regression must be included in the final source-frozen run. Do not derive a final
pass count from the number of table rows below.

## P1H acceptance matrix

| Requirement | Concrete tests and independent expectation | Scope and limitations |
|---|---|---|
|1. Valid gzip streams | `basic` checks known artifact hashes, CRC vector `123456789`, exact byte counts, both identity flags, terminal, unavailable EOF before finish and complete final accounting. Reader `valid` includes empty members and FEXTRA/FNAME/FCOMMENT/FHCRC. `semantics` includes more than65,535 raw bytes across multiple stored blocks. | One member only; actual source EOF must be declared. Container completeness is distinct from exchange-session completeness. |
|2. CRC corruption | `corruption` flips the CRC trailer; reader `errors` compares exact provisional output/error across input chunk schedules. `restart` tests a CRC error observed in physical read-ahead beyond a logical pause. | Previously accepted source events remain a provisional prefix; a bad CRC never yields complete/publication-eligible source. |
|3. Truncated gzip members | `fragments` declares true EOF at every interior compressed byte and requires an integrity error. Reader `errors` additionally checks exact `truncated` classification. | Deliberate bounded interruption is reported separately; no trailer integrity is inferred from a prefix. |
|4. Invalid headers | `corruption` changes magic, method, reserved flags and Deflate block type. Reader tests check optional-header FHCRC and exact header-byte caps. | No transparent plain/zlib/raw-Deflate fallback; optional metadata is bounded rather than retained without limit. |
|5. Concatenated members | `corruption` appends a second complete member and separately trailing garbage; both require gzip `trailing_data`. Reader tests verify the same policy at bytewise and whole-input chunk sizes. | Concatenated gzip is deliberately unsupported, not described as universally malformed gzip. Historical archive member structure remains unverified. |
|6. Expansion protection | `budgets` uses a frozen Python-generated4096-A-byte compressed fixture and requires `expansion_limit` before an enormous incomplete BinaryFile payload can be published. Reader limits independently compare maximum ratio arithmetic, slack and overflow boundaries. | Absolute compressed/decompressed bounds also apply. Expansion ratio alone is not a complete memory or decompression-bomb defense. |
|7. Fragmented input | `fragments`:530 chunk sizes,529 two-part splits and530 cuts under both EOF/bounded policies, totaling2,119 schedules. `basic` moves a paused pipeline with real owned decompressed output pending and resumes it correctly. | Borrowed gzip output is retained only while its owning reader remains stable; no caller input span becomes stored market state. |
|8. Invalid BinaryFile framing | `corruption` exercises missing terminal and data after terminal despite a valid gzip envelope. The Python reference includes incomplete lengths/payloads and invalid message lengths; preserved P1E/P1G framing suites remain required. | Complete gzip does not prove BinaryFile completeness. Partial frames are residual bytes, not accepted source records. |
|9. Unsupported ITCH messages | `semantics` inserts H and requires an explicit reconstruction/source-rejected outcome; the independent Python campaign supplies additional unsupported fixtures. | No silent source skip, inferred halt or implicit conversion to session reset. |
|10. Invalid order lifecycle | `semantics` sends D999 against absent state. It also tests crossed native insertion and default-disabled C; rejected events leave accepted context/native/receipt prefixes aligned. | Native crossing remains an explicit compatibility stop; no synthetic matching or missing history is introduced. |
|11. Multi-symbol interleaving | The literal trace interleaves TEST and TWO, checks every surviving ID/FIFO ticket and both journals; P/Q/B leave liquidity unchanged. `semantics` separately verifies explicit C book-only opt-in. | At most two configured books; no hidden-order book or auction allocation reconstruction. |
|12. Source interruption | Every interior-byte bounded cutoff is incomplete without inventing corrupt EOF. `restart` also finishes an explicit logical pause under an EOF request and requires bounded-prefix reporting with any physical read-ahead diagnostic retained. | Deliberate pause cannot certify unseen bytes or full-session integrity. Finishing seals the object; resuming a finished object is rejected. |
|13. Restart behavior | `restart` captures a logical accepted-frame checkpoint, rebuilds from compressed byte0 using a different chunk schedule, verifies it and resumes each instance from its own consumed compressed position. It rejects changed config/source/code/hash/native descriptor and changed actual source prefix. | Trusted in-memory integrity descriptor, not MAC/origin authentication, compressed seek, inflater-state persistence or crash-safe hot recovery. |
|14. Allocation failure | `allocation` injects every reached request:10 factory and23 feed requests in the literal workload; no leak, missing error or diverging accepted prefix is permitted. It also tests allocator-callback reentry into feed/checkpoint/finish and failed checkpoint export without uncommitting state. Reader allocation tests separately exercise C allocator callbacks. | C++ exceptions are contained by the zlib C callback boundary. Fault counts describe executed scenarios, not an assertion that every possible allocation path is exhausted. |
|15. Resource exhaustion | `budgets` tests exact and cap+1 compressed/decompressed bytes, optional-header limit, expansion ratio, frame count, reconstruction source count, native journal limit and tiny shared PMR. Preserved P1G tests cover active/lifetime/match/level caps and atomic native failures. | No journal redesign. Hard memory governance is provided by the caller's selected bounded resource; process RSS must be measured separately. |
|16. Deterministic output | Every fragment schedule checks the same literal state and canonical accepted-prefix digest; positive restart and negative-model controls compare semantic output. Separate Python checks generate expected source/context/native fields and byte-prefix hashes independently. | Final cross-compiler hashes and sanitizer outcomes require actual frozen-source execution. Timing values are not deterministic semantic outputs. |
|17. Complete source accounting | Prefix checks require physical complete frames=`considered + unconsidered cap+1`, disjoint considered=`context_committed + rejected + pending`, and native+external=`accepted`. Full source identity/CRC/terminator flags are checked independently. | Compressed/decompressed physical read-ahead is not a logical source position. Full-file totals remain unavailable for unacquired tails. |

## Logical pause and physical read-ahead

A pipeline may have decompressed farther than its accepted frame boundary. Its owned
pending output is bounded by the configured output buffer. A checkpoint intentionally
excludes physical read-ahead and partial framing; replay starts from byte0 and pauses
at the declared accepted-record count before comparing source/context/native evidence.
The new instance resumes from its own physical compressed position, not the original
instance's offset. This prevents duplication or loss when input chunk schedules differ.

The corrupt-CRC pause regression exercises both extremes: bytewise input has not yet
seen the bad trailer at pause4, while whole-input decompression can already know the
CRC is bad. Both can describe the same provisional logical prefix. The known physical
error remains exposed as `observed_gzip_error`; it is not cleared or treated as a
validated source. On resume, both process the same retained logical remainder and
terminate with CRC failure and no complete/publication-eligible result. Finishing
while intentionally paused reports bounded-prefix status, retaining that diagnostic.

## Completeness, identity and publication boundary

`StreamingSummary` separates gzip member verification, BinaryFile terminal observation,
actual compressed/decompressed hashes, expected identity comparisons, physical and
accepted positions, source completeness, publication eligibility and error state.
Actual EOF, a valid member/trailer, a valid terminal and both expected SHA256 matches
are required for complete source publication. A valid CRC or matching prefix hash
alone cannot establish any of those other facts. The raw source time-of-day and
exchange tracking values retain P1G meanings; no UTC/date/sequence is invented.

A complete authored artifact can end before the exchange-style S/O..S/C lifecycle is
complete. The source context's independent `session_incomplete` flag remains visible;
container publication eligibility is not a claim of a complete historical session or
observed-market L3 eligibility. Caller assertions about synthetic initialization remain
caller evidence checked by the declared fixture/oracle, not a NASDAQ initial-state proof.

## Final gate and memory evidence still required

The final report must attach actually executed GCC/Clang Debug/Release/ASan+UBSan,
Python regression and source-built/installed-wheel results; independent campaign
counts/digests; preserved P1E/P1F/P1G hashes; and actual memory/benchmark evidence.
Focused tests do not substitute for these gates. Measure reader buffers/zlib storage,
framer, context lifetime/retirement/match state, live native state, receipts, journal,
allocation counts and process RSS separately. Existing15,944-byte journal entries and
retained history remain a scaling limitation even though input decompression is bounded.

`GIG_BUILD_ITCH_STREAMING` is an optional separate target/dependency boundary. A build
with the feature OFF is not a streaming qualification. Existing Python interfaces and
ordinary wheel defaults do not gain a P1H API or a mandatory compression dependency.
See `P1H_COMPRESSION_DEPENDENCY_REVIEW.md` for the selected zlib installation, license,
API evidence and supported single-member policy. No real archive was acquired or
licensed for redistribution; actual NASDAQ pilot acquisition remains separately gated.
