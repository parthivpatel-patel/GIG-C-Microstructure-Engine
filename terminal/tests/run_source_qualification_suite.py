"""Exact offline qualification cohort;no real provider connections or gate activation."""
import json,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
for key in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):
    os.environ[key]='0'
for key in ('CODESPACES','CODESPACE_NAME','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN','GIG_TERMINAL_ALLOWED_ORIGINS'):
    os.environ.pop(key,None)
suite=unittest.defaultTestLoader.loadTestsFromNames(['terminal.stocks.test_'+name for name in
    ('sec_directory_boundary','sec_identity_diagnostics','sec_terminal_reference','sec_qualification','operational','backend','overnight')])
assert suite.countTestCases()==142,('Unexpected cohort',suite.countTestCases())
result=unittest.TextTestRunner(verbosity=2).run(suite)
print('SOURCE_QUALIFICATION_COUNTS='+json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun==142 and not result.skipped else 1)
