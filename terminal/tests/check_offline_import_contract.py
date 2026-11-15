"""Real authored exports exercise strict browser JSON ingress with no application/socket."""
import json,socket,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
def forbidden(*a,**k):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden
from terminal.stocks.test_xbrl_calculation_product import prepared,ROLE,EARLY,LATE
from terminal.stocks.xbrl_calculation_product import company_calculation_contract
from terminal.stocks.test_xbrl_vintages import workspace,CUTOFFS
from terminal.stocks.xbrl_vintages import company_vintages
from terminal.stocks.xbrl_product import company_contract
w,g=prepared();rows=[['calculation',company_calculation_contract(w,'AAPL',EARLY,g,role=ROLE,rounding_mode=mode)]for mode in('round-to-nearest','truncation')]
rows.append(['calculation',company_calculation_contract(w,'AAPL',LATE,{},role=ROLE)])
rows.append(['calculation',company_calculation_contract(w,'AAPL',LATE,g,role=ROLE)])
v=workspace();rows.append(['vintages',company_vintages(v,'AAPL',CUTOFFS,role=ROLE)])
rows.append(['statement',company_contract(v,'AAPL',LATE,role=ROLE,profile='accuracy-extension-v2')])
with tempfile.TemporaryDirectory()as directory:
 p=Path(directory)/'authored-imports.json';p.write_text(json.dumps(rows));result=subprocess.run(['node','--experimental-strip-types',str(root/'terminal/tests/offline-import-contract.mjs'),str(p)],capture_output=True,text=True,timeout=20)
 if result.returncode:raise AssertionError(result.stderr)
 print(result.stdout.strip())
