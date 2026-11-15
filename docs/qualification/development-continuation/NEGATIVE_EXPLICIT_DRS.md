# Explicit mixed positive/negative hypercube profile

`INHERITED_EXPLICIT_NEGATIVE_HYPERCUBES_V4` adds an opt-in single-role subset of
mixed `all`/`notAll` assignments to the existing supplied explicit-domain engine.
Original V1/V2/V3 defaults, refusals, schemas and canonical outputs remain unchanged.
This is not complete XDT conformance or cross-role/typed hypercube validation.

Authoritative basis: XBRL Dimensions1.0, Recommendation18 September2006 with
corrected errata to25 January2012, sections2.6–2.7 and3.1.2–3.1.4:
https://xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18%2Bcorrected-errata-2012-01-25-clean.html .
The result of each applicable cube is joined by its assignment operation. A positive
cube must be valid. A negative assignment is satisfied only when its cube evaluates
invalid for the reported context. An invalid positive cannot be replaced by a valid
negative result. Inherited assignments retain their source role and attributes.

The supported subset requires at least one applicable positive assignment. It
validates positives first, then negative assignments. Before negative evaluation,
all its cube declarations, explicit axes, domain graphs, defaults, primary-item
polymorphism, container and resource limits are admitted independently. Only
contextual closed-extra, outside-domain-member or missing-required-dimension outcomes
may constitute an evaluated invalid cube. Declaration/schema/domain-cycle/default/
resource/unsupported errors always reject; there is no catch-all error-to-negation
conversion. Global invalid contexts, including an explicitly reported default member,
are never treated as satisfied exclusions. A valid negative cube rejects the primary
fact's candidate collection. Unsupported negative-only networks reject explicitly.

The profile preserves one definition link/role, usable explicit members, a common
segment/scenario container, at most64network assignments and16applicable assignments
per fact. These budgets count both signs. Existing ancestry2048node/32level,
domain2048member/32level, combined32axis, source and8MiBoutput limits remain.
Repeated `(primary_item,hypercube,kind)` relationships are unsupported, while the
same positive/negative pair is evaluated as an actual contradiction. Typed axes,
unknown domains, targetRole switching, precedence/prohibition, unusable relationships
and empty cubes remain unsupported. Open cubes retain the conservative supplied
extra-dimension admission contract of the previous profile.

V4 produces `gig.sec.xbrl.dimensional_instance.v4` or
`gig.sec.xbrl.dimensional_inline_set.v4` with an exact-profile dimensional proof.
Every assignment retains its originating primary item, cube, inherited status,
container, closed flag and context/source identity. It adds `kind`,
`hypercube_valid` and `failure_reason`. Accepted positives have valid=true and no
failure. Accepted negatives have valid=false and a specific contextual invalidity
reason. Negative `used_defaults` is empty: evaluating a negated cube never supplies
a dimension value to the reported fact. Top-level defaults aggregate only the
positive assignments. This does not assert a complete intermediate evaluation trace.
Original inline/source lineage is preserved, and schema/proof/outcome/aggregate
contracts are checked before financial selection. The complete-DRS flag stays false.

Twenty-two adversarial offline tests cover inherited/direct signs, contextual
exclusions, valid-negative contradiction, positive defaults/nonselection, legacy
refusal, negative-only scope, malformed declaration/domain/cycle/default/role errors,
positive failure,16/17and64/65assignment limits, negative-axis resource ceilings,
identical/equivalent cube contradictions, atomic collection refusal, original inline
lineage, explicit-default global errors and proof corruption. No provider/network
source, application, accounting equivalence or observed filing acceptance is implied.
