# Restricted explicit dimensional context profile — November 12, 2026

`EXPLICIT_CLOSED_HYPERCUBE_V1` is an explicit optional corroboration step on supplied
DTS and inline-document-set batches. The offline CLI exposes --dimensional-profile
with that exact choice. It requires supplied DTS input and declaration binding;
normal ingestion does not silently acquire a full dimensional-validity claim.

DTS discovery retains definition-link locators and the standard dimensional arc
families with source identities. Malformed links reject;unknown roles,precedence,
prohibitions,targetRole transitions,unusable arcs and split links remain explicit
unsupported metadata. Typed-domain references are retained,not guessed as explicit
axes. Metadata admission alone is not context validity.

The implemented context profile requires one complete supplied definition link/
role,one direct positive **closed** hypercube assignment,explicit declared abstract
hypercube/dimension items,one domain root per axis and usable direct domain/member
relationships. Every selected fact must fit that scope. Required axes,member
reachability,closed extra dimensions,context placement and defaults are checked.
Explicit reporting of a default member,conflicting/out-of-domain defaults,missing
required axes and domain cycles reject. Kahn cycle/depth validation covers diamond
paths;adjacency/domain caching avoids repeated full arc scans for every fact.

Open or negative hypercubes,primary inheritance,multiple assignments/roles,
context qualifiers,typed dimensions and broader DRS semantics remain unsupported.
No assumption silently makes them valid. Missing taxonomy documents also prevent
corroboration. Full schema construction/DRS flags stay false.

Default use is recorded as derived taxonomy evidence. No missing dimension is
inserted into the source context and no financial value is created. Explicitly
dimensioned facts retain the existing consolidated-selection exclusion;facts
relying on a default are also excluded. This avoids treating a defaulted segment
as an independently observed consolidated value. Numeric values,original source
hashes,contexts and source-fact identifiers remain unchanged.

Limits:64definition links,4,096arcs/network,32axes/context,2,048reachable members,
32domain levels and the existing8MiBoutput bound. Output evidence is checked before
record accumulation. All graph/source hashes,existing XML and collection limits,
permission gates and atomic batch semantics remain mandatory.

Tests cover valid explicit/defaulted contexts,closed extras,wrong placement,
missing/outside/default members,conflicts,cycles including a diamond,unreviewed
relationships,missing/split links,typed/nonabstract declarations,atomic failed
later batches,inline-set integration and actual offline CLI selection. Fixtures
are authored and do not establish real SEC/extension-taxonomy conformance.

The normative feature family is XBRL Dimensions1.0 (corrected recommendation):
https://www.xbrl.org/Specification/XDT-REC-2006-09-18+Corrected-Errata-2012-01-25.html .
The profile is an intentionally narrow implementation,not evidence of fresh
specification retrieval or complete conformance-corpus qualification. Complete
DRS/effective-network validation remains PARTIAL.
