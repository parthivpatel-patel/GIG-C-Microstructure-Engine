# Offline ITCH5.0 H/Y compatibility

## Subsequent observed-prefix verification — October 23, 2026

The separately authorized repeat4KiB inspection now passes all350 complete frames
under opt-in v2 (S1,R345,H2,Y2); default v1 retains346 decoded/4 unsupported.
Both observed H states are T with blank reason/reserved space; both Y actions are0.
Independent typed-field hashes and all4 directory associations agree. This does
not establish full historical compatibility, source completeness or initial L3 state.
No observed context/book reconstruction occurred. See
[NASDAQ_HY_PREFIX_VALIDATION.md](NASDAQ_HY_PREFIX_VALIDATION.md) and its evidence.
Statements below describe their original checkpoint unless explicitly updated.

Scope: bounded decoding and source-context observations,with independently authored
synthetic fixtures only. No additional Nasdaq/LOBSTER requests,retained market
payloads,observed L3 replay,broker integration or release. Starting feature HEAD
`160de7febd4e16f10e3b1dc7b136bceb6db03873`,clean and remote-equal;main remains
`165c5038336887116d69160b0d8e5a1a5ef59d16`.

## Authoritative source and historical limits

Reused the already retrieved official
[TotalView-ITCH5.0 specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification.pdf),
1200722 bytes,SHA256
`45e0531d1b4b3beb886e9618b2ab824a5aa9bda3a99c0dff03509306e68aacc3`.
The local PDF identity was rechecked offline. Source retrieval evidence remains
`/tmp/gig-p1c-range-ex8_ustn/itch5.json`;decoded text is retained beside the PDF.
No specification or archive was fetched during this assignment.

References:page3 Architecture (daily locate identity),page4 Data Types (big-endian
unsigned integers,ASCII Alpha fields left justified/right space padded),page8
§1.2.2 H,page9 §1.2.3 Y,AppendixC reason descriptions,and AppendixA revision log
(pp22 onward). The retained document includes an April28,2023 revision and notes
Y's introduction in2010/2011,well before the2019 artifact lead. It is **not a
separately authenticated December2019 specification snapshot**. Absence of a later
H/Y change in this log is supporting context,not proof of every2019 field/profile.
The implementation therefore names a bounded status-observation profile,not a
certified full2019 feed profile.

[First-prefix inspection](NASDAQ_FIRST_PREFIX_INSPECTION.md) reported H2/Y2 with
25/20-byte lengths,not their complete field values. Those payloads were released;
this offline study does not retrospectively claim their new typed decoding passed.

## Exact wire contracts

Offsets are payload-relative,excluding the two-byte BinaryFile length prefix.

| Field | Offset | Length | Contract |
|---|---:|---:|---|
| Message type |0 |1 |ASCII H or Y |
| Stock locate |1 |2 |Unsigned big-endian,daily stock identity;zero is global/non-stock in general,not a valid mapped H/Y security |
| Tracking number |3 |2 |Exact unsigned source field;not assumed unique or increasing |
| Timestamp |5 |6 |Unsigned nanoseconds since source midnight;no date,UTC offset or receive timestamp invented |
| Stock |11 |8 |Exact padded Alpha bytes;no trimming/case folding |
| H trading state |19 |1 |H halted,P paused,Q quotation-only,T trading on Nasdaq |
| H reserved |20 |1 |Alpha reserved;no authoritative fixed value supplied |
| H reason |21 |4 |Alpha reason code,retained exactly |
| Y action |19 |1 |ASCII0 no price test;1 restriction due to intraday price drop;2 restriction remains in effect |
| H/Y total payload | |25 /20 |Exact;truncation and extra bytes rejected |

Local validation policy is the existing printable-ASCII range32–126 for Alpha.
Stock,reason and reserved bytes are owned by value. In particular,reserved is **not
forced to space**,and reason is **not forced into a presumed exhaustive historical
AppendixC enum**. Unknown printable reason values remain opaque observations;
control/non-ASCII bytes are rejected explicitly. This is a documented conservative
wire policy,not an invented reserved-field meaning. Y actions are ASCII digits,
not integer octets0/1/2. The full48-bit time range remains observable at wire level;
optional context policies independently impose intraday/monotonic bounds.

H's documented pre-opening spin and absent-security halt convention require a
known complete spin/system-hours context. An incomplete prefix cannot establish
that premise,so absence creates no synthetic halted/trading status here. Y is an
observation at dissemination time,not a simulated short-sale rule or fee/impact
input. No H/Y message establishes an empty book,clears liquidity,blocks source
executions,creates an order,advances a native sequence or restores a broken trade.

## Explicit versioned API

`DecodeProfile::baseline_v1` remains the default. It retains prior H/Y
`unsupported_type` outcomes and all five historical canonical hashes. Existing
three-argument `decode` remains and delegates to that baseline. The four-argument
overload explicitly selects `DecodeProfile::status_observations_v2`:

```cpp
auto decoded = gig::itch::decode(payload, location, provenance,
    gig::itch::DecodeProfile::status_observations_v2);
gig::itch::ContextPolicy policy;
policy.decode_profile = gig::itch::DecodeProfile::status_observations_v2;
auto context = gig::itch::SourceContext::create(manifest, policy);
```

The new owned `StockTradingAction` and `RegShoRestriction` alternatives are
appended to `Message`;existing alternative indices remain unchanged. New
`SemanticKind::trading_action` and `reg_sho_restriction` values are likewise appended.
Unknown profile values are structured errors. New-profile normalized records carry
`normalization_version=2` and their exact policy. No existing v1 hash is redefined.
New H/Y canonical identity is independently versioned in validation evidence.
Source compatibility does not imply a certified stable C++ binary ABI;rebuild
clients against the matching headers/libraries.

## Context and integration semantics

H/Y require an already admitted directory with the exact stock-locate and all8
stock bytes. Unknown/zero locate,mismatched stock and conflicting directories
reject before cursor/state commit. Existing source-adjacency,source/session/
provenance conflicts,optional timestamp and system lifecycle policies apply.
Before O/after C under the ordered-lifecycle policy remains invalid. No extra
H→Q→T or0→1→2 state machine is invented;repeated observations are allowed.

Accepted H/Y have external-observation integration,without before/after order
states,native price/quantity candidates or native mutation. The normalized source
contains all wire fields and input provenance;missing metadata stays missing.
The context does not infer or retain a separate trading-eligibility table. Consumers
receive typed observations;an execution-policy/regime engine is out of scope.

Preparation is nonmutating and uses no new allocations. Commit advances only
accepted-source location/time/count,using the existing prepared-token guarantees.
Directory/order/match vectors remain unchanged. The synthetic reconstructor checks
binding stock/locate,stores the exact source receipt and increments external-source
accounting,with no native journal/sequence/revision/FIFO change. Receipt bounds
still limit history. No unbounded per-security status history is added.

The selected profile participates in ContextPolicy/config equality and trusted
restart descriptors. Replaying identical synthetic source bytes under a different
profile fails identity checks. Factory/authored-empty,provenance,CRC/framing/source
identity and terminal/publication restrictions are unchanged. The H/Y feature
never relabels observed input synthetic or uses synthetic initialization as evidence
for a real historical session.

## Independent validation

New C++ contract tests cover finite enums,exact lengths,raw Alpha preservation,
48-bit timestamp/16-bit identity boundaries,unknown references,symbol mismatch,
source atomicity,lifecycle,fragmented S/R/H/Y frames,partial-frame consumption,
two-book isolation,allocation failures and deterministic/profile-bound restart.
The partial-frame regression distinguishes complete-frame boundary from total
consumed bytes,closing the temporary inspection-harness comparison gap without
rewriting its original evidence.

`check_itch_hy_reference.py` independently encodes bytes with struct.pack and uses
explicit ranges/maps to derive expected results **before** invoking C++. It imports
no production decoder/header/table. It checks8002 wire cases and16000 context
candidates across320 sessions,seed917717. A deliberately changed expected timestamp
must be detected. Exhaustive octet mutations cover state/action,stock,reserved and
reason fields;context traces exercise clocks,interleaving,unknown locate,session
boundaries and failed-event nonadvancement.

Synthetic stored-block gzip fixtures extend the existing18-event pipeline to21
source records:7 native mutations and14 external observations. Four fragmentation
sizes,restart under changed fragmentation,checkpoint-profile mismatch,partial
publication rejection and every reached allocation-failure site are checked.
No fixture contains source-derived market bytes.

Actual full-matrix/package counts,compiler identities,hashes and historical
assumptions are recorded in HY_VALIDATION_EVIDENCE.json and the completion section
below. Passing synthetic cases do not establish observed-market acceptance.

## Next bounded real-data experiment — not authorized here

The smallest useful next request is a **fresh, separately authorized repeat of
bytes0–4095**,not a larger range,to inventory actual H/Y enum/reserved/reason fields
under the explicitv2 decoder. Recheck preflight,ETag/size206 response and original
4KiB/576KiB/256MiB/8MiB/30s limits;reuse corrected partial-frame accounting and
anonymous-memory retention. No request,expanded range,observed initialization,
source-context admission or book reconstruction occurs in this study. Actual
unseen reserved bytes or historical values may still produce explicit rejection.

## Completed validation and packaging closure

Implementation checkpoint: `0f6e0a1ce3085dc7a8ffd73229119e182110d847`.
The resumed packaging closure changes no C++ implementation, test fixture or
canonical expectation. Existing source hashes and all nine original JUnit/log
hashes were rechecked; the completed full matrix was not repeated.

| Configuration | Passed / total | Failed / skipped / disabled |
|---|---:|---:|
| GCC Debug |131 /131 |0 /0 /0 |
| GCC Release |131 /131 |0 /0 /0 |
| GCC ASan+UBSan |131 /131 |0 /0 /0 |
| Clang Debug |131 /131 |0 /0 /0 |
| Clang Release |131 /131 |0 /0 /0 |
| Clang ASan+UBSan |131 /131 |0 /0 /0 |
| Python Debug |134 /134 |0 /0 /0 |
| Python Release |134 /134 |0 /0 /0 |
| Python ASan+UBSan |135 /135 |0 /0 /0 |

Total: **1,189 final CTest outcomes**, GCC14.2, Clang19.1.7, CPython3.12.14,
Linux x86_64. ASan/UBSan and the Python leak control executed, without suppression.
Context construction reached3 injected allocation failures; accepted H/Y context
observations allocated zero times. Streaming/restart tests reached33 injected
failure sites and verified cleanup. These are reached sites in the authored
fixtures, not a proof about every possible allocation in arbitrary workloads.
The six canonical hashes (five preserved plus the new H/Y oracle) are recorded
per configuration in [HY_VALIDATION_EVIDENCE.json](HY_VALIDATION_EVIDENCE.json).
No independent-machine, ARM64, hosted CI or observed-market result is claimed.

### Source-distribution defect and regression

The first installed direct/source-wheel interface checks passed, but the archive
inventory correctly blocked delivery. scikit-build-core0.11.6's
`build/_file_processor.py::each_unignored_file` checks force-includes before ignore
rules. Unanchored basename patterns such as `README.md`, `CMakeLists.txt` and
`THIRD_PARTY_NOTICES.md` therefore admitted nested ignored build-tree files.
The failing archive contained69,893 files, including69,626 build members;
compressed size48,051,726 bytes. It remains private failing-before evidence.

An intermediate root-anchoring repair removed build members but still forced
`python/**` cache files into the archive. A complete member inventory caught that
incomplete repair before delivery. The final repair removes unnecessary recursive
force-includes, retaining only root-anchored build/notice/document filenames;
source trees follow normal ignore rules. No package/API version was changed.
This is a packaging-content change, not an engine behavior/schema change.

`tests/test_sdist_patterns.py` executes three pinned-backend checks: negative
controls reproduce both the unanchored-basename leak and the recursive cache
leak; the actual current configuration preserves source files and excludes both.
Run with the build environment's Python (tomllib requires Python3.11+):

```sh
/workspace/gig-tools/bin/python tests/test_sdist_patterns.py
python3 scripts/check_sdist_inventory.py path/to/gig_microstructure-0.1.1.tar.gz \
  --source-root . --manifest /tmp/sdist-manifest.json
```

The standalone inventory checker rejects nonregular, duplicate, unsafe,
unintended or byte-mismatched members and requires complete source/header/Python/
CMake/schema trees. It does not extract the archive. Compare against the exact
source snapshot used to build it, before subsequently editing documentation.
Final artifact hashes, inventory and fresh installed-consumer outcomes are pinned
in the accompanying evidence. Archives/wheels/logs stay ignored under
`build/hy-validation`; no binary, raw market data or private environment is committed.

### Changed-file inventory and limits

Implementation checkpoint: `.github/workflows/ci.yml`, `CMakeLists.txt`,
`include/gig/itch/{decoder,context}.hpp`,
`src/itch/{decoder,context,reconstruction}.cpp`,
`scripts/check_itch_hy_reference.py`,
`tests/test_itch_hy.cpp`, `tests/test_itch_hy_streaming.cpp`.
Closure: `pyproject.toml`, `scripts/check_sdist_inventory.py`,
`tests/test_sdist_patterns.py`, this report, `HY_VALIDATION_EVIDENCE.json`,
`ITCH_HISTORICAL_COMPATIBILITY_MATRIX.md`, `REPRODUCIBILITY.md`,
`OVERNIGHT_ENGINEERING_PROGRESS.md`, `RC_OWNER_ACTIONS.md`,
`NASDAQ_REAL_DATA_PILOT_PLAN.md`, `REAL_MARKET_DATA_ACCESS.md` (all documents in docs/).
The institutional audit and prior phase evidence remain preserved.

Remaining limits: explicit opt-in v2 only; no Python H/Y API, latest-state trading
policy, full2019 certification, observed initialization or real-market replay.
Nine known ITCH families remain unsupported, as listed in the compatibility matrix.
Previously inspected H/Y payload values were not retained or revalidated.
Ordinary Python wheels exercise the existing research API; native CTest supplies
H/Y/streaming validation. No package publication or main merge is authorized.
