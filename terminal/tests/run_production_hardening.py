"""Strict offline institutional hardening cohort, including controlled process exits."""
import json
import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
for key in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_ALPACA_IEX_STREAM_ENABLED',
            'GIG_ALPACA_LIVE_ENABLED','GIG_PAPER_EXECUTION_ENABLED',
            'GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):
    os.environ[key]='0'
for key in ('CODESPACES','CODESPACE_NAME','GIG_TERMINAL_ALLOWED_ORIGINS'):
    os.environ.pop(key,None)
suite=unittest.defaultTestLoader.loadTestsFromName('terminal.test_production_hardening')
expected=29
assert suite.countTestCases()==expected,suite.countTestCases()
result=unittest.TextTestRunner(verbosity=2).run(suite)
print('HARDENING_COUNTS='+json.dumps({'tests':result.testsRun,'expected':expected,
      'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun==expected and not result.skipped else 1)
