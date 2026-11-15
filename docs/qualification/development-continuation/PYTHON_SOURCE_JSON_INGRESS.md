# Explicit Python source-sensitive JSON ingress

The source-sensitive readers already shared duplicate-key rejection in
`terminal.verification.artifacts.decode`; that rule is retained, including decoded
escaped-name aliases. This package adds an explicit `numeric_policy='exact-integer'`
for SEC metadata/index/checkpoint decoding and the offline XBRL batch-manifest CLI.
It does not silently replace every JSON reader's numeric behavior.

The selected policy parses original numeric lexicals before any float conversion.
Exact coefficient/exponent arithmetic admits mathematically integral values,
including valid integral exponent forms, as Python integers. It preserves integers
beyond JavaScript's safe range and full u64 metadata. Fractional values, underflow,
signed-zero lexicals and numeric-resource excess reject. Limits are128characters per
number token, absolute exponent128 and128digits in the resulting integer. Booleans
remain booleans. Source bodies/hashes are retained as originally received; accepting
an exact integral exponent in a directory size does not rewrite its original bytes.
Existing source/file/node/depth/request/time/retention bounds continue to apply.

The generic decoder's default remains finite-float evidence behavior. Exact provider
observations continue through the existing independent Decimal parsers in
StockWorkspace.fetch and qualify_sec_sources.decode; no float observation or exact
financial decimal is silently coerced to an integer. Reported XML/inline amounts
and rational values continue to use their original string contracts.

A concrete checkpoint source-binding defect was separately reproduced: Python dict
equality treated a normalized source amendment boolean false as equal to numeric0.
A recomputed checkpoint using that replacement restored successfully before repair,
without source transport. Source-row binding now compares canonical JSON bytes,
and adjacent current/sharded/refresh metadata comparisons do likewise. A boolean
cannot become a numeric alias of its original normalized source row. The failing
receipt is work/python-ingress-metadata-alias-before.json; final regressions require
rejection and unchanged accepted checkpoint state.

Four historical-source JSON loads also lacked duplicate-key hooks despite checking
caller/self-derived byte revisions. HistoryStore.read, datasets.analyze_revisions,
history_backup._validate and the backup manifest restore reader now reuse the
existing duplicate-aware finite-float decoder. A matching SHA does not make an
ambiguous JSON object acceptable. Valid private snapshots, backup/restore and
fractional retention clocks retain their prior behavior. No new persistence or
retention is enabled.

## Reviewed ingress inventory

| Boundary | Policy after this package |
|---|---|
| SEC filing submissions, historical shards, directory and version1–4 checkpoints | Existing duplicate/UTF8/finite/structure checks plus explicit exact-integer lexicals; canonical typed metadata binding |
| inspect_xbrl_instances.py XML/DTS/inline-set batch manifests | Same explicit exact-integer policy before source XML and output publication |
| Private historical revisions, selected dataset revisions, backup validation/manifest | Existing duplicate-aware finite-float decoder; original byte/SHA/retention/index validation retained |
| SEC private configuration | Existing duplicate hook and exact string/boolean schema; unchanged |
| SessionSchedule and MarketCatalog | Existing duplicate hooks and their separate bounded text/row contracts; unchanged |
| StockWorkspace.fetch and qualify_sec_sources.decode | Existing duplicate hook, Decimal and constant rejection; legitimate decimal observations unchanged |
| General evidence/deployment/sec-binding readers sharing artifacts.decode | Default finite-float policy retained; source-specific validators still apply |
| Frontend response.ts, app/SSE messages and localStorage | Outside private financial-file ingress; JSON number/response semantics were not globally replaced |
| Benchmark/native subprocess output, independently generated normalized API output in qualify_sec_sources, offline dependency metadata readers | Existing separate contracts; not represented as universally migrated or security-cleared |

No canonical in-memory clone or test fixture path was changed. This inventory is a
review of the named source-sensitive package, not a claim that every JSON parse in
the repository has identical semantics or complete security qualification.

Ten exact-metadata/source regressions plus five history-ingress regressions cover
large integers, integral exponents, fractional rounding/underflow/signed zero,
malformed UTF8 and escaped aliases, original CLI no-output behavior, source directory
admission, actual checkpoint boolean aliases, immutable failure, Decimal observation
preservation, matching-hash ambiguous history, backup atomicity and ordinary recovery.
An87-test focused cohort (including existing source/CLI/history tests) passes with
no application/socket/provider invocation. The representative provider regression
uses an injected authored fetcher only. No permissions, dependency versions, source
rights or public API defaults are enabled or changed.
