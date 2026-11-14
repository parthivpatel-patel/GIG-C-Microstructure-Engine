# Bounded statement-vintage exports

`terminal.stocks.xbrl_vintages.company_vintages(workspace, symbol, cutoffs, role=...,
form='10-K', expected_collection_sha256=...)` exports one independently selected
Company-v2 packet per authored acceptance cutoff. One to eight strictly increasing
instants are required; equivalent-offset duplicates and reversed cutoffs reject
before selection. An optional collection identity rejects stale requests. Total
canonical output is bounded to256KiB, matching the offline frontend file budget.

The contract `gig.backend.company_xbrl_vintages.v1` preserves each child's exact
source, units, periods, acceptance cutoff, missingness, conflicts and signed identity.
It does not combine filings or use an older statement to fill a newer missing role.
Amendment links remain explicit and non-additive. Same-time competing filings remain
ambiguous. Source transitions describe selected accession changes, not inferred
accounting restatement meaning. No name/order/value similarity becomes equivalence.

The existing Stock Intelligence supplied-XBRL panel accepts this private offline
export using its existing file control and exposes a named acceptance-vintage
selector. Every child and envelope is verified before display. Issuer, collection,
cutoff, order, form, role, previous-accession and transition bindings are checked;
failed or stale loads cannot keep a previous bundle selectable. The live/read-only
single-cutoff API and existing v1/v2 packets remain compatible. There is no new HTTP
acquisition, background task or provider request.

Eight Python fixtures exercise original/amendment boundaries, missing role and
same-time ambiguity, exact nanoseconds, stale/output budgets, unknown collections
and deterministic identity. Actual Python-to-TypeScript admission verifies three
vintages and rejects six tampered/mismatched exports, including tampering with a
nested signed child after resigning only the outer envelope. Automated build and
contract verification do not establish browser/device or owner acceptance.
