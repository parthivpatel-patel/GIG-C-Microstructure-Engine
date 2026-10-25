# Terminal security review

Scope:local single-owner research application,not a public multi-tenant production
service. Default127.0.0.1:8787,one worker;explicit exact Origin for mutations/WS,
Host allowlist,restricted CORS,security headers/CSP,no-store responses.4KiB bodies /
5s read deadline,30 mutations/sec,8WS clients,2s send deadline,latest-view coalescing,
bounded native/source/history/output caps. No upload,shell command,arbitrary path,
external URL fetch,credential configuration,broker/order-submission endpoint.

Actual independent tests reject foreign/missing origins,Host rebinding,extra fields,
duplicate JSON,NaN,oversized/non-JSON bodies,unsupported operations and unknown API.
Authored child commands are whitelisted:20s/192KiB per pipe,zero user command/path.
Native L2 failure-atomic staging and checked rational math are independently tested.
Authored recorder permission gate precedes encoding and file access. Filesystem
assumes a trusted single operator;hostile concurrent directory mutation/crash-safe
storage is not proven. No arbitrary code or observed market rows enter exports.

Confirmed integration finding:full gateway sanitizer cohort passed functional
assertions but LSan reported240bytes/3 allocations. pydantic_core2.50.1 import alone
reproduced it;native import alone was clean. Candidate pydantic_core2.41.5 also
reported160bytes/2 allocations;it was not adopted. No suppression/ignored objects.
Because the gateway uses explicit bounded validation and no Pydantic models,the
runtime was narrowed from FastAPI/Pydantic to direct Starlette ASGI,retaining exact
REST/WS contracts. Subsequent full terminal cohort and live LSan checkpoint passed.
Before/after/import-only receipts are retained and hash-bound. This scopes the
finding to the tested dependency import;no general upstream false-positive claim.

Initial Vite7.1.7 audit flagged2 dependency findings. Updated pinned Vite8.3.5 and
plugin-react6.1.2;current npm audit reports0. Python lock16 installed versions matched
bounded TLS PyPI version metadata with0 reported advisories. Dependency inventory
records licenses/integrity. These registry snapshots are not exhaustive security
proof,source audit,OS/kernel review or legal approval. Existing project provider /
release risk registers remain;no unrelated risks are accepted by this work.

Private authenticated port forwarding needs separate platform/account configuration;
no verified external URL or physical Android/network penetration test. Origin/Host
checks are not Internet authentication. Do not expose this service publicly or use
multiple workers for shared mutable state. Manual ARM workflow stays owner-gated;
all pushes use[skip ci],no workflow launched. No main/data/broker/paid-service changes.

Additional reviewed native diagnostic defect:aggregate L2 labeled an older sequence
as duplicate instead of regression. A new exact-code/unchanged-revision assertion
failed before the fix;the minimal split (< regression,==duplicate) repairs reporting
without accepting stale input or changing valid arithmetic/replay outputs. The full
nine-configuration matrix is rerun for that final native change. Existing L3 engine
semantics are untouched. Frozen receipt verifiers continue validating their original
explicit historical profiles;current terminal evidence separately requires155 native,
158 Python and159 Python-sanitizer outcomes,including market_data.aggregate_depth.
