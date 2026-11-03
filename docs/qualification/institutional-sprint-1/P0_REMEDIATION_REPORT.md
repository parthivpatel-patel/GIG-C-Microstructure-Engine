# P0/P1/P2 remediation report

No P0 defect was confirmed in this sprint. The following actual P1/P2 defects were reproduced and repaired; severity reflects the private, single-user, default-disabled retention profile. A malformed owner-local artifact is not evidence of remote unauthenticated write access.

| Finding | Before / evidence | Repair | Regression / residual |
|---|---|---|---|
| R01 P1 blocking file admission | Four subprocess FIFO cases time out in authored manifest/events, L2 load and catalog metadata | Reuse existing nonblocking descriptor reader; reject nonregular/symlink/oversize/changed files before parsing | All reject within 2 s; actual catalog stays responsive. Local disk/NFS/hardware stalls are not certified bounded syscalls |
| R02 P2 ambiguous JSON | Duplicate authored manifest accepted; array raises AttributeError | Bounded strict object decoder for manifest/events; L2 original ProviderError duplicate classification retained | Duplicate/nonobject/deep/byte-corrupt inputs reject; exact authored source remains required |
| R03 P1 publication barrier | Authored save calls no directoryfsync before returning complete | Sync staged directory, rename, then parent directory; explicit post-rename uncertainty | Stage ENOSPC/sync failure leaves no final target; process exits before/after rename classified; valid uncertain target never overwritten |
| R04 P2 directory enumeration | list(root.iterdir()) materializes every entry before eight-dataset check | Scandir+islice inspects at most8 | Twelve-entry fixture confirms8 examined and no admission |
| R05 P1 backup barriers | Two backup/deletion tests observe no directorysync | Sync stage database descriptor, manifest and publication directory; sync completed deletion | Sync failure preserves live DB; uncertain backup remains verifiable/restorable; repeat refuses overwrite |

## Failed-before record

`failing-before.log`: seven methods produce two assertion failures and five errors (four subprocess timeouts plus nonobject AttributeError). `backup-failing-before.log`: two directory-barrier assertions fail. These ignored logs are hash-bound in EVIDENCE.json. Directory scan and later fault/oracle cases add post-repair acceptance; no claim is made that every added case was executed before repair.

The final cohort has 29 methods: recording admission, finite resource scans, disk-full injection, abrupt process exits, ambiguous publication/retry, corruption, symlink/oversize/deep JSON, responsive API, backup/restore and independent benchmark negative controls. All 29 pass in Debug, Release and ASan/UBSan.

A new API test initially used TestClient's untrusted default host; existing Host validation correctly rejected it. The fixture now uses the configured loopback origin. No security assertion was relaxed. Existing L2 duplicate_json_key error class was preserved rather than changing the old regression expectation.

## Atomicity and durability limits

Before rename, failure removes only the operation's pending stage and publishes no final dataset. After rename, a failed parent fsync cannot prove persistence or rollback; the operation raises `recording_publication_uncertain` and retains the valid visible target for inspection. It never reports success or blindly retries/overwrites. Backup uses the analogous `history_backup_publication_uncertain` behavior.

A process exit test is not a power-cut test. Root-directory provisioning, storage-controller/filesystem behavior, hardware durability and simultaneous independent writers remain unqualified. SQLite native live state is not the C++ journal. No native journal, order execution, public API schema, observed-data permission or mathematical formula was redesigned. Malformed authored JSON previously accepted is intentionally rejected; valid canonical artifact bytes remain unchanged.

## Remaining critical findings

- Confirmed unresolved P0 defects: **none established by this bounded review**.
- Confirmed repaired P1 defects: R01/R03/R05 tested contracts above.
- Remaining P1 assurance gaps: actual private edge/current ARM64/provider/advisory and sustained-load acceptance. These are not converted to PASS or invented code exploits.
- P2 code opportunity R06: apply row-budget admission before SQLite observation recovery fetchall. Current database size limits and disabled retention remain safe defaults; no actual unbounded ingestion failure is asserted.

Separately, a qualification-policy assertion demonstrated that the existing ARM64 job did not yet run this new29-test cohort. The manual owner-gated job now includes it; all3 policy cases passed in each local configuration. This is coverage preparation, not a native ARM64 result.
