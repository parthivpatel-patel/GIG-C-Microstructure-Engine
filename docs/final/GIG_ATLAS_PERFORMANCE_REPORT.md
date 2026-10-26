# Performance and memory evidence

Local x86_64,Python3.12.14,Chromium154.0.8037.57;authored fixtures only. Native source
unchanged. Exact raw observations/source hashes and bundle inventory in final manifest.

* Initial JS230732 bytes;Python-gzip9 size71427 bytes. Optional stock70384 bytes;
  Three/OrbitControls507532 bytes deferred. Compression configuration differs from Vite's
  size report;no claimed network byte equality. Existing optional-chunk warning retained.
* Cold isolated Chromium contexts,cache disabled,1 warmup/3 measured runs:
  Initial navigation including networkidle wait(ms): [774.687, 842.953, 889.57].
  Stock route(ms): [145.519, 263.168, 139.814].
  Loopback health roundtrip(ms): [2.801, 15.78, 11.572].
  Sampled JS heap(bytes): [5094672, 5707780, 5171568].
  DOM nodes: [1479, 1479, 1479].

* Conditional GARCH64 observations,1 warmup/3 traced measured runs(seconds):
  [0.10076920199207962, 0.10599013598402962, 0.09858382301172242];median0.100769.
* MessagePack decode-only1000×32 rows:0.209837s,
  152499.1 rows/s. Excludes auth/network/normalization/publication.
* Traced Python peak21489 bytes;process peakRSS17516KiB.
  RSS includes interpreter/imports;not incremental native memory. Not a production SLO.

Phase5 journal observations remain12232-byte physical record,15944-byte logical entry,
~100MB live/~150MB peak tracked PMR at8192 synthetic records. This assignment's native
suite exercises journal/recovery/allocation regressions;no new optimization or memory
reduction claimed. Retain baseline until a separate reservation/compaction candidate can
pass equivalence,recovery,snapshot-version,allocation-failure and canonical gates.
Existing bounded model inputs/retained snapshots/buffers remain the primary safeguards.
Long-run memory growth,GPU memory,physical Android,independent-machine throughput and
provider/network tail latency are NOT VERIFIED by these short loopback observations.
