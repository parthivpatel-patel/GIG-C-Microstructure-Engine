# Bounded supplied SEC/XBRL instance research

Implemented source:`terminal/stocks/xbrl_instance.py`,`xbrl_collection.py`;offline entry point:`scripts/inspect_xbrl_instances.py`. This is an additive supplied-file research path. It does not issue SEC requests,replace the existing companyfacts APIs,start GIG,or enable observed-data persistence.

## Instance admission

The strict profile reads UTF-8 XBRL2.1 instance XML using expanded namespace names. Contexts preserve exact issuer CIK,instant/duration/forever periods,explicit/typed dimensions and opaque segment/scenario content. Units preserve numerator/denominator measures. Facts preserve exact lexical values,nil,decimals/precision,context/unit identity,source ordinal and source fact hashes. DTDs,entities,processing instructions,XInclude,inline HTML,malformed references,duplicate IDs and unsafe source URLs are rejected. External schema references are retained but never fetched.

Selected consolidated financial facts require the existing selected US-GAAP concepts,explicit matching unit/period profile and no dimensions/opaque segment. Conflicting exact values are excluded;consistent duplicates retain their individual source IDs. Unknown concepts are retained as unverified. No tolerance interval is inferred from decimals/precision. Expanded namespace-qualified concepts remain in source lineage;different taxonomy versions are not silently collapsed into one vintage by local name. Selected ratios use the existing exact period-aware financial implementation,not new floating-point calculations.

The caller-supplied concept profile is a declared input contract,not DTS authentication or proof that an SEC taxonomy version has been independently verified. Selected namespace/name/unit/period mappings cannot be changed inconsistently. Extension concepts do not become financial metrics merely because their local names resemble a selected tag.

## Filing batches and point-in-time selection

`FilingCollection.ingest_batch` prepares every supplied instance before replacing the immutable accepted collection. Same-accession conflicting contents,source/issuer mismatch,cycles and contradictory declared amendment lineage reject the entire batch. Identical retries are idempotent. Missing amendment targets remain unresolved;none are guessed. Pagination is bound to the collection hash,so stale cursors cannot silently cross collection revisions.

`at_acceptance_time` uses exact nanosecond acceptance metadata and filing-date boundaries. Unknown acceptance is excluded;receipt/filing midnight is never substituted. Latest eligible fact per expanded concept/period/unit is selected. Equal-time conflicts are excluded. Amendments remain separate source accessions and are not added to original statements. Source receipts remain supplied values or null. Fiscal years/quarters are not inferred from calendar dates. Fact exclusions,per-input truncation,output truncation,unresolved amendment links and source manifests accompany results.

Bounds:2 MiB per XML input,depth32,30,000 nodes,512 contexts,128 units,4,096 facts/unsupported nodes,8 MiB parsed output;8 files/8 MiB raw input per batch,32 retained filings,16 MiB collection payload;page size8;256 selected periods per metric,with explicit truncation. The existing selected-financial converter's256-current/16-revision limits are disclosed in input coverage. These are bounded research contracts,not full-universe or complete-history guarantees. Caller owns serialized collection access;there is no background worker or persistence in this module.

## Offline command

Use only a copy whose processing is authorized. The batch JSON has exact fields `schema`=`gig.sec.xbrl.input_batch.v1`,`issuer_cik`,`origin`,`entries`. Each entry has relative `path`,`manifest`,`gaap_namespace`. Paths may not escape the batch directory or follow symlinks. The manifest fields are:

```
issuer_cik,accession,form,filed,accepted_at,received_at,origin,
source_sha256,source_url,amends_accession,permission_reference
```

CIK is10 digits;accession is the exact SEC accession;unknown acceptance/receipt/amendment target is null. `origin=HISTORICAL_SYNTHETIC` is for independently authored fixtures only. An actual official response requires a separately approved supplied copy,`origin=OBSERVED_OFFICIAL_RESPONSE`,the exact official archive URL and a permission reference;the tool additionally requires `--allow-observed`. That flag is not a grant of rights or a provider authorization bypass. Permission references are hashed in outputs. No observed input was processed in this sprint.

```bash
PYTHONPATH=. .venv/bin/python scripts/inspect_xbrl_instances.py --batch <private-directory>/batch.json --as-of <UTC-acceptance-cutoff> --output <private-directory>/selection.json
```

The stdout summary contains counts/hashes/classification,not raw XML or financial rows. Optional full selection output is private0600,exclusive-create and never overwrites an existing result. Keep inputs/outputs outside tracked source. Failures exit2 with bounded safe categories. Inputs are not copied or newly retained. No application,server or provider connection is needed.

## Executed validation and remaining scope

32 tests:16 parser,12 filing collection and4 offline-tool cases. All passed with GCC Debug/Release/ASan+UBSan and Clang Debug/Release native environments. Coverage includes malformed/oversized XML,entity attacks,namespace/units/period integrity,unknown concepts,dimensions,nil,exact conflicts,source scope,atomic failed batches,idempotency,amendment/cutoff ordering,unknown receipts,stale cursors,symlinks/path traversal,private output and error redaction. Authored fixtures only;no real SEC or restricted LOBSTER data. Full no-launch cohort includes174 tests;the final namespace-lineage/CLI diagnostic refinements were checked by the32 affected tests in all five environments after the broad run.

Still missing for full SEC02:full DTS/schema/type validation,inline-XBRL transformation,extension-taxonomy semantics,presentation/calculation relationships,complete statement construction and comprehensive historical instance acquisition/vintage receipts. The current UI/v2 companyfacts path remains unchanged and is not relabeled as full XBRL statements. These residual components are engineering work as well as source-coverage requirements,not all external blockers. The bounded instance reader and offline selection/export are working infrastructure,not completion of the entire XBRL standard or empirical provider qualification.
