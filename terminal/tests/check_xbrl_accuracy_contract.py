#!/usr/bin/env python3
"""Actual Python→TypeScript v2 accuracy/extension checks;no ASGI or sockets."""
import json,socket,subprocess,sys,tempfile,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
def forbidden(*_a,**_k):raise AssertionError('NO_APPLICATION_OR_NETWORK_ALLOWED')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.stocks.test_xbrl_statement_v2 import extension
from terminal.stocks.test_xbrl_statements import collection,LATE,ROLE
from terminal.stocks.service import StockWorkspace
from terminal.stocks.xbrl_product import company_contract

def main():
 cases=[]
 def add(name,c):
  w=StockWorkspace(environment={})
  if c is not None:w.admit_xbrl_collection('AAPL',c)
  p=company_contract(w,'AAPL',LATE,role=ROLE,profile='accuracy-extension-v2');cases.append([name,p])
 add('compatible',collection(extension()));add('boundary',collection(extension(value='399')));add('inconsistent',collection(extension(value='397')))
 add('conflict',collection(extension(extra='<ext:CompanyLiquidity contextRef="I" unitRef="USD" decimals="0">401</ext:CompanyLiquidity>')))
 add('unsupported_type',collection(extension(kind='t:Unknown')));add('same_local_name',collection(extension(name='Assets')))
 add('dimensioned',collection(extension(context_extra='<x:segment><d:explicitMember dimension="ext:RegionAxis">ext:NorthMember</d:explicitMember></x:segment>')));add('unavailable',None)
 e=extension();e['raw']=e['raw'].replace(b'unitRef="USD" decimals="0">600',b'unitRef="USD">600');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();add('unknown_accuracy',collection(e))
 original=extension();amend=extension(value='399',accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession='0000000123-24-000001');add('amendment',collection(original,amend))
 import asyncio
 from terminal.stocks.test_sec_filing_ingest import Clock,Wire,resources,AGENT,ACC
 async def ingested():
  clock=Clock()
  async def unused(*_):raise AssertionError('NO_OLD_SOURCE_FETCH')
  w=StockWorkspace(environment={'GIG_SEC_ENABLED':'1','GIG_SEC_POLICY_REVIEWED':'1','GIG_SEC_USER_AGENT':AGENT},fetcher=unused,clock=clock)
  coordinator=w.create_sec_filing_ingestor('AAPL',transport=Wire(resources(),clock),enabled=True,sleep=clock.sleep)
  await coordinator.ingest(ACC);w.install_sec_filing_result('AAPL')
  return company_contract(w,'AAPL',LATE,role=ROLE,profile='accuracy-extension-v2')
 cases.append(['ingestion',asyncio.run(ingested())])
 with tempfile.TemporaryDirectory()as directory:
  path=Path(directory)/'authored-v2.json';path.write_text(json.dumps(cases,sort_keys=True))
  r=subprocess.run(['node','--experimental-strip-types',str(root/'terminal/tests/xbrl-accuracy-contract.mjs'),str(path)],cwd=root,capture_output=True,text=True,timeout=20)
  if r.returncode:raise AssertionError(r.stderr[-3000:])
  report=json.loads(r.stdout);assert report['cases']==11 and not report['application_started']and not report['provider_requested'];print(json.dumps(report,sort_keys=True))
 return 0
if __name__=='__main__':raise SystemExit(main())
