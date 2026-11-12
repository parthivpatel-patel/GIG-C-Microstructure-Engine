# Explicit numeric simple-content derivation — November 12, 2026

`NUMERIC_SIMPLE_CONTENT_V2` extends the existing optional numeric **value** profile
with named complexType/simpleContent extension and restriction. It is not full
XML Schema validation. The original NUMERIC_VALUE_FACETS_V1 remains unchanged in
admission scope:it refuses these complex derivations unless V2 is explicitly chosen.
Both ordinary supplied-DTS batches and the new inline-set/CLI path accept the
versioned choice. Default declaration-only ingestion remains compatible.

The supported structure contains one simpleContent and one extension/restriction,
a declared base QName,and no unmodeled attributes/content. Empty extensions
inherit the supported numeric base. Restrictions apply all inherited supported
numeric facets. Base traversal uses the existing8-level/128-type bounds and cycle
rejection. Exact value/unit/lexical/nil checks and output limits remain mandatory.

Complex content,mixed types,attribute declarations/wildcards,unsupported facets,
substitution chains and other schema features remain explicit unsupported results;
V2 cannot silently clear them. The DTS records NAMED_NUMERIC_DERIVATION_METADATA_V2
when such derivations are present. Complete schema construction/derivation validity,
attribute-use legality,DRS and accounting/statement mapping are not established.
`schema_type_validation` and `complete_statements` stay false.

References describe the applicable feature family,not a fresh conformance-corpus
qualification:https://www.w3.org/TR/xmlschema-1/#Complex_Type_Definitions and
https://www.w3.org/TR/xmlschema-2/ . Source documents,hashes and declaration paths
remain independently visible. No schema is fetched. Authored cases cover explicit
V1/V2 separation,extension/restriction values,unit inheritance,cycles,unsupported
content/attributes,atomic failed batches,inline-vintage integration and CLI selection.
