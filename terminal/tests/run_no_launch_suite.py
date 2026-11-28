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
assert app._application is None,'Application constructed during import'
app.create_app=no_socket
from terminal.stocks.test_sec_expansion import Expansion
names=['terminal.stocks.test_acceptance','terminal.stocks.test_live_checkpoint','terminal.stocks.test_filing_vintage','terminal.stocks.test_observation_store','terminal.stocks.test_projection','terminal.stocks.test_trade_tape','terminal.stocks.test_live_recovery','terminal.stocks.test_sec_continuation','terminal.stocks.test_reconnect_stability','terminal.stocks.test_live_market.Semantics','terminal.stocks.test_final_qualification.AsyncReliability','terminal.stocks.test_final_qualification.RetryArithmetic']
# This is a selected no-server development cohort,not the full API/fixed cohort.
selected=[n for n in unittest.defaultTestLoader.getTestCaseNames(Expansion) if n not in ('test_endpoints_keep_origin_boundary_and_query_budgets','test_older_cached_page_is_readable_without_new_upstream_request')]
names += ['terminal.test_native_recovery','terminal.test_aggregate_recovery','terminal.stocks.test_xbrl_instance','terminal.stocks.test_xbrl_collection','terminal.stocks.test_xbrl_tool']
names += ['terminal.test_itch_product','terminal.test_itch_source_product','terminal.test_itch_durable_recovery','terminal.test_session_recovery','terminal.stocks.test_inline_xbrl','terminal.stocks.test_inline_set','terminal.stocks.test_inline_registry_numeric','terminal.stocks.test_xbrl_dts','terminal.stocks.test_xbrl_binding','terminal.stocks.test_xbrl_types','terminal.stocks.test_xbrl_enumeration','terminal.stocks.test_xbrl_vintages','terminal.stocks.test_xbrl_whitespace','terminal.stocks.test_xbrl_dimensions','terminal.stocks.test_xbrl_open_dimensions','terminal.stocks.test_xbrl_restriction_constraints','terminal.stocks.test_xbrl_calculation_intervals','terminal.stocks.test_xbrl_calculation_report','terminal.stocks.test_xbrl_calculation_product','terminal.stocks.test_xbrl_lineage','terminal.stocks.test_xbrl_typed_dimensions','terminal.stocks.test_xbrl_inherited_dimensions','terminal.stocks.test_xbrl_relationships','terminal.stocks.test_xbrl_statements','terminal.stocks.test_xbrl_product','terminal.stocks.test_xbrl_accuracy','terminal.stocks.test_xbrl_statement_v2','terminal.stocks.test_xbrl_embedded','terminal.stocks.test_sec_filing_ingest','terminal.stocks.test_sec_source_expansion','terminal.stocks.test_sec_multidoc','terminal.stocks.test_sec_transform_profile','terminal.stocks.test_sec_ingest_store','terminal.stocks.test_xbrl_duplicate_diagnostics','terminal.stocks.test_sec_ingest_cli']
names += ['terminal.stocks.test_xbrl_statement_set','terminal.stocks.test_xbrl_negative_dimensions','terminal.stocks.test_xbrl_dimensional_calculation']
names += ['terminal.stocks.test_python_json_ingress','terminal.stocks.test_history_json_ingress','terminal.stocks.test_xbrl_dts_source_audit','terminal.stocks.test_statement_set_source_acceptance']
names += ['terminal.stocks.test_xbrl_negative_only_dimensions','terminal.stocks.test_inline_dts_source_audit','terminal.stocks.test_xbrl_accounting_relationships','terminal.stocks.test_xbrl_accounting_statements']
names += ['terminal.providers.test_kraken_ordered','terminal.providers.test_kraken_book_session']
names += ['terminal.providers.test_'+name for name in ('recovery_hardening','supervisor','coinbase_supervisor','transport','kraken','integrity','kraken_admin','differential')]
names += ['terminal.stocks.test_sec_expansion.Expansion.'+n for n in selected]
names += ['terminal.stocks.test_xbrl_typed_hypercubes','terminal.providers.test_kraken_depth_session','terminal.stocks.test_financial_intelligence_product']
names += ['terminal.stocks.test_xbrl_cross_role','terminal.providers.test_kraken_public_session','terminal.test_itch_source_completion']
names += ['terminal.stocks.test_xbrl_inherited_cross_role','terminal.stocks.test_xbrl_statement_comparison','terminal.providers.test_kraken_coordinator','terminal.test_itch_completion_capsule']
names += ['terminal.providers.test_supervisor_joint','terminal.stocks.test_xbrl_effective_cross_role']
names += ['terminal.test_itch_capsule_persistence']
names += ['terminal.test_kraken_joint_recording','terminal.test_l2_playback.Playback']
names += ['terminal.stocks.test_xbrl_bound_restrictions']
names += ['terminal.stocks.test_xbrl_mixed_cross_role']
names += ['terminal.stocks.test_xbrl_typed_bounds','terminal.providers.test_kraken_large_depth']
suite=unittest.defaultTestLoader.loadTestsFromNames(names)
expected=1452
assert suite.countTestCases()==expected,('Unexpected no-launch cohort',suite.countTestCases())
result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'schema':'gig.no_launch.developer_tests.v1','selected_names':names,'expected':expected,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'socket_attempts_allowed':False,'app_factory_allowed':False,'application_constructed':app._application is not None,'scope':'Explicit developer subset;not full API,browser,provider or final acceptance'}
print('NO_LAUNCH_COUNTS='+json.dumps(report,sort_keys=True))
assert app._application is None,'Application constructed during developer tests'
raise SystemExit(0 if result.wasSuccessful()and not result.skipped and result.testsRun==expected else 1)
