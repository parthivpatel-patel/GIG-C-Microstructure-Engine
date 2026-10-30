# One final acceptance session in the existing private Codespace

This is final acceptance after engineering,not an intermediate development request.
The owner may perform it later. Existing Alpaca keys and SEC private configuration
are reused. Do not print/copy/regenerate keys or the SEC contact. No new setup/account
is required. No acquisition or final acceptance was performed on the owner's behalf.

## Before the single run

Keep the forwarded8787 port **Private**,with GitHub authentication required. Stop the
existing ATLAS server with Ctrl+C in its original terminal. Do not kill another
application or change GIG Quant Terminal. The source helper refuses an occupied8787
port rather than opening a second application-owned upstream connection.

Alpaca's cloud/private-display record remains unavailable in this repository;ticket
381230 has no recorded resolution. Only an existing verified applicable record may
satisfy those gates. Do not enable flags merely to make this procedure pass. If rights
remain unresolved,leave them disabled:SEC can qualify independently,and the report
will explicitly mark Alpaca BLOCKED. This is not a request for another general account
authorization or new credentials.

Only if the existing Alpaca gates are legitimately enabled and a free account-wide
streaming slot is arranged,add `--exclusive-stream-window` to the source command
below. Otherwise omit it:the helper will not open an IEX connection. Other applications
can share the same allowance;the nominal plan limit is not an additional allowance.

## Update,qualify once,and start privately

Run this one sequence from the existing repository on `feat/atlas-final-release`:

```bash
git pull --ff-only origin feat/atlas-final-release
npm --prefix terminal/web run build
.venv/bin/python -m pip install -r terminal/server/requirements.txt
umask 077
mkdir -p build/operational
(set -o noclobber; .venv/bin/python scripts/qualify_atlas.py --execute > build/operational/source-qualification-final.json)
GIG_ALPACA_STORE_ENABLED=0 GIG_HISTORY_STORE_ENABLED=0 bash scripts/start_terminal.sh
```

If update,build or dependency installation fails,stop before acquisition. The exclusive output redirect refuses
to overwrite an existing final source report,before making any request. Preserve that
prior report;do not delete evidence simply to rerun. Review results privately in the editor;do not paste contacts/credentials or raw
provider observations into chat. A helper exit2 means some stage is blocked,
inconclusive or rejected;it does not require resetting SEC configuration or replacing
keys. The existing dependency update installs the fixed MessagePack1.2.3 release;it
does not reconfigure providers,replace keys or rebuild the native engine. An unsafe
old parser is refused by startup and before upstream acquisition. The normal gated
application can still start once that security patch is installed.

The helper performs at most two paper asset reads,two bounded IEX historical reads,
four SEC reads and one optional30-second IEX connection,subject to existing permissions.
It has no automatic retries and reports fixed safe failure codes/stages. Registry
source-entry,accepted and excluded counts are separate;no aliases/CIKs are guessed.
Fresh actual quote AND trade observations per requested symbol are required for a live
PASS. Quiet/empty windows remain INCONCLUSIVE. SEC readiness alone is not retrieval.
The independent raw SEC read is intentional reconciliation,not an automatic retry.
No account/order/position endpoint or persistent observed store is enabled.

The source CLI is transient and does not inject its in-memory observations into the
normal server. Startup/explicit UI loads collect the application's own permitted
receipts in a separate lifetime. The shown launch disables observed retention for this
acceptance process only;it does not change saved configuration or remove old data.
Source/read/body/cancellation budgets and the non-hard180-second shutdown caveat remain
as described in `../milestones/OPERATIONAL_QUALIFICATION_RUNBOOK.md`.

## Sequential browser acceptance

Open the existing **private forwarded HTTPS address from the Codespaces Ports tab**.
This assignment supplies no newly verified external URL. One final session should
record the following criteria against `git rev-parse HEAD`:

| Check | PASS criterion | Otherwise |
|---|---|---|
| Actual SEC | Accepted official mapping and selected facts/filings reconcile;source receipts and accepted/excluded counts present | Preserve the safe stage/code. No request to redo ready configuration |
| AAPL/APLD/CRWV identity | Search resolves exact source-provided identities;CIK is official or explicitly null | Never guess or silently convert punctuation |
| Actual assets/history | Applicable Alpaca rights/free-plan evidence exists;actual source counts and AAPL/MSFT IEX bars/independent exact-time comparison qualify | BLOCKED/INCONCLUSIVE remains honest;fallback count is not imported coverage |
| Actual live IEX | Authorized window supplies fresh quotes/prints within configured symbol limit;IEX-only label and source/receive clocks visible | Empty/quiet/not authorized is not observed-data PASS |
| Private transport | GitHub authentication required,port Private,actual HTTPS/WSS accepted using exact Origin/Host or bound proofs;no secret displayed | Keep local TLS fixture evidence separate from actual target privacy |
| Reconnection | Disconnect/reconnect only the browser network;state resynchronizes without another upstream provider connection or relabeling stale data live | Do not induce uncontrolled upstream faults or consume another account slot |
|12 workspaces | Every exact workspace in REQUIREMENT_MATRIX loads;search,symbol switching,financial period/filing controls,replay and simulation work | Record reproducible defects;do not fabricate data for unavailable sources |
|13 modes | Each applicable mode renders,rotates/zooms/resets and exposes source/method labels;missing inputs yield informative unavailable state;2D fallback works | No L2/L3,execution direction or IV invented from Level1 |
| Actual devices | Desktop and Android controls readable and usable;touch/keyboard/camera and responsiveness acceptable | Emulated viewports/touch do not close the physical-device gate |
| Owner decision | Exact candidate,sources,limitations and unresolved issues explicitly accepted by owner | Milestone2 remains NOT VERIFIED |

Copy `../milestones/FINAL_ACCEPTANCE_TEMPLATE.json` into ignored private evidence,
fill it from actual results,record SEC source/accepted/excluded counts,and retain source
report hash. Do not commit provider observations,screenshots,keys,cookies or proof values
without applicable rights. A green source CLI or automated test total does not imply
owner acceptance,legal rights,production readiness,or current-candidate ARM64 qualification.

## External infrastructure gate

The manual owner-gated free-runner workflows are prepared;ATLAS qualification now
includes the strict94-case source qualification cohort in addition to the unchanged
six compiler/configuration jobs and frozen checks. No workflow was dispatched here.
Only a separately owner-authorized eligible/free run against the actual candidate may
close its ARM64/hosted gate. Older successful SHAs do not qualify these Python/TS
changes. Main/default-branch workflow registration was not modified.
