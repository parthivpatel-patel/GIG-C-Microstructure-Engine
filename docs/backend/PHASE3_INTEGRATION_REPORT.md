# Phase 3 integration and reproducibility

Preserved Phase2 shell,styles,shared-scale comparisons,filing pages and deferred3D.
Only Stock's observed-price panel gains a compact history-integrity note. New v2 GET
is additive;v1/provider gate/origin/proof/stream contracts are unchanged. It reads accepted
cache only and cannot initiate provider loading. Native C++ source is unchanged.

Authored end-to-end path:curated AAPL/CIK → injected SEC acceptance → injected IEX raw
bars → neutral validation → cached financials/history → exact descriptive research →
ATLAS. API test checks no native book mutation,malformed query rejection and history
JSON Schema. Browser checks exact2/101 returned close change for authored101→103,
synthetic origin,2 records,incomplete history,visible integrity note and native transport.
Existing global NVDA→AAPL regression remains intact. No authored amount represents a
verified actual company or market observation.

Local commands(use the validated environments,not arbitrary system Python):

```bash
python terminal/tests/run_native_suite.py --expected-tests 274
python -m unittest terminal.stocks.test_phase3 -v
npm --prefix terminal/web test
python terminal/tests/run_atlas_browser_suite.py
```

Browser driver requires four authored loopback servers as documented in the Phase2
report. Build completes first;seven suites run serially with asset-hash verification.
Do not build assets concurrently. Live provider flags stay0. Browser captures are
Chromium/SwiftShader emulation,not physical Android or external Codespaces acceptance.

Codespace update to this deliberately separate backend branch:

```bash
git fetch origin
git switch --track origin/feat/atlas-phase3-backend
npm --prefix terminal/web run build
bash scripts/start_terminal.sh
```

If already on this branch,use git pull --ff-only instead of switch. Stop the old server
with Ctrl+C first. Keep8787 PRIVATE and open its authenticated forwarded HTTPS URL.
No native rebuild,new production dependency,provider activation or paid service is needed.
Only an owner with existing authorized SEC configuration should load official disclosures.
