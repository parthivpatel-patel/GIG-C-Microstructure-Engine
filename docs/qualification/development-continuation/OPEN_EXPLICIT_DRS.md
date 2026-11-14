# Explicit direct open-hypercube dimensional profile

`DIRECT_EXPLICIT_HYPERCUBE_V2` adds an opt-in direct positive open/closed hypercube
profile. The existing `EXPLICIT_CLOSED_HYPERCUBE_V1` default, derived schemas, proof
fields and refusal of open cubes remain unchanged. V2 input must still be an
original plain-instance or inline-set artifact bound to its supplied DTS.

Authoritative sources reviewed November 14, 2026 (America/New_York):

- XBRL Dimensions1.0, Recommendation18 September2006 with corrected errata to
  25 January2012, sections2.3.3,3.1.3–3.1.4:
  https://xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18%2Bcorrected-errata-2012-01-25-clean.html
- XBRL International technical dimensions FAQ, section2:
  https://www.xbrl.org/guidance/technical-dimensions-faq/

A closed cube excludes unexpected dimensions. An open cube permits additional
reported dimensions without relaxing its own required-dimension validity. This
implementation uses a deliberately conservative open subset: every extra reported
axis must itself have a supplied usable explicit declaration and single-domain
network in the same role. Its member must belong to that domain, and an explicit
default member is rejected. Unknown/typed axes or domains are not accepted merely
because the primary cube is open. Existing cube defaults are documented in proof
without synthesizing context data or consolidating dimensioned values.

The supported network remains one definition link and role, one direct positive
all assignment, one to32 hypercube dimensions and at most32 combined required and
additional axes. Domain graphs remain bounded to2048 members and32 levels, with
cycles rejected. Every selected fact must have a direct assignment; inheritance,
negative/multiple assignments, empty cubes, target-role switching, typed dimensions,
unusable members, unsupported precedence and opaque/wrong-container contexts remain
explicitly unsupported. This is not a complete XDT validator.

V2 produces `gig.sec.xbrl.dimensional_instance.v2` or
`gig.sec.xbrl.dimensional_inline_set.v2` with an exact-profile dimensional proof.
Per-fact records add `closed` and sorted expanded `extra_dimensions`; original
fact/context/declaration/source identities are preserved. Derived-schema and proof
profile must agree. Defaults remain unavailable as consolidated financial data,
and actual dimensioned contexts remain excluded by selected financials. The
`complete_drs_validation` flag stays false.

Sixteen authored regressions cover additional membership/default/declaration checks,
legacy refusal, closed/open behavior, required/defaulted dimensions, unsupported
negative/inherited/role/cycle/typed scope, container and combined-axis limits,
atomic collection admission, derived-proof refusal, and original inline provenance.
No provider, network source, application or accounting equivalence is involved.
