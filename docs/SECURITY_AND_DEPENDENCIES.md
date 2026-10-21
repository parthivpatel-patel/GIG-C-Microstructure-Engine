# Security, licenses and research provenance

This is an offline private research prototype. No live exchange/broker connectivity,
credentials, external data or paid infrastructure is required. No source, data or
wheel has been publicly released by this work. The repository does not grant a
public project license; obtain authorization before redistribution. Do not infer
license permission from GitHub visibility or Python package metadata.

Native code uses the C++ standard library and compiler-provided 128-bit integers.
Optional bindings pin pybind11 2.13.6 (BSD3 notice retained) and scikit-build-core
0.11.6 (build tool); jsonschema 4.23.0 is the runtime schema dependency. The exact
12-package tested tool/runtime closure is requirements-python.lock. The archived
Phase 9 review records each installed version, declared license metadata, license
file paths, wheel SHA256 matched against TLS-delivered PyPI metadata and available
version-specific advisory responses. Metadata is inventory evidence, not legal
advice or a substitute for reading upstream terms. Build-only licenses do not
implicitly relicense the project. Platform CPython/compiler/libc/kernel CVEs and
all upstream source authenticity are outside this registry snapshot's scope.
Debian compiler packages were matched to signed repository metadata without
installing system packages; their exact identities/hashes are retained separately.

Review boundaries: strict duplicate-key JSON parsing; bounded input byte/depth/list
sizes; no pickle/eval or dynamically loaded remote schema; exact integer strings
and explicit version rejection; native domain validation before application;
owned results and GIL-held native calls; allocator-failure tests; export safe names,
no-overwrite finalization, hash/schema verification and incomplete markers. Runtime
has no network client. File hashes provide integrity, not signatures or data-source
authenticity. Export is not a crash-safe database transaction. Calling code must
control trusted directories and resources; hostile concurrent filesystem mutation
is not a proven sandbox boundary. Native C++ caller-owned resource lifetimes remain
the caller's responsibility. No formal verification, fuzzing campaign, penetration
test or exhaustive dependency/platform vulnerability audit is claimed.

All benchmarks and examples use deterministic synthetic inputs. No restricted
market-data license is consumed. Observed data adapters must supply dataset/version,
source-record identity, stream/session scope, clocks/precision, transformation
lineage, digests and license terms. Missing metadata stays unavailable. Simulation
outputs remain explicitly synthetic; generator seed, model, parent runs and profile
availability/oracle labels follow outputs into manifests. Retain actual hashed input
bytes and parent-manifest hashes; a caller-supplied completeness assertion is not
independent proof of a complete or authentic provenance graph.
