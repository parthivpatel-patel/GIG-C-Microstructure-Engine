# Full ITCH product sessions — November 11, 2026

`terminal/server/app.py:create_app` now calls the explicit `select_product_session` policy. The default remains the existing authored-native session. Importing the app module no longer constructs an application: the existing `terminal.server.app:app` ASGI export is lazy and is created only when explicitly requested by the operator's launcher. No launcher,ASGI factory,listener or provider is run by the offline verification commands.

## Explicit private selection

The server-owned selection contract is `GIG_TERMINAL_SESSION=itch`, `GIG_ITCH_SESSION_PATH` and an independently retained `GIG_ITCH_SESSION_SHA256`. All three are required. Unknown session kinds,incomplete pins,corrupt files,unsafe ownership/modes,unknown versions and unapproved code/binary changes fail closed. Configuring paths while leaving the default session selected also fails rather than silently ignoring recovery intent. No setting is enabled by this change. Browser controls cannot supply filesystem paths,hash authority or provider destinations.

The selected NativeSession is restored paused without the default20-event restart. It owns the complete native/context artifact,source/capture/generation/configuration,receipts and source cursors. Both books remain independent. The actual product state API uses native snapshots and exact native book metrics,with source/provenance labels;the selected book is a control,not a guessed equity ticker or SEC identity. The product projects native prices and quantities back into exact source Price(4)/shares using the native-validated context price quantum and share lot. This also supports nonunit native ticks and lots without rounding. Native snapshots,configuration and metrics remain available unchanged;display metric amounts are converted by exact rational unit factors,not recalculated analytics. The source-unit projection is explicitly labelled in provenance.

The private bundle includes the full durable image,admission,binary identity,selected book,speed,migration lineage and a bounded authored continuation. Maximums are48MiB bundle,32MiB native artifact,2MiB/256 continuation records,and4 migration records. All supplied suffix records are preflighted in isolation before selection. Unknown/partial/terminal frames fail admission. There is no provider connection,observed storage or trading operation.

## Replay and persistence

The minimum replay position is the selected checkpoint's committed source count. Replay cannot seek into missing earlier history. A sequential step restores the latest hot boundary and applies exactly one new record;committed prefix or suffix events are not reapplied. Explicit historical seek is a separate operation that reconstructs only the supplied post-checkpoint range in isolation. Candidate errors and actual native budget exhaustion leave the accepted owner untouched. End/error state remains paused.

Capture persists the current full image and only its remaining continuation. Reopening starts paused at that current boundary. Immutable private publication reuses the existing checked writer: complete write,file fsync,exclusive new link,directory fsync. A new revision never replaces rollback input. Tests cover before-publication disk faults,after-publication uncertainty and actual child-process exit after linking. These are local filesystem/process observations,not hardware power-loss or RPO/RTO guarantees.

Switching to the existing authored source remains available. A server-pinned ITCH selection can be selected again through its known dataset ID;the browser cannot nominate another checkpoint. The Replay UI exposes both source-bound book choices,the correct minimum seek position and continuation-scoped progress. Live connection and simulation controls require switching to their appropriate dataset. No L1 feed is reinterpreted as order-level depth.

## Explicit migration

The native artifact remains version1. Product revision1 remains supported;revision2 adds the bounded source-recovery lineage described in ITCH_SOURCE_PRODUCT.md. `ItchRecovery.migrate` admits old trusted bytes against the current native invariants and canonical state,re-encodes the same source/config/capture/generation under the target code identity,and validates again. The product migration target is derived from the actual native binary and product/engine source files. Original source bytes remain unchanged;the new bundle records source bundle/image/implementation/binary hashes. Migration is explicit,bounded and never automatic. It does not establish equivalence of arbitrary historical algorithms or provide an unknown-schema converter.

Offline operator commands are available without starting GIG:

```bash
<venv>/bin/python scripts/manage_itch_session.py inspect --input <private-bundle> --expected-sha256 <independently-retained-bundle-hash>
<venv>/bin/python scripts/manage_itch_session.py migrate --input <old-private-bundle> --expected-sha256 <trusted-old-hash> --output <new-immutable-private-revision>
```

The source admission must already be trusted. Hashing an arbitrary downloaded file does not grant authenticity or authorization. Creating an initial bundle is an explicit Python operation using the validated SDK and `build_bundle`;observed inputs remain unsupported by this authored profile.

## Verification boundaries

The product test program uses the actual NativeSession/selector,real native bindings and private files. It checks paused restore,no startup reapplication,both books/native metrics,book-depth limits,replay/cursor/capture continuity,candidate failure,strict schemas/generation,private permissions,immutable rollback preservation,crash restart,explicit migration,offline CLI and safe return to the existing workflow. ASGI factory wiring is inspected without invoking it. Frontend unit/build checks verify data contracts and replay bounds;no browser/visual or owner-private-target acceptance is inferred.

A new stepping test caught redundant suffix reapplication in an intermediate implementation and was repaired before publication. The old no-launch harness imported an eagerly constructed ASGI object before replacing its factory. No server/listener was started by that import,but the earlier no-factory label was too strong. The lazy export plus explicit `_application is None` assertions now make the no-construction boundary executable. Prior source-bound test receipts are preserved,not retroactively relabeled.

The full XBRL context-placement repair is documented separately. Official Kraken documentation retrieval received proxy CONNECT403;no retry,feed connection or provisional-status change was made. Full XBRL schema/transform/relationship/statement coverage and actual provider,target/browser/device,ARM64 and hardware qualification remain separate open requirements.

## Replay worker rejection regression

The final developer pass reproduced a separate worker-lifecycle defect: a source
frame refused after restoration raises `ItchProductError` (`ValueError`), while
the background replay coroutine previously caught only native `EngineError`.
The session paused correctly, but that coroutine could exit permanently. The
bounded `NativeSession.tick()` now owns that iteration, pauses both control
states on either classified rejection, retains the accepted checkpoint and
publishes a bounded diagnostic. An offline test compiles the actual nested
worker coroutine with a deterministic clock; it verifies survival, unchanged
accepted books and explicit subsequent resume. It neither constructs an ASGI
application nor opens a socket. Failing-before and passing-after logs are
retained under `build/remaining-engineering/product-worker-rejection-*`.
