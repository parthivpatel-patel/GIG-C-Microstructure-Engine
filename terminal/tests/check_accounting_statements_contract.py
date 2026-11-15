"""Actual original-source accounting products through the bounded TS JSON consumer."""
import hashlib,json,socket,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
def forbidden(*args,**kwargs):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.stocks.test_xbrl_accounting_statements import recipe,prepared,export,EARLY,LATE,A,B
from terminal.stocks.test_xbrl_dts import document
rows=[]
for name,entry in [('reported',recipe()),('exact',recipe(exact=True)),('conflicting',recipe(alias='101')),('missing',recipe(alias=None))]:
 w,i,b=prepared(entry);rows.append([name,export(w,i,b)])
e=recipe();d=e['documents'][2];e['documents'][2]=document('extension.xsd',d['raw'].replace(b'id="CashFlowTotal" name="CashFlowTotal" type="x:monetaryItemType"',b'id="CashFlowTotal" name="CashFlowTotal" type="x:stringItemType"'));w,i,b=prepared(e);rows.append(['unsupported',export(w,i,b)])
w,i,b=prepared(recipe(),recipe(alias=None,accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A));rows.extend([['original_vintage',export(w,i,b,at=EARLY)],['amended_vintage',export(w,i,b)]])
with tempfile.TemporaryDirectory()as directory:
 path=Path(directory)/'accounting.json';path.write_text(json.dumps(rows));r=subprocess.run(['node','--experimental-strip-types',str(root/'terminal/tests/accounting-statements-contract.mjs'),str(path)],capture_output=True,text=True,timeout=30)
 if r.returncode:raise AssertionError(r.stderr)
 print(r.stdout.strip())
