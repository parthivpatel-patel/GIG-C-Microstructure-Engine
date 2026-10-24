# GIG C++ MICROSTRUCTURE ENGINE
# AUTONOMOUS DEVELOPMENT MANDATE — PHASES 3–9

## EXECUTIVE AUTHORIZATION

You are authorized to continue developing the GIG C++ Microstructure Engine through Phases 3, 4, 5, 6, 7, 8, and 9 without requesting routine approval between phases.

This authorization applies only to the standalone private repository:

parthivpatel-patel/GIG-C-Microstructure-Engine

Development branch:

feat/bootstrap-cpp20-engine

Verified Phase 2 starting point:

511ae18c9eff750dda346e9c1cc13571a6594bee

Follow the complete original master specification, Phase 0 architecture, Phase 0B decisions, Phase 1 contracts, and Phase 2 implementation documentation.

Your objective is to develop the most complete, correct, reproducible, and technically defensible implementation reasonably achievable within the available environment.

Do not rush through phases merely to claim completion.

You are acting as Principal Quantitative Systems Architect, Principal C++ Engineer, Quantitative Research Engineer, Performance Engineer, and Technical Reviewer.

## 1. AUTONOMOUS EXECUTION POLICY

Proceed sequentially through Phases 3–9.

You do not need my approval after each successfully validated phase.

At every phase boundary:

1. Verify the previous checkpoint.
2. Review requirements and dependencies.
3. Implement the next bounded milestone.
4. Execute appropriate tests.
5. Fix discovered defects.
6. Review the changes.
7. Commit and push.
8. Verify the remote GitHub SHA.
9. Write a completion report.
10. Continue to the next phase.

Do not substitute planning or status messages for implementation.

Do not claim work is complete without supporting evidence.

If execution is interrupted, resume from the latest verified remote checkpoint after rechecking the repository state.

Do not assume an interrupted cloud session has continued running.

## 2. NONNEGOTIABLE SAFETY RULES

Never:

- Force-push.
- Rewrite published Git history.
- Delete the repository.
- Merge into main.
- Modify GIG Quant Terminal.
- Introduce live trading.
- Connect a broker account.
- Submit real orders.
- Commit credentials or restricted market data.
- Fabricate benchmark results.
- Conceal failing tests.
- Weaken correctness requirements to improve speed.
- Claim unsupported exchange mechanics.
- Introduce unnecessary infrastructure.

Do not create paid cloud resources or incur external costs.

Do not perform external publication or release actions without explicit authorization.

## 3. GITHUB AS THE DURABLE SOURCE OF TRUTH

GitHub is the authoritative project state.

At the beginning of every work session:

- Verify repository identity.
- Verify development branch.
- Fetch and inspect remote changes.
- Check working-tree cleanliness.
- Confirm the last verified commit SHA.
- Read the latest phase report.

After every meaningful, verified checkpoint:

- Review the diff.
- Run required tests.
- Commit the work.
- Push normally.
- Verify that the exact remote SHA matches.
- Record the checkpoint and remaining risks.

If the remote branch advances unexpectedly, inspect and reconcile safely.

If pushing or remote verification fails, stop accumulating substantial unpushed work.

Never discard another contributor's changes.

## 4. PHASE 3 — BOOK-STATE ANALYTICS

Implement:

- Best bid and ask.
- Spread.
- Exact midpoint.
- Microprice.
- Top-of-book imbalance.
- Configurable depth imbalance.
- Aggregated bid and ask depth.
- Explicit unavailable metric states.
- Immutable analytics results.
- Snapshot revision and provenance tracking.

Use exact arithmetic where required.

Validate calculations with independent Python integer/Fraction references and hand-worked examples.

Test empty books, one-sided books, locked books, half-tick prices, zero denominators, extreme values, and insufficient depth.

Ensure analytics do not mutate the book.

Complete and validate Phase 3 before proceeding.

## 5. PHASE 4 — TRADE, QUOTE, AND FLOW ANALYTICS

Implement defensible research metrics where supported by the data contracts:

- Order Flow Imbalance.
- Trade direction classification.
- Lee–Ready-style trade signing with documented assumptions.
- Trade and quote event intensities.
- Effective spread.
- Realized spread.
- Horizon-based price impact.
- Return and volatility estimators.
- Windowed microstructure statistics.

Explicitly handle:

- Quote lag.
- Unknown trade direction.
- Timestamp alignment.
- Sampling frequency.
- Missing observations.
- Sequence gaps.
- Reset boundaries.
- Look-ahead prevention.

Kyle-style lambda and VPIN-style diagnostics are experimental.

Implement them only when the required assumptions, independent reference calculations, and valid input conditions can be established.

Do not invent unavailable market data or calibration parameters.

Document every mathematical formula, unit, assumption, and invalid state.

## 6. PHASE 5 — QUEUE, LATENCY, AND SYNTHETIC MATCHING

Implement a separate offline simulation subsystem.

Required capabilities:

- Synthetic price-time-priority matching.
- Deterministic seeded event scheduling.
- Queue-position tracking.
- Partial fills.
- Full fills.
- Order cancellation.
- Cancellation races.
- Order arrival latency.
- Acknowledgment latency.
- Execution latency.
- Marketable limit orders.
- Supported time-in-force semantics.
- Configurable simulation assumptions.

Keep historical reconstruction and synthetic matching completely separate.

Never present simulated executions as observed exchange executions.

Ensure causality: simulated decisions cannot use information unavailable at decision time.

Validate the simulator against independent reference examples.

## 7. PHASE 6 — EXECUTION ALGORITHMS AND TCA

Implement offline research versions of:

- TWAP.
- VWAP.
- POV.
- Configurable execution schedules.
- Participation constraints.
- Inventory constraints.
- Transaction cost calculations.
- Slippage decomposition.
- Fee and spread costs.
- Implementation shortfall.
- Execution-quality reporting.

Historical VWAP schedules must not use future volume information unless explicitly labeled as an oracle benchmark.

Use deterministic scenarios and independently calculated numerical references.

Document modeling limitations, including missing hidden liquidity, adverse selection, and market impact calibration.

Do not connect to live brokers.

## 8. PHASE 7 — PERFORMANCE ENGINEERING

Establish reproducible baselines for the implemented engine.

Measure:

- Book mutation throughput.
- Replay throughput.
- Snapshot and analytics performance.
- Matching and simulation performance.
- Allocation counts.
- Peak memory.
- Event-copy overhead.
- p50, p95, and p99 latency where statistically meaningful.

Record:

- CPU and architecture.
- OS and compiler.
- Optimization flags.
- Dataset or synthetic generator.
- Workload composition.
- Sample counts.
- Repetitions.
- Exact commit SHA.

Optimize only when profiling identifies a measurable bottleneck.

For every optimization:

1. Preserve a pre-optimization baseline.
2. Implement one bounded change.
3. Run correctness tests.
4. Compare deterministic outputs.
5. Benchmark under comparable conditions.
6. Report gains and regressions.
7. Revert changes that undermine correctness or maintainability without sufficient benefit.

Do not introduce lock-free structures, concurrency, custom allocators, or specialized containers solely for appearance.

## 9. PHASE 8 — PYTHON BINDINGS AND GIG INTEGRATION

Create a clean, documented Python research interface using an appropriately pinned binding library.

Support:

- Validated event input.
- Deterministic replay.
- Book snapshots.
- Analytics.
- Offline simulation.
- Structured errors.
- Provenance.
- Reproducible outputs.

Implement versioned interchange schemas for:

- Events.
- Book snapshots.
- Metric results.
- Simulation outputs.
- Research run manifests.

Preserve exact 64-bit integers across Python and JSON boundaries.

Test object ownership, lifetime safety, exceptions, and schema compatibility.

GIG Quant Terminal remains a separate consumer.

Do not modify or introduce a build dependency on the Terminal repository.

## 10. PHASE 9 — RELEASE VALIDATION AND REPRODUCIBILITY

Perform:

- Clean build verification.
- Debug and Release testing.
- AddressSanitizer validation.
- UndefinedBehaviorSanitizer validation.
- Clang compatibility testing where available.
- ARM64/aarch64 validation where available.
- Deterministic replay reproducibility.
- Independent numerical reference validation.
- Benchmark reproduction.
- Python package smoke tests.
- Schema compatibility checks.
- Documentation review.
- Security and dependency review.
- License and data provenance review.

Provide a complete reproducibility guide.

Clearly distinguish:

- Verified on x86_64.
- Verified on ARM64.
- Cross-compiled only.
- Not tested.
- Unsupported.

If native ARM64 hardware is unavailable, do not claim native ARM64 validation.

Do not publish a release without my authorization.

## 11. QUALITY GATES FOR EVERY PHASE

A phase is complete only when:

- Required implementation exists.
- Its mathematical and engineering contracts are documented.
- Relevant unit tests pass.
- Regression tests pass.
- Independent reference checks pass where applicable.
- Debug and Release builds pass.
- Required sanitizers pass.
- Relevant benchmarks are recorded.
- Limitations are disclosed.
- Changes are reviewed.
- Commits are pushed.
- Exact remote SHAs are verified.

A blocked phase is not a completed phase.

Do not silently skip required work.

## 12. FAILURE HANDLING

When a test fails:

Investigate, fix, and rerun it.

When an optimization regresses correctness:

Revert or correct it.

When a dependency is unavailable:

Prefer a documented, technically sound alternative.

When GitHub Actions is inaccessible:

Run equivalent local checks where possible, report hosted CI as unverified, and continue if no other gate is blocked.

When native ARM64 is unavailable:

Document the limitation and complete other independently verifiable work.

Stop and request my intervention only when:

- An unresolved correctness defect blocks safe progress.
- A fundamental architecture change requires a decision.
- Git history or remote state cannot be reconciled safely.
- A required external credential or restricted dataset is necessary.
- The next action would violate an explicit project restriction.
- A mandatory validation gate cannot be satisfied or reasonably isolated.

Do not repeatedly interrupt for ordinary engineering choices.

## 13. RESOURCE MANAGEMENT

Use the available cloud environment efficiently.

Prefer:

- Bounded test workloads.
- Deterministic synthetic datasets.
- Incremental builds.
- Minimal dependencies.
- Small durable checkpoints.
- CPU-only computation.

Avoid excessive memory, unnecessary parallel builds, and expensive infrastructure.

Do not assume a GPU is available.

## 14. DOCUMENTATION AND INTERVIEW READINESS

For each phase, maintain documentation explaining:

- Architecture.
- Mathematical definitions.
- Data structures.
- Time and space complexity.
- Memory behavior.
- Numerical precision.
- Assumptions.
- Failure modes.
- Testing methodology.
- Benchmark methodology.
- Alternative designs.
- Limitations.

Include explanations suitable for defending the system in Quant Developer, Quant Researcher, and Quantitative Software Engineering interviews.

## 15. REQUIRED PROGRESS REPORTS

At every completed phase, write a durable report in the repository.

Include:

A. Phase objective.

B. Starting and ending SHAs.

C. Changed files.

D. Implemented functionality.

E. Tests and actual results.

F. Independent validation evidence.

G. Benchmark evidence.

H. CI status.

I. Known limitations.

J. Remaining risks.

K. Acceptance checklist.

L. Next phase.

Continue automatically after completing and verifying each phase.

## 16. FINAL DELIVERABLE

At the end of Phase 9, produce:

1. Complete implementation summary.
2. Final architecture diagram.
3. Phase-by-phase completion matrix.
4. GitHub commit traceability.
5. Correctness and numerical validation report.
6. Performance benchmark report.
7. Python integration guide.
8. GIG Quant Terminal integration contract.
9. Reproducibility instructions.
10. Known limitations and future research directions.
11. Interview preparation guide.
12. Final acceptance assessment.

Do not claim completion of unverified requirements.

Do not merge into main or publish a release.

## FINAL EXECUTION INSTRUCTION

Begin with Phase 3 immediately.

Proceed autonomously through Phases 4–9 as each phase satisfies its quality gates.

Do not stop after every phase to request routine approval.

Keep implementation, testing, documentation, and GitHub checkpoints moving forward within the active execution session.

If the environment stops or the task reaches its execution limit, leave the repository in a clean, durable state and record the exact continuation instructions.

Stop only after Phase 9 is complete or a genuine blocking condition is encountered.

Preserve correctness, reproducibility, and GitHub history above development speed.