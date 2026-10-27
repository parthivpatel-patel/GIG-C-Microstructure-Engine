# Final bounded engineering readiness and acceptance plan

Current full-scope assessment: [DEVELOPMENT_SCOPE_AUDIT.md](DEVELOPMENT_SCOPE_AUDIT.md).
This report remains a historical checkpoint; its bounded-closure judgment is
superseded by the full original-requirement audit and additional implementation.


Baseline:ff41c97abbd79012ea9232eb56dfb5481e5f94c2.
This closes the reproduced defects found in the current pass. It does not certify
absence of all defects or complete the broader optional product roadmap.

## Completed justified engineering

1. **Medium:stream projection integrity.** Full frames previously accepted an
   inconsistent receipt baseline;legacy/projected frames could mix on one reader;
   channel changes could arrive as deltas;extra status tuple fields were ignored.
   Negative controls reproduced these omissions. The reader now rejects them before
   publishing state. A connection stays on its initial negotiated profile,with a new
   reader/full window after reconnect. Channel/symbol/generation changes require full
   synchronization. Legacy full streams remain supported as a consistent profile.
2. **Medium:persistence diagnostic publication.** SQLite append/prune transactions
   released their shared writer lock before assigning cached metadata. The minute
   retention worker could race source append and overwrite a newer summary. The writer
   lock now spans durable commit and non-fallible cached-summary publication. A portable
   lock-ownership regression fails before repair on both append and prune. An actual
   two-thread200-append/100-prune stress test checks summary,chain and recovery agreement.
   This repairs diagnostics,not a claimed SQLite transaction corruption. Existing
   rollback,process-exit,expiry/corruption and resource-budget tests remain intact.
3. **Medium:lost graphics context.** Actual WEBGL_lose_context injection reproduced
   both renderers remaining on a dead canvas without the declared fallback. They now
   stop render work,clear stale selection where applicable,dispose controls/listeners/
   geometry/material/renderer resources,release the context and show an explicit 2D
   alternative. Retry rebuilds only that renderer from retained observations. It does
   not restart the provider socket,change subscriptions or mutate the native book.
   Native 3D also gains focusable canvas/keyboard camera controls. Software-renderer
   tests9/9 cover both failures,retry,state isolation and keyboard movement. This is
   not physical GPU or Android qualification.

Measurement tools also accept GIG_MARKET_EVIDENCE for separate output directories,
so a new run need not replace an earlier run's artifacts. No dependency was added.

## Every remaining matrix item:disposition

The following table covers all distinct PARTIAL/BLOCKED/NOT IMPLEMENTED items from
the existing matrix,including historical aliases. COMPLETE rows need regression
maintenance and eventual acceptance,not speculative replacement implementations.

| Matrix item | Disposition | Required work or reason to stop now |
|---|---|---|
| Owner's external Codespaces authentication | External qualification | Authenticate private forwarded port on actual owner devices;local proxy tests cannot impersonate that identity |
| In-place subscription handover | External qualification | Offline lifecycle is implemented;qualify actual entitled provider acknowledgements and disclosed capture gap |
| Minimal per-symbol delta optimization | Optional future | Existing bounded unsubscribe-all/subscribe is correct;optimize only against measured need and authoritative provider semantics |
| Complete exchange sequence/exactly-once tape | Source limitation/external | No exchange sequence/completeness authority exists in current contract;software cannot infer it |
| Quotes/trades/basic OHLCV bars | External qualification | Implemented/fixture validated;account/feed acceptance needs authorized observations |
| Updated/daily bars/status/LULD source profiles | Optional future plus source qualification | Require reviewed authoritative profiles before extension;current unsupported messages fail explicitly |
| Reconciled corrected trade tape | Optional future | Required before claiming corrected net volume;current affected aggregates stay unavailable rather than wrong |
| Source reconnect/recovery | External qualification | Fixture lifecycle/backoff/resubscription is implemented;qualify against actual provider interruptions,not a synthetic success claim |
| Exchange/network latency estimate | External clock authority | Unsynchronized clocks support age diagnostics,not a defensible one-way latency estimate |
| Browser snapshot bandwidth optimization | Current contract closed | History projection and40 exact cross-language comparisons pass;further field compression is optional,not a correctness gap |
| Backend transport queue depth/exchange drops | Optional diagnostics/source limitation | Public transport bounds are enforced;do not add private-library introspection or invent unknown exchange drops |
| Authorized directory search | External qualification | Generic bounded catalogs and SEC resolver exist;current source listings/entitlement need official acceptance |
| Actual provider directory acquisition/qualification | External authorization/source | Requires allowed access,documented rights and current source reconciliation |
| Sustained GPU/context-loss qualification | Engineering closed for loss handling;external hardware | Software context loss/retry is now verified;physical GPU/device sustained stress remains open |
| Mobile/accessibility | Bounded engineering validated;external full audit | Five widths/nine-workspace themes,labels,focus/reduced motion/keyboard alternatives tested;physical device and full WCAG/screen-reader audit remain |
| Authoritative current calendar/halts | External source plus optional profile | Existing schedules are explicitly supplied/partial;no fabricated market-open or halt state |
| Observed complete equity L3 validation | External evidence and separate scope | Requires permitted complete source history,independent initialization/order identity and reference evidence |
| Licensed live equity L2/L3 | External entitlement | No depth is generated from L1;an entitled source is mandatory before adapter qualification |
| Full accounting/XBRL presentation/vintage completeness | Optional broader product scope | Selected reported facts are supported;full XBRL contexts/presentation require a separately bounded implementation/oracle,not a cosmetic completion claim |
| Empirical forecasting/OOS validity | External research evidence;optional forecasting scope | Models are labelled demonstrations;calibration/OOS claims need adequate authorized observations and independent research design |
| Crash-safe hot live/L3 recovery | Optional separate architecture | Current SQLite ledger recovers historical observations,not hot native state;hot recovery needs authenticated source/checkpoint/joint-state design |
| SEC/live provider reconciliation here | External configuration/qualification | Identifying SEC configuration and provider credentials/rights are absent;do not retry blocked operations |
| Exact-candidate ARM64/hosted CI | External authorized infrastructure | Manual gated workflow exists;the current SHA needs an actual authorized run,not inherited qualification |
| Complete authenticated SEC PIT/XBRL database | Optional broader scope plus source evidence | Same full-XBRL boundary;no complete historical response availability claim is supported |
| Observed provider/storage acceptance | External permission/qualification | Requires explicit processing/display/retention rights and accepted actual observations |
| Actual authoritative APLD/CRWV reconciliation | External SEC configuration/source | Default CIKs remain null;official directory fetch/issuer reconciliation must succeed before promotion |
| Full authenticated XBRL/PIT source history | Optional broader scope plus source evidence | Historical filing metadata and bounded revisions do not authenticate past companyfacts responses |
| New-candidate actual ARM64 qualification | External infrastructure | Same exact-SHA gate;workflow was neither dispatched nor registered on main by this task |
| Actual live provider/recovery/retention qualification | External qualification | Same account,source,interruption and retention acceptance gates;fixtures remain synthetic |

There is no remaining reproduced defect from this pass. No new speculative feature
is added solely to turn these limitations into green cells. Broader roadmap engineering
remains PARTIAL;this is closure of the implemented bounded research-terminal scope.

## Eventual final acceptance:exact required evidence

Perform only after development is frozen and necessary authorization is established.
This list is not a request for intermediate manual owner tests.

1. **Candidate identity/reproduction:**record the exact feature-branch SHA,clean source,
   toolchain/dependency versions and locked setup. Reproduce production frontend build,
   relevant backend/native consumers and all eight frozen native hashes. Source archive
   must contain intended byte-identical source and no private data/configuration.
2. **Private browser transport:**use the authenticated private Codespaces port8787 HTTPS
   origin. Verify exact configured origin,one-use endpoint-bound HTTP proofs,native WSS
   and stock SSE;cross-origin,forged forwarding,reused/mis-targeted proofs must fail.
   Reconnect must start from a full accepted window and never show stale data as live.
   Record sanitized status/reasons only,no cookies,tickets,contacts or keys.
3. **Official SEC acceptance:**with valid identifying configuration and reviewed fair
   access,perform bounded official requests. Independently reconcile AAPL/APLD/CRWV
   symbols/CIKs to returned source records and hashes. Missing mappings stay null.
   Verify issuer consistency,accessions,amendments,units,periods and acceptance cutoffs.
   Same-day ambiguous/unknown availability stays unavailable;no look-ahead substitution.
4. **Authorized L1 acceptance:**establish actual account/feed/private-display/cloud
   processing permission first. Verify source quote/trade fields and timestamps,default
   four-symbol/restrictive limits,quiet-feed liveness,late/duplicate handling,acknowledged
   handover,interruptions/reconnect and truthful freshness/status. Bound retained windows,
   client slots and resource use. No NBBO,depth,complete tape or exchange latency claim.
5. **Storage acceptance:**only with documented retention permission,enable explicit
   opt-in policy/seconds/private directory. Verify bounded durable records,atomic frame
   failure,restart chain/tail checks,expiry and no live relabeling. Account for rollback
   journal,disk/backups and offline-host deletion limits. Recoveries are historical only.
6. **User/device acceptance:**exercise all nine workspaces,dark/light,five target widths,
   actual desktop Chrome/Android,keyboard/screen-reader alternatives,global selection,
   filings,simulation/research labels,multi-stock controls and visual source separation.
   Inject context loss/retry on intended hardware;2D alternatives must remain useful.
   Collect sanitized screenshots/resource measurements and record any hardware gaps.
7. **Independent machine/ARM64:**owner-authorized eligible free infrastructure must run
   the manual branch-gated candidate workflow on the exact chosen SHA. Capture actual
   ARM64 architecture,all six job conclusions,strict test counts,eight hash matches,
   package checks and run IDs. Older runs or static workflow tests do not pass this gate.
8. **Closure:**review all evidence,privacy and remaining scope. Any failure blocks its
   acceptance gate. No merge,release,provider activation or trading operation is implied.

## Assessments

**Engineering:**the implemented bounded scope is ready for controlled final acceptance
once external prerequisites are met. Confirmed defects in this pass are repaired and
automatically tested. This does not mean every optional roadmap capability is complete.

**Production:**NOT READY. Real-source/account acceptance,exact-candidate independent
qualification,operational guarantees,hardware/accessibility evidence and any broader
claimed research capability require their own supporting evidence. This is a private
research terminal,not a production trading system or a complete PIT/L3 data authority.
