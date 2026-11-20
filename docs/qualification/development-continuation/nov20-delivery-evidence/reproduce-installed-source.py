"""Run exactly the installed source cohort in the retained packaging receipt."""
import json,os,socket,sys,unittest
from pathlib import Path
receipt=json.loads(Path(os.environ['GIG_DELIVERY_PACKAGE_RECEIPT']).read_text())
root=Path.cwd();assert (root/'terminal/stocks/financial_intelligence_product.py').is_file()
import gig_microstructure as gig
assert Path(gig.__file__).resolve().is_relative_to(Path(os.environ['GIG_DELIVERY_INSTALLED']).resolve()),gig.__file__
sys.path.insert(0,str(root))
def forbidden(*_a,**_k):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.server import app
assert app._application is None
app.create_app=forbidden
names=receipt['installed_source']['selected_names'];suite=unittest.defaultTestLoader.loadTestsFromNames(names)
assert suite.countTestCases()==709
result=unittest.TextTestRunner(verbosity=2).run(suite)
assert app._application is None
out={'schema':'gig.installed_source_guarded.v1','source':receipt['source'],'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'application_constructed':app._application is not None,'app_factory_allowed':False,'socket_attempts_allowed':False,'sdk':gig.__file__}
print('INSTALLED_GUARDED_COUNTS='+json.dumps(out,sort_keys=True))
raise SystemExit(0 if result.wasSuccessful()and not result.skipped else 1)
