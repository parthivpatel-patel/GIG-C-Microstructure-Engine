# Bounded private research envelope: observed controls and proposed qualification

This is a research envelope, not a production SLO. No deployment configuration or
managed runtime was changed. Target Codespaces/ARM64/endurance acceptance remains
pending; Codex x86_64 measurements do not qualify those targets.

| Component | Existing hard bound / observed control | Qualification interpretation |
|---|---|---|
| Native terminal | Single owner; 32 MiB tracked PMR; authored bounded replay | PMR is not total RSS; capacity errors must preserve accepted state |
| Native journal library | Default4096/max100000 records; physical ordinary record12232bytes |100000 ordinary payload≈1.223GB/book before overhead; not a viable terminal RAM target |
| Analytical HTTP work | One admitted physical worker/app; busy requests rejected; cancelled caller cannot free its slot; shutdown drains | No application waiting queue; no machine-wide quota or hard preemptive deadline |
| Browser SSE |8 clients, latest snapshots,≤1 MiB frame,2 s send deadline | Current in-flight sends/bytes and peak bytes are measured; no event backlog is retained |
| Upstream transport |4 frames×32768byte configured limit; 256 history/256 dedup identities | Actual library queue depth unavailable through stable public API; source losses UNKNOWN without exchange sequence |
| Browser state | Bounded histories, optional renderers andpoint budgets | Physical GPU/mobile memory not qualified by headless fixtures |
| Optional private stores |32 MiB SQLite page/file caps per store; observation payload16MiB/10000rows; TTL; FULL sync, DELETE journal, secure_delete | Rollback journals, backups/staging require extra disk; observed retention remains disabled |
| History backup | Explicit no-overwrite, digest/schema checks, expiry on restore,128 MiB free-space precheck | Not a global disk quota or independent production backup/RPO certificate |

Proposed private-session operating target:one owner/one backend process, at most
four IEX symbols when separately permitted, eight browser clients, one analytical
worker,512 MiB backend RSS alert target,512 MiB available private working disk plus
separate build/dependency space. These are documented targets, not newly enforced
service/container limits or measurements of the owner's target. Do not assume
unlimited Codespaces/free hosting or enable observed retention to test them.

`qualify_remediation_envelope.py` is a reproducible fixture-only Linux qualification:
5000 synthetic quote observations; bounded history/dedup and exact counts; 40maximum
quantity concentration levels; four journal scales/reset mixtures. Python fixture
child has a512MiB address-space cap,20/22 s CPU soft/hard bounds,32 MiB per-output-file
cap and30s wall deadline. Native probe children have the same resource caps and a
10 s watchdog each. Inputs/counts are fixed; no archive/provider input is accepted.
This cap is a qualification-process bound, not a change to the running terminal.

The exact25-case remediation cohort adds quiet heartbeats, bounded coalescing, real
2 s slow-reader timeout, cancelled sends, client/payload exhaustion,5000-observation
burst/browser resync/stale/generation behavior,100busy rejections andphysical worker
shutdown/failed-job accounting. Existing native allocation-failure/journal recovery
and Python crash/hash/TTL tests remain mandatory. A short bounded campaign does not
close sustained overnight production endurance.

```bash
PYTHONPATH=build/python-release/python:. .venv/bin/python scripts/qualify_remediation_envelope.py --native-build build/python-release --output build/private-envelope-new
```

Use a fresh output directory and existing qualified Release build; do not substitute
an ASan binary whose shadow address-space requirements exceed this measurement cap.
Run the regular sanitizer regression separately. Current scalar-IV diagnostics,
archive-scale journal redesign, global quotas andhot lossless recovery are separate
contracts; this sprint does not silently introduce them. Research restart loss/time,
backup/rollback drills on the actual target and provider/retention permissions remain
open. Replayed supplied prefixes are not exchange-complete or crash-safe hot books.
