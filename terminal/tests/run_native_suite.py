"""Exact terminal test cohort for release/debug/sanitized native binding consumers."""
import unittest

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromNames([
        'terminal.server.test_server','terminal.providers.test_kraken',
        'terminal.providers.test_kraken_admin','terminal.providers.test_integrity','terminal.providers.test_supervisor','terminal.providers.test_coinbase_candidate','terminal.providers.test_transport','terminal.providers.test_differential',
        'terminal.test_live_api','terminal.test_l2_recording','terminal.test_l2_playback','terminal.test_l2_capture','terminal.test_provider_diagnostic','terminal.test_l2_research',
        'terminal.test_historical','terminal.test_recording','terminal.test_recording_api'])
    suite.addTests(unittest.defaultTestLoader.discover('terminal/tests',pattern='test_native_depth.py'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
