# GIG ATLAS research-candidate release notes

Private candidate on feat/atlas-final-release;not published/tagged/merged. Native Python
package version0.1.1 preserved;no incompatible version or release identity invented.

Added owner-gated stock IEX quote/trade transport,pinned multi-dataset exact risk workflow,
authored-only derived JSON export,conditional GARCH optimizer,fixed missing-emission HMM
routine and partial retained filing-date endpoint. No existing v1/v2 API removed;new proof
targets are exact and bounded. Native C++ interfaces/eight identities unchanged.

New server dependency:msgpack1.1.2(Apache-2.0). No frontend/paid dependency. Existing .venv:

```bash
# Stop the old terminal with Ctrl+C;preserve local edits before switching.
git fetch origin
git switch --track origin/feat/atlas-final-release
.venv/bin/python -m pip install -r terminal/server/requirements.txt
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

Already on branch:git pull --ff-only. Fresh setup:bash scripts/setup_terminal.sh first.
Keep Codespaces port8787 PRIVATE;use its authenticated forwarded HTTPS URL. Do not expose
fixture servers or change Origin/Host/proof settings. No native rebuild needed for an
existing compatible installation;fresh setup builds the actual native extension normally.

Private storage remains opt-in:existing GIG_HISTORY_STORE_ENABLED and directory flags;
use owner-private .gig-history,never commit contents. Observed retention approval remains
separate. No automatic schema migration or provider activation. Existing schema1/old
snapshot identities remain readable. New dataset endpoint rejects explicit incompatible
price units. Live start additionally needs reviewed GIG_ALPACA_LIVE_ENABLED,not set by code.
See REAL_DATA_ACCEPTANCE for owner-only gated commands and limitations before activation.

For regression instructions see PHASE8_QUALIFICATION_REPORT. Source archive inventory and
all changed-file/log/screenshot fingerprints are in final_evidence.json. Reverting a
candidate must preserve private data/backups and prior branches;do not reset/rewrite history.
