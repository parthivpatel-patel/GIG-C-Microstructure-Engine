"""Explicit installed-profile consumers with app/socket prohibition and no fallback."""
import json,os,socket,sys,unittest
from pathlib import Path
config=json.loads(Path(os.environ['GIG_COMPLETION_CONFIG']).read_text());root=Path.cwd();mode=sys.argv[1]
import gig_microstructure as gig
assert Path(gig.__file__).resolve().is_relative_to(Path(os.environ['GIG_COMPLETION_INSTALLED']).resolve()),gig.__file__
assert (root/'terminal/providers/kraken_public_session.py').is_file()
sys.path.insert(0,str(root))
def forbidden(*_a,**_k):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.server import app
assert app._application is None
app.create_app=forbidden
if mode=='sdk':
 sys.path.insert(0,str(root/'tests'));names=['test_python'];expected=8
elif mode=='source':names=config['source_test_names'];expected=config['expected_source_tests']
elif mode=='streaming':
 assert Path(os.environ['GIG_ITCH_FIXTURE']).is_file();names=['terminal.test_itch_source_completion','terminal.test_itch_source_product'];expected=22
else:raise AssertionError(mode)
suite=unittest.defaultTestLoader.loadTestsFromNames(names);assert suite.countTestCases()==expected,(mode,suite.countTestCases(),expected)
r=unittest.TextTestRunner(verbosity=2).run(suite);assert app._application is None
receipt={'schema':'gig.completion.installed_profile_checks.v1','source':config['source'],'mode':mode,'selected_names':names,'expected':expected,'tests':r.testsRun,'errors':len(r.errors),'failures':len(r.failures),'skipped':len(r.skipped),'sdk':gig.__file__,'fixture':os.environ.get('GIG_ITCH_FIXTURE')if mode=='streaming'else None,'application_constructed':False,'app_factory_allowed':False,'socket_attempts_allowed':False}
print(json.dumps(receipt,sort_keys=True))
raise SystemExit(0 if r.wasSuccessful()and not r.skipped and r.testsRun==expected else 1)
