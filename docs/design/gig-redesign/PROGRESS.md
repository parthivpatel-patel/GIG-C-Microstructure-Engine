# GIG redesign durable checkpoint

Branch `development/gig-ui-redesign`,exact Sprint4baseline `0c03a698fdac1be8b1032b255208a3ef2320341a`. Created in an isolated worktree after verifying no existing local/remote target branch. Sprint4/release/main remain preserved. Continuation found surviving camera implementation;it was not discarded or recreated.

Implemented a shared camera-only30Hz lifecycle with frame-time movement,interaction suspension,reduced-motion/visibility/intersection/data availability gates and explicit cleanup. Wired all five renderer families (native depth,advanced laboratory,L1cloud,GARCH,option surface) with independent pause/resume and preserved manual controls/fallbacks. Twelve focused deterministic lifecycle tests pass;production TypeScript/build and114frontend tests pass. Browser verification and complete new institutional shell/order-book/design-system implementation follow;this is not a completed visual qualification.

Exact next action:implement new GIG shell/navigation,readable bid/ask ladder and unified system-font theme,then actual browser visual/motion/recovery regressions. No backend/native/provider/permission change is authorized or made.

## Institutional interface checkpoint

Implemented new Navigation,TerminalHeader,WorkspaceLaunchpad and exact two-sided OrderBook components. System font stack,GIG identity/browser title,shared high-contrast dark/light themes,larger canvases,rank-aware cumulative depth and readable native numbers replace the previous shell. Replay/session configuration and concentration controls use progressive disclosure;playback remains directly available. Existing global search/API proofs/12workspaces/15visualization modes/backend policies are preserved.

Removed the three superseded stylesheet entrypoints after consolidating used workspace contracts into readable workspaces.css/new authoritative terminal.css. Removed61overwritten declarations and148superseded shell selectors;internal atlas-* identifiers remain stable. Renderer code was formatted with the pinned TypeScript printer,not rewritten mathematically. Ask geometry now uses coral rather than amber:384baseline comparisons show identical source,coordinates,numeric values,axes and labels excluding the intentional color change. Old/new display hashes are recorded;all8native identities are unchanged.

Production TypeScript/build and118frontend tests pass. New Chromium program passes10checks including48workspace/theme/width paths,real visible-scene camera movement,pause/resume,offscreen intersection,controlled visibility event,reduced media preference,context loss/retry and cleanup. Advanced pause intent survives context recovery.274backend tests,8native reference tests and independent native oracle pass. Existing broad browser programs are still running;final screenshots/contrast/evidence review follows.

Initial development failures retained:TypeScript unknown-scale ReactNode and JSX wrapper syntax corrected;test runner parsed arguments were shadowed by its server loop and renamed;new tests now explicitly enable the pre-existing optional3D renderer,create a real offscreen layout,use the existing9draw-call ceiling,and await replay POST completion before asserting camera-only source stability. Original mathematical/safety assertions remain unchanged. No provider operation,credential access or backend/native change occurred.
