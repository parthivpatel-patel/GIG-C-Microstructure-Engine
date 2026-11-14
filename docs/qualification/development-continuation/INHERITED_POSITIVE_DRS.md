# Explicit inherited positive-hypercube dimensional profile

`INHERITED_POSITIVE_EXPLICIT_HYPERCUBES_V3` adds an opt-in subset for conjunctive
positive hypercubes inherited through a supplied primary-item domain-member graph.
V1 closed and V2 direct open/closed profiles retain their original defaults,
refusals, derived schemas and canonical outputs. This is not a general DRS validator.

Authoritative basis reviewed: XBRL Dimensions1.0, Recommendation18 September2006
with corrected errata to25 January2012, sections2.5.3.2,2.6–2.6.1 and3.1.2–3.1.4:
https://xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18%2Bcorrected-errata-2012-01-25-clean.html .
Positive assignments propagate transitively to primary-item descendants. Their role,
container and closed attributes remain those of the original assignment. Applicable
positive hypercubes in one base set require conjunction; a usable cube cannot replace
an invalid applicable cube. Converging inheritance paths do not duplicate the same
ancestor assignment. Directed cycles remain invalid.

The supported contract retains exactly one definition link/role, usable explicit
members and supplied domains/defaults. It finds every direct or ancestor positive
assignment for each selected fact through reverse domain-member traversal. Each
applicable cube is validated separately, including required axes, closed/open
constraints, domain membership and default rules. The primary source of an assignment
cannot also be a member of its assigned dimension domain. Ancestor declaration,
cycle, depth and resource failures reject before publication.

There may be at most64positive assignments in the supplied network and16applicable
assignments per fact. Repeated primary/cube pairs are explicitly unsupported, even
with different closed/container attributes; no precedence/equivalence is guessed.
All applicable assignments must use the same segment/scenario container. Primary
ancestry is bounded to2048nodes and32levels; domain graphs retain their2048member/
32level ceilings. Across all applicable cubes and reported extra dimensions the
axis union is bounded to32. The existing8MiBderived-output and all source budgets
remain. Negative assignments, cross-role switching, typed dimensions, unsupported
arc priority/prohibition, unusable relationships and empty cubes remain unsupported.
Open cubes retain the conservative V2 rule that additional reported explicit axes
also need supplied usable domain/declaration validation.

V3 produces `gig.sec.xbrl.dimensional_instance.v3` or
`gig.sec.xbrl.dimensional_inline_set.v3` with exact-profile proof. Each fact has an
`assignments` list rather than an arbitrary representative cube. Every assignment
retains its actual source `primary_item`, `hypercube`, `context_element`, `closed`,
`inherited` flag, `used_defaults` and `extra_dimensions`. Its originating DTS remains
hash-bound. The per-fact default union must agree with its assignments and never
synthesizes context values or consolidates dimensioned data. Schema/profile,
assignment structure, provenance flags, containers and aggregate defaults are
validated before selected financials. The complete-DRS flag remains false.

Twenty-one authored adversarial tests cover transitive/direct conjunction, diamond
inheritance, all-cube failure, default aggregation, legacy refusal, primary cycles
and depth,16/17and64/65assignment limits, unsupported repeated/negative/typed/
cross-role/precedence/container cases, missing assignment and polymorphism, two
independent open-cube axes, combined default-axis budget, atomic collection
admission, original inline lineage and proof corruption. Legacy V1/V2 artifacts
were also directly compared with the prior implementation for four closed/defaulted/
open cases. No provider, application, external filing, accounting equivalence or
complete statement acceptance is implied.
