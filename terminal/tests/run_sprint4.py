"""Strict offline Sprint4 cohort;new source,wire,research and paper tests only."""
import os,sys,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED','GIG_ALPACA_STORE_ENABLED','GIG_HISTORY_STORE_ENABLED'):os.environ[k]='0'
for k in ('CODESPACES','CODESPACE_NAME','GIG_TERMINAL_ALLOWED_ORIGINS'):os.environ.pop(k,None)
suite=unittest.defaultTestLoader.loadTestsFromNames(['terminal.stocks.test_sprint4_history','terminal.paper.test_alpaca','terminal.stocks.test_historical_research','terminal.test_sprint4_api','terminal.test_sprint4_boundaries'])
expected=95;assert suite.countTestCases()==expected,suite.countTestCases();r=unittest.TextTestRunner(verbosity=2).run(suite)
print('SPRINT4_COUNTS='+json.dumps(dict(tests=r.testsRun,expected=expected,failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped))))
raise SystemExit(0 if r.wasSuccessful()and r.testsRun==expected and not r.skipped else 1)
