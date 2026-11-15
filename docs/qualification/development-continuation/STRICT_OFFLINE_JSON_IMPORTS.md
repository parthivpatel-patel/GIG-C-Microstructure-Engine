# Strict private financial-export JSON ingress

A reproduced boundary defect affected the offline file inputs in XbrlStatements and
SourceCalculations: JSON.parse silently kept the final occurrence of duplicate
member names before any artifact hash/lineage check. A contradictory earlier schema
member, including an escaped alias for that name, therefore disappeared before
verification. Six actual authored calculation/statement/vintage exports reproduced
this behavior while still passing their existing digest and semantic validators.

The new shared `offlineJson.ts` ingress checks JSON syntax and bounded structure
before constructing its object graph. It rejects duplicate decoded member names at
any object depth, including escaped aliases; legal equal names in separate objects
remain independent. It also rejects unsafe/fractional/nonfinite JSON number values,
which cannot represent the integer metadata contract of these private exports.
Reported financial decimals, exact rational components and other exact quantities
remain strings and are unchanged. Review also exposed a precision trap in the first
integer guard: Number conversion can round a fractional lexical such as
1.0000000000000001 or9007199254740991.1 to a safe integer, and underflow can become
zero. The final guard checks the original bounded coefficient/exponent with BigInt
before any Number conversion; regressions retain these exact rejected forms. The helper does not interpret financial semantics,
validate source identity, rewrite keys, normalize text or replace the existing
statement/calculation/vintage validators.

The file reader checks the browser Blob's declared size before reading and verifies
its actual buffer length. UTF8 decoding is fatal: malformed bytes cannot be replaced
silently before hash admission. A browser UTF8 BOM retains the previous file-reader
behavior. Exact-source values and authored arrays survive. Optional abort checks
before and after file reading prevent stale statement imports from being parsed;
existing component generation fences still prevent stale UI publication. No
application, API, socket, transport, provider permission or storage is introduced.

Bounds are256KiBUTF8input,32nesting levels,40,000values/member names,16,384UTF16
units per decoded string and128characters per JSON number token. Numeric exponents are bounded to±128. Before native Number decoding, a bounded
BigInt coefficient/exponent calculation requires exact integrality and the safe-integer
range; rounded fractional lexicals and underflow cannot masquerade as integers.
Number values must be exact safe integers; source-specific exact numbers stay string-encoded. Lexical scanning
uses a depth-bounded descent and a sticky number scanner, without repeatedly slicing
the remaining input. No global browser/process RAM or arbitrary hostile JavaScript
Blob-implementation guarantee is claimed. Native browser Blob.size bounds the retained
input buffer; all application values are still checked by their existing contracts.

Eight frontend tests cover valid exact strings/arrays, root/nested/escaped duplicates,
malformed grammar, integer precision/nonfinite values, text/byte/depth/node budgets,
prototype-shaped names as inert data, malformed UTF8/size mismatches and aborts.
The actual Python-to-TypeScript ingress contract exercises six existing exports,
proves all six ambiguous forms passed the previous parser boundary, then rejects
12plain/escaped duplicate variants with the strict parser. Existing full source
contracts continue to run after ingress. SourceCalculations' accessible control,
error alert, loading status and stale-result fences are preserved.

Reproduction (offline developer checks; no application or server):

```
node --experimental-strip-types --test terminal/web/src/offlineJson.test.ts
PYTHONPATH=build/recovery-release/python:. work/venv/bin/python terminal/tests/check_offline_import_contract.py
cd terminal/web
npm test
npm run build
```

This closes a demonstrated ambiguous-JSON admission defect. It does not establish
source authentication, standards completeness, vulnerability clearance, complete
statements, exhaustive WCAG or physical assistive-technology acceptance. No dependency
version or permission is changed.

Recovery continuation also rejects numeric negative-zero metadata (-0,-0.0,-0e12):
its sign cannot survive canonical JSON integer interpretation. Reported financial
strings such as "-0.00" are preserved byte-for-byte as strings. Nine focused parser
checks and the six-export ingress contract now retain23adversarial rejections,
including invalid calendar periods/acceptance,cutoff/sourcehash mismatches and exact
lexical fractional,unsafe,underflow and signed-zero metadata cases. Existing valid
legacy statement,vintage and calculation exports remain admitted. Dimensional
artifacts are separately validated in the Python dimensional-report corpus;the
existing browser has no new dimensional-report import mode.
