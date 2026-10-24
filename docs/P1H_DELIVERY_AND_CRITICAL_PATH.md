# P1H delivery and conditional critical path

As of 2026-10-23, P1H is complete and remotely verified on
`feat/bootstrap-cpp20-engine`. Starting P1G checkpoint:
`c3c3d8caef8f5b60aa4ce29f0f0875dc3bdd91c4`; P1H implementation:
`e055f055a447baa6bf1f913c09f7c7dcd57a8878`; P1H evidence checkpoint:
`cafcdb986afac5298c95bcf3418acb7cf3e6aafe`.
Main remains `165c5038336887116d69160b0d8e5a1a5ef59d16`.
A subsequent documentation-only commit records the completion status and plans.

## Evidence and scope

[P1H validation](P1H_VALIDATION_REPORT.md), [coverage](P1H_COVERAGE.md),
[raw evidence manifest](P1H_EVIDENCE.json), and [reproduction](REPRODUCIBILITY.md)
contain the executed results. All 1,063 CTest outcomes passed with zero failures,
skips or disabled tests across nine configurations. Both installed-wheel consumer
suites passed. Canonical P1E/P1F/P1G hashes remain unchanged.

The standalone pipeline is synthetic-only. Joint source/native transactions remain
P1G contracts. Whole-source publication requires valid EOF, gzip integrity, framing,
semantics and exact configured identities. Accepted prefixes remain provisional.
Restart rebuilds from byte zero; it is not durable crash recovery or compressed seeking.
System zlib is optional, unvendored and disabled for ordinary Python wheels.

## Complete P1H changed-file inventory

A=added, M=modified, relative to the verified P1G checkpoint:

```text
M	.github/workflows/ci.yml
M	CMakeLists.txt
M	CMakePresets.json
M	THIRD_PARTY_NOTICES.md
M	benchmarks/CMakeLists.txt
A	benchmarks/itch_streaming_benchmark.cpp
M	docs/OVERNIGHT_ENGINEERING_PROGRESS.md
A	docs/P1H_COMPRESSION_DEPENDENCY_REVIEW.md
A	docs/P1H_COVERAGE.md
A	docs/P1H_EVIDENCE.json
A	docs/P1H_VALIDATION_REPORT.md
M	docs/REPRODUCIBILITY.md
M	include/gig/itch/binary_file.hpp
A	include/gig/itch/gzip.hpp
A	include/gig/itch/streaming.hpp
A	scripts/check_itch_streaming_benchmark.py
A	scripts/check_itch_streaming_reference.py
A	src/itch/gzip.cpp
A	src/itch/streaming.cpp
A	tests/itch_streaming_reference_driver.cpp
A	tests/support/itch_gzip_fixture.hpp
A	tests/test_itch_gzip.cpp
A	tests/test_itch_streaming.cpp
```

Subsequent planning/status changes affect only documentation: this file,
P1I_END_TO_END_VALIDATION_PLAN.md, P1J_INDEPENDENT_AUDIT_AND_RC_REQUIREMENTS.md,
P1G_VALIDATION_REPORT.md, P1H_VALIDATION_REPORT.md, P1H_EVIDENCE.json and
OVERNIGHT_ENGINEERING_PROGRESS.md. No native journal, matcher, execution or TCA
implementation changed in P1H. Existing audits and remediation evidence are preserved.

## Remaining risks and external gates

- Hosted CI cannot be independently inspected: authenticated API request returned
  Forbidden. Actual Ubuntu runner zlib package/runtime compatibility requires
  execution evidence; installing a package is not proof of CMake>=1.3.1 compatibility.
- Linux x86_64 GCC/Clang only; ARM64, other OSes, libc++ and other Python versions
  remain unqualified. Local sanitizers do not prove absence of all defects.
- Fixed microstep decompression is a correctness baseline; no exchange latency SLA.
  Benchmark medians cover a stored-DEFLATE synthetic workload on a shared host.
- Journal entry size remains 15,944 bytes and hard journal limit 100,000. No storage
  optimization occurred. Budget admission can stop a source before EOF; this must
  never be presented as full-session validation. PMR caps exclude fixed objects,
  fixtures, allocator/process overhead and dependency memory outside that resource.
- Real-source prelude, historical message profiles, symbol routing and initial-state
  evidence are not established. Unsupported records must stop or be explicitly
  classified. No automatic empty-book inference is permissible.
- User-provided Nasdaq permission supports sample download/use; unrestricted raw
  redistribution/publication is unresolved. No market data was acquired. Further
  acquisition requires separate authorization and disk/runtime/resource verification.
- LOBSTER support case #17931099 is external and does not block synthetic work.

## Dependency-aware critical path

There are 13 calendar days from October 23 to November 5 and 20 to November 12.
These are planning windows, not completion or production-readiness promises.

1. Review and explicitly authorize the [P1I plan](P1I_END_TO_END_VALIDATION_PLAN.md).
   Synthetic end-to-end coverage and independent audit preparation can proceed
   without market-data licensing/network resolution once authorized.
2. Close failure/accounting/restart/adversarial and resource gates on frozen source;
   qualify actual hosted toolchains and dependency versions. Repair before an RC.
3. Execute the [P1J independent audit and RC requirements](P1J_INDEPENDENT_AUDIT_AND_RC_REQUIREMENTS.md)
   against an exact candidate SHA. A private synthetic research candidate may be
   assessed separately from observed-market validation.
4. Separately authorize a resource-bounded official-source format pilot. Verify
   artifact integrity/profile/session and initialization eligibility before any L3
   claim; acquire independent reference evidence before empirical correctness claims.
5. Only after explicit further authorization consider release publication or a merge.
   Neither is included here. Production trading is a separate scope.

If observed-market gates cannot close by November 5, preserve the synthetic candidate
and disclose the blocked empirical scope. November 12 is contingency for evidence and
repairs, not permission to weaken acceptance or label unvalidated work complete.
No P1I/P1J production code has begun. Exact next action: user review and authorization.
