# Standard effective relationships V1

This offline profile supplements the original strict `presentation` graph; it
never changes the legacy graph's usability decisions. `effective_relationships`
is explicitly versioned as `gig.sec.xbrl.effective_relationships.v1` with profile
`STANDARD_EFFECTIVE_ARCS_V1`. DTS declaration binding preserves the graph and
concept declarations inside the source-bound proof.

Reference: XBRL 2.1, sections 3.5.3.9 (equivalent arcs/overriding/prohibiting),
5.2.4 (calculations), 5.2.5 (presentation), published specification at
https://www.xbrl.org/Specification/XBRL-RECOMMENDATION-2003-12-31+Corrected-Errata-2013-02-20.html .
This is a deliberately restricted implementation, not specification conformance
certification or a fresh network verification of that document.

Only standard presentationLink/presentationArc/parent-child and
calculationLink/calculationArc/summation-item are interpreted. Locator endpoints
must resolve to supplied declarations. Base-set identity includes link/arc names,
link role and arcrole. Equivalent supported arcs have identical endpoints, order,
preferredLabel and weight where applicable. Default order is 1; exact decimal
normalization makes 1.00 and +1 equal. Order and relationship-specific attributes
are NOT discarded when deciding equivalence. Highest nonnegative priority wins;
a prohibition at that priority removes the equivalence class. Higher-priority
optional relationships can override lower prohibitions. Every supporting and
superseded arc retains source URI/SHA and link/child index.

Links sharing the same supported base set are combined across supplied documents.
Unknown attributes, resource/extended-link content or arcroles invalidate the
entire affected role/kind. No partial usable graph is published by dropping an
unsupported arc. Malformed structure, priorities, use and numeric fields reject.
No custom arcroleRef, label text, generic links or targetRole semantics are inferred.

Presentation preserves preferred-label role URIs; they are not resolved to label
text. Calculation supports signed unit weights only (+1/-1), with balance-sign
checks where both balances are declared. Other weights are explicitly unsupported.
Multiple effective calculation relationships for one endpoint pair are unsupported,
not arbitrarily summed. Directed cycles and paths deeper than 32 invalidate the
network. There are at most 64 role/kind sets, 4096 total input arcs and 4 MiB output.
Global schema/taxonomy/statement completeness flags remain false.

Developer checks: 14 authored effective-relationship tests; 139 passing XBRL cases
in `build/remaining-engineering/effective-relationships-139.log`. Fixtures are
independently authored and contain no provider observations. No application,
server, provider request or trading operation was performed.
