# Supplied DTS and filing-vintage binding — November 12, 2026

`FilingCollection.ingest_dts_batch` is a new explicit offline contract alongside the unchanged strict-key `ingest_batch`. Each entry supplies raw instance/inline XML,its existing permission/source manifest,its explicit selected-concept profile,an instance URI and bounded supplied taxonomy documents with SHA-256 values. Total batch bytes are preflighted before XML parsing. No URI is fetched.

The existing source/permission gate runs before parsing. DTS discovery then uses the same instance hash/origin. Selected facts join declarations by exact expanded QName. Missing selected declarations,contradictory period types,abstract selected facts and nil facts whose declaration is not nillable reject the whole batch. The old accepted collection remains unchanged if any filing,document or declaration fails.

`xbrl_binding.py` carries document hashes,missing references,unsupported semantics,declared types and selected source-fact IDs into a versioned `SELECTED_DECLARATION_CONSISTENCY_V1` corroboration record. Existing acceptance-time exports retain it. Numeric values,unit checks,source/receipt timestamps,amendment links and original fact IDs remain intact. Unknown concepts stay unverified and unselected.

This is declaration consistency with supplied documents,not complete XML Schema,type,dimension/DRS,calculation or accounting validation. Declared custom types are retained,not inferred or relabeled validated. Structural closure alone is insufficient. Presentation order does not generate a financial-statement mapping. `schema_type_validation` and `complete_statements` remain false. Missing original taxonomy receipts remain unknown.

Eight authored binding cases cover source/graph identity,expanded declarations,period/abstract/nil contradictions,atomic failed batches,unknown concepts,permission-before-parsing,preflight budgets and backward compatibility. Together with existing instance/inline/DTS/collection/tool checks,the affected XML cohort contains59 tests. Tests use authored XML and do not establish real-provider correctness or source completeness.

The later explicit NUMERIC_VALUE_FACETS_V1 profile adds selected numeric value/restriction corroboration through the same batch and offline CLI. See XBRL_NUMERIC_PROFILE.md. Declaration-only behavior and full-schema/statement limitations above remain intact;current aggregate counts are in REPORT.md.
