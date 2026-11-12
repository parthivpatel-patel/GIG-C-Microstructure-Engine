#!/usr/bin/env python3
"""Offline Python product → TypeScript statement contract. No ASGI or sockets."""
import json,socket,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
def forbidden(*_a,**_kw):raise AssertionError('NO_APPLICATION_OR_NETWORK_ALLOWED')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.stocks.test_xbrl_statements import collection,entry,LATE,ROLE
from terminal.stocks.service import StockWorkspace
from terminal.stocks.xbrl_product import company_contract

def main():
 cases=[]
 def add(name,c,at=LATE,role=ROLE):
  workspace=StockWorkspace(environment={})
  if c is not None:workspace.admit_xbrl_collection('AAPL',c)
  value=company_contract(workspace,'AAPL',at,role=role);cases.append([name,value['statement_view']['status'],value])
 add('available',collection());add('unavailable',None);add('before_acceptance',collection(),at='2024-02-01T12:00:00Z')
 add('conflict',collection(entry(extra_facts='<g:Assets contextRef="I" unitRef="USD">1001</g:Assets>')))
 add('ambiguous',collection(entry(),entry(value='1001',accession='0000000123-24-000002')))
 add('amendment',collection(entry(),entry(value='1100',accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession='0000000123-24-000001')))
 add('roles',collection(),role=None);add('exact',collection(entry(value='0.3',cash='0.1',liabilities='0.2')))
 with tempfile.TemporaryDirectory()as directory:
  path=Path(directory)/'authored-contract.json';path.write_text(json.dumps(cases,sort_keys=True))
  result=subprocess.run(['node','--experimental-strip-types',str(root/'terminal/tests/xbrl-statement-contract.mjs'),str(path)],cwd=root,capture_output=True,text=True,timeout=20,check=True)
  report=json.loads(result.stdout);assert report['cases']==8 and report['assertions']==58 and not report['application_started']and not report['provider_requested'];print(json.dumps(report,sort_keys=True))
 return 0
if __name__=='__main__':raise SystemExit(main())
