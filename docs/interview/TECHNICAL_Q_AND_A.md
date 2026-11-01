# Technical questions and defensible answers

**What is independently verified?** Exact numerical references, native book/replay/simulation oracles and negative controls, source/provenance contracts, bounded fixture ingestion, browser/API paths and the stated toolchain matrix. Refer to the exact source-bound Sprint3 manifest. These are finite engineering results, not empirical alpha or production certification.

**How do you avoid overflow and unit errors?** Native strong price/quantity/time identifiers with checked integer/rational arithmetic; exact backend decimal/fraction paths; explicit units and approximation only at display. The paper sandbox accepts decimal cent strings and whole-share strings, rejects excess precision and checks each new fill increment against the limit.

**Why not convert every event to a book change?** Hidden/cross/broken/admin observations have different semantics. L1 quotes do not supply order IDs or full depth. Incomplete initialization and unsupported source events remain explicit; no synthetic order is relabeled as observed.

**What does a canonical hash prove?** Equality of declared deterministic output under the tested fixture/contract. It does not prove broad exchange compatibility, data licensing, queue reconstruction from partial snapshots or profitability. This sprint compares eight identities in six unchanged-source native configurations; it does not launch ARM64 qualification.

**How are UI response limits enforced?** Before copying/decoding an incoming chunk. A3MiB unknown-length stream exceeds the2MiB retained buffer cap, cancels and shows an error. UTF-8 split boundaries, false lengths, abort and stalled cancellation are tested. Browser transport can prefetch independently, so this is not a strict download-byte cap.

**How do model demonstrations prevent look-ahead claims?** Explicit supplied chronology and training/holdout/fold scopes; fixed-filter outputs versus full-sample fitted states are distinguished. SEC filing acceptance time is not reconstructed from cache receipt time. Source availability and corporate-action/session gaps remain limitations. No profitable-signal claim.

**How do you handle ambiguous order acknowledgment?** Persist intent/reservation before send, bind a stable client ID and never blindly resend a possibly created order. Unknown state blocks new admission until reconciliation. Fake tests cover create/cancel timeouts and failure after fake commit. Real broker coherence and actual paper-order tests are not implemented/authorized yet.

**Is the fake paper architecture exactly-once or crash-safe?** SQLite FULL transactions and actual child interruption/backup/restart tests support the stated local boundary. A network acknowledgment and local commit cannot be atomic. Hashes are corruption checks, not malicious-owner signatures. No broker hot recovery, power-loss durability, RPO/RTO or exactly-once network claim.

**How do you secure private browser forwarding?** Exact configured Origin/Host, same-origin non-simple bootstrap and one-use endpoint-bound proof, bounded bodies/rate/work/client counts and safe diagnostics. Arbitrary forwarded headers do not grant authority. Local HTTPS/WSS proxies test rewriting; owner GitHub authentication/private-port acceptance is a separate evidence gate.

**How is 3D scientifically honest?** Explicit source/coverage/symbol/time, model-specific required inputs, exact inspection/table alternatives and no fabricated depth. Event-driven rendering and disposal preserve responsiveness. Node geometry timing/SwiftShader pixels are not real-GPU throughput or exchange latency.

**What is still missing?** Genuine provider permission/qualification for the selected scopes, current-owner deployment acceptance/current ARM64, observed complete initialization and independent empirical L3 comparison, real broker transport/risk approval/account/order qualification and long-session operational testing. Optional speculative models and production live trading are outside this sprint.
