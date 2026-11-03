# Reliability qualification — actual outcomes

Implementation `11f1e9cfe6898970461855829650220a9e57bb5d`, Linux x86_64. Real provider/account/order calls:0. Paid resources/workflow dispatches:0. All inputs are authored fixtures or existing deterministic native tests. Native/UI/execution source remains unchanged.

| Python cohort | Debug | Release | ASan+UBSan |
|---|---:|---:|---:|
| New hardening/fault/oracle |29|29|29|
| Existing final read-only qualification |35|35|35|
| Sprint4 history/research/paper |96|96|96|
| Sprint3 fake paper/risk/recovery |52|52|52|
| Sprint 2 backup/recovery/evidence |30|30|30|
| Stocks/live/projection/persistence |207|207|207|
| Terminal/native API/security/financial |274|274|274|
| **Executed total** |**723**|**723**|**723**|

**2,169 main-matrix Python outcomes plus9 separately refreshed workflow-policy outcomes; zero final failures/errors/skips.** After the backup repair only the new 29 and affected Sprint 2 backup 30 cohorts were refreshed; unchanged successful cohorts were retained. Earlier24-test logs remain archived. No failed test was deleted or assertion weakened.

| Other check | Actual final result |
|---|---|
| GCC native Debug/Release/ASan+UBSan CTest |158/158/159;475 total; zero failures/skips |
| Eight frozen native identities |8 in each configuration;24 unchanged comparisons |
| Frontend Node tests |118/118;zero failures/skips |
| Strict TypeScript/production build |PASS;22asset files byte-identical to redesign |
| Actual browser programs |GIG 10 / native 21 / recorded L2 playback 9 checks;3programs exit0 |
| Source packaging patterns |3/3 including negative controls |
| Actual source archive |1,129 safe intended byte-identical members at the core implementation checkpoint; later CI/doc-only closure excluded |
| Runtime consistency |pip check:no broken requirements |
| Correctness-gated performance |8native cases+independent two-symbol reconstruction+Python replay+projection oracle |

## Failure boundaries tested

- Four FIFO-backed reads reject in bounded subprocesses; API catalog returns a rejected entry instead of leaving a waiting reader.
- Duplicate/nonobject/deep/oversize manifests and duplicate event keys reject; byte corruption cannot masquerade as accepted source.
- ENOSPC/fsync failures before rename publish no target. Staged directory and parent publication syncs are observed.
- Abrupt process exit before rename leaves only an explicitly unaccepted pending directory; after rename, restart validates the existing finalized recording. This is not a real power-loss test.
- Post-rename parent-sync failure returns uncertainty and retains valid data; retries refuse overwrite. Backup follows the same acknowledgment rule; failed stage sync preserves the original live SQLite database.
- Existing backup restart/interruption/internal-corruption controls pass. Existing observation-store abrupt exit, chain corruption, capacity/retention and concurrent publication checks pass.
- Existing provider tests cover duplicates/out-of-order/stale data, frame atomicity, disconnect, quiet feeds, bounded retries, rate limiting, cancellation and source isolation. New benchmark negative controls deliberately corrupt a projection sequence and verify oracle rejection.
- Existing Origin/Host/endpoint proof, source permissions and execution-disabled tests remain. No browser forced click is used. The new API fixture was corrected to use the configured loopback host after the original untrusted TestClient host was properly rejected.

## Commands and scope

Actual commands/environments and log digests are stored in EVIDENCE.json. The matrix runner used the existing pinned `/workspace/gig-terminal-clean-venv` and native Debug/Release/sanitizer builds; those absolute paths are execution evidence, not required owner paths. Reproduction entrypoints:

```bash
.venv/bin/python terminal/tests/run_production_hardening.py
.venv/bin/python terminal/tests/run_final_qualification.py
.venv/bin/python terminal/tests/run_remediation_sprint2.py
.venv/bin/python terminal/tests/run_native_suite.py --expected-tests 274
npm --prefix terminal/web test
npm --prefix terminal/web run build
```

Configure the validated native module path/build and offline socket guard for each configuration; do not simply set ASAN_OPTIONS on an uninstrumented binary and call it sanitizer qualification. Native CTest source was unchanged, so existing-source builds were rerun rather than rebuilt. Python ASan uses the prior native-binding launcher and live LSan checkpoint 0 with shutdown leak checking disabled; no new shutdown leak certification. No new Clang/native ARM64 runtime qualification was executed.

The existing browser automation ran against immutable finalized assets and actual native loopback service with provider gates0, private temporary storage and software Chromium. It is not owner GitHub authentication, physical Android/Safari or live-source evidence. Previous local HTTPS/WSS 20 checks and comprehensive SEC 142 checks remain source-bound historical evidence from 3cc7581; they were not relabeled newly executed here because their code paths did not change.

## Outstanding acceptance

Actual owner private edge, current native ARM64, live/historicalIEX, target dependency/advisory clearance, realistic long-duration/slow-source/consumer soak and actual filesystem power-loss behavior remain pending. No RPO/RTO, corrected-tape completeness, hot L3 recovery or source-loss percentage is claimed. Initial storage-root provisioning and hostile shared-filesystem races are outside these specific process-fault tests.

The CI-only follow-through commit adds the29-test cohort to the existing owner-gated GCC Release ARM64 step. One new assertion failed before that line existed; all3 workflow-policy cases then passed in Debug/Release/ASan+UBSan (9overlapping outcomes). Existing six-job/manual/free-owner/hash guards were preserved. No workflow was dispatched.
