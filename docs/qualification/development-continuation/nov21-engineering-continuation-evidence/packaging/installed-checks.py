"""Isolated installed SDK/source consumers with hard socket/app-factory guards."""
import json,os,socket,sys,unittest
from pathlib import Path
config=json.loads(Path(os.environ['GIG_RECOVERY_CONFIG']).read_text());root=Path.cwd();mode=sys.argv[1]
import gig_microstructure as gig
assert Path(gig.__file__).resolve().is_relative_to(Path(os.environ['GIG_RECOVERY_INSTALLED']).resolve()),gig.__file__
assert (root/'terminal/providers/kraken_coordinator.py').is_file()
assert (root/'terminal/stocks/xbrl_inherited_cross_role.py').is_file()
assert (root/'terminal/stocks/xbrl_effective_cross_role.py').is_file()
assert (root/'terminal/tests/statement_comparison_ui_fixtures.py').is_file()
sys.path.insert(0,str(root))
def forbidden(*_a,**_k):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.server import app
assert app._application is None
app.create_app=forbidden
if mode=='sdk':
 sys.path.insert(0,str(root/'tests'));names=['test_python'];expected=8
elif mode=='source':
 assert not hasattr(gig._native,'restore_itch_completion_capsule')
 names=config['source_test_names'];expected=config['expected_source_tests']
elif mode=='streaming':
 assert hasattr(gig._native,'restore_itch_completion_capsule')
 assert Path(os.environ['GIG_ITCH_FIXTURE']).is_file()
 names=['terminal.test_itch_completion_capsule','terminal.test_itch_source_completion','terminal.test_itch_source_product']
 expected=config['expected_streaming_tests']
else:raise AssertionError(mode)
suite=unittest.defaultTestLoader.loadTestsFromNames(names)
assert suite.countTestCases()==expected,(mode,suite.countTestCases(),expected)
result=unittest.TextTestRunner(verbosity=2).run(suite)
assert app._application is None
receipt={'schema':'gig.nov21.engineering.installed_checks.v1','source':config['source'],'mode':mode,
 'selected_names':names,'expected':expected,'tests':result.testsRun,'errors':len(result.errors),
 'failures':len(result.failures),'skipped':len(result.skipped),'sdk':gig.__file__,
 'fixture':os.environ.get('GIG_ITCH_FIXTURE')if mode=='streaming'else None,
 'application_constructed':False,'app_factory_allowed':False,'socket_attempts_allowed':False}
print(json.dumps(receipt,sort_keys=True))
raise SystemExit(0 if result.wasSuccessful()and not result.skipped and result.testsRun==expected else 1)
