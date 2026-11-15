# Explicit negative-only hypercube profile with global defaults

`NEGATIVE_ONLY_EXPLICIT_HYPERCUBES_V5` adds an opt-in single-role subset whose
applicable inherited/direct assignments are exclusively `notAll`. The mixed profile
remains V4; applicable positive assignments reject under V5 rather than silently
switching modes. Original V1–V4 defaults, refusals, schemas and canonical outputs are
unchanged. No cross-role OR operation or typed-hypercube semantics are introduced.

Authoritative basis: XBRL Dimensions1.0, Recommendation18 September2006 with
corrected errata to25 January2012, sections2.6–2.7.1,3.1.2 and3.1.4:
https://xbrl.org/specification/dimensions/rec-2012-01-25/dimensions-rec-2006-09-18%2Bcorrected-errata-2012-01-25-clean.html .
An exclusively negative assignment is satisfied when its supported cube is invalid
for the context. Applicable negative assignments are combined conjunctively in the
same base set. Declared dimension defaults are global within their domain scope and
must not be explicitly reported as context members. A missing dimension with a
valid default can make a cube valid, in which case its `notAll` rejects the primary.

V4 depended on a valid positive cube to admit the reported context before exclusion
checks. V5 replaces that prerequisite with independent global admission: every
reported explicit axis/member must have a supplied usable declaration/domain and
must not report a default member. Every declared default is validated against its
explicit dimension and supplied domain, even when no applicable cube uses it.
Repeated default-axis arcs, conflicting/outside defaults, unknown/typed declarations,
domain cycles, opaque/wrong-container contexts and resource errors reject before
negation. Only the same narrow V4 contextual cube-invalid outcomes can satisfy an
exclusion; unsupported/schema/default/resource failures never become witnesses.

Global defaults are retained as derived aspect metadata, without rewriting any
original fact or context. `used_defaults` contains exactly the global-default axes
absent from that fact's original reported context. A reported nondefault member
therefore supersedes its implicit default. This conservative selection policy keeps
an otherwise empty context with unrelated implicit defaults from being promoted to
a consolidated value. A default-free dimensionally valid empty context may retain
its original unqualified reported numeric fact; no missing value is imputed.

The profile retains one definition link/role, one common segment/scenario container,
usable explicit domains, at most64network assignments and16applicable assignments,
2048node/member and32level graph bounds. At most32global defaults and32combined
global/reported/applicable axes are admitted. Existing source and8MiBderived-output
limits remain. Multiple definition links/roles, targetRole, typed axes, unusable
members, arc precedence/prohibition and empty cubes remain explicitly unsupported.
This is not general XDT conformance or complete OIM/accounting acceptance.

V5 produces `gig.sec.xbrl.dimensional_instance.v5` or
`gig.sec.xbrl.dimensional_inline_set.v5` and an exact-profile proof. Fact records add
`global_defaults` to the V4 group shape. All assignments are `notAll`, valid=false,
with a specific contextual failure reason and empty assignment `used_defaults`.
Top-level implicit-default provenance comes from the globally checked map rather
than a failed cube. Original source/fact/inline identities are preserved. The
complete-DRS flag remains false. Selected financials rejects relabeling, bad proof
shapes/outcomes and any mismatch between global defaults, reported dimensions and
the derived used-default map. Original-byte audit is still required for independent
reconstruction of supplied metadata; self-hashes alone are not source authentication.

Twenty-two authored fixtures cover negative-only inheritance, global/default-free
contexts, default overrides, closed extras with unrelated defaults, valid-negative
rejection, invalid reported contexts, legacy/mixed refusal, all-cube conjunction,
global duplicate/domain/cycle/default and32/33axis budgets,16/17and64/65assignment
limits, primary cycles, atomic collection admission, original inline lineage and
thirteen rehashed proof-corruption variants. Initial tests also retained expected
pre-integration unknown-V5 selection errors. A diagnostic-order fixture led to V5
preflighting duplicate default arcs before domain evaluation; all underlying failures
remained fail-closed and its assertion was retained. Current focused/related checks
pass. No application, provider, external filing or accounting equivalence is involved.
