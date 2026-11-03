# Institutional production audit — Sprint 1

Date: November 2, 2026 (America/New_York). Baseline `3cc75815714ffb2b73fa2e78b0a44060a34d733d`; target `development/gig-ui-redesign`. Implementation checkpoint **`11f1e9cfe6898970461855829650220a9e57bb5d`** is committed, pushed and remotely verified. Additional CI-policy checkpoint `56c503c3c4c47cbf95e32c4b8fc6a35700a69edb` adds the new offline recovery cohort to the existing owner-gated ARM64 job and verifies that requirement. No workflow was dispatched. The final evidence/documentation commit follows separately.

## Verdict and scope

GIG has substantial executable research infrastructure: C++20 strong types, exact arithmetic, FIFO order book, deterministic journal/replay, source-context reconstruction, independent oracles, simulation/execution-cost analytics, Python interchange and a private browser terminal. It is not qualified institutional production software merely because these components or passing tests exist.

This sprint repaired five bounded P1/P2 finding groups: nonregular recording files could block worker reads; authored JSON admitted ambiguity/unstructured errors; authored publication omitted directory durability barriers; recording admission enumerated an entire directory; and history backup/deletion omitted directory barriers. Nine regression methods failed before repair. No confirmed P0 exploit, native UB, unsafe order admission or current numeric defect was reproduced. That is not proof none exists.

The review covered representative actual ownership/transaction/arithmetic/replay paths, provider gates and source validation, recording/SQLite recovery, browser proof/stream boundaries, deployment/pins, export guards and benchmark code. It inspected historical audit findings and source-bound recent evidence instead of treating old prose as fresh results. This is targeted source review plus adversarial tests, not exhaustive line-by-line certification, formal verification, independent human certification or a penetration test.

## Native systems

`src/book/order_book.cpp` uses move-owned PMR state, price maps, FIFO lists and an order-ID index; normal complexity depends on levels/orders, allocations and container behavior. It is not an allocation-free low-latency book. Mutation is single-owner; direct concurrent native access is not supported. The gateway serializes shared native mutations and keeps worker-created replay native objects local to their worker.

`src/replay/replay.cpp` reserves journal admission before book mutation, verifies stream/session/dataset/ordering boundaries and retains recovery-required diagnostics. `src/itch/context.cpp` validates prepared owner/generation tokens before a no-fail commit. Exact signed128 arithmetic and symmetric capacity are intentional; source numeric/time conversions reject unsupported ranges. Existing allocation-failure, independent-reference and sanitizer cases pass. No native implementation was changed.

The synthetic L3 oracle does not establish exchange-specific empirical correctness. Unknown initialization, missing history, hidden/cross/broken observations and unsupported profiles must retain explicit classifications. IEX best quotes/prints never provide missing L3 identities or full depth. Matching simulation is a separate authored model, not observed exchange fills.

## Data, research and security

Read-only IEX and historical adapters preserve source/receipt timestamps, provenance, partial venue coverage, duplicate/late/stale status and bounded retries. Current source/account/clock/unit behavior remains provider-unqualified here. SEC integration preserves source/filing/missingness boundaries; no new SEC or other provider requests were made. Research exports retain source/profile/digest guards. Mathematical fixture correctness is not predictive alpha, calibrated queue behavior or empirical forecasting evidence.

The explicit private IEX launcher leaves legacy live and paper-execution flags zero, with default-disabled storage/export/options/SIP. Source permissions do not authorize orders. Origin/Host/proof controls remain intact; forwarded headers do not grant authority. Private GitHub authentication is an external deployment assumption, not established by localhost tests. No secrets/configuration values, real data or account information were read or committed.

Pins and `pip check` are consistency evidence, not current CVE/OS clearance. Owner-target patch/advisory review is open. A same-owner, private filesystem is the supported persistence threat model; this is not a hostile shared-filesystem sandbox.

## Reliability and performance

Recording reads now reuse the existing descriptor-based bounded reader: O_NONBLOCK/O_NOFOLLOW, regular-file admission, fstat size and mutation checks. Strict authored JSON preserves valid bytes while rejecting duplicates/nonobjects. L2 legacy duplicate-key error classification remains compatible. Bounded scans and fsync barriers are tested. An error after rename explicitly reports uncertain publication; valid targets are not deleted or overwritten. No power-loss RPO/RTO or complete-session hot recovery is claimed.

A new benchmark combines existing independent native book/reconstruction preflights with exact Python replay and a four-symbol bounded projection oracle. It records p50/p95/p99 serial service samples, throughput, memory, CPU time, toolchain and source/result hashes. Results are local authored workloads, not exchange/edge latency or an optimization claim. See PERFORMANCE_BASELINE.md.

## Qualification decision

All executed final tests pass. The current candidate is an improved private-research engineering baseline. It is **not institutionally production-qualified**: current native ARM64, actual owner Codespaces/private-edge/browser acceptance, live/historical IEX, current runtime/advisory clearance and realistic sustained-load assurance remain incomplete. Existing older ARM64 runs do not qualify this checkpoint. No workflow was launched.

The 29-requirement matrix provides source line ranges, reproduction, severity, actual evidence, effort and acceptance criteria. Fixed issues retain their failed-before history. Remaining priorities and bounded effort are in REMAINING_WORK_PLAN.md. No fabricated readiness percentage is assigned.
