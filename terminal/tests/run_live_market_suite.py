"""Fixed authored stock/SEC/live cohort;never enables operator provider gates."""
import os,sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):os.environ[k]='0'
for k in ('CODESPACES','CODESPACE_NAME','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN','GIG_TERMINAL_ALLOWED_ORIGINS'):os.environ.pop(k,None)
suite=unittest.defaultTestLoader.loadTestsFromNames(['terminal.stocks.test_'+name for name in ('phase3','phase4','phase5','final','sec_integration','live_market')])
assert suite.countTestCases()==104,('Unexpected cohort',suite.countTestCases())
result=unittest.TextTestRunner(verbosity=2).run(suite)
print('LIVE_MARKET_COUNTS='+json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun==104 and not result.skipped else 1)
