"""No-application,network-forbidden real-native durability/restart regression."""
import os,socket,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if len(sys.argv)!=2:raise SystemExit('fixture executable required')
os.environ['GIG_ITCH_FIXTURE']=sys.argv.pop()
def forbidden(*_a,**_k):raise AssertionError('NO_APPLICATION_OR_NETWORK_ALLOWED')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
suite=unittest.defaultTestLoader.loadTestsFromName('terminal.test_itch_durable_recovery')
assert suite.countTestCases()==9
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful()and not result.skipped and result.testsRun==9 else 1)
