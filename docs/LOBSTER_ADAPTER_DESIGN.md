# Bounded LOBSTER adapter

C++20 target gig::lobster; allocation-free parser APIs in
include/gig/lobster/adapter.hpp. Exact fixed-field6/20 CSV contracts, distinct
nanoseconds/Price4/shares wire units, from_chars integer bounds, no floating-point
conversion. Seconds after unspecified-zone midnight convert exactly to nanoseconds;
more than9 fractional digits, scientific form, overflow, malformed/truncated/extra
columns, bad enum/price/share/admin fields are refused. No order-side/aggressor
confusion: direction is resting side. Types1/2/3/4 visible candidates;5 hidden and7
halt are separate non-mutating semantics;6/unknown explicitly unsupported.

Reference arrays preserve5 occupied levels, strict ascending asks/descending bids,
tail-only signed sentinels with volume0. Locked/crossed and real-price zero-volume
states are flagged observations, not silently repaired/discarded. Invalid ordering /
sentinel/overflow is rejected. Both rows parse before PairedValidator accepts a
pair; failures stop and cannot advance accepted counters or mutate a book. Equal
timestamps retain physical order; decreases reject. Row-pair EOF mismatch is explicit.

Configurable logical byte/record/line/deadline budgets (ceilings1GiB,10M rows,4096
bytes/line,1hour) and stop-first malformed count1. Parser storage is fixed-size, no
heap or retained CSV views. Caller supplies one explicit instrument binding; CSV
contains no instrument identity and cannot infer it. File reader/projector enforces
its own bounded PMR/I/O controls; parser does not claim total process-RSS governance.
Pure parser is not full observed-data readiness, initial seed or provenance attestor.

Authored C++ tests + independent Decimal/regex Python encoder cover all documented
codes, invalid enums/columns/time/bounds, sentinels/order/cross/zero-volume, failure
atomicity, monotonic/tied time, record caps and alignment.79 independent cases;
reference digest in evidence/lobster_parser_validation.json. No attached rows were
read for these tests. Existing observed.readiness_contracts invokes added tests
without weakening original controls or changing strict CTest/golden requirements.
