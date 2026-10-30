"""Exact offline remediation cohort,with provider/network startup disabled."""
import json,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
for key in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED','GIG_ALPACA_STORE_ENABLED','GIG_HISTORY_STORE_ENABLED'):
    os.environ[key]='0'
for key in ('CODESPACES','CODESPACE_NAME','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN','GIG_TERMINAL_ALLOWED_ORIGINS'):
    os.environ.pop(key,None)
suite=unittest.defaultTestLoader.loadTestsFromNames(['terminal.stocks.test_remediation_options','terminal.test_concentration','terminal.test_research_resources'])
assert suite.countTestCases()==25,suite.countTestCases()
result=unittest.TextTestRunner(verbosity=2).run(suite)
counts={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}
print('REMEDIATION_COUNTS='+json.dumps(counts))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun==25 and not result.skipped else 1)
