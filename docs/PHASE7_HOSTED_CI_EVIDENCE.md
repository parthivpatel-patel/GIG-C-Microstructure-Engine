# Phase 7 hosted CI evidence — October 24, 2026 (America/Los_Angeles)

Entry feature SHA ea2df47597fecb446013c902d2a74be4644ffdc0, clean. Owner reports
C++ CI #129 SUCCESS, PR event, six green GCC/Clang Debug/Release/ASan+UBSan jobs,
approximately4m29s, six nonfatal warnings. Owner also reports commit-triggered
#128 SUCCESS. These are owner observations, not independently retrieved artifacts.
Run numbers128/129 are not API database run IDs. Tested SHAs remain unknown.

One authorized API request returned exit1/Forbidden (raw build/extended/evidence/
hosted.stderr); api.github.com absent from current reported allowlist, policy
state unknown. No retry or bypass. Exact IDs, tested SHAs, job/runner/compiler/
dependency versions, expected CTest counts, warning content and PR merge-versus-head
identity remain unverified. Six warnings are not classified harmless without logs.

Workflow source at entry: .github/workflows/ci.yml, Ubuntu24.04, gcc/clang ×
debug/release/asan-ubsan, strict warnings, pinned zlib helper, Python enabled on
GCC Release. It requires154 native/157 Python-enabled CTest outcomes, no skips/
disabled/failures and all8 canonical hashes. Configuration is not execution proof.

## Exact owner export procedure

On an authorized GitHub client, export metadata without inferring IDs:

```sh
gh api --paginate --slurp 'repos/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/workflows/ci.yml/runs?per_page=100' > workflow-pages.json
```

Select workflow_runs entries by run_number128/129; retain their id, event, head_sha,
head_branch, pull_requests, conclusion, workflow_id, check_suite_id, html_url and
runner timestamps. For each actual ID, export the run endpoint and `/jobs?per_page=100`
with all pages, `gh run view ID --log`, and available JUnit/artifacts. Export each
job's check-run annotations to preserve all six warnings and exact affected steps.
Keep credential values out of files.

For PR events, retain PR head/base and merge SHA and the checkout log's actual
resolved HEAD; do not substitute branch HEAD for a merge commit. Compare tested
source tree with candidate tree using authenticated Git objects. Report any delta,
including later test changes. Require actual per-job CTest count/hash summaries,
compiler identification, runner image version and zlib build/runtime identity.
Hash all exports and record acquisition time. No numerical run ID or exact source
match has been invented here. RC17 remains BLOCKED for independently bound evidence.
