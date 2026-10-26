# Financial intelligence

**PARTIAL,implemented and fixture-tested:**existing16 selected metrics extended with
cost-of-revenue aliases,investing/financing/FX/net-cash-change tags,basic EPS and diluted
weighted shares. EPS uses USD/shares;weighted shares use shares;no monetary conversion.
Independent SEC reconciliation script has a separately declared matching taxonomy profile.
Existing12 descriptors/formulas,source identities,filing vintages,as-of policy and exact
arithmetic preserved. No source value is changed to force an equation to balance.

accounting.py adds exact same-period/same-USD residual diagnostics:
assets−liabilities−stockholders-equity;revenue−cost−gross-profit;CFO+CFI+CFF+FX−cash-change.
Every component must be uniquely reported for the same start/end. Missing/competing
concepts yield null/unavailable,not zero. Results retain source facts. Zero residual says
only SELECTED_COMPONENTS_EQUAL,not full statement reconciliation. Nonzero residual can
reflect noncontrolling interests,cash scope/taxonomy or context differences;not an automatic
engine defect or fraud claim. EPS numerator/rounding adjustments are not inferred.

Statement API/UI includes these checks from the same accepted financial object as its
period packets. Original raw fact tables and exact descriptors remain. Tests cover exact
positive balance/gross-profit/cash-flow identities,missing FX,competing concepts and share
units using authored raw facts through the actual normalizer.

**BLOCKED here:**official SEC reconciliation;identifying User-Agent absent. Owner should
use the existing reviewed Codespaces SEC settings and scripts/qualify_sec_sources.py,
not fabricate contact information. **NOT IMPLEMENTED:**official company directory refresh,
full XBRL dimensional/presentation/context reconstruction,full statements,automatic fiscal
calendar reconciliation and original intraday filing-vintage authority. Curated CIK seeds
remain checked against accepted SEC CIKs but not independently re-certified here.
