# Next bounded NASDAQ prefix — offline proposal only

No request executed or additional market byte acquired in this assignment.
The prior4KiB experiment is complete and its authorization consumed. This document
is a resource/experiment design, not authorization or a fresh network preflight.

Official artifact remains `12302019.NASDAQ_ITCH50.gz` at
<https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/12302019.NASDAQ_ITCH50.gz>.
Frozen reported total3524013057 bytes and ETag `"64b3281599bfd51:0"` need response
consistency, not a new HEAD or directory request. Previously observed Range support
and file identity may have changed; no current availability claim is made.

| Proposed limit | Exact contract requiring owner approval |
|---|---|
| Range |One GET `bytes=0-16383`, byte-zero gzip prefix, no request for a later compressed offset |
| Compressed entity body |16384 bytes maximum, read remaining only, close without a cap-plus-one probe |
| Decompressed output |2162688 bytes maximum (2MiB+64KiB), further constrained by128×consumed compressed bytes+65536; no unbounded flush |
| Managed process memory |256MiB envelope using prior64MiB supervisor/192MiB single-worker model and RSS/time watchdog; no sanitizer inside this envelope |
| Private retained output |8MiB total including tools/logs; anonymous raw descriptor preferred; no payload/row dump |
| Execution |30s acquisition+two inspections, network overall15s and blocking wait<=5s; preparation outside this declared window |
| Headers/frames |64KiB aggregate headers, at most65536 complete frames; explicit prefix residual, no inferred terminator |
| Retention |Raw bytes released immediately after comparison; maximum7 days only if separately approved retention becomes necessary |
| Retries/redirects/range growth |Zero; authorization consumed by first attempt regardless of outcome |

Before approval/execution, independently test the updated inspector caps, exact
response/read boundary, slow input, ignored ranges, header/body oversize, short
response, gzip bomb/CRC/truncation, fragmented framing and corrected consumed=
complete+residual accounting with local authored fixtures. The4KiB inspector is
hard-coded to4096 and must not simply be rerun or have guards disabled.

Require206, exact `Content-Range: bytes 0-16383/3524013057`, Content-Length16384,
consistent ETag/Last-Modified, no redirect/chunked transfer/content transformation,
normal inherited proxy and TLS verification. Validate before application body
reads. Read only remaining budget; compute a fresh16KiB prefix SHA256 and separately
verify first4096 digest equals
`133d94175e46e156baf6c7284f1fdad7e00f0fd4700bd09ed87a5afc98a700c2`.
That is local continuity evidence, not publisher-authenticated full-file integrity.
Reject changed representation, ignored Range200,416, inconsistent/missing/duplicate
metadata, resource limits or parsing errors. Never retry, stitch or expand silently.

Potential value: additional directory/status inventory and possibly new message
types/values, decoded under all explicitly named profiles and compared against a
separate spec-derived parser. **No guarantee** that16KiB contains L/V/W/h/N or any
order event. The observed first14,267 raw bytes were predominantly directory spin;
compressed size cannot defensibly predict the next types or session coverage.
Stop on unsupported types; inventory them explicitly, not silently omit them.

A partial gzip member can validate header and complete observed record structure,
fields, ordering, symbol associations and consumed-prefix hashes. It cannot verify
an unseen trailer/CRC, full expanded size, whole archive hash, authentic calendar
trading date, source losslessness, complete exchange session or valid L3 start.
Never use the synthetic reconstructor on observed bytes. No initial orders, queue
positions or execution history may be inferred from timestamps/file start/spins.
No real-market L3, empirical research result or new data download is authorized here.
