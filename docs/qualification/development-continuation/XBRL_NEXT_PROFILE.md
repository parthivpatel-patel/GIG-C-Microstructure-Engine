# Supplied inline-XBRL and DTS/presentation development profiles

Historical profile evidence below is retained. Later numeric/DTS/vintage and source-recovery packages are documented in XBRL_NUMERIC_PROFILE.md and REPORT.md;the earlier48/262case counts are not current totals.

Additive offline code:`terminal/stocks/inline_xbrl.py`,`xbrl_dts.py`. Existing strict `parse_instance` remains instance-only. FilingCollection now dispatches supplied instance/XHTML files without provider calls. All source hashes,receipts,CIKs,contexts,units,amendment/cutoff and permission requirements remain intact.

## Plain inline-XBRL1.1

The profile accepts well-formed XHTML with a single default-target ix:resources container,plain nonFraction/nonNumeric facts,and exact bounded scale/sign conversion. Original source XML SHA,lexical input,inline ID,document-order ordinal,expanded concept and transformation metadata are preserved. It uses the existing selected-fact/financial implementation. Nil is unavailable,not zero. Permission/source admission occurs before XML processing.

Transformation registries,continuations,tuples,named targets,nested fact markup,permissive HTML repair and inline1.0 are explicitly unsupported;the whole operation rejects rather than silently producing misleading financial values. No external schema or resource is fetched. This is a tested useful subset,not complete inline-XBRL or full DTS validation. The ordinary instance reader's outputs and strict rejection of HTML remain compatible.

## DTS discovery and presentation

`discover` consumes an explicit supplied-file map and independently expected instance/source hashes. It traverses declared schemaRef/import/include/linkbaseRef references with bounded depth,verifies document kind and imported namespace,and records missing supplied documents without fetching them. It retains expanded element declarations,types,period/balance metadata and source identities. Custom-type definitions/redefinition and unsupported schema semantics remain unvalidated or rejected explicitly.

For a single simple presentation extended link per role,it resolves locator IDs to supplied concept declarations,preserves exact decimal order and preferred-label roles,and checks directed cycles. Unknown locators,nonzero-priority/prohibited/unsupported arc roles and roles split across multiple links are not exposed as usable complete hierarchies. It does not invent cross-document precedence or calculate financial statements from presentation order. Structural closure is separate from XML Schema/type validation;`schema_type_validation` and `complete_statements` remain false.

Limits:16supplied documents,2MiB each,8MiB total;32instance schema roots;depth8;4096discovery edges;2048concepts;64presentation networks and4096arcs per network;16MiB output. Existing XML DTD/entity/XInclude/namespace/node/depth budgets apply. No URI is opened. Original receipt metadata remains null unless genuinely supplied elsewhere;hash consistency is not official-source authentication. Observed processing is default-disabled and needs separate explicit input authorization.

## Executed tests

48passing authored XBRL cases:32existing instance/collection/tool cases,7inline cases and9DTS cases. These include exact scaling under a2-digit Decimal context,permission-before-parser,unsupported transformations,source conflicts,namespace/document-kind confusion,missing imports,cycles,unusable split roles,unsafe XML,determinism and unchanged inputs. An initial DTS case exposed an import incorrectly admitting a linkbase as a schema;document-kind admission now rejects it. The original failing test is retained locally. A Python regex escape warning in new code was fixed using a raw string,not suppressed.

The262-case guarded developer cohort includes the48XBRL cases,62provider cases and9product-session cases alongside prior native/SEC/streaming regressions. Exact final compiler/binding runs are in the source-bound continuation evidence. No real SEC filing,Kraken/IEX payload,restricted LOBSTER input or new observed retention was used.

Remaining:full transformation registry/continuation/tuple handling,complete XML Schema/DTS type validation,extension-taxonomy semantics,equivalent/prohibited arc precedence,calculation networks,complete statement assembly,comprehensive historical source/vintage evidence and integration into the existing read-only v2 companyfacts UI. Those requirements remain PARTIAL;this profile is not substituted for them.

Final bounds:the inline reader now caps fact/trace materialization before conversion and checks the complete output including inline lineage against8MiB. Negative policy-bound fixtures verify both controls;all48affected XML tests passed again in each supported binding environment after these final guards. The initial broad262-case results remain recorded separately.
