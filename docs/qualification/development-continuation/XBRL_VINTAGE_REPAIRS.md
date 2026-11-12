# XBRL vintage and structural admission repairs — November 12, 2026

Starting source57e7bc2. Four authored test methods failed against that source
(six failing assertions/subtests). The failing-before receipt is retained locally
as build/remaining-engineering/xbrl2-before.log.

`FilingCollection.at_acceptance_time` compared the exact UTC nanosecond cutoff
with the lexical date prefix for its additional filing-date guard. Equivalent
instants across an offset/date boundary could therefore produce different facts,
and a positive offset could admit a future filing date. The guard and financial
descriptor date now derive from the same UTC instant with integer arithmetic.
Original acceptance/receipt timestamps and the caller's as_of spelling remain
unchanged. The two equivalent results share financial eligibility;their complete
selection hashes still distinguish the explicitly supplied as_of strings.

Context/entity/period/segment/scenario and compound-unit containers now reject
significant text outside their supported structural children. Previously an
opaque textual qualifier in an otherwise empty segment could disappear and leave
a fact apparently consolidated. Text in actual identifier,measure,period leaf
and explicitly preserved opaque/typed-member payloads is unaffected. Whitespace
remains accepted. No unknown contextual qualifier is guessed or imputed.

63 existing and new authored XBRL cases passed after repair. Numeric values and
source-byte hashes for supported inputs are unchanged. Derived outputs for the
previously erroneous offset cases intentionally differ. Malformed structural
inputs now reject. Native algorithms and reference identities were not modified.
No provider,application or server was started.
