# Requirements status overlay

Original176-row audit is preserved on `67ad42d08daf45d8c523c733587cdbd88852b81d`. This overlay lives only on
`fix/atlas-audit-remediation-1`; it does not rewrite that audit ormodify the release
branch. Machine-readable full rows:[REQUIREMENTS_STATUS.json](REQUIREMENTS_STATUS.json).

| Status | Rows |
|---|---:|
| BLOCKED_EXTERNAL_DEPENDENCY | 11 |
| IMPLEMENTED_AND_VERIFIED | 139 |
| IMPLEMENTED_NOT_FULLY_VERIFIED | 7 |
| NOT_APPLICABLE | 6 |
| PARTIALLY_IMPLEMENTED | 11 |
| UNKNOWN_REQUIREMENT_EVIDENCE | 2 |


Changes:OPT-03 options boundary→bounded verified; UX-12 applicable risk/model summary
formatting→verified; OPS-16 historical documentation clarity→verified; QUANT-13 missing
concentration→PARTIAL with an explicit research proposal. The historical metric
acceptance remains unresolved. No permission, universal-history orproduction
qualification row is promoted to PASS. Remaining unknown source rows stay UNKNOWN.
