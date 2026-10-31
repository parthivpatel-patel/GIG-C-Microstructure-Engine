"""Strict independent Sprint2 cohort. Only authored fixtures;providers stay off."""
import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
for name in ('GIG_SEC_ENABLED', 'GIG_ALPACA_ENABLED', 'GIG_LIVE_ENABLED', 'GIG_COINBASE_ENABLED',
             'GIG_ALPACA_STORE_ENABLED', 'GIG_HISTORY_STORE_ENABLED'):
    os.environ[name] = '0'
for name in ('CODESPACES', 'CODESPACE_NAME', 'GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'GIG_TERMINAL_ALLOWED_ORIGINS'):
    os.environ.pop(name, None)
suite = unittest.defaultTestLoader.loadTestsFromNames([
    'terminal.test_sprint2_review', 'terminal.test_sec_evidence_binding',
    'terminal.test_private_deployment', 'terminal.test_sprint2_recovery'])
assert suite.countTestCases() == 30, suite.countTestCases()
result = unittest.TextTestRunner(verbosity=2).run(suite)
counts = {'tests': result.testsRun, 'expected': 30, 'failures': len(result.failures),
          'errors': len(result.errors), 'skipped': len(result.skipped)}
print('SPRINT2_COUNTS=' + json.dumps(counts, sort_keys=True), flush=True)
raise SystemExit(0 if result.wasSuccessful() and result.testsRun == 30 and not result.skipped else 1)
