# Remaining work and revised effort

No confirmed open P0 defect remains from this bounded review. This is not a proof of global absence. Repaired P1/P2 issues and exact acceptance scopes are in P0_REMEDIATION_REPORT.md and the 29-row matrix.

## Code work still justified

1. **P2 bounded damaged-database admission (R06): 2–4 active hours.** ObservationStore.recover currently fetches rows before checking 10,000 count. Consider LIMIT 10001 and preflight payload/type counts; add over-capacity/oversize/corrupt-counter fixtures before changing it. Existing database-size bounds/default-disabled retention remain; do not claim a reproduced unlimited-ingestion defect.
2. **Release/operator reproducibility: 1–2 hours.** Bind actual deployment receipt, safe upgrade/rollback instructions and target artifact inventory to the delivered SHA. No branch merge or automatic deployment is authorized.
3. **Conditional repairs only:** Any defect reproduced during target/soak/advisory qualification needs a scoped regression and repair. Do not preemptively replace the journal, introduce new services or add speculative models. The 1,223 MB theoretical 100,000-record storage scaling justifies a separately benchmark-gated equivalence plan if a required workload exceeds current budgets; not an optimization in this sprint.

## Additional automated tests

- **Realistic bounded soak/slow-consumer/cancellation: 3–5 active hours**, plus declared execution windows. Test deployed 250 ms projection cadence, four symbols, bounded worker/client counts, reconnect churn, storage exhaustion, stop/restart and source-accounting consistency. The 512-event microbenchmark is not a session soak. Freeze inputs/reference outputs and measure memory plateaus; do not invent an arrival-rate SLA.
- Current target clean source/wheel/native ABI, security dependency and operating-system advisory review: **2–4 active hours**, remediation contingent on actual findings. Pins/pip check do not prove security clearance. Preserve warnings/tests and install no paid service.

**Revised scoped engineering estimate: 8–15 active hours** (the four packages above), not a blanket 40–80 hour product estimate. Add **0–8 hours contingency only if concrete qualification defects are reproduced**. The independently actionable recovery/soak portion is 5–9 hours; target-dependent artifact/advisory portions are 3–6 hours and require their access/evidence first. These are relative implementation/testing estimates, not calendar promises or a guarantee of institutional readiness. Market windows, owner availability, CI queues, data rights and additional findings are excluded.

## Environment-dependent verification

| Gate | Required evidence | Current blocker |
|---|---|---|
| Actual IEX/history |Owner-account permitted bounded probe with accepted nonempty source receipts and honest quiet/empty results|No keys/private owner environment available in this task;zero provider attempts|
| Private Codespaces |Exact deployed SHA/native/assets;private authenticated HTTPS/WSS and owner browser review|Actual owner edge/device not accessible here|
| Native ARM64 |Current-SHA six configurations, eight identities, Python/artifact consumers on genuine AArch64|No native hardware/sysroot;older runs/fragment cross object are insufficient|
| Runtime/security |Target OS/package/advisory clearance and reviewed artifacts|No fresh external advisory or target-machine patch evidence|
| Storage durability |Provisioned private root and target filesystem operational failure acceptance|Mock fsync/process exit is not a power cut or hardware RPO/RTO proof|

## Owner-only actions

Use the already supplied `docs/qualification/PRIVATE_IEX_RUNBOOK.md` after final engineering is accepted. Preserve existing changes/configuration, fetch/switch/pull only this development branch and build locked dependencies/assets. No keys/contact values need to be pasted into chat. Keep 8787 Private. Keep paper and legacy live-execution flags 0; run only the explicit read-only profile.

When an exclusive account stream window is available, run the bounded qualification command, then the private launcher. Record returned stage classifications and actual source/private-edge/browser evidence. Separately authorize a free-eligible manual ARM64 run against the exact delivered SHA. This task did not dispatch it. Expect roughly 1–3 hours of owner-operated qualification/review, plus market/CI/environment waiting that cannot be estimated here.

## Provider/licensing boundaries

The owner-reported Alpaca Support #384778 permission covers personal noncommercial owner-only private Codespaces IEX research, not public redistribution, business use, paid feeds or trading. Actual provider plan/schema/units/freshness remain to be qualified. SIP stays disabled in the narrow launcher; its existing 900-second check is fixture-tested. Observed retention/export stays disabled unless separately selected and reviewed; no NASDAQ/LOBSTER input was accessed. Complete observed L3 validation needs independent complete initialization/order-level evidence and is not supplied by IEX L1.

## Recommended Sprint 2

Execute the scoped recovery-admission and sustained-workload packages, close current runtime/artifact/ARM/private-edge evidence when available, and repair only reproduced failures. Preserve all 12 workspaces / 15 modes and the existing architecture. Do not turn this into another UI redesign, broker activation or feature-count project. Institutional production readiness remains **NOT ESTABLISHED** until the appropriate evidence exists.
