# Dataset and initialization provenance

Machine-readable schema contract `gig.market_initialization.v1` is implemented by
`scripts/check_initialization_manifest.py`; checked authored example is
`tests/fixtures/market_seed_manifest.json`. Exact required field set prevents silent
ignored policy fields. Fields include provider, dataset, origin, instruments
(locate/symbol/native instrument), optional Gregorian session date, source SHA256,
capture start/end, initial-state source, snapshot SHA256, completeness declaration,
verification method, event boundary, optional sequence information, missing-data
flag, license/redistribution references, declared validation status, complete seed
orders/retired IDs/matches, lifecycle stage and optional last wire timestamp.

License references identify external evidence; they do not grant rights. `observed`
is never relabelled synthetic. Authored fixture date is explicitly fictional.
Actual observations require authorized publisher/source chain, private retention
controls, source integrity and separately verified initialization/reference evidence.
Public access and an unkeyed SHA256 do not prove upstream completeness or publication
rights. No market-data bytes or acquisition occur in this phase.

Canonical snapshot digest is SHA256 over UTF8/ASCII-escaped compact sorted-key JSON,
orders sorted by reference, retired IDs numerically sorted, matches sorted by number.
Priority/arrival ranks are retained explicitly. Capture source hash is separate
from snapshot hash; no hash of a subset is labelled whole archive integrity.
Field validation precedes eligibility. Unknown input stays context-only. Observed
verification is explicitly unimplemented even if every declaration looks complete.

Example (synthetic only):

```sh
python3 scripts/check_initialization_manifest.py tests/fixtures/market_seed_manifest.json
python3 tests/test_market_initialization.py
```

The first command exits1/context-only without separately supplied trusted digests;
this is expected. `--trusted-source-sha256` and `--trusted-snapshot-sha256` bind an
independently controlled fixture expectation; they cannot enable observed L3.
Corrupt JSON/schema/state exits2. Positive synthetic eligibility exits0. Store input
manifest, its hash, trusted expectation provenance, exact seed boundary and errors
with every comparison. Do not publish restricted payloads in divergence reports.
