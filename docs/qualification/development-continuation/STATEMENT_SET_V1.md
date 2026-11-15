# Acceptance-selected source statement sets and historical cutoffs

`company_statement_set(workspace,symbol,as_of,dts_graphs,role_bindings,*,form='10-K',
expected_collection_sha256=None)` returns `gig.backend.company_statement_set.v1`.
`company_statement_history(...,cutoffs,...)` returns independent views under
`gig.backend.company_statement_history.v1`. Both are explicit offline APIs with no
new HTTP route, source reads, activation or legacy/default changes.

For each accession the caller explicitly designates three distinct presentation
roles (or null): balance_sheet, income_statement and cash_flow_statement. These are
caller designations, not inferred statement classification, certified GAAP roles or
accounting equivalence. No role name, presentation proximity, concept local name or
numeric resemblance creates a mapping. The source facts, exact expanded concepts,
declarations and effective presentation/calculation relationships are independently
bound to the selected original DTS. A designated role missing in that filing stays
unavailable; no older filing role is substituted.

Authority for the existing source relationship and context behavior: XBRL2.1
Recommendation31December2003 with corrected errata20February2013, contexts/units
sections4.7/4.8 and relationship sections5.2.4/5.2.5:
https://www.xbrl.org/Specification/XBRL-RECOMMENDATION-2003-12-31+Corrected-Errata-2013-02-20.html
Presentation describes source structure, not accounting equivalence. Existing V2
closed reported-accuracy diagnostics are retained without claiming full Calc1.1.

Selection reuses exact nanosecond acceptance and form-family rules. Competing latest
filings remain ambiguous. Every explicitly supplied amendment ancestor must resolve
at the cutoff; amendments replace the selected whole filing rather than fill or add
to earlier cells. Unknown acceptance, missing current graph or role bindings remain
unavailable. A resolved supplied chain is not complete history or a proven accounting
restatement. Historical cutoffs strictly increase; each carries its own immutable
source/lineage/role identity. SOURCE_CHANGED is not an inferred restatement label.

Original source IDs, lexical values, units and contexts are retained. Source-bound
extension numeric values remain separate derived records, with accounting_metric
null. Historical comparative periods remain separate exact start/end rows; no fiscal
quarter is inferred. Nil, zero, absent, conflicting duplicates and ambiguous units
remain distinct. Dimensioned/default-dependent/opaque facts are not promoted into
consolidated rows. All three available source views still have complete_statements
false. Completeness of a GAAP financial statement cannot be established from this
bounded source structure alone.

Full supplied graph and parsed artifact identities, original fact identities,
context/unit hashes, effective relationship provenance and declaration document
membership are rechecked. Fresh declaration corroboration replaces abbreviated
retained proof for derived view construction; the outer parsed_sha256 always names
the admitted original artifact. Child selected_instance_sha256 identifies the
revalidated derived artifact. Integrity hashes do not independently authenticate
issuer sources. Definition/default networks and unknown graph semantics remain
outside this consolidated profile and fail closed.

Limits:32filings/maps,16DTS documents,4096facts/arcs,512contexts,128units;
existing128concepts/8duplicates/12periods bounds apply. Period truncation rejects
rather than presenting incomplete coverage as accepted. Output1MiB,history8cutoffs/
2MiB. No mutation of admitted collections or graphs occurs. Legacy statement,
company-v2,SDK and native contracts remain available unchanged.

Sixteen adversarial tests cover three authored issuer roles, exact signed sums,
source IDs and periods, comparative missing cells,nil/zero/conflicts/units,whole
amendment selection,missing graphs/roles,latest ambiguity,unknown/future acceptance,
stale/corrupt sources,bounds,history order/transitions and legacy immutability.
The authored corpus is synthetic protocol evidence, not observed issuer validation.
