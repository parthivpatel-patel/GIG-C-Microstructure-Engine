# Bounded BinaryFile source adapter

Implementation: include/gig/itch/input_adapter.hpp and src/itch/input_adapter.cpp,
in-tree CMake target gig::itch_input_adapter. Single owner, incremental raw
BinaryFile bytes; no filesystem, network, gzip acquisition or legal attestation.
This is an **implemented/tested ingress and source-context bridge**, not a completed
observed-market native-L3 adapter. The latter remains explicitly blocked.

BinarySourceAdapter::create accepts a typed DatasetContract, SourceManifest,
ContextPolicy, FramerLimits and InitialClaim. Dataset roles preserve provider,
dataset/acquisition/permission/redistribution/initial-state reference identities,
optional exact Gregorian session date, explicit capture boundaries and known gaps.
Source provenance preserves declared origin/source/raw-artifact digest/seed. No
missing date, source record, sequence or clock is invented. Session identity must
be explicitly supplied; it is an external/capture namespace, not inferred exchange
sequence or date. Identity/reference tokens are assertions, not rights verification.

feed consumes at most one frame per call, returning consumed bytes, physical
location/type and either an owned normalized observation or a native synthetic
transaction receipt. Caller loops over every unconsumed byte and retains dataset
contract with receipts. Unsupported/unknown/malformed/lifecycle/resource errors
stop permanently and preserve the accepted semantic prefix. Record/rejection
counts refer to complete frames; framing errors are separate (no imaginary record).
No callback or fallible normalization copy follows accepted context commit.

Context-only route accepts observations with unknown, session-start-evidence,
snapshot-evidence or incomplete initialization claims. Even a caller claiming a
complete observed start/snapshot gets **no native book**, full_l3_complete=false
and publication_eligible=false. SourceContext initialization remains incomplete.
This permits future authorized decoder/context inspection without fabricating
observed history. Authored mocks of origin declarations test policy preservation;
they are not observed datasets or observed correctness evidence.

Native route is available only for authored_synthetic plus a matching existing
ReconstructionConfig: exact source/provenance/context policy, no known gaps, explicit
existing factory evidence and source-record limits. It delegates to the already
validated joint context/native transaction, not a second mutation implementation.
Native book access is absent for context-only/moved-from objects. No source is
relabelled and no observed path is forced through the synthetic factory.

Input budgets: at most128MiB raw bytes/100000 records, framer buffer <=65535 bytes,
existing context capacities and logical memory budget; native receipt/journal limits
remain explicit. Supply a caller-owned bounded TrackedResource/PMR governor for a
hard aggregate allocation budget; PMR must outlive adapter. Default allocator does
not certify process RSS. No whole archive loaded, no retained observed event vector.
SHA256 updates over exactly consumed raw framing bytes; EOF requires declared raw
artifact hash and optional end offset. This digest is not gzip/whole-upstream capture
or publisher authentication. Gzip transport can be separately supplied using the
existing qualified reader, but no new archive ingestion or concatenation policy is
silently introduced.

finish distinguishes exact complete declared input, locally ordered session,
complete synthetic L3 and publication eligibility. Bounded interruption/truncated
EOF/corrupt digest/gaps never publish complete L3. Finish is idempotent, moved/finished
feed is rejected, and reentrant calls are refused. Restart means re-create and replay
from the authenticated source boundary; no serialized hot adapter snapshot exists.

Tests inside existing itch.reconstruction_initialization cover chunk1/7/4096 native
replay and final ledger/book, caller observed claims without book access, invalid
initialization/date/provenance/gaps, checksum corruption, unknown/duplicate/type
refusals, header/payload/terminal truncation, record caps, interrupted/moved/finished
state, and actual allocation-failure sweeping to full success with zero live PMR.
Initial compilation caught a misleading-indentation fixture warning; braces fixed,
-Werror preserved. Final executed matrix is evidence/market_data_adapter_validation.json.

Observed native integration is NOT implemented here: complete observed initial
context/native/FIFO seed and authenticated upstream history remain missing. Current
API intentionally refuses to pretend those capabilities exist. A later adapter
phase needs explicit source/evidence and independently validated seed/projection;
no real-market correctness or production readiness follows from synthetic tests.
