# Phase7 product and reliability checkpoint

Integrated working product changes,not mockups:

* Stock Overview now exposes a separate permission-gated IEX stream panel. Status polling
  every5s never initiates acquisition. Explicit start replaces1–4-symbol subscription;
  stop closes transport. Only accepted observations display quote/print fields,source
  timestamps and LIVE/SIMULATED/STALE/UNAVAILABLE classification. IEX is never NBBO/depth.
* Private archive adds revision selection,explicit weights,exact shared-interval analysis,
  immutable identity/exclusion disclosure and rational risk values. Edits invalidate prior
  results. Authored derived JSON export is browser-local;observed export remains disabled.
* Quant & Risk adds the separate bounded conditional GARCH search with convergence,
  likelihood/source receipts and explicit limitations. Existing grid/held-out models stay
  visible and unchanged;new fitting is not silently substituted into existing evaluations.
* Company search,selected financials,filings,all9 existing navigation workspaces,replay,
  native simulation,optional3D,operations,dark/light themes and privacy controls preserved.
  Risk remains integrated in Stock Intelligence,not a newly claimed tenth independent route.

Browser qualification:original7 suites91 assertions,Phase4 nine,Phase5 six,and5 new final
journeys. Final journey exercises company selection,authorized authored ingestion,pinned
revision/exact risk,JSON export content and invalidation,GARCH diagnostics,360/390px themes,
keyboard focus,native WebSocket continuity and return to Command Center. Previous90
workspace/theme/width combinations(360/390/768/1280/1920) and NVDA→AAPL regression preserved.
All assets built before original suites,hashes checked throughout;no build/test race.

Actual local screenshots:build/final/visual/{dataset-research-dark,garch-search-dark,
final-mobile-light,final-mobile-dark,return-command-center}.png. Representative desktop
research and mobile renderings inspected. Manifest records32 total screenshots from
current original/Phase4/5/final runs. These contain clearly labelled authored fixtures;
not provider screenshots,physical Android or external Codespaces authentication evidence.

Initial JS230732 bytes;optional Stock Intelligence70384 bytes;OrbitControls/Three507532
bytes remain deferred. Build reports optional-chunk warning;not suppressed. Reduced motion,
semantic details/forms/labels,focus visibility and mobile container checks retained. Full
WCAG2.2AA,screen-reader and physical-device qualification NOT VERIFIED. No new frontend
framework or production dependency. Safe closure/performance evidence in Phase8 report.
