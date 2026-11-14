"""Actual acceptance-selected Python report consumed by TypeScript; no app/network."""
import json,socket,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
def forbidden(*a,**k):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.connect=forbidden;socket.socket.bind=forbidden
from terminal.stocks.test_xbrl_calculation_product import prepared,ROLE,EARLY,LATE
from terminal.stocks.xbrl_calculation_product import company_calculation_contract
w,g=prepared();rows=[company_calculation_contract(w,'AAPL',EARLY,g,role=ROLE,rounding_mode=mode)for mode in('round-to-nearest','truncation')];rows.append(company_calculation_contract(w,'AAPL',LATE,{},role=ROLE));rows.append(company_calculation_contract(w,'AAPL',LATE,g,role=ROLE))
with tempfile.TemporaryDirectory()as d:
 p=Path(d)/'reports.json';p.write_text(json.dumps(rows));r=subprocess.run(['node','--experimental-strip-types',str(root/'terminal/tests/xbrl-calculation-report-contract.mjs'),str(p)],capture_output=True,text=True,timeout=20)
 if r.returncode:raise AssertionError(r.stderr)
 print(r.stdout.strip())
