"""Actual Python-to-TypeScript vintage admission; no application or sockets."""
import json,socket,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
def forbidden(*a,**k):raise AssertionError('NO_APPLICATION_OR_NETWORK_ALLOWED')
socket.socket.connect=forbidden;socket.socket.bind=forbidden
from terminal.stocks.test_xbrl_vintages import workspace,CUTOFFS,ROLE
from terminal.stocks.xbrl_vintages import company_vintages
with tempfile.TemporaryDirectory()as d:
 p=Path(d)/'bundle.json';p.write_text(json.dumps(company_vintages(workspace(),'AAPL',CUTOFFS,role=ROLE)))
 r=subprocess.run(['node','--experimental-strip-types',str(root/'terminal/tests/xbrl-vintage-contract.mjs'),str(p)],capture_output=True,text=True,timeout=20)
 if r.returncode:raise AssertionError(r.stderr)
 print(r.stdout.strip())
