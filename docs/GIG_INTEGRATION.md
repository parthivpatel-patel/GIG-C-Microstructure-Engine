# GIG integration boundary

PROPOSED / MUST HAVE contract; NOT IMPLEMENTED. Independent versioned event,
snapshot, metric and run-manifest schemas. Begin with offline files/CLI; Python
(pybind11 is SHOULD HAVE in Phase 8) follows validated C++ contracts. No dependency
on GIG Quant Terminal and no terminal modifications.

Carry integer prices/quantities/IDs exactly (decimal strings for JSON crossing
JavaScript), explicit timestamp unit/clock/precision, sequence scope, metadata,
validity and full lineage. Reject unknown major versions; document additive minor
changes. Never promise a stable C++ ABI across toolchains. Missing metrics have
reason codes, not fabricated zero values. Compatibility fixtures must test exact
round trips, ownership and error semantics independently of terminal code.
