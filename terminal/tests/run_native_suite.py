"""Exact terminal test cohort for release/debug/sanitized native binding consumers."""
import unittest

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromNames([
        'terminal.server.test_server','terminal.providers.test_kraken',
        'terminal.test_historical','terminal.test_recording','terminal.test_recording_api'])
    suite.addTests(unittest.defaultTestLoader.discover('terminal/tests',pattern='test_native_depth.py'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
