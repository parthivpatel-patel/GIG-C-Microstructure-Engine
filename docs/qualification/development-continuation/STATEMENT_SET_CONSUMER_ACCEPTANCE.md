# Three-role and filing-vintage consumer acceptance

New offline developer command:

```
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_statement_set_contract.py
```

The tool invokes existing company_statement_set/company_statement_history with full
original authored DTS graphs and explicit role designations. Five source-set cases
cover three available roles, an admitted numeric-proof artifact, conflicting income
facts, missing/undesignated roles and comparative missing cells. Four independent
history cutoffs cover unavailable, first available, changed amendment source and
unchanged source. The existing actual TS verifyStatementProfile consumer validates
23 child packets through its strict private JSON boundary. No UI or server starts;
Python socket bind/connect/connect_ex are forbidden by this developer tool.

Statement-set APIs return bare child views. Test-only envelopes use existing
company_contract metadata and those actual views, with their actual canonical
hashes, to exercise the unchanged v2 consumer. This does not introduce a public
statement-set wrapper validator, route, browser default or runtime schema. The
combined test-harness file is capped2MiB; each actual consumer packet independently
crosses the existing256KiB strict importer. No production import budget is enlarged.

The acceptance checks connect the admitted original parsed identity and supplied
full-DTS identity to each fresh declaration-revalidated child view. Original
parsed_sha256 and lineage receipts need not equal child selected_instance_sha256;
the latter explicitly names the revalidated derived artifact. A numeric-proof
fixture proves this intended identity split without mutating the admitted original.
All three designated roles must retain the same selected raw source, acceptance
cutoff, collection, source document hashes and relationship identity. Every numeric
source ID remains from that original filing. Caller labels are not certified GAAP
statement classifications or accounting equivalence.

The harness also checks exact nanosecond order, source-qualified whole amendment
selection, explicit ancestor links, original ancestor receipts and missingness.
Authentic later income views cannot substitute into an earlier selected filing.
Seven re-signed adversarial cases cover child/outer source mismatch, original and
role identity corruption, context identity change, ancestor substitution and an
otherwise authentic cross-vintage child. These checks use independently retained
fixture source expectations; they do not claim that self hashes authenticate issuers.

Six additional Python source-acceptance regressions test admitted-vs-revalidated
identity, fresh original graph authority over abbreviated retained role proof,
coherently rehashed changed graph rejection, missing amendment rows without older
filling, exact nanosecond/clock-alias order and caller-controlled role labels. They
add acceptance evidence without changing existing source/statement behavior.

Final focused results:22Python source/set checks pass;5source sets,4history entries,
23actual v2 child packets,1,018assertions and7adversarial rejections pass. The bounded
harness fixture is796,426bytes. Initial harness checks exposed only test-assumption
issues: the combined fixture exceeds a single private packet's256KiB ceiling, and
an unavailable designated view intentionally has empty context/unit maps. The
harness now applies the real bound per packet and explicitly checks empty unavailable
maps; no production bound, assertion or API was weakened. No new runtime source
correctness defect was found in this package. Complete GAAP statements, complete
history, source authenticity, observed issuer qualification and browser/owner
acceptance remain outside this developer evidence.
