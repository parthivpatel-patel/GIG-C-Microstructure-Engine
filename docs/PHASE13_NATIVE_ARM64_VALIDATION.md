# Phase 13 — native ARM64 qualification preparation

> **October 24, 2026 closure update (America/New_York):** Native Linux ARM64
> qualification is CLOSED at f02363e0e09b9767b4dc6748737206254e5e4c6a.
> Run40126420107 and all six job successes are independently verified from official
> public GitHub pages. See [current qualification and readiness overlay](NATIVE_ARM64_QUALIFICATION.md)
> and its structured evidence. Current RC18 is PASS scoped; RC13 and RC17 are
> PARTIAL, RC16/security and observed-market gates remain blocked. Aggregate:
> 19 scoped PASS / 5 BLOCKED / 2 PARTIAL / 1 OUT OF SCOPE.
> The report below is preserved historical source-bound evidence; its ARM-not-run,
> API-only access blocker, old counts/source-equivalence and owner actions do not
> override the newer closure. No raw hosted log/JUnit export is claimed.


October 24, 2026 (America/New_York). **Prepared, not executed. Native ARM64 and
independent-machine gates remain unclosed.** No billable runner was launched.

## Verified baseline and hosted evidence

Local and remote feature HEAD at entry: `caaf5a14032406f0fbbb962595c20bf840fcb1a9`.
Branch: `feat/bootstrap-cpp20-engine`; clean working tree. Remote main:
`165c5038336887116d69160b0d8e5a1a5ef59d16`. Reviewed Phase 12 report and existing
`.github/workflows/ci.yml`. Existing six-configuration CI is byte-identical.

Owner confirms successful workflow runs **#140 and #141**. These are run numbers,
not independently recovered run IDs. Exact commit/PR merge SHA, job conclusions,
runner versions, test counts and warnings remain unverified. One request:

```
gh api 'repos/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/runs?per_page=5'
```

returned exit 1, `Get "https://api.github.com/repos/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/runs?per_page=5": Forbidden`.
No blocked retries. Runtime observations are current, connectivity connected,
network-policy enforcement unknown; api.github.com is absent from the effective
allowlist. No runtime identity or secret readiness was reported. Git remote access
works separately; it does not establish Actions API authorization.

## Runner eligibility and cost

Official GitHub documentation source retrieved successfully over verified HTTPS:

- [Runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners),
  source `https://raw.githubusercontent.com/github/docs/main/content/actions/reference/runners/github-hosted-runners.md`:
  SHA256 `2ba4307f64e55251e63555e97a51381e4eb36334693a464c743522a09546a148`, 8957 bytes.
- Runner table source `https://raw.githubusercontent.com/github/docs/main/data/reusables/actions/supported-github-runners.md`:
  SHA256 `2c5913f214ddf4991c36bb2ad4928bd8b2c48dbf6b8fb4d7cec4bc3a72bcca5f`, 9087 bytes.
- [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions),
  source `https://raw.githubusercontent.com/github/docs/main/content/billing/concepts/product-billing/github-actions.md`:
  SHA256 `a40dc1897d605b0c6b3780523260180780649741a27ce47ce12b8e964e14342c`, 14678 bytes.

These are current mutable documentation observations, not immutable policy
contracts. The table lists `ubuntu-24.04-arm` and `ubuntu-22.04-arm` in both
public and private standard Linux runner categories. Public ARM specifications:
4 CPUs, 16 GB RAM, 14 GB SSD; private: 2 CPUs, 8 GB RAM, 14 GB SSD. Actual runner
resources must be measured. This is standard hosted infrastructure, not the
separately billed larger-runner product.

Public standard runner compute is free; private standard runner usage consumes
plan allowances and excess is billed to the repository owner. Artifact/storage
allowances are separate. Larger runners are charged even with free minutes.
Repository was described as private in prior instructions, but present visibility,
plan, policies, remaining minutes/storage and spending controls cannot be
independently read through the blocked API. **Free eligibility is NOT established.**
Do not change repository visibility to obtain free execution. Do not provision a
larger runner, purchase capacity or dispatch until owner verifies no charges.

## Prepared workflow and independent reproduction

`.github/workflows/native-arm64.yml` is separate and manual-only. No push/PR,
schedule or automatic trigger is added. Required boolean `free_usage_verified`
defaults false; job also requires the authorized feature ref. Owner confirmation
is a procedural gate, not an API billing meter. A six-job run can consume up to
360 runner-minutes at its 60-minute/job ceiling; cancellation/queue behavior and
storage must also be considered before dispatch. No artifact-upload charges are
introduced by this workflow; logs still require retention review.

The six fresh jobs use GCC/Clang × Debug/Release/ASan+UBSan on
`ubuntu-24.04-arm`. Each verifies runner.arch=ARM64, uname=aarch64, clean checkout
and exact github.sha; prints run ID/attempt, image identity, OS, CPU, RAM/disk,
compiler/build-tool/Python versions; builds the existing SHA-qualified zlib 1.3.1
in a private prefix. No QEMU, cross compiler, restored build cache or container
is used. Hosted runner identity remains part of trusted GitHub evidence, not a
hardware-attestation claim.

Existing strict presets and assertions are retained. Planned CTest totals are
154 in five native-only jobs and 157 in GCC Release with Python. All eight exact
canonical digests are copied unchanged from existing CI and checked in JUnit.
Missing/failed/skipped/disabled cases fail qualification. `/usr/bin/time -v`
records CTest process-tree resource observations, not isolated engine RSS or
exchange latency. Benchmark smoke checks remain correctness-only.

GCC Release installs the pinned Python lock, builds and installs a private wheel,
runs interface/export tests and research example. It builds two fixed-epoch sdists,
requires byte equality, validates member safety/completeness/content against Git,
then builds and installs a second wheel from the verified archive and reruns
consumer checks. The lock was previously x86-qualified only: ARM dependency wheel
availability and ABI behavior remain actual test gates, not assumptions. Python
bindings are NOT enabled in sanitizer jobs, matching existing infrastructure;
ARM Python sanitizer qualification remains separate and untested.

An external hosted machine can supply fresh-environment reproducibility evidence;
it is not an independent human audit. The full runner logs/JUnit, dependency
identities and source SHA must be exported and reviewed before RC13 changes.
Source archives contain code/docs only, never market data. No publication.

## Actual validation and gate status

| Item | Actual result |
|---|---|
| Baseline branch/local/remote/clean | Verified |
| Owner runs #140/#141 | Owner-confirmed success only; IDs/SHAs/jobs unavailable |
| New native workflow runs / IDs | NONE; not dispatched |
| Native ARM64 tests, hashes, Python, sanitizer/resource results | NOT RUN |
| Independent hosted reproduction | NOT RUN |
| Workflow YAML structure | Parsed with PyYAML 6.0.3 BaseLoader; manual/default-false/ref guard, six entries verified |
| Shell / embedded Python syntax | 13 run blocks pass bash -n; inline Python parses |
| Original CI | Byte-identical to entry Git blob |
| Engine regression rerun | Not required: no engine/test/API/dependency-lock edits |
| Existing cross/QEMU evidence | Preserved; 154 distinct tests and eight matches, not native evidence |

Syntax/structure checks do not validate GitHub service semantics or runner image
contents. No actionlint or hosted validation is claimed. No additional market
requests or cloud configuration changes occurred.

Release gates stay **RC13 BLOCKED, RC17 BLOCKED, RC18 PARTIAL**. The previous
18 scoped PASS / 7 BLOCKED / 1 PARTIAL / 1 OUT OF SCOPE assessment is unchanged.
RC16 security/provider and observed-market gates are unaffected. Private synthetic
evaluation remains scoped GO; formal closure blocked; observed L3 NO-GO;
production readiness outside scope.

## Exact owner actions

1. Verify repository visibility, Actions policies, standard ARM label eligibility,
   remaining free minutes/storage and spending limits in owner Settings/Billing.
   Do not dispatch if any extra charge is possible without separate approval.
2. Provide authorized Actions read access and supported api.github.com allowlisting
   through environment review/publication, or export metadata/logs yourself.
   For #140/#141 use `gh api --paginate --slurp
   repos/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/workflows/ci.yml/runs?per_page=100`
   (quote the endpoint in a shell); select `run_number`, then export each actual
   numeric run ID with `gh run view ID --json headSha,event,status,conclusion,jobs`
   and `gh run view ID --log`. Bind PR head/base/merge/checkout SHA separately.
3. Manual dispatch requires workflow registration on the default branch under
   [GitHub workflow_dispatch rules](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow). This new file exists only on the feature branch;
   no default-branch modification is authorized here. If GitHub cannot discover it,
   stop: owner must authorize a suitable workflow-registration/trigger approach.
   Do not merge into main merely to enable dispatch.
4. Once registration, free eligibility and authorization are established, run
   `gh workflow run native-arm64.yml --ref feat/bootstrap-cpp20-engine -f free_usage_verified=true`.
   This command was NOT executed. Keep tested SHA explicit and export all six job
   logs, JUnit and warning annotations before retention expires. Any failure must
   retain failing-before evidence and be repaired before claiming qualification.
5. Compare all eight hashes and counts, source archive inventory, installed Python
   outputs and measured versions/resources. Only actual successful native jobs
   permit updating RC18; assess RC13 and RC17 separately. Security gates remain.

Changed files: this report and `.github/workflows/native-arm64.yml` only.
Final commit identity is reported after push to avoid a self-referential hash.
