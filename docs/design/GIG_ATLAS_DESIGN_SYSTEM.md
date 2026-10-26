# GIG ATLAS design system

October25,2026 America/New_York. Baseline805294762f55efbbeb6fd988f7b8d842eb474654.
This is an implemented additive design system,not a replacement native engine.

## Visual language

Institutional depth through clear hierarchy,restrained surfaces and exact source labels.
Original GIG wordmark and system typography;no proprietary interface assets,remote fonts,
chart framework or additional production dependency was introduced.

| Token | Dark | Light |
|---|---|---|
|Canvas|#10151e|#f2f5f9|
|Surface|#171f2c|#ffffff|
|Raised|#1c2838|#e9eff7|
|Primary text|#e9eef7|#17263b|
|Secondary text|#a7b5ca|#4e6078|
|Border|#34445b|#c5d0df|
|Blue|#85b8ff|#1757a1|
|Positive|#7ddbb5|#116844|
|Negative|#ff9c94|#a62f30|

`terminal/web/src/atlas.css` defines these variables and integrates existing components.
Spacing generally uses4/8/12/16/20/24/28px;surfaces use8–12px radii,subtle elevation
and visible borders. System fonts use tabular numerals. Body14px,financial values23–27px,
section titles23px,page title28–34px. Small provenance text remains10–12px;this is a
known area for physical-device usability review rather than a WCAG certification.

## Implemented primitives

Shared surfaces,cards,table containers,segmented button groups,inputs,search results,
status/provenance badges,empty/error states,native disclosure panels,skeleton blocks,
visible keyboard focus,skip link and a native modal help dialog. Chart descriptions and
exact-value tables complement SVG trends. Native title hints are supplemented by
expandable text;do not put essential mobile information only in a hover tooltip.

Themes persist under `gig.atlas.theme`;a storage failure does not prevent rendering.
Reduced-motion preference disables presentation animation/transitions. Financial
skeletons indicate unresolved loading and never stand in for actual observations.

## Financial presentation rules

* Compact dollar labels are rounded for display with BigInt arithmetic;exact provider
  strings remain in expandable detail. Missing is “Unavailable”,distinct from$0.00.
* USD/share is explicit. Backend rational percentages/multiples change presentation
  units only;financial formulas are never recomputed in JavaScript.
* Synthetic,observed response,cached,theoretical and simulated classifications remain
  visible. Configuration readiness is not provider permission or source validation.
* Charts require unambiguous comparable periods;no invented intermediate observations.
  SVG coordinates are approximate visual projections;exact source values are retained.
* Financials are selected reported facts,not complete reconstructed statements.

## Responsive/accessibility policy

Persistent labelled desktop navigation becomes horizontally scrollable labelled mobile
navigation. Tables scroll inside bounded focusable containers. Summary cards stack on
small phones;Trends/Statements/Ratios render on demand to reduce scrolling and DOM size.
All five specified widths are browser tested. Token text/link contrasts are checked
against4.5:1;this does not certify legacy canvas colors or the entire application.


Phase 2 recovery: see [Phase 2 report](GIG_ATLAS_PHASE2_REPORT.md) and
`gig_atlas_phase2_evidence.json` for current refinements,stable-build browser checks,
viewport screenshots,performance observations and remaining accessibility limits.
