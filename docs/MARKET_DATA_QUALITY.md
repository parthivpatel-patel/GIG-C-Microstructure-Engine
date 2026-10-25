# Quality classifications and measurable coverage

Exact validation covers decimal grammar/integral scaling/ranges,stock/instrument
scope,snapshot-before-update,zero deletion,duplicate levels,oversized payloads,
checksum mismatch,clock regression,source unknown sequence,staleness,subscription
identity and bounded trade-ID deduplication. Each authored rejection preserves
accepted native/cache state or marks explicit invalid source continuity.

The candidate Kraken checksum covers subscribed top10. It is not an exchange
sequence number and cannot prove that every trade/depth update was received.
Tracking/capture/render positions are never exchange IDs. Duplicate detection is
scoped to the last accepted payload and a256-trade window,not historical global
uniqueness. Out-of-window trade duplicates need provider/session evidence.

The gateway exposes source origin,capabilities,feed reason,missing timestamps,
source/fixture hash,clock scope,initialization scope,sequence/capture completeness,
client/rejection/timeout counts and native PMR stats. In LIVE mode book/metrics
remain empty/null and origin UNAVAILABLE while access is blocked. No synthetic
fallback. L2 initialization does not qualify L3 IDs/FIFO. For authored L3,the explicit
complete empty fixture boundary legitimately establishes that synthetic source only.

Existing ITCH/LOBSTER validation remains unchanged. Five-level reference agreement
cannot establish complete observed L3 state. Browser snapshots are sampling views,
not full source journals or complete scientific export manifests. Observed input
accuracy,provider current-wire compliance,real reconnect/gaps and real staleness
have not been demonstrated. Consult evidence manifests for exact executed tests.
