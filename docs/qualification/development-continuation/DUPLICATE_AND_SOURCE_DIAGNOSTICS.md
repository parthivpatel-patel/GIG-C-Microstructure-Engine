# Duplicate accuracy and source-ingestion observations

The existing conservative source-value policy is preserved. DUPLICATE_ACCURACY_DIAGNOSTICS_V1
adds explanations,not a new fact-selection algorithm:identical values,overlapping
or touching accuracy,disjoint accuracy,unknown accuracy,nil-only and mixed-nil
conflicts are distinct. Differing values remain unavailable even when enclosures
overlap. No averaging,most-recent-row or nearest-value rule is inferred.

Original fact IDs,reported values and supported closed enclosures remain visible.
The utility reuses bounded exact accuracy admission (8facts,finite supported grid,
no float math). V2rows expose an optional duplicate_diagnostic field. Existing v1
and v2numeric semantics/source facts are unchanged;missing/unsupported scope stays
unavailable. Browser admission binds diagnostic references to derived/original facts
and rejects a reported substitute in a conflicting row.

Optional source_ingestion observations contain coordinator state,retained counts,
last HTTP code,fixed error codes and exact decimal-string process counters. They
contain no request headers,contact values,credentials or raw bodies. An explicit
installed_collection_matches flag binds coordinator and displayed collection SHA;
a newer accepted source is not silently described as already installed. These are
export/cache observations,not current live connectivity,source authenticity or
complete provider-source accounting. Frontend labels state this distinction.

The actual offline Python→TypeScript checker now includes the fixture ingestion→
DTS→collection→company→client path alongside prior accuracy/extension cases.
It passes11cases/65assertions;the existing v1checker remains separate. 6new authored
duplicate cases and2frontend cases cover overlap without selection,disjoint/INF,
negative/zero,nil/unknown,unchanged source IDs,sanitized counters and mismatch guards.
No application,browser,provider,retention gate or trading capability is activated.
