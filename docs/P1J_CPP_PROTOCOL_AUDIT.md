# P1J C++ protocol and memory review

Reviewed October 23, 2026 UTC at evidence checkpoint
`5584ce34de5b839d2a78fabcd8e6603cec1185f3`; implementation identity
`5ff7c8596f8705d92b7d97f55f860d0cb8d409fb`. This review inspected actual
`include/gig/itch`, `src/itch`, native book/replay mutation and the native
validation example, with P1J requirements, original institutional audit and its
preserved remediation addendum, P1I report, boundary review and evidence manifest
as context. No production source was edited. The review agent shares the workspace
with the integrating reviewer: this is a separate review/calculation pass, not
organizational independence, clean-machine restoration or exchange certification.

**No new confirmed critical/high or other candidate-scope correctness defect was
reproduced in this review.** This bounded result does not close unrelated release,
observed-source, advisory, hosted CI or production gates. Historical findings and
their original failing-before evidence remain authoritative for their dated source;
this report does not relabel all original recommendations as fixed.

## Actual accepted-state and hostile-input trace

| Inspected source ranges | Reviewed behavior and conclusion |
|---|---|
| `src/itch/decoder.cpp:5–109` | Exact supported lengths precede all field access; BE integer extraction is bounded by fixed field width. Offset/payload-end addition rejects overflow before diagnostics use offsets. Enum/text admission and the 2,000,000,000 wire-price cap are explicit. Recognized but unimplemented types return unsupported; unknown types return unknown. No implicit missing-message interpretation was found. |
| `src/itch/context.cpp:9–67,237–272`; `include/gig/itch/context.hpp:82–148` | Storage multiplication/addition is checked, capacities reserved and actual capacity bytes rechecked. Move-only prepared tokens carry object address, lifetime instance, accepted generation and consumed state. Public commit validates ownership/generation. Context move invalidates donor; pre-move tokens cannot commit to the destination address. Lifetime-instance exhaustion rejects rather than wraps. Private adapter-only commit writes reserved slots with nothrow element assertions. Caller PMR must outlive objects and returned PMR containers. |
| `src/itch/context.cpp:74–235` | Cursor/timestamp/lifecycle/provenance checks precede preparation. Directory and order identity, retired-reference retention, replacement-new-reference uniqueness and match retention are explicit. E/C reduce the identified resting order, including a non-head order; native removal need not be FIFO-head execution. Partial reductions retain arrival; U retires the old ID and assigns the new source arrival. C preserves source execution price/printability while projection uses resting price and requires explicit book-only opt-in. P/Q/B are retained observations; Q-origin B is unsupported. Missing/duplicate/broken identities stop without silently synthesizing state. |
| `src/itch/reconstruction.cpp:9–29,55–70,77–110,142–209` | Exact factor cancellation precedes multiplication; fractional, overflow and signed native price bounds reject. Factory requires explicit complete authored-empty synthetic evidence, matching source/session/provenance and exact selected unit quantum. At most two explicit bindings are admitted. Process owns pending bytes, checks exact retry identity, prepares context, checks binding/stock/C policy and validates token, checks reserved receipt space, projects, then calls one native apply. Only private reserved context/receipt/count assignments follow native success. Accepted-state rollback is distinct from diagnostic/capacity changes. |
| `src/book/order_book.cpp:21–114,147–234`; `src/replay/replay.cpp:109–143` | Ledger/remaining arithmetic occurs in local copies. Add/lose-priority replacement stage level/list/index nodes; real first-insert hash capacity is established before transfer/erase. List splice and equal-resource node transfer preserve FIFO, while U loses priority. Replay journal reservation precedes native mutation; accepted cursor/order/journal updates follow success. Standard allocation/container failures are caught. No new fallible allocation/callback after successful mutation was found in this path. |
| `src/itch/gzip.cpp:13–47,57–129`; `include/gig/itch/gzip.hpp:40–69` | Zlib callback allocation product/header size is checked and aligned; allocation exceptions are contained at the C ABI. PMR deallocation obeys the resource's normal nonthrowing contract. Heap-owned zlib state survives reader moves without changing opaque/header/output addresses. Reader outputs are borrowed spans until next feed/destruction. Header/input/output/expansion limits, deterministic byte admission, CRC/trailer verification and sticky errors are explicit; standalone reader is not advertised as concurrent/reentrant. |
| `src/itch/binary_file.cpp:9–64`; `src/itch/streaming.cpp:18–151` | Framing bounds payload, byte/record/ordinal counters, detects terminal/trailing bytes and distinguishes partial length/payload/absent terminator. Streaming owns decompressed read-ahead in stable gzip state, including across moves. A logical pause can precede a physically observed CRC error; deferred fatal error survives resume and blocks complete publication. Source completion requires actual declared EOF, member verification, terminal framing, exact raw/compressed identities, no pause and no error. Before finish, matched hashes alone do not imply completeness. Accepted-prefix hash includes exact framed committed records, excluding terminator and unread tail. |
| `src/itch/restart.cpp:17–109`; `src/itch/streaming.cpp:133–151` | Raw restart rebuilds an isolated fresh instance from byte zero and compares context, receipts and native descriptors; changed bytes/config/code reject. Streaming checkpoint compares the logical accepted boundary across chunk schedules. Trusted expected identities are caller inputs, not publisher authentication. No hot restore, gzip seeking or crash durability is inferred. |
| `examples/itch_validation_demo.cpp:17–101` | Authored fixed synthetic rows, explicit resource/profile limits, retained native/context identities and distinct source/session/integrity flags are exported. Caller implementation digest is constrained to lowercase hex before direct JSON insertion; other inserted identity values are fixture constants. Output is assembled/capped before stdout and sink failure returns nonzero. It remains the downstream consumer's responsibility to check exit/parse/schema/semantics; stdout is not durable atomic publication. |

## New executed independent numerical probe

This review authored a new minimal C++ stdin driver calling only public
`price4_to_ticks` / `shares_to_lots`, and a Python `fractions.Fraction` oracle.
Expected results use arbitrary-precision rational arithmetic and native destination
domain limits, rather than reproducing production gcd cancellation. It did not
rerun an existing reference model or replace a golden digest.

Command, from repository root:

```sh
g++ -std=c++20 -O2 -Iinclude build/p1j/evidence/cpp-review/probe.cpp build/p1i/clean-native/libgig_itch_reconstruction.a build/p1i/clean-native/libgig_itch_context.a build/p1i/clean-native/libgig_itch.a build/p1i/clean-native/libgig_microstructure.a -o build/p1j/evidence/cpp-review/probe
python3 build/p1j/evidence/cpp-review/check.py
```

**24,000 cases passed: 2,475 exact admissible results and 21,525 rejections; zero
mismatches.** Seed `20261023`. Cases cover zero/invalid scales, nonreduced scales,
off-unit fractions, full-width 64-bit share/scaling products, zero, UINT32_MAX wire
values, INT64_MAX/UINT64_MAX boundaries, and exact cancellations. The standalone
conversion factory accepts typed Price4 beyond the wire decoder's narrower exchange
cap; these probe values test conversion arithmetic, not decoder admission.

Retained local artifacts under `build/p1j/evidence/cpp-review/`:

| Artifact | SHA256 |
|---|---|
| `probe.cpp` | `99abcf944d19d8b3581feaa06b2e3414e07432dc0cdf7772d9e6ad5e2592c3c8` |
| `check.py` | `2fdcfee50633d5c014ec8f7b0829aff24b82ee5bc98dd3d7c18ea0ed495e9c4d` |
| Executed `probe` | `9a9071c45b3ce9ad856c870e461d7b7f7492e4f942b3e2bdfd7378ab092083b2` |
| Linked `libgig_itch_reconstruction.a` | `eb2ba5ee62a1e7043b112dfc504e67bf78d4c59731c7b1c2e4bb5031f345847b` |
| Generated stdin corpus | `88b93bc2ab050328e0bdec1d34c7e20e96d068435f567b6fd9eac3d5b79b0373` |
| Driver stdout | `6bff74060c0fe2db84a45e9f4111d46e5ba296068c11e648e85aa9d324b46dba` |

`result.json` retains counts/seed/corpus/output identities. The initial probe draft
failed compilation because a conditional expression mixed distinct price/quantity
Result types; the driver was corrected before execution. This was a probe-author
mistake, not a production failure. No failing-before production counterexample was
found or repaired. These ignored local artifacts require retention/restoration by
the integrating evidence manifest; paths alone do not promise durability.

## Material limitations and acceptance dependencies

These are explicit missing/excluded capabilities, not newly discovered defects.

| Item / priority / status | Current behavior, source and consequence | Improvement / acceptance / effort / dependencies |
|---|---|---|
| CPP-L1 / P1 evidence / retained limit | `include/gig/itch/context.hpp:20–35`, `include/gig/itch/reconstruction.hpp:24–40`; lifetime orders, matches, receipts and large native journal entries retain bounded history. Default PMR is not a governor; native/canonical/query objects can coexist. A selected cap is not proof that all maxima fit simultaneously. | Retain actual selected governor/PMR/RSS/query/restart coexistence measurements in final RC evidence. Small evidence-integration effort; depends on frozen final profile and matrix, not storage optimization. |
| CPP-L2 / P0 observed / missing | `src/itch/reconstruction.cpp:77–110`; only caller-declared complete authored-empty synthetic initialization is accepted. File EOF, lifecycle completeness and initial-state proof are separate facts. Historical full-context/FIFO seed and observed reference evidence are absent. | Keep observed qualification blocked; future actual source inventory, initial/full history and independently aligned reference are required. Separate substantial authorized work/data rights; no candidate code repair requested. |
| CPP-L3 / P2 production / excluded | `src/itch/restart.cpp:17–109`, `src/itch/streaming.cpp:133–151`; deterministic isolated replay/checkpoint comparison, caller-owned PMR lifetimes and single-threaded ownership do not provide durable crash restore, authenticated descriptors or stable native ABI. | Preserve exclusions. Future requirements, failure model, platform/ABI and operational authorization precede implementation. Substantial separate project; not a synthetic RC blocker when accurately scoped. |
| CPP-L4 / P1 validation / integrating gate | Existing P1I nine-configuration manifest and query/fault evidence describe named implementation source; this review's new probe exercises one local GCC/O2 binary. It does not independently requalify every sanitizer/compiler combination. | Integrator retains/rechecks exact source/evidence identities and final supported matrix. Routine evidence work dependent on final unchanged core source; do not describe this probe as a sanitizer sweep. |

No network access, market-data acquisition, dependency upgrade, commit, release,
main change or production repair was performed by this review.
