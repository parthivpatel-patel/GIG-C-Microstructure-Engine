"""Exact terminal test cohort for release/debug/sanitized native binding consumers."""
import unittest
import argparse,json,os,sys
from pathlib import Path

# Direct file execution must resolve this checkout, including fresh wheel runners.
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

def build_suite():
    suite=unittest.defaultTestLoader.loadTestsFromNames([
        'terminal.server.test_server','terminal.providers.test_kraken',
        'terminal.providers.test_kraken_admin','terminal.providers.test_integrity','terminal.providers.test_supervisor','terminal.providers.test_coinbase_candidate','terminal.providers.test_coinbase_supervisor','terminal.providers.test_transport','terminal.providers.test_differential',
        'terminal.test_live_api','terminal.test_l2_recording','terminal.test_l2_playback','terminal.test_l2_capture','terminal.test_provider_diagnostic','terminal.test_websocket_diagnostic','terminal.test_arm64_terminal_policy','terminal.test_l2_research',
        'terminal.test_historical','terminal.test_recording','terminal.test_recording_api','terminal.stocks.test_workspace','terminal.stocks.test_repair','terminal.stocks.test_backend'])
    suite.addTests(unittest.defaultTestLoader.discover('terminal/tests',pattern='test_native_depth.py'))
    return suite

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--expected-tests',type=int);args=p.parse_args()
    os.environ['GIG_LIVE_ENABLED']='0';os.environ['GIG_COINBASE_ENABLED']='0';os.environ['GIG_SEC_ENABLED']='0';os.environ['GIG_ALPACA_ENABLED']='0'
    # This CLI launches authored localhost fixtures, never the operator's server.
    # Individual forwarding-policy tests supply their own explicit environment.
    for name in ('CODESPACES','CODESPACE_NAME','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN','GIG_TERMINAL_ALLOWED_ORIGINS'):
        os.environ.pop(name,None)
    suite=build_suite();expected=suite.countTestCases()
    if args.expected_tests is not None and expected!=args.expected_tests:
        raise SystemExit(f'Expected {args.expected_tests} tests; discovered {expected}')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print('TERMINAL_TEST_COUNTS='+json.dumps({'tests':result.testsRun,'expected':expected,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)},sort_keys=True),flush=True)
    raise SystemExit(0 if result.wasSuccessful() and not result.skipped and result.testsRun==expected else 1)
