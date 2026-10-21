# Standalone GIG Quant Terminal consumer contract — wire 1.0

Phase 8 implements optional Python research bindings and versioned offline interchange.
GIG Quant Terminal is a separate consumer: no source/build dependency and NO Terminal
modifications. Nothing here connects a broker, transmits live orders or publishes a
release. C++ ABI/toolchain layout is not an integration contract.

Preferred boundary: locally installed gig-microstructure wheel for CPython research,
or checksummed offline version1.0 JSON/manifest exports. See PHASE_8_INTERFACE.md and
schemas/ for exact fields, codes, bounds, failure/ownership rules and examples.
Consumers can read JSON without compiling C++ or changing Terminal builds.

Consumer MUST preserve decimal strings for all64-bit IDs/prices/lots/times/sequences/
seeds (JS uses BigInt, NEVER Number); exact ratios carry numerator/denominator strings.
Preserve missing reason + null, unit/clock/precision, sequence scope, schema version,
origin/source/transformation, complete lineage and run/journal/revision refs. Python
Fraction view is explicit. Approximate volatility is labeled and separate. Unknown
schema/version, unsupported states and invalid ranges reject, never silently coerce.
Custom string-integer bound annotations need consumer semantic validation.

Treat observed/reconstructed and synthetic/simulated outputs distinctly. Simulator
exchange truth can precede delayed client reports; only delivered reports are a causal
client information set. Forecast VWAP requires availability at start; hindsight profile
results retain oracle label. Empty/one-sided/depth/gap/horizon/clock invalidity remains
visible. No certified venue mechanics or economically calibrated impact is implied.

A complete local run consists of manifest.json with complete=true, no errors/incomplete
marker, retained input artifacts/parent manifests and checksummed outputs. Verify hashes,
versions, source licenses and code/build/configuration before use. Hash integrity does
not authenticate data source or guarantee a complete external provenance graph. Never
consume a partially finalized directory as valid research. No secrets/restricted data
are bundled. Source repository remains private and has no authorized public release.

Use packaged read-only schema assets for compatibility tests; re-run round trips,
large-integer and missingness tests before accepting a future version. Schema changes
require review/versioning. Native ARM64, platforms/interpreters beyond those actually
reported in validation remain unverified. No undocumented stable cross-toolchain ABI.
