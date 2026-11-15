# Opt-in positive explicit-dimensional calculation reports

`bind_dimensional_calculation_report(parsed, dts, *, role=None,
rounding_mode='round-to-nearest', dimensional_profile=INHERITED_PROFILE)` returns
`gig.sec.xbrl.dimensional_calculation_report.v1`, profile
POSITIVE_EXPLICIT_DIMENSIONAL_CALCULATIONS_V1. This is a separate original-source
API; existing non-dimensional reports, original parsed facts, DRS profiles and
product defaults stay unchanged. Full original DTS and original plain/inline
artifact identities are required; derived dimensional artifacts are not originals.

The binder reruns declaration binding and V3 inherited/conjunctive positive explicit
DRS validation against original inputs. It does not trust supplied dimensional proof
records. Every calculation participant requires a newly validated DRS fact record,
known numeric declaration/type/period/unit and original source fact identity.
The accepted fact-admission boundary is exactly existing ADMITTED_PROFILE or
CONFLICTED_EXACT_VALUES facts: the DRS engine proves only those inputs. Source
extension/UNVERIFIED_CONCEPT participants and facts unadmitted for a foreign unit
currently reject for missing participant DRS proof; no broader extension or unit
compatibility is claimed. A unique
supported effective signed-unit summation-item calculation network is selected.
Original context/entity/period/unit hashes and calculation arc/declaration hashes
remain independently checked. Inline source segments and original manifests remain.

All dimension-default relationships in the single supported source definition role
are checked globally, including defaults unrelated to a participant's applicable
hypercubes. Duplicate/conflicting defaults, unknown or typed axes, unusable/unknown
definition scope, members outside the supplied domain, cycles and excessive graphs
reject. All reported explicit contexts must use one source container placement.
Negative, typed, opaque, forever and cross-role scopes remain unsupported here.

OIM3.4 prohibits explicit default members in a fact's dimensions. Therefore
`aspects.dimensions` contains reported explicit dimensions only. Globally inferred
defaults appear separately in `effective_dimension_values`,
`implicit_default_dimensions` and their actual source provenance. They are not
inserted into original source contexts or represented as reported OIM dimensions.
The derived aspect hash is named distinctly from original source context hashes.
This global normalization is not a per-cube invention of missing dimensions.

Facts bind only on exact entity, full period, unit and explicit dimension aspects;
matching aliases retain original context/unit references. Incompatible units or
unvalidated participant dimensions reject; differing members or periods never join.
Exact rounding/truncation intervals and duplicate intersections reuse the existing
math API. All reported source values survive, selected_reported_value remains null,
and missing contributions remain INCOMPLETE rather than zero. No accounting metric,
GAAP alias, consolidation, statement completeness or source authentication is inferred.

Authoritative references reviewed for this package:

- Calculations1.1 Recommendation with14February2024errata, sections3.2,4.1,5.1–5.7:
  https://www.xbrl.org/Specification/calculation-1.1/REC-2023-02-22%2Bcorrected-errata-2024-02-14/calculation-1.1-REC-2023-02-22%2Bcorrected-errata-2024-02-14.html
- OIM1.0 Recommendation with19April2023errata, section3.4 explicit taxonomy-defined
  dimensions/defaults and sections5–6 equality/duplicates:
  https://www.xbrl.org/Specification/oim/REC-2021-10-13%2Berrata-2023-04-19/oim-REC-2021-10-13%2Bcorrected-errata-2023-04-19.html
- XBRL International technical dimensions FAQ, section3 default usability:
  https://www.xbrl.org/guidance/technical-dimensions-faq/

This is bounded source validation/binding, not a complete OIM loader, XDT validator
or Calc1.1 conformance claim. Existing full-network missing-contribution policy is
conservative; it does not implement every general report calculation binding rule.
Only original date-only source periods, supported positive V3 and signed-unit
networks are supported. V4 negative semantics are not enabled by this API.

Limits retain existing8MiB input artifacts,16DTS documents,4096source facts/arcs,
512contexts,128units,32dimensions/defaults,2048members/domain,32graph depth,
8duplicates/data point,128terms/parent and128bindings/4MiB output. Budgets reject
rather than truncate. Each report includes original hashes, recomputed DRS/definition
identities, default-source arcs, per-fact source proof and exact calculation lineage.

Twenty-one adversarial source fixtures cover explicit/defaulted/inherited alignment,
global defaults not used by cubes, missing/incompatible aspects, aliasing, explicit
default refusal, unsupported types/scopes, corrupted source identities, untrusted
proof replacement, duplicate conflicts/nil/missing accuracy, source inline lineage,
role/arc provenance, independent domain cycles and resource ceilings. No application,
server, provider, deployment, trading or paid resource was used.
