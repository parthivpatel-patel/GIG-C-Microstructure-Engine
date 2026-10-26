# Known limitations and remaining engineering work

1. BLOCKED:Alpaca381230 rights/account entitlement;credentials/provider endpoint access
   and actual private browser display qualification. No account ownership inference.
2. PARTIAL:IEX SDK-grounded quote/trade profile;corrections/cancels/other family semantics
   fail explicitly. Provider error codes preserved without invented entitlement meanings.
3. NOT VERIFIED:actual provider proxy/TLS negotiation,reconnect timing,rates,stale market
   periods and subscription caps. Offline fake transport is not observed qualification.
4. PARTIAL:history raw paging/storage;no authoritative session calendar,corporate actions,
   cursor resumption,page-to-row source partition or complete exchange history.
5. PARTIAL:multi-revision exact interval intersection;no implicit missing fill/FX;equal
   generic price-unit strings do not independently verify actual settlement currency.
6. PARTIAL:selected financial facts/descriptors/checks;no complete XBRL dimensions,
   presentation/contexts,complete fiscal calendar or statement reconstruction.
7. PARTIAL:retained filing-date vintages;older truncated facts cannot be recovered;no
   intraday acceptance-time trading authority. Official SEC reconciliation owner-blocked.
8. PARTIAL:HMM Baum-Welch/two-state local fits;fixed-parameter missing-data filtering is
   not missing-data EM or broad model-selection/calibration evidence.
9. PARTIAL:GARCH conditional constrained search fixes mean/initial variance;finite budget,
   local solutions,no Hessian/global MLE/parameter uncertainty or empirical advantage.
10. NOT VERIFIED:observed OOS/walk-forward calibration,model uncertainty and causal alpha.
11. PARTIAL:portfolio explicit rebalanced weights;no holdings/FX/calendar authority,
    financing/liquidity/cost constraints or empirically calibrated tail coverage.
12. PARTIAL:private storage quotas/access expiry/backup;no global filesystem quota,
    guaranteed physical erasure,cross-process restore contention or power-loss HA.
13. NOT IMPLEMENTED:benchmark-gated native journal compaction/migration. Baseline preserved.
14. NOT VERIFIED:exact-HEAD ARM64/hosted success,external Codespaces,physical Android and
    comprehensive screen-reader/WCAG2.2AA qualification.
15. BLOCKED:observed Level3 correctness without licensed complete initial state/reference.
16. PARTIAL:release candidate package;no public tag/release/main merge or production claim.

The explicit price-unit conflict discovered during final review was reproduced before
repair and is FIXED with regression coverage. No known failing local final test remains.
Concurrent ingestion busy diagnostics were also repaired(409 rather than generic422);
load/request completion synchronization is explicit in the browser regression.
This list is substantive remaining engineering,not merely external permission paperwork.
Reserve November7–10 for integration/critical fixes/security/browser acceptance;defer
speculative features. If external gates remain unresolved,deliver a disabled-provider
research candidate. November10 is a target,not an evidence-free readiness assertion.
