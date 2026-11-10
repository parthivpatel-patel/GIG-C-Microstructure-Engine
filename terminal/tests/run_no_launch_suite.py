"""Selected developer checks that forbid application factories and network sockets.

This is not the full API, browser, provider or acceptance cohort. Run from any
working directory with the intended native binding directory on PYTHONPATH.
"""
import socket,unittest,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
# A hard guard for this developer test profile:neither listeners nor outbound sockets.
def no_socket(*_a,**_k):raise AssertionError('NO_APPLICATION_OR_NETWORK_ALLOWED')
socket.socket.bind=no_socket;socket.socket.connect=no_socket;socket.socket.connect_ex=no_socket
from terminal.server import app
app.create_app=no_socket
from terminal.stocks.test_sec_expansion import Expansion
names=['terminal.stocks.test_live_checkpoint','terminal.stocks.test_filing_vintage','terminal.stocks.test_observation_store','terminal.stocks.test_projection','terminal.stocks.test_trade_tape','terminal.stocks.test_live_recovery','terminal.stocks.test_sec_continuation','terminal.stocks.test_reconnect_stability','terminal.stocks.test_live_market.Semantics','terminal.stocks.test_final_qualification.AsyncReliability','terminal.stocks.test_final_qualification.RetryArithmetic']
# This is a selected no-server development cohort,not the full API/fixed cohort.
selected=[n for n in unittest.defaultTestLoader.getTestCaseNames(Expansion) if n not in ('test_endpoints_keep_origin_boundary_and_query_budgets','test_older_cached_page_is_readable_without_new_upstream_request')]
names += ['terminal.stocks.test_sec_expansion.Expansion.'+n for n in selected]
suite=unittest.defaultTestLoader.loadTestsFromNames(names)
expected=116
assert suite.countTestCases()==expected,('Unexpected no-launch cohort',suite.countTestCases())
result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'schema':'gig.no_launch.developer_tests.v1','selected_names':names,'expected':expected,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'socket_attempts_allowed':False,'app_factory_allowed':False,'scope':'Explicit developer subset;not full API,browser,provider or final acceptance'}
print('NO_LAUNCH_COUNTS='+json.dumps(report,sort_keys=True))
raise SystemExit(0 if result.wasSuccessful()and not result.skipped and result.testsRun==expected else 1)
