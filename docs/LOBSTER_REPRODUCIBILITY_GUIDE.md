# LOBSTER reproducibility — current synthetic work and future permission gate

## Current allowed workflow

No attached-data processing is authorized. Use only independently authored fixtures.
C++20 GCC/Clang,CMake>=3.20,Ninja,Python stdlib; existing full engine matrix additionally
uses pinned project dependencies/zlib/Python packaging tools. See REPRODUCIBILITY.md.

```sh
cmake --preset debug
cmake --build --preset debug
ctest --preset debug --output-on-failure
python3 scripts/check_lobster_reference.py build/debug/gig_lobster_tests
python3 scripts/check_lobster_reconstruction.py build/debug/gig_lobster_validate
python3 tests/test_lobster_workflow.py build/debug/gig_lobster_validate
python3 scripts/benchmark_lobster_synthetic.py build/debug/gig_lobster_tests build/debug/gig_lobster_validate /tmp/new-authored-performance.json
```

Benchmark output must be a new file. It generates toy CSV values/IDs, not historical
observations. One warmup/three measured repetitions;20k parser pairs and2k full
analysis rows/repetition. Parser timing excludes fixture construction/output;
analysis includes paired I/O/hash/parse/reference/native-subset work. Record compiler,
configuration/source,architecture,RSS/PMR limits; no exchange-latency interpretation.

CTest observed.readiness_contracts includes native controls, both independent oracles,
13 workflow methods and pre-existing readiness checks. Strict native154/Python157 /
Python-sanitizer158 counts remain; no golden updated or check disabled. Final focused
module checks supplement full regression after row-index diagnostics/coverage update.

## Future private workflow — do not execute before written permission

Need explicit permission covering third-party cloud processing/storage, retention,
private research purpose and derivative/publication restrictions. Owner currently
states these are not established. Public sample download and this guide grant none.
Keep ZIP/CSV/private reports outside Git; no upload or additional dataset download.
Original provided attachment and earlier private copies must remain untouched until
authorized or separate retention/deletion instructions are given.

Create a private gig.lobster.run.v1 manifest with exact fields:
schema,origin(observed),dataset/session identity,instrument(symbol/native_id1/venue_id1),
initialization(unknown),message_sha256/reference_sha256,permission. Permission has
cloud_processing_approved(boolean,currently false),scope(private-research),
evidence_reference(printable token/official reference),derivative_reporting_approved.
Only set approval after applicable terms/written authorization is independently
reviewed. This record is an operator attestation, not an automated legal verifier.
Do not claim complete/seeded initialization from aggregate depth; validator rejects.

Once authorized, bounded archive verification/extraction can be invoked:

```sh
python3 scripts/lobster_archive.py /private/authorized/manifest.json /private/authorized/sample.zip --sha256 APPROVED_ARCHIVE_SHA256 --extract-to /private/authorized/new-extraction --report /private/authorized/new-inventory.json
python3 scripts/run_lobster_validation.py /private/authorized/manifest.json /private/authorized/messages.csv /private/authorized/orderbook.csv --driver build/debug/gig_lobster_validate --output /private/authorized/new-analysis.json --max-rows 1000000 --max-bytes 134217728 --max-memory 67108864 --timeout 120 --max-line 4096
```

These are future placeholder paths, not commands executed on the attached sample.
Cloud approval=false refuses before any private input open/subprocess. Archive
limits32MiB compressed/64MiB member/128MiB total/32 entries/200x ratio/30s, bounded
central-directory preflight, immutable temporary snapshot/hash, CRC and atomic staged
extraction. Symlinks/traversal/encryption/unsupported methods/overlap refused. Never
overwrite extraction/report destinations. ZIP64/multidisk not supported. Private
extraction/report inside Git refused. No remote access.

Analysis consumes each CSV incrementally with4096-byte max lines and paired EOF,
checks raw-file expected SHA256 on the same read before successful output, maintains
nondecreasing nanosecond times/ties and explicit one-instrument binding. PMR cap is
not a whole-process/ASan virtual-memory limit; fixed row buffers and bounded lifetime
IDs are separate. Native unknown-subset state stops on ambiguous/censored coverage,
unsupported/inconsistent identity or resource failures; reference observation and
eligible conditional tests remain separate. Lifetime audit scans are linear and
bounded100k; not a full-day scalability claim. Malformed input stops at first error;
no silent alignment truncation, skip or invented initial state.

Result schema gig.lobster.run_result.v1 wraps gig.lobster.analysis.v1. Contains origin,
source hashes/permission context, row/type/time/price/share histograms, anomaly counts,
per-metric eligibility/matches, unknown/inconsistent/unsupported/blocked/native states,
lower-bound/equality checks, first mismatch row/category/code, first unknown row,
resource/timing counters and full_l3_complete=false. Price ranges exclude admin /
unsupported codes; share histogram bin0 is zero, bin k1..64 is[2^(k-1),2^k-1].
Code histogram bucket0 groups0/>=8, slots1..7 retain literal codes including unsupported6.
Counts/metrics have distinct denominators; no global historical L3 accuracy. Internal
price quantumUSD0.0001/lot1 preserves wire units, not market tick calibration. No
exchange timezone/absolute clock/sequence/IDs inferred. Row errors print static fields
and safe index when available; integrity/resource refusal exits2 with no success
summary. Partial comparisons/mismatches are analytical results requiring review,
not automatic evidence of a core engine defect. Missing upstream events require
trusted integrity/sequence evidence; arbitrary caller rehashing proves no completeness.

Reproduction requires retaining private source, approved manifest/hashes, exact code /
compiler/limits and report. Do not publish raw context. Empirical comparison needs
reference alignment/profile validation and eligibility review after permission; Level5
requires independent complete order-level initialization and comprehensive evidence
that this five-level sample does not provide by itself.
