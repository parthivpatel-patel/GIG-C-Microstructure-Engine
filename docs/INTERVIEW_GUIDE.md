# Defending the design

Why one owner? Deterministic transitions, explicit ordering and staged commit make
replay auditable. Parallelism would complicate timestamp ties and resource lifetime;
there is no measurement justifying it. TSan is not evidence needed for absent threads.

Why standard containers? Ordered price maps give O(log L) levels, FIFO lists stable
priority and a hash index expected O(1) IDs, O(N+L) memory. This baseline makes failure
safety reviewable. Intrusive pools/dense ladders are alternatives only after profiles
justify complexity. Hash worst case remains linear. Book and replay atomicity are
logical-state guarantees; allocator capacity can change on a failed operation.

Why separate reconstruction and matching? An identified feed execution changes the
reconstructed historical book once. Matching it again invents volume. The separate
simulator uses modeled maker-price FIFO, exchange truth, delayed client reports and
explicit synthetic provenance. Full bounded state clones make atomic multi-fill
commit simple but cost O(N+E+F+R) per staged command, not production latency.

Why exact rational analytics? Integer ticks/lots and checked 128-bit ratios prevent
silent rounding and expose overflow. Reduced fractions still have bounded
intermediates; reject unsupported values rather than silently widen/approximate.
Volatility square root alone is explicitly approximate. Independent Python integers
and Fraction calculations test the C++ formulas, including boundaries.

How is look-ahead prevented? Prefix/revision/clock checks select only causal quotes;
spread horizons remain unavailable until reached. VWAP requires declared ex-ante
profile availability; hindsight profiles are oracle-labeled. POV budgets use visible
external volume and submitted inventory, so missed fills can underexecute. No data
contract authenticates the truth of an external availability assertion.

What does implementation shortfall measure? Exact signed fill cost relative to a
declared decision benchmark, supplied fees, delay/spread components and terminal
opportunity for unfilled inventory. It does not identify causal market impact or
calibrated adverse selection from synthetic inputs. Cost conventions are explicit.

What establishes correctness? Hand examples, seeded independent reference states,
conservation/invariants, malformed input tests, real allocation-failure injection,
Debug/Release and aborting sanitizers. Tests support bounded contracts, not universal
exchange fidelity. Native ARM and hosted CI remain separate evidence questions.

What establishes speed? Correctness-gated identical workloads, raw repeated bulk and
separate service samples, source/toolchain hashes, PMR counts and process memory.
Shared-cloud samples and gprof's coarse resolution did not justify optimization;
reporting no improvement is preferable to inventing a speedup. Python boundary
costs and native timing scopes are different experiments.

How does Terminal consume it? Optional standalone Python and exact schema1.0 owned
research documents, no Terminal dependency or edits. Decimal-string integers avoid
JSON precision loss. Explicit unavailable values, model labels and manifests carry
assumptions; incompatible schema versions fail. ABI stability is not promised.
