# Explicit original plain-instance and DTS source reconstruction

`audit_dts_sources(parsed,dts,instance_raw,documents,*,manifest,concepts,instance_uri,
allow_observed=False,embedded_profile=None)` is an additive offline provenance audit.
It requires original raw plain-XBRL bytes, original DTS bodies and explicit parser
choices. Existing supplied-artifact binders remain compatible and do not silently
acquire a raw-source requirement. This audit does not infer a concept profile,
processing permission, source URI or embedded-linkbase policy.

A reproduced boundary showed why raw-byte reconstruction is a separate guarantee:
the existing dimensional calculation binder can consume an internally consistent,
rehashed DTS artifact whose default metadata was changed from South to North while
its document receipts retained the original body hashes. Its API receives supplied
artifacts rather than source bodies. The new explicit audit rejects that altered
metadata by reconstructing the graph from the original bytes. This is an artifact
trust-boundary distinction, not a claim that a rehashed artifact authenticates source
content or that legacy hash consistency was independent provider authentication.

The audit first validates the original manifest, processing approval, origin, body
hash and URI scope before any XML parsing. It requires an original pre-binding
`gig.sec.xbrl.instance.v1` artifact and `gig.sec.xbrl.dts.v1` graph. It reparses the
plain original under the explicitly supplied concepts and requires exact original
parsed identity, including facts, source IDs, contexts, units and schema references.
Bound/derived artifacts and inline document sets reject explicitly. No manufactured
XML instance or inferred inline-reference union is used.

It rediscovers the DTS from actual raw supplied bodies with the same explicit
embedded profile. Every original body must be in the reconstructed loaded closure;
missing, duplicate-URI and unreferenced extra documents reject. The entire graph,
canonical hash, declarations, reference union, relationships, DRS/default metadata
and unsupported-feature diagnostics must equal the reconstructed artifact. A known
unsupported semantic is preserved rather than silently removed or promoted into a
conformance claim. Malformed XML/entities/references reject through existing parsers.

Bounds are2MiBper original body,16DTS documents and8MiBcombined original input,
8MiBparsed artifact,16MiBDTS graph and1MiBreceipt, together with the existing XML,
reference, namespace, node and graph limits. No URI is fetched. No source storage,
accepted filing, calculated value or selection state is written or replaced.

The successful `gig.sec.xbrl.dts_source_audit.v1` receipt contains canonical source/
parsed/DTS hashes, actual source fact/context/unit identities and a sorted document
hash inventory. It omits original bytes/text and the plaintext processing reference.
The receipt states `independent_source_authentication=false`: caller-supplied original
bytes and hashes are not external provider authentication, full XML Schema/DRS
conformance, financial equivalence or complete statement acceptance.

Twenty-three adversarial tests exercise exact reconstruction, a demonstrated changed
default, rehashed declaration/type/definition/calculation/source/reference tampering,
fact/context/unit/ID corruption, body digest failures, raw-body replacement, closure
coverage, deterministic ordering, processing/URI/reference gates before XML,
embedded-profile parity, preserved unsupported diagnostics, unsupported derived/
inline artifacts, explicit concept scope, malformed versions/XML/entities, resource
limits and forbidden sockets. The first count-limit fixture contained only fifteen
documents and therefore correctly rejected duplicate URIs before the requested
count-boundary error; it was corrected to exceed sixteen without changing any
assertion or runtime boundary. Failing and successful logs are retained separately.
