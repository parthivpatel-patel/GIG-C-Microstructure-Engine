# Explicit inline-XBRL document-set profile — November 12, 2026

`parse_document_set` adds an explicit default-target inline-XBRL1.1 profile.
The existing plain `parse_inline`/`parse_filing` contracts remain strict and keep
their unsupported-feature rejections. No observed source or URL is acquired.

## Supported behavior

Up to8supplied XHTML documents share a validated filing identity,known acceptance
instant and default-target resource pool. Original URI,raw SHA,source URL,
permission-reference hash and receipt/acceptance metadata are retained per document.
Document order is deterministically sorted by URI,not treated as market chronology.
Every original manifest/permission is checked before parsing any XML in the set.
Conflicting filing identity,duplicate URI or ambiguous global IDs reject.

The profile extracts ordered text through an explicit passive-XHTML subset.
NonNumeric facts can follow bounded continuedAt chains across the supplied set.
`ix:exclude` removes text only from nonnumeric value extraction. Missing/wrong-kind
links,cycles,shared/orphan continuations and nested facts reject explicitly.
Numeric continuations,escaped HTML,named targets,tuples,active/unknown fact markup
and legacy inline1.0 remain unsupported. No markup is executed or fetched.

Two narrow numeric transformation subsets are supported in the2015-02-26 registry
namespace: numdotdecimal and numcommadecimal. They accept unsigned plain digits
or conventional three-digit grouping,an optional decimal fraction,and XML outer
whitespace. Other lexical forms/registries/functions reject. Sign and integer scale
are then applied exactly without Decimal-context rounding. The new profile bounds
scale to±18;the unchanged legacy plain profile retains±6. This is not full registry
conformance. Nil stays missing;fact-kind,unit,context and precision admission remain
explicit. Unknown concepts are retained but never selected as financial facts.

## Provenance and vintage

The result has a distinct `gig.sec.xbrl.inline_set.v1` schema. Its source hash is
explicitly a **derived document-set manifest hash**,not an invented original XML
response digest. Aggregate source URL/receipt/permission reference remain unknown;
all original per-document values are retained in document_set.documents. Each fact
has exact document/node/continuation segment lineage. Context/unit source locations
are retained separately. Selected financials expose actual original document SHA
sets and the derived set hash;source_instance_sha256 is null when no single original
contains the inputs. No first-document attribution is guessed for another document.

`FilingCollection.ingest_inline_set_batch` integrates this profile with immutable
filing batches,amendment lineage and exact acceptance-time selection. Optional supplied
DTS discovery uses the real reference union directly,not manufactured official XML.
It binds a distinct dts_set schema to the derived set identity. Existing selected
numeric declaration/facet checks can run on it. Full schema/DRS/statement flags remain
false. Any invalid later entry leaves the whole accepted collection unchanged.

The underlying XML Node representation now retains text/child interleaving. A
failing-before typed-context case proved that `A<Code/>B` and `AB<Code/>` previously
collided. Opaque mixed-content context trees now preserve normalized content_order,
under DIM_CONTEXT_ELEMENT_V3_ORDERED. Affected derived context/fact identities change
intentionally;the parsed artifact profile/version hash also changes. Raw input SHA,
supported reported values and native identities are unchanged. Existing stored
artifacts are not silently rewritten;conflicting reingestion still rejects.

## CLI and limits

The existing offline inspect tool accepts `gig.sec.xbrl.input_inline_set_batch.v1`:
top-level issuer_cik,origin,numeric_profile and entries. Each entry has gaap_namespace,
documents (relative path,URI,existing complete manifest),and taxonomy_documents
(null for explicit profile-only ingestion,or supplied path/URI/SHA records).
The command remains `scripts/inspect_xbrl_instances.py --batch ... --as-of ...
--output ...`. Paths cannot escape the batch directory or follow symlinks. The output
is an exclusive private0600 result;stdout contains bounded counts/status,not raw text.
Numeric corroboration requires explicit taxonomy input. No command grants source rights.

Limits:2MiB per original,8MiB total/batch,8documents/set,60,000combined nodes,
32continuation links/fact,16,384extracted characters/value,4,096facts,512contexts,
128units,32schema refs and8MiBparsed output. Existing XML depth/namespace/DTD/entity
and supplied-DTS bounds remain in force. Trace bytes are checked during accumulation.

Specification references identify the bounded feature families,not fresh provider
qualification: https://www.xbrl.org/specification/inlinexbrl-part1/rec-2013-11-18/
and the namespace http://www.xbrl.org/inlineXBRL/transformation/2015-02-26 . No fresh
registry/conformance-corpus retrieval is claimed. Authored tests exercise useful
subsets and explicit exclusions;full document-set/transform/HTML/schema conformance
and complete financial statements remain PARTIAL.
