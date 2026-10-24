# Independent book reconstruction: byte-adapter validation

This phase strengthens the existing independent Python reference in
`scripts/check_itch_l3_reference.py`; it does not duplicate production C++ transitions.
The reference uses flat orders and explicit source-state dictionaries, independently
reads big-endian literal message fields, derives rational unit conversions, applies
lifecycle/FIFO rules and builds expected receipts/state. Candidate execution uses the
real incremental BinarySourceAdapter, SourceContext and SyntheticReconstructor in
`tests/itch_l3_reference_driver.cpp --adapter`. Expected values are computed before
candidate invocation. No production mutation implementation is imported into Python.

After each accepted or refused source record compare order identities, side, price,
remaining quantity, FIFO priority, per-symbol depth/best prices, revisions/ledger,
context lifecycle, journal/source receipt accounting, provenance and eligibility.
The original outcome printer is unchanged. Native event metadata/derived identity
remain governed by the existing projection; an additional adapter dataset identity
is independently checked in the returned summary. Physical bytes/hash/records,
accepted/native/rejected counts and completion/publication flags are checked too.
Complete input is distinct from a complete session and from eligible synthetic L3.

Scope: independently authored synthetic S/R/A/F/E/C/X/D/U/P/Q/B lifecycle cases,
existing profile/context error cases and deliberately bounded two-symbol books.
The existing H/Y/admin/auction independent suites remain separate regression gates.
This supplement does not establish exhaustive historical profile coverage or full
exchange semantics, nor validate an observed-market L3 reconstruction. Context-only
observed claims cannot acquire a native book. The diagnostic reader explicitly
refuses origin=observed: future authorized observed validation needs its own evidence
and seed/projection gate, not a relabelled synthetic fixture.

Supplement schedules: original directed cases, up to128 simultaneous active orders
across two symbols/32 price levels, UINT32_MAX quantities, repeated partial cancels,
complete closing session, first16 fixed-seed grammar cases and first32 mutation
cases. Each runs with byte fragments1 and257. These are bounded stress cases, not a
whole-market scalability claim. Existing 65186-candidate L3 oracle and prior67-session/
476-prefix readiness supplement remain in the same CTest case, along with the new
164 schedules/2228 prefix comparisons. Seed5255495; frozen eight hashes unchanged.
New expected-state digest is supplemental and separately named in the JSON evidence.

Resource/failure coverage also resides in the adapter initialization tests: malformed
framing/EOF, unknown references, duplicates, unknown types, byte/record caps,
interruption, invalid claims, digest mismatch and actual failing-PMR allocation
sweep with no leaked live state. Reusing those tests avoids pretending the Python
flat model is an allocator oracle. The existing SourceContext/native transaction
oracle remains responsible for failure atomicity at the native boundary.

Model independence is architectural, not an external third-party review: the same
engineering session authored/reviewed the harness. A shared misunderstanding of ITCH
semantics remains possible; independently aligned observed references are still
required. No market-data request, new ARM workflow or canonical regeneration occurred.
