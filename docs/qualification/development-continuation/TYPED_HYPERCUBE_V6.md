# Bounded typed hypercube corroboration — V6

This developer-only, offline profile integrates the existing original-schema scalar typed-domain checker with one direct positive **closed** hypercube and one definition role. It is an explicit opt-in extension of the dimensional producer, not a full XBRL Dimensions implementation. No provider, application, server or owner acceptance session was used. Existing V1–V5 profile identities and default selection are retained.

## Source contract

`terminal.stocks.xbrl_dimensions.TYPED_PROFILE` is `DIRECT_CLOSED_TYPED_HYPERCUBE_V6`. Call `corroborate(parsed, dts, profile=TYPED_PROFILE, documents=original_dts_documents, allow_observed=False, instance_uri=None)`. Plain originals require their explicit original `instance_uri`; a retained non-null source URL must agree. Inline originals use their actual retained absolute schema-reference union. No synthetic instance XML or guessed permission reference is constructed.

Inputs remain declaration-bound original `gig.sec.xbrl.instance.v1` or `gig.sec.xbrl.inline_set.v1` artifacts. The explicit processing approval and retained per-source permission hashes are validated before original XML processing. Every original schema and linkbase body in the discovered closure must be supplied, hash verified, bounded and accounted for exactly once. The graph is rebuilt from those raw bodies and actual reference roots with the retained explicit embedded-linkbase profile, then compared by canonical bytes, including all diagnostics, provenance and effective relationships. This detects retained-graph tampering even if an attacker recalculates its artifact hash. Unknown embedded-linkbase semantics reject; original byte hashes alone do not independently authenticate the issuer or provider.

This reconstructs the **DTS** from original bodies and retained parsed-source metadata. It does not independently reparse the original filing bytes; the separate original plain/inline source audit remains the contract for full original filing reconstruction.

The normative source is [XBRL Dimensions 1.0, Recommendation 18 September 2006, corrected through 25 January 2012](https://xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18%2Bcorrected-errata-2012-01-25-clean.html), consulted using the documentation tool during this package. Relevant sections: 2.2.2 (hypercube dimensions), 2.3.3 (closed cubes), 2.5.2 and 2.5.2.1.1 (typed declaration/global nonabstract DTS target), 2.5.3.1.1 and 2.7.1.1 (explicit dimension-domain/default sources), 3.1.3.1 (individual hypercube validity), 3.1.4.1 (reported dimension values), and 3.1.4.4.2–3 (typed member/declaration/content). This profile implements only the subset below; the specification permits broader structures than this profile accepts.

## Supported behavior

A selected fact must have the single direct closed `all` assignment. Its cube must contain at least one typed axis. Every typed axis is mandatory and must contain a supported scalar instance of the exact global element referenced by its original schema declaration. Typed axes cannot acquire explicit domains or defaults. Required explicit axes can coexist; their supplied domain memberships, unreported default values, conflicting defaults, reported defaults, primary-item polymorphism, domain cycles and depth limits remain checked. Both kinds must use the assignment's context container. Closed extra dimensions and opaque context content reject.

Typed scalar support stays exactly the existing `TYPED_DOMAIN_SCALAR_V1` checker: original `xs:string` lexical content; valid XML boolean lexical forms; exact supported XML Schema numeric scalars/named numeric restrictions. Unsupported attributes/nil, complex content, anonymous domain types, QName-valued types, substitution chains and XPointer expressions reject the V6 corroboration with an explicit diagnostic instead of creating partial acceptance. Existing standalone diagnostics remain available for inspection.

The producer deep-copies inputs and preserves original contexts, values, fact IDs, receipts and source identities. Typed lexical content is never normalized, compared for equality, substituted into facts, or aggregated as consolidated financial data. Missing information stays missing. Successful facts produce restricted proof; `complete_drs_validation` remains `false`.

## Exact derived proof

Output schemas are `gig.sec.xbrl.dimensional_instance.v6` and `gig.sec.xbrl.dimensional_inline_set.v6`. Their `dimensional_validation` has `profile`, `facts`, `typed_context_diagnostics_sha256`, `complete_drs_validation:false`, and `scope`.

Each fact record has exactly:

- `source_fact_id`, `role`, `hypercube`, `context_element`, `used_defaults`;
- `typed_dimensions`, sorted by expanded dimension QName;
- `status:"VALIDATED_RESTRICTED_TYPED_CONTEXT"`.

Each typed dimension record has exactly `dimension`, `member_tree_sha256`, `typed_domain_ref`, `domain_source_sha256`, `scalar_validation`. The member tree digest binds the original reported XML tree. The original domain schema digest and absolute domain reference retain its declaration source. `scalar_validation` is the unchanged standalone-checker result: `resolved_type` and `validation`, with `numeric_profile` and `restriction_types` additionally required for numeric results. No raw source XML or permission plaintext is added to the proof.

## Collection and selection boundary

`FilingCollection.ingest_dts_batch` forwards the original documents, collection observation permission and exact instance URI only for V6. `ingest_inline_set_batch` forwards the original taxonomy documents and collection observation permission only for V6. V1–V5 call signatures and default behavior remain unchanged. A failed later member leaves the entire collection batch unpublished.

`selected_financials` accepts both V6 schemas and checks the exact record fields, original context semantic digest/container/axis set, original member-tree digest, domain reference and schema digest against retained DTS receipts, supported scalar type/status/profile fields, and independently validates scalar boolean/numeric lexical forms and numeric base ranges. Typed rows remain excluded from consolidated financial selection. Missing, duplicate, malformed and rehashed inconsistent proof records fail closed.

This consumer boundary checks retained artifact consistency. Original schema restrictions and source graph interpretation are replayed by the producer from supplied raw DTS, not reconstructed from hashes by the consumer. The diagnostics digest retains identity; it does not authenticate an issuer or replace an original-source audit. The UI import contracts do not acquire an implicit new supported profile.

## Bounds and remaining scope

Original DTS limits remain 16 documents, 2 MiB per document, 8 MiB total, depth 8, 4,096 edges, 32 roots, and the XML parser's existing limits. V6 retains 32 cube axes, 2,048 explicit domain members, 32 explicit graph levels, 4,096 checked typed members, 4,096 scalar text characters and 8 MiB output. Duplicate source URIs reject. Resource errors remain errors.

Still unsupported in V6: multiple/inherited assignments, open cubes, negative cubes, cross-role relationships, arc priority/prohibition, unusable members, complex/anonymous/nil typed semantics, typed equality, schema-wide conformance and automatic financial promotion. Older opt-in profiles retain their own supported explicit semantics; V6 does not supersede them. Observed provider qualification, full standards conformance and owner acceptance remain unclaimed.

## Developer verification

Focused adversarial tests cover exact original binding/provenance, scalar lexical/range/facet rejection, mandatory typed values, mixed explicit/default behavior, closed extras, opaque/wrong containers, unsupported typed structures, schema/linkbase coverage/digests/duplicates, recomputed retained-graph tampering, source URI/root union, permission-before-XML gating, supported/unsupported embedded sources, 32-axis acceptance/33-axis rejection, explicit domain cycles/default contradictions, and preserved legacy rejections. Recovery verification: 33 focused tests pass (`delivery-focused.log`); 259 related dimensional, typed-scalar, instance, collection, inline, dimensional-calculation and source-audit tests pass (`delivery-related.log`). Additional fixtures exercise two-document inline collection integration, batch atomicity, consumer scalar checks, eighteen rehashed proof-corruption variants and no new kwargs for legacy collection calls. Ten representative V1–V5 artifacts and their selected-financials outputs are independently canonical-identical to `f7813d71a079ba7efdf234db7efa424e6eebbf20` (`delivery-legacy-identities.log`). These checks concern supported developer contracts; full DRS, live-provider and owner acceptance remain unclaimed. Package logs are in `work/typed-hypercube/`; the sprint report records final integrated counts and exact verified commits.
