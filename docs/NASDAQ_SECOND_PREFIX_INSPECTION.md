# Second NASDAQ prefix inspection — authorized16KiB experiment

**PASS for observed complete-message decoding and limited source-context checks;
INCONCLUSIVE for full historical compatibility or observed L3.**
One GET at2026-10-24T00:25:22Z (October23,20:25:22 EDT). Entry feature HEAD
ef6970626f53354827864e937f3403ce281035df, clean/local/remote equal; main unchanged.
The existing 4KiB requests were not repeated. This new byte-zero16KiB extent
necessarily overlaps them, as explicitly authorized. No other Nasdaq/LOBSTER call.

Followed NASDAQ_NEXT_PREFIX_PREFLIGHT_PROPOSAL.md:16384-byte entity body,
2162688-byte output and128×consumed+65536 guard,256MiB managed envelope,
8MiB private output,30s acquisition/inspection deadline,15s worker alarm/5s socket
waits,64KiB headers,65536 frames, zero retries/redirects/extra ranges.
All37 local safety controls passed before GET. Inherited proxy/CA/TLS hostname
verification retained; configured policy status is not proof of origin access.
Metadata was checked before body reads:206, exact single Content-Range/Length/ETag,
Last-Modified, no transfer/content transformation or Location. Each body read is
min(1024, remaining16384); no extra-byte probe, body drain or range expansion.
The one-shot marker prevents repeating this consumed budget. TLS/kernel buffering
and HTTP overhead are outside the approved application entity-body counter.

Official artifact:
<https://emi.nasdaq.com/ITCH/Nasdaq%20ITCH/12302019.NASDAQ_ITCH50.gz>.

| Transport /format property | Actual result |
|---|---|
| HTTP status /Content-Range |206 /`bytes 0-16383/3524013057` |
| Content-Length /read body |16384 /16384 bytes |
| ETag |`"64b3281599bfd51:0"`, frozen validator matches |
| Last-Modified |Tue,31Dec2019 05:13:48 GMT |
| Content-Type |application/x-gzip |
| Compressed SHA256 |`5a436e3cc4fe35007cf56695d52d1500aa9427b540ff24e1c6c1a3482e5e7cae` |
| First4096 SHA256 |`133d94175e46e156baf6c7284f1fdad7e00f0fd4700bd09ed87a5afc98a700c2`, exact prior identity |
| Gzip header |10 bytes; Deflate8,flags0,MTIME0,XFL0,OS0; no optional fields |
| Decompressed bytes |58606, independent Python/native inflaters agree |
| Decompressed SHA256 |`60646c01b1d78eb61a57865f47d4b89a44bb62f548d66dcf2273c3a0d5e57569` |
| Complete BinaryFile frames /bytes |1433 /58594 |
| Buffered incomplete frame |12 bytes; native consumed58606=58594+12 |
| Terminal /gzip trailer |Neither observed; incomplete member, no observed gzip error; whole CRC/ISIZE unverified |

| Type | Frames | Length | v1 | v2 /v3 |
|---|---:|---:|---|---|
| S |1 |12 |Decoded |Decoded |
| R |1424 |39 |Decoded |Decoded |
| H |4 |25 |Unsupported |Decoded |
| Y |4 |20 |Unsupported |Decoded |
| Total |1433 | |1425 decoded,8 explicit unsupported,0 rejected |1433 decoded,0 unsupported/rejected |

Independent spec-derived Python fields and native typed re-encoding compare exact
source ordinal/physical offset/length and every decoded field. All three profile
counts, ordered hashes, source provenance and raw size/hash agree; zero typed
roundtrip or association errors. V2/v3 ordered field SHA256:
`d3c97833dfbb4638d074f925a3572a6131ac21f80aed7ce0aec1d97b75159b26`.
All8 H/Y associations match already observed directories;1424 unique locates,
zero duplicates. H:T4, reserved spaces and blank reasons; Y:ASCII0 four times.
No symbol/locate rows or raw payload bytes are committed.

A bounded SourceContext v3 is used with observed origin, unknown initialization
and an explicitly unverified capture-scope token, not an invented exchange session
or trading date. Native and independent model both accept1433 source records,
1424 directories, zero orders/matches and zero errors. The temporary inspector
allows65536 directories within the existing4MiB logical context budget, rather
than assuming the default64 suffices;192MiB worker limit remains enforced.
Independent `scope_complete=true` means its context model covers the observed
families, **not source/session/initialization completeness**. No book, synthetic
reconstructor, native sequence, journal, order history or publication is created.

Raw timestamps11072057543747–11354370974277 ns since midnight, no regressions/outside-
day observations in complete frames. Tracking numbers are preserved, not interpreted
as globally unique sequences. No calendar date/UTC/receive clock/losslessness inferred.

| Resources | Actual result |
|---|---|
| Total bounded acquisition +both inspections |0.665s; worker0.564s |
| Peak sampled combined RSS |29,614,080 bytes |
| Worker /supervisor peak RSS |18,350,080 /11,010,048 bytes |
| Wait-accounted child peak RSS |18,481,152 bytes |
| Headers read, including proxy/response status |403 bytes |
| Private output before aggregate report |172290 bytes; final size in evidence remains far below8MiB |
| Managed caps |64MiB supervisor soft address limit plus one192MiB hard-capped child; summed RSS/time watchdog |
| Raw retention |Anonymous descriptor closed, processes exited; **zero raw market bytes retained** |

RSS polling is not an exact simultaneous peak or a whole-host/kernel guarantee.
Preparation/compilation/synthetic controls precede the30s experiment. Subsequent
reporting uses sanitized aggregates only. No source-engine changes or completed
1261-outcome matrix rerun was needed for this inspection checkpoint.

No decoder/context defect was reproduced. Coverage grew from350 to1433 complete
frames but exposed **no new message family or order event**. The rest of the gzip
member, full artifact integrity, session closure, missing-history state and valid
initial L3 evidence remain unverified; truncation is expected, not archive damage.
At this checkpoint K/J/I/O remain explicit unsupported families; none occurs here.

The single request authorization is exhausted. Do not automatically request64KiB
or infer that more prefix bytes will reach orders. Prioritize offline completeness,
readiness gates and a resource/initial-state/reference plan for any later pilot.
A further acquisition needs a new exact authorization; no request is pending.
Full aggregate evidence and tool hashes: NASDAQ_SECOND_PREFIX_EVIDENCE.json.
