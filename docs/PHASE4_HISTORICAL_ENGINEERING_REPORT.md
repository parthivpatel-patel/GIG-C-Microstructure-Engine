# Phase 4 historical engineering closure

## Assessment and checkpoints

Completed the authorized bounded inspection, offline retained-specification expansion, failure-boundary qualification, packaging checks, measurement, and private-candidate readiness review. The bounded synthetic candidate passes its executed checks. Observed L3 validation and formal release closure remain blocked; this is not production or exchange certification.

Starting commit: `ef6970626f53354827864e937f3403ce281035df`.
Acquisition checkpoint: `70b61658953551bc275e46140803d1a568a98ae3`.
Validated implementation: `b549b5aa5cc157f636430800b9a16c5ec2159a39`.
Branch: `feat/bootstrap-cpp20-engine`. Main remains `165c5038336887116d69160b0d8e5a1a5ef59d16`.
The final documentation commit is reported after pushing, rather than self-referencing an unknowable commit hash here.

The structured companion [evidence](PHASE4_HISTORICAL_ENGINEERING_EVIDENCE.json) records commands, counts, canonical identities, code hashes, package hashes, measurements, and local evidence-file hashes. Local raw logs and artifacts remain under `build/phase4-historical/evidence`; they are not committed binaries or distributable market data.

## Single authorized acquisition

Exactly one GET was made, after 37 local safety controls passed. No retries, range expansion, redirects, subsequent NASDAQ request, or LOBSTER request occurred.

| Observation | Actual result |
|---|---|
| Official artifact | `12302019.NASDAQ_ITCH50.gz` |
| HTTP / Content-Range | 206 / `bytes 0-16383/3524013057` |
| Compressed bytes | 16,384 |
| Compressed SHA256 | `5a436e3cc4fe35007cf56695d52d1500aa9427b540ff24e1c6c1a3482e5e7cae` |
| First 4 KiB SHA256 | `133d94175e46e156baf6c7284f1fdad7e00f0fd4700bd09ed87a5afc98a700c2` |
| Decompressed bytes | 58,606 |
| Complete frames / residual bytes | 1,433 / 12 |
| Message counts | S 1; R 1,424; H 4; Y 4 |
| Default v1 | 1,425 decoded; 8 explicitly unsupported; 0 rejected |
| H/Y v2 and administrative v3 | 1,433 decoded; 0 unsupported; 0 rejected |
| Independent parser agreement | Complete frame counts, ordered typed fields and associations agree |
| Elapsed / sampled summed RSS | 0.665 seconds / 29,614,080 bytes |

All eight H/Y symbol/locate associations agree. Context accepted 1,433 observations and 1,424 directories, with zero orders or matches. No native book was instantiated. Source initialization remains unknown. Temporary parser `scope_complete` means reference coverage only, not session completeness.

The gzip member is deliberately incomplete. Its trailer, CRC, ISIZE, full archive integrity, trading date and complete session remain unverified. No named raw payload was retained; anonymous payload descriptors were closed. See [inspection](NASDAQ_SECOND_PREFIX_INSPECTION.md) and [acquisition evidence](NASDAQ_SECOND_PREFIX_EVIDENCE.json). The prefix establishes no new message-family coverage and does not justify automatic acquisition growth.

## Offline retained-2023 profile

Added opt-in `retained_2023_auctions_v4`, normalization version 4. Existing v1/v2/v3 defaults and semantics remain unchanged. This profile describes 23 typed retained-specification layouts, not universal historical compatibility.

| Type | Length | Representation and restrictions |
|---|---:|---|
| K | 28 | IPO quoting update; global locate zero, exact known-symbol association; A/C qualifier; cancelled release and price must be zero |
| J | 35 | LULD auction collar; exact stock/locate and raw Price(4) values; external observation |
| I | 50 | NOII; full uint64 share counts, exact prices, direction/cross/variation enumerations; external observation |
| O | 48 | Direct-listing discovery; eligibility, exact prices and raw near-time value; no invented timestamp unit |

All four remain contextual observations, not native liquidity mutations. Execution, matching, journal, replay, TCA and Python research API behavior were not changed. K's retained table identifies binary Price(4), while contradictory ASCII-like prose cannot fit its four bytes: the named profile explicitly chooses the binary table policy. This ambiguity is not empirically resolved for 2019. O is a 2023 addition; later I enumeration additions are not claimed as 2019 observations. See [compatibility matrix](ITCH50_COMPATIBILITY_MATRIX.md) for exact fields and specification references.

Checked prices, lengths, enums, mapping, optional clock policy, cancellation constraints and resource budgets reject inadmissible input before semantic commit. IPO observations route by exact configured symbol while preserving wire locate zero. Message size remains 48 bytes and DecodedRecord 304 bytes through ordinary alignment-aware member ordering; no packed access or unsafe aliasing was introduced.

## Independent and failure validation

The independently implemented Python oracle generates expectations before calling production code: 40,129 wire cases and 16,960 context candidates across 320 sessions. Seeds are 731991 and 817321. It covers full-width integers, all type octets, lengths, profiles, mappings, field constraints and deliberate expectation corruption controls.

Real allocation injection exercised three context-factory and 33 streaming allocation sites, with zero outstanding tracked allocations after cleanup. Accepted external observations required no incremental context allocations. Synthetic integration checks source receipts, native sequence/journal/FIFO isolation, routing across both symbols, restart and profile/config mismatch.

Ten streaming faults were exercised at fragments 1 and 65,536 (20 schedules): CRC corruption, truncated trailer, missing BinaryFile terminator byte, insufficient payload limit, invalid I direction, inconsistent K cancellation, duplicate add, journal exhaustion, source-record budget exhaustion and unknown type. Independent accepted-prefix counts and classifications agree across fragment sizes. Failure does not authorize complete publication. Existing replay/journal and Python interfaces were reviewed; no new production defect was reproduced and no speculative core repair was made. See [reliability review](PHASE4_RELIABILITY_REVIEW.md).

## Executed final matrix

| Configuration | Passed | Failed / skipped |
|---|---:|---:|
| GCC 14.2 Debug | 150 | 0 / 0 |
| GCC 14.2 Release | 150 | 0 / 0 |
| GCC 14.2 ASan+UBSan | 150 | 0 / 0 |
| Clang 19.1.7 Debug | 150 | 0 / 0 |
| Clang 19.1.7 Release | 150 | 0 / 0 |
| Clang 19.1.7 ASan+UBSan | 150 | 0 / 0 |
| Python 3.12 Debug | 153 | 0 / 0 |
| Python 3.12 Release | 153 | 0 / 0 |
| Python ASan+UBSan | 154 | 0 / 0 |
| Total CTest outcomes | **1,360** | **0 / 0** |

No disabled tests. Python sanitizer includes the existing live LSan control. The seven prior canonical hashes are unchanged in every configuration. New auction oracle SHA256 is `76ad62693c22631e4be0842f44029d779211451a395e8538d70450ae7015ebc6`, identical across all nine configurations. CI summary positive and deliberately wrong-hash controls passed locally. Hosted CI, ARM64 and independent-machine reproduction are not verified.

Both checkout-built and source-archive-built wheels passed fresh installed consumers: eight interface plus six export-contract cases each, 28 total. Three pinned-backend packaging regressions passed. The refreshed source archive contains 291 safe, intended, byte-identical regular members with required trees complete. Initial inventory comparison correctly flagged documentation snapshot drift; logs preserve that result. All non-documentation members agree between tested and refreshed archives. These are tested implementation snapshots, not a claim that an archive built before closure includes the final reports. Wheel version 0.1.1 and research schema 1.0 are unchanged; no Python auction API is advertised.

## Performance and memory

Executed 38 sequential GCC/Clang Release measurement runs after regression/package jobs finished. Raw timing samples, commands, binary hashes, generator identities, input sizes, repetitions, compiler/platform details and independent arithmetic checks are recorded in the companion evidence. CPU: Xeon Platinum 8573C; five affinity CPUs, quota equivalent to four CPUs. Shared-host timing is not isolated exchange latency.

| Workload | GCC | Clang |
|---|---|---|
| Pure fixed-A decode, three 10,000-call runs: p50 ns | 98 / 98 / 97 | 77 / 76 / 77 |
| Same: p99 ns | 119 / 128 / 118 | 80 / 120 / 87 |
| Same: worst ns | 278 / 50,977 / 88,885 | 439 / 23,516 / 61,875 |
| Framing+decode, 65,536 records: median ns/record | 88.5849 | 76.6407 |
| Reconstruction, 128 workload units: records/s | 83,159.4 | 89,129 |
| Streaming, 128 units, fragment 17: records/s | 71,166.5 | 73,465.4 |
| Streaming, 128 units, fragment 65,536: records/s | 74,168.2 | 78,331.5 |
| Profile-128 peak RSS bytes | 76,062,720 | 76,070,912 |

Decode uses two warmup batches and two clock reads per measured call, with no overhead subtraction. It is a cache-warm homogeneous synthetic fixture, not v4 auction throughput or a tail-latency SLA. Outliers have no attributed cause. Other batches include their documented creation/validation/destruction stages; journal call latency is not independently isolated. Seven repetitions accompany framing/context/reconstruction/streaming measurements. Raw files retain dispersion, not just medians. Small-process wait4 RSS may include the pre-exec parent's memory floor and must not be interpreted as intrinsic engine memory.

Both compilers' profile-128 runs measured 77,281,358 peak PMR bytes, with zero tracked bytes after destruction. Streaming peaks at 1,346,672 / 5,250,448 / 20,865,488 PMR bytes for 8 / 32 / 128 units. Journal entry size remains **15,944 bytes**: 100,000 element payloads alone require 1,594,400,000 bytes per book, excluding other state/capacity. Existing linear context searches and active-order accounting remain scalability concerns. No journal redesign or runtime optimization was justified by causal measurement in this phase. A separate optimization needs isolated equivalent fixtures, independent state/receipt/recovery equivalence, resource-failure comparisons and reproducible before/after measurements.

## Readiness and next actions

The machine-readable observed-readiness gate rejects malformed/coerced/duplicate-key metadata, caps local metadata input, and remains BLOCKED even if all external claims are positive: observed adapter, complete native/context seed and independent observed-book oracle are unavailable. It is a fail-closed audit, not cryptographic attestation. Actual prefix-derived facts cannot certify initial state, complete capture, exact units, restart or observed reconstruction.

The [current RC overlay](PHASE4_PRIVATE_CANDIDATE_READINESS.md) has 18 scoped PASS, seven BLOCKED, one NOT RUN and one OUT OF SCOPE across RC01–RC27. Earlier frozen assessments remain historical evidence. Owner/hosted-CI, legal/publication, security/portability and observed-data gates are not satisfied by local synthetic tests.

November 5 remains the private synthetic closure target; November 12 is contingency, not a promise about external approvals. First finish owner evidence and hosted/independent-environment qualification. Any further observed acquisition needs separate explicit byte/resource authorization and a scientifically useful coverage objective. Then require authenticated session/initial-state evidence, full event accounting, exact instrument rules, resource qualification and an independent observed-book oracle. Do not enlarge the prefix merely to obtain more directories. No full archive, real L3 reconstruction, merge, release, broker connection or Terminal change is authorized by this closure.

## Changed-file inventory and reproduction

Implementation checkpoint changes: `.github/workflows/ci.yml`, `CMakeLists.txt`, `benchmarks/CMakeLists.txt`, `benchmarks/itch_decode_latency.cpp`, `include/gig/itch/{decoder,context}.hpp`, `src/itch/{decoder,context,reconstruction}.cpp`, `scripts/check_itch_auction_reference.py`, `scripts/check_itch_decode_latency.py`, `scripts/check_observed_l3_readiness.py`, `tests/test_itch_auction.cpp`, `tests/test_itch_auction_streaming.cpp`, `tests/test_observed_readiness.py`.

Documentation: `NASDAQ_SECOND_PREFIX_INSPECTION.md`, `NASDAQ_SECOND_PREFIX_EVIDENCE.json`, `ITCH50_COMPATIBILITY_MATRIX.md`, `OBSERVED_L3_READINESS_CONTRACT.md`, `PHASE4_RELIABILITY_REVIEW.md`, `PHASE4_PRIVATE_CANDIDATE_READINESS.md`, this report, its JSON evidence, `OVERNIGHT_ENGINEERING_PROGRESS.md`, `RC_OWNER_ACTIONS.md`, `REPRODUCIBILITY.md` (all under `docs/`). Existing audits and prior remediation evidence were preserved.

Use [reproducibility instructions](REPRODUCIBILITY.md) for configuration and local commands. The readiness CLI deliberately returns exit 1 for BLOCKED; that is not a failed engine regression. No background execution continues after this report.
