# Keyboard search and exact order-book inspection

Reviewed November 21, 2026 (America/New_York). This package repairs two concrete
code-level accessibility gaps in the existing GIG workspaces. It does not certify
WCAG 2.2 AA, real browser/device behavior or assistive-technology acceptance. No
application/server/browser/provider was started; no dependency was added.

## Observed gaps and resulting behavior

The global search previously rendered result buttons in an unlinked generic region.
Tab could reach those buttons, but the search input exposed no expanded/listbox
relationship, active result or successful-result live announcement. The new input is
a named combobox linked to a uniquely identified listbox. Up/Down Arrow choose an
active result while DOM focus stays on the input; Enter opens that exact result.
Escape dismisses the supplied results while keeping the query. Tab remains native
navigation. Enter with no active result remains the normal search submission.
Home/End, text-editing keys, modified keys and input-method composition are not
captured as option selections. Active option state is tied to both query and exact
result snapshot, so replaced, reordered or relabelled results cannot reuse a prior
active index. App now uses a separate directory-request lifetime guard. A query change or Escape
invalidates its previous query context immediately, even when text stays unchanged.
Opening a company invalidates the context and clears search feedback. Replaced
requests have separate revisions; only the newest success or error may publish.
Option callbacks additionally bind the query/request selection revision of their render, so an old
same-query option cannot select after a replacement request, even before rerender.
Effect cleanup/replay invalidates pending request tickets while preserving the
selection revision of current rendered options; unmount still closes all admission.
Captured handlers from an earlier same-query context cannot start new work. Unmount
closes admission, and effect cleanup/replay reopens valid current handlers without
reviving earlier requests. The existing bounded request timeout/transport API is
unchanged: invalidation suppresses results/errors, not a claim of network abort.

Result counts and supplied empty/error messages use one persistent polite atomic
status container, with visible messages retained. App request failures retain its
existing global alert banner; obsolete failures cannot replace current feedback. Native input instructions describe the available keys.
Popup/instruction IDs are unique per component instance; active descendants refer
to actual options. Options remain pointer-operable and outside the Tab sequence
because input-focused arrow selection supplies their keyboard path. Selected-option
outline uses existing theme tokens and adds no animation. The existing search
shortcut now respects inherited content-editable state and composition.

Order-book raw integer values previously appeared only in a row title while the
visible formatter can truncate beyond eight decimal places. Each row now provides
a native details/summary control with an exact side/price-tick accessible name and
a definition list containing price ticks, quantity integer and displayed cumulative
quantity. This retains actual accepted integers, including sums beyond uint64 and
binary64, without Number conversion or a hover dependency. Non-action row tab stops
are removed; named, focusable bid/ask scroll regions and native table header scopes
remain. Existing normalized display, scales, visible-level bounds, ordering and
source/coverage disclosures are unchanged. These raw integers are accepted contract
values, not independently reconstructed original provider lexemes.

## Automated developer evidence

`terminal/web/src/accessibilityNavigation.test.ts` renders the actual Header and
OrderBook leaves with React static markup and exercises the keyboard admission
helper used by the component. Its 28 tests cover collapsed/expanded relationships,
unique IDs, named options, polite error/result announcements, escaped source labels,
arrow entry/wrap, Enter/Escape, IME/modifiers/native editing, invalid counts, stale
selection signatures, exact truncated/large values, scopes/regions, empty books and
compact/expanded depth. The tests preserve input data and displayed-only totals.
Eight of these cases exercise the actual async admission runner used by App, using
controlled promises for replacement, query changes, selection/dismissal, unmount,
effect replay, stale handlers and current synchronous/asynchronous failures. Two additional cases exercise the actual
selection runner used by App, rejecting old query/dismissed/unmounted callbacks and
same-query options captured before a request replacement.
These are SSR and deterministic logic checks, not actual DOM focus or screen-reader
measurements. The source helper has no request, provider or financial semantics.

From the repository root, with installed locked dependencies:

```sh
node --experimental-strip-types --test terminal/web/src/accessibilityNavigation.test.ts
npm --prefix terminal/web test
npm --prefix terminal/web run build
```

Parent integration registers the new test in the retained frontend suite. Logs are
in `work/nov21-accessibility/` with TypeScript/build diagnostics retained separately.
Final evidence owns the exact source SHA and total integrated count; overlapping
cohorts must not be summed. Existing source-import and twelve-workspace checks stay
in the broad suite. Native identities and data contracts are untouched.

## Exact later physical/browser/AT acceptance procedure

This procedure requires separate authorization to launch the exact candidate and
use named real targets. It is not executed by this package. Use permissioned supplied
source fixtures or a separately authorized source; a provider subscription is not
needed to assess this widget's keyboard behavior. Bind the candidate SHA, actual
browser/OS/AT versions, physical viewport/device, theme, zoom and source identities
to each receipt. Record failures as findings rather than assuming these checks pass.

1. In desktop keyboard mode, invoke global search by Ctrl/Cmd+K and by slash outside
   editing controls. Confirm visible input focus. In an inherited content-editable
   control and during IME composition, slash/confirmation must remain editing input.
2. Submit a bounded directory search. Record the actual screen-reader announcement
   for one, several and no results, plus an unavailable/error response. Verify the
   expanded/listbox relationship and named options in the real accessibility tree.
   New query/result snapshots must remove any obsolete active descendant.
3. Keep DOM focus on the input. Verify Down starts at the first result, Up starts at
   the last, repeated arrows wrap and the active option scrolls into view. The AT
   must announce the same exact company/symbol highlighted by the visible outline.
   Enter opens only that active result. Escape closes results without changing text;
   Tab leaves normally; Home/End and modifier combinations retain native editing.
   Inspect parent workspace focus/announcement after selection separately. Delay an
   earlier search response or error until after a replacement query, Escape, company
   selection or unmount: it must not reinstall obsolete results or feedback. The
   guard repairs request admission; physical workspace focus remains a separate check.
4. On actual touchscreen/mobile targets with VoiceOver or TalkBack, assess the
   combobox/listbox accessibility tree, option exploration and double-tap selection.
   Test existing keyboard modes separately where the physical device supports them.
   Do not infer mobile support from desktop SSR or viewport emulation.
5. In Order Book, use keyboard-only focus to reach each named scroll region and the
   exact-value summary. Enter/Space must open/close the native disclosure. Confirm
   assistive output associates bid/ask, price ticks, quantity and cumulative integer.
   Use a permitted fixture with price scale 10^9 and price ticks3 to distinguish the
   formatted `0.00000000…` from the exact integer3; include cumulative quantity
   36893488147419103230. Neither value may be rounded or silently omitted.
6. Check real table header relationships and reading order, expanded disclosures,
   empty sides and compact/40-level views. At 200%/400% zoom and a real narrow mobile
   viewport, verify scrolling, wrapping, focus visibility and reachability without
   clipping exact digits. Check dark/light themes and reduced-motion preference.
   No color-only selection or hover-only exact information may be required.

Retain actual pass/fail observations and accessibility-tree/screenshots/AT output
where permitted, with hashes and source provenance. Browser focus, virtual-cursor
behavior, pointer target size, contrast and full WCAG/device acceptance remain
unverified until those real tests run. UX02 stays PARTIAL; other external blockers
and the current observation-only scope remain unchanged.
