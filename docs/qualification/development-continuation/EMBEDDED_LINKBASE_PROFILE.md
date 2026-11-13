# Opt-in schema-appinfo embedded linkbases

SCHEMA_APPINFO_LINKBASE_V1 processes supplied link:linkbase containers directly in
xs:schema/xs:annotation/xs:appinfo. Explicitly requested only;the original default
continues to classify embedded scope as unsupported and refuses a usable partial
network. Unknown profiles reject before XML parsing. Unsupported placements remain
unusable;unknown root attributes/children and nested resources reject.

Embedded standard presentation/calculation/definition links reuse the existing
bounded effective-arc and restricted dimensional processors. Relative locators
resolve against the real containing schema URI,not an invented document/hash.
Every opt-in effective arc preserves original link and arc node ordinals in addition
to source URI/SHA. Multiple roots in the same document cannot alias one location.
Definition arcs preserve their source positions. At most32embedded roots,64effective
networks,4096input arcs and the existing source/output byte/depth limits apply.
No new fetch occurs. Legacy default results do not gain ordinal metadata.

The new keyword embedded_profile is supported by supplied DTS/inline-set collection
admission and the private inspect tool's --embedded-linkbase-profile option. All
permission,original source,atomic batch and profile guards remain. Existing simple
closed-cube dimensional validation works with one supported embedded definition
link;broader DRS and multiple-role semantics are not invented. Extension consolidation
still refuses unsupported DRS. Schema type and complete-statement flags remain false.

This is not generic linkbase/role-resource/schema conformance. Fragment-selected
external linkbaseRef,roleRef/arcroleRef resources inside embedded containers,
xml:base and unsupported structure remain rejected/unavailable. Old schema snapshots
are not silently migrated. New input interpretation must be requested explicitly.

13new authored tests include original-source provenance,duplicate roots,priority/
prohibition across containers,legacy refusal,bad placement/resources,unresolved
references,closed-cube admission,atomic rollback and the actual private export path.
Affected57-test cohort passed in multi-embedded-product.log. Broader current evidence
is recorded in REPORT.md;no browser/provider/observed data qualification is implied.
