"""Strict offline read-only IEX/launcher/jitter qualification; no provider traffic."""
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
for key in ('GIG_ALPACA_ENABLED', 'GIG_ALPACA_IEX_STREAM_ENABLED',
            'GIG_ALPACA_LIVE_ENABLED', 'GIG_PAPER_EXECUTION_ENABLED',
            'GIG_SEC_ENABLED', 'GIG_ALPACA_STORE_ENABLED', 'GIG_HISTORY_STORE_ENABLED'):
    os.environ[key] = '0'
suite = unittest.defaultTestLoader.loadTestsFromName('terminal.stocks.test_final_qualification')
expected = 35
assert suite.countTestCases() == expected, suite.countTestCases()
result = unittest.TextTestRunner(verbosity=2).run(suite)
print('FINAL_QUALIFICATION_COUNTS=' + json.dumps({
    'tests': result.testsRun, 'expected': expected, 'failures': len(result.failures),
    'errors': len(result.errors), 'skipped': len(result.skipped)}))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun == expected and not result.skipped else 1)
