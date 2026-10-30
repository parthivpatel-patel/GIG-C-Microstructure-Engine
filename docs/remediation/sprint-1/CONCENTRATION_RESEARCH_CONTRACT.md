# Proposed supplied-depth concentration v1

Historical requirement: original unified terminal directive (audit source H02),
§16 lines542–553 and §26C, explicitly requests “Liquidity concentration”. No
estimator, normalization, units or approval of HHI was recovered. The original
complete C++ master remains unavailable. **The original definition/acceptance is
OPEN. This implementation is an explicitly proposed research metric, not an
assertion that HHI was historically approved.**

`gig.research.supplied_depth_concentration.v1` is a read-only, non-mutating extension
in `terminal/server/concentration.py`. It consumes an owned native/aggregate depth
observation; it never invents orders, mutates the native book or upgrades provenance.
Default state projection: both sides, up to10 supplied levels per side.
`GET /api/v2/research/concentration?side=both&depth=10` also permits `bid` or `ask`,
and integer depth1–20. Duplicate/unknown query parameters reject. The existing
state schema retains its native metrics unchanged and adds `research_metrics`.

For n selected side/price buckets with quantities q(i)>0 and Q=Σq(i):

```text
HHI = Σ(q(i)/Q)^2
normalized_HHI = (n*HHI - 1)/(n-1), if n>1
normalized_HHI = 1, if n=1 (explicit single-bucket convention)
```

- Units: dimensionless quantity concentration, not price/notional/ownership risk.
- Equal selected quantities give HHI1/n and normalized0. One positive bucket gives1.
- Both-side selection treats bid and ask levels as distinct buckets. No order-level
  or market-wide distribution is inferred. Uniform quantity scaling cancels.
- Validate ordered, unique positive signed-int64 prices and uint64 quantities;
  at most20 supplied levels per side. The selected prefix may be shorter than
  requested. `requested_depth_populated` and available/selected counts disclose it.
- Partial depth can produce `AVAILABLE_SUPPLIED_SUBSET`; it cannot establish a full
  book. Comparisons require identical side/depth/coverage conventions.
- Empty selection, all-zero denominator, a zero level mixed with positive levels,
  malformed/out-of-budget levels and unavailable source have explicit distinct
  unavailable outcomes. No zero, missing or malformed level is silently dropped.
- Arithmetic uses exact bounded Python integers/Fraction (≤40 uint64 quantities;
  total<2^70 and denominator<2^140). Wire values are numerator/denominator strings.
  This is postprocessing of native snapshots, not duplicate book-transition logic.
- Provider, instrument, origin, revision, position, available timestamps, dataset,
  fixture/recording identity and clock parents remain attached. Unknown values stay
  null. No synthetic-to-observed relabeling or exchange completeness claim.

Independent tests use hand-calculated rational answers and256 independently
calculated Decimal cases, asymmetric selections, partial/empty/zero states,
40maximum quantities, invalid formats/budgets, provenance, HTTP/native-state
isolation and source unavailability. The browser labels it PROPOSED RESEARCH v1,
with exact details and a supplied-depth-only warning. Original A19 remains PARTIAL
pending an explicit definition/acceptance decision.
